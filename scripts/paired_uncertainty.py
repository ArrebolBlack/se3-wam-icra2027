"""Descriptive task-stratified paired bootstrap from accepted experiment data.

For binary paired outcomes, resampling the observed four-cell counts with a
multinomial distribution is exactly equivalent to resampling scene pairs for
the mean success difference. Tasks and their sample sizes remain fixed. These
pointwise percentile intervals condition on the evaluated checkpoints; they
exclude training-seed variability and multiple-comparison/selection adjustment.
They do not replace FUTURE0's existing Bonferroni-corrected McNemar tests.

Method references (official documentation, accessed 2026-10-17):
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html
https://stat.ethz.ch/R-manual/R-devel/library/boot/html/boot.html
https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.multinomial.html
"""
from pathlib import Path
import argparse
import csv
import json

import numpy as np

from common import REPO as ROOT, add_research_argument, require, research_root, write_csv

CELLS = ("both_success", "arm_only_success", "reference_only_success", "both_failure")
RESAMPLES, SEED = 100_000, 20261017


def export_csv(rows, path):
    write_csv(path, rows)


def paired_interval(task_counts, seed=SEED, resamples=RESAMPLES):
    """Return a pooled mean difference and its conditional percentile interval."""
    counts = np.asarray([task_counts[t] for t in sorted(task_counts)])
    require(counts.ndim == 2 and counts.shape[1] == 4, "Expected four cells per task")
    require(np.issubdtype(counts.dtype, np.integer) and np.all(counts >= 0),
            "Counts must be nonnegative integers")
    sizes = counts.sum(axis=1)
    require(np.all(sizes > 0), "Every task must contain paired observations")
    require(resamples >= 100_000, "Use at least 100,000 bootstrap resamples")
    rng = np.random.Generator(np.random.PCG64(seed))
    net = np.zeros(resamples, dtype=np.int64)
    for cell, n in zip(counts, sizes):
        sampled = rng.multinomial(int(n), cell / n, size=resamples)
        net += sampled[:, 1] - sampled[:, 2]
    distribution = 100 * net / sizes.sum()
    lower, upper = np.quantile(distribution, [0.025, 0.975], method="linear")
    totals = counts.sum(axis=0)
    return dict(n=int(sizes.sum()), tasks=len(sizes),
                scenes_per_task=";".join(str(int(n)) for n in sizes),
                **dict(zip(CELLS, map(int, totals))),
                delta_pp=100 * int(totals[1] - totals[2]) / int(sizes.sum()),
                ci95_low_pp=float(lower), ci95_high_pp=float(upper),
                resamples=resamples, bootstrap_seed=seed, rng="PCG64",
                numpy_version=np.__version__, quantile_method="linear",
                interval_method="task-stratified paired percentile bootstrap",
                confidence_level=0.95, multiplicity_adjusted=False,
                uncertainty_scope="scene sampling conditional on evaluated checkpoints; excludes training-seed variability")


