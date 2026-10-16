"""Plot accepted P15 / DEV84 pose predictions from their original report archive.

This is an offline target-pose diagnostic, not an online contact or rollout result.
The aggregate row compares P15, CV and CA per-horizon medians and interquartile
ranges across all 84 saved states. These ranges are not confidence intervals.
Selection: order all 84 states by mean eight-horizon translation L2 error, then
take nearest-rank 50th, 90th and 100th percentiles (ranks 42, 76, 84). Ties use
the original state index. RGB pixels and predictions are never synthesized.

Run with Python containing numpy, Pillow and pypdf; Chrome renders SVG to PDF.
At 6.875 in the smallest type is 8.25 pt. The source archive is read only.
"""

from pathlib import Path
import argparse
import base64
import csv
import io
import json
import math
import subprocess
import tarfile
import tempfile
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image
from pypdf import PdfReader
from kinematic_baselines import analyze, export_analysis


ROOT = Path(__file__).resolve().parent
DEFAULT_ARCHIVE = Path(
    "C:/workspace/se3-wam-research/local_private/future0-aux-20261012/"
    "P15-archive-aux-p15-reports-a36-low-priority-4g-a1-a1/"
    "reports-downloaded-20261013T110014343027Z.tar"
)
ACCEPTANCE = (
    "C:/workspace/se3-wam-research/docs/experiments/FUTURE0/results/"
    "auxiliary_supervision/P15_complete_report_archive_20261013.json"
)
REVIEW = ROOT.parent / "tmp" / "prediction-review"
EXAMPLE_OFFSET = 224
W, H = 660, 493 + EXAMPLE_OFFSET  # 96 CSS px/in, or 6.875 x 7.46875 in.
FONT = 11  # 8.25 pt.
INK, GRID, GT, PRED = "#252A30", "#DADDE2", "#454A50", "#7B4299"
METHOD_STYLES = (("P15", PRED, "4 2.4", "circle"),
                 ("CV", "#246BA0", None, "square"),
                 ("CA", "#BF6817", "1.2 2.4", "triangle"))
HORIZONS = np.arange(50, 401, 50)
SELECTION = ((0.5, "Median"), (0.9, "90th percentile"), (1.0, "Maximum"))
QUANTILE_METHOD = "linear"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(archive, member):
    return json.load(archive.extractfile(member))


def read_npz(archive, member):
    with np.load(io.BytesIO(archive.extractfile(member).read()), allow_pickle=False) as z:
        return {k: z[k] for k in z.files}


