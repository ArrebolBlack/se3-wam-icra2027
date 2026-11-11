# b/c 与 M 角色配色候选 v15

已采纳到[正式图目录](../../INDEX.md)。本目录保留审核快照；后续修改使用正式目录中的源文件与 PPTX。

- [可编辑 PPTX](fig2_se3wam.pptx)、[可编辑 SVG](fig2_se3wam.svg)：审阅或继续精修时读取。
- [整图 PDF 前后对照](before_after.pdf)：第一页为被替代的 v14，第二页为本轮已采纳版本。
- [b/c 前后对照](bc_before_after.png)、[新版局部](bc_detail.png)：上方为被替代的 v14、下方为已采纳的 v15；核对阅读方向与缓存／状态路径时查看。
- [完整 PNG](fig2_se3wam.png)、[PDF](fig2_se3wam.pdf)、[纸面宽度预览](fig2_paper_width.png)：核对整体、主干 M 配色和缩印效果时查看。
- [生成源](build_fig2.py)、[PPTX 生成源](build_fig2_pptx.mjs)、[对象转换](pptx_scene.py)：重建时读取。
- [布局](layout_metadata.json)、[导出核查](export_report.json)、[局部核查](candidate_review.json)：核对保留范围、mask 和连接关系时读取。
- [素材索引](assets/INDEX.md)：核对真实输入、参考监督及原创机器人图标时读取。

M 使用与 S 相邻的低饱和冷色；共享 World FFN 保持统一颜色。b 保留 S/M/A 块级 mask，增加 Q/K 方向和禁读纹理。c 压缩联合训练，World prefill 生成 S/M 各层注意力输入的 K/V；固定缓存从上方作为条件输入，下方噪声进入 Action 更新循环并输出单个机器人动作图标。

Action update 表示一次采样更新中贯穿所有层的 Action 计算及状态更新；反馈不包含 world prefill 或 K/V bank。Token、堆叠和动作图标均为示意；几何输出仍为实录参考监督。a 的几何、排版和字号均保留，仅调整 M 的颜色标识。
