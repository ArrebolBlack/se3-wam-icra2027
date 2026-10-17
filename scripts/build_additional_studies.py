"""Export the completed recipe and frozen-decoder studies; never run a model."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--research-root", type=Path, required=True)
    args = parser.parse_args()
    experiments = args.research_root / "docs/experiments"
    output = Path(__file__).resolve().parents[1] / "tables"
    batch = read(experiments / "BATCH0/results/full_measurements_20261016.json")
    assert batch["complete_comparison"] and len(batch["runs"]) == 8
    runs = sorted(batch["runs"], key=lambda r: (
        r["training"]["profile"], r["training"]["seed"], r["training"]["global_batch"]))
    assert {(r["training"]["profile"], r["training"]["seed"], r["training"]["global_batch"])
            for r in runs} == {(p, s, b) for p in ("G", "I") for s in (0, 1) for b in (16, 64)}
    rows = []
    for run in runs:
        train, timing = run["training"], run["timing"]
        assert train["completed_epochs"] == 4 and train["global_samples_seen"] == 641664
        assert run["n"] == 1400 and len(run["episodes"]) == 1400
        assert sum(ep["success"] for ep in run["episodes"]) == run["successes"]
        assert abs(run["success_rate"] - run["successes"] / 1400) < 1e-12
        rows.append(f'{train["profile"]} & {train["seed"]} & {train["global_batch"]} & '
                    f'{train["world_size"]} & {run["successes"]:,} & {100 * run["success_rate"]:.2f} & '
                    f'{timing["training_compute_seconds"] / 60:.2f} & '
                    f'{timing["created_to_result_seconds"] / 60:.2f} \\\\')
    overview = r"""% Generated from Research BATCH0/results/full_measurements_20261016.json.
\begin{table*}[t]
\centering\small
\caption{Completed training-recipe study, four epochs per run. G uses frozen
DINOv3-S and I a trainable CNN; both use the corresponding P07 combination.
Batch 64 jointly changes learning rate and device count (details in text).
Training time excludes saving and validation. Job time runs from job creation
through complete evaluation, including the observed queue and startup.}
\label{tab:batch_recipe}
\begin{tabular}{@{}lrrrrrrr@{}}
\toprule
Profile & Seed & Batch & GPUs & Success /1,400 & SR (\%) & Train (min) & Job (min) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    (output / "batch_recipe.tex").write_text(overview, encoding="utf-8")
    task_names = [
        ("grasp", "Grasp"), ("t1_belt", "Belt"), ("t1_occ", "Occlusion"),
        ("t1_so3", "SO(3) grasp"), ("t1_xyz", "XYZ grasp"), ("t2_se3", "SE(3) place"),
        ("t2_trans", "Translation place"), ("t3_full", "Full passage"),
        ("t3_phase", "Phase passage"), ("t4_can", "Supported can"),
        ("t4_slider", "Slider"), ("t4_sphere", "Capture"),
        ("t4_sphere_tabletop", "Supported sphere"), ("t5_replan", "Replan")]
    task_rows = []
    for task, label in task_names:
        counts = []
        for run in runs:
            episodes = [ep for ep in run["episodes"] if ep["task_id"] == task]
            assert len(episodes) == 100, (run["run"], task, len(episodes))
            counts.append(str(sum(ep["success"] for ep in episodes)))
        task_rows.append(label + " & " + " & ".join(counts) + r" \\")
    tasks = r"""% Generated from the 11,200 original BATCH0 episode results.
\begin{table*}[t]
\centering\small
\caption{Training-recipe successes per task (100 scenes per entry).
B16 and B64 include their respective learning-rate/device settings;
s0/s1 denote training seeds. All runs use the same accepted scene identities
and inference seeds. Differences across tasks remain visible despite similar totals.}
\label{tab:batch_tasks}
\begin{tabular}{@{}lrrrrrrrr@{}}
\toprule
 & \multicolumn{4}{c}{G: frozen DINOv3-S} & \multicolumn{4}{c}{I: trainable CNN} \\
\cmidrule(lr){2-5}\cmidrule(l){6-9}
Task & B16/s0 & B64/s0 & B16/s1 & B64/s1 & B16/s0 & B64/s0 & B16/s1 & B64/s1 \\
\midrule
""" + "\n".join(task_rows) + r"""
\midrule
Total & """ + " & ".join(str(run["successes"]) for run in runs) + r""" \\
\bottomrule
\end{tabular}
\end{table*}
"""
    (output / "batch_tasks.tex").write_text(tasks, encoding="utf-8")
    decoder = read(experiments / "GRIPPER2/results/learned/training-report.json")
    audit = read(experiments / "GRIPPER2/results/learned/regression-audit.json")
    assert decoder["training_complete"] and audit["audit_accepted"]
    assert audit["n"] == len(audit["cases"]) == 11
    assert sum(case["native"]["success"] for case in audit["cases"]) == audit["successes"] == 9
    assert not audit["regression_passed"] and not audit["fresh_rollout_permitted"]
    matrices = [decoder[k]["validation"]["confusion"] for k in ("raw_only", "context")]
    assert all(sum(map(sum, matrix)) == 41533 for matrix in matrices)
    assert [sum(row) for row in matrices[0]] == [sum(row) for row in matrices[1]]
    matrix_rows = [name + " & " + " & ".join(str(x) for m in matrices for x in m[i]) + r" \\"
                   for i, name in enumerate(("Open", "Hold", "Close"))]
    confusion = r"""% Generated from Research GRIPPER2/results/learned/training-report.json.
\begin{table}[t]
\centering\small
\caption{Frozen-decoder validation confusion matrices: 41,533 valid issued
commands from 350 demonstrations. Rows are ground truth; columns are predicted
open/hold/close. These are offline classification counts, not policy successes.}
\label{tab:decoder_confusion}
\begin{tabular}{@{}lrrrrrr@{}}
\toprule
 & \multicolumn{3}{c}{Raw only} & \multicolumn{3}{c}{Context} \\
\cmidrule(lr){2-4}\cmidrule(l){5-7}
GT & Open & Hold & Close & Open & Hold & Close \\
\midrule
""" + "\n".join(matrix_rows) + r"""
\bottomrule
\end{tabular}
\end{table}
"""
    (output / "decoder_confusion.tex").write_text(confusion, encoding="utf-8")
    print("Exported 8 recipe runs, 11200 episode results, and 2 decoder confusion matrices; regression 9/11.")


if __name__ == "__main__":
    main()
