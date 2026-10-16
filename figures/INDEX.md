# 论文图源索引

当前正文使用三幅矢量图；概念图与实测图分别标注证据性质。

- [interaction_timing.svg](interaction_timing.svg)：同一目标的运动历史、未来表示与接触几何示意。
- [study_framework.svg](study_framework.svg)：已实现 D 主干的输入、访问矩阵、训练损失与在线动作计算。
- [future_supervision.svg](future_supervision.svg)：FUTURE0 十五组按设计因素分组的成功率差与配对场景得失；分母、单 seed 与无区间条件见图注。
- [generate_figures.py](generate_figures.py)：前两幅图的生成源。
- [plot_future_supervision.py](plot_future_supervision.py)：从 Research CSV 生成实测图；[future_supervision_data.csv](future_supervision_data.csv) 为本稿导出的绘图数据。

[渲染脚本](../scripts/render_figures.py) 将 SVG 转为 PDF。旧图和 [PPTX 项目](../figure_projects/) 未被当前正文引用；benchmark_frames 是场景素材，不是预测结果。新定性图的目的与取样要求见[补充材料 G](../appendix/qualitative.tex)。
