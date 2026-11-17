# Depth 与 3D RoPE 局部预览 v28

状态：2026-11-16 按用户要求在 v27 副本上制作，尚未采纳。上一级正式 PPTX、PDF 和中英文图注均未修改。

- [局部前后对比](local_before_after.png)：上为 v27，下为本候选；比较输入行与 Q/K/V 局部时查看。
- [完整纸面预览](fig2_paper_width.png)、[整图前后对比 PDF](before_after.pdf)：检查原版式中的效果；PDF 第 1 页为 v27，第 2 页为候选。
- [可编辑候选 PPTX](fig2_se3wam.pptx)、[PDF](fig2_se3wam.pdf)、[SVG](fig2_se3wam.svg)：本轮局部方案的源文件与导出。
- [构建脚本](make_preview.py)：使用[制作时的 v27 输入与导出工具](base_v27/INDEX.md)生成候选与对比；从论文环境运行。该输入随候选保留，不随正式母版更新。
- [局部核对](preview_check.json)、[导出信息](export_report.json)：检查改动范围、实际点坐标和纸面尺寸。

## 本轮范围

Current RGB-D 的两张缩略图在原输入框内缩小并重排，新增真实深度反投影的稀疏 patch 锚点。
RGB 独立进入原 Vision Encoder；平均深度与三维位置经嵌入，在其后加入视觉 patch token。
Q/K/V 列只新增指向蓝色视觉 patch 代表 token 的 `3D RoPE(x_i) · Q,K` 标注。
主干、其他输入和读出、全部面板、标题、尺寸与原有虚线保持原样。

## 科学关系与素材

- 依据 `sections/method.tex`、`appendix/implementation.tex` 和模型仓的 `frame_encoder.py`、`attention.py`。
- 输入场景背景来自 `assets/geometry_labels.npz` 的实录显示点云；蓝色锚点来自其中的 196 个 patch 源点，按已有显示范围展示 130 个。
- 选中的第 173 号 patch（从 0 计数）对应原始 Depth 像素 `(87,199)`，与三维小图的 `x_i` 一一对应。所有 196 个点由现有深度和标定重算，与保存坐标的最大绝对差为 0 m。
- 图中点的投影沿用现有场景的正交视角；模型使用机器人基座系坐标。RGB 仍为已有 Blender 示意，不声称与原始 Depth 逐像素配准。
- 3D RoPE 仅标在视觉 patch 的 Q/K 上，未扩展到 V、目标、机器人、M 或 A token。

## 验证与后续判断

使用 Windows Microsoft PowerPoint 导出。原有对象仅调整两张输入图及对应边框共 4 项，另 258 个顶层对象保留；嵌套对象随其原始组完整保留。
144 dpi 逐像素对比确认两个局部区域以外没有变化，纸面尺寸仍为 495 × 293.90625 pt。
此次新增说明增加了输入区的局部密度；是否采用点云、几何支路和竖排 RoPE 标注，等待用户审阅。
