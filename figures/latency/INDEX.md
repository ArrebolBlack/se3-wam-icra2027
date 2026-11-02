# 附加延迟曲线（正文单栏图，`fig:latency`）

正文推理延迟段引用的延迟扫描图：SR 随附加延迟 0–200 ms 的变化。保留既有七条计划序列；六个基线的五点均已验收，最终模型注明待测。OpenWAM采用官方加速组；其关闭加速组及其他基线保留在完整表内。不跨缺失点连线。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：单栏浮动体、图注和 `fig:latency` 标签。
- [英文 PDF](latency.pdf)、[中文 PDF](latency_zh.pdf)：当前导出；同名 SVG、PNG 供编辑与预览。
- [绘图脚本](plot_latency.py)：直接读取共用的 [supp_latency.tex](../../tables/supp_latency.tex)，填数后重绘。
- [来源与复现](SOURCE.md)：数据来源、序列选择与复现命令。
- [绘图依赖](requirements.txt)。

当前正文编译编号为 Fig. 4；图号以 `fig:latency` 的实际编译结果为准。
