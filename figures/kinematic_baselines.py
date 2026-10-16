"""Offline CV / CA diagnostics using saved P15 DEV84 input poses only.

Run with the bundled Python and NumPy: python -B figures/kinematic_baselines.py
The plotting script imports analyze() and exports these same CSVs. No model/GPU
execution is needed; inputs and predictions come from the accepted archive.

Inputs: observed_anchor_position_m, observed_anchor_quaternion_xyzw (raw robot-
base coordinates), observed_timestamp_s, validity and frame indices from each
evaluation/dev/inputs/state-NNN.npz. All predictions for all 84 states are made
before opening any scored/future-label member. Generation members are accessed
only by a whitelist of observed fields and actual object descriptor/mask fields.

With d=0.05 s and p0,p1,p2 at times 0,-d,-2d:
  CV: v=(p0-p1)/d, delta_p(h)=h*v.
  CA: v0=(3*p0-4*p1+p2)/(2*d), a=(p0-2*p1+p2)/d**2;
      delta_p(h)=h*v0 + h**2*a/2.
All positions, velocities and accelerations use fixed robot-base axes.
The last-interval v is centered at -25 ms, not an instantaneous velocity at t=0.
CA's backward formula extrapolates v to t=0. No simulator velocity is read.

For object-to-robot-base rotations R0,R1,R2, define spatial interval velocities
  w_plus=Log(R0 R1.T)/d, w_minus=Log(R1 R2.T)/d (rad/s, robot-base axes).
CV predicts delta_R(h)=Exp(h*w_plus). CA estimates current spatial velocity
  w0=1.5*w_plus-0.5*w_minus and alpha=(w_plus-w_minus)/d,
then integrates dR/dt = [w0+t*alpha]_x R, R(0)=I. This is a fixed-base-frame
constant angular-acceleration extrapolator with backward interval estimates;
it is not componentwise extrapolation of absolute rotation vectors. Numerical
integration is left-multiplied exponential midpoint, maximum step 1 ms, checked
against 0.5 ms. No clipping, smoothing, fitting or label-dependent tuning.
Quaternion math is float64, scalar-last xyzw, normalized on ingestion.

Rotation conventions agree with the standard axis-angle/composition definitions:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.from_rotvec.html
https://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.transform.Rotation.__mul__.html
SciPy is not required. Quantiles are NumPy method='linear'; summaries are
descriptive, not confidence intervals or independent training-seed evidence.
"""
import argparse
import csv
import io
import json
from pathlib import Path
import tarfile

import numpy as np

ROOT = Path(__file__).resolve().parent
ARCHIVE = Path("C:/workspace/se3-wam-research/local_private/future0-aux-20261012/"
               "P15-archive-aux-p15-reports-a36-low-priority-4g-a1-a1/"
               "reports-downloaded-20261013T110014343027Z.tar")
HORIZONS = np.arange(50, 401, 50)
INPUT_FIELDS = ("observed_anchor_position_m", "observed_anchor_quaternion_xyzw",
                "observed_timestamp_s", "observed_anchor_valid", "observed_frame_mask",
                "observed_frame_indices", "oracle_source_frame_indices")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def arrays(archive, member, fields):
    with np.load(io.BytesIO(archive.extractfile(member).read()), allow_pickle=False) as z:
        return {key: z[key] for key in fields}


def unit(q):
    q = np.asarray(q, dtype=np.float64)
    norm = np.linalg.norm(q, axis=-1, keepdims=True)
    require(np.isfinite(q).all() and np.all(norm > 0), "invalid quaternion")
    return q / norm


def conjugate(q):
    return q * np.array([-1, -1, -1, 1])


def multiply(a, b):
    xyz = a[..., 3:] * b[..., :3] + b[..., 3:] * a[..., :3] + np.cross(a[..., :3], b[..., :3])
    w = a[..., 3:] * b[..., 3:] - np.sum(a[..., :3] * b[..., :3], axis=-1, keepdims=True)
    return np.concatenate((xyz, w), axis=-1)


def exponential(v):
    angle = np.linalg.norm(v, axis=-1, keepdims=True)
    return np.concatenate((0.5 * np.sinc(angle / (2 * np.pi)) * v, np.cos(angle / 2)), axis=-1)


