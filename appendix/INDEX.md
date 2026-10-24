# 独立补充材料索引（v4 方法论文版，2026-10-23）

[supplementary.tex](../supplementary.tex) 单独编译；[英文合并版](../paper_full.tex) 包含正文、参考文献和同一套附录。
[content.tex](content.tex) 按 A–F 装配，[reading_map.tex](reading_map.tex) 提供阅读导航。中文对应文件在 [zh/appendix/](../zh/INDEX.md)。

- A [implementation.tex](implementation.tex)：场景与摘要 token、预测头、动作与主干、训练配方、DROID 预训练与任务微调、部署。
- B [benchmark.tex](benchmark.tex)：任务与角色、场景与示范、实时协议、基线适配、划分与统计、指标与计时。
- C [real.tex](real.tex)：六任务装置、成功条件、无标记跟踪与球体旋转屏蔽、示范和评测试验。
- D [results.tex](results.tex)：逐任务与失败结果、协议与延迟、DOMINO、位姿噪声、四层筛选、离线预测诊断和视频。
- E [analysis.tex](analysis.tex)：平移与旋转误差分解、接触点、环境间隙及适用范围。
- F [related.tex](related.tex)：动态操作与延迟、世界模型、3D 与运动表示的扩展相关工作。

附录之间用 `\ref{app:...}`，引用正文用 `\mainref{...}`（独立补充经 `xr-hyper` 读取 `main.aux`）。
v1 的附录源码（protocol、q1_history 等）已移入 `local_private/archived-v1-20261020/`。
