# Fig.2 仿真画面与几何标签

- [来源](sources.json)：同 Fig.4 的传送带 episode、采样时刻、开发机执行位置与时间偏移；核对或替换素材时读取。
- [标签包](labels.npz)：深度、相机、完整点云、196×8 流及可见性、八个历史/未来目标位姿、专家 EEF 和动作记录；重建叠加或供 Fig.1/3 复用。
- [验证结果](validation.json)：与原始相邻帧流、可见性、位姿和 EEF 记录的独立比较。
- [Blender RGB](rgb_blender.png)、[原始 RGB](rgb_native.png)、[深度显示](depth.png)：同一采样时刻的画面与度量深度显示；原始度量值由标签包拥有。
- [点云底图](pointcloud.png)：由绘图脚本重建的稠密显示底图，叠加的稀疏流保留在 SVG 中。
- [稀疏流矢量面板](flow_gt.svg)、[目标 SE(3) 矢量面板](target_se3_gt.svg)：从 Fig.2 同一场景导出的独立素材；Fig.1/3 复用时读取。

重建与科学范围见 [Fig.2 工程说明](../README.txt)；真实轨迹 HDF5 和 Blender 原生场景由 Fig.4 原始工程拥有。
