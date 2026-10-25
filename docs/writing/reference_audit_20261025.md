# 参考文献核对与取舍建议

核对日期：2026-10-25。对象为根目录 `references.bib` 的全部 110 条，以及当前英文正文、附录和中文稿中的引用。当前源码使用 71 个引用键，39 条只存于文献库。下列增删与正文措辞调整供作者讨论，本轮已实施的修改限于出版信息、书目信息与阅读 PDF。

当前覆盖已经足够广，主要问题是部分出版信息过时、同一论点的举例过密，以及若干比较句对已有方法概括过强。建议优先补齐最直接的方法来源、压缩重复例子，并将差异准确落到“目标 SE(3) 与全场景稀疏 3D 流的角色分工及监督方式”。

## 已替换的 arXiv 引用

| 引用键 | 论文或方法 | 更新后来源 |
|---|---|---|
| `pi05` | π0.5 | [CoRL 2025，PMLR 305，17–40](https://proceedings.mlr.press/v305/black25a.html) |
| `ahead` | AHEAD / Intercepting the Future | [CoRL 2026，已录用](https://arthurjakobsson.com/publications/) |
| `domino` | DOMINO / PUMA | [ECCV 2026，314–333](https://link.springer.com/chapter/10.1007/978-3-032-37592-6_18) |
| `dynamicvla` | DynamicVLA | [NeurIPS 2026，已录用](https://neurips.cc/virtual/2026/poster/156061) |
| `fastwam` | Fast-WAM | [NeurIPS 2026，已录用](https://neurips.cc/virtual/2026/poster/149922) |
| `physmani` | PhysMani | [ECCV 2026，20–39](https://link.springer.com/chapter/10.1007/978-3-032-37029-7_2) |
| `docir` | DOCIR | [IROS 2025，15873–15879](https://doi.org/10.1109/IROS60139.2025.11246704) |
| `moge2` | MoGe-2 | [NeurIPS 2025，35928–35959](https://proceedings.neurips.cc/paper_files/paper/2025/hash/336572db3e99930814d6b328d4220cb6-Abstract-Conference.html) |
| `wog` | World Guidance | [ICML 2026，115917–115933](https://proceedings.mlr.press/v306/su26c.html) |
| `dawn` | Pixel Motion Diffusion is What We Need for Robot Control | [CVPR 2026，23663–23672](https://openaccess.thecvf.com/content/CVPR2026/html/Nguyen_Pixel_Motion_Diffusion_is_What_We_Need_for_Robot_Control_CVPR_2026_paper.html) |
| `fofpred` | FOFPred | [CVPR Findings 2026，按作者正式引用格式](https://fofpred.github.io/) |
| `flowdreamer` | FlowDreamer | [RA-L 11(3)，2466–2473，2026](https://doi.org/10.1109/LRA.2026.3653273) |
| `objectforesight` | ObjectForesight | [ECCV 2026，437–453](https://link.springer.com/chapter/10.1007/978-3-032-37098-3_24) |

AHEAD、DynamicVLA、Fast-WAM 保留“Accepted for publication”状态，不填尚未取得的论文集卷页。FOFPred 明确标为 Findings，不写成 CVPR 主会。ObjectForesight 的会议展示标题省略了 Future，但 Springer 正式论文仍含 Future，按正式出版标题保留。

已是会议论文、但链接仍指向 arXiv 的 NWM、RTC、SE3-Nets、DSR、Im2Flow2Act、VPP、HiF-VLA、RAFT-3D、VGGT、D4RT 已改为正式来源；其他已核实条目补充可用的卷页、DOI 或官方入口。π0.5 与 Octo 的作者起始顺序按正式论文集纠正，保留文献库已有的长作者列表省略习惯。

PMLR 论文集的出版年份与会议举办年份有时不同。本轮按官方 BibTeX 统一了 DSR（2021）、PerAct（2023）、OpenVLA、Im2Flow2Act、3D Diffuser Actor、General Flow（后四者均为 2025）。这不改变它们分别属于 CoRL 2020、2022、2024 的事实。

kPAM 同样区分会议年与出版年：属于 ISRR 2019，Springer 论文集出版于 2022；已补齐正式卷页、DOI 和出版商链接。

仍有 28 条保留 arXiv：本轮未找到足够的正式出版依据。[DINOv3 在 Meta 官方出版页](https://ai.meta.com/research/publications/dinov3/)仍列为技术报告；不能把使用 DINOv3 的会议论文或同名方法当成它的正式版本。两个 OpenWAM 条目作者、标题和 arXiv 编号不同，也不能仅凭同名合并。

## 当前引用结构

| 需要交代的问题 | 当前情况 | 建议 |
|---|---|---|
| 运动目标、历史与预测 | PUMA、DynamicWAM、AHEAD、DBC-TFP、PhysMani 等已覆盖 | 保留直接比较方法；补回一个早期学习式动态抓取工作即可 |
| 低延迟执行与动作块 | RTC、DynamicVLA、VLASH、BID、SmolVLA、StreamingVLA、Chronos 较密集 | 保留实际使用的执行来源与最直接对照；压缩重复异步例子 |
| 未来监督与低开销部署 | UWM、UVA、DreamVLA、Fast-WAM、WoG 等已覆盖 | 补 FLARE；区分训练目标、在线保留的 token 和是否生成未来输出 |
| 几何运动表示 | 点轨迹、3D 流、关键点、SE(3) 已覆盖 | 每种表示留代表作；保留能界定角色分工的 DOCIR |
| 可复现依赖 | MAE、DINOv3、flow matching、DROID、MuJoCo、robosuite、真机感知组件均有引用 | 按实际使用保留，不因与贡献距离远而删掉依赖来源 |

## 建议增加或重新启用

1. **优先补 FLARE，CoRL 2025。** 它将策略内部特征与未来观测的潜表示对齐，直接属于本文“预测监督改善动作表征”的方法脉络。放在 Related Work 第二段，并与 Fast-WAM 一起界定：本文的新意不是首次使用低开销未来监督，而是监督的几何内容和按角色分配的精度。FLARE 仍有新增的 future tokens，不宜写成完全零推理开销。[正式论文](https://proceedings.mlr.press/v305/zheng25a.html)
2. **建议重新引用现有 `akinola2021dynamic`。** 该工作已经结合运动预测、可达性、抓取质量和实时规划，适合连接经典截获系统与近期动态 VLA；当前第一段容易从传统控制直接跳到 2025–2026 方法。它已经在文献库中，无须新增条目。[作者项目页与论文](https://crlab.cs.columbia.edu/dynamic_grasping/)
3. **可选重新引用现有 `dsr`。** 如果保留“结构化场景动力学”这一比较，DSR 比继续增加新近 WAM 名称更能说明场景级 3D 动力学的前史。可以替换一个重复的刚体动力学例子，不必净增加引用量。[正式论文](https://proceedings.mlr.press/v155/xu21b.html)

不建议为了覆盖广度重新塞入 NWM、DreamerV3、TD-MPC2、V-JEPA 2 或更多通用 VLA。它们只有在正文实际讨论导航、潜空间规划、强化学习或相应骨干时才需要。

## 建议优先精简

以下是对正文取舍的建议，不是本轮已删除的条目。

| 优先级 | 候选 | 理由与保留条件 |
|---|---|---|
| 高 | DynamicManip | 主要支撑动态数据合成；当前没有专门讨论该问题，单独一句较偏离方法主线 |
| 高 | DELE-w0.5、Efficient-WAM | 在本段只承担“紧凑 latent”例子，已有更直接的预测监督来源可说明该点 |
| 高 | StreamingVLA、Chronos | 若没有使用其执行设计、物理时间表示或实验对照，可从执行段压缩；保留 RTC、DynamicVLA、VLASH 足以解释主要区别 |
| 高 | AffordTrajDP | 与关键点、物体轨迹组中的 kPAM、SPOT 等作用重叠，可先去掉这一举例 |
| 中 | MaskWAM 与 OA-WAM | mask/slot 分组可选一个代表；若正文要单独比较对象可寻址机制，再同时保留 |
| 中 | GR-1、Seer、VPP | 视频预测作为策略目标的前史不必三个并列，选最贴近本文训练方式的一至两个 |
| 中 | PerAct、RVT、3D Diffuser Actor、DP3 | 作为“3D 输入有用”的同句支撑过密，保留 PerAct 与 DP3；真正实验比较的方法另保留 |
| 中 | ATM、Track2Act、Im2Flow2Act、TraceVLA | 应区分输入历史轨迹、预测未来轨迹与跨域动作接口；删去正文不展开的重复例子 |
| 中 | 3DFlowAction、FlowDreamer、General Flow、PointWorld | 保留 PointWorld；其他根据是否要讨论生成式规划或动作接口选择一至两个 |

**不建议因为重叠而删掉 PUMA、DynamicWAM、Fast-WAM、DOCIR、SPOT、PointWorld 等直接影响贡献边界的工作。** SG-WAM 同时涉及几何表征和训练期未来监督，比一般 WAM 名称更接近当前论点，也值得保留一句准确比较。近期但没有增加独立比较维度的工作可以不引；直接先行工作和实验基线的取舍则应服从正文论点与实际实验。

39 条未被当前源码引用的文献不进入最终 bibliography，删除它们不会缩短论文参考文献页。可以在下一轮定稿时从活跃库清走，但不应把这种清理等同于删减正文引用。

## 比增删更需要修改的三处概括

1. **Introduction 的“历史与预测都会增加执行时延”。** PUMA 的预测分支用于训练；Fast-WAM、WoG 和 SG-WAM 的部署机制也不同。应改为“读取高成本历史输入或在推理时生成未来会增加开销”，并单独说明训练期未来监督。否则同一篇 PUMA 在引言被当作推理代价的例子，在 Related Work 又被说成部署时丢弃预测器，前后不一致。[PUMA](https://h-embodvis.github.io/DOMINO/)；[WoG 方法第 3.3 节](https://arxiv.org/html/2602.22010)；[SG-WAM 方法第 3.2–3.5 节](https://arxiv.org/html/2608.01397)
2. **Introduction 的目标中心方法“blind to surroundings”。** PUMA 包含场景历史光流，不能把它描述为没有周围场景信息。更准确的区别是：这些方法没有以本文的方式，将目标的精确度量位姿与周围场景的稀疏运动分别设置为预测监督目标。[PUMA 原始说明](https://h-embodvis.github.io/DOMINO/)
3. **Related Work 的“这些工作只用一种表示”。** Track2Act 从 2D 轨迹估计刚体变换；FlowDreamer 同时涉及 RGB-D 与 3D scene flow。这些来源不能支撑一概而论的单一表示结论。应将句子收窄到本文真正比较的“按接触角色区分监督精度”，并把 DOCIR 的输入角色划分与本文预测目标的角色分工说清楚。[Track2Act](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/9800_ECCV_2024_paper.php)；[FlowDreamer](https://sharinka0715.github.io/FlowDreamer/)

建议的下一轮规模是：补 FLARE、重新启用 Akinola，先从重复举例中减少约 8–12 篇。总数只是结果，不设硬性配额；每条引用都应对应一个可明确说出的用途。

## 验证与范围

四个论文入口已重新编译；最终日志和 BibTeX 日志未出现错误或未定义引用。另用 `nocite{*}` 编译全部 110 条，覆盖当前没有被正文引用的条目；引用键保持不变。出版信息核对不等于逐篇复现实验，也不验证论文中尚未完成的结果占位。

## 逐条来源索引

下表是本次核对的日期快照。正式来源优先采用论文集、出版商与会议记录；尚未找到正式发表依据的条目保留 arXiv，不能据此断言其永远没有其他版本。1957 年 Smith 条目的书目信息仅取得馆藏索引交叉核对，未取得原始期刊扫描。

| 引用键 | 当前使用 | 核对后出版状态与来源 |
|---|---|---|
| `nwm` | 未引用 | [CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Bar_Navigation_World_Models_CVPR_2025_paper.html) |
| `cotvla` | 未引用 | [CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Zhao_CoT-VLA_Visual_Chain-of-Thought_Reasoning_for_Vision-Language-Action_Models_CVPR_2025_paper.html) |
| `dynamicwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.00793) |
| `dreamzero` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2602.15922) |
| `droid` | 正文 | [RSS 2024](https://www.roboticsproceedings.org/rss20/p120.html) |
| `pi05` | 正文 | [CoRL 2025](https://proceedings.mlr.press/v305/black25a.html) |
| `dreamvla` | 正文 | [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/22d4f952efa13970f0b1ffb22170d416-Abstract-Conference.html) |
| `akinola2021dynamic` | 未引用 | [IROS 2021](https://crlab.cs.columbia.edu/dynamic_grasping/) |
| `act` | 正文 | [RSS 2023](https://www.roboticsproceedings.org/rss19/p016.html) |
| `ahead` | 正文 | [CoRL 2026，已录用](https://arthurjakobsson.com/publications/) |
| `dbctfp` | 正文 | [IEEE Robotics and Automation Letters 2025](https://doi.org/10.1109/LRA.2025.3557746) |
| `dinov3` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2508.10104) |
| `diffusionpolicy` | 正文 | [RSS 2023](https://www.roboticsproceedings.org/rss19/p026.html) |
| `domino` | 正文 | [ECCV 2026](https://link.springer.com/chapter/10.1007/978-3-032-37592-6_18) |
| `dynamicvla` | 正文 | [NeurIPS 2026，已录用](https://neurips.cc/virtual/2026/poster/156061) |
| `fastwam` | 正文 | [NeurIPS 2026，已录用](https://neurips.cc/virtual/2026/poster/149922) |
| `flowmatching` | 正文 | [ICLR 2023](https://openreview.net/forum?id=PqvMRDCJT9t) |
| `libero` | 未引用 | [Advances in Neural Information Processing Systems (Datasets and Benchmarks Track) 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/8c3c666820ea055a77726d66fc7d447f-Abstract-Datasets_and_Benchmarks.html) |
| `mujoco` | 正文 | [IROS 2012](https://doi.org/10.1109/IROS.2012.6386109) |
| `oawam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2605.06481) |
| `physmani` | 正文 | [ECCV 2026](https://link.springer.com/chapter/10.1007/978-3-032-37029-7_2) |
| `pointworld` | 正文 | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_PointWorld_Scaling_3D_World_Models_for_In-The-Wild_Robotic_Manipulation_CVPR_2026_paper.html) |
| `robosuite` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2009.12293) |
| `openwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2610.07922) |
| `affordtraj` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.01603) |
| `dreamwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.04996) |
| `flowwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2607.13017) |
| `dynamicmanip` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.01452) |
| `pactwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2602.15882) |
| `dcwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2607.25918) |
| `dele` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.22067) |
| `longwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2610.10528) |
| `chronos` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2610.13929) |
| `rtc` | 正文 | [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/300ccb2187dedd4edcc07f7e76d8e553-Abstract-Conference.html) |
| `docir` | 正文 | [IROS 2025](https://doi.org/10.1109/iros60139.2025.11246704) |
| `se3nets` | 正文 | [ICRA 2017](https://doi.org/10.1109/icra.2017.7989023) |
| `se3posenets` | 正文 | [ICRA 2018](https://doi.org/10.1109/ICRA.2018.8461184) |
| `dsr` | 未引用 | [CoRL 2020；PMLR 出版于 2021](https://proceedings.mlr.press/v155/xu21b.html) |
| `atm` | 正文 | [RSS 2024](https://www.roboticsproceedings.org/rss20/p092.html) |
| `im2flow2act` | 正文 | [CoRL 2024；PMLR 出版于 2025](https://proceedings.mlr.press/v270/xu25a.html) |
| `tracevla` | 正文 | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/8667f264f88c7938a73a53ab01eb1327-Abstract-Conference.html) |
| `vpp` | 正文 | [International Conference on Machine Learning 2025](https://proceedings.mlr.press/v267/hu25g.html) |
| `hifvla` | 未引用 | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Lin_HiF-VLA_Hindsight_Insight_and_Foresight_through_Motion_Representation_for_Vision-Language-Action_CVPR_2026_paper.html) |
| `foretime` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.20735) |
| `openwam_alpha` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2609.07398) |
| `farneback` | 仅附录 | [Proceedings of the Scandinavian Conference on Image Analysis 2003](https://www.ida.liu.se/ext/WITAS-ev/Computer_Vision_Technologies/PaperInfo/farneback03.html) |
| `foundationpose` | 正文 | [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Wen_FoundationPose_Unified_6D_Pose_Estimation_and_Tracking_of_Novel_Objects_CVPR_2024_paper.html) |
| `sam2` | 仅附录 | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/45c1f6a8cbf2da59ebf2c802b4f742cd-Abstract-Conference.html) |
| `dpflow` | 未引用 | [CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Morimitsu_DPFlow_Adaptive_Optical_Flow_Estimation_with_a_Dual-Pyramid_Framework_CVPR_2025_paper.html) |
| `moge2` | 未引用 | [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/336572db3e99930814d6b328d4220cb6-Abstract-Conference.html) |
| `raft3d` | 未引用 | [CVPR 2021](https://openaccess.thecvf.com/content/CVPR2021/html/Teed_RAFT-3D_Scene_Flow_Using_Rigid-Motion_Embeddings_CVPR_2021_paper.html) |
| `vlash` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2512.01031) |
| `3dflowaction` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2506.06199) |
| `dp3` | 正文 | [RSS 2024](https://www.roboticsproceedings.org/rss20/p067.html) |
| `vggt` | 未引用 | [CVPR 2025](https://openaccess.thecvf.com/content/CVPR2025/html/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.html) |
| `d4rt` | 未引用 | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Zhang_Efficiently_Reconstructing_Dynamic_Scenes_One_D4RT_at_a_Time_CVPR_2026_paper.html) |
| `smith1957` | 正文 | [Chemical Engineering Progress 1957，馆藏索引](https://cir.nii.ac.jp/crid/1574231875295965056) |
| `azuma1994` | 未引用 | [Proceedings of SIGGRAPH 1994](https://doi.org/10.1145/192161.192199) |
| `hove1991` | 未引用 | [American Control Conference 1991](https://www.mit.edu/~nsl/abstracts/robotcatch-abst.html) |
| `baeuml2010` | 正文 | [IROS 2010](https://elib.dlr.de/67146/) |
| `uwm` | 正文 | [RSS 2025](https://www.roboticsproceedings.org/rss21/p015.html) |
| `uva` | 正文 | [RSS 2025](https://www.roboticsproceedings.org/rss21/p074.html) |
| `diffusionforcing` | 未引用 | [NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/hash/2aee1c4159e48407d68fe16ae8e6e49e-Abstract-Conference.html) |
| `dynawm` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2607.02604) |
| `spatialtracker` | 未引用 | [CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/html/Xiao_SpatialTracker_Tracking_Any_2D_Pixels_in_3D_Space_CVPR_2024_paper.html) |
| `groundingdino` | 仅附录 | [ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/6319_ECCV_2024_paper.php) |
| `mae` | 正文 | [CVPR 2022](https://openaccess.thecvf.com/content/CVPR2022/html/He_Masked_Autoencoders_Are_Scalable_Vision_Learners_CVPR_2022_paper.html) |
| `wilddet3d` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2604.08626) |
| `allen1993` | 正文 | [IEEE Transactions on Robotics and Automation 1993](https://doi.org/10.1109/70.238279) |
| `barshalom2001` | 正文 | [Wiley 2001](https://onlinelibrary.wiley.com/doi/book/10.1002/0471221279) |
| `hutchinson1996` | 未引用 | [IEEE Transactions on Robotics and Automation 1996](https://doi.org/10.1109/70.538972) |
| `marturi2019dynamic` | 正文 | [Autonomous Robots 2019](https://doi.org/10.1007/s10514-018-9799-1) |
| `rt1` | 未引用 | [RSS 2023](https://www.roboticsproceedings.org/rss19/p025.html) |
| `rt2` | 正文 | [CoRL 2023](https://proceedings.mlr.press/v229/zitkovich23a.html) |
| `octo` | 未引用 | [RSS 2024](https://www.roboticsproceedings.org/rss20/p090.html) |
| `openvla` | 正文 | [CoRL 2024；PMLR 出版于 2025](https://proceedings.mlr.press/v270/kim25c.html) |
| `pi0` | 正文 | [RSS 2025](https://www.roboticsproceedings.org/rss21/p010.html) |
| `streamingvla` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2603.28565) |
| `bid` | 正文 | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/0d78dd998f7b9ac79604d47a2d79bb0d-Abstract-Conference.html) |
| `smolvla` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2506.01844) |
| `finn2017deep` | 未引用 | [ICRA 2017](https://research.google/pubs/deep-visual-foresight-for-planning-robot-motion/) |
| `dreamerv3` | 未引用 | [Nature 2025](https://www.nature.com/articles/s41586-025-08744-2) |
| `tdmpc2` | 未引用 | [ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/cf73d57b6dcda32b293df7c2d5341f49-Abstract-Conference.html) |
| `dinowm` | 未引用 | [International Conference on Machine Learning 2025](https://proceedings.mlr.press/v267/zhou25t.html) |
| `vjepa2` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2506.09985) |
| `unipi` | 未引用 | [NeurIPS 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1d5b9233ad716a43be5c0d3023cb82d0-Abstract-Conference.html) |
| `susie` | 未引用 | [ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/8ea50bf458f6070548b11babbe0bf89b-Abstract-Conference.html) |
| `gr1` | 正文 | [ICLR 2024](https://proceedings.iclr.cc/paper_files/paper/2024/hash/2c37c5bcef24b9541550261dcd63261b-Abstract-Conference.html) |
| `seer` | 正文 | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/e5b5c402bb7bd5e60bede6961d6fe39e-Abstract-Conference.html) |
| `maskwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2606.13515) |
| `efficientwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2606.10040) |
| `wog` | 正文 | [ICML 2026](https://proceedings.mlr.press/v306/su26c.html) |
| `sgwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.01397) |
| `peract` | 正文 | [CoRL 2022；PMLR 出版于 2023](https://proceedings.mlr.press/v205/shridhar23a.html) |
| `rvt` | 正文 | [CoRL 2023](https://proceedings.mlr.press/v229/goyal23a.html) |
| `3ddiffuseractor` | 正文 | [CoRL 2024；PMLR 出版于 2025](https://proceedings.mlr.press/v270/ke25a.html) |
| `groot` | 未引用 | [CoRL 2023](https://proceedings.mlr.press/v229/zhu23b.html) |
| `3dvla` | 未引用 | [International Conference on Machine Learning 2024](https://proceedings.mlr.press/v235/zhen24a.html) |
| `4dvla` | 未引用 | [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/30b9c38b9ebeee281cd2bc41d39bf0e7-Abstract-Conference.html) |
| `track2act` | 正文 | [ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/9800_ECCV_2024_paper.php) |
| `langtomo` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2505.07817) |
| `dawn` | 未引用 | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Nguyen_Pixel_Motion_Diffusion_is_What_We_Need_for_Robot_Control_CVPR_2026_paper.html) |
| `fofpred` | 未引用 | [CVPR Findings 2026，作者引用格式](https://fofpred.github.io/) |
| `generalflow` | 正文 | [CoRL 2024；PMLR 出版于 2025](https://proceedings.mlr.press/v270/yuan25a.html) |
| `flowdreamer` | 正文 | [IEEE Robotics and Automation Letters 2026](https://doi.org/10.1109/lra.2026.3653273) |
| `kpam` | 正文 | [ISRR 2019；Springer 出版于 2022](https://link.springer.com/chapter/10.1007/978-3-030-95459-8_9) |
| `spot` | 正文 | [ICRA 2025](https://research.nvidia.com/publication/2025-05_spot-se3-pose-trajectory-diffusion-object-centric-manipulation) |
| `objectforesight` | 正文 | [ECCV 2026](https://link.springer.com/chapter/10.1007/978-3-032-37098-3_24) |
| `flownet3d` | 未引用 | [CVPR 2019](https://openaccess.thecvf.com/content_CVPR_2019/papers/Liu_FlowNet3D_Learning_Scene_Flow_in_3D_Point_Clouds_CVPR_2019_paper.pdf) |
| `cotracker` | 未引用 | [ECCV 2024](https://www.ecva.net/papers/eccv_2024/papers_ECCV/html/7890_ECCV_2024_paper.php) |
