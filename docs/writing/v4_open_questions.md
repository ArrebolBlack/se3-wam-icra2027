# v4 稿待确认问题（2026-10-23，整合 T5/T6/T7 后更新）

v4 稿：摘要、引言按 Notion《SE(3)-WAM论文10.23》终稿同步；Related Work 新写；其余正文与附录按真实架构重写。
随后并入三条分支，整合分支为 `paper-v4-integrated`：
- `v4-t5-real`：真机任务核实，加入六张真机示意图；
- `v4-t6-code`：对照模型代码核对实现细节；
- `v4-t7-aux`：精简辅助外观目标的篇幅。

各分支的完整证据见 `v4_t5_real_report.md`、`v4_t6_code_report.md`、`v4_t7_aux_report.md`。

下列问题在投稿前必须由作者确认或修改。数值占位（彩色方括号）不在此逐项列出，以 `python scripts/check_build.py --strict` 的统计为准。
源文件中的 `% CONFIRM(...)` 注释对应本文件的条目，可用 `grep -rn "CONFIRM(" --include=*.tex .` 定位：
- `CONFIRM(A1)` 对应 A1；
- `CONFIRM(real tracker)` 对应 A6；
- `CONFIRM(real figures)` 对应 A5。

## A. 与研究记录不一致或尚无证据的表述（优先处理）

### A1. “推理期间场景持续运动”的实时协议（仍未决定）

**当前写法**
- 摘要、引言第 4 段、§4.1 Protocol、附录 C.3（Executor / Real-time protocol）、结论都写为：观测、场景运动与执行共用物理时钟，方法计算期间物理按其实测延迟推进。
- 表 1 有 +150 ms 列与 Paused 列。

**代码证据（T6 核实）**
- P5 配置为 `execution.profile: synchronous_receding_horizon`、`steps_per_replan: 1`。
- benchmark 的 `evaluation/rollout.py:351–377` 先调用 `policy.act`，再调用 `environment.step`，所以推理期间物理暂停。
- wall pacing 不会让物理在推理期间推进。

**整合时的处理**
- 附录 A.6 Deployment 改为中性写法：“每执行一条指令后重新规划；查询期间场景与剩余指令如何推进，由附录 C 的评测协议决定”。
- A.6 加了 `% CONFIRM(A1)` 注释。
- 其余各处的实时叙述未改。

**需要决定**
- 方案一：最终评测改用“按实测延迟推进物理”的协议，需在 benchmark 中实现并重跑。
- 方案二：把上述各处改为同步协议，并删除 Paused 列与相关论述。
- 方法 §3.1 中的实时 lead 分析是动机，不能当作已有的实时实验。

### A2. 仿真中的目标位姿来自仿真器真值
- **当前写法**：§3.2 与附录 A.1、C.1、F.2 都写“仿真中位姿读自仿真器”。表 3 与表 S-remember 有 “SE(3) with tracker noise” 一行。附录 D.2 的 DOMINO/LIBERO 结果也报告加噪声的变体。
- **需要决定**：确认是否补跑按跟踪误差标定的位姿噪声消融。若不补跑，删除相应的行与句子。

### A3. DROID 基座（PW0，正式训练进行中）

**T6 已核实并写入**
- 输入为当前 RGB-D 与 T8 机器人状态，没有目标位姿，204 个场景 token。
- 监督为动作、PointWorld 稀疏 3D 流（可见性权重 0）与未来 DINO（0.1）。
- 48 层，1,017.181M 可训练参数，64 卡，20 轮，21,060 次更新。
- 训练/验证划分为 37,874 / 4,213 个 episode，对应 538,740 / 60,149 个窗口。
- XYZ/DINO 只监督 anchor 位置，其余 S8 位置只有动作损失。
- 正式训练从第 10 轮恢复，仍在进行，尚未验收。

**需要确认**
1. 真机策略是否采用这个 48 层基座，以及它在 RTX 5090 上的 p95 出动作时间。
2. 正式预训练完成后，用实际结果替换“训练中”的表述。
3. 附录 B 中 12 层试点对照（仅动作、动作+流、动作+流+DINO）是否会运行。不运行就删除。

### A4. 消融的规模
- **当前写法**：附录 F 写明筛选在缩小规模上完成：4 层 × 768、4 轮、40,104 次更新、global 16、单种子。表 3 与 §4.4 写“使用最终模型与配方”。
- **需要决定**：在 24 层最终模型上重跑表 3 各行，或把表 3 改标为筛选规模的结果。

### A5. 真机：六个任务（T5 已核实任务集合，细节仍占位）

**当前写法**
- 摘要、引言、§4.3、结论、表 2、表 S10、表 S-real-ci 与附录 D.3 统一为六个任务：
  - T1 传送带抓取；
  - T2 移动容器放置；
  - T3 转台抓取；
  - T4 遥控小车抓取；
  - T5 碰撞后拦截；
  - T6 斜坡滚动/滑动拦截。
- 六类运动描述为直线、圆周、自由平面、撞击后与重力加速。

**图 S4 的图片**
- 使用 `figures/real/01..06*.png`。
- 图注明确写为 “AI-generated concept illustrations, to be replaced by photographs of the setup”。
- 源文件有 `% CONFIRM(real figures)`。
- **投稿前必须换成实拍照片，或删除该图**。

**仍需提供**
- 每个任务的速度或运动范围、示范数 N、每任务试验数 n。
- 成功与失败判定（表 S10 中的占位）。
- 相机型号与分辨率。
- 基线集合：目前 π0.5 与 DynamicWAM 两行仍以 `\fillin` 标为候选。
- 评测天数。

