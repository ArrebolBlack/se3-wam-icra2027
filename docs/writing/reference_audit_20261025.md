# 参考文献核对与引用取舍

核对日期：2026-10-25。首轮核对根目录 `references.bib` 的全部 110 条；本轮新增 FLARE 后共 111 条。正文与附录合计引用从 71 条减至 63 条，另有 48 条仅存于文献库。本轮仅调整书目与中英文引用标记，正文句子和论述保持不变。

当前引用覆盖动态操作、预测监督、实时执行和几何表示。本轮补入两个有独立用途的来源，并移除十个并列举例；删除的是论文中的引用标记，文献库中的已核对条目仍保留备查。

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

## 已实施的引用取舍

新增 [FLARE，CoRL 2025](https://proceedings.mlr.press/v305/zheng25a.html)，替换“紧凑潜表示预测”处的 DELE-w0.5 与 Efficient-WAM。FLARE 的原文明确预测紧凑的未来观测表示，因此现有句子即可准确容纳该引用；其未来 token 仍参与推理，本轮没有把它放入“训练后丢弃预测器”的引用组。

重新启用已有的 [Akinola 等，IROS 2021](https://crlab.cs.columbia.edu/dynamic_grasping/)，放在“学习型策略进入运动场景”这一现有陈述之后。它结合学习得到的运动预测、抓取质量与实时规划，补充经典系统和近期动态策略之间的来源。

| 移除的正文引用 | 该处保留或替换的来源 | 取舍依据 |
|---|---|---|
| StreamingVLA | DynamicVLA、SmolVLA | 保留推理与执行重叠的代表作 |
| Chronos | VLASH | 执行时刻条件已有直接来源 |
| DELE-w0.5、Efficient-WAM | FLARE | 使用更早且直接支撑紧凑未来表示预测的正式论文 |
| VPP | GR-1、Seer | 保留视频预测作为策略目标的代表性前史 |
| RVT、3D Diffuser Actor | PerAct、DP3 | 3D 输入的一般性陈述保留两个代表作 |
| TraceVLA | ATM、Track2Act、Im2Flow2Act | 压缩 2D 轨迹组的并列举例 |
| 3DFlowAction | General Flow、FlowDreamer、PointWorld | 保留动作接口与场景预测的相关来源 |
| AffordTrajDP | kPAM、SPOT、ObjectForesight | 保留关键点和 SE(3) 轨迹两类来源 |

PUMA、DynamicWAM、Fast-WAM、DOCIR、SPOT、PointWorld、SG-WAM 及实际依赖、基线来源保留。DynamicManip 被正文单独点名，移除其引用会留下无来源的陈述；MaskWAM 与 OA-WAM 分别支撑现有“掩码或槽”的表述，因此均保留。DSR 本轮不额外启用。

## 验证与范围

修改限定为 `references.bib`、中英文 `related_work.tex` 的引用标记、核对报告及重新编译的 PDF。移除引用命令并归一化空白后，中英文正文分别与修改前一致；两种语言新增与移除的引用键完全对应。四个入口检查引用解析、最终参考文献集合和 BibTeX 日志；论文中的结果占位与正文论述不属于本轮修改范围。

四份 PDF 编译成功，最终日志无 LaTeX 错误、未定义引用或 BibTeX 警告，中英文引用集合一致。正文独立版含 60 条、附录独立版含 18 条、完整中英文稿各含 63 条参考文献。仓库总体检查仍报告正文结束于第 9 页；单独编译修改前的引用版本同样结束于第 9 页。中文附录 A 另有一处既存长公式溢出，位于未修改的 `zh/appendix/implementation.tex`，本轮不调整版式或正文。

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
| `akinola2021dynamic` | 正文 | [IROS 2021](https://crlab.cs.columbia.edu/dynamic_grasping/) |
| `act` | 正文 | [RSS 2023](https://www.roboticsproceedings.org/rss19/p016.html) |
| `ahead` | 正文 | [CoRL 2026，已录用](https://arthurjakobsson.com/publications/) |
| `dbctfp` | 正文 | [IEEE Robotics and Automation Letters 2025](https://doi.org/10.1109/LRA.2025.3557746) |
| `dinov3` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2508.10104) |
| `diffusionpolicy` | 正文 | [RSS 2023](https://www.roboticsproceedings.org/rss19/p026.html) |
| `domino` | 正文 | [ECCV 2026](https://link.springer.com/chapter/10.1007/978-3-032-37592-6_18) |
| `dynamicvla` | 正文 | [NeurIPS 2026，已录用](https://neurips.cc/virtual/2026/poster/156061) |
| `fastwam` | 正文 | [NeurIPS 2026，已录用](https://neurips.cc/virtual/2026/poster/149922) |
| `flare` | 正文 | [CoRL 2025](https://proceedings.mlr.press/v305/zheng25a.html) |
| `flowmatching` | 正文 | [ICLR 2023](https://openreview.net/forum?id=PqvMRDCJT9t) |
| `libero` | 未引用 | [Advances in Neural Information Processing Systems (Datasets and Benchmarks Track) 2023](https://proceedings.neurips.cc/paper_files/paper/2023/hash/8c3c666820ea055a77726d66fc7d447f-Abstract-Datasets_and_Benchmarks.html) |
| `mujoco` | 正文 | [IROS 2012](https://doi.org/10.1109/IROS.2012.6386109) |
| `oawam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2605.06481) |
| `physmani` | 正文 | [ECCV 2026](https://link.springer.com/chapter/10.1007/978-3-032-37029-7_2) |
| `pointworld` | 正文 | [CVPR 2026](https://openaccess.thecvf.com/content/CVPR2026/html/Huang_PointWorld_Scaling_3D_World_Models_for_In-The-Wild_Robotic_Manipulation_CVPR_2026_paper.html) |
| `robosuite` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2009.12293) |
| `openwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2610.07922) |
| `affordtraj` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.01603) |
| `dreamwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.04996) |
| `flowwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2607.13017) |
| `dynamicmanip` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.01452) |
| `pactwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2602.15882) |
| `dcwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2607.25918) |
| `dele` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.22067) |
| `longwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2610.10528) |
| `chronos` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2610.13929) |
| `rtc` | 正文 | [NeurIPS 2025](https://proceedings.neurips.cc/paper_files/paper/2025/hash/300ccb2187dedd4edcc07f7e76d8e553-Abstract-Conference.html) |
| `docir` | 正文 | [IROS 2025](https://doi.org/10.1109/iros60139.2025.11246704) |
| `se3nets` | 正文 | [ICRA 2017](https://doi.org/10.1109/icra.2017.7989023) |
| `se3posenets` | 正文 | [ICRA 2018](https://doi.org/10.1109/ICRA.2018.8461184) |
| `dsr` | 未引用 | [CoRL 2020；PMLR 出版于 2021](https://proceedings.mlr.press/v155/xu21b.html) |
| `atm` | 正文 | [RSS 2024](https://www.roboticsproceedings.org/rss20/p092.html) |
| `im2flow2act` | 正文 | [CoRL 2024；PMLR 出版于 2025](https://proceedings.mlr.press/v270/xu25a.html) |
| `tracevla` | 未引用 | [ICLR 2025](https://proceedings.iclr.cc/paper_files/paper/2025/hash/8667f264f88c7938a73a53ab01eb1327-Abstract-Conference.html) |
| `vpp` | 未引用 | [International Conference on Machine Learning 2025](https://proceedings.mlr.press/v267/hu25g.html) |
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
| `3dflowaction` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2506.06199) |
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
| `streamingvla` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2603.28565) |
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
| `efficientwam` | 未引用 | [arXiv，未确认正式发表](https://arxiv.org/abs/2606.10040) |
| `wog` | 正文 | [ICML 2026](https://proceedings.mlr.press/v306/su26c.html) |
| `sgwam` | 正文 | [arXiv，未确认正式发表](https://arxiv.org/abs/2608.01397) |
| `peract` | 正文 | [CoRL 2022；PMLR 出版于 2023](https://proceedings.mlr.press/v205/shridhar23a.html) |
| `rvt` | 未引用 | [CoRL 2023](https://proceedings.mlr.press/v229/goyal23a.html) |
| `3ddiffuseractor` | 未引用 | [CoRL 2024；PMLR 出版于 2025](https://proceedings.mlr.press/v270/ke25a.html) |
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
