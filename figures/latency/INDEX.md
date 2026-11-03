# 附加延迟曲线（正文单栏、左右双面板，`fig:latency`）

正文推理延迟段引用的延迟扫描图：SR随附加延迟0–200 ms的变化。3.25 × 2.60 in单栏内左右面板分别展示策略与SE(3)历史配对比较，右侧使用矩阵图例，底部共用Ours图例；十配置五点均已验收，阴影表示按任务分层的场景bootstrap 95%区间。最终模型仍待补，已预留图例及颜色。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：单栏浮动体、图注和 `fig:latency` 标签。
- [英文 PDF](latency.pdf)、[中文 PDF](latency_zh.pdf)：当前导出；同名 SVG、PNG 供编辑与预览。
- [英文排版预览](latency_preview.pdf)、[中文排版预览](latency_preview_zh.pdf)：已通过的布局，加入明确标注的Ours合成占位曲线；论文暂引此版，caption保持原文。数值不得用于实验结论。
- [绘图脚本](plot_latency.py)：读取已接收JSON的点估计与区间，核对共用的 [supp_latency.tex](../../tables/supp_latency.tex) 后重绘。
- [来源与复现](SOURCE.md)：数据来源、序列选择与复现命令。
- [绘图依赖](requirements.txt)。

当前正文编译编号为 Fig. 4；图号以 `fig:latency` 的实际编译结果为准。