def load_data(path):
    with tarfile.open(path) as archive:
        accepted = read_json(archive, "evaluation/accepted.json")
        dev = read_json(archive, "evaluation/dev/accepted.json")
        epoch = read_json(archive, "control/epoch4.json")
        manifest = read_json(archive, "evaluation/dev/generation-manifest.json")
        require(accepted["accepted"] and accepted["arm"] == "P15", "P15 acceptance is missing")
        require(epoch["epoch"] == accepted["completed_epochs"] == 4, "expected final epoch 4")
        require(epoch["optimizer_step"] == accepted["optimizer_step"] == 40104,
                "expected the accepted 40104-update endpoint")
        require(epoch["global_samples_seen"] == 641664 and epoch["formal_training_credit"],
                "incorrect formal training exposure")
        require(dev["accepted"] and (dev["states"], dev["episodes"], dev["tasks"]) == (84, 28, 14),
                "expected complete accepted DEV84")
        require(dev["future_targets_after_all_generation"] and dev["original_noise_arrays_reused"],
                "offline prediction / target separation evidence is missing")
        require(manifest["complete"] and len(manifest["samples"]) == 84, "incomplete manifest")
        rows = []
        for index, sample in enumerate(manifest["samples"]):
            member = f"evaluation/dev/scored/pose-state-{index:03}.npz"
            pose = read_npz(archive, member)
            require(pose["future_anchor_valid"].shape == (8,) and pose["future_anchor_valid"].all(),
                    f"state {index}: selection requires all eight valid horizons")
            pred, gt = pose["predicted_delta_position_m"], pose["gt_delta_position_m"]
            require(pred.shape == gt.shape == (8, 3), f"state {index}: malformed translations")
            translation_error = np.linalg.norm(pred - gt, axis=-1)
            require(np.allclose(translation_error, pose["translation_error_m"], rtol=1e-6, atol=1e-9),
                    f"state {index}: recorded translation errors do not match positions")
            rp, rg = pose["predicted_delta_rotation_matrix"], pose["gt_delta_rotation_matrix"]
            require(rp.shape == rg.shape == (8, 3, 3), f"state {index}: malformed rotations")
            relative = rp @ np.swapaxes(rg, -1, -2)
            rotation_error = np.arccos(np.clip((np.trace(relative, axis1=-2, axis2=-1) - 1) / 2, -1, 1))
            require(np.allclose(rotation_error, pose["rotation_error_rad"], atol=2e-7),
                    f"state {index}: recorded rotation errors do not match matrices")
            require(np.isfinite(pred).all() and np.isfinite(gt).all() and np.isfinite(rotation_error).all(),
                    f"state {index}: nonfinite values")
            rows.append(dict(index=index, sample=sample, pose=pose, pose_member=member,
                             translation_error_mm=translation_error * 1000,
                             rotation_error_deg=np.rad2deg(rotation_error),
                             mean_translation_mm=float(translation_error.mean() * 1000),
                             mean_rotation_deg=float(np.rad2deg(rotation_error).mean())))
        rows.sort(key=lambda r: (r["mean_translation_mm"], r["index"]))
        selected = []
        for q, label in SELECTION:
            rank = math.ceil(q * len(rows))
            row = dict(rows[rank - 1], rank=rank, quantile=q, selection_label=label)
            member = f"evaluation/dev/inputs/state-{row['index']:03}.npz"
            data = read_npz(archive, member)
            require(data["rgb"].shape == (1, 8, 1, 3, 224, 224), "unexpected observation shape")
            require(data["rgb"].dtype == np.uint8, "expected original uint8 RGB")
            require(data["observed_frame_indices"][-1] == row["sample"]["frame"],
                    "state index / current observation mismatch")
            row["rgb"] = data["rgb"][0, -1, 0].transpose(1, 2, 0)
            row["current_time_s"] = float(data["observed_timestamp_s"][-1])
            row["input_member"] = member
            selected.append(row)
        return rows, selected, dict(accepted=accepted, dev=dev, epoch=epoch)


def aggregate_horizons(rows, analysis):
    require(len(rows) == len({r["index"] for r in rows}) == 84, "expected 84 distinct states")
    require(len({(r["sample"]["task"], r["sample"]["episode"], r["sample"]["frame"])
                 for r in rows}) == 84, "duplicate observed states")
    aggregate = {}
    for method, *_ in METHOD_STYLES:
        summary = [r for r in analysis["summaries"] if r["method"] == method and r["scope"] == "per_horizon"]
        require([r["horizon_ms"] for r in summary] == HORIZONS.tolist(), "aggregate horizon ordering differs")
        aggregate[method] = {key: np.array([[r[f"{key}_{stat}"] for r in summary]
                                          for stat in ("q25", "median", "q75")])
                             for key in ("translation_error_mm", "rotation_error_deg")}
    for key in ("translation_error_mm", "rotation_error_deg"):
        values = np.stack([r[key] for r in rows])
        require(values.shape == (84, 8) and np.isfinite(values).all(), "P15 aggregate coverage differs")
        np.testing.assert_allclose(aggregate["P15"][key], np.quantile(values, [0.25, 0.5, 0.75],
                                                                    axis=0, method=QUANTILE_METHOD))
    return aggregate


