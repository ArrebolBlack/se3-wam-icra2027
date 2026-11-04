# Fig2 概念稿 v6：FoveaWAM 架构

候选稿，尚未替换正文图 [fig2_se3wam.pdf](../../fig2_se3wam.pdf)。

- [矢量 PDF](fig2_concept_v6.pdf)、[300 dpi 预览](fig2_concept_v6.png)、[可编辑 SVG](fig2_concept_v6.svg)：三栏结构 (a) 训练视图、(b) 注意力 mask、(c) 缓存推理。
- [生成脚本](build_fig2_v6.py)：在仓库根目录运行 `python figures/Fig2/concepts/v6/build_fig2_v6.py`；PNG 用 PyMuPDF 导出（本机 pdftoppm 会被 MiKTeX 更新提示拦住）。
- [版面检查](layout_report.json)：文字越界与文字重叠检查结果。
- `assets/rgb.png`、`assets/depth.png`：从 [t1_belt.png](../../../Fig4/archive/benchmark/benchmark_frames/t1_belt.png) 裁出的同一帧 agentview RGB 与度量深度，是录制的教师数据，不是模型输出。其余几何图形均为示意。

相对当前正文图的设计变化：
- 配色与 Fig1 v5.2 一致：目标用青色，世界流/场景用赭色，动作用紫色。
- 每个读出头都放在它所读取 token 的正上方（patch → 场景流，mean(M) → 目标 SE(3)，A → 速度），身份上下贯通；虚线表示只在训练时使用，实线表示部署时使用。
- 主干占据视觉中心：共享 masked attention 横贯两个流，World FFN 和 Action FFN 分开，标注 ×24。
- 输入使用真实 RGB-D 缩略图；token 组用括号标注数量（S 212 / M 16 / A 8）；图中给出总损失。
- mask 与推理流程分别移到 (b)、(c)，主图不再画缓存箭头。
