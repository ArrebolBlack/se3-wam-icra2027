# Fig.1 数据与布局数值

- [source.json](source.json)：当前几何标签的录制、相机与帧号；追溯监督来源时读取。其中 latency 字段属于旧标签导出配置，不是当前 c 图的延迟。
- [labels.npz](labels.npz)、[当前 RGB](frame_tau_rgb.png)、[当前深度](frame_tau_depth_m.npy)：第29帧的标定、目标位姿、14×14流标签与 RGB-D；重建点云时读取。
- [基座变换](base_from_world.npy)：同一录制的世界系到机器人基座系变换；将流标签与世界系点云对齐时读取。
- [参考帧](reference_frames/INDEX.md)：a 图的观察与未来帧栈；更新真实参考图像时读取。
- [当前 Paused 占位](ours_paused.json)：83% Paused SR、28 ms 原生 p95，明确标为 placeholder；修改当前 c 图的临时点时读取。其余点直接解析主表，主表的 Ours 不填占位数。
- [旧 native 占位](ours.json)：早期概念稿使用的45 ms／50% native布局点；仅回看旧概念时读取，不用于当前论文图。
