# Fig. 1 真机场景与 Native 性能

[合成预览 PDF](fig1.pdf) · [SVG](fig1.svg) · [PNG](fig1.png) · [论文组版](panels.tex) · [英文图注](figure.tex) · [中文图注](figure_zh.tex)

左侧为淡化远景的真机 RGB 照片，叠加玫红目标 SE(3) 和蓝色稀疏流。右侧为主表的 Native SR 与原生 p95 散点图，玫红突出 FoveaWAM，基线用灰色。中英文共用英文图体，子图文字采用 Arial Regular / Bold。

- [左图 PDF](real_scene.pdf) · [SVG](real_scene.svg) · [PNG](real_scene.png)：由[真机场景源](data/real_scene/scene_rgb.svg)重建，编辑场景或标注时读取。
- [性能绘图](draw_latency.py)：直接从[主表](../../tables/main_results.tex)读取 Native SR／p95；修改右图时读取。线性 0–200 ms，沿用用户选择省略 OpenWAM-α off。
- [右图 PDF](native_tradeoff.pdf) · [SVG](native_tradeoff.svg) · [PNG](native_tradeoff.png)：3.25 in 宽，审阅或复用性能图时读取。
- [SVG 生成入口](build_fig1.py)：生成独立左右图与合成预览；调整真机场景裁切时读取。论文通过 [panels.tex](panels.tex) 并排引用两份 PDF，共用 Fig. 1 编号和 `fig:teaser` 标签。
- [VLA／WAM 二维性能图参考](references/INDEX.md)：TinyVLA 主参考及 4 篇同领域图、来源与裁图复现入口；评审本次视觉优化时读取。
- [布局数据](layout_report.json)：两块图位置、主表数值与速度比；核对图表时读取。
- [数据入口](data/INDEX.md)：当前真机素材与历史仿真数据；更换示例时读取。当前几何由 MoGe-2 估计，未来运动为示意。
- [历史资产](archive/INDEX.md)：旧三栏图及组件；回看先前设计时读取。

## 重建

在本目录运行：

```powershell
python build_fig1.py
node render_fig1.mjs
```

[导出入口](render_fig1.mjs)生成独立左右图和合成预览的 PDF、PNG。标注与图表为矢量，RGB 底图为嵌入位图。

[旧概念 v5.2](concepts/v5_2/fig1_concept_v52.pdf)保留为独立概念，不接入论文。
