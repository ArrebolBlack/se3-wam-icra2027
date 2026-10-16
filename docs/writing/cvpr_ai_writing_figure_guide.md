# AI 辅助 CVPR 论文写作与科研画图指南

这份指南把已精读论文的表达方式整理成可执行的写作与画图规则。适合直接作为 AI 的参考上下文，
用于起草、改写、图表设计和 caption 撰写。核心要求是：**让具体问题、实际方法和实验使用同一条
论证线；让图中的颜色、箭头、坐标与比较条件具有明确含义。**

以下规则与视觉数值是写作归纳和可调设计建议，不是 CVPR 官方格式，也不定义 SE(3)-WAM 的
架构、实验方案或科学结论。18 篇论文的具体观察、会议等级、图号页码和原文入口仍由
[精读笔记](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md)保存；涉及项目事实时按
[项目入口](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/PROJECT_BRIEFING.md)读取对应的研究路线或实验主文档，不从风格范例推导事实。

## AI 使用入口

| 当前任务 | 读取本指南的部分 | 同时提供的事实 |
|---|---|---|
| 规划整篇或压缩篇幅 | 篇幅规则与参考样本、当前论文的正文与附录分配 | 当前稿件、Research 研究范围、已接受证据与目标年度指南 |
| 起草某一节 | 科研写作风格、证据与措辞、写作任务提示词 | 本节问题、实际方法、结果与允许引用的来源 |
| 润色已有正文 | 科研写作风格、证据与措辞 | 原稿及需要保留的术语、数字、条件和引用 |
| 设计或生成图表 | 科研画图风格、按图的用途组织画面、画图任务提示词 | 图的目的、真实资产或数据、比较条件和输出尺寸 |
| 写 caption | Caption 的职责、对应图类 | 已完成图、编码说明、统计口径与支持的有限结论 |

先读取任务所需部分；需要核对某个范例时，再进入末尾的精读来源。无需默认加载全部论文或
实验目录。将指南与本次事实一起交给 AI：**风格决定怎样表达，事实决定能表达什么。**

最小输入可以是下面的简短说明：

```yaml
task: 起草 / 润色 / 绘图 / caption
target: 目标章节或图表；语言；篇幅或最终尺寸
question: 任务、条件与本节要回答的具体问题
method: 实际输入输出；训练与部署路径；符号、坐标和时序
evidence: 来源位置；比较对象与共同设置；指标、样本量、结果和不确定性
limits: 失败、阴性结果、未测试条件与计算成本
```

字段按任务取用，未知项明确留空。缺少结果时可以完成问题、已知方法和图的布局；结果句保留
`[MISSING: 具体事实]`，证据图保留明确标注的空位。不得补造数据、轨迹、引用、模块、失败原因
或新颖性。缺项清单放在给作者的说明中，最终投稿正文和图表不保留未解决占位。

## 篇幅规则与参考样本

### 官方要求与年度边界

