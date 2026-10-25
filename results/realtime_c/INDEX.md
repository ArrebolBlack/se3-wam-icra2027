# INFER0 实时协议 C：已核验结果副本

实验事实和完整原始数据归[研究仓 49276f6d](https://github.com/ArrebolBlack/se3-wam-research/tree/49276f6d/docs/experiments/INFER0/results/realtime-c-capture-index)及其 INFER0 主文档；本目录只保存论文实际转录的结果。

- [act-report.json](act-report.json)、[act-per-task.csv](act-per-task.csv)：ACT seed0，14 任务各 100 个留出场景，零人工附加延迟；SR、13 任务接触误差、任务内场景 bootstrap 区间、失败类别与回放计时。
- [act-delay-audit.json](act-delay-audit.json)、[dp-delay-audit.json](dp-delay-audit.json)：RTX 5090、batch 1、3 轮各 300 次调用的延迟复算。原始轮次在研究仓 `results/realtime-c-5090/`。

ACT 的 1,400 场全部从原始 query/command/timing 重新审计并与共享参考联结。实际 benchmark 运行版本为 `68a44b06`，其等价实现与上游测试已合并为 `5e5eaa31`。ACT/DP 当前 rollout 的计算设备也是 RTX 5090，物理时钟仍只使用预先测得的延迟样本；调用的现场计算耗时不进入结果。两者只读取 agent-view RGB，DP 读取因果两帧历史。

共享参考中原有的 40 处数值 IK 未解点已全部分类：37 处由两连杆几何必要条件排除，965/990 由覆盖完整关节域及原位姿容差的区间证书排除，926 场景补解成功。原求解器记录保留；两个新排除场景的 ACT 都未发生接触，因此接触误差不变。全部原始证据、参考、复算命令与 TOS 归档入口位于研究仓 `results/realtime-c-capture-index/`。

本次只填 ACT 原生实时结果和 ACT/DP 延迟；DP SR、附加延迟、Paused、Equal latency、原生执行器及真机数据仍缺失。单方法区间不是方法差值的配对区间。
