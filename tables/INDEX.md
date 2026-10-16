# 论文表格索引

数值来自 [Research 证据路由](../docs/writing/evidence_map.md)，不是拟定结果。

## 正文

- [system_results.tex](system_results.tex)：BASE1 系统参照与内部候选，区分训练和输入条件。
- [combination_results.tex](combination_results.tex)：BASE2 十二组组合筛选。
- [q1_results.tex](q1_results.tex)：HISTORY1 已完成五组与剩余条件。

## 补充材料

- [task_definitions.tex](task_definitions.tex)：十四任务标识与交互类型，中英文共享以支持逐任务表引用。

- [system_budgets.tex](system_budgets.tex)：系统参照的训练预算、fixed140 计数与执行差异。

以下五张表由[导出脚本](../scripts/build_evidence_tables.py)生成；数值更新先核对 Research。

- [future_complete.tex](future_complete.tex)：全部十五组，分别报告 fixed140 与 1,260 场补集。
- [future_paired.tex](future_paired.tex)：总体配对得失、原始精确检验与多重比较校正。
- [future_tasks.tex](future_tasks.tex)：逐任务成功数。
- [future_failures.tex](future_failures.tex)：原生评测器失败类别。
- [combination_tasks.tex](combination_tasks.tex)：十二组组合的逐任务计数。
