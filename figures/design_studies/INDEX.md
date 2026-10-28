# 附录设计研究图

- [历史输入与干预](history.tex)、[中文](history_zh.tex)：HISTORY1 输入比较的配对区间与同检查点干预；替代原 `supp_remember` 表。
- [表示与预测路径](prediction_path.tex)、[中文](prediction_path_zh.tex)：BASE2/SCALE0 的三种子点、均值与样本标准差；替代原 `supp_prediction_path` 表。
- [绘图与核对脚本](plot.py)：读取本目录数据，重建两种语言的 PDF/SVG/PNG，核对逐种子均值与标准差。
- [来源及复现](SOURCE.md)、[数据](data/INDEX.md)：核对实验范围或更新图时读取。
