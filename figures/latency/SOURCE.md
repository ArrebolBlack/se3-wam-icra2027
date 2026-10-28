# 附加延迟图：来源与复现

绘图直接读取 `tables/supp_latency.tex`，不维护第二份数值 CSV。数据是 INFER0 实时协议下的 1,400 个留出场景结果。图例保留原图六条计划序列：ACT、π0.5+SE(3)、DynamicVLA、OpenWAM-α、DynamicWAM+SE(3)、SE(3)-WAM，并加入已有实测结果的 DP。五个尚无结果的方法以空心标记和 † 注明待测，不从图例中删掉，也不在坐标区虚构曲线。其余基线在完整表中保留。

目前 ACT 与 DP 各有 0/150 ms 两个实测点，零成功率仍保留。其他方法和延迟点继续待测。

仅连接扫描网格 0、50、100、150、200 ms 中相邻且都有测量的点，缺失值保持 NaN，不跨缺口连线。未接收逐种子区间，因此不画置信带，也不预先宣称某个基线最强。纵轴固定 0–100%。+150 ms 虚线对应主表的条件，不编码结果。

在论文根目录运行 `python figures/latency/plot_latency.py`，同时输出中英文 PDF/SVG/PNG。宽度 3.25 in，高 2.45 in，文字 7–7.5 pt。依赖 Matplotlib 见根 requirements.txt，图内中文字体为 Microsoft YaHei。
