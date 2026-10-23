# v4 稿待确认问题（2026-10-23）

本文件随 v4 稿（摘要、引言按 Notion《SE(3)-WAM论文10.23》终稿同步；Related Work 新写；其余正文与附录按真实架构重写）一起提交。
下列问题在投稿前必须由作者确认或修改。每项给出当前写法所在位置、写法依据，以及需要作出的决定。
数值占位（彩色方括号）不在此逐项列出，以 `python scripts/check_build.py --strict` 的统计为准。

## A. 与研究仓库记录不一致或尚无证据的表述（优先处理）

### A1. “推理期间场景持续运动”的实时协议
- **当前写法**：摘要、引言第 4 段、§4.1 Protocol、附录 C.3（Executor / Real-time protocol）、结论均写为：观测、场景运动与执行共用物理时钟，方法计算期间物理按其实测延迟推进。
- **研究记录**：现行评测为同步时钟，每步 50 ms、每次推理执行一步，推理期间场景暂停（BACKBONE0 “同步每次执行一步、50ms 物理时钟”；PW0 配置 `execution.profile: synchronous_receding_horizon`, `steps_per_replan: 1`；BASE1 DynamicWAM 记录 `wall_control_period_s=None`）。
- **需要决定**：最终评测改用“按实测延迟推进物理”的协议；或把上述各处改为同步协议，并删除 Paused 列与相关论述。

### A2. 仿真中的目标位姿来自仿真器真值
- **当前写法**：§3.2、附录 A.1、C.1、F.2 明确写“仿真中位姿读自仿真器”；表 3 与表 S-remember 有“SE(3) with tracker noise”一行；表 S-tracker 中仿真位姿标为主设置（\sel）。旧稿“仿真中用 FoundationPose 跟踪”的说法已删除。
- **依据**：项目简介“物体 GT 与运动学属于 oracle 信息研究”；HISTORY1 结论限定于 GT 输入条件。
- **需要决定**：确认按跟踪误差标定的位姿噪声消融会补跑；若不补跑，删除相应行与正文句子。

### A3. DROID 基座不含目标位姿
- **当前写法**：§3.6、附录 B、表 S-pretraining(-data) 按 PW0 已批准的子配方：输入为当前 RGB-D 与 T8 机器人状态，目标为动作 + 稀疏 3D 流（PointWorld 轨迹，可见性损失权重 0）+ 未来 DINO（0.1）；48 层、1,017.181M 可训练参数，20 轮、21,060 次更新、global 512、64 卡。真机策略微调时新增目标状态 token 与位姿头。
- **需要确认**：(1) 真机策略是否就用这个 48 层基座（以及它在 RTX 5090 上的 p95 出动作时间）；(2) 正式预训练完成后用实际结果替换“训练中”的事实；(3) 表 S-pretraining 中的试点对照（仅动作、动作+流、动作+流+DINO，12 层）是否会运行。

### A4. 消融的规模
- **当前写法**：附录 F 写明筛选在缩小规模（4 层 × 768、4 轮、40,104 次更新、global 16、单种子）上完成；表 3 与 §4.4 写“使用最终模型与配方”。
- **依据**：BACKBONE0、Q3-INFO0、FUTURE0、HISTORY1 均为小规模；更大容量复验 Q3-INFO1 尚待放行。
- **需要决定**：在 24 层最终模型上重跑表 3 各行；或把表 3 改标为筛选规模的结果。

### A5. 真机五个任务
- **当前写法**：§4.3、表 2、表 S-real-ci、附录 D.3、图 S4 中任务名称（T1–T5）、驱动装置、速度、示范数 N、每任务试验数（暂写 20）、基线集合（暂为 π0.5 与 DynamicWAM）均为占位。之前讨论过的 6 任务表格在会话中丢失，需重新提供。
- **需要决定**：最终任务表、每任务的成功判定、试验数与基线。

### A6. 主表与附录中计划中的对照是否已运行
- 表 1：π0.5+SE(3)、DynamicWAM+SE(3)、CV input、Kalman interceptor、+150 ms 与 Paused 列。
- 附录 D.2：DOMINO 与 LIBERO（已从正文主表移到附录）。
- 附录 E/F：表 S-protocols、S-latency、S-predict、S-clearance、S-extrapolation、S-interventions 的全部行。
- **需要决定**：保留哪些对照；未运行的整行删除，而不是留占位。

## B. 由研究记录推断、需对照模型代码核实的实现细节

| 位置 | 当前写法 | 依据 / 不确定处 |
|---|---|---|
| §3.4、A.1、A.5、图 2 | 世界流 = 212 个场景 token（196 patch + 8 目标状态 + 8 机器人状态）+ 16 个摘要（meta）token；动作 token 只读取摘要 token 与彼此；共享注意力投影、分流 FFN | P5 dense candidate、SPEED0（“Action 读取 16 个 meta 及 8 个 Action key”）。请确认场景 token 是否读取 meta、meta 是否读取场景。 |
| A.3 | 位姿头读取目标状态 token 与摘要 token 的池化最终状态；流头为每个 patch token 上的线性读出 | 推断，Q3-INFO0 仅说明 `_FutureReadouts` 从 scene/meta 隐藏特征读出。 |
| A.4 | 指令为基座坐标系平移增量 + 左相对旋转向量 + 夹爪；截断 0.10 m / 0.5 rad | 沿用旧稿；BACKBONE0 记录平移限制 0.10 m。增量的参考位姿请核实。 |
| A.6、表 S-hyper | AdamW 2e-4、wd 1e-4、β=(0.9,0.999)、warmup 5,174、余弦到 0、global 512、20 轮 51,740 更新、梯度截断 0.1、noise8 | P5 dense candidate（尚未提交正式训练）。正式训练若改配方需同步。 |
| paper_config.tex | `\cfgTrainHardware`、`\cfgTrainHours` 为占位 | 最终训练卡数与时长未定。 |
| §3.3、A.3 | 可见性损失为 BCE；仿真中可见性损失启用 | 请核实仿真配方中可见性权重。 |

## C. 叙事与写作上的决定

- **C1 辅助外观目标**：最终配置保留未来深度、DINO、运动区域 RGB 与当前目标 RGB 重建（各 0.1）。正文把它们写为“辅助外观目标”，摘要未提。若认为冲淡“目标精确、其余粗略”的主线，可压缩其篇幅。
- **C2 名称与题目**：题目暂为 “\ours: Role-Aware 4D World–Action Modeling for Dynamic Manipulation”，`\ours` 仍显示 SE(3)-WAM；改 `paper_config.tex` 中 `\ours` 一处即可全文替换。
- **C3 术语**：全文统一为“稀疏 3D 流（sparse 3D flow）”；Notion 摘要中 “coarsely as a sparse 3D flow” 已沿用。
- **C4 执行与领先时长**：v4 不含领先时长条件化；附录 G.4 改为“滚动重规划下的领先时长”，表 3 的 Physical time 组已删除。

## D. 参考文献

- 新增 39 条均对照 arXiv 或会议页面核对。kPAM 的会议（ISRR 2019）来自记忆、未经页面直接证实，请再核对。
- 大团队论文（RT-1、RT-2、Octo、OpenVLA、π0、V-JEPA 2、SmolVLA、UniPi、Marturi 2019）作者列表以 “and others” 截断。

## E. 编译

- 英文三份 PDF 在容器中编译无错误、无未定义引用、无溢出；正文在第 8 页结束；中英文数字与结构差异为零；单元测试通过。
- 中文稿只在容器字体（Noto）下编译过，仍有 4 处轻微溢出；请在本机用 ctex（fontset=windows）编译确认。
