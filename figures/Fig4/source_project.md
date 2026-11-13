# Fig. 4：OnTimeBench 总览制作工程

## 机制对比

子图 (a) 两栏使用同一个 OnTimeBench 场景、相机和裁剪。左栏显示观测时刻（0.4 s），用于示意 DOMINO 的 PUMA 评测协议。
右栏保持原有控制目标推进四个 50 ms 周期（至 0.6 s），球心在三维空间移动 18.04 cm，图中标作 18 cm。虚线圆圈标出观测时的球心投影。
[场景记录](protocol_example.json) · [DOMINO 的 PUMA 评测器](https://github.com/H-EmbodVis/DOMINO/blob/main/policy/PUMA/examples/Robotwin/eval_files/model2robotwin_interface.py#L483-L503)

## 十四项任务的面板来源

子图 (c) 复用内嵌的场景图和矢量运动标记。标记在新图中加粗，保留原始投影路径及箭头端点。
[场景与标记的 SVG 源文件](dynamic14.svg) · [旧版两行七列成图](archive/dynamic14/INDEX.md)

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
- [sources.json](sources.json)：任务、episode、seed、相机及帧时间；其中帧路径相对于 Blender 工程。

## 精修依据

保持原来的 episode、seed、当前时刻、相机、几何和物理参数。只调整历史采样与展示：
谐波运动取一个较远历史姿态，其余取两个；旋转导线改为最近 10–20 s 内的 10、15、20 s。
其余双历史面板按相同时间间隔取样，任务之间的时间尺度不同，不能用跨面板间距比较速度。
碰撞面板取 0.80、1.45、2.10 s，依次展示接触前、记录到接触时和接触后；
1.45 s 位于真实接触区间 [1.438, 1.456] s 内。历史姿态与事件定位点使用同一个记录样本。
滚动/滑动任务的实际位移随时间增加，仍保持记录中的加速、离开斜坡和下落过程。
当前帧均沿用原稿；这些示例不是 FoveaWAM 成功证据，也不是预测轨迹。

历史几何分别在不含其他实体的渲染层中绘制，再通过原生历史可见性、当前前景深度和当前目标排除遮罩合成。
每个姿态仅施加一次透明度（较早 0.32、较近 0.52；单历史 0.52），避免复杂网格内部多次透射产生深色假边。
不手工移动姿态、不插值、不沿屏幕等距摆放；当前场景保持原有渲染材质与光照。
除细导线外，历史可见轮廓另用 0.25 pt 低对比度矢量线描边；轮廓直接来自原生分割与遮挡遮罩，避免灰底上的历史姿态消失。

实测平移轨迹为 0.45–0.48 pt 深蓝矢量线和箭头，始终保留原始投影坐标及遮挡关系。
0.46 pt 灰色方向符号只用于不能由中心轨迹表达的旋转/振荡：谐振双向箭头在目标右侧，
旋转弧线分别位于抓取物体下方、容器右下和导线末段下方，不再使用悬空角标。
灰色符号的长度、弧长及位置为排版示意，方向来自真实运动轴，不表示实测位移。
谐振的 0.25 s 历史帧已接近当前时间窗内最大的投影分离；平移抓取已从 0 s 起采样。
目标轮廓遮住部分真实中心轨迹时，仅保留可见的轨迹段，不移动轨迹或物体来制造间距。
碰撞面板额外使用 0.55 pt 橙色箭头表示上方滑块的记录运动，箭头终点是接触样本中滑块与目标碰撞点的平均位置。
`impact` 文字和细引线定位该接触位置。
任务名 7 pt，组名 7.5 pt，局部标注 6.5 pt。
两个 `entry` 均向右上移动；`entry`、`avoid`、`tray` 和 `impact` 使用深灰文字直接标注于平缓背景，
不加矩形底衬，以保留原图内容。引线从文字外缘引出；线条仅保留较窄、较淡的浅色描边。
配色和层级与当前方法图的克制色彩相协调，参考 SAM 2 时序图的历史淡化和线条层级，不借用其科学内容。

## 重建任务面板

从本目录运行，`$sourceProject` 与 `$outputProject` 分别指向上面两个工程：

```powershell
& "$sourceProject/.venv/Scripts/python.exe" prepare_motion.py --source-project $sourceProject --output $outputProject
& "$sourceProject/blender/.venv/Scripts/python.exe" render_panels.py --source-project $sourceProject --output $outputProject --tasks grasp t1_belt t1_xyz t1_so3 t1_occ t2_trans t2_se3 t3_phase t3_full t4_sphere t4_sphere_tabletop t4_slider t4_can t5_replan --samples 96 --device OPTIX
& "$sourceProject/.venv/Scripts/python.exe" build_figure.py --source-project $sourceProject --output $outputProject
```

准备步骤仅对保存状态做 MuJoCo 前向重放，不运行新的物理轨迹。
渲染步骤复用原始工程的 `render_blender.py` 和 `timeline.py`；
排版步骤复用原始工程的 PDF/SVG 基元。修改源文件并重建后，再将成图和来源记录复制到本目录。

2026-11-02 旧版检查：十四个面板的 41 个所选位姿逐一与原始记录一致；
十四个原生场景保存后重开，最大位置误差 6.87×10⁻⁸ m，旋转矩阵比较误差为 0；
PDF 为 495 × 144 pt，14 个场景位图配合嵌入 Arial 字体和矢量标注，PNG 为 4125 × 1200 px。
已检查整体、逐面板、灰度、论文尺寸和中英文正文嵌入效果；四份论文 PDF 编译成功，最终日志无未定义引用或 LaTeX 错误。
旧版整体预览为制作工程下的 `preview.png`；精修前后的局部对比为 `review/local-comparison-v2.png`，
左列为修改前，右列为修改后，依次为 Translating grasp、Rotating grasp、Post-impact grasp。
