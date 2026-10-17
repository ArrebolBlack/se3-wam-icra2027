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
\caption{\tablelang{Completed training-recipe study, four epochs per run. G uses frozen
DINOv3-S and I a trainable CNN; both use the corresponding P07 combination.
Batch 64 jointly changes learning rate and device count (details in text).
Training time excludes saving and validation. Job time runs from job creation
through complete evaluation, including the observed queue and startup.}{已完成的训练配方研究，每次训练四轮。G 使用冻结的 DINOv3-S，I 使用可训练 CNN；二者均采用对应的 P07 组合。Batch 64 同时改变学习率和设备数（详见正文）。训练耗时不含保存和验证。作业耗时从创建作业起计至完整评测结束，包含实际发生的排队和启动时间。}}
\label{tab:batch_recipe}
\begin{tabular}{@{}lrrrrrrr@{}}
\toprule
\tablelang{Profile}{配置} & \tablelang{Seed}{种子} & \tablelang{Batch}{批大小} & \tablelang{GPUs}{GPU 数} & \tablelang{Success /1,400}{成功数 /1,400} & \tablelang{SR (\%)}{成功率 (\%)} & \tablelang{Train (min)}{训练 (min)} & \tablelang{Job (min)}{作业 (min)} \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
"""
    (output / "batch_recipe.tex").write_text(overview, encoding="utf-8")
    task_names = [
        ("grasp", r"\tablelang{Grasp}{抓取}"), ("t1_belt", r"\tablelang{Belt}{传送带}"), ("t1_occ", r"\tablelang{Occlusion}{遮挡}"),
        ("t1_so3", "SO(3)"), ("t1_xyz", "XYZ"), ("t2_se3", r"\tablelang{SE(3) placement}{SE(3) 放置}"),
        ("t2_trans", r"\tablelang{Trans. placement}{平移放置}"), ("t3_full", r"\tablelang{Full passage}{完整穿越}"),
        ("t3_phase", r"\tablelang{Phase passage}{相位穿越}"), ("t4_can", r"\tablelang{Can}{罐体}"),
        ("t4_slider", r"\tablelang{Slider}{滑块}"), ("t4_sphere", r"\tablelang{Sphere}{球体}"),
        ("t4_sphere_tabletop", r"\tablelang{Tabletop sphere}{桌面球体}"), ("t5_replan", r"\tablelang{Replan}{重规划}")]
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
\caption{\tablelang{Training-recipe successes per task (100 scenes per entry).
B16 and B64 include their respective learning-rate/device settings;
s0/s1 denote training seeds. All runs use the same accepted scene identities
and inference seeds. Differences across tasks remain visible despite similar totals.}{训练配方研究的逐任务成功数（每项 100 个场景）。B16 和 B64 分别包含各自的学习率与设备设置；s0/s1 表示训练 seed。所有运行使用相同的已接受场景身份和推理 seed。总分相近时，逐任务差异仍然存在。}}
\label{tab:batch_tasks}
\begin{tabular}{@{}lrrrrrrrr@{}}
\toprule
 & \multicolumn{4}{c}{\tablelang{G: frozen DINOv3-S}{G：冻结 DINOv3-S}} & \multicolumn{4}{c}{\tablelang{I: trainable CNN}{I：可训练 CNN}} \\
\cmidrule(lr){2-5}\cmidrule(l){6-9}
\tablelang{Task}{任务} & B16/s0 & B64/s0 & B16/s1 & B64/s1 & B16/s0 & B64/s0 & B16/s1 & B64/s1 \\
\midrule
""" + "\n".join(task_rows) + r"""
\midrule
\tablelang{Total}{总计} & """ + " & ".join(str(run["successes"]) for run in runs) + r""" \\
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
                   for i, name in enumerate((r"\tablelang{Open}{张开}", r"\tablelang{Hold}{保持}", r"\tablelang{Close}{闭合}"))]
    confusion = r"""% Generated from Research GRIPPER2/results/learned/training-report.json.
\begin{table}[t]
\centering\small
\caption{\tablelang{Frozen-decoder validation confusion matrices: 41,533 valid issued
commands from 350 demonstrations. Rows are ground truth; columns are predicted
open/hold/close. These are offline classification counts, not policy successes.}{冻结解码器在验证集上的混淆矩阵：350 条演示中共 41,533 条有效下发指令。行是真值，列是预测的张开／保持／闭合类别。这些数值为离线分类计数，不是策略成功数。}}
\label{tab:decoder_confusion}
\begin{tabular}{@{}lrrrrrr@{}}
\toprule
 & \multicolumn{3}{c}{\tablelang{Raw only}{仅原始输出}} & \multicolumn{3}{c}{\tablelang{Context}{含上下文}} \\
\cmidrule(lr){2-4}\cmidrule(l){5-7}
\tablelang{GT}{真值} & \tablelang{Open}{张开} & \tablelang{Hold}{保持} & \tablelang{Close}{闭合} & \tablelang{Open}{张开} & \tablelang{Hold}{保持} & \tablelang{Close}{闭合} \\
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
