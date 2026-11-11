# 字体与输入侧精修 v14

已采纳到[正式图目录](../../INDEX.md)。本目录保留审核快照；后续修改使用正式目录中的源文件与 PPTX。

基于当前论文版的可编辑排版候选：图内标签缩小约 13%，a/b/c 小标题统一；RGB-D、Target history、Robot state 和 Noisy actions 四行等距分布。较大的 token 连续排成一列，用颜色和小间隙区分，移除汇合线及 token 到主干的箭头。Summary M 标注 learned token 段，不占第五行输入。

- [可编辑 PPTX](fig2_se3wam.pptx)、[可编辑 SVG](fig2_se3wam.svg)：审阅或继续精修时读取。
- [论文尺寸 PDF](fig2_se3wam.pdf)、[预览 PNG](fig2_se3wam.png)、[实际宽度预览](fig2_paper_width.png)：核对整体效果和缩印阅读时查看。
- [前后对照](before_after.pdf)：第一页为被替代的 v13，第二页为本轮已采纳版本。
- [生成源](build_fig2.py)、[PPTX 生成源](build_fig2_pptx.mjs)、[对象转换工具](pptx_scene.py)：重建图形或 PowerPoint 时读取。
- [布局参数](layout_metadata.json)、[导出信息](export_report.json)、[局部核查](candidate_review.json)：核对布局与保留范围时读取。
- [素材索引](assets/INDEX.md)：核对图像、原始几何标签和原创图标来源时读取。

主干、两次残差、逐层状态更新、右侧几何示例及下方 b/c 布局与当前采用版一致，仅调整其文字大小。Token 数量为排版示意；RGB-D、目标历史和机器人状态属于 S，learned summaries 属于 M，noisy actions 属于 A。几何示例仍为实录参考监督。
