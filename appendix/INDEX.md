# 独立补充材料索引（v2）

[supplementary.tex](../supplementary.tex) 单独编译；[英文合并版](../paper_full.tex) 包含正文、参考文献和同一套附录。
[content.tex](content.tex) 按 A–G 装配，[reading_map.tex](reading_map.tex) 提供阅读导航。中文对应文件在 [zh/appendix/](../zh/INDEX.md)。

- A [analysis.tex](analysis.tex)：交互误差分解的推导、旋转与接触点、环境与间隙、分块执行下的领先时长、**定量预测**（临界领先时长、临界噪声、时域偏移、间隙、坍缩）、量级与适用范围。
- B [benchmark.tex](benchmark.tex)：任务、**角色与临界领先时长**、误差项、场景与示范、共享执行器与实时协议、受控扫描（速度/延迟/间隙/噪声/遮挡）、划分与统计、指标。
- C [implementation.tex](implementation.tex)：条件 token、**位姿跟踪器**（含无模型历史）、世界分支、动作分支（领先时长嵌入、延迟采样、增量参考）、耦合掩码、训练配方、部署。
- D [design.tex](design.tex)：完整设计研究——记住、预测、行动与交互检验，含选择规则、冻结读出与干预协议；全部报告留出集数值。
- E [pretraining.tex](pretraining.tex)：DROID 的划分与时间、目标/先验/深度来源、因果输入与离线标签、接触与外源运动、有效性偏差、标签质量、配方与规模、独立后训练。
- F [evaluation.tex](evaluation.tex)：基线（共同条件、调参预算、复现、+SE(3) 注入、运动学基线）、DOMINO 与 LIBERO、真机协议与 Wilson 区间、计时。
- G [results.tex](results.tex)：各任务结果（所有方法）、结局类别、协议对照与延迟扫描、阴性与无效结果、生效时刻的定性对齐、补充视频说明。

附录之间用 `\ref{app:...}`，引用正文用 `\mainref{...}`（独立补充经 `xr-hyper` 读取 `main.aux`）。
v1 的附录源码（protocol、q1_history 等）已移入 `local_private/archived-v1-20261020/`。
