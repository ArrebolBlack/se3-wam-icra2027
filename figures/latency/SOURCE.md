# 延迟与策略排名图：来源与复现

绘图读取完整精度估计和场景区间，并与 Table S5 的一位小数逐点核对。BF16 Full last 的 0 与 150 ms 点与 Table 1 共用，五档延迟均使用同一权重和同一批场景。原始来源见[结果入口](../../results/realtime_c/INDEX.md)。

左侧为 ACT、DP、DynamicVLA、PUMA、OpenWAM-α 官方加速及 off，右侧为 π0.5 与 DynamicWAM 各自加入 SE(3) 历史前后的曲线。两面板共用 BF16 Full last 的实线圆点。该评测沿用编译 BF16/Euler5 的 900 次 RTX 5090 计时回放（p95 15.113 ms），输入为单路 RGB-D 和仿真目标位姿。每点为单训练种子的 1,400 场结果。

各序列连接 0–150 ms 的四个实测点（`PLOT_XS`；+200 ms 档只列于 Table S5，原因见补充材料时延小节），95% 区间显示为逐点误差棒。区间由 10,000 次任务分层场景 bootstrap 计算，两面板共享 0–100% 纵轴；区间表示场景采样不确定性，不表示训练种子间波动。

当前布局采用作者提供的 `docs/figures_20261116/scripts/fig6_full.py` 三面板方案，尺寸为 3.25 × 4.50 in。上方 (a, b) 分别标注横轴；左侧图例分四行，右侧为 Base／+SE(3) 矩阵和误差棒说明，共用 FoveaWAM 图例居中。这两个面板按[共享配色](../method_colors.json)的 `methods` 取色，保持原有线型、标记和区间编码。曲线完全不透明，主方法线宽 1.2 pt，对照线宽 0.85 pt。字体为 Arial 7 pt，子图编号与标题为 8 pt 粗体；中文文字使用微软雅黑。

下方 (c) 直接读取 [Table 1 数据](../../results/realtime_c/table1-20261104.json) 的完整精度 Paused／Native SR 和原生 p95，以 Paused SR 降序排列并计算两种设置下的名次。空心点表示 Paused，实心点表示 Native，箭头从前者指向后者。方法颜色读取与 Fig. 1(b) 相同的 `categories`；原生名次上升为绿、下降为红、不变为黑。p95 显示为整数毫秒，但排序与正文中 150 ms 门槛的核对使用未舍入数据，因此 DynamicWAM 的 149.6 ms 不计入超过 150 ms 的方法。

在论文根目录运行 `python figures/latency/plot_latency.py`，输出 `latency.pdf`／`latency.png` 及对应中文和 SVG 文件。PNG 为 600 dpi，PDF 为纯矢量。脚本核对 Table S5 与[扫描 JSON](../../results/realtime_c/latency-five-point-20261104.json)的全部 55 个实测点，绘制其中 44 个，并核对 (c) 的 Native SR 与扫描零延迟点一致。

实际折线坐标与误差棒端点在绘图时逐项核对。三面板的尺寸、字体、纯矢量导出与排名核对见 [layout_report.json](layout_report.json)。

2026-11-03 的 `latency_preview`／`latency_preview_zh` 保留作历史合成预览。

制作参考：已核对[CVPR 2027作者指南](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)；版式对照[VAR的Fig. 5](https://proceedings.neurips.cc/paper_files/paper/2024/file/9a24e284b187f662681440ba15c416fb-Paper-Conference.pdf)的并排坐标、字体层级及紧凑图例，以及[VGGT](https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.pdf)的正文图文比例。绘图审查流程参考Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)；作为制作工具记录于此。

本次细线图版还查看了 [Vision Transformers Need Registers Fig. 8](https://proceedings.iclr.cc/paper_files/paper/2024/file/0b408293619f725fd30162af057e531a-Paper-Conference.pdf) 的实测折线与分面、[D-Adaptation Fig. 2](https://proceedings.mlr.press/v202/defazio23a/defazio23a.pdf) 的细线和一致编码，以及 [Rich Human Feedback Fig. 2/4](https://arxiv.org/pdf/2312.10240) 的白底坐标和对齐方式。
