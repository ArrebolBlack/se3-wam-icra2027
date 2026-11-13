# Fig. 2：按角色分配预测精度

引言中的单栏图，标签 `fig:paradigms`。用同一录制场景和放大区域比较 Video WAMs、目标中心预测器和 FoveaWAM。(a) 堆叠未来帧，(b) 堆叠历史观测与当前帧。(b) 和 (c) 在同一原色当前帧上叠加录制标签。

- [生成脚本](build_paradigms.py)：版式、配色、标注与文字的主源；`python build_paradigms.py --render` 写出 SVG，并经 [共享导出](../../scripts/common.py) 用 Chrome 打印 PDF 与 PNG。依赖 Pillow。
- [素材投影脚本](prepare_assets.py)：把录制标签投影到渲染帧并描出目标轮廓，写出 `assets/overlay.json`；标签或帧变化后运行一次。需要 contourpy（随 matplotlib 安装）。
- [素材索引](assets/INDEX.md)：四帧录制状态的 Blender 渲染，以及用于叠加的流、位姿与轮廓。
- [可编辑 SVG](paradigms.svg)：脚本输出，文字为 Arial 的可编辑 `<text>`，底图内嵌；手工微调后需同步回脚本。
- [论文 PDF](paradigms.pdf)、[PNG 预览](paradigms.png)：正文插图和整体检查入口，单栏宽 3.25 in，高约 2.15 in，字号 6.8–8 pt。
- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：图体、图注和引用。
- [来源说明](source.json)：帧号、标签来源、显示处理与图中数字的出处；核对科学含义时读取。
- [英文引言](../../sections/introduction.tex)、[中文引言](../../zh/sections/introduction.tex)：正文插入位置与 (a)(b)(c) 引用。
- [旧版三栏流程图](archive/three_column_pipeline/INDEX.md)：被替代的输入—模型—输出版本及其素材来源。
