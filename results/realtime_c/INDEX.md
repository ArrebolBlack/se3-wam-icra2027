# INFER0 实时协议 C：已核验结果副本

## 五点附加延迟扫描（2026-11-02）

- [45点指标](latency-five-point-20261102.json)：[Research正式验收](https://github.com/ArrebolBlack/se3-wam-research/tree/1a51774e6/docs/experiments/INFER0/results/realtime-c-latency-sweep)的原样副本；用于正文Fig. 4与附加延迟表。九配置各有0／50／100／150／200 ms五点，每点1400场；其中0／150 ms复用下方Table 1，新增三个点共37800场。

表内九配置全部填齐并按每列已有结果更新前两名标记；图采用[单栏内左右双面板](../../figures/latency/INDEX.md)，展示全部九配置的五点与场景bootstrap区间。PUMA、最终模型仍待补。点估计不要求单调，SE(3)输入对照的收益不作全延迟范围一致为正的解释；原始轨迹、逐场审计与配对差值区间仍归Research。

45个表格值与绘图点逐项核对；图中区间直接使用已接收JSON。10个待补单元格和10个排名标记保持不变，0／150 ms的18个单元格与Table 1一致。英文正文、独立补充、完整阅读版和中文稿均已编译，并视觉检查Fig. 4与表S7所在页面。

## 当前填表数据（2026-11-01）

实验事实归[Research 1e9f33651正式验收](https://github.com/ArrebolBlack/se3-wam-research/tree/1e9f33651/docs/experiments/INFER0/results/realtime-c-table1-rollout/formal64-accepted-20261101)。本批九配置、三协议共37800场：33600场新运行与4200场DynamicWAM＋SE(3)已验收复用；各组一个训练种子、14任务各100场。

- [27组指标](formal64-20261101.json)：Research已验收JSON的原样副本；用于主表SR/p95、协议表Late/动作年龄及扫描表0/150 ms。
- [378行逐任务结果](formal64-per-task-20261101.csv)：Research证据包中的336行新运行结果，加复用组42行；用于逐任务表的实时SR。完整e_p与接触数读取上面的JSON。

OpenWAM默认行表示官方cache＋compile，off行关闭两者。SR保留原训练单agentview，p95及回放预算使用双相机5090测量；不能称为双相机训练策略。DP采用DDIM16/H15，以下旧DDPM100结果不再填当前表。π0.5＋SE(3)与DynamicWAM＋SE(3)分别使用已训练30000/40000步端点。两者实测延迟下的SR低于基础方法，Paused下较高，不能概括为实时收益普遍为正。

该批更新main_results、supp_per_task、supp_protocols、supp_latency与DP返回块长度，中英文说明同步。保留e_p无法形成完整13任务均值时的缺失值；e_t只留证据，不重新加入论文。新增扫描点已由上方五点验收补齐；PUMA、最终模型、Equal latency、Original和真机仍待填。不将官方PUMA权重计时混入未验收的Dynamic-14端点行。

Paused保留统一执行器，零附加延迟时每50 ms重规划，只暂停推理期间物理。它是无推理等待对照，不是性能上界，也不是原生整块执行结果；定义归附录B.3。原始归档、完整审计和复算工具仍归Research，不在论文仓复制。

本次`build.ps1 -Check`完成四份PDF编译、17项检查；正文止于第8页，中英文数字与结构差异均为0，英文三份文档无溢出。中文引言原有12.8817 pt换行溢出与填数前相同；本次表格无新增溢出。主表、协议与扫描表90个已填汇总单元格逐项核对，逐任务表152个数值单元格及27组分母闭合复核通过。

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
