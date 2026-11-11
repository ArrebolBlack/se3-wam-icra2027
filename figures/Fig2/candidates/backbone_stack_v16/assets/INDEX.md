# v16 素材

沿用正式 v15 的几何与输入素材，保留副本以独立重建。

- [RGB](rgb.png)、[Depth](depth.png)：Blender 入口与原始深度缩略图；核对输入时读取。
- [几何标签](geometry_labels.npz)、[来源](source.json)：历史 SE(3) 与未来参考监督；核对几何示例时读取。
- [机器人图标](robot_arm.svg)：原创透明矢量；调整状态与动作图标时读取。
- [旧紧凑单层](backbone_v2.svg)、[旧布局](backbone_v2_layout.json)：保留连接关系的设计参考；追溯原单层时读取。新层组由本候选的 `build_fig2.py` 直接生成。