def export_data(path, rows, selected, evidence, analysis):
    selected_by_index = {r["index"]: r for r in selected}
    ranking_columns = ["rank", "state_index", "task", "episode", "frame", "mean_translation_error_mm",
                       "mean_rotation_error_deg", "valid_horizons", "selection"]
    with (ROOT / "prediction_examples_selection.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=ranking_columns)
        writer.writeheader()
        for rank, row in enumerate(rows, 1):
            s = row["sample"]
            writer.writerow(dict(rank=rank, state_index=row["index"], task=s["task"], episode=s["episode"],
                                 frame=s["frame"], mean_translation_error_mm=row["mean_translation_mm"],
                                 mean_rotation_error_deg=row["mean_rotation_deg"], valid_horizons=8,
                                 selection=selected_by_index.get(row["index"], {}).get("selection_label", "")))
    curve_columns = ["selection", "rank", "state_index", "task", "episode", "frame", "current_time_s",
                     "horizon_ms", "pred_dx_m", "pred_dy_m", "pred_dz_m", "gt_dx_m", "gt_dy_m", "gt_dz_m",
                     "translation_error_m", "rotation_error_rad"]
    with (ROOT / "prediction_examples_data.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=curve_columns)
        writer.writeheader()
        for row in selected:
            p, s = row["pose"], row["sample"]
            for h, horizon in enumerate(HORIZONS):
                out = dict(selection=row["selection_label"], rank=row["rank"], state_index=row["index"],
                           task=s["task"], episode=s["episode"], frame=s["frame"],
                           current_time_s=row["current_time_s"], horizon_ms=int(horizon),
                           translation_error_m=float(p["translation_error_m"][h]),
                           rotation_error_rad=float(p["rotation_error_rad"][h]))
                for axis, component in enumerate("xyz"):
                    out[f"pred_d{component}_m"] = float(p["predicted_delta_position_m"][h, axis])
                    out[f"gt_d{component}_m"] = float(p["gt_delta_position_m"][h, axis])
                writer.writerow(out)
    export_analysis(analysis)
    provenance = dict(
        source_archive=str(path.resolve()), research_acceptance=ACCEPTANCE,
        source_members=["evaluation/accepted.json", "evaluation/dev/accepted.json", "control/epoch4.json",
                        "evaluation/dev/generation-manifest.json"],
        run_id=evidence["epoch"]["run_id"], arm="P15", training_seed=0, epochs=4,
        optimizer_steps=40104, global_samples=641664,
        dev_states=84, dev_episodes=28, dev_tasks=14, valid_horizons_per_state=8,
        aggregate=dict(
            data_csv="prediction_examples_aggregate.csv", horizons_ms=HORIZONS.tolist(),
            methods=[style[0] for style in METHOD_STYLES],
            n_states_per_horizon=[len(rows)] * len(HORIZONS),
            errors="Translation: norm(predicted_delta_position_m - gt_delta_position_m) * 1000; "
                   "rotation: acos(clip((trace(R_pred @ R_gt.T) - 1) / 2, -1, 1)) * 180 / pi. "
                   "P15 recomputed from every saved pose and checked against recorded errors; "
                   "CV/CA constructed only from observed GT poses.",
            summary="Equal weight per state at each horizon; median line and 25th–75th percentile band.",
            quantiles=[0.25, 0.5, 0.75], quantile_method=QUANTILE_METHOD,
            quantile_definition="Sort the 84 errors at each horizon; linearly interpolate at "
                                "zero-based rank (84 - 1) * q (NumPy method='linear').",
            numpy_version=np.__version__,
            scope="Descriptive spread across all 84 saved states (28 episodes, 14 tasks), including "
                  "dependent states. CSV additionally reports each method's mean/median over 672 dependent "
                  "state-horizon errors. No confidence interval, resampling or training-seed robustness claim.",
        ),
        kinematic_baselines=analysis["metadata"],
        selection_rule="Sort all 84 states by arithmetic mean of the eight translation L2 errors; "
                       "break ties by original state index. Select nearest-rank percentiles 50, 90, 100 "
                       "(ranks 42, 76, 84). This is a diagnostic selection, not a random sample.",
        pose_definition="Independent cumulative translation in robot-base coordinates and left-relative "
                        "rotation. Rotation error is the SO(3) geodesic angle, shown in degrees.",
        image_definition="Uncropped last observed agentview RGB, original 224x224 uint8 pixels.",
        input_condition="Original P15 GT current_kinematics object input; the displayed RGB is one input view, "
                        "not the full conditioning information.",
        scope="Saved offline DEV84 target-pose readout versus the recorded demonstration future. "
              "No contact timing, counterfactual action validity, closed-loop success or uncertainty claim.",
        selected=[dict(state_index=r["index"], rank=r["rank"], label=r["selection_label"],
                       sample=r["sample"], current_time_s=r["current_time_s"],
                       input_member=r["input_member"], pose_member=r["pose_member"],
                       generation_member=f"evaluation/dev/generation/state-{r['index']:03}.npz",
                       mean_translation_error_mm=r["mean_translation_mm"],
                       mean_rotation_error_deg=r["mean_rotation_deg"]) for r in selected],
    )
    (ROOT / "prediction_examples_source.json").write_text(json.dumps(provenance, indent=2) + "\n", encoding="utf-8")


def text(svg, x, y, value, size=FONT, weight="normal", color=INK, anchor="start"):
    svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" font-weight="{weight}" '
               f'fill="{color}" text-anchor="{anchor}">{escape(str(value))}</text>')


def line(svg, x1, y1, x2, y2, color=GRID, width=.65, dash=None):
    svg.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" '
               f'stroke-width="{width:g}"' + (f' stroke-dasharray="{dash}"' if dash else "") + '/>')


