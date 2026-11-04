# Fig.1：选定三栏底稿（2026-11-03）

[论文 PDF](fig1.pdf) · [可编辑 SVG](fig1.svg) · [预览](fig1.png) · [英文图注](figure.tex) · [中文图注](figure_zh.tex)

本图已接入论文，作为下一轮精修的底稿。b 下选择七版比较中的 **E：灰色点云近景**，恢复较大的机械臂与桌面轮廓；b 上为黑箱，c 为已选定的线性 0–200 ms 版本。中英文共用英文图体。

- a：原始录制的多帧观察与未来帧栈，Video WAM 黑箱和动作出口；参考帧说明表示形式，不是基线模型预测。
- b 上：RGB-D、Pose history → FoveaWAM；训练专用虚线输出 Target SE(3)、Sparse 3D flow，实线输出 Action chunk。
- b 下：当前 RGB-D 的灰色点云、灰色源锚点与青绿运动箭头；橙红色当前目标表面和位姿轨迹，独立展示 +50／+200／+400 ms 的 SE(3) 字形。保留 E 的取景与点径，不采用全视野透视版。箭头显示放大倍数只写在 caption。
- c：纵轴使用 Table 1 **Paused** 列，横轴为各方法原生部署 p95；直接标方法名。省略 OpenWAM-α (off)，保留 OpenWAM-α 默认缓存／编译配置。斜箭头由 OpenWAM-α 指向 FoveaWAM，标 ≈5.4× faster；50 ms 竖线作为参考。

## 数值与几何来源

[数据入口](data/INDEX.md)拥有帧与布局配置的路由；[主表](../../tables/main_results.tex)拥有各 baseline 的 SR 和 p95。

**83% Paused SR、28 ms 和据此计算的约5.4×加速均为用户批准的排版占位。** 当前主表的 Ours 仍为待测，不把该点写成实验结果。83% 对应推理期间暂停物理的评测，不是原生时延下的成功率。速度比使用 OpenWAM-α 的151.7 ms除以28 ms。各 baseline 计时口径见主表；PUMA 含官方三相机预算，其他基线使用双相机计时输入。

点云来自 t5_replan 第29帧（1.45 s）的当前 RGB-D，按相机标定反投影，再以原近景等轴视角展示。裁切范围为目标周围 XY 半径0.62 m、world z 0.58–1.2 m。显示原14×14网格中落在裁切内、+400 ms标签有效且可见的锚点；非零流阈值为数值容差1e-6 m，不按美观抽稀。位移在三维中统一放大3倍后投影；目标轨迹没有放大。

红色当前表面点由目标 mask 着色，未来位置与旋转来自真实标签；长方体为位姿字形，不表示目标真实外形。几何面板展示监督示例，不是模型预测。

当前可见非零流主要属于机械臂和目标，不能作为非目标环境运动的完整示例。后续按静态背景、动态背景和目标分别精修；选择动态背景示例时应让非目标环境运动清楚可见。

## 重建

```powershell
../../.venv/Scripts/python.exe build_fig1.py
node render_fig1.mjs
```

[绘图入口](build_fig1.py)产生可编辑 SVG 与[布局数据](layout_report.json)；[c 绘图](draw_latency.py)直接解析主表 Paused SR／p95 与当前占位配置；[导出入口](render_fig1.mjs)产生矢量 PDF 和预览 PNG。PDF 为6.875×2.371 in，点云、坐标轴、位姿、箭头和文字均保持矢量；只有六张参考帧为位图。

[历史资产](archive/INDEX.md)用于回看已替换设计。
[旧重设计概念 v5.2](concepts/v5_2/fig1_concept_v52.pdf)（[SVG](concepts/v5_2/fig1_concept_v52.svg)、[脚本](concepts/v5_2/build_concept.py)）保留为独立概念，不接入论文；其示意场景、配色与 native 占位不代表当前选定稿。
