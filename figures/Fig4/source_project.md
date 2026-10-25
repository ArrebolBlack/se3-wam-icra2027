# Fig. 4 制作工程与来源

`dynamic14.pdf` 和 `dynamic14.svg` 直接复制自已验收的 `fig4_refined` 导出，未二次裁切或缩放。
正文使用 PDF，SVG 保留可编辑任务名、分组与排版；场景内的历史位姿和轨迹保留为原生 Blender 对象。

本机完整工程：

```text
C:/Users/XUE/.codex/visualizations/2026/10/25/01a172e5-a1e5-7ba3-90bd-3b76c482a936/fig4-dynamic14/
```

- `blender/INDEX.md`：完整交付与重建命令。
- `blender/panels/<task>/scene.blend`：十四个可编辑场景，贴图与历史可见性遮罩已打包。
- `blender/scripts/render_panels.py`、`build_blender_figure.py`：真实状态渲染、运动叠加及排版。
- `assets/`、`recordings/`：原始帧、分割、深度、episode、种子、模型与轨迹状态。
- `blender/visual_review.md`、`blender/reviews/round3_stageB_review.md`：独立盲评与科学核对；当前图配合图注通过第三轮 Blender 验收。

本目录的 `sources.json` 保留每个面板的来源时间和路径：`frame_file` 相对于上述工程根目录，
`blender_scene`、`raw_render`、`annotated_render` 和 `validation` 相对于其 `blender/` 子目录。
这些是固定原生专家 episode 的任务示例，不是 SE(3)-WAM 策略成功证据。
历史位姿来自同一真实轨迹；遮挡保持真实；无生成式场景、未来预测或物理参数修改。
印刷可读性按数字样张验收，未做实体打印。详细记录在制作工程中维护，不在论文仓重复复制。
