# Fig2：SE(3)-WAM 架构

当前采用 v25。目标历史和未来监督以同一目标的连续轨迹及三色位姿轴呈现，图中文字统一使用 Arial Regular 和 Arial Bold。中英文稿共用同一矢量 PDF，后续精修以 PowerPoint 为编辑源。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：当前图体、图注与标签 `fig:architecture`；修改本图时读取。
- [论文矢量图](fig2_se3wam.pdf)、[预览](fig2_se3wam.png)：当前正文插图与快速查看入口。
- [可编辑 SVG](fig2_se3wam.svg)、[导出脚本](build_fig2.py)：从 PowerPoint 生成 SVG、PDF 和预览时读取。
- [可编辑 PowerPoint](fig2_se3wam.pptx)：当前论文版的单页原生对象，文字、箭头和图形可分别编辑；在 PowerPoint 中精修时读取。
- [纸面宽度预览](fig2_paper_width.png)：核对缩印后的文字与连线。
- [600 dpi PNG](fig2_se3wam_600dpi.png)：需要高分辨率位图导出时使用。
- [导出核查](export_report.json)：查看图页尺寸、矢量路径、位图和 SVG 文本统计。
- [素材索引](assets/INDEX.md)：当前 RGB-D、几何标签与来源；修改真实示例时读取。
- [来源与重建说明](README.txt)：当前版本、模型依据、实录与示意范围、重建命令。
- [正文入口](../../sections/method.tex)、[中文正文入口](../../zh/sections/method.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查旧稿的可编辑源、导出图、脚本和数据时读取。
- [排版候选](candidates/INDEX.md)：审阅主干、输入、token、字体及 b/c 机制的后续精修时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。

当前图的详细要求以图源为准，新资产与脚本放入本目录；被替代的版本移入 `archive/` 并更新其索引。
