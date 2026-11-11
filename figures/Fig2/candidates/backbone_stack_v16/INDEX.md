# 多层 Transformer 主干候选 v16

供与正式 v15 比较，正式论文尚未替换。

- [可编辑 PPTX](fig2_se3wam.pptx)、[SVG](fig2_se3wam.svg)：审阅或继续精修时读取。
- [主干前后对照](backbone_before_after.png)、[新版主干](backbone_detail.png)：左侧为 v15，右侧为本候选；比较整体体量与逐层结构时查看。
- [整图 PDF 前后对照](before_after.pdf)：第一页为正式 v15，第二页为本候选。
- [完整 PNG](fig2_se3wam.png)、[PDF](fig2_se3wam.pdf)、[纸面宽度预览](fig2_paper_width.png)：核对模型整体、缩印和与其他面板的关系时查看。
- [生成源](build_fig2.py)、[PPTX 生成源](build_fig2_pptx.mjs)、[对象转换](pptx_scene.py)：重建可编辑图形时读取。
- [布局](layout_metadata.json)、[导出核查](export_report.json)、[局部核查](candidate_review.json)：核对重复层、残差、最终状态及保留范围时读取。
- [素材索引](assets/INDEX.md)：核对实录监督与原图标来源时读取。

主干以完整的 World–Action Transformer 包住沿深度排列的代表层，层间省略号与 L layers 括号表示整体层数，图中三组并非实际只有三层。只标注中间代表层的算子；算子文字仍逆时针旋转 90°。每层共享 masked attention，S/M 共用一个 World FFN，A 使用 Action FFN，各状态均保留两次残差更新。预测由最终 S_L、M_L、A_L 状态读出。

原输入与 token 列、角色配色、几何示例及 b/c 完整保留。几何示例仍为实录参考监督；图中不新增参数规模、预训练来源或其他未实现的网络分支。
