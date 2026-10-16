# 结果输入与事实来源

当前正文和补充表追溯实验原生报告，入口见[证据路由](../docs/writing/evidence_map.md)。Research 拥有实验事实；论文中的表和绘图 CSV 是导出，新接收的最小原件副本单列如下。

- bindings.json：历史 result ID 与 LaTeX 宏映射；维护旧接口时读取。
- pending.json：不含观测值的历史占位输入；默认构建仍读取它。
- [import_results.py](../scripts/import_results.py)：旧 publication manifest 消费器；其存在不证明当前 Benchmark 提供对应生产接口。
- [HISTORY1 GT-history 原件接收](history_gt_e/INDEX.md)：已结束任务的原生结果、预算与配置摘录；核对配对统计及训练履历时读取，实验归属仍为 HISTORY1。
- [历史评测复现材料](replay_materials/INDEX.md)：评测器、任务配置、1,400 个接受场景及有序划分的本地候选包；核对协议与原生解析时读取，尚非匿名公开发布包。

results.tex 保留为空占位的生成文件，不承载本次新表的数值，也不手工回填。当前表的导出与完整来源见[表格索引](../tables/INDEX.md)。尚未完成的实验在正文和补充的对应位置标出。
