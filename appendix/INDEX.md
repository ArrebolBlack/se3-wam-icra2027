# 独立补充材料索引（v4 方法论文版，2026-10-23）

[supplementary.tex](../supplementary.tex) 单独编译；[英文合并版](../paper_full.tex) 包含正文、参考文献和同一套附录。
[content.tex](content.tex) 按 A–E 装配（2026-10-25 重排），[reading_map.tex](reading_map.tex) 提供阅读导航与补充视频说明。中文对应文件在 [zh/appendix/](../zh/INDEX.md)。

- A [implementation.tex](implementation.tex)：误差分解（A.1）、场景与摘要 token、预测头、动作与主干、在 Dynamic-14 上训练、DROID 预训练与任务微调。
- B [benchmark.tex](benchmark.tex)：任务、角色与成功条件；场景、示范与数据划分；执行协议与延迟测量；基线与消融对照；指标与统计。
- C [results.tex](results.tex)：逐任务结果与失败、最终消融与种子稳定性、协议延迟与计时、位姿噪声（定义与结果）、预测诊断、DOMINO。
- D [real.tex](real.tex)：平台、装置布局与任务，位姿跟踪与示范标签，示范、微调与试验，详细结果与失败案例。
- E [design.tex](design.tex)：四层模型的初步设计研究（编码器、主干与历史；预测目标与辅助监督；世界—动作耦合）。

原 E（analysis）并入 A.1，原 F（扩展相关工作）取消，相关文件与 supp_interventions.tex 移至 `local_private/archived-appendix-20261025/`。

附录之间用 `\ref{app:...}`，引用正文用 `\mainref{...}`（独立补充经 `xr-hyper` 读取 `main.aux`）。
v1 的附录源码（protocol、q1_history 等）已移入 `local_private/archived-v1-20261020/`。
