# Fig. 2 素材

- `frame_now.png`、`frame_p050.png`、`frame_p200.png`、`frame_p400.png` 为第 29、30、33、37 帧的 640 px Blender 渲染。调整底图或裁切时读取。
- `frame_m350.png` 和 `frame_m200.png` 为第 22、25 帧的 640 px Blender 渲染，用于面板 (b) 的观测历史。
- [overlay.json](overlay.json) 保存标定投影后的流和位姿，以及从渲染帧自动提取的目标轮廓。更新素材时运行 [prepare_assets.py](../prepare_assets.py)；帧号和标签来源见 [source.json](../source.json)。
