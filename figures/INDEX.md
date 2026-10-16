# 论文图源索引

当前正文使用三幅矢量图；概念图与实测图分别标注证据性质。

- [interaction_timing.svg](interaction_timing.svg)：同一目标的运动历史、未来表示与接触几何示意。
- [study_framework.svg](study_framework.svg)：已实现 D 主干的输入、访问矩阵、训练损失与在线动作计算。
- [future_supervision.svg](future_supervision.svg)：FUTURE0 十五组按设计因素分组的成功率差、十四组场景 bootstrap 区间与配对得失；P00 为参照，区间条件见图注。
- [generate_figures.py](generate_figures.py)：前两幅图的生成源。
- [plot_future_supervision.py](plot_future_supervision.py)：从 Research CSV 生成实测图；[future_supervision_data.csv](future_supervision_data.csv) 为本稿导出的绘图数据。
- [future_supervision_uncertainty.csv](future_supervision_uncertainty.csv)：全部 27 对比较的任务内配对 bootstrap 区间与复现参数；查看单 checkpoint 的场景抽样不确定性时读取。
- [base2_paired_uncertainty.csv](base2_paired_uncertainty.csv)：BASE2 匹配 I−F、I−E 及事后十三任务敏感性分析的场景 bootstrap 区间；未校正训练 seed 波动或候选选择偏差。
- [history_paired_uncertainty.csv](history_paired_uncertainty.csv)：九臂 HISTORY1 原生结果配对后的八项区间；用于 Q1 条件性场景差异，排除训练 seed 和选择不确定性。
- [history_interventions.csv](history_interventions.csv)：八种当前位姿条件的离线历史扰动汇总；首动作变化与固定 ridge 读出分别报告，不表示闭环收益。
- [prediction_examples.svg](prediction_examples.svg)：DEV84 上 P15/CV/CA 的逐时距中位数/四分位带、中位数放大视图与三个真实 P15 位姿预测例子；与真实接触证据区分阅读。
- [prediction_examples_aggregate.csv](prediction_examples_aggregate.csv)：三方法各八时域及总体的描述性汇总；每方法 672 个状态—时距误差并非独立样本，分位带不是置信区间。
- [kinematic_baselines.py](kinematic_baselines.py)：从实际可见 GT pose 历史计算 CV/CA，明确末区间导数、当前速度外推及左乘旋转积分；不读取未来信息构造预测。
- [prediction_examples_baseline_inputs.csv](prediction_examples_baseline_inputs.csv) 与 [prediction_examples_baseline_errors.csv](prediction_examples_baseline_errors.csv)：84 状态的原始输入/导数，以及三方法共 2,016 项预测和误差，供复算与检查尾部误差。
- [benchmark_task_examples.svg](benchmark_task_examples.svg)：八个任务条件的真实 DEV84 观察；显示任务几何，不作为 rollout 结果。
- [plot_benchmark_task_examples.py](plot_benchmark_task_examples.py)：按每任务最低 state index 选择原图；完整来源及成员记录见 [benchmark_task_examples_source.json](benchmark_task_examples_source.json)。
- [plot_prediction_examples.py](plot_prediction_examples.py)：从原生归档复算误差、按确定秩选例并生成定性图；来源见 [prediction_examples_source.json](prediction_examples_source.json)，曲线与选择分别导出为同名前缀的 data.csv、selection.csv。

[渲染脚本](../scripts/render_figures.py) 将 SVG 转为 PDF。旧图和 [PPTX 项目](../figure_projects/) 未被当前正文引用；benchmark_frames 是场景素材，不是预测结果。新定性图的目的与取样要求见[补充材料 G](../appendix/qualitative.tex)。
