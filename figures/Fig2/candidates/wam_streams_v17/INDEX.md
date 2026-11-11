# WAM 主干分组候选 v17

针对 v16 的单层算子重复过多，改用一张完整层的正面与整体层堆叠。正式论文仍采用 v15。

- [主干前后对照](backbone_before_after.png)、[主干局部](backbone_detail.png)：左为上一候选 v16，右为本候选；比较模型轮廓、共享范围与阅读密度时查看。
- [整图对照 PDF](comparison.pdf)：三页依次为正式 v15、上一候选 v16、本候选 v17。
- [整图 PDF](fig2_se3wam.pdf)、[PNG](fig2_se3wam.png)、[论文宽度预览](fig2_paper_width.png)：查看与输入、输出及 b/c 的比例时读取。
- [可编辑 SVG](fig2_se3wam.svg)、[可编辑 PPTX](fig2_se3wam.pptx)：继续精修时使用；几何、文字和箭头均为独立矢量对象，只有 RGB/Depth 为原缩略图。
- [图源](build_fig2.py)、[PPTX 入口](build_fig2_pptx.mjs)、[对象转换](pptx_scene.py)：重建图源与原生对象时读取。
- [参考与取舍](references.md)：查看近期 WAM 原图的画法、借用部分及结构差异时读取。
- [布局](layout_metadata.json)、[导出信息](export_report.json)：核对位置、字号和最终状态读出时读取。
- [素材](assets/INDEX.md)：核对输入和参考监督的来源时读取。

World 区域共同容纳 S/M，Action 区域容纳 A。一条共享 masked attention 带贯穿两区，S/M 使用同一个 World FFN，A 使用 Action FFN；每个状态保留两次残差。整层背后的轮廓及 ×L 表示逐层重复，不表示三个独立模型。S_L/M_L/A_L 表示最终状态，算子文字仍逆时针旋转 90°。

输入与 token、角色配色、几何示例及 b/c 保留。几何仍是录制的参考监督示例；本候选只改变主干的视觉层级。
