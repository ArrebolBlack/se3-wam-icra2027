"""Rebuild the fixed-readout failure figure from retained, real GRIPPER2 records.

python figures/plot_decoder_failures.py --extract [--research-root <Research>]
python figures/plot_decoder_failures.py

Extraction is read-only in Research; plotting needs only the adjacent CSV/JSON.
No model execution, training, rollout, smoothing, or interpolated measurements.
"""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scripts"))
from common import REVIEW, figure_parser, research_root
from common import read_csv as load_csv, read_json as read, write_csv as dump_csv

PREFIX = "decoder_failures"
MODES = ("sign", "deadband", "learned")
LABELS = {"sign": "Sign", "deadband": "Fixed 0.1", "learned": "Learned"}
COLORS = {"sign": "#3E6787", "deadband": "#008875", "learned": "#D55E00"}
STYLES = {"sign": "-", "deadband": (0, (3, 1.6)), "learned": "-"}
CASE_NAMES = ("t4_sphere:000052", "t5_replan:000035")


def episode(root, scenario):
    matches = []
    for path in root.rglob("completed-episodes.json"):
        for row in read(path):
            if row["scenario_id"] == scenario:
                matches.append(path.parent / Path(row["result"]).name)
    assert len(matches) == 1, (root, scenario, matches)
    return matches[0]


def physical(path, sphere):
    source = path.with_suffix(".trace.npz" if sphere else ".physics.npz")
    with np.load(source, allow_pickle=False) as z:
        states, columns = z["states"], z["columns"].tolist()
    assert states.shape[1] == len(columns) and np.isfinite(states).all()
    x = {k: states[:, i] for i, k in enumerate(columns)}
    assert np.allclose(np.diff(x["time_s"]), 0.002, rtol=0, atol=1e-10)
    x["aperture_mm"] = abs(x["finger_left_qpos"] - x["finger_right_qpos"]) * 1000
    x["raw_bilateral_contact"] = ((x["left_pad_contact"] != 0) & (x["right_pad_contact"] != 0)).astype(int)
    return x, source


def first_difference(a, b, columns, threshold):
    n = min(len(a["time_s"]), len(b["time_s"]))
    assert np.array_equal(a["time_s"][:n], b["time_s"][:n])
    delta = np.max(np.column_stack([abs(a[k][:n] - b[k][:n]) for k in columns]), axis=1)
    found = np.flatnonzero(delta >= threshold)
    assert len(found)
    return float(a["time_s"][found[0]])


