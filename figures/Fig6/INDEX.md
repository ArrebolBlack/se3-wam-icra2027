# Fig6：真机任务与配对试验

当前已嵌入合成排版预览；图体和图注保留 AI 标识，尚不是真机试验结果。

- [英文图源](figure.tex)、[中文图源](figure_zh.tex)：通栏图体、双语图注和 `fig:real_trials` 标签；论文集成时读取。
- [当前导出](outputs/INDEX.md)：矢量 PDF、可编辑 SVG 和 600 dpi PNG；插图或编辑时读取。
- [素材](assets/INDEX.md)、[面板清单](manifest.json)、[生成提示](generation_prompts.json)：保留的合成原图、确定性裁剪和缺失数据状态；替换素材时读取。
- [排版脚本](build_figure.py)：独立重建当前图；运行 `python figures/Fig6/build_figure.py`，需要 Pillow、reportlab、PyMuPDF 和 Windows Arial 字体。
- [集成记录](INTEGRATION.md)：来源、局部排版改动、构建验证与尚缺的真实材料；验收时读取。
- [正文入口](../../sections/experiments.tex)、[中文正文入口](../../zh/sections/experiments.tex)：核对本图上下文与引用时读取。
- [历史资产](archive/INDEX.md)：查旧稿的可编辑源、导出图、脚本和数据时读取。
- [全部图项目](../INDEX.md)：返回正文图目录。

历史占位规格已归档；当前图保持 6.875 × 2.375 in 宽高比，不强制压回 1.8 in。
