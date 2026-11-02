# 附加延迟图：来源与复现

绘图读取[已接收的50点JSON](../../results/realtime_c/latency-five-point-20261102.json)中的完整精度点估计和场景区间，并逐点核对与 `tables/supp_latency.tex` 的一位小数一致。数据由[正式结果接收](../../results/realtime_c/INDEX.md)追溯至Research的2026-11-02五点验收，不另建数值副本。

单栏图沿用Research验收预览的左右双面板布局：左侧展示ACT、DP、DynamicVLA、PUMA、OpenWAM-α官方加速及off配置，右侧展示π0.5与DynamicWAM各自加入SE(3)历史前后的配对曲线。图表均覆盖十配置50点，每点采用一个训练种子的1400场结果；0／150 ms复用 Table 1，50／100／200 ms来自四个 standard 任务的42000场新增评测。PUMA使用单agentview E7 rollout，但沿用官方D14三相机计时预算；最终FoveaWAM仍待补。

仅连接扫描网格0、50、100、150、200 ms的实测点，不作平滑或单调约束。阴影直接使用接收JSON中的95%区间：10000次按任务分层的场景bootstrap，不表示训练种子方差，也不是两条曲线差值的配对区间；图注据此使用task-stratified scene-bootstrap。两面板共享0–70%的纵轴以容纳PUMA的上界。

2026-11-02精修保持3.25 in单栏宽度，将图高从2.65 in收至2.38 in；曲线区高度由1.18 in增至1.45 in。横轴标题共享，面板标题左对齐；左侧图例合并ACT/DP所在行，右侧以方法为行、Base与+SE(3)为列。配对曲线使用相同颜色和形状，以虚实线及空实心区分；OpenWAM关闭加速组同样用虚线空心菱形。六种方法族颜色对白底的sRGB对比度为4.26–6.17，灰度下仍有点形及线型提示。

在论文根目录运行 `python figures/latency/plot_latency.py`，同时输出中英文矢量PDF、可编辑SVG和600 dpi PNG。字体7–7.5 pt，主线1.1 pt；英文与方法名用Arial，中文用Microsoft YaHei，数学符号用STIX。中英文TeX均使用单栏 `figure`，英文按 `\columnwidth`、中文按3.25 in放置。依赖Matplotlib见根requirements.txt。导出后核对50个绘图点及50组区间、文字边界、字体嵌入、灰度预览和正文实际尺寸。

制作参考：已核对[CVPR 2027作者指南](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)；版式对照[VAR的Fig. 5](https://proceedings.neurips.cc/paper_files/paper/2024/file/9a24e284b187f662681440ba15c416fb-Paper-Conference.pdf)的并排坐标、字体层级及紧凑图例，以及[VGGT](https://openaccess.thecvf.com/content/CVPR2025/papers/Wang_VGGT_Visual_Geometry_Grounded_Transformer_CVPR_2025_paper.pdf)的正文图文比例。绘图审查流程参考Kassis, T., Agarwal, V., He, Y., Patel, D., & Brueckner, A. M. (2026), [Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents](https://doi.org/10.48550/arXiv.2609.00065)；作为制作工具记录于此。
