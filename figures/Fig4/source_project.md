# Fig. 4：OnTimeBench 总览制作工程

## 机制对比

子图 (a) 两栏使用同一个 OnTimeBench 场景、相机和裁剪。左栏显示观测时刻（0.4 s），用于示意 DOMINO 的 PUMA 评测协议。
右栏保持原有控制目标推进四个 50 ms 周期（至 0.6 s），球心在三维空间移动 18.04 cm，图中标作 18 cm。虚线圆圈标出观测时的球心投影。
[场景记录](protocol_example.json) · [DOMINO 的 PUMA 评测器](https://github.com/H-EmbodVis/DOMINO/blob/main/policy/PUMA/examples/Robotwin/eval_files/model2robotwin_interface.py#L483-L503)

## 十四项任务的面板来源

子图 (c) 保留现有矢量运动标记及其原始投影路径、箭头端点；内嵌场景图由原始回放重渲染。
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
不手工移动姿态、不插值、不沿屏幕等距摆放；光照保持原值，当前材质见下节。
除细导线外，历史可见轮廓另用 0.25 pt 低对比度矢量线描边；轮廓直接来自原生分割与遮挡遮罩，避免灰底上的历史姿态消失。

实测平移轨迹为 0.45–0.48 pt 深蓝矢量线和箭头，始终保留原始投影坐标及遮挡关系。
0.46 pt 蓝色方向符号只用于不能由中心轨迹表达的旋转/振荡：谐振双向箭头在目标右侧，
旋转弧线分别位于抓取物体下方、容器右下和导线末段下方，不再使用悬空角标。
方向符号的长度、弧长及位置为排版示意，方向来自真实运动轴，不表示实测位移。
谐振的 0.25 s 历史帧已接近当前时间窗内最大的投影分离；平移抓取已从 0 s 起采样。
目标轮廓遮住部分真实中心轨迹时，仅保留可见的轨迹段，不移动轨迹或物体来制造间距。
碰撞面板额外使用 0.55 pt 黑色箭头表示上方滑块的记录运动，箭头终点是接触样本中滑块与目标碰撞点的平均位置。
`impact` 文字和细引线定位该接触位置。
任务名 7 pt，组名 7.5 pt，局部标注 6.5 pt。
两个 `entry` 均向右上移动；`entry`、`avoid`、`tray` 和 `impact` 使用深灰文字直接标注于平缓背景，
不加矩形底衬，以保留原图内容。引线从文字外缘引出；线条仅保留较窄、较淡的浅色描边。
配色和层级与当前方法图的克制色彩相协调，参考 SAM 2 时序图的历史淡化和线条层级，不借用其科学内容。

## 当前材质与渲染参数（2026-11-16）

默认参数唯一来源为研究仓 `scripts/benchmark_infra/mujoco_blender/studio_controls.py` 的 `DEFAULTS`。
调色台 `/api/state` 与研究仓 `render_blender.py` 共用该来源；本图的 [render_panels.py](render_panels.py)
通过 `--research-root` 导入同一渲染器，不再使用历史工程里的副本。

用户在 agentview 第 30 帧比较 0.50 / 0.15 / 0.10 后选定全局 specular **0.10**，
以减少传送带近处的反光泛白。所有 Principled BSDF 材质均应用该值，包括桌面、机械臂和历史姿态材质。
AgX Medium High Contrast、曝光 0、Gamma 1、饱和度 1、普通及传送带粗糙度 0.34 均保持原值；
历史姿态的粗糙度仍为 0.9。环境强度 0.15，主光 220 W / 1.5 m、补光 80 W / 2 m、
轮廓光 160 W / 1.5 m，灯光位置和方向不变。Cycles / OPTIX，1024 × 1024，96 samples，seed 42。

工作台配色在 Blender 材质中设置，色值按 sRGB 转成 scene-linear Base Color：

| 材质 | 场景 | sRGB | scene-linear RGB |
| --- | --- | --- | --- |
| `db0_buzz_fixture_base_visual` | t3_phase、t3_full | `#2E2E2E` | (0.027321, 0.027321, 0.027321) |
| `ramp_visual` | 四个 Capture 任务及两个协议面板 | `#2E2E2E` | (0.027321, 0.027321, 0.027321) |
| `ramp_support_0_visual` 至 `ramp_support_3_visual` | 对应 Capture 支架（按场景实际数量） | `#6B6B6B` | (0.147027, 0.147027, 0.147027) |

深灰取 Pass 原台面中间通道约 0.18 并中性化，支架保留原亮度约 0.42 并去蓝。
背景大底桌 `table_visual`、机械臂原色、传送带原版绿色和纹理不变；不进行像素级桌面处理或传送带降饱和。
矢量部分沿用 2026-11-16 定稿 SVG，与 `tmp/palette_20261116/recolor_fig4.py` 的 MAP 配色一致。

## 重建全部场景及成图

当前原生场景、渲染与核验资产位于论文仓 `build/fig4-blender-20261116/`，不进入 Git。
其中 `panels/<task>/scene.blend` 是 14 个任务的原生场景，`protocol/<paused|advancing>/scene.blend`
是两个协议面板；各自包含 `history.png` 与保存后重开的 `validation.json`。

两个协议面板必须使用当时的专用控制保持回放，不能替换为持续执行 oracle 的原始任务轨迹：

```text
C:/workspace/se3-wam-icra2027/tmp/fig4_redesign/concept_a3/capture/
```

该回放包含 0.40–0.60 s 的五个真实样本；使用第 0、4 帧。
当前裁剪为 `[211, 300, 428, 372]`（x、y、宽、高），已更新 [protocol_example.json](protocol_example.json)
里遗留的早期横向裁剪记录，以匹配当前 SVG 内嵌图像；不改变画面或矢量位置。

从本目录运行：

```powershell
$sourceProject = 'C:/Users/XUE/.codex/visualizations/2026/10/25/01a172e5-a1e5-7ba3-90bd-3b76c482a936/fig4-dynamic14'
$researchRoot = 'C:/workspace/se3-wam-research'
$protocolSource = 'C:/workspace/se3-wam-icra2027/tmp/fig4_redesign/concept_a3/capture'
$outputProject = 'C:/workspace/se3-wam-icra2027/build/fig4-blender-20261116'
& "$sourceProject/.venv/Scripts/python.exe" prepare_motion.py --source-project $sourceProject --output $outputProject
& "$researchRoot/.envs/blender-paper/mujoco-blender-render/Scripts/python.exe" render_panels.py --source-project $sourceProject --research-root $researchRoot --protocol-source $protocolSource --output $outputProject --tasks grasp t1_belt t1_xyz t1_so3 t1_occ t2_trans t2_se3 t3_phase t3_full t4_sphere t4_sphere_tabletop t4_slider t4_can t5_replan --protocol --samples 96 --device OPTIX
python build_figure.py --output $outputProject
```

准备步骤仅对保存状态做 MuJoCo 前向重放，不运行新的物理轨迹。
[build_figure.py](build_figure.py) 以当前 `ontimebench.svg` 为版式与矢量源，只替换 16 个内嵌 PNG；
可用 `--template` 指定另一份同结构 SVG。图片 payload 以外内容逐字节校验不变。
导出复用 `scripts/common.py` 的 Chrome、图片内嵌与 PDF 元数据工具，在 Windows 上使用 Arial。
最终 PDF 为 495 × 236 pt，PNG 为 4125 × 1967 px（600 dpi）。

2026-11-16 重渲染核验：16 个 Blender 场景保存后重开，1696 个材质均为 specular 0.10；
最大位置误差 6.87×10⁻⁸ m、旋转矩阵误差 0，几何、样本时间、相机及任务面板裁剪保持不变。
已检查无传送带的 t4_slider、全部任务与协议面板；旧版像素级过渡成图见
[归档索引](archive/palette_transition_20261116/INDEX.md)。
