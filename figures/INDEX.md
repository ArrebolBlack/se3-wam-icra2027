# 论文图源索引

当前正文使用三幅矢量图；概念图与实测图分别标注证据性质。

- [interaction_timing.svg](interaction_timing.svg)：观测、执行与接触的概念问题图。
- [study_framework.svg](study_framework.svg)：Q1–Q3、训练监督及计算路径。
- [future_supervision.svg](future_supervision.svg)：FUTURE0 十五组成功率点图；分母、单 seed 与无区间条件见图注。
- [generate_figures.py](generate_figures.py)：前两幅图的生成源。
- [plot_future_supervision.py](plot_future_supervision.py)：从 Research CSV 生成实测图；[future_supervision_data.csv](future_supervision_data.csv) 为本稿导出的绘图数据。

[渲染脚本](../scripts/render_figures.py) 将 SVG 转为 PDF。旧图和 [PPTX 项目](../figure_projects/) 未被当前正文引用；benchmark_frames 是场景素材，不是预测结果。新定性图的目的与取样要求见[补充材料 G](../appendix/qualitative.tex)。
