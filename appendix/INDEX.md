# 独立补充材料索引（v3 方法论文版）

[supplementary.tex](../supplementary.tex) 单独编译；[英文合并版](../paper_full.tex) 包含正文、参考文献和同一套附录。
[content.tex](content.tex) 按 A–G 装配，[reading_map.tex](reading_map.tex) 提供阅读导航。中文对应文件在 [zh/appendix/](../zh/INDEX.md)。

- A [implementation.tex](implementation.tex)：条件 token、位姿跟踪器、世界与动作分支、R0–R5 耦合、训练配方和部署。
- B [pretraining.tex](pretraining.tex)：DROID 4D 标签、因果输入与离线标签、接触与外源运动、标签质量、规模和后训练。
- C [benchmark.tex](benchmark.tex)：任务与角色、场景与示范、实时协议、受控扫描、划分与统计、指标。
- D [evaluation.tex](evaluation.tex)：基线适配、DOMINO 与 LIBERO、真机协议与区间、计时。
- E [results.tex](results.tex)：逐任务结果、结局类别、协议与延迟对照、阴性结果、定性与视频说明。
- F [design.tex](design.tex)：完整组件研究，含历史、预测目标、耦合与主干、物理时间及干预协议。
- G [analysis.tex](analysis.tex)：交互误差分解、旋转与接触点、环境与间隙、领先时长、比例关系、量级和适用范围。

附录之间用 `\ref{app:...}`，引用正文用 `\mainref{...}`（独立补充经 `xr-hyper` 读取 `main.aux`）。
v1 的附录源码（protocol、q1_history 等）已移入 `local_private/archived-v1-20261020/`。
