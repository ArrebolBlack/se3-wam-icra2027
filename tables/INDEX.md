# 论文表格索引

实测数值来自 [Research 证据路由](../docs/writing/evidence_map.md)。完整协议中的未测量单元格统一为横线，不表示零或预设结果。
共用附录表用 `\tablelang{英文}{中文}` 选择文字，数值单元格与引用标签共用；英文入口取第一项，中文入口取第二项。生成表的翻译同时维护在现有导出脚本中。

## 正文

- [design_system_results.tex](design_system_results.tex)：完整系统在新场景、延迟、外部与真机评测中的结果位置；待填测量。
- [design_study_results.tex](design_study_results.tex)：D/E与选定主干下核心信息流比较；待填测量。
- [q1_results.tex](q1_results.tex)：HISTORY1 八种当前位姿条件与 GT-motion 参照的完整结果。

## 补充材料

- [system_results.tex](system_results.tex)：BASE1 系统参照与内部候选，保留开发集、训练和输入条件。
- [combination_results.tex](combination_results.tex)：BASE2十二组合及匹配控制，完整开发筛选。
- [design_granularity_results.tex](design_granularity_results.tex)：同族轨迹的角色、共享bank与采样分配；待填比较。
- [design_backbone_results.tex](design_backbone_results.tex)、[design_information_flow_results.tex](design_information_flow_results.tex)：D/E主干与完整R0–R6的成功率、生成调用及成本。
- [design_intervention_results.tex](design_intervention_results.tex)：冻结未来状态干预的动作、接触、成功率与有效覆盖；待填测量。
- [design_crosscheck_results.tex](design_crosscheck_results.tex)：历史/未来/信息流交互及未参与选择场景的确认。
- [design_pretraining_data.tex](design_pretraining_data.tex)、[design_scale_results.tex](design_scale_results.tex)：真实数据可用监督、模型/数据/训练预算矩阵。
- [design_transfer_results.tex](design_transfer_results.tex)、[design_initialization_results.tex](design_initialization_results.tex)：独立后训练、世界预训练消融与初始化控制。
- [design_delay_results.tex](design_delay_results.tex)：延迟、动作年龄、接触与部署成本；同步筛选与实测墙钟分别报告。
- [task_definitions.tex](task_definitions.tex)：接受部署包绑定的十四任务成功顺序、数值阈值与时限；中英文附录共享。
- [task_sampling.tex](task_sampling.tex)：历史 validation 配方中的初态、运动与事件提议范围；与具体接受场景及成功规则分别阅读。

- [system_budgets.tex](system_budgets.tex)：系统参照的训练预算、fixed140 计数与执行差异。
- [future_target_definitions.tex](future_target_definitions.tex)：原部署包中未来目标的尺寸、单位、几何支持与有效掩码；中英文附录共享。
- [history_encoders.tex](history_encoders.tex)：HISTORY1 的原始采样时间、表示张量、压缩接口和新增 token；中英文附录共享。
- [history_complete.tex](history_complete.tex)：九臂历史结果的 fixed140、1,260 补集和开发总分；中英文附录共享。
- [history_cross_round.tex](history_cross_round.tex)：旧轮保留GT运动与当前位姿轮的八编码结果；仅作跨轮描述，与新训GT参照及冻结干预分开。
- [history_tasks.tex](history_tasks.tex)：九臂逐任务成功数，由 history_uncertainty.py 从原生 episode 结果导出。
- [history_interventions.tex](history_interventions.tex)：八种当前位姿条件在过去图像重复/反序下的首动作变化；离线敏感性与闭环收益分别解释。
- [kinematic_prediction_results.tex](kinematic_prediction_results.tex)：DEV84 上 P15 与同可见 GT 历史条件下 CV/CA 的误差均值和中位数；不表示闭环收益。
- [q3_conditions.tex](q3_conditions.tex)：R0–R6 的监督、访问边和生成顺序计划；中英文附录共享，尚无实测结果。
- [batch_recipe.tex](batch_recipe.tex)、[batch_tasks.tex](batch_tasks.tex)：BATCH0八次完整训练的成功数、耗时及逐任务结果；由新增研究导出脚本生成。
- [decoder_confusion.tex](decoder_confusion.tex)：冻结夹爪两头的完整验证混淆矩阵；离线分类与闭环回归分开解释。

以下五张表由[导出脚本](../scripts/build_evidence_tables.py)生成；数值更新先核对 Research。

- [future_complete.tex](future_complete.tex)：全部十五组，分别报告 fixed140 与 1,260 场补集。
- [future_paired.tex](future_paired.tex)：总体配对得失、逐项置信区间与校正精确检验。
- [future_tasks.tex](future_tasks.tex)：逐任务成功数。
- [future_failures.tex](future_failures.tex)：原生评测器失败类别。
- [combination_tasks.tex](combination_tasks.tex)：十二组组合及匹配 P00/P03 控制的逐任务计数。
