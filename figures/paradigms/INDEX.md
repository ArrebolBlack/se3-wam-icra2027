# Fig. 2：按角色分配预测精度

引言中的单栏图，标签 `fig:paradigms`。用同一录制场景比较全场景、目标中心和按角色分配精度（FoveaWAM）三种预测方式。(a) 堆叠未来帧。(b) 和 (c) 用同一当前帧，分别叠加目标位姿轨迹，以及目标位姿轨迹与稀疏 3D 流。

当前采用 2026-11-16 D2 定稿画法：流沿真实八步轨迹，以 Fig. 1(a) 的 turbo 0.12–0.66 渐变箭身和箭头头部表示时间，所有箭身、头部及时间图例均无描边；目标用核心红，SE(3) 轮廓、轨迹和 RGB 坐标轴均无衬边，✓ / ✗ 用核心绿 / 红。缩略图的放大区域框仅用 0.5 pt 黑色细框，无白色衬边，连接线不变。底图按共享参数重渲染，specular 0.10，保留原相机与传送带绿色。

- [生成脚本](build_paradigms.py)：版式、配色、标注与文字的主源；`python build_paradigms.py --render` 写出 SVG，并经 [共享导出](../../scripts/common.py) 用 Chrome 打印 PDF 与 PNG。依赖 Pillow。
- [四帧渲染脚本](render_assets.py)：从原生场景重放第 29、30、33、37 帧，导入研究仓共享参数并核对原相机与位姿误差；重建底图时读取。
- [素材投影脚本](prepare_assets.py)：把录制标签投影到渲染帧并描出目标轮廓，写出 `assets/overlay.json`；标签或帧变化后运行一次。需要 contourpy（随 matplotlib 安装）。
- [素材索引](assets/INDEX.md)：当前帧和三张未来帧的 Blender 渲染，以及用于叠加的流、位姿与轮廓。
- [可编辑 SVG](paradigms.svg)：脚本输出，文字为 Arial 的可编辑 `<text>`，底图内嵌；手工微调后需同步回脚本。
- [论文 PDF](paradigms.pdf)、[PNG 预览](paradigms.png)：正文插图和整体检查入口，单栏宽 3.25 in，字号 6.8–8 pt。
- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：图体、图注和引用。
- [来源说明](source.json)：帧号、标签来源、显示处理与图中数字的出处；核对科学含义时读取。
- [英文引言](../../sections/introduction.tex)、[中文引言](../../zh/sections/introduction.tex)：正文插入位置与 (a)(b)(c) 引用。
- [旧版三栏流程图](archive/three_column_pipeline/INDEX.md)：被替代的输入—模型—输出版本及其素材来源。

在本目录重建（使用论文 Python 环境运行后两步）：

```powershell
& 'C:/workspace/se3-wam-research/.envs/blender-paper/mujoco-blender-render/Scripts/python.exe' render_assets.py --research-root C:/workspace/se3-wam-research
python prepare_assets.py
python build_paradigms.py --render
```
