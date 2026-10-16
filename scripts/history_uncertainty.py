"""Export descriptive HISTORY1 paired intervals from eight native full1400 files.

Run with NumPy 2.3.5: python -B scripts/history_uncertainty.py
Optional --source selects the HISTORY1/results directory; --output selects CSV.
The contrast is history arm minus Current (cp_e). Comparison order is Window,
Codec-MV, Flow, Flow12D, PACT-Age, Wan, PACT-Uniform (zero-based); seed is
20261017 + order. The first five seeds remain unchanged; the added two use
20261022 and 20261023, respectively.
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
               ("cp_pact_uniform", "PACT-Uniform"))
IDENTITY = ("task_id", "scenario_id", "source_seed", "inference_seed")
TASKS = ("grasp", "t1_belt", "t1_occ", "t1_so3", "t1_xyz", "t2_se3",
         "t2_trans", "t3_full", "t3_phase", "t4_can", "t4_slider", "t4_sphere",
         "t4_sphere_tabletop", "t5_replan")
CELL = {(True, True): 0, (True, False): 1, (False, True): 2, (False, False): 3}


def read_arm(source, arm):
    data = json.loads((source / arm / "independent1260/full1400.json").read_text(encoding="utf-8"))
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


def history_intervals(source):
    require(np.__version__ == "2.3.5", "Reproduce this export with NumPy 2.3.5")
    reference = read_arm(source, REFERENCE)
    results = []
    for order, (arm, name) in enumerate(COMPARISONS):
        rows = read_arm(source, arm)
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
            source=f"HISTORY1/results/{arm}/independent1260/full1400.json;HISTORY1/results/{REFERENCE}/independent1260/full1400.json"))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=ROOT / "figures/history_paired_uncertainty.csv")
    args = parser.parse_args()
    results = history_intervals(args.source)
    export_csv(results, args.output)
    print(f"Validated eight complete paired arms (14 tasks x 100 scenes); exported {len(results)} intervals to {args.output}")
    for result in results:
        print(f"{result['condition']}: gain/loss {result['arm_only_success']}/{result['reference_only_success']}; "
              f"{result['delta_pp']:.2f} pp "
              f"[{result['ci95_low_pp']:.2f}, {result['ci95_high_pp']:.2f}]")
