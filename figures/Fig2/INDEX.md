# Fig2：SE(3)-WAM 架构

当前为 v3 列对齐稿（2026-10-29）：每个读出头位于其读取的 token 正上方，输入缩略图、几何输出与动作块都取自同一条传送带轨迹；中英文稿共用 PDF；6.875 × 2.46 in。由 matplotlib 生成（Windows 下自动用 Arial）。`layout_text_boxes.json` 属上一版，已不再更新；`assets/flow_gt.svg`、`target_se3_gt.svg` 仍是上一版脚本导出的独立面板。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：当前图体、图注与标签 `fig:architecture`；修改本图时读取。
- [论文矢量图](fig2_se3wam.pdf)、[预览](fig2_se3wam.png)：当前正文插图与快速查看入口。
- [可编辑 SVG](fig2_se3wam.svg)、[生成脚本](build_fig2.py)：修改图形、文字或重建导出时读取。
- [文字位置清单](layout_text_boxes.json)：重建后的文本边界与分组；检查裁切和重叠时读取。
- [来源与重建说明](README.txt)：模型依据、示意图范围和重建命令。
- [画面与标签](assets/INDEX.md)：同 Fig.4 传送带轨迹的真实 RGB-D、GT 流/位姿、专家 EEF 和开发机验证结果。
- [标签导出](export_labels.py)、[独立核验](verify_labels.py)：在开发机从原始 HDF5 重建和验证时使用。
- [正文入口](../../sections/method.tex)、[中文正文入口](../../zh/sections/method.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查旧稿的可编辑源、导出图、脚本和数据时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。

当前图的详细要求以图源为准，新资产与脚本放入本目录；被替代的版本移入 `archive/` 并更新其索引。
