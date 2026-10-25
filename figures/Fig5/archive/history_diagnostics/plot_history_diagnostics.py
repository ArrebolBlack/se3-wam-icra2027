"""Plot HISTORY1 diagnostics using retained aggregate measurements only.

python figures/Fig5/archive/history_diagnostics/plot_history_diagnostics.py --extract [--research-root <Research>]
python figures/Fig5/archive/history_diagnostics/plot_history_diagnostics.py

The extract operation reads two Research CSVs and the paper's existing 100,000-
resample paired intervals. It never runs probes, models, or physical rollouts.
Plotting alone uses the adjacent source JSON, preserving every selected source row.
"""
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from common import REVIEW, figure_parser, read_csv, research_root

PREFIX = "history_diagnostics"
ARMS = ("cp_e", "cp_window", "cp_flow", "cp_flow12d", "cp_wan", "cp_pact_age",
        "cp_pact_uniform", "cp_codec_mv", "gt_e")
NAMES = ("Current", "Window", "Flow", "Flow12D", "Wan", "PACT-Age",
         "PACT-Uniform", "Codec-MV", "GT-history Current")
SITES = ("fused_condition", "action_readout_tau0")
MODES = ("repeat_current", "reverse")
BLUE, PURPLE, INK = "#3E6787", "#7B61A8", "#30343B"
WIDTH_MM, HEIGHT_MM = 178, 94


def only(rows, **criteria):
    found = [r for r in rows if all(r[k] == v for k, v in criteria.items())]
    assert len(found) == 1, (criteria, len(found))
    return found[0]


