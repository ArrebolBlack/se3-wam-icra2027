# 延迟与策略排名（正文单栏、三面板，`fig:latency`）

3.25 × 4.50 in 单栏图：(a, b) 为 0–150 ms 附加延迟下的策略与 SE(3) 历史对比；(c) 为 Table 1 的 Paused／Native 成功率、p95 与名次。复现与数据说明见 [SOURCE.md](SOURCE.md)。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：单栏浮动体、图注和 `fig:latency` 标签。
- [英文 PDF](latency.pdf)、[中文 PDF](latency_zh.pdf)：当前导出；同名 SVG、PNG 供编辑与预览。
- [历史英文排版预览](latency_preview.pdf)、[中文排版预览](latency_preview_zh.pdf)：含合成占位曲线的旧布局检查，不再用于论文。
- [绘图脚本](plot_latency.py)：读取延迟扫描与主表 JSON，核对 Table S5 和 Native 点后重绘中英文三面板。
- [来源与复现](SOURCE.md)：数据来源、序列选择与复现命令。
- [绘图依赖](requirements.txt)。
- [导出检查](layout_report.json)：通过的图版之数据坐标、区间端点、尺寸、字体与纯矢量检查。

当前正文编译编号为 Fig. 6，标签为 `fig:latency`。

配色读取[共享颜色](../method_colors.json)：(a, b) 使用 `methods`，(c) 使用与 Fig. 1 相同的 `categories`。
