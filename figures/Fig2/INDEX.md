# Fig2：SE(3)-WAM 架构

当前采用 2026-11-04 连续历史与紧凑动作采样版：Target history 共用参考显示累计运动，c 使用居中噪声、模块内循环标志和单个机器人输出。保留既定主干与开放式 a/b/c 布局。中英文稿共用 PDF，后续局部精修从本目录的 `build_fig2.py` 与 `assets/` 接续。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：当前图体、图注与标签 `fig:architecture`；修改本图时读取。
- [论文矢量图](fig2_se3wam.pdf)、[预览](fig2_se3wam.png)：当前正文插图与快速查看入口。
- [可编辑 SVG](fig2_se3wam.svg)、[生成脚本](build_fig2.py)：修改图形、文字或重建导出时读取。
- [纸面宽度预览](fig2_paper_width.png)、[布局坐标](layout_metadata.json)：检查缩印阅读、文字位置和连线时读取；由绘图脚本重建。
- [导出核查](export_report.json)：查看矢量、字体、输入连接及保留图块的检查结果。
- [素材索引](assets/INDEX.md)：当前 RGB-D、几何标签与来源；修改真实示例时读取。
- [来源与重建说明](README.txt)：当前版本、模型依据、实录与示意范围、重建命令。
- [正文入口](../../sections/method.tex)、[中文正文入口](../../zh/sections/method.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查旧稿的可编辑源、导出图、脚本和数据时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。

当前图的详细要求以图源为准，新资产与脚本放入本目录；被替代的版本移入 `archive/` 并更新其索引。