def extract(research):
    public = research / "docs/experiments/GRIPPER2/results/learned"
    audit = read(public / "regression-audit.json")
    diagnosis = read(public / "failure-diagnosis.json")
    assert audit["audit_accepted"] and audit["successes"] == 9 and audit["n"] == 11
    assert not audit["fresh_rollout_permitted"] and not audit["production_default_changed"]
    failures = [r for r in audit["cases"] if not r["native"]["success"]]
    assert {r["scenario_id"].removeprefix("v1:validation:") for r in failures} == set(CASE_NAMES)
    commands, samples, cases = [], [], []
    for name in CASE_NAMES:
        sid = "v1:validation:" + name
        case = next(r for r in diagnosis["cases"] if r["scenario_id"] == sid)
        sphere = name.startswith("t4_sphere:")
        delay = 0 if sphere else 1
        roots = {"learned": research / "local_private/gripper-learned-20261017-a6/collected/final/learned/regression-e5"}
        for mode in ("sign", "deadband"):
            roots[mode] = research / "local_private" / case["reference_source"] / "collected" / (
                f"GRIPPER0/epoch5-{mode}" if sphere else f"mechanism/epoch5/{mode}")
        controls, physics, native, sources = {}, {}, {}, {}
        for mode in MODES:
            path = episode(roots[mode], sid)
            controls[mode] = read(path.with_suffix(".control.json"))
            physics[mode], source = physical(path, sphere)
            native[mode] = read(path)["results"][0]
            assert native[mode] == case["modes"][mode]["native"]
            sources[mode] = {"native": path.relative_to(research).as_posix(),
                "commands": path.with_suffix(".control.json").relative_to(research).as_posix(),
                "physics": source.relative_to(research).as_posix()}
            for i, r in enumerate(controls[mode]["actions"]):
                assert r["tick"] == i and abs(r["time_s"] - i * .05) < 1e-10
                applied_s = (i + delay) * .05
                commands.append(dict(case=name, mode=mode, issued_tick=i, applied_tick=i + delay,
                    issued_s=float(r["time_s"]), applied_s=applied_s,
                    raw_g=float(r["raw_prediction"][6]), command=float(r["command"][6]),
                    applied_before_terminal=int(applied_s < native[mode]["elapsed_s"] - 1e-10)))
            x = physics[mode]
            for i in range(len(x["time_s"])):
                samples.append(dict(case=name, mode=mode, time_s=float(x["time_s"][i]),
                    aperture_mm=float(x["aperture_mm"][i]),
                    left_pad_contact=int(x["left_pad_contact"][i] != 0),
                    right_pad_contact=int(x["right_pad_contact"][i] != 0),
                    raw_bilateral_contact=int(x["raw_bilateral_contact"][i]),
                    attachment_active=int(x["attachment_active"][i]) if "attachment_active" in x else "",
                    eef_x_m=float(x["eef_x"][i]), eef_y_m=float(x["eef_y"][i]), eef_z_m=float(x["eef_z"][i]),
                    object_x_m=float(x["object_x"][i]), object_y_m=float(x["object_y"][i]), object_z_m=float(x["object_z"][i])))
        t = case["first_change"]["issued_tick"]
        applied_s = case["first_change"]["applied_tick"] * .05
        assert t + delay == case["first_change"]["applied_tick"]
        assert controls["learned"]["actions"][t]["raw_prediction"][6] == case["first_change"]["raw_gripper"]
        assert controls["learned"]["actions"][t]["command"][6] == 1
        checks = {}
        for mode in ("sign", "deadband"):
            assert controls[mode]["actions"][t]["command"][6] == -1
            for key in ("scenario_id", "source_seed", "inference_seed", "index"):
                assert controls[mode]["scenario"][key] == controls["learned"]["scenario"][key]
            raw = lambda m: np.array([r["raw_prediction"] for r in controls[m]["actions"]])
            command = lambda m: np.array([r["command"] for r in controls[m]["actions"]])
            assert np.array_equal(raw(mode)[:t+1], raw("learned")[:t+1])
            assert np.array_equal(command(mode)[:t], command("learned")[:t])
            x, y = physics[mode], physics["learned"]
            n = min(len(x["time_s"]), len(y["time_s"]))
            assert np.array_equal(x["time_s"][:n], y["time_s"][:n])
            mask = x["time_s"][:n] <= applied_s
            keys = sorted(set(x) & set(y))
            assert all(np.array_equal(x[k][:n][mask], y[k][:n][mask]) for k in keys)
            calculated = dict(
                aperture_first_10um_difference_s=first_difference(x, y, ["aperture_mm"], .01),
                eef_first_10um_difference_s=first_difference(x, y, ["eef_"+d for d in "xyz"], 1e-5),
                object_first_10um_difference_s=first_difference(x, y, ["object_"+d for d in "xyz"], 1e-5))
            for key, val in calculated.items():
                assert val == case["comparisons"][mode][key]
            q, r = command(mode), command("learned")
            count = min(len(q), len(r))
            arm_tick = int(np.flatnonzero(np.max(abs(q[:count, :6]-r[:count, :6]), axis=1) >= 1e-5)[0])
            assert arm_tick == case["comparisons"][mode]["first_arm_command_difference_tick"]
            for m in (mode, "learned"):
                x0 = physics[m]
                i = int(np.argmin(abs(x0["time_s"] - (applied_s + .05))))
                assert abs(x0["aperture_mm"][i] - case["modes"][m]["one_tick_after"]["aperture_m"]*1000) < 1e-12
            checks[mode] = dict(recorded_raw_prefix_exact=True, recorded_command_prefix_exact=True,
                physical_prefix_exact=True, physical_fields_compared=len(keys),
                first_arm_command_difference_tick=arm_tick, **calculated)
        for mode in MODES:
            x = physics[mode]
            indices = np.flatnonzero(x["raw_bilateral_contact"])
            contact = None if not len(indices) else float(x["time_s"][indices[0]])
            assert contact == case["modes"][mode]["raw_bilateral_first_s"]
            if "attachment_active" in x:
                ids = np.flatnonzero(x["attachment_active"])
                attach = None if not len(ids) else float(x["time_s"][ids[0]])
                assert attach == case["modes"][mode]["attachment_first_s"]
        cases.append(dict(name=name, epoch=5, delay_ticks=delay, first_change=case["first_change"],
            modes=case["modes"], sources=sources, recomputed=checks,
            local_window_s=[.55, .90] if sphere else [1.40, 1.80],
            full_window_s=[0, 2.05] if sphere else [0, 5.5]))
    dump_csv(HERE / f"{PREFIX}_commands.csv", commands)
    dump_csv(HERE / f"{PREFIX}_physics.csv", samples)
    source = dict(selection="All two failures in the prespecified 11-case known-counterexample regression; 9/11 is not a random-sample success rate.",
        source_report="docs/experiments/GRIPPER2/results/learned/failure-diagnosis.json",
        source_audit="docs/experiments/GRIPPER2/results/learned/regression-audit.json",
        evidence_scope="Recorded raw predictions, commands, and 2 ms physical prefixes. Complete per-frame Policy input tensors were not recorded.",
        command_clock="issued_s=tick/20; applied_s=(tick+delay_ticks)/20. The final queued command is excluded when it has not executed before the terminal event.",
        physics_clock="2 ms samples; aperture is abs(left_qpos-right_qpos) in mm; bilateral contact is the conjunction of actual left/right pad collision flags. Attachment is a separate state.",
        divergence_detection="First componentwise absolute position difference >=10 micrometers; aperture difference >=10 micrometers; arm-command threshold is 1e-5.",
        display="No smoothing or decimation. Commands/aperture show the declared local window. Event strips span the complete episode, clipped only at the native terminal time. Full original sample rows are retained in CSV.",
        aggregate=dict(known_cases=11, passed=9, new_420_runs_permitted=False, production_default_changed=False),
        cases=cases, exported_rows=dict(commands=len(commands), physics=len(samples)))
    (HERE / f"{PREFIX}_source.json").write_text(json.dumps(source, indent=2, allow_nan=False)+"\n", encoding="utf-8")
    print(json.dumps({"exported_rows": source["exported_rows"], "recomputed": {c["name"]: c["recomputed"] for c in cases}}))


