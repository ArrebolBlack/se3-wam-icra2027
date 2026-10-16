# 本稿证据路由

本文件用于定位，不复制维护实验结论。Research 路径以 C:/workspace/se3-wam-research 为根；模型和 benchmark 实现以其正式仓库为准。本次材料读取于 2026-10-16，随后完成写作与排版核验。

## 故事与研究边界

- [用户指定 Notion：SE(3)-WAM 新故事](https://app.notion.com/p/SE-3-WAM-3ad7e1a213238072a28dd4281671442b?source=copy_link)：问题驱动的完整 Q1–Q3 主线。
- [当前实验路线](https://www.notion.so/3ed7e1a2132381b2a87ef2b071cdff78)：设计筛选、真实数据基座、独立仿真/真机后训练与外部验证。
- Research 的 docs/PROJECT_BRIEFING.md 与 docs/experiments/40_experiment_mainline_cn.md：项目和实验归属入口。

## 结果与正文对应

| 对象 | Research 主要来源 | 论文用途 |
|---|---|---|
| FUTURE0 | docs/experiments/FUTURE0/FUTURE0.md；results/independent1260/analysis/ 下的 report.md、arm-summary.csv、fixed140-arm-summary.csv、paired-summary.csv、task-summary.csv、failure-summary.csv、analysis.json | Q2、图 3、补充表、统计与成本 |
| BASE2 | docs/experiments/BASE2/BASE2.md；results/candidate-comparison.md 与 .json | 组合与匹配控制缺口 |
| HISTORY1 | docs/experiments/HISTORY1/HISTORY1.md 及直接结果 | 视觉历史、探针与剩余比较 |
| BASE1 | docs/experiments/BASE1/BASE1.md 及端点评测报告 | 七方法、八端点及预算 |
| BACKBONE0 | docs/experiments/BACKBONE0/BACKBONE0.md | D/E 定义、容量和多 seed 方案 |
| Q3-INFO0 | docs/experiments/Q3-INFO0/Q3-INFO0.md | R0–R6、生成接口与成本方案 |
| HARD0 | docs/experiments/HARD0/HARD0.md 及诊断结果 | 执行动作位置监督与短训 |
| GRIPPER | docs/experiments/GRIPPER0/GRIPPER0.md、GRIPPER1/GRIPPER1.md、GRIPPER2/GRIPPER2.md 及历史轨迹一致性审计 | 最近标签三态、死区及历史保持诊断 |

FUTURE0 与 BASE2 的五张补充表由 scripts/build_evidence_tables.py 导出；实测图由 figures/plot_future_supervision.py 生成。正文摘要表逐项对照源文件。补集与开发集、配对场景与训练种子、训练辅助预测与在线使用分别报告。

## 写作核验

- 正文、方法与数值表经过独立证据复核；方法公式对应当前标签和实际损失。
- 中文初稿先整理论证与重复限定，再润色语言，最后核对数字、比较范围与完成状态。
- [文后核对说明](verification_zh.tex)：待核实项目、旧稿缺依据的表述及本轮事实修正；仅供作者审读。
- [CVPR 模板说明](../CVPR_TEMPLATE.md)：年度状态、编译与版面。
