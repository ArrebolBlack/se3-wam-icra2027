# 附加延迟曲线（正文单栏、左右双面板，`fig:latency`）

3.25 × 2.60 in 单栏内左右面板展示策略与 SE(3) 历史在 0–150 ms 附加延迟下的 SR（+200 ms 时 8 条与 10 条指令的动作块已无法覆盖到下一动作块到达，该档只保留在 Table S5）。BF16 Full last 绘制四个实测点，区间采用任务分层场景 bootstrap。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：单栏浮动体、图注和 `fig:latency` 标签。
- [英文 PDF](latency.pdf)、[中文 PDF](latency_zh.pdf)：当前导出；同名 SVG、PNG 供编辑与预览。
- [历史英文排版预览](latency_preview.pdf)、[中文排版预览](latency_preview_zh.pdf)：含合成占位曲线的旧布局检查，不再用于论文。
- [绘图脚本](plot_latency.py)：读取已接收JSON的点估计与区间，核对共用的 [supp_latency.tex](../../tables/supp_latency.tex) 后重绘。
- [来源与复现](SOURCE.md)：数据来源、序列选择与复现命令。
- [绘图依赖](requirements.txt)。

当前正文编译编号为 Fig. 5，标签为 `fig:latency`。