def values(rows, field):
    return np.array([float(r[field]) for r in rows])


def segments(time, active, stop):
    """2 ms left-constant recorded contact intervals, truncated at termination."""
    active = np.asarray(active, dtype=bool) & (time < stop)
    padded = np.r_[False, active, False]
    starts = np.flatnonzero(np.diff(padded.astype(int)) == 1)
    ends = np.flatnonzero(np.diff(padded.astype(int)) == -1)
    return [(float(time[s]), min(float(time[e-1]+.002), stop)-float(time[s])) for s, e in zip(starts, ends)]


def axis_style(ax, window):
    ax.set_xlim(window)
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#9AA0A6")
    ax.tick_params(length=2.2, pad=2)
    ax.grid(axis="y", color="#E5E7EB", lw=.5, zorder=0)
    ax.set_axisbelow(True)


def plot():
    source = read(HERE / f"{PREFIX}_source.json")
    commands = load_csv(HERE / f"{PREFIX}_commands.csv")
    physics = load_csv(HERE / f"{PREFIX}_physics.csv")
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
        "axes.labelsize": 8, "axes.titlesize": 9, "xtick.labelsize": 7.5, "ytick.labelsize": 7.5,
        "axes.linewidth": .65, "svg.fonttype": "none", "pdf.fonttype": 42,
        "path.simplify": False})
    fig = plt.figure(figsize=(178/25.4, 150/25.4), facecolor="white")
    grid = fig.add_gridspec(2, 3, left=.078, right=.99, top=.865, bottom=.11,
        width_ratios=[1.03, 1.04, 1.43], wspace=.34, hspace=.65)
    handles = [Line2D([0], [0], color=COLORS[m], linestyle=STYLES[m], lw=1.5, label=LABELS[m]) for m in MODES]
    handles += [Patch(facecolor="#545454", label="Bilateral pad contact"),
        Patch(facecolor="white", edgecolor="#545454", hatch="////", label="Attachment")]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.515, .995), ncol=5,
        frameon=False, fontsize=7.8, handlelength=1.5, columnspacing=1.1)
    for row, case in enumerate(source["cases"]):
        name = case["name"]
        local, full = case["local_window_s"], case["full_window_s"]
        change = case["first_change"]
        issued_s, applied_s = change["issued_tick"]*.05, change["applied_tick"]*.05
        sub = grid[row, 0].subgridspec(2, 1, hspace=.23)
        raw_ax, cmd_ax = fig.add_subplot(sub[0]), fig.add_subplot(sub[1])
        aperture_grid = grid[row, 1].subgridspec(2, 1, height_ratios=[3.1, 1], hspace=.72)
        ap_ax = fig.add_subplot(aperture_grid[0])
        note_ax = fig.add_subplot(aperture_grid[1]); note_ax.axis("off")
        event_ax = fig.add_subplot(grid[row, 2])
        for ax in (raw_ax, cmd_ax, ap_ax):
            axis_style(ax, local)
        for mode in MODES:
            cr = [r for r in commands if r["case"] == name and r["mode"] == mode]
            pr = [r for r in physics if r["case"] == name and r["mode"] == mode]
            color, style = COLORS[mode], STYLES[mode]
            raw_ax.plot(values(cr, "issued_s"), values(cr, "raw_g"), color=color, ls=style, lw=1.05,
                marker="o", ms=2.1)
            executed = [r for r in cr if int(r["applied_before_terminal"])]
            tx, cy = values(executed, "applied_s"), values(executed, "command")
            cmd_ax.step(np.r_[tx, case["modes"][mode]["native"]["elapsed_s"]], np.r_[cy, cy[-1]],
                where="post", color=color, ls=style, lw=1.15)
            ap_ax.plot(values(pr, "time_s"), values(pr, "aperture_mm"), color=color, ls=style, lw=1.25)
            i = int(np.argmin(abs(values(pr, "time_s")-(applied_s+.05))))
            ap_ax.plot(applied_s+.05, float(pr[i]["aperture_mm"]), "o", color=color, ms=3, zorder=5)
        raw_ax.axvline(issued_s, color="#555555", ls=":", lw=.8)
        for ax in (cmd_ax, ap_ax):
            ax.axvspan(applied_s, applied_s+.05, color="#D55E00", alpha=.085, lw=0)
            ax.axvline(applied_s, color="#555555", ls=":", lw=.8)
        raw_ax.set_ylim(-1.22, 1.22); raw_ax.set_yticks([-1, 0, 1]); raw_ax.set_ylabel("Raw $g$")
        raw_ax.tick_params(labelbottom=False)
        cmd_ax.set_ylim(-1.22, 1.22); cmd_ax.set_yticks([-1, 0, 1]); cmd_ax.set_ylabel("Applied\ncommand")
        cmd_ax.set_xlabel("Time (s), local window")
        ap_ax.set_xlabel("Time (s), same local window")
        ap_ax.set_ylabel("Aperture (mm)", labelpad=2)
        # Cover every aperture sample in the declared local window.
        visible = [float(r["aperture_mm"]) for r in physics if r["case"] == name
            and local[0]-1e-9 <= float(r["time_s"]) <= local[1]+1e-9]
        ap_ax.set_ylim(min(visible)-.5, max(visible)+.6)
        ap_ax.set_yticks([60, 70, 80] if row == 0 else [76, 78, 80])
        ticks = [.6, .7, .8, .9] if row == 0 else [1.4, 1.5, 1.6, 1.7, 1.8]
        for ax in (raw_ax, cmd_ax, ap_ax):
            ax.set_xticks(ticks)
        baseline = case["modes"]["sign"]["one_tick_after"]["aperture_m"]*1000
        learned = case["modes"]["learned"]["one_tick_after"]["aperture_m"]*1000
        divergence = case["recomputed"]["sign"]["aperture_first_10um_difference_s"]
        note_ax.text(0, 1,
            f"Separation: {divergence:.3f} s\nAt {applied_s+.05:.3f} s:\nSign / 0.1: {baseline:.2f} mm\nLearned: {learned:.2f} mm",
            transform=note_ax.transAxes, va="top", fontsize=7.8, linespacing=1.3)
        raw_ax.set_title("Issued prediction", loc="left", pad=4)
        ap_ax.set_title("Physical response", loc="left", pad=4)
        event_ax.set_title("Contact and outcome (full episode)", loc="left", pad=4, fontsize=8.6)
        event_ax.set_xlim(full); event_ax.set_ylim(-.32, 3.65)
        event_ax.spines[["top", "right", "left"]].set_visible(False)
        event_ax.spines["bottom"].set_color("#9AA0A6")
        event_ax.set_yticks([]); event_ax.set_xlabel("Time (s), full episode")
        event_ax.tick_params(length=2.2, pad=2)
        event_ax.set_xticks([0, .5, 1, 1.5, 2] if row == 0 else [0, 1, 2, 3, 4, 5])
        event_ax.axvline(applied_s, color="#666666", ls=":", lw=.8, zorder=0)
        check = case["recomputed"]["sign"]
        for key, marker, text, y in (("eef", "D", "EEF", 3.24), ("object", "o", "Object", 2.87)):
            t = check[key+"_first_10um_difference_s"]
            event_ax.plot(t, y, marker=marker, color="#555555", ms=3)
            event_ax.text(t + .03*(full[1]-full[0]), y, f"{text} {t:.3f}", va="center", fontsize=7.6)
        event_ax.text(.01, 3.59, "First separation from Sign (10 µm)", fontsize=7.5, va="top")
        for mode, y in zip(MODES, (2.04, 1.03, .02)):
            info = case["modes"][mode]
            stop = info["native"]["elapsed_s"]
            pr = [r for r in physics if r["case"] == name and r["mode"] == mode]
            time = values(pr, "time_s")
            event_ax.plot([0, stop], [y, y], color=COLORS[mode], alpha=.3, lw=.7)
            bars = segments(time, values(pr, "raw_bilateral_contact"), stop)
            event_ax.broken_barh(bars, (y-.055, .11), color=COLORS[mode], linewidth=0)
            if case["delay_ticks"]:
                bars = segments(time, values(pr, "attachment_active"), stop)
                event_ax.broken_barh(bars, (y+.10, .11), facecolor="white", edgecolor=COLORS[mode], hatch="////", linewidth=.35)
            event_ax.plot(stop, y, marker="|", color=COLORS[mode], markersize=7, mew=1.25)
            outcome = "success" if info["native"]["success"] else (
                "tray contact" if info["native"]["failure_code"] == "tray_contact" else "downstream exit")
            event_ax.text(0, y+.35, f"{LABELS[mode]}: {outcome}, {stop:.3f} s", color=COLORS[mode], fontsize=7.8)
            first_contact = info["raw_bilateral_first_s"]
            if first_contact is not None:
                event_ax.text(first_contact, y-.15, f"{first_contact:.3f}", fontsize=7.5, va="top", color=COLORS[mode])
            else:
                event_ax.text(.03*(full[1]-full[0]), y-.13, "no bilateral contact", fontsize=7.5, va="top", color="#555555")
        label = "(a) Catching | E5, sphere 000052" if row == 0 else "(b) Replanning | E5, replan 000035"
        top = grid[row, 0].get_position(fig).y1
        fig.text(.015, top+.045, label, fontsize=9.2, weight="bold")
        timing = f"First reversal: issued {issued_s:.3f} s → applied {applied_s:.3f} s"
        fig.text(.505, top+.045, timing, fontsize=8.1, ha="left")
    fig.text(.078, .022, "Command: −1 open, 0 hold, +1 close. Shading: first altered 50 ms interval. No curve smoothing.", fontsize=7.8)
    for extension in ("svg", "pdf"):
        fig.savefig(HERE / f"{PREFIX}.{extension}",
                    metadata={"CreationDate": None} if extension == "pdf" else None)
    svg = HERE / f"{PREFIX}.svg"
    svg.write_text("\n".join(line.rstrip() for line in
                   svg.read_text(encoding="utf-8").splitlines()) + "\n",
                   encoding="utf-8", newline="\n")
    REVIEW.mkdir(parents=True, exist_ok=True)
    fig.savefig(REVIEW / f"{PREFIX}.png", dpi=180)
    plt.close(fig)


if __name__ == "__main__":
    args = figure_parser(__doc__, extract=True).parse_args()
    if args.extract:
        extract(research_root(args.research_root))
    plot()
