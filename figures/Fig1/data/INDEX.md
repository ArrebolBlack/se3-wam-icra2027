# Fig.1 数据与布局数值

- [当前真机场景](real_scene/INDEX.md)：选定彩色图体、输入 RGB、MoGe 估计深度与示意运动参数；修改当前左图时读取。
- [历史仿真来源](source.json)：旧几何标签的录制、相机与帧号；追溯监督来源时读取。其中 latency 字段不是当前性能图的延迟。
- [历史仿真标签](labels.npz)、[RGB](frame_tau_rgb.png)、[深度](frame_tau_depth_m.npy)：第29帧的标定、目标位姿、14×14流标签与 RGB-D；回看旧仿真可视化时读取。
- [历史基座变换](base_from_world.npy)：同一仿真录制的世界系到机器人基座系变换；回看旧流标签与点云对齐时读取。
- [参考帧](reference_frames/INDEX.md)：旧三栏稿的观察与未来帧栈；回看历史素材时读取。
- [旧 b 上组件与来源](../archive/three_panel_real_inputs_20261104/INDEX.md)：Blender输入与彩色小点云流程的历史记录。
- [主表](../../../tables/main_results.tex)直接拥有右图各方法的 Native SR／p95；当前图不读取手填 Ours 点。旧28 ms占位保留在[历史稿](../archive/three_panel_text_inputs_20261103/INDEX.md)。
- [旧 native 占位](ours.json)：早期概念稿使用的45 ms／50% native布局点；仅回看旧概念时读取，不用于当前论文图。
