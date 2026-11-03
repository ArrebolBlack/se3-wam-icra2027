# Fig1：首页跨栏首图（定稿规格，2026-11-02）

2026-11-02 已按下列规格出图并替换 `\figplaceholder`；中英文共用同一 PDF（图内文字只有英文）。
**含占位**：\ours 的点与 L 均为占位值，结果出来后按下文“占位值”一节重建。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：图体、图注与标签 `fig:teaser`。
- 版面入口：`main.tex` 用 `\twocolumn[{...\maketitle\input{sections/teaser}}]` 把本图放在标题下方；中文审读稿为单栏，置于摘要之后。
- [论文 PDF](fig1.pdf)、[可编辑 SVG](fig1.svg)（文字为可编辑 Arial）、[600 dpi 预览](fig1.png)：6.875 × 2.4 in，两张底图为位图，其余全部矢量。
- [标签导出](extract_labels.py)、[绘图脚本](build_fig1.py)、[绘图数据](data/)、[导出检查](layout_report.json)：重建本图时读取。
- [历史资产](archive/INDEX.md)：旧 storyboard（含生成图像，已弃用）与 2026-11-01 占位。

## 总体

- 位置：第 1 页标题与作者下方，跨双栏。
- 尺寸：宽 6.875 in（`\textwidth`），高约 2.4 in。
- 分栏：(a) 约 60%，(b) 约 40%，栏间 0.15 in。
- 栏标题（加粗，一行）：(a) **Precise where contact demands it**；(b) **Success vs. latency**。
- 配色：只用两种强调色。目标 SE(3) 为珊瑚色（#D85A30），稀疏 3D 流为青绿（#1D9E75）；其余元素为灰色。坐标轴三轴可用红/绿/蓝细线。
- 字体与字号：与正文图一致（Helvetica/Arial，打印后不小于 7 pt）。
- 禁止：生成或修饰的图像；“best”“first”等字样；倍数箭头标注。

## (a) 角色感知的精度分配

- 底图：一帧真实的 ConMoto 智能体视角 RGB 渲染，任务 `t5_replan`（撞击后抓取），选撞击刚发生后的帧；只裁掉无关桌面边缘。
- 目标在采集时刻 τ：实心描边（珊瑚色）。
- 目标在执行时刻 τ+L：同一目标的半透明轮廓，取真实轨迹上 τ+L 的位姿（L 取 \ours 的 p95 时延，按控制周期取整）。
- SE(3) 预测：8 个时域（50–400 ms）的小坐标轴，取自真实训练标签；要画到能看出旋转在变化。
- 稀疏 3D 流：只画 14×14 patch 点。传送带和撞击器上的点画箭头，长度按位移统一缩放；背景点位移接近零，画成小灰点。
- 时间轴：底部细线，三个刻度 capture τ / inference L（虚线区间）/ execution τ+L，与画面中的实线、半透明目标对应。
- 图例：一行两项，“Target SE(3), 8 horizons”与“Sparse 3D flow”。

## (b) 成功率–时延散点

- 数据：横轴为 p95 出动作时间（ms，对数刻度）；纵轴为 \bench 原生时延下的 SR；均取自主表 1，不画误差棒。
- 点：形状区分类别（圆为反应式，三角为 VLA，方块为视频 WAM），统一灰色，只标类别名；\ours 为大号珊瑚色实心点并标方法名。
- 参考线：50 ms 控制周期处一条竖虚线，标 “control period”。

## 数据来源与帧号（2026-11-02 出图）

- 底图：ConMoto native-expert 录制 `v1:test_id:t5_replan:000000~r000000`（seed 0，agentview 224×224），
  文件 `C:/Users/XUE/.codex/visualizations/2026/10/25/01a172e5-a1e5-7ba3-90bd-3b76c482a936/fig4-dynamic14/recordings/t5_replan/recording/episodes/v1%3Atest_id%3At5_replan%3A000000~r000000.hdf5`
  （sha256 见 `data/source.json`；与 Fig. 3 同一 episode）。本机只有这一条带完整 `supervision/` 的 t5_replan 录制；train 分片在远端（`/vepfs-mlp2/.../db0-restore-20260915`）。
- 帧：**τ = 第 29 帧（t = 1.45 s）**，即撞击开始（`striker_impact_onset` 1.438 s）后的第一帧，撞击器仍与目标接触（接触区间 1.438–1.456 s）。
  τ+L = 第 30 帧（1.50 s）。`data/frame_tau_rgb.png` 是 `policy/rgb[29]` 原样无损导出，未做任何处理。
