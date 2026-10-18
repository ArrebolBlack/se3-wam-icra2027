"""Plot the frozen GT-history E intervention from retained measurements.

python figures/plot_gt_history_intervention.py --research C:/workspace/se3-wam-research --extract
python figures/plot_gt_history_intervention.py

Extraction only averages the three retained windows per episode and checks the
paired counts. Native 20,000-resample intervals are copied without resampling.
No model, rollout, training, or bootstrap is run by this script.
"""
import argparse
from collections import Counter, defaultdict
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


HERE = Path(__file__).resolve().parent
PREFIX = "gt_history_intervention"
WIDTH_MM, HEIGHT_MM = 178, 85
TRUE, STATIONARY, INK = "#0072B2", "#D55E00", "#30343B"
TASK_NAMES = {
    "grasp": "Grasp", "t1_belt": "T1 Belt", "t1_occ": "T1 Occlusion",
    "t1_so3": "T1 SO(3)", "t1_xyz": "T1 XYZ", "t2_se3": "T2 SE(3)",
    "t2_trans": "T2 Translation", "t3_full": "T3 Full", "t3_phase": "T3 Phase",
    "t4_can": "T4 Can", "t4_slider": "T4 Slider", "t4_sphere": "T4 Sphere",
    "t4_sphere_tabletop": "T4 Sphere (table)", "t5_replan": "T5 Replan",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def extract(research):
    relative = Path("docs/experiments/HISTORY1/results/gt-history-intervention")
    root = research / relative
    summary = json.loads((root / "summary.json").read_text(encoding="utf-8"))
    actions = json.loads((root / "actions.json").read_text(encoding="utf-8"))
    tasks, episodes = read_csv(root / "tasks.csv"), read_csv(root / "episodes.csv")
    assert summary["accepted"] and actions["accepted"]
    assert summary["training_updates_added"] == actions["training_updates_added"] == 0
    assert len(actions["rows"]) == summary["action_windows"] == 210
    groups = defaultdict(list)
    for row in actions["rows"]:
        assert row["identity"]["changed_calls"] == 0
        assert row["identity"]["current_pose_preserved"]
        assert row["intervention"]["current_pose_preserved"]
        groups[(row["task"], row["episode"])].append(row)
    assert len(groups) == summary["action_episodes"] == 70
    assert set(map(len, groups.values())) == {3}
    assert set(Counter(task for task, _ in groups).values()) == {5}
    action_rows = []
    for (task, episode), windows in sorted(groups.items()):
        action_rows.append(dict(task=task, episode=episode, windows=len(windows),
            first_translation_mm=float(np.mean([r["first_translation_mm"] for r in windows])),
            identity_translation_mm=0.0,
            source_cases=";".join(sorted(r["case"] for r in windows))))
    action_metric = next(r for r in summary["action_metrics"] if r["metric"] == "first_translation_mm")
    np.testing.assert_allclose(np.mean([r["first_translation_mm"] for r in action_rows]), action_metric["mean"], rtol=0, atol=1e-12)
    task_rows = [{"task": row["task"], "label": TASK_NAMES[row["task"]],
                  **{key: int(row[key]) for key in ("n", "true_history", "stationary_history", "true_only", "stationary_only")}}
                 for row in tasks]
    assert len(task_rows) == 14 and {r["n"] for r in task_rows} == {100}
    assert len(episodes) == 1400
    for row in task_rows:
        paired = [e for e in episodes if e["task_id"] == row["task"]]
        assert len(paired) == row["n"]
        for key in ("true_history", "stationary_history"):
            assert sum(int(e[key]) for e in paired) == row[key]
        assert sum(int(e["difference"]) == 1 for e in paired) == row["true_only"]
        assert sum(int(e["difference"]) == -1 for e in paired) == row["stationary_only"]
    assert sum(r["true_history"] for r in task_rows) == summary["original_successes"] == 824
    assert sum(r["stationary_history"] for r in task_rows) == summary["stationary_successes"] == 9
    assert sum(r["true_only"] for r in task_rows) == summary["true_only"] == 815
    assert sum(r["stationary_only"] for r in task_rows) == summary["stationary_only"] == 0
    caption = (
        "A frozen GT-history E endpoint uses object motion history in control. "
        "Stationary history replaces past object poses with the current pose and recomputes the native motion descriptors at inference. "
        "(a) L2 change in the first issued translation after physical action limits, relative to true history. "
        "Each point averages three windows from one episode; all 70 episode means are shown in ascending order "
        "(five episodes per fixed task). The dashed line and shaded band denote the mean and its 95% interval. "
        "Identity copying changes no action element in any of the 210 windows. "
        "(b) Success rates under true and stationary history at the same frozen endpoint over 1,400 paired scenarios "
        "(100 per task); the right column gives true-to-stationary success counts per 100. "
        "True history yields 824 successes versus 9 with stationary history, a paired difference of 58.21 pp "
        "[56.50, 59.86]; 815 scenarios lose success and none gain it. "
        "Both 95% percentile intervals are copied from the native analysis (20,000 within-task resamples, seed 1729), "
        "resampling episodes in (a) and paired scenarios in (b). "
        "Offline observations and initial action noise are fixed. In each online call, current pose, vision, EEF history, "
        "timestamps and validity masks are unchanged by the intervention; later observations follow each trajectory. "
        "The result measures inference-time input mismatch at one checkpoint (training seed 0); it neither estimates "
        "training variability nor the benefit of adding history during training, and does not compare matched, "
        "physically realizable alternative motion histories.")
    data = dict(experiment="HISTORY1", endpoint="GT-history E, E4, training seed 0",
        action_metric=action_metric,
        closed_loop={key: summary[key] for key in ("original_successes", "stationary_successes", "n", "true_sr", "stationary_sr", "difference_pp", "paired_95_interval_pp", "true_only", "stationary_only")},
        inputs={name: (relative / name).as_posix() for name in ("summary.json", "actions.json", "tasks.csv", "episodes.csv")},
        native_analysis="docs/experiments/HISTORY1/assets/analyze_gt_intervention.py",
        research_summary="docs/experiments/HISTORY1/HISTORY1.md#冻结gt-e的se3历史干预跟进2026-10-18",
        action_aggregation="Three windows averaged per episode; 70 episodes, five per each of 14 fixed tasks. No window is treated as an independent episode.",
        interval=dict(resamples=20000, seed=1729, method="task-stratified percentile bootstrap; paired scenarios for closed loop; episode means for action", recomputed=False,
            note="Native intervals retained exactly. Distinct from the paper's older 100,000-resample training-comparison intervals."),
        checks=dict(action_mean_recomputed=True, task_counts_recomputed_from_paired_csv=True,
            identity_action_elements_equal="Confirmed by the native NPZ analysis; this script reads retained controls only.",
            first_action_changed_windows=summary["first_action_changed_windows"],
            identity_closed_loop="140 scenarios reproduce the original 84 successes; not an additional 1,400-scenario evaluation."),
        design=dict(width_mm=WIDTH_MM, height_mm=HEIGHT_MM, font="Arial", min_font_pt=8,
            encoding="Blue filled circle: true history; orange open square: stationary history. Action points are episode means; band is a confidence interval for their mean, not their spread.",
            task_order="Source task order, including both zero-success tasks; no performance-based selection.",
            action_order="Ascending first-translation change; sorted independently of task.",
            source_style_comparison=[
                dict(paper="CoT-VLA, CVPR 2025", pdf_page=8, printed_page=1709, figure=6, observation="Rendered original viewed: direct numbers, compact panel hierarchy and light reference grids. Borrow the hierarchy, not incremental component-causality language."),
                dict(paper="PointWorld, CVPR 2026", pdf_page=8, printed_page=20772, figure=6, observation="Rendered original viewed: aligned axes and redundant marker/color identities. Use shared two-condition identities with full zero-based success axes."),
                dict(paper="SimLingo, CVPR 2025", pdf_pages=[6,8], printed_pages=[11998,12000], figures=[4], tables=[4,5,6], observation="Rendered originals viewed: same-scene instruction comparisons and compact category-level success reporting; retain all categories and label this as one frozen-endpoint intervention, not a training-mixture comparison.")]),
        caption_suggestion=caption)
    write_csv(HERE / f"{PREFIX}_episodes.csv", action_rows)
    write_csv(HERE / f"{PREFIX}_tasks.csv", task_rows)
    (HERE / f"{PREFIX}_source.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def render(data):
    action_rows = read_csv(HERE / f"{PREFIX}_episodes.csv")
    tasks = read_csv(HERE / f"{PREFIX}_tasks.csv")
    values = np.sort([float(r["first_translation_mm"]) for r in action_rows])
    assert len(values) == 70 and len(tasks) == 14
    metric, closed = data["action_metric"], data["closed_loop"]
    np.testing.assert_allclose(values.mean(), metric["mean"], rtol=0, atol=1e-12)
    plt.rcParams.update({"font.family": "Arial", "font.size": 8,
        "axes.labelsize": 8.2, "xtick.labelsize": 8, "ytick.labelsize": 8,
        "axes.linewidth": .7, "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.fonttype": "none", "text.color": INK, "axes.labelcolor": INK,
        "xtick.color": INK, "ytick.color": INK})
    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), facecolor="white")
    def text_mm(x, y, text, **kwargs):
        return fig.text(x / WIDTH_MM, y / HEIGHT_MM, text, **kwargs)
    a = fig.add_axes([14 / WIDTH_MM, 19 / HEIGHT_MM, 59 / WIDTH_MM, 48 / HEIGHT_MM])
    b = fig.add_axes([113 / WIDTH_MM, 19 / HEIGHT_MM, 43 / WIDTH_MM, 48 / HEIGHT_MM])
    for ax in (a, b):
        ax.spines[["top", "right"]].set_visible(False)
        ax.spines[["left", "bottom"]].set_color("#8A8E94")
        ax.tick_params(length=3, pad=3, width=.7)
        ax.set_axisbelow(True)
    a.grid(axis="y", color="#E5E7EA", linewidth=.55)
    a.set(xlim=(0, 71), ylim=(-1.5, 52), xticks=[1, 20, 40, 60, 70], yticks=[0, 10, 20, 30, 40, 50])
    a.axhspan(metric["ci_low"], metric["ci_high"], color=STATIONARY, alpha=.13, linewidth=0)
    a.axhline(metric["mean"], color=STATIONARY, linestyle=(0, (3, 2)), linewidth=.9)
    a.axhline(0, color="#7F858D", linewidth=1)
    a.scatter(np.arange(1, 71), values, s=11, facecolor=STATIONARY, edgecolor="white", linewidth=.25, zorder=3)
    a.text(3, 25.0, "Mean 18.40 mm", fontsize=8.2, color=STATIONARY, weight="bold")
    a.text(3, 21.7, "95% CI [16.90, 19.93]", fontsize=8, color=STATIONARY)
    a.text(29, 1.8, "Identity: 0", fontsize=8, color="#62666D")
    a.set_xlabel("Episodes (sorted)", labelpad=4)
    a.set_ylabel("First translation change (mm)", labelpad=5)
    text_mm(1, 82, "(a) First-action response", fontsize=9.3, weight="bold", va="top")
    text_mm(1, 76.4, "70 episodes; 3 windows per episode", fontsize=8, color="#62666D", va="top")
    text_mm(14, 70.7, "Stationary history vs. true history", fontsize=8, color=STATIONARY, va="center")

    y = np.arange(len(tasks))
    true = np.array([int(row["true_history"]) for row in tasks])
    stationary = np.array([int(row["stationary_history"]) for row in tasks])
    b.set(xlim=(-3, 103), ylim=(13.6, -.6), xticks=[0, 50, 100], yticks=y)
    b.set_yticklabels([row["label"] for row in tasks])
    b.spines["left"].set_visible(False)
    b.tick_params(axis="y", length=0, pad=5)
    b.grid(axis="x", color="#E5E7EA", linewidth=.55)
    for yy in y:
        b.axhline(yy, color="#F0F1F3", linewidth=.5, zorder=0)
    # The small symmetric vertical offsets keep two coincident zero results visible.
    for yy, t, s in zip(y, true, stationary):
        b.plot([s, t], [yy + .2, yy - .2], color="#B8BEC6", linewidth=1.05, zorder=1)
    b.scatter(true, y - .2, s=19, color=TRUE, edgecolor="white", linewidth=.3, zorder=3)
    b.scatter(stationary, y + .2, s=18, marker="s", facecolor="white", edgecolor=STATIONARY, linewidth=1, zorder=4)
    for yy, t, s in zip(y, true, stationary):
        b.text(1.12, yy, f"{t} → {s}", transform=b.get_yaxis_transform(), va="center", fontsize=8)
    b.set_xlabel("Success rate (%)", labelpad=4)
    text_mm(86, 82, "(b) Closed-loop success", fontsize=9.3, weight="bold", va="top")
    text_mm(86, 76.4, "Same endpoint; 100 scenarios per task", fontsize=8, color="#62666D", va="top")
    handles = [Line2D([], [], marker="o", markersize=4.2, linestyle="none", color=TRUE, label="True history"),
        Line2D([], [], marker="s", markersize=4.2, linestyle="none", markerfacecolor="white", markeredgecolor=STATIONARY, color=STATIONARY, label="Stationary")]
    fig.legend(handles=handles, loc="center left", bbox_to_anchor=(85 / WIDTH_MM, 70.7 / HEIGHT_MM),
        frameon=False, borderaxespad=0, handlelength=.9, handletextpad=.4, columnspacing=.8, ncol=2, fontsize=8)
    text_mm(161, 70.7, "Count / 100", fontsize=8, va="center")
    text_mm(86, 8.3, "Overall: 824 → 9 / 1,400", fontsize=8.3, weight="bold", va="center")
    text_mm(86, 3.5, "True − stationary: 58.21 pp [56.50, 59.86]", fontsize=8, va="center")
    text_mm(1, 6.8, "Frozen GT-history E; inference-time intervention.", fontsize=8, color="#62666D", va="center")
    text_mm(1, 2.2, "Shading: 95% CI of the mean; dots: episode means.", fontsize=8, color="#62666D", va="center")
    for ext in ("pdf", "svg", "png"):
        path = HERE / f"{PREFIX}.{ext}"
        fig.savefig(path, dpi=300, facecolor="white", metadata={"Creator": "plot_gt_history_intervention.py"} if ext == "pdf" else None)
        if ext == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    print(json.dumps(dict(outputs=[f"{PREFIX}.{ext}" for ext in ("pdf", "svg", "png")],
        width_mm=WIDTH_MM, height_mm=HEIGHT_MM, action_episodes=len(action_rows), closed_loop_scenarios=closed["n"],
        first_translation_mean_mm=float(values.mean()), true_successes=int(true.sum()), stationary_successes=int(stationary.sum()),
        native_interval_resamples=data["interval"]["resamples"], bootstrap_rerun=False)))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research", type=Path)
    parser.add_argument("--extract", action="store_true")
    args = parser.parse_args()
    if args.extract:
        assert args.research is not None, "--research is required with --extract"
        source = extract(args.research)
    else:
        source = json.loads((HERE / f"{PREFIX}_source.json").read_text(encoding="utf-8"))
    render(source)
