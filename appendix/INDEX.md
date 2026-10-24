# 独立补充材料索引（v4 方法论文版，2026-10-23）

[supplementary.tex](../supplementary.tex) 单独编译；[英文合并版](../paper_full.tex) 包含正文、参考文献和同一套附录。
[content.tex](content.tex) 按 A–H 装配，[reading_map.tex](reading_map.tex) 提供阅读导航。中文对应文件在 [zh/appendix/](../zh/INDEX.md)。

- A [implementation.tex](implementation.tex)：场景与摘要 token、无标记位姿标签与因果输入、真机球体分量屏蔽、预测头、动作流、主干耦合与部署。
- B [pretraining.tex](pretraining.tex)：DROID 数据与划分、基座学习的内容（无目标位姿）、PointWorld 流标签、配方与规模、逐任务微调（Research PW0）。
- C [benchmark.tex](benchmark.tex)：任务与角色、场景与示范、实时协议、受控扫描、划分与统计、指标。
- D [evaluation.tex](evaluation.tex)：基线适配、DOMINO四方法最小比较、真机协议与区间、计时。
- E [results.tex](results.tex)：逐任务结果、结局类别、协议与延迟对照、阴性结果、定性与视频说明。
- F [design.tex](design.tex)：最终24层四核心对照、已完成四层筛选与静止历史干预、三种合成噪声及离线外推误差。
- G [analysis.tex](analysis.tex)：交互误差分解、旋转与接触点、环境与间隙、滚动重规划下的领先时长、比例关系、量级和适用范围。
- H [related.tex](related.tex)：动态操作与延迟、世界模型、3D 与运动表示的扩展相关工作。

附录之间用 `\ref{app:...}`，引用正文用 `\mainref{...}`（独立补充经 `xr-hyper` 读取 `main.aux`）。
v1 的附录源码（protocol、q1_history 等）已移入 `local_private/archived-v1-20261020/`。
