# Fig. 1 真机场景与 Native 性能

[合成预览 PDF](fig1.pdf) · [SVG](fig1.svg) · [PNG](fig1.png) · [论文组版](panels.tex) · [英文图注](figure.tex) · [中文图注](figure_zh.tex)

左侧保留 P040 完整真机画幅，叠加 21 根按预测时刻着色的稀疏 3D 流箭头、目标历史虚影、SE(3) 位姿示意和夹持特写。箭头使用 turbo 的 0.12–0.66 段；机器人、小车和时间图例的流箭身与头部统一无描边，与 Fig. 2、Fig. 3 及后续 flow 图一致。目标位姿、线框与标签固定使用核心红 `#C0263A`，不读取数据图配色。右侧为主表的 Native SR 与原生 p95 散点图，采用[共享配色](../method_colors.json)的 `categories`：FoveaWAM、Video WAM、VLA、Reactive 分别使用 matplotlib tab10 的红、蓝、橙、绿；延迟比箭头与文字同用 tab:red。数据图采用 tab10、示意图采用核心色板，规范见 [palette_spec_20261116.md](../../claude/palette_spec_20261116.md) 第 2.5 节及 Fig. 1 节。两侧子标题居中下置。中英文共用英文图体，子图文字采用 Arial Regular / Bold。

- 目标时间标注为 Past / Now / Future，三者均为核心红、50 号粗体；时长由左上角流色标 `0 → +400 ms` 表达。`Target SE(3)` 配红色立方体线框图标，与 `Sparse 3D flow` 组成左上角图例，两行标题均为 59 号粗体。夹持特写使用深灰 `#3A3A3A`、线宽 4 的细框，无文字标签。
- [左图 PDF](real_scene.pdf) · [SVG](real_scene.svg) · [PNG](real_scene.png)：审阅真机场景叠加或复用左图时读取。
- [左图标注脚本](draw_real_scene.py)：调整历史遮罩、点轨迹配色、目标位姿和夹持特写时读取。
- [性能绘图](draw_latency.py)：直接从[主表](../../tables/main_results.tex)读取 Native SR／p95；修改右图时读取。线性 0–200 ms，沿用用户选择省略 OpenWAM-α off。
- [右图 PDF](native_tradeoff.pdf) · [SVG](native_tradeoff.svg) · [PNG](native_tradeoff.png)：3.25 in 宽，审阅或复用性能图时读取。
- [SVG 生成入口](build_fig1.py)：生成独立左右图与合成预览；调整子图比例和尺寸时读取。论文通过 [panels.tex](panels.tex) 并排引用两份 PDF，共用 Fig. 1 编号和 `fig:teaser` 标签。
- [VLA／WAM 二维性能图参考](references/INDEX.md)：TinyVLA 主参考及 4 篇同领域图、来源与裁图复现入口；评审本次视觉优化时读取。
- [布局数据](layout_report.json)：两块图位置、主表数值与速度比；核对图表时读取。
- [数据入口](data/INDEX.md)：当前真机素材与历史仿真数据；更换示例时读取。
- [历史资产](archive/INDEX.md)：旧三栏图及组件；回看先前设计时读取。

## 重建

在本目录运行：

```powershell
python build_fig1.py
node render_fig1.mjs
```

[导出入口](render_fig1.mjs)生成独立左右图和合成预览的 PDF、PNG。标注与图表为矢量，RGB 底图为嵌入位图。

[旧概念 v5.2](concepts/v5_2/fig1_concept_v52.pdf)保留为独立概念，不接入论文。
