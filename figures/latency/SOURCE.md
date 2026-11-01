# 附加延迟图：来源与复现

绘图直接读取 `tables/supp_latency.tex`，不维护第二份数值 CSV。当前数据由[正式结果接收](../../results/realtime_c/INDEX.md)追溯至Research的2026-11-01验收。图例保留ACT、DP、π0.5+SE(3)、DynamicVLA、OpenWAM-α、DynamicWAM+SE(3)、SE(3)-WAM七条既有序列；OpenWAM采用官方缓存与编译组。最终模型仍用空心标记和 † 注明待测，坐标区不绘制虚构点。其他基线及OpenWAM关闭加速组在完整表中保留。

图中六个基线各有0/150 ms两个实测点；50/100/200 ms与最终模型继续待测。采用一个训练种子的1400场结果，不把场景区间解释为训练种子方差。

仅连接扫描网格 0、50、100、150、200 ms 中相邻且都有测量的点，缺失值保持 NaN，不跨缺口连线。未接收逐种子区间，因此不画置信带，也不预先宣称某个基线最强。纵轴固定 0–100%。+150 ms 虚线对应主表的条件，不编码结果。

在论文根目录运行 `python figures/latency/plot_latency.py`，同时输出中英文 PDF/SVG/PNG。宽度 3.25 in，高 2.45 in，文字 7–7.5 pt。依赖 Matplotlib 见根 requirements.txt，图内中文字体为 Microsoft YaHei。
