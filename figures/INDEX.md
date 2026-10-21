# 论文图源索引

v2 稿件的图分三类：复用的 v1 图（PDF）、TikZ 草图（随开关自动变化）、以及带详细规格的占位框（`\figplaceholder`）。
逐幅规格与替换方式见 [v2 图规格](../docs/writing/v2_figure_specs.md)。

## v2 正文

- 图 1 首图：占位，见 `sections/teaser.tex`（真机照片 + 4D 叠加，需真实试验数据）。
- 图 2：[interaction_timing.pdf](interaction_timing.pdf)（复用；`sections/formulation.tex` 中裁去顶部标题行）。源：[generate_figures.py](generate_figures.py)。
- 图 3：[architecture_tikz.tex](architecture_tikz.tex)（TikZ 草图，读取 `paper_config.tex` 的开关与配置宏）。
- 图 4：占位，见 `sections/experiments.tex`（六个面板：坍缩、记住×领先、记住×噪声、预测×目标动力学、预测×环境、行动×耦合）。

## v2 补充材料

- 图 S1：[benchmark_task_examples.pdf](benchmark_task_examples.pdf)（复用的真实仿真截图，非策略结果）。源：[plot_benchmark_task_examples.py](plot_benchmark_task_examples.py)。
- 图 S2–S5：占位（4D 提升示意、预训练规模、真机平台、生效时刻的定性对齐），见对应附录文件。

## v1 图与数据（v2 未引用，保留以便追溯）

每幅 v1 图只由一个脚本生成，`python scripts/build_figures.py` 依次重建，`--only <名称>` 只重建指定的图；SVG 由 `scripts/common.py`
调用 Chrome/Edge 打印成 PDF。v1 图包括 model_design、future_supervision、study_framework、history_diagnostics、gt_history_intervention、
prediction_examples、decoder_failures 等，及其 CSV/JSON 数据与来源说明（v1 版本的索引见快照 `local_private/archived-v1-20261020/`）。
其中 [model_design.svg](model_design.svg)（[draw_model_design.py](draw_model_design.py)）可作为精修图 3 的起点，
[kinematic_baselines.py](kinematic_baselines.py) 可复用于图 4d 的离线外推误差。
