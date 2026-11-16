# 附加延迟图：来源与复现

绘图读取完整精度估计和场景区间，并与 Table S5 的一位小数逐点核对。BF16 Full last 的 0 与 150 ms 点与 Table 1 共用，五档延迟均使用同一权重和同一批场景。原始来源见[结果入口](../../results/realtime_c/INDEX.md)。

左侧为 ACT、DP、DynamicVLA、PUMA、OpenWAM-α 官方加速及 off，右侧为 π0.5 与 DynamicWAM 各自加入 SE(3) 历史前后的曲线。两面板共用 BF16 Full last 的实线圆点。该评测沿用编译 BF16/Euler5 的 900 次 RTX 5090 计时回放（p95 15.113 ms），输入为单路 RGB-D 和仿真目标位姿。每点为单训练种子的 1,400 场结果。

各序列连接 0–150 ms 的四个实测点（`PLOT_XS`；+200 ms 档只列于 Table S5，原因见补充材料时延小节），95% 区间显示为逐点误差棒。区间由 10,000 次任务分层场景 bootstrap 计算，两面板共享 0–100% 纵轴；区间表示场景采样不确定性，不表示训练种子间波动。

当前布局为 3.25 × 2.60 in 单栏，两个面板分别标注横轴。左侧图例分四行，右侧为 Base／+SE(3) 矩阵和误差棒说明。配对曲线使用相同颜色和形状，以虚实线及空实心区分。底部居中为两面板共用的 FoveaWAM (Ours) 图例，使用玫红色实线圆点。字体为 7–8 pt，主方法线宽 1.2 pt，对照线宽 0.85 pt；曲线无平滑或横轴位移，所有线条完全不透明。

在论文根目录运行 `python figures/latency/plot_latency.py`，输出中英文矢量 PDF、可编辑 SVG 和 600 dpi PNG。脚本仍核对 Table S5 与 JSON 的全部 55 个实测点，绘制其中 44 个。[绘图数据](../../results/realtime_c/latency-five-point-20261104.json)

2026-11-16 采用作者通过的 Matplotlib 细线图版。实际折线坐标与误差棒端点已逐项核对，英文、中文导出均为纯矢量；检查见 [layout_report.json](layout_report.json)。

2026-11-03 的 `latency_preview`／`latency_preview_zh` 保留作历史合成预览。

制作参考：已核对[CVPR 2027作者指南](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)；版式对照[VAR的Fig. 5](https://proceedings.neurips.cc/paper_files/paper/2024/file/9a24e284b187f662681440ba15c416fb-Paper-Conference.pdf)的并排坐标、字体层级及紧凑图例，以及[VGGT](https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.pdf)的正文图文比例。绘图审查流程参考Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)；作为制作工具记录于此。

本次细线图版还查看了 [Vision Transformers Need Registers Fig. 8](https://proceedings.iclr.cc/paper_files/paper/2024/file/0b408293619f725fd30162af057e531a-Paper-Conference.pdf) 的实测折线与分面、[D-Adaptation Fig. 2](https://proceedings.mlr.press/v202/defazio23a/defazio23a.pdf) 的细线和一致编码，以及 [Rich Human Feedback Fig. 2/4](https://arxiv.org/pdf/2312.10240) 的白底坐标和对齐方式。