def logarithm(q):
    q = unit(q)
    q = np.where(q[..., 3:] < 0, -q, q)
    length = np.linalg.norm(q[..., :3], axis=-1, keepdims=True)
    angle = 2 * np.arctan2(length, q[..., 3:])
    scale = np.divide(angle, length, out=np.full_like(length, 2), where=length > 1e-15)
    return scale * q[..., :3]


def matrix(q):
    q = unit(q)
    x, y, z, w = np.moveaxis(q, -1, 0)
    return np.stack((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w),
                     2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w),
                     2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)), axis=-1).reshape(q.shape[:-1]+(3, 3))


def integrate_ca(w0, alpha, max_step):
    q = np.tile([0., 0., 0., 1.], (len(w0), 1))
    outputs, previous = [], 0.
    for h in HORIZONS / 1000:
        steps = int(np.ceil((h - previous) / max_step - 1e-10))
        dt = (h - previous) / steps
        for k in range(steps):
            midpoint = previous + (k + 0.5) * dt
            q = unit(multiply(exponential((w0 + midpoint * alpha) * dt), q))
        outputs.append(q.copy())
        previous = h
    return np.stack(outputs, axis=1)


def rotation_error(pred, gt):
    relative = pred @ np.swapaxes(gt, -1, -2)
    return np.degrees(np.arccos(np.clip((np.trace(relative, axis1=-2, axis2=-1)-1)/2, -1, 1)))