def extract(research):
    table_root = research / "docs/experiments/HISTORY1/results/paper-evidence/tables"
    readout_path = table_root / "probe-readouts-macro.csv"
    action_path = table_root / "probe-action-changes-macro.csv"
    paired_path = HERE / "history_paired_uncertainty.csv"
    readouts, actions, pairs = map(read_csv, (readout_path, action_path, paired_path))
    selected = []
    for arm, name in zip(ARMS, NAMES):
        a = [only(readouts, arm=arm, site=site, label="past_position_lag7_m") for site in SITES]
        b = [only(actions, arm=arm, mode=mode,
                  metric="action_issued__first_step__translation_m") for mode in MODES]
        assert all(r["physical_unit"] == "m" and int(r["tasks"]) == 14 for r in a + b)
        assert all((r["oracle_determined"] == "True") == (arm == "gt_e") for r in a)
        c = None if arm == "cp_e" else only(pairs, experiment="HISTORY1", arm=arm)
        if c:
            assert int(c["resamples"]) == 100000 and int(c["training_seed"]) == 0
            assert int(c["n"]) == 1400 and int(c["tasks"]) == 14
            assert c["reference_arm"] == "cp_e"
        selected.append(dict(arm=arm, name=name, readout_source_rows=a,
                             action_source_rows=b, paired_source_row=c,
                             meta_v_error_mm=float(a[0]["retained_error"]) * 1000,
                             action_input_error_mm=float(a[1]["retained_error"]) * 1000,
                             repeat_current_change_mm=float(b[0]["mean"]) * 1000,
                             reverse_change_mm=float(b[1]["mean"]) * 1000,
                             delta_pp=0.0 if c is None else float(c["delta_pp"]),
                             ci95_low_pp=None if c is None else float(c["ci95_low_pp"]),
                             ci95_high_pp=None if c is None else float(c["ci95_high_pp"])))
    data = dict(
        experiment="HISTORY1", training_seed=0, rows=selected,
        sources=dict(readouts=str(readout_path), actions=str(action_path),
                     paired_intervals="figures/Fig5/archive/history_diagnostics/history_paired_uncertainty.csv",
                     research_analysis="docs/experiments/HISTORY1/assets/analysis/paper.py",
                     research_extraction="docs/experiments/HISTORY1/assets/probes/native.py"),
        selections=dict(
            a=dict(label="past_position_lag7_m", lag_steps=7, sampling_hz=20,
                   lag_ms=350, sites=list(SITES), metric="retained_error",
                   interpretation="Frozen linear probe from each representation alone; per-window three-dimensional Euclidean error, then within-episode, within-task, and across-task means. Not RMSE, a policy-head error, or a conditional information gain."),
            b=dict(metric="action_issued__first_step__translation_m", modes=list(MODES),
                   interpretation="L2 change in first issued translation after physical action limits, relative to baseline under fixed input and initial noise. Offline replay only."),
            c=dict(reference="cp_e", resamples=100000,
                   interval="pointwise 95% task-stratified paired scenario percentile bootstrap",
                   interpretation="Existing paper intervals copied without resampling; training-seed variability and arm/development selection are not quantified.")),
        unit_conversions=dict(a="metres * 1000 -> millimetres", b="metres * 1000 -> millimetres",
                              c="percentage points; no conversion"),
        aggregation=dict(a_b="Unweighted mean of the 14 fixed task-level point estimates; no macro confidence interval.",
                         c="1,400 paired scenarios, 100 in each of 14 fixed tasks; seed0 E4 endpoints."),
        input_boundary="Eight current-pose arms retain GT current pose and EEF history. GT-history Current additionally receives GT motion history; it is not a visual-history encoding.",
        zero_controls="Current and GT-history Current have no visual-history input. Their visual-history interventions therefore produce zero change; GT motion history is not intervened on.",
        design=dict(width_mm=WIDTH_MM, height_mm=HEIGHT_MM, font="Arial", min_font_pt=8,
                    marker_encoding="A: filled circle Meta V, open diamond Action input. B: filled square Repeat current, open triangle Reverse past. C: point and scenario CI.",
                    source_style_comparison=[
                        dict(paper="CoT-VLA, CVPR 2025", pdf_page=8, printed_page=1709, figure=6,
                             local_pdf="local_private/cvpr_writing_materials_2026_10_13/papers/cot_vla.pdf",
                             observation="Inspected rendered PDF page. Compact labeled ablation panels, light grids, and clearly separated legends; borrow hierarchy and restrained axes, not the component-accumulation causal narrative."),
                        dict(paper="PointWorld, CVPR 2026", pdf_page=8, printed_page=20772, figure=6,
                             local_pdf="local_private/cvpr_writing_materials_2026_10_13/papers/pointworld.pdf",
                             observation="Inspected rendered PDF page. Side-by-side quantitative panels use consistent category identities and redundant marker/color legends; borrow aligned comparisons while replacing five bar colors with shared rows and two markers.")]),
        caption_suggestion=("Readable history and action sensitivity do not imply a closed-loop gain in HISTORY1. "
            "(a) Frozen linear-probe error for object position 350 ms in the past at final Meta V and the action input at the first NFE (tau=0). "
            "(b) L2 change in the first issued translation after repeat-current or reverse-past interventions, with initial noise fixed and physical action limits applied. "
            "Both offline panels show descriptive means across 14 fixed tasks, without confidence intervals. "
            "(c) Success-rate difference from Current over 1,400 paired scenarios (100 per task), with pointwise 95% task-stratified percentile intervals from 100,000 resamples. "
            "All results use a single training seed; intervals capture scenario sampling conditional on these checkpoints, not training variability or model-selection uncertainty. "
            "The separated GT-history Current row has additional GT motion information. Current and GT-history Current have no visual-history input, so both interventions are zero controls; GT motion inputs remain intact."))
    (HERE / f"{PREFIX}_source.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def render(data):
    assert tuple(r["arm"] for r in data["rows"]) == ARMS
    rows = data["rows"]
    plt.rcParams.update({"font.family": "Arial", "font.size": 8,
                         "axes.labelsize": 8.2, "xtick.labelsize": 8,
                         "ytick.labelsize": 8.2, "axes.linewidth": .7,
                         "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
                         "text.color": INK, "axes.labelcolor": INK,
                         "xtick.color": INK, "ytick.color": INK})
    fig = plt.figure(figsize=(WIDTH_MM / 25.4, HEIGHT_MM / 25.4), facecolor="white")
    x_positions = (33, 84, 134)
    widths = (42, 42, 40)
    axes = [fig.add_axes([x / WIDTH_MM, 23 / HEIGHT_MM, w / WIDTH_MM, 43 / HEIGHT_MM])
            for x, w in zip(x_positions, widths)]
    y = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8.8])
    for ax in axes:
        ax.set_ylim(9.8, -.56)
        ax.set_yticks(y)
        ax.tick_params(axis="y", length=0, pad=6)
        ax.tick_params(axis="x", length=3, pad=3, width=.7)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.spines["bottom"].set_color("#7F858D")
        ax.set_axisbelow(True)
        ax.grid(axis="x", color="#E7E9EC", linewidth=.55)
        for yy in y[:-1]:
            ax.axhline(yy, color="#F1F2F4", linewidth=.55, zorder=0)
        ax.axhspan(7.87, 9.77, color="#F4F4F4", zorder=0)
        ax.axhline(7.68, color="#A6AAB0", linewidth=.65)
    axes[0].set_yticklabels([*NAMES[:-1], "GT-history Current\n+ GT motion input"])
    axes[1].set_yticklabels([])
    axes[2].set_yticklabels([])
    axes[0].get_yticklabels()[-1].set_fontsize(8)
    # One shared condition column keeps all nine rows aligned across measures.
    fig.text(3 / WIDTH_MM, 69.5 / HEIGHT_MM, "History condition", fontsize=8.2, weight="bold")

    a, b, c = axes
    a.set_xlim(7.5, 12.0)
    a.set_xticks([8, 10, 12])
    a.scatter([r["meta_v_error_mm"] for r in rows], y - .14, s=20,
              color=BLUE, marker="o", edgecolors="white", linewidths=.35, zorder=3)
    a.scatter([r["action_input_error_mm"] for r in rows], y + .14, s=21,
              facecolors="white", edgecolors=PURPLE, marker="D", linewidths=.95, zorder=3)
    a.set_xlabel("Position error (mm)\nlower is better", labelpad=5)

    b.set_xlim(-1, 27)
    b.set_xticks([0, 10, 20])
    b.scatter([r["repeat_current_change_mm"] for r in rows], y - .14, s=21,
              color=PURPLE, marker="s", edgecolors="white", linewidths=.35, zorder=3)
    b.scatter([r["reverse_change_mm"] for r in rows], y + .14, s=27,
              facecolors="white", edgecolors=PURPLE, marker="^", linewidths=.95, zorder=3)
    b.set_xlabel("Issued translation change\nL2 (mm)", labelpad=5)

    c.set_xlim(-12, 9)
    c.set_xticks([-10, -5, 0, 5])
    c.axvline(0, color="#686D75", linestyle=(0, (2.5, 2)), linewidth=.8, zorder=1)
    c.scatter([0], [y[0]], s=23, marker="o", facecolors="white", edgecolors=INK, linewidths=.9, zorder=4)
    c.text(1, y[0], "reference", fontsize=8, va="center", color="#62666D")
    for yy, row in zip(y[1:], rows[1:]):
        delta, low, high = [row[k] for k in ("delta_pp", "ci95_low_pp", "ci95_high_pp")]
        c.errorbar(delta, yy, xerr=[[delta-low], [high-delta]], fmt="o", color=INK,
                   markersize=4, markeredgewidth=.7, elinewidth=1.05, capsize=2, zorder=3)
    c.set_xlabel("SR difference (pp)\nvs. Current", labelpad=5)

    titles = ("(a) Past-state readout", "(b) Action sensitivity", "(c) Closed-loop success")
    subtitles = ("Position 350 ms in the past", "Visual-history intervention", "1,400 paired scenarios")
    for x, title, subtitle in zip(x_positions, titles, subtitles):
        fig.text(x / WIDTH_MM, 89 / HEIGHT_MM, title, fontsize=9.1, weight="bold", va="top")
        fig.text(x / WIDTH_MM, 83 / HEIGHT_MM, subtitle, fontsize=8, color="#62666D", va="top")

    legend_specs = [
        [Line2D([], [], marker="o", markersize=4.5, linestyle="none", color=BLUE, label="Meta V"),
         Line2D([], [], marker="D", markersize=4.5, linestyle="none", markerfacecolor="white",
                markeredgecolor=PURPLE, color=PURPLE, label="Action input (τ=0)")],
        [Line2D([], [], marker="s", markersize=4.5, linestyle="none", color=PURPLE, label="Repeat current"),
         Line2D([], [], marker="^", markersize=5, linestyle="none", markerfacecolor="white",
                markeredgecolor=PURPLE, color=PURPLE, label="Reverse past")]]
    for x, handles in zip(x_positions, legend_specs):
        fig.legend(handles=handles, loc="upper left", bbox_to_anchor=((x-1.2) / WIDTH_MM, 78 / HEIGHT_MM),
                   frameon=False, borderaxespad=0, handlelength=1, handletextpad=.4,
                   labelspacing=.45, fontsize=8)
    fig.text(134 / WIDTH_MM, 75.5 / HEIGHT_MM, "Point estimate", fontsize=8, va="center")
    fig.text(134 / WIDTH_MM, 70.5 / HEIGHT_MM, "+ 95% paired-scenario CI", fontsize=8, va="center")
    fig.text(3 / WIDTH_MM, 4 / HEIGHT_MM,
             "Seed 0. Offline: 14-task means, no CIs. Closed loop: scenario uncertainty only.",
             fontsize=8, color="#62666D", va="center")
    for ext in ("pdf", "svg", "png"):
        path = (REVIEW if ext == "png" else HERE) / f"{PREFIX}.{ext}"
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=300, facecolor="white",
                    metadata={"Creator": "plot_history_diagnostics.py", "CreationDate": None}
                    if ext == "pdf" else None)
        if ext == "svg":
            path.write_text("\n".join(line.rstrip() for line in path.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
    plt.close(fig)
    print(json.dumps(dict(outputs=[f"{PREFIX}.{x}" for x in ("pdf", "svg")], preview=str(REVIEW / f"{PREFIX}.png"),
                          width_mm=WIDTH_MM, height_mm=HEIGHT_MM, conditions=len(rows),
                          min_font_pt=8, paired_resamples=100000)))


if __name__ == "__main__":
    args = figure_parser(__doc__, extract=True).parse_args()
    if args.extract:
        source = extract(research_root(args.research_root))
    else:
        source = json.loads((HERE / f"{PREFIX}_source.json").read_text(encoding="utf-8"))
    render(source)