def marker(svg, x, y, color, shape="circle"):
    if shape == "circle":
        svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="1.65" fill="{color}"/>')
    elif shape == "square":
        svg.append(f'<rect x="{x-1.7:.3f}" y="{y-1.7:.3f}" width="3.4" height="3.4" fill="{color}"/>')
    elif shape == "triangle":
        svg.append(f'<polygon points="{x:.3f},{y-2.2:.3f} {x-2.1:.3f},{y+1.7:.3f} '
                   f'{x+2.1:.3f},{y+1.7:.3f}" fill="{color}"/>')


def plot(svg, x, y, width, height, series, limits, bands=(), markers=None):
    low, high, ticks = limits
    px = lambda value: x + (value - 50) / 350 * width
    py = lambda value: y + height - (value - low) / (high - low) * height
    for tick in ticks:
        line(svg, x, py(tick), x + width, py(tick))
        label = f"{tick:g}".replace("-", "−")
        text(svg, x - 5, py(tick) + 3.6, label, anchor="end", color="#555B62")
    line(svg, x, y, x, y + height, color="#A8ACB2")
    line(svg, x, y + height, x + width, y + height, color="#A8ACB2")
    for tick in (50, 200, 400):
        line(svg, px(tick), y + height, px(tick), y + height + 3, color="#A8ACB2")
        text(svg, px(tick), y + height + 15, tick, anchor="middle", color="#555B62")
    for lower, upper, color in bands:
        require(np.all(lower >= low) and np.all(upper <= high), "axis would truncate an IQR band")
        boundary = list(zip(HORIZONS, lower)) + list(zip(HORIZONS[::-1], upper[::-1]))
        points = " ".join(f"{px(h):.3f},{py(v):.3f}" for h, v in boundary)
        svg.append(f'<polygon points="{points}" fill="{color}" fill-opacity="0.12"/>')
    for i, (values, color, dash) in enumerate(series):
        points = " ".join(f"{px(h):.3f},{py(v):.3f}" for h, v in zip(HORIZONS, values))
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="1.55" '
                   f'stroke-linejoin="round" stroke-linecap="round"' + (f' stroke-dasharray="{dash}"' if dash else "") + '/>')
        for h, v in zip(HORIZONS, values):
            marker(svg, px(h), py(v), color, markers[i] if markers else "circle")


def nice_limits(values, nonnegative=False, intervals=3):
    lo, hi = min(0.0, float(np.min(values))), max(0.0, float(np.max(values)))
    span = max(hi - lo, .01)
    rough = span / intervals
    base = 10 ** math.floor(math.log10(rough))
    step = next(v * base for v in (1, 2, 2.5, 5, 10) if v * base >= rough)
    lower = 0.0 if nonnegative else math.floor(lo / step) * step
    upper = math.ceil(hi / step) * step
    if upper == lower:
        upper = lower + step
    ticks = np.arange(lower, upper + step * .1, step)
    return lower - (0 if nonnegative else step * .08), upper + step * .08, ticks


