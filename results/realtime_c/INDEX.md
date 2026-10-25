# INFER0 实时协议 C：已核验结果副本

实验事实和完整原始数据归[研究仓 4836618d](https://github.com/ArrebolBlack/se3-wam-research/tree/4836618d/docs/experiments/INFER0/results/realtime-c-capture-index)及其 INFER0 主文档；本目录只保存论文实际转录的结果。

- [act-report.json](act-report.json)、[act-per-task.csv](act-per-task.csv)：ACT seed0，14 任务各 100 个留出场景，零人工附加延迟；SR、13 任务接触误差、任务内场景 bootstrap 区间、失败类别与回放计时。
- [dp-report.json](dp-report.json)、[dp-per-task.csv](dp-per-task.csv)：DP seed0同一1400场正式组；SR为0，8251次查询均超50 ms，完整接触误差及动作年龄为缺失。
- [act-paused-report.json](act-paused-report.json)、[act-paused-per-task.csv](act-paused-per-task.csv)、[配对结果](act-paused-paired.json)：ACT完整Paused组及同场景实时对照；PRO6000计算、5090分布回放。
- [act-delay150-report.json](act-delay150-report.json)、[act-delay150-per-task.csv](act-delay150-per-task.csv)、[配对结果](act-delay150-paired-native.json)：ACT完整附加150 ms组及原生延迟对照。
- [act-delay-audit.json](act-delay-audit.json)、[dp-delay-audit.json](dp-delay-audit.json)：RTX 5090、batch 1、3 轮各 300 次调用的延迟复算。原始轮次在研究仓 `results/realtime-c-5090/`。

ACT/DP各1,400场全部从原始 query/command/timing 重新审计并与共享参考联结。实际 benchmark 运行版本为 `68a44b06`，其等价实现与上游测试已合并为 `5e5eaa31`。这两个正式组的计算设备也是 RTX 5090，物理时钟只使用预先测得的延迟样本；现场计算耗时不进入结果。两者只读取 agent-view RGB，DP读取因果两帧历史。

共享参考中原有的 40 处数值 IK 未解点已全部分类：37 处由两连杆几何必要条件排除，965/990 由覆盖完整关节域及原位姿容差的区间证书排除，926 场景补解成功。原求解器记录保留；两个新排除场景的 ACT 都未发生接触，因此接触误差不变。全部原始证据、参考、复算命令与 TOS 归档入口位于研究仓 `results/realtime-c-capture-index/`。

本次填ACT/DP原生实时结果、ACT完整Paused与附加150 ms组和5090延迟；DP完整Paused、DP附加延迟、Equal latency、原生执行器及真机完整组仍缺失。ACT Paused直接复用已验收scene0，没有重复执行；附加150 ms组的1400场均正常退出，全部原始查询和指令已审计。DP的全零场景bootstrap退化为[0,0]，正文另报描述性的Wilson区间0–0.274%；单方法区间不是方法差值的配对区间。DP仅T4_sphere有6次被动接触，不能把该任务均值填为完整13任务误差。

相机输入另经[研究仓 8f4546be](https://github.com/ArrebolBlack/se3-wam-research/tree/8f4546be)复核：BASE1共同协议记录七个已训练端点的agentview输入及缺失视图处理，未取得端点的+SE(3)腕部输入保持未确认。合并时保留负责人新稿对CV-input段及表格行的删除；CV技术时序核对留在研究记录，不重新加入论文。