- 标签：直接调用训练适配器 `se3_wam.data.dynamic_benchmark.read_targets(horizon=8, anchor=True, object_reference=True)`
  （SE3-WAM-canonical `b0a72806`），得到 8 个时域（50–400 ms）的目标位姿与 14×14 patch 的 3D 流（机器人基座系）；脚本只把它们投影回同一相机。
  目标偏航（基座系）：τ 2.4°，h1–h8 为 12.6、18.6、21.4、22.0、22.0、22.0、22.0、22.0°。
- τ 实线轮廓 / τ+L 半透明轮廓：第 29 / 30 帧的真实分割（`supervision/geom_id` 中 instance `target`）。
- (b)：`tables/main_results.tex` 的 10 个基线行，全部取原生 SR 与 p95，绘图时直接解析该表；类别按正文第 4 节：
  反应式 ACT、DP；VLA $\pi_{0.5}$、$\pi_{0.5}$+SE(3)、DynamicVLA、PUMA；视频 WAM OpenWAM-α、OpenWAM-α (off)、DynamicWAM、DynamicWAM+SE(3)。

## 复现

```powershell
# 1) 标签快照（需要 SE3-WAM-canonical 环境：h5py、scipy、torch）
C:/workspace/SE3-WAM-canonical/.venv/Scripts/python.exe extract_labels.py --episode <上面的 hdf5> --latency-ms 50
# 2) 出图（仓库 .venv，见根目录 requirements.txt；字体 Arial）
../../.venv/Scripts/python.exe build_fig1.py
```

`extract_labels.py` 默认 `--frame-rule after-onset`（第 29 帧）；`--frame-rule after-end` 取撞击结束后的第一帧（第 30 帧）。

## 占位值

- **L = 50 ms 为占位值**：\ours 的 p95 时延尚未测出。测出后用 `--latency-ms <p95>` 重跑步骤 1（按 50 ms 控制周期向上取整，决定 τ+L 用哪一帧），再跑步骤 2。
- **(b) 的 \ours 点为占位**：`data/ours.json`（`status: placeholder`，p95 45 ms、SR 50%，仅为排版位置），图中标注 “(placeholder)”。
  主表填数后改成实测值、`status` 改为 `final`，标注自动消失。

## 与规格的偏离

- 帧：选撞击开始后的第一帧（第 29 帧，仍在接触），没有选撞击结束后的第一帧（第 30 帧）。第 30 帧时旋转大多已在 τ 与 h1 之间完成，8 个时域内只剩 3.4° 变化，看不出旋转在变；第 29 帧在 8 个时域内变化 9.4°，τ 与 τ+L 之间相差 10°。
- 稀疏 3D 流：真实标签中**传送带与撞击器上没有箭头**。传送带网格在 MuJoCo 中静止（货物靠接触被带动），105 个传送带 patch 的标签全为 0；撞击器太小，没有 patch 中心落在上面。
  非零流只在机械臂/夹爪（13 个 patch，400 ms 位移 46–78 mm）与目标（1 个 patch，44 mm）上，图中照实画出；箭头为 400 ms 位移的真实投影（比例 1:1），< 10 mm 画成灰点。
- (a) 版面：在整帧右侧加了同一帧的放大视图（白框示位）。8 个时域的原点在 224 px 图上只隔约 1.3 px，不放大看不出位姿与旋转。放大视图用双线性显示插值，没有其他图像处理。
- 坐标轴配色：x 轴用珊瑚色、y 轴深灰、z 轴浅灰，未用红/绿/蓝。目标是红色、传送带是绿色，红/绿轴会看不见。轴长为图示长度（x 28 mm、y 12 mm、z 8 mm），原点与朝向来自标签；颜色深浅从 50 ms 到 400 ms 渐淡。
- 图例与时间轴放在 (a) 底部两行（时间轴在上，图例在下）；(b) 的类别图例放在左下空白处，只写类别名。
- 底图分辨率为策略输入的 224 px，印刷时约 115 ppi（整帧）。

## 刻意不放的内容及理由

- 微型架构图：与 Fig. 2 重复，且会与 Trace-WAM 首图形式相近。
- 多帧缩略图墙：小图打印后看不清精度差异。
- 雷达图：数值难读，不对应“又准又快”的主张。
- 真机照片：正文 Fig. 6 已有。
