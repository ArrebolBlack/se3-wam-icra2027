# 本稿证据路由

本文件用于定位，不复制维护实验结论。Research 路径以 C:/workspace/se3-wam-research 为根；模型和 benchmark 实现以其正式仓库为准。本次材料在 2026-10-17 复查，新增结果按各实验原生报告更新。

## 故事与研究边界

- [用户指定 Notion：SE(3)-WAM 新故事](https://app.notion.com/p/SE-3-WAM-3ad7e1a213238072a28dd4281671442b?source=copy_link)：问题驱动的完整 Q1–Q3 主线。
- [用户指定 Notion：Dynamic Manipulation 文献调研](https://app.notion.com/p/Dynamic-Manipulation-3d37e1a2132380378946c03f3a8780f4?source=copy_link)：动态操作、历史表示、未来预测及世界—动作接口的文献入口；参考文献条目与具体主张再对照论文原文。
- [当前实验路线](https://www.notion.so/3ed7e1a2132381b2a87ef2b071cdff78)：设计筛选、真实数据基座、独立仿真/真机后训练与外部验证。
- Research 的 docs/PROJECT_BRIEFING.md 与 docs/experiments/40_experiment_mainline_cn.md：项目和实验归属入口。

## 结果与正文对应

| 对象 | Research 主要来源 | 论文用途 |
|---|---|---|
| FUTURE0 | docs/experiments/FUTURE0/FUTURE0.md；results/independent1260/analysis/ 下的 report.md、arm-summary.csv、fixed140-arm-summary.csv、paired-summary.csv、task-summary.csv、failure-summary.csv、analysis.json | Q2、图 3、补充表、统计与成本 |
| BASE2 | docs/experiments/BASE2/BASE2.md；results/candidate-comparison.md、final-comparison.json；I/E/F-full1400.json | 十二组合及两项匹配控制、任务收益集中性 |
| HISTORY1 | docs/experiments/HISTORY1/HISTORY1.md 及各臂 results；新接收 GT-history 原件见下 | 九臂结果、八臂离线历史扰动与剩余交叉比较 |
| BASE1 | docs/experiments/BASE1/BASE1.md 及端点评测报告 | 七方法、八端点及预算 |
| BACKBONE0 | docs/experiments/BACKBONE0/BACKBONE0.md | D/E 定义、容量和多 seed 方案 |
| Q3-INFO0 | docs/experiments/Q3-INFO0/Q3-INFO0.md | R0–R6、生成接口与成本方案 |
| HARD0 | docs/experiments/HARD0/HARD0.md 及诊断结果 | 执行动作位置监督与短训 |
| GRIPPER | docs/experiments/GRIPPER0/GRIPPER0.md、GRIPPER1/GRIPPER1.md、GRIPPER2/GRIPPER2.md 及历史轨迹一致性审计 | 最近标签三态、死区及历史保持诊断 |

FUTURE0 与 BASE2 的五张补充表由 scripts/build_evidence_tables.py 导出；实测图由 figures/plot_future_supervision.py 生成。正文摘要表逐项对照源文件。补集与开发集、配对场景与训练种子、训练辅助预测与在线使用分别报告。

- 原实现：Research 的 local_private/future0-independent1260-20261015/release-a3/payload.zip 内 model-source/src/se3_wam/ 与 assets/configs/；核对原实验的几何注入、object tokens、目标构造、损失、归一化和动作执行。当前模型代码不替代历史部署包。
- 成本原件：local_private/future0-20261012/unified-cost-host-readback-20261014/reports.tar 与 docs/experiments/FUTURE0/results/comparison/cost/measurement-accepted.json；核对设备实录、精度、样本与计时边界。
- 配对区间：[计算脚本](../../scripts/paired_uncertainty.py)读取原任务内四格计数；[未来监督区间](../../figures/future_supervision_uncertainty.csv)与[组合匹配控制区间](../../figures/base2_paired_uncertainty.csv)保存重采样设置和条件范围。
- 真实离线预测：[来源说明](../../figures/prediction_examples_source.json)与[选例表](../../figures/prediction_examples_selection.csv)追溯 P15 accepted DEV84；[脚本](../../figures/plot_prediction_examples.py)生成示例图，[CV/CA计算](../../figures/kinematic_baselines.py)仅使用模型可见的历史 GT pose。总体均值/中位数与逐时距分布共同解释离线误差，不替代闭环接触证据。
- HISTORY1 编码接口：Research 的 local_private/history1-20261016/source-export 与原 history1-migrate-zone10-20261016-a1.zip；核对 Flow12D、采样时间、codec/Wan、query 压缩与已分配槽位。
- HISTORY1 GT-history 新接收：[最小原件](../../results/history_gt_e/INDEX.md)来自已结束任务的原生 reports.tar，保留确切对象地址、四轮预算、恢复与配置；逐场核对后纳入论文，Research 仍拥有该实验。
- HISTORY1 离线干预：[汇总脚本](../../scripts/history_interventions.py)核对八臂 probes/extract 与 probes/readouts 的原生报告及本地归档；[导出 CSV](../../figures/history_interventions.csv)描述动作敏感性，正式 probe NPZ 的跨臂数组核查仍缺。
- BASE2 接受部署：Research 的 local_private/base2-combination-20261016/ 内 base2-controls-zone10-20261016-a1.zip（F）、base2-resumefix-zone10-20261016-a6.zip（I）与 payload-requeue-zone10-a4.zip；核对 CNN、完整 Window、目标 crop 重建及训练归一化，区别于后续 canonical 改动。
- 历史评测协议：Research 的 local_private/zenith-pro6000-history-20261011/asset-adapt/history-assets-a1.tar.gz 内 benchmark-source/configs/tasks/ 与 src/se3_wam_benchmark/envs/families/；失败映射在 evaluation/result.py:92–144，双指垫接触在 envs/base.py:257–290。future0-20261012/runtime-upload-a1/complete-runtime-assets.json 记录原件及完整读回；release-a3/payload.zip、上述 BASE2 F/I 包与 HISTORY1 migrate 包的 runtime-assets、benchmark_source 和十四套场景清单绑定相同历史资源。171 个 benchmark 文件与该仓库既有 41005787853052dd2b386abfe7313845ad9fa0f6 版本一致。该绑定证明接受包的配置来源，不代表新增逐个远端进程检查。

- 初态与运动采样：上述历史归档的 configs/scenarios/<task>.yaml 为 E7/agentview 配方，scenarios/_recipes.py 负责采样与坐标编译；不是 configs/tasks 的成功条件。release-a3/payload.zip 的 evaluation_reference/scenes/validation.jsonl 和 suites/sr_<task>.yaml 保存实际接受场景与筛选。T5 的原生 action_delay_steps 经 suite/rollout/make_env 到 control/action.py 的队列执行；与没有注入实测计算耗时分别解释。

## 写作核验

- 正文、方法与数值表经过独立证据复核；方法公式对应当前标签和实际损失。
- 中文初稿先整理论证与重复限定，再润色语言，最后核对数字、比较范围与完成状态。
- [文后核对说明](verification_zh.tex)：待核实项目、旧稿缺依据的表述及本轮事实修正；仅供作者审读。
- [CVPR 模板说明](../CVPR_TEMPLATE.md)：年度状态、编译与版面。
