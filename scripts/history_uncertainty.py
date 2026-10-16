"""Export descriptive HISTORY1 paired intervals from nine native full1400 files.

Run with NumPy 2.3.5: python -B scripts/history_uncertainty.py
Optional --source selects the HISTORY1/results directory; --output selects CSV.
--gt-e-report selects the separately received native GT-history report.
The contrast is history arm minus Current (cp_e). Comparison order is Window,
Codec-MV, Flow, Flow12D, PACT-Age, Wan, PACT-Uniform, GT motion (zero-based);
seed is 20261017 + order. The first seven seeds and contrasts are unchanged.
Reuse paired_uncertainty.py's task-stratified paired percentile bootstrap:
100,000 replicates, PCG64, 100 paired scenes per fixed task, linear quantiles.
These pointwise intervals describe the evaluated four-epoch seed0 checkpoints
on development scenes. They exclude training-seed variation and selection or
multiplicity adjustment; no p-values or new hypothesis-test family are added.
This checks rollout identities and outcomes, not cross-arm probe NPZ arrays.
"""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np

from paired_uncertainty import ROOT, SEED, export_csv, paired_interval, require

SOURCE = Path("C:/workspace/se3-wam-research/docs/experiments/HISTORY1/results")
REFERENCE = "cp_e"
COMPARISONS = (("cp_window", "Window"), ("cp_codec_mv", "Codec-MV"),
               ("cp_flow", "Flow"), ("cp_flow12d", "Flow12D"),
               ("cp_pact_age", "PACT-Age"), ("cp_wan", "Wan"),
               ("cp_pact_uniform", "PACT-Uniform"), ("gt_e", "GT motion"))
IDENTITY = ("task_id", "scenario_id", "source_seed", "inference_seed")
TASKS = ("grasp", "t1_belt", "t1_occ", "t1_so3", "t1_xyz", "t2_se3",
         "t2_trans", "t3_full", "t3_phase", "t4_can", "t4_slider", "t4_sphere",
         "t4_sphere_tabletop", "t5_replan")
CELL = {(True, True): 0, (True, False): 1, (False, True): 2, (False, False): 3}


def read_arm(source, arm, report=None):
    path = report if report is not None else source / arm / "independent1260/full1400.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data["accepted"] is True and data["experiment"] == "HISTORY1" and
            data["arm"] == arm, f"Unaccepted or mismatched result: {arm}")
    for key, value in (("training_seed", 0), ("epochs", 4), ("optimizer_step", 40104),
                       ("expected", 1400), ("completed", 1400), ("missing", 0),
                       ("infrastructure_errors", 0)):
        require(data[key] == value, f"{arm}: unexpected {key}")
    episodes = data["episodes"]
    rows = {tuple(row[key] for key in IDENTITY): row for row in episodes}
    require(len(rows) == len(episodes) == 1400, f"{arm}: missing or duplicate identities")
    require(len({row["scenario_id"] for row in episodes}) == 1400,
            f"{arm}: duplicate scenarios")
    require({row["inference_seed"] for row in episodes} == set(range(20260918, 20262318)),
            f"{arm}: unexpected inference seeds")
    require(all(type(row["success"]) is bool for row in episodes), f"{arm}: nonbinary success")
    require(Counter(row["task_id"] for row in episodes) == Counter({t: 100 for t in TASKS}),
            f"{arm}: expected 14 original tasks with 100 scenes each")
    successes = sum(row["success"] for row in episodes)
    require(successes == data["successes"] and abs(successes / 1400 - data["success_rate"]) < 1e-12,
            f"{arm}: success marginal mismatch")
    for task in TASKS:
        require(data["tasks"][task] == dict(completed=100, successes=sum(
            row["success"] for row in episodes if row["task_id"] == task)),
            f"{arm}: task marginal mismatch: {task}")
    require(data["fixed140"]["completed"] == 140 and
            data["independent1260"]["completed"] == 1260 and
            data["fixed140"]["successes"] + data["independent1260"]["successes"] == successes,
            f"{arm}: development split marginal mismatch")
    for split, start, count, per_task in (("fixed140", 20260918, 140, 10),
                                        ("independent1260", 20261058, 1260, 90)):
        members = [row for row in episodes if start <= row["inference_seed"] < start + count]
        require(len(members) == count and
                Counter(row["task_id"] for row in members) == Counter({t: per_task for t in TASKS}) and
                all(row["index"] == row["inference_seed"] - start for row in members),
                f"{arm}: native {split} identities or task denominators differ")
        require(sum(row["success"] for row in members) == data[split]["successes"],
                f"{arm}: native {split} success count differs")
    return rows


