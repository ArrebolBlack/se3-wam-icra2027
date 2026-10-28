# 附加延迟曲线（正文单栏图，`fig:latency`）

正文“Latency and protocols”段引用的延迟扫描图：SR 随附加延迟 0–200 ms 的变化。保留原图六条计划序列并加入 DP；五个方法在图例中注明待测。ACT、DP 已有 0/150 ms 实测点；保留真实零值，不跨缺失点连线。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：单栏浮动体、图注和 `fig:latency` 标签。
- [英文 PDF](latency.pdf)、[中文 PDF](latency_zh.pdf)：当前导出；同名 SVG、PNG 供编辑与预览。
- [绘图脚本](plot_latency.py)：直接读取共用的 [supp_latency.tex](../../tables/supp_latency.tex)，填数后重绘。
- [来源与复现](SOURCE.md)：数据来源、序列选择与复现命令。
- [绘图依赖](requirements.txt)。

目录暂不编号：插入后正文图号为 Fig. 5，原 Fig5（消融）与 Fig6（真机）在 PDF 中顺延为 Fig. 6、7；目录重新编号待 Fig. 6 调整完成后统一进行。
