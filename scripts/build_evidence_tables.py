"""Export five supplementary tables from Research's existing result summaries.

This runs no experiment. Grouping and labels expose the study design; all counts
remain source values. Bonferroni p=min(1,27p) is the existing reported family.
Usage: python scripts/build_evidence_tables.py --research-root C:/workspace/se3-wam-research
"""
from pathlib import Path
import argparse
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
GROUPS = [
    ("Reference and component objectives", [
        ("P00", "No future supervision"), ("P01", "3-D scene flow"),
        ("P02", "Target pose"), ("P03", "Scene flow + target pose")]),
    ("Scene replacements: target-pose objective retained", [
        ("P04", "Wan latent + pose"), ("P05", "Dense 2-D displacement + pose"),
        ("P06", "Codec motion + pose"), ("P07", "Sparse scene tracks + pose")]),
    ("Target replacements: scene-flow objective retained", [
        ("P08", "Scene flow + object DINO"), ("P09", "Scene flow + target tracks")]),
    ("Additional objectives: scene flow + target pose retained", [
        ("Aalpha", "P03 + motion magnitude"), ("P12", "P03 + depth"),
        ("P13", "P03 + DINO"), ("P14", "P03 + dynamic RGB"),
        ("P15", "P03 + depth / DINO / dynamic RGB")]),
]
ARMS = [arm for _, group in GROUPS for arm, _ in group]
TASK_GROUPS = [
    ("Reference grasp", [("grasp", "Grasp")]),
    ("T1: target motion", [("t1_belt", "Belt"), ("t1_occ", "Occlusion"),
        ("t1_so3", "SO(3)"), ("t1_xyz", "XYZ")]),
    ("T2: receptacle motion", [("t2_se3", "SE(3)"), ("t2_trans", "Translation")]),
    ("T3: constrained passage", [("t3_full", "Full"), ("t3_phase", "Phase")]),
    ("T4: object capture", [("t4_can", "Can"), ("t4_slider", "Slider"),
        ("t4_sphere", "Sphere"), ("t4_sphere_tabletop", "Tabletop sphere")]),
    ("T5: post-impact replanning", [("t5_replan", "Replan")]),
]
TASKS = [task for _, group in TASK_GROUPS for task, _ in group]
TASK_HEADERS = ["Grasp", "Belt", "Occl.", "SO(3)", "XYZ", "SE(3)", "Trans.",
                "Full", "Phase", "Can", "Slider", "Sphere", "Tabletop", "Replan"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def arm_label(arm):
    return r"$A_{\alpha}$" if arm == "Aalpha" else arm


def data_row(values):
    return " & ".join(str(v) for v in values) + r" \\"


def group_row(title, columns):
    return [r"\addlinespace[2pt]", r"\multicolumn{"+str(columns)+r"}{@{}l}{\emph{"+title+r"}} \\[-1pt]"]


def grouped_rows(columns, row_fn, skip=()):
    body = []
    for title, members in GROUPS:
        body += group_row(title, columns)
        for arm, target in members:
            if arm not in skip:
                body.append(data_row(row_fn(arm, target)))
    return body


def table(name, caption, label, spec, headers, body, tabsep=3.0):
    lines = ["% Generated from Research source summaries; do not edit numerical cells.",
             r"\begin{table*}[!htp]", r"\centering\small", r"\begingroup",
             rf"\setlength{{\tabcolsep}}{{{tabsep:g}pt}}", r"\renewcommand{\arraystretch}{1.10}",
             r"\caption{"+caption+"}", r"\label{"+label+"}",
             r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}"+spec+r"@{}}",
             r"\toprule"] + headers + [r"\midrule"] + body + [
             r"\bottomrule", r"\end{tabular*}", r"\endgroup", r"\end{table*}", ""]
    (ROOT/"tables"/name).write_text("\n".join(lines), encoding="utf-8")


