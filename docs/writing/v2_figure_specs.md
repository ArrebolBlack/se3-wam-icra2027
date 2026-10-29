# 图项目入口与共享绘图规范

正文图与补充设计研究图由[图项目索引](../../figures/INDEX.md)路由。每幅图的布局、图注、数据要求与标签，以项目内的中英文 TeX 源码为准。

## 正文项目

| 当前图 | 项目入口 | 内容 |
|---|---|---|
| Fig1 | [首图](../../figures/Fig1/INDEX.md) | 动态接触与几何监督 |
| Fig2 | [架构](../../figures/Fig2/INDEX.md) | SE(3)-WAM 矢量架构图与可编辑源 |
| Fig3 | [原理示意](../../figures/Fig3/INDEX.md) | 作用于运动目标的示意 |
| Fig4 | [基准总览](../../figures/Fig4/INDEX.md) | Dynamic-14 十四任务 |
| Fig5 | [延迟扫描](../../figures/latency/INDEX.md) | 0–200 ms 下的实测点；缺失点保留空缺 |
| Fig6 | [消融分析](../../figures/Fig5/INDEX.md) | 按任务划分、两种延迟下的消融热图 |
| Fig7 | [真机任务总览](../../figures/Fig6/INDEX.md) | 单排六任务实拍 |

旧版 interaction_timing、PPTX 工程、基准截图与统计图位于对应项目的 `archive/`。旧图按当前主题归类；历史图号和实验结果不能据此改写为当前稿件图号或结果。

## 共享绘图规范

尺寸按 CVPR 双栏模板：通栏宽 6.875 in（17.46 cm），单栏宽 3.25 in（8.26 cm）。字号以最终尺寸计 7–9 pt，主曲线 1.2–1.6 pt。颜色沿用全文语义色（定义在 `preamble.tex`，与 [写作与画图指南](cvpr_ai_writing_figure_guide.md) 一致）：

| 语义 | 颜色 | 用途 |
|---|---|---|
| 观测/历史 | `#0072B2`（蓝） | 过去的 SE(3) 位姿、观测帧、历史相关曲线 |
| 预测/世界 | `#E69F00`（橙） | 预测的目标 SE(3)、场景 3D 流、世界分支 |
| 动作 | `#7B61A8`（紫） | 指令、夹爪路径、动作分支 |
| 真值/中性 | `#4D4D4D`（灰） | 真值位姿、坐标轴、视觉历史等对照组 |
| 失败标注 | `#D55E00`（红橙） | 失败原因、反应式策略的错误落点 |

在统计图里颜色表示方法族或任务族，并在各面板间保持一致；同一图中的颜色含义保持单一。所有统计图只用真实数据，允许零效应与负效应，不把预期趋势画成实测曲线。真实照片和日志叠加遵循图源中的要求；AI 概念图保留其标记，不能充当实验记录。

## 替换与重建

在对应图项目内，把 `\figplaceholder[...]{宽度}{标题}{规格}` 替换为 `\includegraphics[width=宽度]{figures/FigN/文件名.pdf}`，保留图注与标签，并同步中文图源。可编辑源、导出图、数据和来源说明都在该项目内维护，详见 [目录约定](../../figures/README.md)。

占位框高度就是版面预算；替换后重新编译，确认页数与浮动体。当前 Fig2 直接引用项目内 PDF，重建方法见其[来源说明](../../figures/Fig2/README.txt)；历史图的生成入口为 `python scripts/build_figures.py --only <名称>`，具体命令和 Research 数据要求见各归档索引。

## 补充材料

补充图按标签引用；具体图号随独立补充和合并版的编译方式变化：

- 位姿噪声：[英文](../../appendix/results.tex)、[中文](../../zh/appendix/results.tex)，标签 `fig:pose_noise`。
- 真机装置：[英文](../../appendix/real.tex)、[中文](../../zh/appendix/real.tex)，标签 `fig:real_setup`。旧 AI 任务素材见 [Fig6 历史资产](../../figures/Fig6/archive/INDEX.md)。
- [历史与预测路径研究](../../figures/design_studies/INDEX.md)：附录 E 的真实数据统计图，标签 `fig:history_study`、`fig:prediction_path`。
