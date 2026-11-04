# Fig.1：真实输入与几何展示（2026-11-04）

[论文 PDF](fig1.pdf) · [可编辑 SVG](fig1.svg) · [预览](fig1.png) · [英文图注](figure.tex) · [中文图注](figure_zh.tex)

当前论文采用选定的三栏设计：b 上使用 Blender 环境示意与 Fig.2 彩色点云，保留黑箱和精修后的箭头／文字；b 下保留 E 版灰色点云近景；c 保留线性0–200 ms坐标，数值直接读取当前 Table 1。中英文共用英文图体。

- a：原始录制的多帧观察与未来帧栈、Video WAM 黑箱和动作出口；参考帧说明表示形式，不是基线预测。
- b 上：[独立可编辑组件](b_upper.svg)包含 Blender RGB 示意、数值深度、Pose history、FoveaWAM 黑箱和彩色几何缩略图。单条训练虚线连接联合几何输出，TRAIN ONLY 位于点云上方；Action chunk 单独用实线连接。
- b 下：当前 RGB-D 的灰色点云、源锚点与青绿流箭头，橙红当前目标表面与位姿轨迹；独立展示+50／+200／+400 ms的SE(3)字形。保持E版取景与点径。
- c：使用[主表](../../tables/main_results.tex)的 Paused SR 与原生部署 p95，直接标方法名；省略 OpenWAM-α (off)。斜箭头从 OpenWAM-α 指向 FoveaWAM，50 ms竖线为参考。

## 数值与素材

FoveaWAM 当前点采用主表报告的 **83.0%／15.1 ms**，相对 OpenWAM-α 的151.7 ms约快 **10.0×**。83.0%沿用主表作者选定的先前同步参考结果，图内及图注保留†说明；BF16共享执行器Paused实测82.0%，来源见[接收结果](../../results/realtime_c/INDEX.md)。Fig.1c直接读取Table 1的Paused与p95单元格，并从接收JSON读取同步参考来源。

计时口径沿用主表：FoveaWAM为单RGB-D视角及仿真目标位姿，PUMA使用官方三相机预算，其他基线使用双相机计时输入。

[数据入口](data/INDEX.md)路由帧、标定与监督；[b 上来源](data/b_upper_source.json)记录渲染与彩色云点来源。Blender RGB是录制状态的展示渲染，不是策略输入观测，也不宣称与旁边的深度逐像素配准。数值深度和点云来自 t5_replan 第29帧（1.45 s）的录制观测，未来几何为真实监督，非模型预测；长方体为位姿字形。

b 上复用 Fig.2 的3700个RGB彩色点，显示工作区内120个有效可见锚点和12个非零+400 ms流。b 下从同帧RGB-D反投影，使用目标周围XY半径0.62 m、world z 0.58–1.2 m的近景裁切，显示8378个云点、123个有效可见锚点和12个非零流。非零数值容差为1e-6 m，流在三维中统一放大3倍后投影；目标轨迹不放大。

当前非零流主要属于机械臂和目标，不能作为非目标环境运动的完整示例。后续精修动态背景时应选取环境运动清楚可见的录制。

## 重建

在本目录运行：

```powershell
../../.venv/Scripts/python.exe build_fig1.py
node render_fig1.mjs
```

[绘图入口](build_fig1.py)读取 b 上组件，并从数据重绘 a／b 下、从主表重绘 c；[c 绘图](draw_latency.py)不读取手填 Ours 配置；[导出入口](render_fig1.mjs)生成矢量PDF、PNG与[布局数据](layout_report.json)。标称尺寸6.875×2.371 in；点云、位姿、箭头、图表与文字保持矢量，只有六张参考帧、Blender环境示意与深度显示为位图。

[历史资产](archive/INDEX.md)用于回看旧稿；[旧概念 v5.2](concepts/v5_2/fig1_concept_v52.pdf)保留为独立概念，不接入论文。