def draw(selected, aggregate):
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="Arial, Helvetica, sans-serif">']
    text(svg, 12, 13, "All 84 states: median (line) and 25th–75th percentile (band)", weight="bold")
    for x, (method, color, dash, shape) in zip((220, 310, 400), METHOD_STYLES):
        svg.append(f'<rect x="{x}" y="22" width="25" height="9" fill="{color}" fill-opacity="0.12"/>')
        line(svg, x, 26.5, x+25, 26.5, color=color, width=1.55, dash=dash)
        marker(svg, x+12.5, 26.5, color, shape)
        text(svg, x+31, 30, method)
    for x, detail_x, width, key, title, intervals, detail_limits in (
        (42, 200, 110, "translation_error_mm", "Translation L2 error (mm)", 5,
         (0.0, 8.0, (0, 4, 8))),
        (382, 536, 108, "rotation_error_deg", "Rotation geodesic error (°)", 3,
         (0.0, 1.2, (0, .6, 1.2))),
    ):
        series = [(aggregate[method][key][1], color, dash) for method, color, dash, _ in METHOD_STYLES]
        bands = [(aggregate[method][key][0], aggregate[method][key][2], color)
                 for method, color, *_ in reversed(METHOD_STYLES)]
        upper = np.concatenate([aggregate[method][key][2] for method, *_ in METHOD_STYLES])
        text(svg, (x + detail_x + width) / 2, 49, title, weight="bold", anchor="middle")
        text(svg, x + width / 2, 67, "Median + IQR", anchor="middle")
        text(svg, detail_x + width / 2, 67, "Median detail", anchor="middle")
        plot(svg, x, 80, width, 108, series, nice_limits(upper, nonnegative=True, intervals=intervals),
             bands=bands, markers=[style[3] for style in METHOD_STYLES])
        # Replot the exact same medians on an expanded linear scale. The
        # adjacent overview retains the complete original IQR and axis limits.
        require(all(np.all((values >= detail_limits[0]) & (values <= detail_limits[1]))
                    for values, *_ in series), "median-detail axis would truncate a curve")
        plot(svg, detail_x, 80, width, 108, series, detail_limits,
             markers=[style[3] for style in METHOD_STYLES])
        text(svg, (x + detail_x + width) / 2, 218, "Prediction horizon (ms)", anchor="middle")
    svg.append(f'<g transform="translate(0,{EXAMPLE_OFFSET})">')
    columns = [(158, 91), (285, 91), (412, 91), (548, 96)]
    text(svg, 67, 16, "Current RGB", weight="bold", anchor="middle")
    for (x, width), title in zip(columns, ("Δx (mm)", "Δy (mm)", "Δz (mm)", "Rotation error (°)")):
        text(svg, x + width / 2, 16, title, weight="bold", anchor="middle")
    line(svg, 186, 31, 211, 31, color=GT, width=1.55)
    text(svg, 217, 35, "GT")
    line(svg, 260, 31, 285, 31, color=PRED, width=1.55, dash="4 2.4")
    text(svg, 291, 35, "P15 prediction")
    text(svg, 425, 35, "Robot-base Δp", color="#555B62")
    task_names = {"t1_belt": "T1-Belt", "t4_sphere_tabletop": "Supported sphere", "t4_can": "Supported can"}
    for i, row in enumerate(selected):
        top = 43 + 142 * i
        p = row["pose"]
        text(svg, 12, top + 13,
             f"({chr(97+i)}) {row['selection_label']} ({row['rank']}/84) · {task_names[row['sample']['task']]}",
             weight="bold")
        text(svg, 645, top + 13,
             f"Mean L2: {row['mean_translation_mm']:.2f} mm   |   Mean rotation: {row['mean_rotation_deg']:.2f}°",
             anchor="end", color="#555B62")
        image_bytes = io.BytesIO()
        Image.fromarray(row["rgb"]).save(image_bytes, format="PNG")
        payload = base64.b64encode(image_bytes.getvalue()).decode("ascii")
        svg.append(f'<image x="12" y="{top+22}" width="110" height="110" '
                   f'href="data:image/png;base64,{payload}"/>')
        text(svg, 67, top + 143, f"t = {row['current_time_s']:.2f} s", anchor="middle", color="#555B62")
        for axis, (x, width) in enumerate(columns[:3]):
            gt = p["gt_delta_position_m"][:, axis] * 1000
            pred = p["predicted_delta_position_m"][:, axis] * 1000
            plot(svg, x, top + 31, width, 85,
                 [(gt, GT, None), (pred, PRED, "4 2.4")], nice_limits(np.concatenate((gt, pred))))
        x, width = columns[-1]
        degrees = np.rad2deg(p["rotation_error_rad"])
        plot(svg, x, top + 31, width, 85, [(degrees, PRED, "4 2.4")], nice_limits(degrees, nonnegative=True))
    text(svg, 405, 478, "Prediction horizon (ms)", anchor="middle")
    text(svg, 12, 491, "Offline DEV84 · original GT-kinematics input · selected by 8-step mean translation error", color="#555B62")
    svg += ["</g>", "</g>", "</svg>"]
    return "\n".join(svg)


