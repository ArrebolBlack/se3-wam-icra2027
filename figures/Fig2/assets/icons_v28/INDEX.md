# Fig. 3 v28 图标素材

作者已选定（2026-11-16）：线框机械臂 + 经典高斯噪声（对比稿中的 A 版）。

- `robot_arm_p1.svg` / `robot_arm_p2.svg` / `robot_arm_p3.svg`：原创线框机械臂，三个姿态，共用 viewBox（底座位置一致）。p1 → p3 夹爪逐步前伸下探。Action chunk 依次用 p1、p2、p3；Robot state 与 (c) 推理输出用 p2。
- `noisy_actions_A.png`、`inference_noise.png`：32 × 32 高斯噪声（灰度 15–240），最近邻放大到 640 px，无格线、无边框；边框在 PowerPoint 中另画。
- `noise_grids_v28.json`：两块噪声的灰度原始值。
- `make_icons_v28.py`：以上素材的生成脚本（颜色：描边 #4A4F55，连杆 #F3F4F6，底座与关节 #DADDE1，夹爪 #E3E6E9）。
- `preview_robot_arm_p*.png`：仅供查看。
