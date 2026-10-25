# 附加延迟曲线：来源与复现

数据唯一来源为 `tables/supp_latency.tex`（A1／INFER0 实时协议、1,400 个留出场景）。填数时同步更新
`data/latency.csv`：每个方法、每个附加延迟一行，SR 空白表示待测；`sr_lo`/`sr_hi` 只给 \ours 填三个训练种子的最小与最大值。

序列：\ours，以及每类基线中最强的一个——反应式（ACT）、VLA（π0.5+SE(3)）、动态 VLA（DynamicVLA）、
图像空间 WAM（DreamVLA 与 OpenWAM-α 中较强者，填数后在 `plot_latency.py` 的 `image_wam` 一项改名）、
动态 WAM（DynamicWAM+SE(3)）。Diffusion Policy 在 0/150 ms 均为 0%，不画。全部方法的数值留在附录表中。

规则：只连接相邻的已测延迟点，不插值未测点；末端直接标注方法名，不用图例；纵轴固定 0–100%。
\ours 用与 Fig. 5 热图“Better”端相同的蓝色（#1674AB）。

在本目录运行（字体优先 Arial，缺失时用度量兼容的 Liberation Sans）：

```
python plot_latency.py --output .
```
