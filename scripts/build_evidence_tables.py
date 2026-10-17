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
    (r"\tablelang{Reference and component objectives}{参照与单项监督目标}", [
        ("P00", r"\tablelang{No future supervision}{无未来监督}"), ("P01", r"\tablelang{3-D scene flow}{三维场景流}"),
        ("P02", r"\tablelang{Target pose}{目标位姿}"), ("P03", r"\tablelang{Scene flow + target pose}{场景流 + 目标位姿}")]),
    (r"\tablelang{Scene replacements: target-pose objective retained}{替换场景监督：保留目标位姿监督}", [
        ("P04", r"\tablelang{Wan latent + pose}{Wan 潜变量 + 位姿}"), ("P05", r"\tablelang{Dense 2-D displacement + pose}{稠密二维位移 + 位姿}"),
        ("P06", r"\tablelang{Codec motion + pose}{Codec 运动 + 位姿}"), ("P07", r"\tablelang{Sparse scene tracks + pose}{稀疏场景轨迹 + 位姿}")]),
    (r"\tablelang{Target replacements: scene-flow objective retained}{替换目标监督：保留场景流监督}", [
        ("P08", r"\tablelang{Scene flow + object DINO}{场景流 + 物体 DINO}"), ("P09", r"\tablelang{Scene flow + target tracks}{场景流 + 目标轨迹}")]),
    (r"\tablelang{Additional objectives: scene flow + target pose retained}{增加监督目标：保留场景流与目标位姿监督}", [
        ("Aalpha", r"\tablelang{P03 + motion magnitude}{P03 + 运动幅值}"), ("P12", r"\tablelang{P03 + depth}{P03 + 深度}"),
        ("P13", "P03 + DINO"), ("P14", r"\tablelang{P03 + dynamic RGB}{P03 + 动态 RGB}"),
        ("P15", r"\tablelang{P03 + depth / DINO / dynamic RGB}{P03 + 深度 / DINO / 动态 RGB}")]),
]
ARMS = [arm for _, group in GROUPS for arm, _ in group]
TASK_GROUPS = [
    (r"\tablelang{Reference grasp}{参照抓取}", [("grasp", r"\tablelang{Grasp}{抓取}")]),
    (r"\tablelang{T1: target motion}{T1：目标运动}", [("t1_belt", r"\tablelang{Belt}{传送带}"), ("t1_occ", r"\tablelang{Occlusion}{遮挡}"),
        ("t1_so3", "SO(3)"), ("t1_xyz", "XYZ")]),
    (r"\tablelang{T2: receptacle motion}{T2：容器运动}", [("t2_se3", "SE(3)"), ("t2_trans", r"\tablelang{Translation}{平移}")]),
    (r"\tablelang{T3: constrained passage}{T3：受限穿越}", [("t3_full", r"\tablelang{Full}{完整}"), ("t3_phase", r"\tablelang{Phase}{相位}")]),
    (r"\tablelang{T4: object capture}{T4：物体捕获}", [("t4_can", r"\tablelang{Can}{罐体}"), ("t4_slider", r"\tablelang{Slider}{滑块}"),
        ("t4_sphere", r"\tablelang{Sphere}{球体}"), ("t4_sphere_tabletop", r"\tablelang{Tabletop sphere}{桌面球体}")]),
    (r"\tablelang{T5: post-impact replanning}{T5：碰撞后重规划}", [("t5_replan", r"\tablelang{Replan}{重规划}")]),
]
TASKS = [task for _, group in TASK_GROUPS for task, _ in group]
TASK_HEADERS = [r"\tablelang{Grasp}{抓取}", r"\tablelang{Belt}{传送带}", r"\tablelang{Occl.}{遮挡}", "SO(3)", "XYZ", "SE(3)", r"\tablelang{Trans.}{平移}",
                r"\tablelang{Full}{完整}", r"\tablelang{Phase}{相位}", r"\tablelang{Can}{罐体}", r"\tablelang{Slider}{滑块}", r"\tablelang{Sphere}{球体}", r"\tablelang{Tabletop}{桌面球}", r"\tablelang{Replan}{重规划}"]


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
    headers = [r" & & \tablelang{Development}{开发集} & \multicolumn{2}{c}{\tablelang{Disjoint complement}{不相交补集}} \\",
               r"\cmidrule(lr){3-3}\cmidrule(lr){4-5}",
               data_row([r"\tablelang{ID}{编号}", r"\tablelang{Future supervision}{未来监督}", r"\tablelang{Success / 140}{成功数 / 140}", r"\tablelang{Success / 1,260}{成功数 / 1,260}", r"\tablelang{SR (\%)}{成功率 (\%)}"])]
    rows = grouped_rows(5, lambda a, target: [arm_label(a), target,
        fixed[a]["successes"], summary[a]["successes"],
        f'{100*int(summary[a]["successes"])/1260:.2f}'])
    table("future_complete.tex",
        r"\tablelang{All fifteen future-supervision conditions, grouped by the objective changed. Each uses one training seed, four epochs, common privileged object-motion input, and action-only deployment. The 140 development scenes and 1,260-scene complement remain separate. Scene flow includes target regions.}{全部十五种未来监督条件，按改变的目标函数分组。每种条件均使用一个训练 seed、四轮训练、相同的特权物体运动输入，并在部署时仅生成动作。140 个开发场景与 1,260 场补集分别报告。场景流包含目标区域。}",
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
    headers = [r" & \multicolumn{4}{c}{\tablelang{P00: no future supervision}{P00：无未来监督}} & \multicolumn{4}{c}{\tablelang{P03: scene flow + target pose}{P03：场景流 + 目标位姿}} \\",
               r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}",
               data_row([r"\tablelang{ID}{编号}"]+[r"\tablelang{Gain}{得}", r"\tablelang{Loss}{失}", r"95\% CI (pp)", r"\tablelang{Adjusted $p$}{校正 $p$}"]*2)]
    table("future_paired.tex",
        r"\tablelang{Paired outcomes over the same 1,260 scenes. Gain means candidate success/reference failure; loss means candidate failure/reference success. Intervals are pointwise task-stratified paired bootstrap intervals for the SR difference, conditional on the trained checkpoints (Appendix~A). Exact two-sided McNemar tests use the full family of fourteen P00 and thirteen P03 contrasts: $p_{\mathrm{adj}}=\min(1,27p)$. P03 against itself is inapplicable.}{相同 1,260 个场景上的配对结果。“得”指候选成功、参照失败；“失”指候选失败、参照成功。区间为给定已训练检查点时，成功率差值的逐项、按任务分层的配对 bootstrap 区间（附录 A）。双侧精确 McNemar 检验的完整比较族包含相对 P00 的十四项和相对 P03 的十三项对照：$p_{\mathrm{adj}}=\min(1,27p)$。P03 与自身的比较不适用。}",
        "tab:paired_future", "l"+"r"*8, headers,
        grouped_rows(9, paired_row, skip=("P00",)))

    counts = {(r["arm"], r["task_id"]): int(r["successes"]) for r in read_csv(src/"task-summary.csv")}
    def task_row(arm, target):
        values = [counts[(arm, task)] for task in TASKS]
        if sum(values) != int(summary[arm]["successes"]):
            raise ValueError("Per-task and overall FUTURE0 counts disagree")
        return [arm_label(arm)]+values+[sum(values)]
    headers = [r" & \tablelang{Reference}{参照} & \multicolumn{4}{c}{\tablelang{T1: target motion}{T1：目标运动}} & \multicolumn{2}{c}{\tablelang{T2: placement}{T2：放置}} & \multicolumn{2}{c}{\tablelang{T3: passage}{T3：穿越}} & \multicolumn{4}{c}{\tablelang{T4: capture}{T4：捕获}} & T5 & \\",
        r"\cmidrule(lr){2-2}\cmidrule(lr){3-6}\cmidrule(lr){7-8}\cmidrule(lr){9-10}\cmidrule(lr){11-14}\cmidrule(lr){15-15}",
        data_row([r"\tablelang{ID}{编号}"]+TASK_HEADERS+[r"\tablelang{Total}{总计}"])]
    table("future_tasks.tex",
        r"\tablelang{Future-study successes: ninety scenes per task and 1,260 per condition. Columns follow the task families in Table~\ref{tab:tasks}; all tasks are retained, including zero-success tasks. Occl. denotes physical occlusion; Trans. denotes translating-receptacle placement; Tabletop denotes tabletop sphere capture.}{未来监督研究的成功数：每个任务 90 个场景，每种条件 1,260 个场景。列按表~\ref{tab:tasks} 的任务族排列，保留全部任务，包括零成功任务。“遮挡”指物理遮挡；“平移”指向平移容器放置；“桌面球”指桌面球体捕获。}",
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
        r"\tablelang{Native evaluator failure counts out of 1,260 scenes per condition, in the same design groups as the success tables. Safety is the evaluator category, not a certified safety measure. Every failure remains in the success-rate denominator.}{原生评测器的失败计数，每种条件共 1,260 个场景，分组与成功数表一致。“安全”是评测器的类别，不是经认证的安全指标。全部失败均保留在成功率分母中。}",
        "tab:future_failures", "llrrrrr",
        [data_row([r"\tablelang{ID}{编号}", r"\tablelang{Future supervision}{未来监督}", r"\tablelang{Boundary}{越界}", r"\tablelang{Safety}{安全类}", r"\tablelang{Task viol.}{任务违规}", r"\tablelang{Timeout}{超时}", r"\tablelang{Total}{总计}"])],
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
    rows += [r"\midrule", data_row([r"\tablelang{Total / 1,400}{总计 / 1,400}"]+[totals[a] for a in combo_arms]+[totals[a] for a in ("E", "F")])]
    configs = ["DINO", "DINO", "CNN", "CNN"]*3
    reconstruction = ["-", "+", "-", "+"]*3
    headers = [r" & \multicolumn{4}{c}{\tablelang{P15: auxiliary}{P15：辅助监督}} & \multicolumn{4}{c}{\tablelang{P07: scene tracks}{P07：场景轨迹}} & \multicolumn{4}{c}{\tablelang{P09: target tracks}{P09：目标轨迹}} & P03 & P00 \\",
        r"\cmidrule(lr){2-5}\cmidrule(lr){6-9}\cmidrule(lr){10-13}\cmidrule(lr){14-14}\cmidrule(lr){15-15}",
        data_row([r"\tablelang{Task}{任务}"]+[rf"\makecell{{{name}\\${sign}$ ({arm})}}" for name, sign, arm in zip(configs, reconstruction, combo_arms)]+[r"\makecell{CNN\\$+$ (E)}", r"\makecell{CNN\\$+$ (F)}"])]
    table("combination_tasks.tex",
        r"\tablelang{Combination-study successes, grouped by future target and visual encoder. DINO is frozen DINO-S; CNN is trained from scratch. Minus/plus denotes current-target RGB reconstruction off/on; parentheses retain source condition IDs. E and F are the selected configuration's matched scene-flow/pose and no-future controls. Each task has one hundred scenes, including development scenes, and each condition has one training seed. Totals use the predefined 1,400-scene selection pool.}{组合研究的成功数，按未来监督目标和视觉编码器分组。DINO 为冻结的 DINO-S；CNN 从头训练。负号／正号表示关闭／开启当前目标 RGB 重建；括号保留源条件编号。E、F 分别为所选配置匹配的场景流／位姿监督对照和无未来监督对照。每个任务含 100 个场景（包括开发场景），每种条件使用一个训练 seed。总数来自预先定义的 1,400 场选择池。}",
        "tab:combination_tasks", "l"+"r"*14, headers, rows, tabsep=1.5)
    print("Exported five grouped supplementary tables; counts, pairing and denominators checked.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--research-root", type=Path, required=True)
    main(parser.parse_args().research_root)
