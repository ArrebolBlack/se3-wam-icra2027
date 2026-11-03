# Fig. 5 来源与复现

本目录是六个对照的设计预览，全部 96 个统计单元均为 NA，不表示零效应。
2026-11-03 新增统一精细流行后，在 Windows 上使用 Arial 重建；旧五行图片已被替换。

## 数据与对照

行序为 `no_se3`、`fine_flow`、`no_flow`、`no_history`、`no_future`、`no_aux`，
对应统一粗粒度流、统一精细流、无场景流监督、无目标历史、无未来监督、无辅助目标。
图内前两行缩写为 “Uniform coarse” 和 “Uniform fine”；完整定义见中英文图注和附录 C.4。
每个对照按单训练种子规划，评测原生延迟与附加 150 ms；八列为 All、五个任务族及两个可重叠机制组。
配对区间仅描述给定训练权重下的场景不确定性，不表示训练种子波动。

`fine_flow` 去掉目标 SE(3) 损失和位姿头，保留辅助目标，并提高全场景流的监督密度。
每 patch 4×4 点、总计 56×56 网格是候选值，尚未按实际目标投影大小核实；
训练前应统计目标表面的流点数，检查典型目标能否获得约 10 个以上的点，再确定密度。
正文、图注和附录继续保留密度、点数和结果占位。

实验规格与状态见 [Research A4](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/experiments/A4/A4.md)，
论文范围见[实验计划](../../docs/EXPERIMENT_PLAN.md)。本次重建没有启动训练或评测。
原始统计工具位于 `C:/workspace/se3-wam-fig5-output/`；其 `INDEX.md` 路由
逐场景输入、`compute_statistics.py`、INFER0 bootstrap 与 `DATA_INTERFACE.md`。
结果齐备后从该接口接收真实统计，不用预期趋势填数。

## 重建

在本目录运行，依赖版本见 [requirements.txt](requirements.txt)，字体为 Arial：

```powershell
python plot_fig5.py --layout stacked --output .
```

单栏宽 3.25 in，高度随行数变化；六行时为 3.448 in（约 3.45 in）。
主标签 7.5 pt，单元值 7.2 pt，上下图共用列名和色条。
中英文均以 `width=3.25in` 嵌入同一矢量 PDF；PDF、SVG、PNG、灰度预览和
`layout_report.json` 随脚本重建。布局报告记录六个对照、96 个待测单元、字体与画布边界。

`--layout paper` 为通栏备选；历史试排由源产物的 `paper_integration/INDEX.md`
和 `single_column/INDEX.md` 路由。填入真实数字后重新检查最终尺寸下的可读性。
