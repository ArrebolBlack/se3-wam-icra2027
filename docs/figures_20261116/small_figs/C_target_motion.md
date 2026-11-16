# C. 推理期间目标移动图（Target motion during inference）

先读 [COMMON.md](COMMON.md)。工作目录：`docs/figures_20261116/small_figs/C_target_motion/`。

## 1. 这幅图要回答的问题

在各方法的推理延迟内，各任务族的目标会移动多远？目的是把“毫秒级延迟”换算成“厘米级空间误差”，
解释为什么延迟会改变成功率和排序（B 图、Fig. 5）。它是解释量级的图，**不是**因果证据。

## 2. 数据与公式

- 任务速度（`tables/task_definitions.tex`，m/s）：Grasp 0.03–0.20（harmonic 0.03–0.20，其余 0.04–0.15）；Place 0.03–0.06；
  Capture 0.55–1.14（四项任务 0.55–1.12、0.59–1.03、0.59–0.97、0.67–1.14）；Impact 0.12–0.14；Pass 为角速度 2.5–7.5°/s。
- 方法 p95（ms）：ACT 5.8，FoveaWAM 15.1，π0.5 59.6，PUMA 60.6，π0.5+SE(3) 61.2，DP 68.9，DynamicVLA 97.3，
  DynamicWAM 149.6，OpenWAM-α 151.7，DynamicWAM+SE(3) 153.3，OpenWAM-α (off) 466.3。
- 恒速近似：$d\,[\mathrm{cm}] = v\,[\mathrm{m/s}] \times L\,[\mathrm{ms}] / 10$。
- 正文 Fig. 4(a) 写的是 200 ms 内小球滚 18 cm（约 0.9 m/s，落在 Capture 范围内）。本图的数值必须与之相容。

## 3. 解释边界（图和图注都必须守住）

- Capture 速度只取首次离坡前后相邻两帧（50 ms），不能当作全程恒速。色带是任务速度范围，不是置信区间，也不是实测位移分布。
- p95 是首条指令可用的时间；执行器还会把交接向上取整到 50 ms 边界，块内后续指令的开环时间更长。所以 $v\times$p95 **低估**了动作陈旧度。
  JSON 中的 `action_age_*` 字段只有 FoveaWAM 与 π0.5+SE(3) 有值，不能当作全体方法的数据。
- `e_p_mm` 是首次接触时末端相对专家接触位姿的误差，**不是**推理期间的目标位移，不能当作位移实测。
- Pass 是角速度，不能直接放进厘米纵轴；OpenWAM-α (off) 的 466 ms 和 Capture 的大位移会超出合理坐标范围，若截断须在图注说明。
- 跨方法相关不是单变量因果（见 B 文档第 3 节）。

## 4. 现有材料

- 四联候选的 (d) 面板：`../fig4_study/fig_latency_wide.png|pdf`，脚本 `../scripts/fig_latency_wide.py`。灰度色带按族，方法色竖线标 p95，0–160 ms × 0–6 cm。
- 早期单图：`../fig4_study/panel_displacement.png`（0–200 ms，0–23 cm，族用彩色色带，方法用灰虚线）；
  `../fig4_study/fig_rank_disp.png` 的 (b) 面板（该单栏方案被用户否决，原因未说明）。

## 5. 交接方观察（未验证的假设，请独立判断）

1. **可能被审稿人视为平凡。** “距离 = 速度 × 时间”本身不需要一幅图。要占正文版面，图需要一个比较基准，让读者看出某个延迟“够不够”：
   例如夹爪开口余量、抓取或放置容差、Fig. 4(a) 的 18 cm 例子。容差必须来自仿真配置或 Research 仓库，**不能编造**；
   找不到可靠来源就在 NOTES.md 中列为缺项。
2. **数据驱动的替代方案。** 横轴取每个（方法, 任务）的 $v\times$p95，纵轴取 Paused→Native 的 SR 降幅，散点按族上色。
   这样能检验“位移越大、损失越大”。但本仓库只有 ACT、DP 的 Paused 分任务结果（`results/realtime_c/*-paused-per-task.csv`），其余在 Research 仓库。
   这仍然只是相关性，而且会与 B 图的论点重叠。
3. **颜色冲突。** 任务族在 Fig. 4 用核心色（Grasp 蓝、Place 绿、Capture 琥珀、Impact 红），方法在数据图用 tab10（OpenWAM 蓝、PUMA 橙、FoveaWAM 红）。
   两套颜色在同一图里会冲突。(d) 用灰度族带，`panel_displacement` 用彩色族带，各有代价。
4. **标签拥挤。** 约 60 ms 处有 π0.5、PUMA、π0.5+SE(3) 三条线，约 150 ms 处也有三条，同色线无法逐一辨认。可以考虑按方法族或代表方法标注。
5. Capture 占据纵轴，压扁了其他族。可以考虑对数纵轴、分面，或只画到某个容差上限。
6. 与 A 图的分工：A 若加目标位置带，两图会重复。需要与 A 协调（写进 NOTES.md）。

## 6. 待决问题（在 NOTES.md 中给出你的判断）

- 这幅图在正文里提供了什么 Table 1 与 Fig. 4(a) 不能提供的信息？如果答案很弱，建议放附录或删除，也是合格结论。
- 用推导量（$v\times L$）还是去取实测数据？取数需要 Research 仓库，请先说明代价与收益。
- 有无可靠的容差参照线？

## 7. 交付

按 COMMON §7。若做并入 Fig. 5 的面板版，面板几何参照 `../scripts/fig_latency_wide.py`。
