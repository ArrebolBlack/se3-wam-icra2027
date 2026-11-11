# Fig2 输入与监督示例

- [RGB](rgb.png)、[Depth](depth.png)：同一录制状态的 Blender RGB 示意与原始深度；核对输入缩略图时读取，两者不是逐像素配准的渲染对。
- [监督数组](geometry_labels.npz)：当前工作区、稀疏位移及有效性、目标历史和未来位姿；重建几何示例时读取。
- [原创机器人 SVG](robot_arm.svg)：透明背景的原生矢量素材；编辑 Robot state 与 Action chunk 图标时读取。
- [来源与显示范围](source.json)：轨迹、当前帧、历史参考、时域、flow 放大和示意范围；核验素材时读取。
- [Blender flow 场景](blender/INDEX.md)：当前状态底图、可编辑原生场景与相机/材质记录；重渲染或修改背景时读取。

文字、模块、flow 标注、SE(3) 字形和机器人符号在编辑源中以原生对象保留。[Fig2 PowerPoint](../fig2_se3wam.pptx)
