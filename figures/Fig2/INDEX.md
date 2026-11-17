# Fig2：SE(3)-WAM 架构

当前采用 v28（作者选定的 A 版）：5 处机械臂改为 `assets/icons_v28/` 中的原创线框图标，转换为原生矢量形状；Action chunk 从左到右使用 p1、p2、p3，Robot state 与推理输出使用 p2。两块噪声改为 32 × 32 高斯噪声位图，消除小矩形拼接细缝，保留原外框、尺寸和虚线分组框。v27 的版式、文字、配色与其他素材保持不变。中英文稿共用同一矢量 PDF，后续精修以 PowerPoint 为编辑源。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：当前图体、图注与标签 `fig:architecture`；修改本图时读取。
- [论文矢量图](fig2_se3wam.pdf)、[预览](fig2_se3wam.png)：当前正文插图与快速查看入口。
- [可编辑 SVG](fig2_se3wam.svg)、[导出脚本](build_fig2.py)：从 PowerPoint 生成 SVG、PDF 和预览时读取。
- [可编辑 PowerPoint](fig2_se3wam.pptx)：当前论文版的单页原生对象，文字、箭头和图形可分别编辑；在 PowerPoint 中精修时读取。
- [纸面宽度预览](fig2_paper_width.png)：核对缩印后的文字与连线。
- [600 dpi PNG](fig2_se3wam_600dpi.png)：需要高分辨率位图导出时使用。
- [导出核查](export_report.json)：查看图页尺寸、矢量路径、位图和 SVG 文本统计。
- [素材索引](assets/INDEX.md)：当前 RGB-D、几何标签与来源；修改真实示例时读取。
- [v28 图标与噪声](assets/icons_v28/INDEX.md)：作者选定的三个机械臂姿态、两块高斯噪声及生成源。
- [素材渲染](render_assets.py)、[素材更新](update_assets.py)：按共享 Blender 参数重渲染背景，并从真实标签更新 PowerPoint 内的可编辑流与目标样式；更新素材后再运行导出脚本。
- `update_assets.py --icons-v28` 仅替换五个机械臂组和两块噪声；普通导出直接运行 `build_fig2.py`。导出会保留噪声原始 PNG 像素、禁用 PDF 插值，并检查每个机械臂区域没有位图。
- [来源与重建说明](README.txt)：当前版本、模型依据、实录与示意范围、重建命令。
- [正文入口](../../sections/method.tex)、[中文正文入口](../../zh/sections/method.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查旧稿的可编辑源、导出图、脚本和数据时读取。
- [排版候选](candidates/INDEX.md)：审阅主干、输入、token、字体及 b/c 机制的后续精修时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。

当前图的详细要求以图源为准，新资产与脚本放入本目录；被替代的版本移入 `archive/` 并更新其索引。
