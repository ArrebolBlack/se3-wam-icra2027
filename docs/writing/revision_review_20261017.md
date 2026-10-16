# 2026-10-17 图表、附录与引文修订评审

本轮对应三项要求：以 CVPR 实际图页重构科研图，提供英文正文与完整附录的一体版本，依据 Dynamic Manipulation 调研补全相关工作。实验来源沿用[证据路由](evidence_map.md)，不在此重复维护实验事实。

## 图面比较与独立评审

比较材料为 Navigation World Models（CVPR 2025，第 1、6 页）、CoT-VLA（CVPR 2025，第 1、3 页）和 PointWorld（CVPR 2026，第 3、5 页）的实际论文图页。比较维度为科学信息、视觉层级、阅读顺序、版面密度、最终尺寸可读性，以及图注与图面的对应关系。

| 图 | 修订与比较过程 | 最终评审 |
|---|---|---|
| 图 1：交互时序 | 原矩形流程图未通过；改用非对称目标、机械臂和相对接触几何呈现历史、未来及接触关系；明确为概念示意。 | 独立评审通过 |
| 图 2：已实现 D 网络 | 原列表式图未通过；重构为实际三流网络、注意力可见性矩阵和监督路径。新图第一轮仍存在 GT 监督来源、flow-matching 输出及 Euler 路径歧义；第二轮逐项修正。 | 独立评审通过 |
| 图 3：未来监督结果 | 原实验编号堆叠图未通过；改为 15 组语义分组及配对得失面板，保留零结果与不利结果，不补造置信区间。 | 独立评审通过 |

绘图执行由 paper_figures 与 experiment_evidence 分工完成；methods_references 独立比较参考图并审阅最终 PDF 图注。三图最终均被评为在对应的信息解释、版式与字体维度上达到参考图的可比质量。此结论是图面评审意见，不代表会议录用判断。最终正文实际尺寸下的最小图中文字约 8.1 pt；所有图均提供可编辑源与矢量 PDF。

参考原文：[Navigation World Models](https://openaccess.thecvf.com/content/CVPR2025/papers/Bar_Navigation_World_Models_CVPR_2025_paper.pdf)、[CoT-VLA](https://openaccess.thecvf.com/content/CVPR2025/papers/Zhao_CoT-VLA_Visual_Chain-of-Thought_Reasoning_for_Vision-Language-Action_Models_CVPR_2025_paper.pdf)、[PointWorld](https://openaccess.thecvf.com/content/CVPR2026/papers/Huang_PointWorld_Scaling_3D_World_Models_for_In-The-Wild_Robotic_Manipulation_CVPR_2026_paper.pdf)。

## 表格与完整附录

正文保留三张关键表：系统比较、模块组合及历史输入；图 3 承担未来监督结果的主要呈现，删除重复的 Q2 摘要表。附录 A–G 收纳任务定义、实现与预算、完整结果、配对统计、逐任务结果、失败类型及待完成实验设计，共十张表。英文合并版与独立补充材料读取同一套附录源文件。

五张生成式结果表中的 633 个数值单元已对照研究仓库来源与派生计算核验。独立评审检查了全部英文附录表的实际排版；中文表格也经逐页及高分辨率检查。末轮修复了附录首表越过标题，以及中文系统表遗漏的问题。

## 参考文献与文字核验

正文实际引用由 19 篇增至 42 篇，含附录的英文完整稿共引用 43 篇。新增相关工作按动态操作与物理时序、历史与对象信息、未来变量、世界与动作耦合组织；依据 Notion 调研选文，并核验原始论文元数据与论述范围。

上一稿将 OpenWAM-Alpha 基线错引到 Yu 等人的同名可组合框架。现根据官方 Alpha 模型说明改引 Wang 等人的模块化预训练工作（2609.07398）；Yu 等人的工作（2610.07922）保留在 Q3 相关工作中。本方 D 为重新初始化的任务网络，不继承上述预训练主干。

中文稿按 writing-refine-zh 要求先梳理论证、删除冗余辩护，再润色语言，最后复核事实和结论强度。此前缺乏依据的表述及待核实问题集中列于[中文文后核对说明](verification_zh.tex)。本轮没有启动新实验，也没有把计划写成结果。

## 成品核查

- main.pdf：10 页，正文 8 页、参考文献 2 页。
- paper_full.pdf：20 页，包含英文正文、参考文献和 A–G 完整附录。
- supplementary.pdf：11 页，独立附录及其参考文献。
- manuscript_zh.pdf：22 页，中文全文、完整附录及文后核对说明。

四份文档均已编译；日志未出现未定义引用、缺字或超宽盒。英文合并版和中文稿经过逐页视觉核查，末轮更动的页面另行复查。CVPR 2027 正式格式仍须在官方要求发布后确认，当前采用官方 2026 author kit 并配置会议年为 2027。

