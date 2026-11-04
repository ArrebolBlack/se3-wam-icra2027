# INFER0 实时协议 C：已核验结果副本

## 当前Table 1与Fig. 4（2026-11-04）

正式模型为C equalaux01：seed0、第8轮best/update20696，12层、271.8M可训练参数；当前论文采用399ec818加速源码的编译BF16/Euler5，TF32关闭。Native、+50、+100、+150、+200 ms与Paused六组8400场均经独立逐查询审计、接触参考联结及collector复算，无缺场或重复。

- [主表数据](table1-20261104.json)：33行已验收结果的Research原样副本，原十配置30行不变；C Native为1064/1400（76.0%），+150 ms为358/1400（25.57%）。Paused实测1148/1400（82.0%），table1_display按作者指令保留原同步1162/1400（83.0%）。
- [扫描数据](latency-five-point-20261104.json)：55个已验收点的Research原样副本；C为76.00／63.43／42.79／25.57／9.79%，每点1400场，0／150 ms与Table 1一致，未混入旧FP32结果。
- [S4逐任务与配对区间](native-per-task-20261104.json)、[逐场成功CSV](native-per-task-20261104-scenes.csv)、[区间CSV](native-per-task-20261104-intervals.csv)：Research对应记录的原样副本，十一配置Native额外+0 ms实时结果、最强对照与完整四格计数。14任务各100场，任务等权均值逐方法与Table 1 Native一致。
- [Fig. 4来源与复现](../../figures/latency/SOURCE.md)：中英文真实曲线、场景区间及表图核对；旧合成预览已退出正文。
- [S6阶段实测](stage-timing-20261104.json)：同一BF16 C在5090上的900组编译边界计时、单独读出和无探针对照；补充分解表时读取。原Table 1/Fig. 4回放标定保持不变，源档归[Research S6验收](https://github.com/ArrebolBlack/se3-wam-research/tree/main/docs/experiments/INFER0/results/c-bf16-s6-20261104)。

实验事实与源档归[Research的BF16 C验收目录](https://github.com/ArrebolBlack/se3-wam-research/tree/main/docs/experiments/INFER0/results/c-bf16-table1-fig4-20261104)。新Paused比原83%新增成功23场、丢失37场，净少14场；场景与种子逐项一致，执行器及精度部署不同，不作单因素归因。此前原FP32六组保留在Research的c-equalaux01-table1-fig4-20261104历史入口。

C的p95为15.113 ms，来自Ubuntu RTX5090 batch1三轮各30预热＋300测量，回放使用全部900个实测值；单RGB-D及仿真目标位姿不计真实跟踪器代价。PUMA保留官方D14三相机预算，其E7 rollout使用单agentview；其他基线保留双相机计时。S4由`python scripts/build_realtime_per_task.py --c-native-results <已验收C目录> --research-output <INFER0结果目录>`生成，Δ复用既有100000次任务内配对bootstrap；对照以所选检查点和观察到的最强基线为条件，并列按表顺序，不作选择校正。整体Δ对PUMA为+16.3571，95%区间[14.2857,18.5]。区间不代表训练种子方差；无完整13任务接触误差时保留缺失。

## 此前基线副本

- [30组指标](formal64-20261101.json)、[50点扫描](latency-five-point-20261102.json)：新增C之前的已验收副本，供核对基线数值未变。
- [378行逐任务结果](formal64-per-task-20261101.csv)：此前九配置的逐任务表来源；PUMA与C的完整逐任务记录归Research。

Equal latency、完整Original executor对照、额外训练种子和真机仍不在本批完成范围。Paused仅暂停推理期间物理，并保留共享执行器与T5队列；原同步结果与共享执行器Paused分别保留来源。

## 历史ACT／DP配置（不用于当前表）

实验事实和完整原始数据归[研究仓 c8c33481](https://github.com/ArrebolBlack/se3-wam-research/tree/c8c33481/docs/experiments/INFER0/results/realtime-c-capture-index)及其 INFER0 主文档；本目录只保存论文实际转录的结果。

- [act-report.json](act-report.json)、[act-per-task.csv](act-per-task.csv)：ACT seed0，14 任务各 100 个留出场景，零人工附加延迟；SR、13 任务接触误差、任务内场景 bootstrap 区间、失败类别与回放计时。
- [dp-report.json](dp-report.json)、[dp-per-task.csv](dp-per-task.csv)：DP seed0同一1400场正式组；SR为0，8251次查询均超50 ms，完整接触误差及动作年龄为缺失。
- [act-paused-report.json](act-paused-report.json)、[act-paused-per-task.csv](act-paused-per-task.csv)、[配对结果](act-paused-paired.json)：ACT完整Paused组及同场景实时对照；PRO6000计算、5090分布回放。
- [dp-paused-report.json](dp-paused-report.json)、[dp-paused-per-task.csv](dp-paused-per-task.csv)、[配对结果](dp-paused-paired.json)：DP完整Paused组及同场景实时对照；PRO6000计算，保留有效中断产物。
- [act-delay150-report.json](act-delay150-report.json)、[act-delay150-per-task.csv](act-delay150-per-task.csv)、[配对结果](act-delay150-paired-native.json)：ACT完整附加150 ms组及原生延迟对照。
- [dp-delay150-report.json](dp-delay150-report.json)、[dp-delay150-per-task.csv](dp-delay150-per-task.csv)、[配对结果](dp-delay150-paired-native.json)：DP完整附加150 ms组，含中断产物复用和原生延迟对照。
- [act-delay-audit.json](act-delay-audit.json)、[dp-delay-audit.json](dp-delay-audit.json)：RTX 5090、batch 1、3 轮各 300 次调用的延迟复算。原始轮次在研究仓 `results/realtime-c-5090/`。

ACT/DP各1,400场全部从原始 query/command/timing 重新审计并与共享参考联结。实际 benchmark 运行版本为 `68a44b06`，其等价实现与上游测试已合并为 `5e5eaa31`。这两个正式组的计算设备也是 RTX 5090，物理时钟只使用预先测得的延迟样本；现场计算耗时不进入结果。两者只读取 agent-view RGB，DP读取因果两帧历史。

共享参考中原有的 40 处数值 IK 未解点已全部分类：37 处由两连杆几何必要条件排除，965/990 由覆盖完整关节域及原位姿容差的区间证书排除，926 场景补解成功。原求解器记录保留；两个新排除场景的 ACT 都未发生接触，因此接触误差不变。全部原始证据、参考、复算命令与 TOS 归档入口位于研究仓 `results/realtime-c-capture-index/`。

本次填ACT/DP原生实时、附加150 ms、完整Paused组和5090延迟；其余附加延迟、Equal latency、原生执行器及真机完整组仍缺失。ACT Paused直接复用已验收scene0；ACT附加150 ms组1400场均正常退出。DP附加150 ms保留原1328场并只补跑72场，1272场worker正常退出，128场在中断前已完整关闭并通过独立审计，退出码null保留。原始归档均完整读回复算。DP两个实时组SR均为0，场景bootstrap退化为[0,0]；附件保留Wilson区间0–0.274%，全零配对差不证明等效。仅T4_sphere有6次被动接触，不能把该任务均值填为完整13任务误差。DP附加150 ms的7524次查询全部超时，无策略指令执行，动作年龄为缺失。各组区间只反映单个训练端点的场景不确定性。

DP Paused为463/1400，SR 33.07%（任务内场景bootstrap 95%为31.00–35.21%），表格取33.1。
1033场有定义的接触、267场无接触、100场T3_phase为N/A，13任务等权e_p为34.07 mm。
保留先前45场有效结果，接续1355场；1251场worker正常退出，149场在中断前完整关闭并通过审计。
早期pilot的9个重复场景保留较早有效副本，不按结果选择。全部8400个原始文件完整读回后独立复算一致。
同端点实时减Paused为-33.07个百分点，配对场景95%区间[-35.21, -31.00]；计算宿主分别为Windows5090与Linux PRO6000。
附件保留研究侧完整误差记录供复算，不向当前论文重新加入已删除的e_t。

此次四份PDF已重新编译，17项单元检查通过，中英文数字与结构差异均为0。
`build.ps1 -Check`仍因主线已有的正文第9页（上限8页）退出；中文稿另有1处已有溢出。
这些版面检查在本次填数前后的输出相同，不把本次编译报告为全部检查通过。

相机输入另经[研究仓 8f4546be](https://github.com/ArrebolBlack/se3-wam-research/tree/8f4546be)复核：BASE1共同协议记录七个已训练端点的agentview输入及缺失视图处理，未取得端点的+SE(3)腕部输入保持未确认。合并时保留负责人新稿对CV-input段及表格行的删除；CV技术时序核对留在研究记录，不重新加入论文。
