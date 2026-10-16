# 论文图

SVG 是论文矢量图的唯一编辑源；同名 PDF 由 `scripts/render_figures.py` 生成。
概念示意不表示已测结果；真实场景帧不替代当前 Benchmark 合同或评测证据。

| 对象 | 用途与何时读取 |
|---|---|
| [teaser_timeline.svg](teaser_timeline.svg) | 正文问题图：观测—执行错位及可能未来；修改开篇动机时读取。 |
| [study_design.svg](study_design.svg) | 正文设计图：完整 Q1–Q3、共同协议与候选空间；修改研究轴时读取。 |
| [benchmark_suite.svg](benchmark_suite.svg) | 正文任务概览：已有模拟器真实帧；核对任务示意与照片来源时读取。 |
| [architecture.svg](architecture.svg) | 附录候选接口示意：历史、物理未来与动作生成路径；不是已选定架构。 |
| `benchmark_frames/` | 原有真实场景图片，供任务概览引用；不包含预测结果或成功率。 |

历史 PPTX 项目从 [`../figure_projects/`](../figure_projects/) 进入，不是当前 SVG 的同步编辑源。
