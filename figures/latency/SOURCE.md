# 附加延迟图：来源与复现

绘图读取[结果JSON](../../results/realtime_c/latency-five-point-20261104.json)的完整精度估计和场景区间，逐点核对 `tables/supp_latency.tex` 的一位小数。十一配置55点均已验收。数据由[结果接收](../../results/realtime_c/INDEX.md)追溯至Research的BF16 C六组验收；此前十配置50点不变。

单栏图沿用左右双面板布局：左侧为ACT、DP、DynamicVLA、PUMA、OpenWAM-α官方加速及off，右侧为π0.5与DynamicWAM各自加入SE(3)历史前后的曲线。C在两面板共用，使用单RGB-D、仿真目标位姿、编译BF16/Euler5、TF32关闭的900次实测计时（p95 15.113 ms），不缩放为固定15 ms。每点为单训练种子的1400场结果，0／150 ms与Table 1共用。PUMA仍用官方D14三相机预算，其他基线仍为双相机计时。

连接0、50、100、150、200 ms网格的实测点，不作平滑或单调约束。阴影为接收JSON中的95%区间：10000次任务分层场景bootstrap，不代表训练种子方差或方法差值的配对区间。纵轴按完整上界向上取整，两面板当前共享0–80%。

当前布局为3.25 × 2.60 in单栏内左右双面板，横轴标题共享，纵轴以20个百分点为刻度间隔。左侧图例分四行：ACT／DP、DynamicVLA／PUMA、OpenWAM-α、OpenWAM-α (off)；右侧保留Base／+SE(3)矩阵，两组图例之间保留约6 pt净空。底部居中放置两面板共用的FoveaWAM (Ours)图例。配对曲线使用相同颜色和形状，以虚实线及空实心区分；OpenWAM关闭加速组用虚线空心菱形。Ours使用玫红色 `#B53058`、3.8 pt星形点和点划线，以略粗线条突出方法，避免压过基线。

在论文根目录运行 `python figures/latency/plot_latency.py`，输出中英文矢量PDF、可编辑SVG和600 dpi PNG。标签7–7.5 pt、说明6.7 pt，基线1.0 pt、Ours 1.25 pt；英文与方法名Arial，中文Microsoft YaHei，数学STIX。中英文TeX为单栏 `figure`，英文按`\columnwidth`、中文按3.25 in。脚本逐点核对55个估计及其区间与共用表格一致。

2026-11-03的`latency_preview`／`latency_preview_zh`为合成预览，不用于当前论文。Table 1 Paused按作者指定使用此前83%同步参考，与本图实时点无关；BF16共享执行器Paused实测82.0%及配对差异归Research验收记录。

制作参考：已核对[CVPR 2027作者指南](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)；版式对照[VAR的Fig. 5](https://proceedings.neurips.cc/paper_files/paper/2024/file/9a24e284b187f662681440ba15c416fb-Paper-Conference.pdf)的并排坐标、字体层级及紧凑图例，以及[VGGT](https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.pdf)的正文图文比例。绘图审查流程参考Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)；作为制作工具记录于此。
