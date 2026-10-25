# Fig. 5 来源与复现

本目录插入的是 2026-10-25 已审阅的设计预览，不是已完成的实验结果。
源产物位于 `C:/workspace/se3-wam-fig5-output/`；该目录的 `INDEX.md` 路由原始事实快照、
逐场景输入、`compute_statistics.py`、未改动的 INFER0 bootstrap 实现、统计验证与独立评审。
这里只接收绘图需要的最小统计快照、可编辑绘图脚本和导出图，实验事实仍由 Research 仓库维护。

现有 80 个单元均为 NA，不能将其解释为零效应。完整结果需要 full 与五个 control，
各三个训练种子、native 和 +150 ms 两个条件；uniform-fidelity 还需已落实的干预定义和训练证据。
填数前使用源产物的 `DATA_INTERFACE.md` 接收合格输入，并重新执行统计与科学验收。
制图和论文替换没有启动训练或评测，也没有改写正文中的预期结果占位。

在本目录运行（Python 依赖版本见本目录 `requirements.txt`，字体使用 Arial）：

```powershell
python plot_fig5.py --layout paper --output .
```

图宽 6.875 in、高 1.92 in，主标签 8 pt、单元值 7.2 pt；以 `figure*` 和
`width=\textwidth` 嵌入。原单栏 3.25 x 1.4 in 预算不能容纳所有标签和数值，
故采用通栏并压缩重复图例与留白。可用 `--layout stacked` 重绘单栏上下排列的备选版；
正文当前保留通栏。前次隔离试排的两种版式均为 9 页；本次按用户要求先替换正文占位，
篇幅不作为替换门槛。历史试排与页面检查见源产物的 `paper_integration/INDEX.md`。

英文实际嵌入仍为 7.2 pt；中文 A4 审读稿按 170 mm 正文宽度缩放后约为 7.01 pt。
