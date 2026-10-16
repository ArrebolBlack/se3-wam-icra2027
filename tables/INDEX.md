# 论文表格索引

数值来自 [Research 证据路由](../docs/writing/evidence_map.md)，不是拟定结果。

## 正文

- [system_results.tex](system_results.tex)：BASE1 系统参照与内部候选，区分训练和输入条件。
- [combination_results.tex](combination_results.tex)：BASE2 十二组组合筛选。
- [q1_results.tex](q1_results.tex)：HISTORY1 已完成八组与剩余条件。

## 补充材料

- [task_definitions.tex](task_definitions.tex)：接受部署包绑定的十四任务成功顺序、数值阈值与时限；中英文附录共享。
- [task_sampling.tex](task_sampling.tex)：历史 validation 配方中的初态、运动与事件提议范围；与具体接受场景及成功规则分别阅读。

- [system_budgets.tex](system_budgets.tex)：系统参照的训练预算、fixed140 计数与执行差异。
- [future_target_definitions.tex](future_target_definitions.tex)：原部署包中未来目标的尺寸、单位、几何支持与有效掩码；中英文附录共享。
- [history_encoders.tex](history_encoders.tex)：HISTORY1 的原始采样时间、表示张量、压缩接口和新增 token；中英文附录共享。
- [kinematic_prediction_results.tex](kinematic_prediction_results.tex)：DEV84 上 P15 与同可见 GT 历史条件下 CV/CA 的误差均值和中位数；不表示闭环收益。

以下五张表由[导出脚本](../scripts/build_evidence_tables.py)生成；数值更新先核对 Research。

- [future_complete.tex](future_complete.tex)：全部十五组，分别报告 fixed140 与 1,260 场补集。
- [future_paired.tex](future_paired.tex)：总体配对得失、逐项置信区间与校正精确检验。
- [future_tasks.tex](future_tasks.tex)：逐任务成功数。
- [future_failures.tex](future_failures.tex)：原生评测器失败类别。
- [combination_tasks.tex](combination_tasks.tex)：十二组组合及匹配 P00 控制的逐任务计数。