核验日期：**2026-10-16**。以下明确规则依据 [CVPR 2026 Author Guidelines](https://cvpr.thecvf.com/Conferences/2026/AuthorGuidelines)。
[CVPR 2027 CFP](https://cvpr.thecvf.com/Conferences/2027/CallForPapers) 已发布，但本次访问
[2027 Author Guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines) 仍未取得细则。
2027 正式指南发布后须重新核对；模板来源与配置只在[模板说明](../CVPR_TEMPLATE.md)维护。

| 部分 | 已核实要求 | 写作时执行 |
|---|---|---|
| 正文 | 最多 8 页，含图表，使用官方模板；超页或不合模板会直接拒稿 | 标题、摘要、公式、caption 等均计入；用编译 PDF 检查正文最后一页 |
| 参考文献 | 可另占页，但超过正文上限的页面只能含被引用的参考文献 | 不能借参考文献额外页放方法、实验或附录 |
| 补充材料 | 可选；审稿人被鼓励阅读，但没有义务阅读 | 超出正文的附录单独提交；核心方法与支持主要结论的比较留在正文 |
| 补充 PDF 格式 | 清晰、整洁即可，可用 CVPR 双栏，也允许单栏；匿名要求同样适用 | 字号按可读性选择，视频及其他附件也检查身份信息 |
| 补充 PDF 页数 | 2026 公开指南未规定单独页数上限 | 不宣称“2027 已确认无限页”；上传类型和大小按当年系统要求核对 |

本指南将文字附录统称为补充 PDF；视频、代码等也属于 supplementary，但不以 PDF 页数衡量。
主文需要在不依赖补充材料的情况下完成主要论证，正文在对应位置指向附录的具体节、表或图。

### 代表论文的实际篇幅

以下为 **4 篇 CVF 官方发表版**的逐页核对，非匿名投稿版，也不是全会平均统计。
VGGT 为 Best Paper，Navigation World Models 为 Best Paper Honorable Mention，奖项见
[CVPR 2025 官方名单](https://cvpr.thecvf.com/Conferences/2025/BestPapersDemos)；另两篇是方向相关样本，
不据录用或篇幅推断审稿分数。

| 论文 | 正文页数 | 主 PDF 总页数 | 独立补充 PDF 总页数 |
|---|---:|---:|---:|
| [VGGT，CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.pdf) | 8 | 13 | [8](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Wang_VGGT_Visual_Geometry_CVPR_2025_supplemental.pdf) |
| [Navigation World Models，CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Bar_Navigation_World_Models_CVPR_2025_paper.pdf) | 8 | 11 | [6](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Bar_Navigation_World_Models_CVPR_2025_supplemental.pdf) |
| [CoT-VLA，CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/papers/Zhao_CoT-VLA_Visual_Chain-of-Thought_Reasoning_for_Vision-Language-Action_Models_CVPR_2025_paper.pdf) | 8 | 12 | [1](https://openaccess.thecvf.com/content/CVPR2025/supplemental/Zhao_CoT-VLA_Visual_Chain-of-Thought_CVPR_2025_supplemental.pdf) |
| [PointWorld，CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_PointWorld_Scaling_3D_World_Models_for_In-The-Wild_Robotic_Manipulation_CVPR_2026_paper.pdf) | 8 | 15 | [25](https://openaccess.thecvf.com/content/CVPR2026/supplemental/Huang_PointWorld_Scaling_3D_CVPR_2026_supplemental.pdf) |

主 PDF 总页数包含参考文献，PointWorld 还含致谢；其第 9–15 页不是附录。
补充总页数包含其自身参考文献：VGGT 的补充参考文献从第 5 页开始，PointWorld 的第 24–25 页为参考文献。
CoT-VLA 的 1 页补充 PDF 还说明了 rollout 视频，因此短 PDF 不代表补充材料少。
可借鉴的是正文的取舍与补充材料的检索性，不能把附录长短当作质量或录用标准。

## 当前论文的正文与附录分配

### 适用对象与事实入口

这是基于现有[主稿](../../main.tex)和[六个分节](../../sections/)制定的**写作方案**，未执行正文搬移或创建附录稿。
[结果说明](../../results/INDEX.md)与[实验章](../../sections/experiments.tex)明确现稿为历史候选、数值仍 pending。
其固定 SE(3)／flow／单向桥设计，以及旧实验章的 Q1–Q5，不等于当前研究已定型。

改稿时按 [Research 项目入口](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/PROJECT_BRIEFING.md)
读取[完整 Q1–Q3 Study 研究路线](https://app.notion.com/p/3ed7e1a2132381b2a87ef2b071cdff78)：
Q1 是历史编码，Q2 是未来表示与预测粒度，Q3 是世界—动作主干与信息流。
下表为该范围安排内容，Q2 获得最多结果篇幅；最终 SE(3)-WAM 实例由比较选择。
当前实验事实继续由[研究接续入口](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/experiments/40_experiment_mainline_cn.md)
路由，不在指南复制运行状态、预算或结果。本方案不新增实验授权。

### 8 页正文预算

页数为最终双栏版面的等效面积，**已包含该部分的图表、公式、caption、标题与留白**。
建议页序用于组织阅读，不用硬分页固定浮动体；最终以编译结果为准。

| 正文内容与现有落点 | 预算（页） | 建议页序 | 必须交代的内容 |
|---|---:|---|---|
| 标题、摘要、Introduction 与问题图；`main.tex`、`sections/introduction.tex` | 1.15 | 1–2 | 观测—执行错位与动作级问题；统一预算下的 Q1–Q3 Study；贡献按实际证据填写，teaser 不预画胜出结果 |
| Related Work；`sections/related_work.tex` | 0.45 | 2 | 按历史信息、未来表示、世界—动作交互组织比较；区分辅助监督、在线预测、联合生成 |
| 共同问题定义、Benchmark 与评价协议；`sections/benchmark.tex`及方法中的时间定义 | 1.00 | 2–3 | 物理时间、输入与特权标签边界、核心任务与成功口径、配对及 split 单位、主要动作指标和共同预算 |
| 可替换设计空间；`sections/method.tex` | 1.40 | 3–4 | Q1 约 0.30、Q2 约 0.60、Q3 约 0.50 页；共同接口、训练／推理信息与梯度路径；给出足以理解比较的结构图和关键定义 |
| Q1 历史编码结果；`sections/experiments.tex`重组 | 0.70 | 5 | 正式编码比较、参考未来目标／主干、历史独有信息的动作级诊断；GT 信息对照与实际视觉输入分开 |
| Q2 未来表示与粒度结果；同上 | 1.45 | 5–7 | 报告 target-only、context-only、统一粒度、异粒度等候选的实际对照；表示误差、接触时间／相对位姿、安全与任务结果相互对应 |
| Q3 主干与信息流结果；同上 | 0.90 | 7–8 | 主干组织及信息路径的系统比较；组件消融解释辅助监督、在线使用、联合生成，不能代替主干研究 |
| 交叉复验、选出实例、成本与泛化；同上 | 0.70 | 8 | Q2 改变后回访 Q1、Q3 改变后检查表示排序；实际选出实例与强基线的动作表现、成本和已完成的外部证据；保留改变结论的失败与负结果 |
| Limitations and Conclusion；`sections/conclusion.tex` | 0.25 | 8 | 总结已支持发现、适用条件与未覆盖范围；不新增能力或实验结果 |
| **合计** | **8.00** | **1–8** | **参考文献另计** |

Q2 的设计与结果合计约 **2.05 页**。若“目标细、相关环境粗”没有稳定收益，正文报告条件或负结果，
调整实例化主张；不要靠把对照移入附录维持预设结论。Q1 与 Q3 同样保留正式研究，不压缩成 Q2 的附带消融。

正文的图表先按 **3–4 幅图、3 张研究结果表**设计，再按实际信息密度调整：问题图、可替换设计与信息流图、
紧凑任务概览、Q2 的预测—动作对应案例／曲线；Q1、Q2、Q3 各一张可独立理解的核心比较表。
选出实例和关键成本可并入对应表，不重复抄写同一结果。统计图与案例只能使用真实结果；缺项先保留设计说明。

### 12 页补充内容的起步方案

以下 **12 页是内容预算，不含补充参考文献**，不是会议要求或必须填满的目标。
各节只展开已完成且与正文相关的内容；证据不足时缩短，不为凑页数扩展任务。
采用独立补充 PDF，首页列目录和正文节／图／表的对应关系，面积计入 A 节。

| 附录节 | 预算（页） | 具体内容 | 与正文的边界 |
|---|---:|---|---|
| A．完整数据与 Benchmark 协议 | 2.0 | 任务几何、事件阈值、传感／控制时钟、split 与反事实组、公开／特权字段、标签有效性和回放说明 | 正文保留影响公平性与结论的时间、信息、成功判据和统计单位 |
| B．实现、数学与训练配置 | 2.0 | 各候选结构与维度、坐标／旋转／对称性约定、损失与标签处理、训练阶段、超参数、硬件和 checkpoint 选择 | 正文保留可替换接口、关键目标、信息／梯度路径及机器人接触后的预测条件 |
| C．Q1 完整结果与历史诊断 | 1.5 | 逐任务／seed、窗口与采样间隔、遮挡与方向歧义、历史交换、参考配置和信息输入对照 | 正文保留编码主比较及支持历史用途的关键动作证据；EEF 历史与严格无记忆分开 |
| D．Q2 完整表示与粒度研究 | 2.0 | 各物理时域、区域／粒度、target/context、预测误差与动作级误差、校准及失败分层 | 正文保留主表示比较、动作收益与重要反例；GT oracle 不写成视觉能力 |
| E．Q3 扩展比较与交叉复验 | 1.5 | 全部已完成主干／信息流配置、匹配预算、辅助／在线路径、适用的 zero／swap／noise／oracle、保留组合的复验 | 正文保留主干研究、关键机制证据与任何会改变设计排序的交互效应 |
| F．成本、规模与外部协议 | 1.5 | 模块及端到端 p50/p95、action age、显存、实际规模比较、已完成的原生外部／静态／实机协议与细分结果 | 固定延迟条件与实测时延分开；支持摘要主张的外部证据须在正文有结果摘要，各协议不混成 DB0 分数 |
| G．失败、可视化与视频说明 | 1.5 | 同物理时间的预测／实际对齐、完整 rollout、失败选择规则、匿名视频文件索引 | 正文保留影响主结论的失败；补充媒体随投稿文件提供，不靠外链扩充内容 |
| **合计** | **12.0** | **之后按需列补充参考文献** | **按证据量增减** |

### 对现稿的具体取舍顺序

1. **先对齐论证。** 将旧实验 Q1–Q5 改按当前 Study 的 Q1–Q3 组织；Introduction 与摘要由
   “固定候选具备哪些模块”转为“比较哪些设计、得到什么有条件的发现”。缺结果处保持 pending。
2. **重组方法。** 现有物理时间、标签有效性、可见信息可进入共同定义；SE(3)、dense flow、
   uncertainty、one-way bridge 只在其实际候选或最终选出实例中说明。不能从旧稿推定它们均为必选组件。
3. **优先移细节。** 将现有 `tables/implementation.tex` 的完整配置放入附录 B，正文以短段保留共同条件；
   `tables/positioning.tex` 的完整文献矩阵放附录或精简，正文保留最相关比较轴及引用。
   `sections/benchmark.tex` 的逐事件阈值、全字段与 replay 细节归附录 A，正文保留口径摘要。
4. **重组结果表。** 将 `tables/main_results.tex`、`tables/mechanism_results.tex` 视为旧候选表结构，
   按 Q1–Q3 的真实比较重排；保留强匹配基线、与主张有关的未来 oracle、动作指标、安全与成本。
   `tables/external_results.tex` 只有实际完成并支持正文主张的摘要进入正文，完整原生协议放附录 F。
5. **最后压缩表达与图表。** 合并重复定义、逐行复述和重复结果，缩减不必要面板；不靠缩字体、
   改模板边距或把核心比较移入附录满足 8 页。若仍超页，减少次要案例和扩展细节，保持完整 Study 的范围。

五个 seed、每 cell 100 次 rollout、180 次实机等旧稿数字是历史计划，不能随篇幅方案写成完成事实。
direct regression、P-Detach 或其他候选也不因旧稿采用而成为已测赢家。
结果接续遵循[结果说明](../../results/INDEX.md)，不手改生成的 `results.tex`；科学事实仍链接 Research 唯一证据。

## 科研写作风格

### 叙事与段落

从可观察的任务问题开始，用足够具体的条件界定它，再说明方法改变了什么、怎样检验、结果
支持到哪一步。Introduction 的常用推进是：**情境与困难 → 相关路线的能力和缺口 → 本文思路
与比较对象 → 证据与贡献边界。** 各部分可合并或重排，段落数量随论证需要决定。

一个段落推进一个主要判断。实验段落先提出问题或给出已支持的结论，随后交代比较、证据和
条件，再解释它回答了什么。保留因果、条件和转折关系，避免把每个段落写成同样的填空模板。
不按表格顺序逐行复述数字，不在段末突然引入一个未经展开的新贡献。

英文优先用明确主体、具体动词和已有术语。使用 *We compare / predict / condition / evaluate*
说明动作，使用 *under / conditioned on / measured by* 说明条件。删去没有证据作用的
*remarkable, powerful, revolutionary, comprehensive* 等评价词。保留准确技术术语，减少长串
形容词、被动名词化和反复出现的宣传性转折。

### 各章节的职责

| 章节 | 要完成的论证 | 写作时检查 |
|---|---|---|
| Title / Abstract | 用任务、关键改变、主要证据与范围交代论文价值 | 标题与已获得贡献一致；摘要数字可追溯到正文；方法意图与机制结论分开 |
| Introduction | 界定具体困难、相关缺口、本文改变及验证方式 | 不声称整个领域失效；每项贡献有对应证据；设计候选不写成结果 |
| Related Work | 按本研究的比较轴连接路线，交代能力、信息与任务条件 | 不逐篇堆名单；区分监督、在线预测、动作生成和规划 |
| Method | 先定义问题和接口，再解释实际计算与训练／推理路径 | 首次定义符号；说明可见信息、坐标、时间和输出；不补造模块 |
| Experiments | 每个小节回答一个问题，报告比较、结果与不确定性 | 共同条件可核对；指标与论点匹配；机制判断有对应的比较 |
| Discussion / Limitations | 解释收益来源、失败和证据边界 | 区分观察与推测；未测试条件不写成已知性能边界；阴性结果保留范围 |
| Conclusion | 回答开篇问题，概括已支持的贡献与条件 | 不新增结果、能力或范围，不重新宣传未验证的机制 |

方法名、符号和实验轴在全文保持一致。不要把近义词当作可以互换的科学对象：未来监督、
在线预测和 oracle 未来；action-conditioned prediction、action generation 和 planning；
per-point flow、物体刚体 SE(3) 状态和严格等变性；预测误差、动作误差和闭环任务结果，均须
分别命名。耗时也要区分模块、规划和完整感知到执行周期。

## 证据与措辞

| 句子承担的功能 | 可用措辞 | 需要的依据 |
|---|---|---|
| 定义与实现 | *We define / introduce / implement…* | 实际对象、接口或实现 |
| 直接测量 | *achieves / reduces / increases… under…* | 指标、比较对象、数值与测试条件 |
| 受控比较支持设计 | *This comparison supports… within…* | 写明共同设置和改变因素，结论限定在比较范围 |
| 尚待验证的解释 | *suggests / is consistent with / may…* | 与观察兼容，并明确是解释而非已识别机制 |
| 理论性质 | *We prove… / is equivariant under…* | 定义、假设、命题和证明；性能实验不能替代 |
| 阴性或不确定结果 | *We did not observe a clear improvement… in…* | 估计、不确定性和已测试条件 |

“首次”“SOTA”“robust”“generalizable”“real-time”都需给出明确范围与相应依据。引用紧跟它
支持的判断，不让一个文献引用承担附近所有主张。普通消融不自动识别因果；相关性不证明替代
真实评估可靠；没有统计显著差异不证明等价。只在确有相应统计分析时使用 *significant*。

数字保持指标、单位、分母、样本量和汇总方式。成功率差值用 *percentage points*；相对变化
另给基准。区分 task completion score、success rate、几何误差和视觉质量。效率写清硬件、
batch、统计量和测量边界；端到端时延说明包含哪些阶段，不以 FLOPs 直接代替执行时延。

### 英文改写示例

以下是原创的假设性句型，不是论文原句或本项目结果。方括号必须由真实事实填写；只采用与
实际方法、证据匹配的句子。

**笼统问题变为具体研究对象。**

Bad: “Existing VLA models cannot handle dynamic environments.”

Better: “We study [task] when [target state] changes during [observation-to-execution delay].
Under this condition, [observed failure] motivates evaluating [specific capability].”

**机制宣称变为有条件的比较结论。**

Bad: “The SE(3) representation causes better control.”

Better: “Under matched [data, capacity, and inference budget], replacing [representation A]
with [representation B] changes [metric] by [estimate and uncertainty]. This comparison
supports [specific design choice] within [tested conditions].”

**未来信息分清训练与部署。**

Bad: “Our policy uses future information to predict actions.”

Better: “During training, [future observation] supervises [output]. At inference,
[future representation] is predicted from [available inputs] and supplied to
[action-generation or planning step].”

该句型只适用于实际在线使用预测的系统；若未来仅作辅助监督，应说明其训练作用和实际部署
输入。辅助支路在部署中是否存在或执行，按实际实现表述，不预设增加预测步骤或移除支路。

**百分比变化给出基准与口径。**

Bad: “Success improves by [difference]%.”

Better: “Success increases from [a]% to [b]%, a gain of [b − a] percentage points across
[number of trials]. We report [uncertainty estimate] for this comparison.”

**阴性结果限定在已测试条件。**

Bad: “The additional reasoning module does not work.”

Better: “For [tasks] under [budget], adding [module] yielded [estimate and uncertainty]
in [metric], providing no clear evidence of improvement in these conditions.”

**效率形容词变为可复现测量。**

Bad: “Our method is fast and suitable for real-time deployment.”

Better: “On [hardware] with [batch size], [computation] takes [latency statistic].
The full observation-to-action cycle takes [latency], including [stages], under
[measurement conditions].”

## 科研画图风格

### 视觉语法

先定义图要回答的问题，再选择图类和编码。让同一物体、场景、方法或变量贯穿面板；文字、
边框、曲线和实体颜色共同说明其身份。布局以阅读顺序、比较关系和真实时序为依据，减少无关
模块、重复图例、装饰图标和交叉箭头。图中只画实际路径或明确标注的概念示意。

下面是可调起点，**不是源论文精确采色或会议规定**。已有稿件有一致风格时优先沿用。

```yaml
background: "#FFFFFF"
panel_background: "#F2F2F2"
semantic_colors:
  observation: "#0072B2"
  prediction: "#E69F00"
  action: "#7B61A8"
  ground_truth: "#4D4D4D"
  failure_annotation: "#D55E00"
typography:
  labels: Arial / Helvetica / DejaVu Sans  # 选一种可用字体
  label_pt: 8–9
  panel_title_pt: 9–10
lines:
  axes_pt: 0.7–0.9
  primary_curve_pt: 1.2–1.6
  auxiliary_pt: 0.5–0.8
width: 按实际论文模板的单栏或双栏宽度设置
```

将字号与线宽区间选为具体数值后写入绘图代码。数值按最终放置尺寸计算，不按大屏预览尺寸
判断。白底、少量浅灰分区、统一留白；结构、文字、
坐标和曲线保持矢量，真实照片保留其内容。流程图通常减少阴影和渐变；统计图避免装饰性 3D
柱图。复杂信息优先分面，避免靠缩小字号塞入一个面板。

**颜色分工。** 语义图的颜色对应观测、预测、动作等物理含义；比较图的颜色对应方法身份，
图例明确说明并跨同类图复用。不要在同一图中让颜色同时代表方法、模态与时间。坐标 triad
可另用 x／y／z 红／绿／蓝，但始终附轴名和 frame 名；用线型、marker 或文字补充颜色区分。

**箭头分工。** 流程图实线表示数据／计算传递，虚线表示训练监督，带文字的回环表示执行反馈。
冻结和可训练状态用明确标签。空间箭头另标轴名、`Δp`、旋转或相应时间段；图例分清功能轴、
坐标轴与运动箭头。箭头接在实际输入输出端点，不能以连线暗示不存在的信息依赖或因果证据。

**几何与时间。** 定义 object、world、camera、EEF frame；若采用 `T^W_O`，明确其映射是
object → world，并检查全文符号约定。平移标 m／cm，旋转标 deg／rad；时刻、预测 horizon
和动作生效时刻分别标明。多帧比较按实际时间对齐，不把等帧数当作等物理时间。

**数据编码。** 数值横轴按真实间距绘制；使用 log 刻度时明确标注。气泡图建议面积与参数量
成比例并给图例；若使用半径或直径编码，则明确映射。条形图通常从零起；局部截断或对数轴
须可见且合理。曲线平滑、样本排序、归一化和案例选择有实际依据并交代，不能用于制造优势。

## 按图的用途组织画面

| 图的用途 | 画面组织 | 输入与需要回答的问题 |
|---|---|---|
| 首页问题与贡献 | 一个场景贯穿当前观测、未来条件和动作；通常 2–3 个主要面板 | 问题发生在哪里，本文改变什么？场景是实测还是概念示意；不预画未经验证的成功 |
| 方法与信息流 | 实际输入 → 表示 → 预测／动作 → 执行；必要时放大一个机制 | 哪些信息何时可见，未来用于训练监督、在线预测还是动作条件？提供实际模块、依赖和训练／部署路径 |
| SE(3) 与接触几何 | 同一物体／EEF 上叠 frame、相对变换、接触点与时间 | 每个量在哪个 frame 定义？提供标定、姿态和接触数据；示意与预测／实测分开 |
| 条件与机制对照 | 方法／条件分行，物理时间分列；相机视角一一对应 | 改变了哪个因素？共同状态、目标、预算与改变因素来自真实协议，不能靠排版声称已控制 |
| 受控设计比较 | 按一个设计轴分组的点图与区间，或带明确基线的条形图 | 哪一改变对应什么结果？提供配置、配对任务、样本量与不确定性；递增模块不自动成为析因实验 |
| 性能与成本 | 时域／延迟曲线与质量—成本散点；分别展示数据与模型规模 | 收益在哪些条件和预算下成立？区分计算量、模块时延、端到端时延 |
| 预测与闭环价值 | current／predicted／actual 对齐，局部失败标注与任务结果对应 | 预测误差是否联系到执行结果？预测质量、闭环改善与相关性分别需要证据 |

定性图同时展示初始条件、真实时间与必要上下文。选择案例时说明选择规则；整体结果用定量
统计支持，不把一张好看的 rollout 当作通用能力。局部框只强调有证据的误差，原图仍保留
场景；几何位置、形变、接触、轨迹与曲线不由 AI 美化补造。

## Caption 的职责

让读者在不逐段回读正文时，能理解这张图的对象、条件、编码和有限结论。通常包括：图的目的
或已支持的观察；各面板含义；比较条件、符号、坐标与单位；适用范围。示意图说明连线和输入
的意义，统计图再说明 `n` 的采样单位、汇总方式、区间计算和指标方向。

下面是句型，各部分按图类选用，不能为了填齐模板补造统计或结果：

```text
Figure [X]. [Purpose or supported takeaway]. (a) [Panel meaning]. (b) [Panel meaning].
[Colors / lines / symbols] denote [defined quantities]. We compare [methods or conditions]
under [shared settings]. [Metric and units] are aggregated over [n and sampling unit];
[interval] is computed by [actual procedure]. The comparison supports [limited conclusion]
within [tested conditions].
```

Caption 不复述整套网络细节，不用泛泛的 “Results of our method” 代替信息，也不把 score、
成功率、几何误差和视觉质量互换。图本身若不足以证明机制，caption 保持观察层面的表述。

## 写作任务提示词

```text
请按《AI 辅助 CVPR 论文写作与科研画图指南》的相关部分，完成本次指定章节的起草或润色。
写作类型、语言、篇幅和事实见下方输入。

从具体问题推进到实际方法和证据，保持术语、符号、指标、条件与引用一致。
主张强度与证据匹配，分清训练监督、部署输入、预测、动作生成和规划。
只借鉴参考论文的论证方式，不复制措辞，不移植其方法、结果或新颖性声明。
润色时保留原稿事实与结论强度；疑点单独列出，不用文字优化暗改科学含义。
缺事实时完成可独立写出的部分，必要位置用 [MISSING: 具体事实]；不生成虚构结果或引用。
整篇任务按“当前论文的正文与附录分配”安排内容，报告各节预算与附录去向；
Q1–Q3 按当前 Research 定义，保持核心比较在正文，不把历史候选或预算写成结果。

先交付可编辑正文，再简短列出关键缺项或超出证据的主张；不要输出冗长的逐步思考。
本次输入：[目标与篇幅] [问题和条件] [实际方法] [结果和比较] [限制与成本] [允许引用来源]
```

## 画图任务提示词

```text
请依据下方事实与资产，按本指南设计 [图的用途]。
先明确这张图回答的问题，再给出面板、实体、编码、坐标、时间和比较条件。
使用已存在的模块和真实数据；缺少资产时只完成可核对的布局或明确标注的示意。
按实际论文尺寸统一字体、线宽与图例，颜色含义跨面板一致。
保留原照片和科学数据；不得生成貌似真实的实验曲线、姿态、接触或成功案例。

有数据时交付可编辑绘图源文件及 SVG/PDF，照片与矢量标注分开保存；
只请求设计时交付图的 brief。两种情况均给 caption 和简短缺项说明。
检查数据对应、语义、最终尺寸可读性和导出文件可用性。

图的 brief：
- purpose / claim：要回答的问题；已有证据支持的结论，未知则留空
- assets / data：真实图像、坐标、结果表及来源位置
- comparison：方法与改变因素；实际共同设置、样本量及统计口径
- panels / time：各面板内容；行列关系、相机和真实时间戳
- geometry / encoding：frame、变换方向、单位；颜色、箭头与线型的含义
- output：按模板确定的尺寸；所需源文件和导出格式
```

## 交付前的直接检查

- 篇幅：正文最后一页不超过第 8 页，额外主 PDF 页面只含参考文献；独立补充 PDF 与正文互相指向，核心论证不依赖审稿人阅读附录。投稿前按当年正式指南复核。
- 正文：问题、方法、实验相互对应；数字与引用可追溯；术语、条件、时序和结论强度没有漂移。
- 图表：数据和资产与源材料一致；面板、时间、frame、单位与箭头含义完整；统计图注明采样与
  汇总口径，已有区间注明计算方法，未估计区间时说明。
- 文件：按最终论文尺寸阅读，文字、线条和图例可辨；导出可打开；保留生成源文件和数据来源。

必要检查通过即可交付。新数据或方法变化后，重新检查其影响的正文和图表，不用同一组机械
检查反复证明已经通过的部分。

## 精读来源按用途路由

这里只链接抽象规则的主要范例；论文事实与具体图页观察继续在精读笔记维护。

| 需要核对的风格 | 定向读取 |
|---|---|
| 从任务缺口到方法用途；性能与成本 | [NWM](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#navigation-world-models) |
| 概念对照；实验问题与证据对应 | [CoT-VLA](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#cot-vla)、[Cosmos Policy](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#cosmos-policy) |
| 研究问题与整篇证据总览 | [World-In-World](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#world-in-world) |
| 同实体几何方法图；受控消融 | [PointWorld](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#pointworld) |
| 全局计算路径与关键机制放大 | [LPWM](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#latent-particle-world-models) |
| 物体上的功能轴；几何公式与支路对齐 | [RoboTwin](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#robotwin)、[RoMan-4D](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#roman-4d-与-gem-4d) |
| 同场景条件对照；阴性结果 | [SimLingo](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#simlingo)、[DAPL](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#dapl) |
| 预测与实际对齐；评估关联的边界 | [Cosmos Policy](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#cosmos-policy)、[IWS](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/research_notes/cvpr_wam_vla_writing_2026_10_13.md#interactive-world-simulator) |
