# v15 素材

沿用正式 v14 的素材，保留副本以独立重建候选。

- [RGB](rgb.png)、[Depth](depth.png)：输入缩略图；核对 Blender 示例与原始深度时读取。
- [几何标签](geometry_labels.npz)、[来源](source.json)：历史 SE(3) 与未来参考监督；调整真实几何示例时读取。
- [机器人图标](robot_arm.svg)：原创透明矢量；调整状态和 action chunk 符号时读取。
- [紧凑主干](backbone_v2.svg)、[布局](backbone_v2_layout.json)：已采用结构的局部源；核对共享 World FFN 与两次残差时读取。
