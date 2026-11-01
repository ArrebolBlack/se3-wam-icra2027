# Fig6：六项真机任务总览

一排六张已审核的任务实拍，斜坡使用新版裁剪；图中只介绍任务场景。2026-11-01 收尾核对：当前英文 PDF 为 Figure 6、第 8 页。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：通栏图体、双语图注和 `fig:real_trials` 标签；论文集成时读取。
- [当前导出](outputs/INDEX.md)：矢量 PDF、可编辑 SVG 和 600 dpi PNG；插图或编辑时读取。
- [素材](assets/INDEX.md)、[面板清单](manifest.json)：六项任务的实拍来源、裁剪与面板映射；替换面板时读取。
- [实拍导入](import_task_photos.py)：导入原片与已审核裁剪，逐张检查像素；重新选片时读取。
- [排版脚本](build_figure.py)：独立重建当前图；运行 `python figures/Fig6/build_figure.py`，需要 Pillow、reportlab、PyMuPDF 和 Windows Arial 字体。
- [集成与收尾记录](INTEGRATION.md)：单排版、最新验证、证据范围和归档后的接续入口；验收或恢复工作时读取。
- [正文入口](../../sections/experiments.tex)、[中文正文入口](../../zh/sections/experiments.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查旧稿的可编辑源、导出图、脚本和数据时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。

当前图宽 6.875 in、高 1.111 in；六幅照片均保持 16:9。原两排版和时序占位已归档。