def future0_intervals(source):
    analysis = json.loads((source / "analysis.json").read_text(encoding="utf-8"))
    require(analysis["cross_arm_scene_seed_pairing_checked"] is True and
            analysis["training_seeds_per_arm"] == 1 and analysis["fixed140_overlap"] == 0,
            "Expected paired independent scenes and one training seed per arm")
    with (source / "paired-summary.csv").open(encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    with (source / "arm-summary.csv").open(encoding="utf-8", newline="") as f:
        arms = {r["arm"]: r for r in csv.DictReader(f)}
    grouped = {}
    for row in raw:
        key = (row["arm"], row["reference_arm"])
        group = grouped.setdefault(key, {})
        require(row["scope"] in ("overall", "task"), f"Unknown scope: {row['scope']}")
        scope = "overall" if row["scope"] == "overall" else row["task_id"]
        require(scope and scope not in group, f"Duplicate or missing scope for {key}")
        counts = [int(row[c]) for c in CELLS]
        n = int(row["n"])
        require(min(counts) >= 0 and sum(counts) == n, f"Invalid denominator for {key}/{scope}")
        require(n == (1260 if scope == "overall" else 90), f"Unexpected denominator for {key}/{scope}")
        require(abs((counts[1] - counts[2]) / n - float(row["sr_difference"])) < 1e-12,
                f"Difference does not match cells for {key}/{scope}")
        group[scope] = (row, counts)
    require(len(raw) == 405 and len(grouped) == 27, "Expected 27 overall and 378 task comparisons")
    expected_tasks = None
    results = []
    for index, ((arm, reference), group) in enumerate(sorted(grouped.items())):
        require("overall" in group and len(group) == 15, f"Missing tasks for {arm}/{reference}")
        overall, counts = group["overall"]
        tasks = {t: c for t, (_, c) in group.items() if t != "overall"}
        expected_tasks = set(tasks) if expected_tasks is None else expected_tasks
        require(set(tasks) == expected_tasks, "Task sets differ across comparisons")
        require(np.array_equal(np.sum(list(tasks.values()), axis=0), counts),
                f"Task cells do not sum to overall for {arm}/{reference}")
        a, r = arms[arm], arms[reference]
        require(int(a["n"]) == int(r["n"]) == 1260, "Arm denominator mismatch")
        require(counts[0] + counts[1] == int(a["successes"]) and
                counts[0] + counts[2] == int(r["successes"]), f"Marginal mismatch for {arm}/{reference}")
        for summary in (a, r):
            require(abs(float(summary["sr"]) - int(summary["successes"]) / 1260) < 1e-12,
                    "Arm success rate mismatch")
        result = paired_interval(tasks, seed=SEED + index)
        results.append(dict(experiment="FUTURE0", arm=arm, reference_arm=reference,
                            comparison_group=overall["comparison_group"], **result,
                            selection_adjusted=False,
                            source="FUTURE0/results/independent1260/analysis/paired-summary.csv"))
    return results


def base2_intervals(source):
    data = {arm: json.loads((source / f"{arm}-full1400.json").read_text(encoding="utf-8"))
            for arm in ("I", "F", "E")}
    fields = ("index", "task_id", "scenario_id", "source_seed", "inference_seed", "shard_index", "shard_count")
    paired = {}
    for arm, d in data.items():
        require(d["accepted"] and d["completed"] == d["expected"] == 1400 and
                d["missing"] == d["infrastructure_errors"] == 0, f"Incomplete BASE2 {arm}")
        rows = {tuple(e[k] for k in fields): e for e in d["episodes"]}
        require(len(rows) == len(d["episodes"]) == 1400, f"Duplicate BASE2 {arm} episodes")
        require(all(type(e["success"]) is bool for e in rows.values()), "Success must be binary")
        require(sum(e["success"] for e in rows.values()) == d["successes"], "BASE2 marginal mismatch")
        paired[arm] = rows
    results = []
    # Preserve the original I-F stream exactly. The new I-E contrast and the
    # post-hoc task-exclusion diagnostic use separate, explicitly recorded seeds.
    for reference, group, seed in (("F", "matched_P00", SEED), ("E", "matched_P03", SEED + 1)):
        require(paired["I"].keys() == paired[reference].keys(), "BASE2 scene pairing mismatch")
        tasks = {}
        for key, a in paired["I"].items():
            r = paired[reference][key]
            require(Path(a["suite"]).name == Path(r["suite"]).name, "BASE2 suite mismatch")
            cells = tasks.setdefault(a["task_id"], [0, 0, 0, 0])
            cells[{(True, True): 0, (True, False): 1, (False, True): 2, (False, False): 3}
                  [(a["success"], r["success"])]] += 1
        require(len(tasks) == 14 and all(sum(c) == 100 for c in tasks.values()), "BASE2 task denominator mismatch")
        scopes = [(tasks, seed, group, "all 14 tasks", "")]
        if reference == "E":
            require(tasks["t3_phase"][1] - tasks["t3_phase"][2] == 72,
                    "BASE2 phase contribution changed")
            complement = {t: c for t, c in tasks.items() if t != "t3_phase"}
            scopes.append((complement, SEED + 2, "matched_P03_excluding_phase_posthoc",
                           "post-hoc remaining 13 tasks", "t3_phase"))
        for task_counts, stream, comparison, scope, excluded in scopes:
            result = paired_interval(task_counts, seed=stream)
            results.append(dict(experiment="BASE2", arm="I", reference_arm=reference,
                                comparison_group=comparison, **result, selection_adjusted=False,
                                selection_note="I selected from 12 candidates on development scenes; interval does not correct selection bias",
                                source=f"BASE2/results/I-full1400.json;BASE2/results/{reference}-full1400.json",
                                analysis_scope=scope, excluded_tasks=excluded))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_research_argument(parser)
    parser.add_argument("--source", type=Path,
                        help="FUTURE0 analysis directory (default: under the Research checkout)")
    parser.add_argument("--output", type=Path, default=ROOT / "figures/Fig5/archive/future_supervision/future_supervision_uncertainty.csv")
    parser.add_argument("--base2", action="store_true")
    args = parser.parse_args()
    experiments = research_root(args.research_root) / "docs/experiments"
    results = future0_intervals(args.source or experiments / "FUTURE0/results/independent1260/analysis")
    export_csv(results, args.output)
    print(f"Validated 27 overall + 378 task comparisons; exported {len(results)} intervals to {args.output}")
    if args.base2:
        results = base2_intervals(experiments / "BASE2/results")
        export_csv(results, ROOT / "figures/Fig5/archive/future_supervision/base2_paired_uncertainty.csv")
        print(json.dumps(results, ensure_ascii=False))