def check_math():
    # Known-axis orientation and noncommuting multiplication order.
    rz = exponential(np.array([0., 0., np.pi/2]))
    rx = exponential(np.array([np.pi/2, 0., 0.]))
    np.testing.assert_allclose(matrix(rz) @ [1, 0, 0], [0, 1, 0], atol=1e-14)
    np.testing.assert_allclose(matrix(multiply(rz, rx)), matrix(rz) @ matrix(rx), atol=1e-14)
    # Exact recovery of a quadratic Cartesian trajectory from the last 3 samples.
    v, a = np.array([.2, -.1, .4]), np.array([.3, .5, -.2])
    t = np.array([-.1, -.05, 0.])[:, None]
    p = t*v + .5*t*t*a
    np.testing.assert_allclose((3*p[-1]-4*p[-2]+p[-3])/.1, v, atol=1e-14)
    np.testing.assert_allclose((p[-1]-2*p[-2]+p[-3])/.0025, a, atol=1e-14)
    # Fixed-axis angular acceleration commutes, so its exact solution is known.
    w, alpha = np.array([[0., 0., .7]]), np.array([[0., 0., .3]])
    h = HORIZONS[None, :, None]/1000
    np.testing.assert_allclose(integrate_ca(w, alpha, .001), exponential(h*w[:, None]+.5*h*h*alpha[:, None]), atol=1e-13)


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def analyze(path):
    check_math()
    with tarfile.open(path) as archive:
        accepted = json.load(archive.extractfile("evaluation/dev/accepted.json"))
        manifest = json.load(archive.extractfile("evaluation/dev/generation-manifest.json"))
        require(accepted["accepted"] and accepted["future_targets_after_all_generation"] and
                (accepted["states"], accepted["episodes"], accepted["tasks"]) == (84, 28, 14), "DEV84 acceptance mismatch")
        require(manifest["complete"] and manifest["future_targets_read"] is False and
                manifest["arm"] == "P15" and len(manifest["samples"]) == 84, "generation manifest mismatch")
        observed, evidence_rows, descriptor_differences = [], [], []
        # Phase 1: baseline construction reads observed inputs only, never scored members.
        for index, sample in enumerate(manifest["samples"]):
            raw = arrays(archive, f"evaluation/dev/inputs/state-{index:03}.npz", INPUT_FIELDS)
            p = raw["observed_anchor_position_m"].astype(np.float64)
            q = unit(raw["observed_anchor_quaternion_xyzw"])
            t = raw["observed_timestamp_s"]
            require(p.shape == (8, 3) and q.shape == (8, 4) and t.shape == (8,), f"state {index}: shape mismatch")
            require(np.isfinite(p).all() and np.isfinite(t).all(), f"state {index}: invalid input")
            require(raw["observed_anchor_valid"].all() and raw["observed_frame_mask"].all(), f"state {index}: invalid history")
            require(np.allclose(np.diff(t), .05, rtol=0, atol=1e-12), f"state {index}: history not uniform 50 ms")
            require(raw["observed_frame_indices"][-1] == sample["frame"] and
                    np.array_equal(raw["observed_frame_indices"], raw["oracle_source_frame_indices"]) and
                    np.array_equal(raw["observed_frame_indices"], np.arange(sample["frame"]-7, sample["frame"]+1)),
                    f"state {index}: noncausal or inconsistent frame indices")
            generated = arrays(archive, f"evaluation/dev/generation/state-{index:03}.npz", INPUT_FIELDS +
                               ("actual_object_values", "actual_object_feature_valid", "actual_object_access_mask"))
            for key in INPUT_FIELDS:
                require(np.array_equal(raw[key], generated[key]), f"state {index}: generation input changed: {key}")
            require(generated["actual_object_access_mask"].all(), f"state {index}: object history inaccessible")
            require(generated["actual_object_feature_valid"][-3:-1, 6:25].all() and
                    generated["actual_object_feature_valid"][-1, :6].all(), f"state {index}: kinematic features invalid")
            d = float(t[-1]-t[-2])
            v = (p[-1]-p[-2])/d
            v0, acceleration = (3*p[-1]-4*p[-2]+p[-3])/(2*d), (p[-1]-2*p[-2]+p[-3])/d**2
            plus = logarithm(multiply(q[-1], conjugate(q[-2])))/d
            minus = logarithm(multiply(q[-2], conjugate(q[-3])))/d
            w0, alpha = 1.5*plus-.5*minus, (plus-minus)/d
            actual = generated["actual_object_values"]
            np.testing.assert_array_equal(actual[-1, :3], p[-1])
            descriptor_differences.append([
                float(np.max(np.abs(actual[-2, 13:16]-v))),
                float(np.max(np.abs(actual[-2, 16:19]-plus))),
                float(np.max(np.abs(actual[-2, 19:22]-acceleration))),
                float(np.max(np.abs(actual[-2, 22:25]-alpha)))])
            observed.append(dict(index=index, sample=sample, p=p, q=q, t=t, v=v, v0=v0, a=acceleration,
                                 w=plus, w0=w0, alpha=alpha))
            row = dict(state_index=index, task=sample["task"], episode=sample["episode"], frame=sample["frame"], dt_s=d)
            for lag in range(3):
                row[f"time_minus_{lag}_s"] = float(t[-1-lag])
                for axis, value in zip("xyz", p[-1-lag]): row[f"p_minus_{lag}_{axis}_m"] = float(value)
                for axis, value in zip("xyzw", q[-1-lag]): row[f"q_minus_{lag}_{axis}"] = float(value)
            for name, values in (("cv_v_mps",v),("ca_v0_mps",v0),("ca_a_mps2",acceleration),
                                 ("cv_w_radps",plus),("ca_w0_radps",w0),("ca_alpha_radps2",alpha)):
                for axis, value in zip("xyz",values): row[f"{name}_{axis}"] = float(value)
            evidence_rows.append(row)
        require(len({(r["sample"]["episode"],r["sample"]["frame"]) for r in observed})==84, "duplicate states")
        require(len({r["sample"]["episode"] for r in observed})==28 and
                len({r["sample"]["task"] for r in observed})==14, "episode/task coverage differs")
        require(np.all(np.max(descriptor_differences,axis=0) < [1e-6,1e-5,1e-5,1e-3]),
                "observed kinematics differ from model-visible raw descriptors")
        h = HORIZONS[None, :, None]/1000
        cv_p = np.stack([r["v"] for r in observed])[:,None] * h
        ca_p = np.stack([r["v0"] for r in observed])[:,None]*h + .5*h*h*np.stack([r["a"] for r in observed])[:,None]
        cv_r = matrix(exponential(h*np.stack([r["w"] for r in observed])[:,None]))
        w0, alpha = np.stack([r["w0"] for r in observed]), np.stack([r["alpha"] for r in observed])
        ca_q = integrate_ca(w0, alpha, .001)
        fine_q = integrate_ca(w0, alpha, .0005)
        convergence = np.degrees(np.linalg.norm(logarithm(multiply(ca_q,conjugate(fine_q))),axis=-1))
        require(float(convergence.max()) < .001, "CA integration has not converged within 0.001 degree")
        ca_r = matrix(ca_q)
        errors = []
        # Phase 2: all CV/CA predictions now fixed; read future labels only for scoring.
        for obs in observed:
            index, sample = obs["index"], obs["sample"]
            keys = ("predicted_delta_position_m", "predicted_delta_rotation_matrix", "gt_delta_position_m",
                    "gt_delta_rotation_matrix", "translation_error_m", "rotation_error_rad", "future_anchor_valid",
                    "current_object_position_robot_base_m", "current_object_quaternion_robot_base_xyzw",
                    "future_anchor_position_robot_base_m", "future_anchor_quaternion_robot_base_xyzw")
            score = arrays(archive, f"evaluation/dev/scored/pose-state-{index:03}.npz", keys)
            require(score["future_anchor_valid"].all(), f"state {index}: invalid future target")
            np.testing.assert_array_equal(score["current_object_position_robot_base_m"], obs["p"][-1])
            # q and -q encode the same physical orientation; compare rotations.
            np.testing.assert_allclose(matrix(score["current_object_quaternion_robot_base_xyzw"]),
                                       matrix(obs["q"][-1]),atol=1e-12,rtol=0)
            np.testing.assert_allclose(score["gt_delta_position_m"], score["future_anchor_position_robot_base_m"].astype(np.float64)-obs["p"][-1], atol=1e-12,rtol=0)
            gt_rotation = matrix(multiply(unit(score["future_anchor_quaternion_robot_base_xyzw"]),conjugate(obs["q"][-1])))
            np.testing.assert_allclose(score["gt_delta_rotation_matrix"],gt_rotation,atol=1e-12,rtol=0)
            for method, pred_p, pred_r in (("P15",score["predicted_delta_position_m"],score["predicted_delta_rotation_matrix"]),
                                           ("CV",cv_p[index],cv_r[index]),("CA",ca_p[index],ca_r[index])):
                pe = 1000*np.linalg.norm(pred_p-score["gt_delta_position_m"],axis=-1)
                re = rotation_error(pred_r,score["gt_delta_rotation_matrix"])
                if method == "P15":
                    np.testing.assert_allclose(pe,score["translation_error_m"]*1000,rtol=1e-12,atol=1e-12)
                    np.testing.assert_allclose(re,np.degrees(score["rotation_error_rad"]),rtol=1e-12,atol=1e-10)
                for j,horizon in enumerate(HORIZONS):
                    row = dict(state_index=index,task=sample["task"],episode=sample["episode"],frame=sample["frame"],
                               horizon_ms=int(horizon),method=method,translation_error_mm=float(pe[j]),rotation_error_deg=float(re[j]))
                    for axis,value in zip("xyz",pred_p[j]): row[f"pred_d{axis}_m"]=float(value)
                    for a in range(3):
                        for b in range(3): row[f"pred_delta_R{a}{b}"]=float(pred_r[j,a,b])
                    errors.append(row)
    require(len(errors)==84*8*3,"error coverage mismatch")
    summaries=[]
    for horizon in [0]+HORIZONS.tolist():
        for method in ("P15","CV","CA"):
            selected=[r for r in errors if r["method"]==method and (not horizon or r["horizon_ms"]==horizon)]
            row=dict(scope="all_horizons" if not horizon else "per_horizon",horizon_ms=horizon,method=method,n_states=84,n_errors=len(selected),quantile_method="linear")
            for metric in ("translation_error_mm","rotation_error_deg"):
                values=np.array([r[metric] for r in selected])
                for stat,val in zip(("q25","median","q75"),np.quantile(values,[.25,.5,.75],method="linear")):
                    row[f"{metric}_{stat}"]=float(val)
                row[f"{metric}_mean"]=float(values.mean())
            summaries.append(row)
    wins={}
    for baseline in ("CV","CA"):
        wins[baseline]={}
        for metric in ("translation_error_mm","rotation_error_deg"):
            model=np.array([r[metric] for r in errors if r["method"]=="P15"]).reshape(84,8)
            base=np.array([r[metric] for r in errors if r["method"]==baseline]).reshape(84,8)
            wins[baseline][metric]=dict(p15_lower_state_mean=int((model.mean(1)<base.mean(1)).sum()),
                                       total_states=84,p15_lower_state_horizons=int((model<base).sum()),total_state_horizons=672)
    metadata = dict(
        methods=["P15","CV","CA"], source_archive=str(path.resolve()), numpy_version=np.__version__,
        source_script="kinematic_baselines.py", input_csv="prediction_examples_baseline_inputs.csv",
        errors_csv="prediction_examples_baseline_errors.csv", summary_csv="prediction_examples_aggregate.csv",
        error_rows=len(errors), states=84, episodes=28, tasks=14, valid_horizons_per_state=8,
        raw_history_available=True, input_fields=list(INPUT_FIELDS), history_spacing_s=.05,
        input_member_template="evaluation/dev/inputs/state-{index:03}.npz",
        input_units="Raw metres and scalar-last xyzw quaternions in robot-base coordinates; FP64 seconds. "
                    "Positions and quaternions are stored as FP32, converted to FP64 for analysis; quaternions normalized.",
        input_validation="All eight poses, frame masks and time differences valid for all 84 states; "
                         "oracle frame indices equal observed indices and end at the current frame. "
                         "Observed arrays equal generation audit arrays. Last two interval features and current "
                         "pose are model-accessible; derived kinematics match actual_object_values before normalization.",
        max_descriptor_differences_v_w_a_alpha=np.max(descriptor_differences,axis=0).tolist(),
        descriptor_difference_units=["m/s","rad/s","m/s^2","rad/s^2"],
        baseline_predictions_precede_label_reads=True,
        information_boundary="CV uses the last two observed GT poses; CA uses the last three. These are a subset "
                             "of P15's accessible GT history; P15 also receives visual and robot conditions. "
                             "No future label, instantaneous simulator velocity, fitting, smoothing or clipping enters prediction.",
        translation_cv="d=0.05 s; v=(p0-p[-1])/d; delta_p(h)=h*v.",
        translation_ca="v0=(3*p0-4*p[-1]+p[-2])/(2*d); a=(p0-2*p[-1]+p[-2])/d^2; "
                       "delta_p(h)=h*v0+0.5*h^2*a.",
        velocity_time="The final 50 ms interval velocity is centered at -25 ms; CA extrapolates v0 to "
                      "the current time. It does not read instantaneous simulation velocity.",
        rotation_cv="Object-to-robot-base R: w_plus=Log(R0*R[-1]^T)/d; delta_R(h)=Exp(h*[w_plus]_x).",
        rotation_ca="w_minus=Log(R[-1]*R[-2]^T)/d; w0=1.5*w_plus-0.5*w_minus; "
                    "alpha=(w_plus-w_minus)/d. Fixed robot-base spatial angular acceleration: "
                    "d(delta_R)/dt=[w0+t*alpha]_x*delta_R, delta_R(0)=I. "
                    "Interval angular velocities are assigned to -25 and -75 ms, then extrapolated to t=0.",
        integration="Float64 left-multiplied exponential midpoint; maximum 0.001 s step; quaternion renormalization.",
        convergence_reference_step_s=.0005, max_ca_integration_difference_deg=float(convergence.max()),
        scoring_validation="All 672 future targets valid; label-relative poses agree with current/future raw "
                           "poses, allowing quaternion sign equivalence. Recomputed P15 errors agree with saved scores.",
        all_horizons=summaries[:3], paired_descriptive_wins=wins,
        summary_scope="Each method has 672 dependent state-horizon errors from 84 states in 28 episodes. "
                      "Means and linear-method quartiles are descriptive, not 672 independent samples, "
                      "confidence intervals or training-seed robustness estimates.",
    )
    return dict(inputs=evidence_rows,errors=errors,summaries=summaries,metadata=metadata)


def export_analysis(analysis, destination=ROOT):
    write_csv(destination / "prediction_examples_baseline_inputs.csv",analysis["inputs"])
    write_csv(destination / "prediction_examples_baseline_errors.csv",analysis["errors"])
    write_csv(destination / "prediction_examples_aggregate.csv",analysis["summaries"])


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive",type=Path,default=ARCHIVE)
    result=analyze(parser.parse_args().archive)
    export_analysis(result)
    print(json.dumps(result["metadata"],indent=2))
