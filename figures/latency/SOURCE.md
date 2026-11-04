# 附加延迟图：来源与复现

绘图读取[已接收的55点JSON](../../results/realtime_c/latency-five-point-20261104.json)中的完整精度点估计和场景区间，并逐点核对与 `tables/supp_latency.tex` 的一位小数一致。数据由[正式结果接收](../../results/realtime_c/INDEX.md)追溯至Research的C equalaux01六组验收；此前50点数值不变。

单栏图沿用原左右双面板布局：左侧展示ACT、DP、DynamicVLA、PUMA、OpenWAM-α官方加速及off配置，右侧展示π0.5与DynamicWAM各自加入SE(3)历史前后的配对曲线；所选C的五点在两面板共用。图表覆盖十一配置55点，每点为一个训练种子的1400场结果。0／150 ms复用Table 1的实时组；C另三个点来自独立16卡低优任务，合计新增7000个图中组合。PUMA沿用官方D14三相机计时预算，其他基线为双相机计时，C为单RGB-D及仿真目标位姿的原始FP32/Euler5计时。

仅连接扫描网格0、50、100、150、200 ms的实测点，不作平滑或单调约束。阴影直接使用接收JSON中的95%区间：10000次按任务分层的场景bootstrap，不表示训练种子方差，也不是两条曲线差值的配对区间；图注据此使用task-stratified scene-bootstrap。两面板共享0–70%的纵轴以容纳PUMA的上界。

当前布局为3.25 × 2.60 in单栏内左右双面板，横轴标题共享，纵轴以20个百分点为刻度间隔。左侧图例分四行：ACT／DP、DynamicVLA／PUMA、OpenWAM-α、OpenWAM-α (off)；右侧保留Base／+SE(3)矩阵，两组图例之间保留约6 pt净空。底部居中放置两面板共用的FoveaWAM (Ours)图例。配对曲线使用相同颜色和形状，以虚实线及空实心区分；OpenWAM关闭加速组用虚线空心菱形。Ours使用玫红色 `#B53058`、3.8 pt星形点和点划线，以略粗线条突出方法，避免压过基线。

在论文根目录运行 `python figures/latency/plot_latency.py`，同时输出中英文矢量PDF、可编辑SVG和600 dpi PNG。标签7–7.5 pt、区间说明6.7 pt，基线1.0 pt、Ours 1.25 pt；英文与方法名用Arial，中文用Microsoft YaHei，数学符号用STIX。中英文TeX均使用单栏 `figure`，英文按 `\columnwidth`、中文按3.25 in放置。依赖Matplotlib见根requirements.txt。导出后核对55个绘图点及55组区间、文字边界与图例净空、字体嵌入和正文实际尺寸。

2026-11-03的 `latency_preview`／`latency_preview_zh` 使用合成Ours占位值，仅保留历史排版检查，不再被论文引用；脚本已移除占位分支。当前TeX引用 `latency`／`latency_zh` 的真实结果。Table 1的Paused按作者指定采用此前83%原生同步参考，与本图五个实时点无关；本轮共享执行器Paused的82.21%及差异保存在Research验收记录。

制作参考：已核对[CVPR 2027作者指南](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)；版式对照[VAR的Fig. 5](https://proceedings.neurips.cc/paper_files/paper/2024/file/9a24e284b187f662681440ba15c416fb-Paper-Conference.pdf)的并排坐标、字体层级及紧凑图例，以及[VGGT](https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.pdf)的正文图文比例。绘图审查流程参考Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)；作为制作工具记录于此。
