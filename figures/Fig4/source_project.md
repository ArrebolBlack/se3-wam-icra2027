# Fig. 3：十四任务总览制作工程

正文图号为 Fig. 3，沿用 `Fig4/` 项目目录和 `fig:bench_overview` 标签。
`dynamic14.pdf` 用于论文，`dynamic14.svg` 保留所有文字、轨迹、箭头和引线的可编辑矢量对象；
`dynamic14.png` 是 600 dpi 预览。版面仍为 6.875 × 2.0 in、两行七列、统一 800 × 510 裁剪尺度。

## 原始记录与当前工程

原始十四个 native-expert episode、状态、模型和导入工具保存在：

```text
C:/Users/XUE/.codex/visualizations/2026/10/25/01a172e5-a1e5-7ba3-90bd-3b76c482a936/fig4-dynamic14/
```

2026-11-02 精修的原生 Blender 场景、重放帧、遮罩及预览在：

```text
C:/Users/XUE/.codex/visualizations/2026/11/02/01a19d42-d9c6-7e33-be04-5e2984704c79/fig3-refined/
```

- `assets/<task>/panel.json`：选帧、真实时间、几何投影、当前/历史可见性；同目录保留原生重放 RGB、深度与分割。
- `panels/<task>/scene.blend`：当前与历史独立渲染层、灯光、相机及合成节点；遮罩已打包。
- `panels/<task>/validation.json`：保存后重开的几何坐标、旋转、尺度误差。
- `sources.json`：论文侧的精简来源记录；其中帧路径相对于当前工程。

## 精修依据

保持原来的 episode、seed、当前时刻、相机、几何和物理参数。只调整历史采样与展示：
谐波运动取一个较远历史姿态，其余取两个；旋转导线改为最近 10–20 s 内的 10、15、20 s。
其余双历史面板按相同时间间隔取样，任务之间的时间尺度不同，不能用跨面板间距比较速度。
滚动/滑动任务的实际位移随时间增加，仍保持记录中的加速、离开斜坡和下落过程。
当前帧均沿用原稿；这些示例不是 FoveaWAM 成功证据，也不是预测轨迹。

历史几何分别在不含其他实体的渲染层中绘制，再通过原生历史可见性、当前前景深度和当前目标排除遮罩合成。
每个姿态仅施加一次透明度（较早 0.32、较近 0.52；单历史 0.52），避免复杂网格内部多次透射产生深色假边。
不手工移动姿态、不插值、不沿屏幕等距摆放；当前场景保持原有渲染材质与光照。
除细导线外，历史可见轮廓另用 0.25 pt 低对比度矢量线描边；轮廓直接来自原生分割与遮挡遮罩，避免灰底上的历史姿态消失。

箭头为 0.45–0.48 pt 深蓝矢量线，定性角落符号为 0.44 pt 灰线；
任务名 7 pt，组名 7.5 pt，局部标注 6.5 pt。
两个 `entry` 均向右上移动，并用小幅白色底衬隔离场景纹理；`avoid` 和 `tray` 使用同一标注样式。
配色和层级与当前方法图的克制色彩相协调，参考 SAM 2 时序图的历史淡化和线条层级，不借用其科学内容。

## 重建

从本目录运行，`$sourceProject` 与 `$outputProject` 分别指向上面两个工程：

```powershell
& "$sourceProject/.venv/Scripts/python.exe" prepare_motion.py --source-project $sourceProject --output $outputProject
& "$sourceProject/blender/.venv/Scripts/python.exe" render_panels.py --source-project $sourceProject --output $outputProject --tasks grasp t1_belt t1_xyz t1_so3 t1_occ t2_trans t2_se3 t3_phase t3_full t4_sphere t4_sphere_tabletop t4_slider t4_can t5_replan --samples 96 --device OPTIX
& "$sourceProject/.venv/Scripts/python.exe" build_figure.py --source-project $sourceProject --output $outputProject
```

准备步骤仅对保存状态做 MuJoCo 前向重放，不运行新的物理轨迹。
渲染步骤复用原始工程的 `render_blender.py` 和 `timeline.py`；
排版步骤复用原始工程的 PDF/SVG 基元。修改源文件并重建后，再将成图和来源记录复制到本目录。

2026-11-02 检查：十四个原生场景保存后重开，最大位置误差 6.87×10⁻⁸ m，旋转矩阵比较误差为 0；
PDF 为 495 × 144 pt，14 个场景位图配合嵌入 Arial 字体和矢量标注，PNG 为 4125 × 1200 px。
已检查整体、逐面板、灰度、论文尺寸和中英文正文嵌入效果；四份论文 PDF 编译成功，最终日志无未定义引用或 LaTeX 错误。
