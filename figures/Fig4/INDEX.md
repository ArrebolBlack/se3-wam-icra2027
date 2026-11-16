# Fig. 4：OnTimeBench 总览

比较推理期间暂停和推进物理的两种协议，展示五个任务族及全部十四项任务。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：当前图体、对应图注与标签 `fig:bench_overview`；修改本图时读取。
- [正文 PDF](ontimebench.pdf)、[可编辑 SVG](ontimebench.svg)、[600 dpi 预览](ontimebench.png)：495 × 236 pt，Arial Bold 矢量文字与运动标记。2026-11-16 配色统一（规范见 tmp/palette_20261116/palette_spec_20261116.md 及项目文档 claude/palette_spec_20261116.md）；16 张场景图已按全局 specular 0.10 和中性深灰工作台材质重渲染，无像素级调色。
- [制作工程说明](source_project.md)：机制示例、任务面板来源及重渲染入口；核对画面或修改素材时读取。
- [运动箭头重建](restyle_motion_arrows.py)：幂等更新 19 个蓝色和 2 个黑色箭头，保留其余 SVG 字节；Harmonic 仅保留一个向上箭头，Rotating 保留一个移动箭头与旋转圆弧。几何唯一来源为 [motion_arrow.py](../../scripts/motion_arrow.py)，按最终印刷 pt 计算。参数、自适应与 27 项核对见[验收记录](../../docs/figures_20261116/arrow_unify/INDEX.md)。
- [正文入口](../../sections/benchmark.tex)、[中文正文入口](../../zh/sections/benchmark.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查早期十四任务图、其他旧稿与占位规格时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。