def render(svg):
    browser = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    require(browser.is_file(), "Chrome renderer is required")
    REVIEW.mkdir(parents=True, exist_ok=True)
    payload = base64.b64encode(svg.read_bytes()).decode("ascii")
    html = (f'<!doctype html><meta charset="utf-8"><style>@page{{size:{W}px {H}px;margin:0}}'
            f'html,body{{width:{W}px;height:{H}px;margin:0;overflow:hidden}}'
            f'img{{display:block;width:{W}px;height:{H}px}}</style>'
            f'<img src="data:image/svg+xml;base64,{payload}">')
    with tempfile.TemporaryDirectory(prefix="render-", dir=REVIEW) as tmp:
        tmp = Path(tmp)
        page = tmp / "figure.html"
        page.write_text(html, encoding="utf-8")
        common = [str(browser), "--headless=new", "--disable-gpu", f"--user-data-dir={tmp/'profile'}",
                  "--no-pdf-header-footer"]
        commands = [common + [f"--print-to-pdf={svg.with_suffix('.pdf')}", page.as_uri()]]
        for suffix, scale in (("", 3), ("_actual_size", 1)):
            image = REVIEW / f"prediction_examples{suffix}.png"
            commands.append(common + [f"--force-device-scale-factor={scale}", f"--window-size={W},{H}",
                                      f"--screenshot={image}", page.as_uri()])
        for command in commands:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8")
            require(result.returncode == 0, result.stderr)
    pdf = PdfReader(svg.with_suffix(".pdf"))
    require(len(pdf.pages) == 1, "expected a one-page figure")
    box = pdf.pages[0].mediabox
    require(abs(float(box.width) - W * .75) < 1 and abs(float(box.height) - H * .75) < 1,
            "PDF dimensions changed")
    require("Mean L2" in pdf.pages[0].extract_text(), "PDF text layer missing")
    require("All 84 states" in pdf.pages[0].extract_text(), "aggregate row missing from PDF")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    args = parser.parse_args()
    # Fix all baselines from observed inputs before any future labels are read.
    analysis = analyze(args.archive)
    rows, selected, evidence = load_data(args.archive)
    aggregate = aggregate_horizons(rows, analysis)
    export_data(args.archive, rows, selected, evidence, analysis)
    svg = ROOT / "prediction_examples.svg"
    svg.write_text(draw(selected, aggregate), encoding="utf-8")
    render(svg)
    print(json.dumps(dict(arm="P15", source_states=len(rows), selected=[
        dict(state_index=r["index"], task=r["sample"]["task"], rank=r["rank"],
             mean_translation_mm=r["mean_translation_mm"], mean_rotation_deg=r["mean_rotation_deg"])
        for r in selected], aggregate_csv=str(ROOT / "prediction_examples_aggregate.csv"),
        svg=str(svg), pdf=str(svg.with_suffix(".pdf"))), indent=2))


if __name__ == "__main__":
    main()
