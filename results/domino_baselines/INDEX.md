# DOMINO 论文证据

实验事实与完整方法说明归 [DOMINO-IO0](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/experiments/DOMINO-IO0/DOMINO-IO0.md)。
消费位置为 [正文表 2](../../tables/main_external.tex)及中英文正文、补充材料中的 DOMINO 段落。

## W5 左臂正式结果

- [四方法正式汇总](w5-formal-20261111.json)保存 2026-11-11 验收的原精度分组指标。每方法覆盖相同的 24 任务 × 100 场。

## 历史混合臂结果

2026-11-02 接收 Research `docs/experiments/DOMINO-IO0/results/` 的已验收原件副本。

- [DynamicWAM训练与评测](dynamicwam-native-formal-20261031.json)：Research原路径为 `a8-baselines-20261023/`；40k端点、官方采样覆盖及 `table2` 分组SR/MS。
- [π0.5评测](pi05-native-evaluation-20261101.json)：30k最终EMA、1200场身份与审计、分组及逐任务结果；填表读取 `groups`。
- [PUMA评测](puma-native-evaluation-20261102.json)：所选6k权重、32卡1200场、分组及逐任务结果；填表读取 `groups`。
- [π0.5训练](pi05-native-training-20261101.json)：官方30k预算、global256与最终EMA验证；其中评测待完成字段记录的是当时训练节点的范围，现行评测见上项。
- [PUMA训练](puma-native-training-20261102.json)：16卡/global64、12k早停、6k验证选点及全240来源；其历史评测接续字段不替代上项终态。

历史三方法共用 24 任务 × 2 臂 × 25 场，每方法一个训练 seed，失败场次计入分母。
All 按场次汇总，等价于对 24 个任务等权。正文表 2 显示一位小数，原精度保留在汇总中。
DynamicWAM严格官方采样实际使用1054/1200训练、210/240验证来源；π0.5与PUMA使用全部来源。
各方法保留自己的训练预算、窗口及初始化，比较未配平算力或样本曝光，测试场景未用于选点与早停。
