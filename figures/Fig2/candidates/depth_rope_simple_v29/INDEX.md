# Depth 与 3D RoPE 简化预览 v29

状态：2026-11-16 局部候选，尚未采纳。用户认可点云方向，要求删除第一版的上方绕线和下方 Embed 说明；母版及其他版式保持原样。

- [与上一版对比](local_before_after.png)：上为第一版局部预览，下为本简化版。
- [与原 v27 对比](v27_before_after.png)：检查相对正式图的全部局部变化。
- [完整纸面预览](fig2_paper_width.png)、[整图前后对比 PDF](before_after.pdf)：PDF 第一页为 v27，第二页为本候选。
- [PPTX 副本](fig2_se3wam.pptx)、[PDF](fig2_se3wam.pdf)、[SVG](fig2_se3wam.svg)：可编辑候选和导出。
- [构建脚本](make_preview.py)、[核对结果](preview_check.json)、[导出信息](export_report.json)：复用上一候选源文件，使用现有 Windows PowerPoint 导出入口重建和核对。

只保留 Depth → 3D patch 锚点、同一个采样点 i / x_i，以及蓝色视觉 patch Q/K 的 `3D RoPE(x_i) · Q,K` 提示。
删除上方 RGB 绕线、下方深度/位置嵌入支路、Embed 文本和加号；其余原生对象不变。
点云、130 个显示锚点和对应采样点均沿用[第一版已核对的数据](../depth_rope_v28/INDEX.md#科学关系与素材)。
输入区的小图说明 Depth 派生的几何，未画点云到视觉编码器的连线。

导出维持 495 × 293.90625 pt；144 dpi 对比确认输入区和 RoPE 标注之外像素完全一致。
正式母版、正文资产和中英文图注未修改。
