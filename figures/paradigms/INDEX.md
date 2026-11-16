# Fig. 2：按角色分配预测精度

引言中的单栏图，标签 `fig:paradigms`。用同一录制场景比较全场景、目标中心和按角色分配精度（FoveaWAM）三种预测方式。(a) 堆叠未来帧。(b) 和 (c) 用同一当前帧，分别叠加目标位姿轨迹，以及目标位姿轨迹与稀疏 3D 流。

- [生成脚本](build_paradigms.py)：版式、配色、标注与文字的主源；`python build_paradigms.py --render` 写出 SVG，并经 [共享导出](../../scripts/common.py) 用 Chrome 打印 PDF 与 PNG。依赖 Pillow。
- [素材投影脚本](prepare_assets.py)：把录制标签投影到渲染帧并描出目标轮廓，写出 `assets/overlay.json`；标签或帧变化后运行一次。需要 contourpy（随 matplotlib 安装）。
- [素材索引](assets/INDEX.md)：当前帧和三张未来帧的 Blender 渲染，以及用于叠加的流、位姿与轮廓。
- [可编辑 SVG](paradigms.svg)：脚本输出，文字为 Arial 的可编辑 `<text>`，底图内嵌；手工微调后需同步回脚本。
- [论文 PDF](paradigms.pdf)、[PNG 预览](paradigms.png)：正文插图和整体检查入口，单栏宽 3.25 in，字号 6.8–8 pt。
- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：图体、图注和引用。
- [来源说明](source.json)：帧号、标签来源、显示处理与图中数字的出处；核对科学含义时读取。
- [英文引言](../../sections/introduction.tex)、[中文引言](../../zh/sections/introduction.tex)：正文插入位置与 (a)(b)(c) 引用。
- [旧版三栏流程图](archive/three_column_pipeline/INDEX.md)：被替代的输入—模型—输出版本及其素材来源。
