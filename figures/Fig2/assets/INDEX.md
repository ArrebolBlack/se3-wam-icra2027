# Fig2 输入与监督示例

- [RGB](rgb.png)、[Depth](depth.png)：同一录制状态的 specular 0.10 Blender RGB 示意与原始深度；RGB 复用 Fig. 2 已校验的 frame 29，两者不是逐像素配准的渲染对。
- [监督数组](geometry_labels.npz)：当前工作区、稀疏位移及有效性、目标历史和未来位姿；重建几何示例时读取。
- [原创机器人 SVG](robot_arm.svg)：透明背景的原生矢量素材；编辑 Robot state 与 Action chunk 图标时读取。
- [来源与显示范围](source.json)：轨迹、当前帧、历史参考、时域、flow 放大和示意范围；核验素材时读取。
- [Blender flow 场景](blender/INDEX.md)：当前状态底图、可编辑原生场景与相机/材质记录；重渲染或修改背景时读取。

文字、模块、flow 标注、SE(3) 字形和机器人符号在编辑源中以原生对象保留。[Fig2 PowerPoint](../fig2_se3wam.pptx)

流示例依次显示 +50、+200、+400 ms，沿实录的 50 ms 采样轨迹使用 turbo 0.12–0.66 渐变箭头，箭身、头部及时间图例均无描边，位移保持原来的 3 倍显示比例。目标历史和未来的 T 形模型保留与场景一致的橙色及原有分面明暗、时间淡化，原点为白点红边，坐标轴保持 RGB；历史轨迹仍为灰色，预测轨迹仍为红色虚线，轨迹与坐标轴均无白色衬边。
