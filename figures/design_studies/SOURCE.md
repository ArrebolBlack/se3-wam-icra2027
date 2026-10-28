# 来源与重建

这些是四层模型、早期同步执行协议下的设计研究，不替代最终模型的实时消融。

历史数据：Research `docs/experiments/HISTORY1/HISTORY1.md` 的当前图像参照 748/1400、八项配对比较，以及冻结检查点的 824/1400 与 9/1400 干预。区间沿用已接受的任务内场景配对 bootstrap，给定单训练 seed 检查点，pointwise、未作多重比较校正；没有重算或改动区间。训练比较与推理干预使用分开的面板和坐标。

预测路径：Research `docs/experiments/BASE2/results/completed-results.md` 的 I/P/Q/E 逐 seed 成功数；以及 `docs/experiments/SCALE0/SCALE0.md` 的 dl2d4/dl4 三 seed 对照。每个端点分母均为 1400；脚本由计数重算 SR、均值及样本标准差，并与原稿六组摘要核对。误差线是训练 seed 的样本 SD，不是场景置信区间。面板间编码器及辅助监督不同。

复现：在论文根目录运行 `python figures/design_studies/plot.py`，依赖根目录 requirements.txt 中的 NumPy 与 Matplotlib；Windows 图中文字使用 Arial / Microsoft YaHei。输出为向量 PDF、可编辑 SVG 与 300 dpi PNG。中英文读取同一份 CSV。宽度均为 6.875 in，图内文字 7.2–9 pt。