def history_intervals(source, gt_e_report):
    require(np.__version__ == "2.3.5", "Reproduce this export with NumPy 2.3.5")
    reference = read_arm(source, REFERENCE)
    results = []
    for order, (arm, name) in enumerate(COMPARISONS):
        rows = read_arm(source, arm, gt_e_report if arm == "gt_e" else None)
        require(rows.keys() == reference.keys(), f"{arm}: scenario/source/inference pairing mismatch")
        tasks = {task: [0, 0, 0, 0] for task in TASKS}
        for key, row in rows.items():
            ref = reference[key]
            require(all(row[k] == ref[k] for k in ("index", "shard_index", "shard_count")) and
                    Path(row["suite"]).name == Path(ref["suite"]).name,
                    f"{arm}: native episode metadata mismatch: {key}")
            tasks[row["task_id"]][CELL[row["success"], ref["success"]]] += 1
        result = paired_interval(tasks, seed=SEED + order)
        results.append(dict(experiment="HISTORY1", arm=arm, condition=name,
            reference_arm=REFERENCE, reference_condition="Current image", comparison_order=order,
            arm_successes=sum(row["success"] for row in rows.values()),
            reference_successes=sum(row["success"] for row in reference.values()),
            **result, training_seed=0, epochs=4, selection_adjusted=False,
            selection_note="Fixed E4 endpoints; fixed140 plus independent1260 development scenes, not a new held-out test; arm/development selection not corrected",
            pairing_fields=";".join(IDENTITY),
            source=("paper/results/history_gt_e/full1400.json" if arm == "gt_e" else
                    f"HISTORY1/results/{arm}/independent1260/full1400.json") +
                   f";HISTORY1/results/{REFERENCE}/independent1260/full1400.json"))
    return results


def export_task_table(source, gt_e_report, output):
    arms = [(REFERENCE, "Current")] + list(COMPARISONS)
    rows = {arm: read_arm(source, arm, gt_e_report if arm == "gt_e" else None)
            for arm, _ in arms}
    names = ("Grasp", "Belt", "Occlusion", "SO(3)", "XYZ", "SE(3) placement",
             "Trans. placement", "Full passage", "Phase passage", "Can", "Slider",
             "Sphere", "Tabletop sphere", "Replan")
    lines = ["% Generated by scripts/history_uncertainty.py from native episode results.",
             r"\begin{table*}[t]", r"\centering\small",
             r"\caption{History-study successes, one hundred scenes per task and condition. "
             r"The first eight conditions retain current GT target pose; GT motion retains "
             r"current RGB and adds privileged target-motion history. All use one training seed "
             r"and the fourth-epoch endpoint; the 1,400 scenes are the development pool.}",
             r"\label{tab:history_tasks}", r"\setlength{\tabcolsep}{2pt}",
             r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrrrrrr@{}}", r"\toprule",
             r"Task & Current & Window & Codec & Flow & Flow12D & PACT-Age & Wan & Uniform & GT motion \\",
             r"\midrule"]
    for task, name in zip(TASKS, names):
        values = [sum(row["success"] for row in rows[arm].values() if row["task_id"] == task)
                  for arm, _ in arms]
        lines.append(" & ".join([name] + [str(value) for value in values]) + r" \\")
    lines += [r"\midrule", " & ".join(["Total / 1,400"] +
              [str(sum(row["success"] for row in rows[arm].values())) for arm, _ in arms]) + r" \\",
              r"\bottomrule", r"\end{tabular*}", r"\end{table*}", ""]
    output.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--gt-e-report", type=Path, default=ROOT / "results/history_gt_e/full1400.json")
    parser.add_argument("--output", type=Path, default=ROOT / "figures/history_paired_uncertainty.csv")
    parser.add_argument("--table-output", type=Path, default=ROOT / "tables/history_tasks.tex")
    args = parser.parse_args()
    results = history_intervals(args.source, args.gt_e_report)
    export_csv(results, args.output)
    export_task_table(args.source, args.gt_e_report, args.table_output)
    print(f"Validated nine complete paired arms (14 tasks x 100 scenes); exported {len(results)} intervals to {args.output}")
    for result in results:
        print(f"{result['condition']}: gain/loss {result['arm_only_success']}/{result['reference_only_success']}; "
              f"{result['delta_pp']:.2f} pp "
              f"[{result['ci95_low_pp']:.2f}, {result['ci95_high_pp']:.2f}]")
