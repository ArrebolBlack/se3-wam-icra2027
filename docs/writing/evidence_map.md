# 本稿证据路由

> 本文件记录 v1 稿件（Q1–Q3 研究顺序）的证据位置。v2 稿件的结构与表格映射见 [v2 作者指南](v2_author_guide.md)；把下列已有结果迁入 v2 表格前，须先确认其实验配置与 v2 选定配置一致。

本文件用于定位，不复制维护实验结论。Research 路径以 C:/workspace/se3-wam-research 为根（导出脚本可用 `--research-root` 或环境变量 `SE3WAM_RESEARCH` 改写）；模型和 benchmark 实现以其正式仓库为准。全文材料在 2026-10-17 复查，Q1 完整结果于 2026-10-18 更新，BASE2 三 seed 结果于 2026-10-19 写入；新增结果按各实验原生报告更新。

## 故事与研究边界

- [用户指定 Notion：SE(3)-WAM 新故事](https://app.notion.com/p/SE-3-WAM-3ad7e1a213238072a28dd4281671442b?source=copy_link)：问题驱动的完整 Q1–Q3 主线。
- [用户指定 Notion：Dynamic Manipulation 文献调研](https://app.notion.com/p/Dynamic-Manipulation-3d37e1a2132380378946c03f3a8780f4?source=copy_link)：动态操作、历史表示、未来预测及世界—动作接口的文献入口；参考文献条目与具体主张再对照论文原文。
- [当前实验路线](https://www.notion.so/3ed7e1a2132381b2a87ef2b071cdff78)：设计筛选、真实数据基座、独立仿真/真机后训练与外部验证。
- Research 的 docs/PROJECT_BRIEFING.md 与 docs/experiments/40_experiment_mainline_cn.md：项目和实验归属入口。

## 结果与正文对应

| 对象 | Research 主要来源 | 论文用途 |
|---|---|---|
| FUTURE0 | docs/experiments/FUTURE0/FUTURE0.md；results/independent1260/analysis/ 下的 report.md、arm-summary.csv、fixed140-arm-summary.csv、paired-summary.csv、task-summary.csv、failure-summary.csv、analysis.json | Q2、图 3、补充表、统计与成本 |
| BASE2 | docs/experiments/BASE2/BASE2.md；results/candidate-comparison.md、final-comparison.json；I/E/F-full1400.json；results/multiseed/full-comparison.json（十四配置三 seed） | 十二组合及两项匹配控制的三 seed 结果、配对对比与 seed 0 任务收益集中性；Research 另有 O–T 扩展配置（O 为当前候选），尚未写入论文 |
| BATCH0 | docs/experiments/BATCH0/BATCH0.md；results/full_measurements_20261016.json、paired_comparison_20261016.json；原始full-readback归档及checkpoint读回 | 附录H双seed训练配方、完整逐任务与耗时；seed0重跑不增加独立seed计数 |
| HISTORY1 | docs/experiments/HISTORY1/HISTORY1.md 及各臂 results；GT-history 与冻结干预原件见下 | 九臂训练比较、探针、离线扰动、跨轮背景与冻结历史闭环干预 |
| BASE1 | docs/experiments/BASE1/BASE1.md 及端点评测报告 | 七方法、八端点及预算 |
| BACKBONE0 | docs/experiments/BACKBONE0/BACKBONE0.md；模型仓库 docs/architecture.md 的 D/E backbone preparation | D/E 参数归属、内部归一化、配对初始化、容量和多 seed 方案 |
| Q3-INFO0 | docs/experiments/Q3-INFO0/Q3-INFO0.md | R0–R6、生成接口与成本方案 |
| 初始化对照 | docs/experiments/LIBERO-DREAM0/LIBERO-DREAM0.md、LIBERO-PI0/LIBERO-PI0.md、LIBERO-SE30/LIBERO-SE30.md | 附录 F 的三项预训练控制方案；终点结果尚不计入证据 |
| HARD0 | docs/experiments/HARD0/HARD0.md 及诊断结果 | 执行动作位置与示范标签覆盖 |
| GRIPPER | docs/experiments/GRIPPER0/GRIPPER0.md、GRIPPER1/GRIPPER1.md、GRIPPER2/GRIPPER2.md；GRIPPER2/results/learned/ 中的training-report、regression-audit、failure-diagnosis、feature-diagnosis及原归档；assets/analyze_learned_features.py | 最近标签三态、死区与历史保持；附录H冻结读出、9/11回归、两例物理失败及局部特征敏感性 |

FUTURE0 的四张补充表与 BASE2 的三张表（三 seed 组合、配对对比、seed 0 逐任务）由 scripts/build_evidence_tables.py 导出；实测图由 figures/plot_future_supervision.py 生成。正文摘要表逐项对照源文件。补集与开发集、配对场景与训练种子、训练辅助预测与在线使用分别报告。

附录H三表由 [build_additional_studies.py](../../scripts/build_additional_studies.py) 从BATCH0逐场结果及GRIPPER2原验证混淆矩阵导出。BATCH0的8次训练、11,200场由原readback/checkpoint文件重建并与汇总一致；20,000次bootstrap独立复算一致。其B16 seed0与BASE2配置及逐场成败相同，属于同seed重跑，seed1为新增重复；未比较两份seed0权重逐张量相等。冻结读出的离线改善与失败回归分别报告，不当作新场景成功率。

- 原实现：Research 的 local_private/future0-independent1260-20261015/release-a3/payload.zip 内 model-source/src/se3_wam/ 与 assets/configs/；核对原实验的几何注入、object tokens、目标构造、损失、归一化和动作执行。当前模型代码不替代历史部署包。
- 成本原件：local_private/future0-20261012/unified-cost-host-readback-20261014/reports.tar 与 docs/experiments/FUTURE0/results/comparison/cost/measurement-accepted.json；核对设备实录、精度、样本与计时边界。
- 配对区间：[计算脚本](../../scripts/paired_uncertainty.py)读取原任务内四格计数；[未来监督区间](../../figures/future_supervision_uncertainty.csv)与[组合匹配控制区间](../../figures/base2_paired_uncertainty.csv)保存重采样设置和条件范围。
- 真实离线预测：[来源说明](../../figures/prediction_examples_source.json)与[选例表](../../figures/prediction_examples_selection.csv)追溯 P15 accepted DEV84；[脚本](../../figures/plot_prediction_examples.py)生成示例图，[CV/CA计算](../../figures/kinematic_baselines.py)仅使用模型可见的历史 GT pose。总体均值/中位数与逐时距分布共同解释离线误差，不替代闭环接触证据。
- HISTORY1 编码接口：Research 的 local_private/history1-20261016/source-export 与原 history1-migrate-zone10-20261016-a1.zip；核对 Flow12D、采样时间、codec/Wan、query 压缩与已分配槽位。
- HISTORY1 GT-history 新接收：[最小原件](../../results/history_gt_e/INDEX.md)来自已结束任务的原生 reports.tar，保留确切对象地址、四轮预算、恢复与配置；逐场核对后纳入论文，Research 仍拥有该实验。
- HISTORY1 冻结 GT-history 干预：docs/experiments/HISTORY1/results/gt-history-intervention/ 保存 summary、逐场配对、动作及恒等复现记录；原件为 local_private/history1-gt-intervention-20261018/reports.tar。本轮独立核对原包的 210 个动作 NPZ、1,540 条闭环记录与原部署源码；真历史 1,400 场沿用此前结果，新增闭环为静止历史 1,400 场和恒等 140 场。新图的[来源与统计设置](../../figures/gt_history_intervention_source.json)、[70 个 episode 均值](../../figures/gt_history_intervention_episodes.csv)、[逐任务计数](../../figures/gt_history_intervention_tasks.csv)由[绘图脚本](../../figures/plot_gt_history_intervention.py)读取；沿用原生 20,000 次、seed 1729 区间，不替换原论文训练比较的 100,000 次区间。
- HISTORY1 跨轮背景：旧 GT-motion Current 的 835 场由 docs/experiments/DB0-TRAIN0/results/history_encoding_fresh_20261010/pro6000/continuation/ 下的 rollout/evidence/accepted-epoch4-fixed140-20261012/e-a4/result.json 和 independent1260/evidence/accepted-independent1260-a1-lp16/e/result.json 的 88+747 核对；其余七臂见 docs/experiments/HISTORY1/results/paper-evidence/tables/successes-by-task.csv。[跨轮表](../../tables/history_cross_round.tex)提供背景，设备与恢复履历不同，不作为匹配的二因素训练实验。
- HISTORY1 探针与离线干预：Research 的 docs/experiments/HISTORY1/results/paired-arrays.json 及 paired-arrays-execution.json 记录九臂9,450个NPZ的385,350项CPU数组配对；paper-evidence/ 提供任务级及宏平均读出和干预表。[原八臂汇总脚本](../../scripts/history_interventions.py)与[导出 CSV](../../figures/history_interventions.csv)保留当前位姿条件的动作敏感性。新报告已完成原数组核查；论文侧另核对原生JSON、分析源码和聚合，不声称重新执行全部原数组比较。
- HISTORY1 读出协议：Research 的 docs/research_notes/assets/history_probe/ 与 docs/experiments/DB0-TRAIN0/assets/history_eight_probe/ 定义ridge、episode交叉拟合与oracle标签处理；HISTORY1/assets/probes/native.py定义实际基线和特征位置。[三联诊断图来源](../../figures/history_diagnostics_source.json)保留九臂源行及本稿100k区间，[绘图脚本](../../figures/plot_history_diagnostics.py)仅作静态读取和作图。
- BASE2 接受部署：Research 的 local_private/base2-combination-20261016/ 内 base2-controls-zone10-20261016-a1.zip（F）、base2-resumefix-zone10-20261016-a6.zip（I）与 payload-requeue-zone10-a4.zip；核对 CNN、完整 Window、目标 crop 重建及训练归一化，区别于后续 canonical 改动。
- 历史评测协议：Research 的 local_private/zenith-pro6000-history-20261011/asset-adapt/history-assets-a1.tar.gz 内 benchmark-source/configs/tasks/ 与 src/se3_wam_benchmark/envs/families/；失败映射在 evaluation/result.py:92–144，双指垫接触在 envs/base.py:257–290。future0-20261012/runtime-upload-a1/complete-runtime-assets.json 记录原件及完整读回；release-a3/payload.zip、上述 BASE2 F/I 包与 HISTORY1 migrate 包的 runtime-assets、benchmark_source 和十四套场景清单绑定相同历史资源。171 个 benchmark 文件与该仓库既有 41005787853052dd2b386abfe7313845ad9fa0f6 版本一致。该绑定证明接受包的配置来源，不代表新增逐个远端进程检查。

- 初态与运动采样：上述历史归档的 configs/scenarios/<task>.yaml 为 E7/agentview 配方，scenarios/_recipes.py 负责采样与坐标编译；不是 configs/tasks 的成功条件。release-a3/payload.zip 的 evaluation_reference/scenes/validation.jsonl 和 suites/sr_<task>.yaml 保存实际接受场景与筛选。T5 的原生 action_delay_steps 经 suite/rollout/make_env 到 control/action.py 的队列执行；与没有注入实测计算耗时分别解释。
- [历史评测本地材料](../../results/replay_materials/INDEX.md)：从上述两份原档提取评测器、配置、完整场景和划分，保留原件及路径变换说明；附录 A 的材料入口与原生解析范围。

## 写作核验

- [2026-10-18完整成稿规则](design_first_acceptance_20261018.md)：完整方法与实验协议的本轮设计、独立数字遮蔽评审及停止条件。新增协议不替代Research既有运行事实，待填测量不写成实测结论。
- 视觉状态参照的来源：[FoundationPose官方项目](https://nvlabs.github.io/FoundationPose/)、[SAM 2论文](https://arxiv.org/abs/2408.00714)与[官方实现](https://github.com/facebookresearch/sam2)；用于本轮因果估计路径选型，不代表本项目已完成部署验证。

- 正文、方法与数值表经过独立证据复核；方法公式对应当前标签和实际损失。
- 中文初稿先整理论证与重复限定，再润色语言，最后核对数字、比较范围与完成状态。
- [v1 文后核对说明](archive/verification_zh.tex)：v1 稿的待核实项目、旧稿缺依据的表述及该轮事实修正；已归档，仅追溯时读取。
- [CVPR 模板说明](../CVPR_TEMPLATE.md)：年度状态、编译与版面。
