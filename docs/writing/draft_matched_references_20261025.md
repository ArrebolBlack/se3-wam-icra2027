# 当前初稿的写作与绘图参考方案

阅读日期：2026-10-25，最后核对至 16:45 UTC。对象是本机工作树的英文主稿、A–E 附录、正文结果表和
六组既有图源，以及阅读期间新增的延迟图；包括当日尚未提交的首图与真机部分，不是早期 Q1–Q3 Study 稿。
以下是修改建议，尚未修改正文、结果、图源或引用库。
原论文题目、版本、图页观察和 PDF 只在
[研究仓库的新增来源笔记](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md)维护。
通用规则仍见 [AI 写作与画图指南](cvpr_ai_writing_figure_guide.md)，本页补充当前稿件的具体取舍。

## 阅读后的判断

当前论文的中心是 **用按角色分配精度的几何预测监督，学习能及时作用于运动目标的策略**。
低维目标历史、目标 SE(3) 与全场景稀疏流、部署时跳过预测头是这条主线的三个环节。
Q1–Q3 开发研究放在附录 E，为设计选择提供来源；正文应以最终方法及其验证为主。

最需要参考的不是更多通用 WAM 架构图，而是三类表达：

1. **把表示选择写成可检验的设计判断。** 误差分解说明为什么值得精确估计目标，但不能
   独自证明所有上下文都只需粗估计，也不能证明 3D 一定胜过 2D。
2. **把训练收益和部署计算清楚分开。** 动作读取摘要隐状态；解码出的 SE(3)／flow 不输入动作。
   跳过预测头并不是首次提出，本文需要突出监督的几何内容及精度分配。
3. **把效率与闭环结果放在一起。** 原生延迟、附加延迟、暂停物理、等延迟回答不同问题；
   不能只靠一个最快推理数字支持动态操作收益。

以上判断来自 [Introduction](../../sections/introduction.tex)、[Method](../../sections/method.tex)、
[Experiments](../../sections/experiments.tex)、[开发研究](../../appendix/design.tex)和
[真实时间协议](../../appendix/benchmark.tex)。附录 E 保留的结果尤其重要：2D／3D 差异跨种子
改变方向，预测路径与损失也曾同时变化；这些事实不应被“优化写作”改成纯表示优势。

## 最值得定向阅读的七篇

下表只给本稿的用途；完整题目、会议状态和来源从对应笔记进入。D4RT 是已核实的
CVPR 2026 Best Paper；其他论文的参考价值不依赖推测审稿分数。