### A6. 真机在线跟踪器（新增）
- **现状**：研究仓库 POSE0 只有离线链路（GroundingDINO + SAM 2.1 + WildDet3D），在线实时跟踪器尚未确定。所核对的模型代码中，没有在线线程、丢失判据或插值规则的可运行实现。
- **整合时的处理**：
  - §3.2 改为通用写法：“因果跟踪器从 RGB-D 流逐帧估计目标位姿，每个估计只输出一次”。
  - 附录 A.2 写 Grounding DINO + SAM 2.1 初始化，跟踪器本身写为 `\fillin{e.g., FoundationPose … or a monocular metric 3D box detector (WildDet3D)}`，并加了 `% CONFIRM(real tracker)` 注释。
  - 表 S-tracker 图注写“真机行使用所选跟踪器”。
- **需要决定**：选用哪个跟踪器，以及丢失判据阈值、参考视图数、插值规则。这些同时决定 A2 的噪声标定。

### A7. 主表与附录中计划的对照是否已运行
- 表 1：π0.5+SE(3)、DynamicWAM+SE(3)、CV input、Kalman interceptor，以及 +150 ms 与 Paused 两列（与 A1 相关）。
- 附录 D.2：DOMINO 与 LIBERO。
- 附录 E/F 中以下各表的全部行：S-protocols、S-latency、S-predict、S-clearance、S-extrapolation、S-interventions。
- **需要决定**：保留哪些对照。未运行的整行删除，不要留占位。

### A8. 种子数
- 正文写本文变体三个训练种子。表 S-predict 的外观目标组与附录 F 开头已注明该组为三个种子。
- 表 S-baselines 中 \ours 行的种子数仍为 `\fillin{3}`。
- **需要确认**：最终各组的种子数。

## B. 实现细节（T6 已对照代码核实，已写入论文）

T6 的主要更正如下，行号证据见 `v4_t6_code_report.md`：

| 项目 | 原写法 | 现写法（代码事实） |
|---|---|---|
| 注意力掩码 | 场景与摘要 token 双向读取 | **S→S；M→S,M；A→M,A**。场景不读取摘要。图 2 的掩码格已改 |
| 位姿头 | 目标状态与摘要 token 池化后接 MLP | 16 个摘要 token 均值上的单个 Linear(d, 8×6) |
| 丢失目标 | 用可学习嵌入替代 | 无有效特征的槽位被掩码，不使用可学习的丢失 token。附录 D 两处 “missing-state embedding” 在整合时同步改掉 |
| 流损失 | 按可见性门控的平方误差 + BCE | 归一化位移（尺度 0.7155 m）三通道平均 MSE + 逐位置 BCE，不按可见性门控。仿真中可见性权重 1，DROID 为 0 |
| 目标 RGB 重建 | 当前 patch 线性解码，MSE | 摘要均值 → MLP → 32×32 RGB，L1 |
| 动作限幅 | 0.10 m / 0.5 rad | 候选配置 0.05 m / 0.5 rad；0.10 m 需显式覆盖。零旋转指令保留上一次朝向目标 |
| 推理精度 | FP16 | FP32（P5 默认，E5 的 FP16 测速不适用） |
| noise8 | 每窗口 8 个样本 | 每个预测位置 8 对独立噪声/时间，复用世界状态 |
| 机器人状态 | 夹爪开度 | 夹爪开度比例，不含关节 |
| DINO 教师 | 每步运行 | 按 episode 缓存 |

**仍需作者处理**
- `paper_config.tex` 中的 `\cfgTrainHardware`、`\cfgTrainHours` 仍是占位。P5 最终仿真训练尚未启动。
- 若正式训练改了配方，同步更新表 S-hyper。

## C. 叙事与写作上的决定

- **C1 辅助外观目标（已处理）**：T7 把外观目标压缩为方法 §3.3 的一句话和附录 A.3 的一段，并按 T6 的证据修正读出与损失。整合时按 T7 的建议，把图 2 中的 “+ depth, DINO, RGB” 改为小字 “+ auxiliary targets”。
- **C2 名称与题目**：题目暂为 “\ours: Role-Aware 4D World–Action Modeling for Dynamic Manipulation”，`\ours` 仍显示 SE(3)-WAM。改 `paper_config.tex` 中 `\ours` 一处即可全文替换。
- **C3 术语**：全文统一为“稀疏 3D 流（sparse 3D flow）”。
- **C4 执行与领先时长**：v4 不含领先时长条件化。附录 G.4 为“滚动重规划下的领先时长”。

## D. 参考文献

- 新增 39 条均对照 arXiv 或会议页面核对过。
- kPAM 的会议（ISRR 2019）来自记忆，未经页面直接证实，请再核对。
- 大团队论文（RT-1、RT-2、Octo、OpenVLA、π0、V-JEPA 2、SmolVLA、UniPi、Marturi 2019）的作者列表以 “and others” 截断。

## E. 编译（整合分支）

- 英文三份 PDF 在容器中编译无错误、无未定义引用、无溢出：main 12 页（正文止于第 8 页），supplementary 24 页，paper_full 36 页。
- 中英文数字与结构差异均为 0。单元测试通过。
- 中文稿在容器字体（Noto）下有 5 处轻微溢出，均为字体替换所致。各分支用本机 MiKTeX + ctex 编译时为 0。
- 重建的 PDF 不纳入提交。