def main(research):
    src = research/"docs/experiments/FUTURE0/results/independent1260/analysis"
    summary = {r["arm"]: r for r in read_csv(src/"arm-summary.csv")}
    fixed = {r["arm"]: r for r in read_csv(src/"fixed140-arm-summary.csv")}
    if set(summary) != set(ARMS) or any(int(r["n"]) != 1260 for r in summary.values()):
        raise ValueError("Unexpected FUTURE0 arms or denominator")
    headers = [r" & & Development & \multicolumn{2}{c}{Disjoint complement} \\",
               r"\cmidrule(lr){3-3}\cmidrule(lr){4-5}",
               data_row(["ID", "Future supervision", "Success / 140", "Success / 1,260", r"SR (\%)"])]
    rows = grouped_rows(5, lambda a, target: [arm_label(a), target,
        fixed[a]["successes"], summary[a]["successes"],
        f'{100*int(summary[a]["successes"])/1260:.2f}'])
    table("future_complete.tex",
        "All fifteen future-supervision conditions, grouped by the objective changed. "
        "Each uses one training seed, four epochs, common privileged object-motion input, "
        "and action-only deployment. The 140 development scenes and 1,260-scene complement "
        "remain separate. Scene flow includes target regions.",
        "tab:all_future", "llrrr", headers, rows)

    pairs = {(r["arm"], r["reference_arm"]): r for r in read_csv(src/"paired-summary.csv")
             if r["scope"] == "overall"}
    if len(pairs) != 27:
        raise ValueError("The reported Bonferroni family must contain 27 comparisons")
    intervals = {(r["arm"], r["reference_arm"]): r for r in
                 read_csv(ROOT/"figures/future_supervision_uncertainty.csv")}
    if set(intervals) != set(pairs):
        raise ValueError("Interval and paired-test comparisons disagree")
    def paired_row(arm, target):
        row = [arm_label(arm)]
        for reference in ("P00", "P03"):
            if arm == reference:
                row += ["---"]*4
                continue
            r = pairs[(arm, reference)]
            gain, loss = int(r["arm_only_success"]), int(r["reference_only_success"])
            if gain-loss != int(summary[arm]["successes"])-int(summary[reference]["successes"]):
                raise ValueError("Paired net disagrees with source success counts")
            p = float(r["mcnemar_exact_two_sided_p"])
            interval = intervals[(arm, reference)]
            ci = f'[{float(interval["ci95_low_pp"]):.2f}, {float(interval["ci95_high_pp"]):.2f}]'
            row += [gain, loss, "$"+ci+"$", f"{min(1, 27*p):.3g}"]
        return row
    headers = [r" & \multicolumn{4}{c}{P00: no future supervision} & \multicolumn{4}{c}{P03: scene flow + target pose} \\",
               r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}",
               data_row(["ID"]+["Gain", "Loss", r"95\% CI (pp)", "Adjusted $p$"]*2)]
    table("future_paired.tex",
        "Paired outcomes over the same 1,260 scenes. Gain means candidate success/reference failure; "
        "loss means candidate failure/reference success. Intervals are pointwise task-stratified "
        "paired bootstrap intervals for the SR difference, conditional on the trained checkpoints "
        "(Appendix~A). Exact two-sided McNemar tests use the full family of fourteen P00 and thirteen P03 contrasts: "
        r"$p_{\mathrm{adj}}=\min(1,27p)$. P03 against itself is inapplicable.",
        "tab:paired_future", "l"+"r"*8, headers,
        grouped_rows(9, paired_row, skip=("P00",)))

    counts = {(r["arm"], r["task_id"]): int(r["successes"]) for r in read_csv(src/"task-summary.csv")}
    def task_row(arm, target):
        values = [counts[(arm, task)] for task in TASKS]
        if sum(values) != int(summary[arm]["successes"]):
            raise ValueError("Per-task and overall FUTURE0 counts disagree")
        return [arm_label(arm)]+values+[sum(values)]
    headers = [r" & Reference & \multicolumn{4}{c}{T1: target motion} & \multicolumn{2}{c}{T2: placement} & \multicolumn{2}{c}{T3: passage} & \multicolumn{4}{c}{T4: capture} & T5 & \\",
        r"\cmidrule(lr){2-2}\cmidrule(lr){3-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}\cmidrule(lr){11-14}\cmidrule(lr){15-15}",
        data_row(["ID"]+TASK_HEADERS+["Total"])]
    table("future_tasks.tex",
        "Future-study successes: ninety scenes per task and 1,260 per condition. "
        "Columns follow the task families in Table~\\ref{tab:tasks}; all tasks are retained, "
        "including zero-success tasks. Occl. denotes physical occlusion; Trans. denotes "
        "translating-receptacle placement; Tabletop denotes tabletop sphere capture.",
        "tab:future_tasks", "l"+"r"*15, headers, grouped_rows(16, task_row), tabsep=2.1)

    failure = {(r["arm"], r["category"]): int(r["count"]) for r in read_csv(src/"failure-summary.csv")
               if r["scope"] == "overall" and r["field"] == "failure_class"}
    cats = ["boundary", "safety", "task_violation", "timeout"]
    def failure_row(arm, target):
        values = [failure[(arm, category)] for category in cats]
        if sum(values) != int(summary[arm]["failures"]):
            raise ValueError("Failure categories do not cover source failures")
        return [arm_label(arm), target]+values+[sum(values)]
    table("future_failures.tex",
        "Native evaluator failure counts out of 1,260 scenes per condition, in the same "
        "design groups as the success tables. Safety is the evaluator category, not a "
        "certified safety measure. Every failure remains in the success-rate denominator.",
        "tab:future_failures", "llrrrrr",
        [data_row(["ID", "Future supervision", "Boundary", "Safety", "Task viol.", "Timeout", "Total"])],
        grouped_rows(7, failure_row), tabsep=2.5)

    d = json.loads((research/"docs/experiments/BASE2/results/final-comparison.json").read_text(encoding="utf-8"))
    if not d["accepted"] or d["n_per_arm"] != 1400:
        raise ValueError("Unexpected BASE2 result scope")
    # Within each future target: DINO-/DINO+/CNN-/CNN+ (RGB reconstruction off/on).
    combo_arms = ["B", "A", "D", "C", "H", "G", "J", "I", "L", "K", "N", "M"]
    totals = {r["arm"]: r["successes"] for r in d["ranking"]}
    for arm in combo_arms:
        if sum(d["per_task"][t][arm]["successes"] for t in TASKS) != totals[arm]:
            raise ValueError("Per-task and overall BASE2 counts disagree")
    controls = {}
    for arm in ("E", "F"):
        control = json.loads((research/f"docs/experiments/BASE2/results/{arm}-full1400.json").read_text(encoding="utf-8"))
        if not control["accepted"] or control["completed"] != 1400 or control["missing"] or control["infrastructure_errors"]:
            raise ValueError(f"Matched control {arm} is incomplete")
        control_counts = {t: control["tasks"][t]["successes"] for t in TASKS}
        if sum(control_counts.values()) != control["successes"] or control["successes"] != totals[arm]:
            raise ValueError("Matched control task counts do not sum to its total")
        controls[arm] = control_counts
    rows = []
    for title, members in TASK_GROUPS:
        rows += group_row(title, 15)
        for task, short in members:
            rows.append(data_row([short]+[d["per_task"][task][a]["successes"] for a in combo_arms]+[controls[a][task] for a in ("E", "F")]))
    rows += [r"\midrule", data_row(["Total / 1,400"]+[totals[a] for a in combo_arms]+[totals[a] for a in ("E", "F")])]
    configs = ["DINO", "DINO", "CNN", "CNN"]*3
    reconstruction = ["-", "+", "-", "+"]*3
    headers = [r" & \multicolumn{4}{c}{P15: auxiliary} & \multicolumn{4}{c}{P07: scene tracks} & \multicolumn{4}{c}{P09: target tracks} & P03 & P00 \\",
        r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}\cmidrule(lr){14-14}\cmidrule(lr){15-15}",
        data_row(["Task"]+[rf"\makecell{{{name}\\${sign}$ ({arm})}}" for name, sign, arm in zip(configs, reconstruction, combo_arms)]+[r"\makecell{CNN\\$+$ (E)}", r"\makecell{CNN\\$+$ (F)}"])]
    table("combination_tasks.tex",
        "Combination-study successes, grouped by future target and visual encoder. "
        "DINO is frozen DINO-S; CNN is trained from scratch. Minus/plus denotes "
        "current-target RGB reconstruction off/on; parentheses retain source condition IDs. "
        "E and F are the selected configuration's matched scene-flow/pose and no-future controls. "
        "Each task has one hundred scenes, including development scenes, and each condition "
        "has one training seed. Totals use the predefined 1,400-scene selection pool.",
        "tab:combination_tasks", "l"+"r"*14, headers, rows, tabsep=1.5)
    print("Exported five grouped supplementary tables; counts, pairing and denominators checked.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-root", type=Path, required=True)
    main(parser.parse_args().research_root)
