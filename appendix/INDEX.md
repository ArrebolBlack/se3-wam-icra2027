# 独立补充材料索引（v4 方法论文版，2026-10-23）

[supplementary.tex](../supplementary.tex) 单独编译；[英文合并版](../paper_full.tex) 包含正文、参考文献和同一套附录。
[content.tex](content.tex) 按 A–D 装配，并设置附录专用的图表间距与浮动规则；开头导读已于 2026-10-25 删除（reading_map.tex 归档至 `local_private/archived-appendix-20261025/`），附录直接从 A 开始。中文对应文件在 [zh/appendix/](../zh/INDEX.md)。

- A [implementation.tex](implementation.tex)：场景与摘要 token、预测头、动作与主干、在 Dynamic-14 上训练、DROID 预训练与任务微调。
- B [benchmark.tex](benchmark.tex)：任务、角色与成功条件；场景、示范与数据划分；执行协议与延迟测量；基线与消融对照；指标与统计。
- C [results.tex](results.tex)：逐任务结果、五点延迟扫描与计时、DOMINO 和消融对照定义。
- D [real.tex](real.tex)：平台、装置布局与任务，位姿跟踪与示范标签，示范、微调与试验，详细结果与失败案例。

原 E（analysis）并入 A.1，原 F（扩展相关工作）取消，相关文件与 supp_interventions.tex 移至 `local_private/archived-appendix-20261025/`。

附录之间用 `\ref{app:...}`，引用正文用 `\mainref{...}`（独立补充经 `xr-hyper` 读取 `main.aux`）。
v1 的附录源码（protocol、q1_history 等）已移入 `local_private/archived-v1-20261020/`。

- 2026-11-02：设计研究（原 E）与误差分解（原 A.1）移入 `local_private/archived-appendix-20261102/`，正文不再指向；正文对附录只在 3.4、4.1、4.2、4.4 末尾各写一句不带字母的 "supplementary material" 指引。
