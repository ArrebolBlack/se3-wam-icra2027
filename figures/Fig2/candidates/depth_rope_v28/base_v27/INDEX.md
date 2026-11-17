# Depth/RoPE 候选的 v27 原始输入

本目录保存提交 `3e53af3` 中的 Fig. 3 原始输入，供相邻 v28–v30 候选复现。
这些候选制作后，正式图已更新机械臂和噪声素材；候选比较应继续使用制作时的输入。

- `fig2_se3wam.pptx`、`fig2_se3wam.pdf`：当时的母版和导出，作为前后对比基准。
- `update_assets.py`：候选脚本导入其中的 DrawingML 绘图函数；不在此目录独立运行素材更新。
- `build_fig2.py`：当时的 PowerPoint 导出入口，由候选脚本指定输出目录后调用。

实录点云、深度、标定仍读取主仓原有资产；核对时这些数据与 `3e53af3` 一致。
依次运行上一级 `make_preview.py`、`../../depth_rope_simple_v29/make_preview.py`、
`../../depth_rope_minimal_v30/make_preview.py` 可重建候选。正式图继续以 `figures/Fig2/` 的母版为准。
