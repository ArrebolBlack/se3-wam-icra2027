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
python plot_fig5.py --layout stacked --output .
```

当前图宽 3.25 in、高 3.1 in，主标签 7.5 pt、单元值 7.2 pt。上图为原生延迟，下图为
附加 150 ms；两图列位置严格对齐，共用顶部列名和底部色条，保留全部五行、八列。
行名缩写对应表 `tab:design` 的完整定义，Rot./Ctx. 释义置于图注。
英文以单栏 `figure` 嵌入，中英文都明确使用 `width=3.25in`，保持审阅时的物理尺寸，
避免按中文整页正文宽度放大。两种版本的单元值均为 7.2 pt。

`--layout paper` 可重建先前的通栏备选。历史试排见源产物的 `paper_integration/INDEX.md`，
当前单栏页面与独立审查见 `single_column/INDEX.md`。篇幅不作为本次替换门槛。
