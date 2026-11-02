# 附加延迟图：来源与复现

绘图读取[已接收的45点JSON](../../results/realtime_c/latency-five-point-20261102.json)中的完整精度点估计和场景区间，并逐点核对与 `tables/supp_latency.tex` 的一位小数一致。数据由[正式结果接收](../../results/realtime_c/INDEX.md)追溯至Research的2026-11-02五点验收，不另建数值副本。

单栏图沿用Research验收预览的左右双面板布局：左侧展示ACT、DP、DynamicVLA、OpenWAM-α官方加速及off配置，右侧展示π0.5与DynamicWAM各自加入SE(3)输入前后的配对曲线；图例分列放在各面板下方。图表均覆盖九配置45点，每点采用一个训练种子的1400场结果；0／150 ms复用Table 1，50／100／200 ms来自四个standard任务的37800场新增评测。PUMA与最终SE(3)-WAM在图注中注明待补，表格占位保持不变。

仅连接扫描网格0、50、100、150、200 ms的实测点，不作平滑或单调约束。阴影直接使用接收JSON中的95%区间：10000次按任务分层的场景bootstrap，不表示训练种子方差，也不是两条曲线差值的区间。两面板共享0–60%的纵轴；同一方法族用颜色和虚实线区分。

在论文根目录运行 `python figures/latency/plot_latency.py`，同时输出中英文PDF/SVG/PNG。宽3.25 in、高2.65 in，文字7–7.5 pt；中英文TeX均使用单栏 `figure`，英文按 `\columnwidth`、中文按3.25 in放置。依赖Matplotlib见根requirements.txt，图内中文字体为Microsoft YaHei。