| 优先级 | 来源笔记 | 对当前稿最有价值的用途 | 本稿位置 |
|---|---|---|---|
| A | [D4RT](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#d4rt) | 先用一个接口解释时空表示；颜色对应实体、时刻与坐标 | 方法开头、Fig. 1／3 |
| A | [MoGe](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#moge) | 几何矛盾 → 表示选择 → 对应监督；同构反事实示意 | §3.2、Fig. 3 |
| A | [FastVLM](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#fastvlm) | 性能与实测端到端延迟同时呈现；拆分时间成本 | §4.2、效率结果图、附录计时 |
| A | [Fast-WAM](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#fast-wam) | 分离未来监督和在线未来生成；把已有贡献与本文增量讲准 | 引言末段、Fig. 2、no-future 对照 |
| A | [RTC](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#rtc) | 控制时间轴、延迟敏感性曲线与任务分解 | §3.4、Fig. 3(b)、§4.2 |
| B | [DiffusionDrive](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#diffusiondrive) | 每项设计回应一个具体失败；案例图与证据对应 | 引言、实验段落、Fig. 6 |
| B | [HiF-VLA](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/draft_style_sources_2026_10_25.md#hif-vla) | 把历史表示的收益和成本一起检验；注入位置局部对照 | 历史输入说明、附录 E |

旧清单中仍优先复用 PointWorld 的 3D 轨迹表达、VGGT 的 token 排列，以及 NWM 的用途驱动
实验组织。CoT-VLA 的未来子目标条件、生成式视频展示不适合作为本稿方法主图的主要模板：
本稿部署路径不生成或读取这些输出。原文入口见研究仓库的[旧来源笔记](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md)。

## 写作如何具体吸收

### 引言：让核心观察先于模块清单

保留现有的 0.1 m/s、150 ms、15 mm 数量级例子，并清楚标为说明问题的计算例子。
接着只推进两件事：观测之后目标仍运动；更昂贵的信息处理也会增加动作陈旧程度。
用 D4RT／MoGe 的组织方式，把“目标精、场景粗”写成对此问题的具体设计回答，再介绍模型。

“未来只作监督”紧接 Fast-WAM 的已有工作定位；主要增量落在度量目标状态、角色相关监督
与计入延迟的控制验证。不要让第三段退回一个新的“测试时无需预测未来”的首创故事。
最终结果齐备后，摘要保留成功率差值、完整出动作延迟和真机范围三个信息即可。

### 方法：按读者的问题排序，而不是把实现展开到同等深度

先说明实际输入、部署输出与训练标签，再回答：为什么目标需要姿态、为什么场景要有流、
为何部署不执行读出头。物理时刻、世界坐标系和动作取用规则各定义一次。
token 维度、mask 有效标记、线性头形状与详细优化器配置沿现有附录入口读取。

“上下文可粗估计”应与 $m\gg\varepsilon$ 等适用条件相连；驱动体通过目标动力学影响接触，
是本稿论证的一部分，不宜扩写成对所有接触、狭窄通道或可变形对象的普遍定理。
角色分配的机制性结论仍取决于最终分组消融，不能由 schematic 的配色证明。

### 实验：一句判断对应一种对照

| 要回答的问题 | 使用已有方案中的证据 | 写作／图形参考 |
|---|---|---|
| 实际运行时是否更成功、更及时？ | 原生延迟 SR 与同硬件 p95 time-to-action；真机包含跟踪 | FastVLM |
| 收益是否随时间压力变化？ | 已计划的 0／50／100／150／200 ms 附加延迟扫描 | RTC |
| 更快是否解释全部收益？ | 暂停物理、等延迟与原 executor 对照分别报告 | FastVLM 的测量边界 + 本稿协议 |
| 未来监督本身是否有用？ | full 与 no-future，保持部署计算一致 | Fast-WAM |
| 为什么是角色相关几何？ | no-SE(3)、no-flow、uniform-fidelity 及预先定义的任务组 | MoGe 的设计—监督对应 |
| 目标历史是否值得其成本？ | 最终 no-history；开发历史研究限定其配方与种子范围 | HiF-VLA |

每段只抓主要差值与区间，不逐行抄表。先陈述共同条件，再说明结果支持到哪一步。
当前 uniform-fidelity 的目标／读出／权重仍有占位；填清后才能把它作为明确的表示对照。
开发筛选与最终 24 层确认保持区分。以上不新增实验承诺，也不授权启动实验。

## 六组既有图源与延迟图的参考分工

下表 Fig1–Fig6 指目录名。当前新增 `fig:latency` 后，PDF 中延迟、消融、真机图依次为
Fig. 5、6、7；后续对话应通过标签和目录定位，避免沿用旧图号。

| 图源目录与内容 | 主参考与局部参考 | 值得吸收的改进 |
|---|---|---|
| [Fig. 1 首图](../../figures/Fig1/INDEX.md) | D4RT Fig. 2；MoGe Fig. 4 | 同一物体贯穿捕获、未来时刻和接触；减少重复标签，角色配色与全文一致。首次阅读应看懂“运动造成偏差、目标精度关键”。保持设计稿身份，真实轨迹齐备后再形成证据图 |
| [Fig. 2 架构](../../figures/Fig2/INDEX.md) | Fast-WAM Fig. 1–2；MoGe Fig. 3 | 保留已验收的主体。重点检查训练支路与部署路径能否一眼分清，以及 world KV 一次计算／action 多步复用。预测头不能有指向动作的输出箭头；不照搬参考的未来 video tokens |
| [Fig. 3 原理](../../figures/Fig3/INDEX.md) | MoGe Fig. 4；RTC Fig. 3 | 对照面板固定物体尺度与视角，只改变历史、执行时刻或精度需求。动作槽与同一时间轴对齐；接触局部放大与原场景有明确连线。一次最多让一个子图承担一个问题 |
| [Fig. 4 任务总览](../../figures/Fig4/INDEX.md) | 既有 PointWorld／NWM 参考 | 保持十四任务的真实状态渲染，精修标签、对齐和任务族层级即可。它负责定义任务分布，不再承担方法机制或实验优势 |
| [Fig. 5 消融](../../figures/Fig5/INDEX.md) | RTC Fig. 5；FastVLM Fig. 4–5 | 当前逐任务双热图信息密集。可将正文重点收束到预设角色组的配对差值与区间，把完整逐任务热图移附录；空位继续显示 NA，不能以筛选结果填充最终对照 |
| [Fig. 6 真机](../../figures/Fig6/INDEX.md) | DiffusionDrive Fig. 2；RTC 的任务—延迟对照 | 真机素材齐备后，按相同 trial key 与真实时间标记比较捕获、首次执行和终局。保持同视角、同裁切尺度；若时刻不同就标实际时间，不能用相同帧序号暗示同步 |

### 已新增延迟图的下一步

最终核对时，[独立延迟图](../../figures/latency/INDEX.md)已加入正文，原来指向首图的引用也已修正。
当前图为设计预览，只有 ACT 在 0／150 ms 的实测点；其余方法继续留空。进一步完善
**成功率—延迟关系**时，建议用两个小面板分别回答效率与时间压力问题：

- 横轴为完整 p95 time-to-action（ms），纵轴为原生延迟 SR；每个已评估方法一个点，必要时
  用标记形状区分输入条件，配对增强基线明确标 `+SE(3)`。只有一个点的方法之间不画插值线。
- 横轴为附加延迟（ms），纵轴为 SR，使用现有延迟扫描的真实工作点与已定义区间。原生耗时
  已包含在协议中，图注区分附加延迟与总延迟，不能把两者混作一个横轴。

有数据后先尝试放在 §4.2；为控制篇幅，压缩重复的 Fig. 1／3 示意与长 caption，完整任务
热图和分阶段计时留附录。若保留 Fig. 5 为正文机制证据，不要为塞入效率图把它整张移走而
让 role-aware 主张只剩附录支撑。具体浮动位置需改稿后编译确定，不先承诺六图或七图。

当前延迟图 caption 计划以三个训练种子的极差作阴影；它与场景 bootstrap 置信区间含义不同。
可以沿用实际统计口径，但必须明确标注，不能将极差写成 95% CI。这里不替实验协议选择区间。

可复用的 caption 草案，方括号为待填事实：

> Success under computation delay. (a) Native-latency success versus p95 time-to-action
> on [hardware], including [measured stages]. (b) Success as [0–200] ms is added to each
> query while physics continues. Results use [scene and seed aggregation]; intervals are
> [the actual paired-bootstrap definition].

这是原创建议句型，不是文献原句；填写必须服从实际统计协议。

## 阅读时发现的具体衔接问题

这些是当前工作树的快照观察，供下一轮改稿处理，本轮没有修改：

1. 最后核对时保存的 `main.pdf` 共 12 页，**正文与 Conclusion／Limitations 延伸至第 9 页**，LLM 声明
   从第 10 页开始。文档索引仍写“8 页正文”，不能把该描述当作当前页数验收；后续源码修改需重新编译验收。
2. 原生基线的腕部相机描述未统一：实验正文写按原配方提供渲染腕部相机，附录 B 的
   Common conditions 写 masked／black wrist inputs。应按实际运行记录统一；风格优化不能
   自行选择一个说法。主结果表的输入列也随之核对。
3. [通用指南](cvpr_ai_writing_figure_guide.md)仍有 v2 的独立 formulation 文件与旧图号预算；
   当前结构应从 [正文索引](../../sections/INDEX.md)和[附录索引](../../appendix/INDEX.md)进入。
   本页不重新定义页数方案，避免与当前作者指南平行维护。

正文结果仍有占位，Fig. 1／6 是明确标注的设计预览；参考图的高完成度不能改变这些证据状态。

## 给下一轮 AI 写作／绘图对话的入口

```text
请先读 docs/writing/draft_matched_references_20261025.md，再从当前 sections/INDEX.md、
appendix/INDEX.md 或 figures/INDEX.md 读取本次目标。参考论文按该文档的来源链接定向读取：
D4RT 学时空接口，MoGe 学几何论证，FastVLM／RTC 学效率证据，Fast-WAM 学训练与推理区别。
真正打开所选参考图，指出本次借用的布局或论证关系，然后修改已授权的目标。
保持当前方法、时间／坐标语义、真实结果与待验证占位；不把参考论文的模块、数据或结论移植进来。
```

本机看图入口由研究仓库来源笔记维护，包含原 PDF、重点整页和独立裁图。
