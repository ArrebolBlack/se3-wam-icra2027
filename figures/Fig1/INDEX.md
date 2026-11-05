# Fig.1：彩色真机场景与 Native 性能（2026-11-04）

[论文 PDF](fig1.pdf) · [可编辑 SVG](fig1.svg) · [预览](fig1.png) · [英文图注](figure.tex) · [中文图注](figure_zh.tex)

当前两块布局：左侧为用户选定的完整彩色真机场景、目标 SE(3) 与稀疏流标注；右侧为最新主表的 Native SR—原生 p95 图。右图以 TinyVLA Fig.1 为主参考，保留原版单一斜向比较与红橙／中性色层级，精修标签和数学下标；中英文共用英文图体。

- [组合入口](build_fig1.py)：等比例放大并排布选定场景，组合右侧性能图；修改整体布局时读取。
- [性能绘图](draw_latency.py)：直接从[主表](../../tables/main_results.tex)读取 Native SR／p95；修改右图时读取。线性 0–200 ms，沿用用户选择省略 OpenWAM-α off。
- [独立右图 PDF](native_tradeoff.pdf) · [SVG](native_tradeoff.svg) · [预览](native_tradeoff.png)：3.25 in 宽，单独审阅或复用右图时读取。
- [VLA／WAM 二维性能图参考](references/INDEX.md)：TinyVLA 主参考及 4 篇同领域图、来源与裁图复现入口；评审本次视觉优化时读取。
- [布局数据](layout_report.json)：两块图位置、主表数值与速度比；核对图表时读取。
- [数据入口](data/INDEX.md)：当前真机素材与历史仿真数据；更换示例时读取。当前几何由 MoGe-2 估计，未来运动为示意，具体性质见图注。
- [历史资产](archive/INDEX.md)：旧三栏图及组件；回看先前设计时读取。

## 重建

在本目录运行：

```powershell
../../.venv/Scripts/python.exe build_fig1.py
node render_fig1.mjs
```

[导出入口](render_fig1.mjs)产生完整图与独立右图的 PDF、PNG。标注与图表为矢量，彩色点云为嵌入位图；左图细修从数据入口的 `real_scene/scene.svg` 进行。

[旧概念 v5.2](concepts/v5_2/fig1_concept_v52.pdf)保留为独立概念，不接入论文。
