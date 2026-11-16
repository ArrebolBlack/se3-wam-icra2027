# Fig. 2 素材

- `frame_now.png`、`frame_p050.png`、`frame_p200.png`、`frame_p400.png` 为第 29、30、33、37 帧的 640 px Blender 渲染；2026-11-16 以 specular 0.10 重建，原相机与材质颜色不变。调整底图或裁切时读取。
- `frame_m350.png` 和 `frame_m200.png` 为第 22、25 帧的旧渲染；已核对当前生成脚本和论文均未引用，未重渲染，仅保留作旧版观测历史参考。
- [overlay.json](overlay.json) 保存标定投影后的八步流轨迹（每点 `track` 为 8×2、640 px 图像坐标）、位姿，以及从新渲染帧自动提取的目标轮廓。更新素材时运行 [prepare_assets.py](../prepare_assets.py)；帧号和标签来源见 [source.json](../source.json)。
