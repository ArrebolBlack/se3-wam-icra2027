# B. 暂停世界改变排序图（Paused vs. Native ranking）

先读 [COMMON.md](COMMON.md)。工作目录：`docs/figures_20261116/small_figs/B_rank_shift/`。

## 1. 这幅图要回答的问题

如果像 DOMINO、PhysMani-Bench 的默认评测那样在推理期间暂停世界，得到的方法排序与真实时间（Native）下是否不同？
正文论点（`sections/experiments.tex` “Effect of inference latency”）是：
*Paused evaluation therefore overestimates slow policies and changes the ranking of methods.*
这是 OnTimeBench 存在意义的核心证据之一。图要让读者一眼看出排序变了、谁变了、变化有多大。

## 2. 数据（`results/realtime_c/table1-20261104.json`，与 Table 1 一致）

SR（%）与逐协议场景 bootstrap 95% 区间；p95 为 time-to-action（ms）。

| 方法 | Paused | 区间 | 名次 | Native | 区间 | 名次 | p95 |
|---|---|---|---|---|---|---|---|
| FoveaWAM | 90.3 | 89.0–91.5 | 1 | 82.1 | 80.4–83.8 | 1 | 15.1 |
| π0.5+SE(3) | 76.0 | 74.4–77.6 | 2 | 58.7 | 56.6–60.9 | 3 | 61.2 |
| π0.5 | 66.6 | 64.8–68.4 | 3 | 54.4 | 52.4–56.4 | 4 | 59.6 |
| DynamicWAM+SE(3) | 64.0 | 62.5–65.5 | 4 | 41.7 | 39.9–43.6 | 7 | 153.3 |
| OpenWAM-α | 58.7 | 56.7–60.7 | 5 | 46.1 | 43.9–48.2 | 6 | 151.7 |
| OpenWAM-α (off) | 58.4 | 56.4–60.4 | 6 | 15.8 | 14.4–17.1 | 11 | 466.3 |
| DynamicVLA | 54.9 | 52.6–57.1 | 7 | 51.1 | 49.0–53.2 | 5 | 97.3 |
| PUMA | 53.1 | 51.7–54.6 | 8 | 61.4 | 59.4–63.2 | 2 | 60.6 |
| DynamicWAM | 49.6 | 47.8–51.6 | 9 | 41.1 | 39.0–43.1 | 9 | 149.6 |
| ACT | 40.6 | 38.6–42.8 | 10 | 41.6 | 39.6–43.8 | 8 | 5.8 |
| DP | 32.0 | 29.9–34.1 | 11 | 31.9 | 29.9–33.9 | 10 | 68.9 |

JSON 中的方法键：`se3_wam`、`pi05_se3`、`pi05`、`dynamicwam_se3`、`openwam_official`（OpenWAM-α）、`openwam`（off）、
`dynamicvla`、`puma`、`dynamicwam`、`act`、`dp`。改数据时以 JSON 为准，并核对 `tables/main_results.tex`。

## 3. 解释边界（图和图注都必须守住）

- **名次存在统计并列。** Native 下 DynamicWAM+SE(3) 41.7、ACT 41.6、DynamicWAM 41.1 的区间重叠；Paused 下 OpenWAM-α 58.7 与 off 58.4 重叠。
  对这些方法写成 “7→8” 之类的精确名次是虚假精度。稳健的排序变化有：PUMA 8→2、π0.5+SE(3) 2→3（两者 Native 区间不重叠）、
  OpenWAM-α (off) 6→11、DynamicWAM+SE(3) 4→7。
  上表是逐协议的边际区间；严格判断两方法是否并列需要配对区间。本仓库只有 Native 的场景级数据
  （`native-per-task-20261104-scenes.csv`），Paused 场景级数据只有 ACT 和 DP，其余在 Research 仓库。
- **Paused 不是上界。** Paused 时每 50 ms 重规划一次，反馈频率也变了。PUMA 在 Native 下反而更高（+8.3），不能把 Paused 画成“理想值”。
- **跨方法比较不是单变量因果。** p95 都约 61 ms 的 PUMA 与 π0.5+SE(3) 分别变化 +8.3 和 −17.3。唯一干净的对照是 OpenWAM-α 两种部署：
  同一策略，Paused 下相同（58.7/58.4），Native 下 46.1 对 15.8，只差延迟。
- 与 Table 1 数据重复，所以这幅图必须提供表格给不了的东西（排序交叉一眼可见），否则不值得占版面。

## 4. 现有材料

- 四联候选的 (c) 面板：`../fig4_study/fig_latency_wide.png|pdf`，脚本 `../scripts/fig_latency_wide.py`。哑铃加箭头，按 Paused 名次排列，右侧名次列升绿降红。
- `../fig4_study/fig_rank_disp.png`：单栏“排名 + 位移”方案，用户回复“不可以”，**原因未说明**。动手前可以问用户原因，不要自行推断。
- `../fig4_study/fig_rank_latency.png`：SR 变化对 p95 的散点（较早备选）；`../fig4_study/dumbbell_mock.png`：早期哑铃预览。

## 5. 交接方观察（未验证的假设，请独立判断）

1. **红色一色多义。** (c) 中 FoveaWAM 用 tab:red，名次下降也用红，同一面板里红色有两种含义。
2. **排序变化靠读数字。** 哑铃编码的是 SR 变化量；“排序改变”要读右侧名次列才看得出。斜率图 / bump chart（Paused 与 Native 两列，线段交叉即排序变化）
   可以直接编码排序，但会弱化幅度和区间。
3. **可以借鉴的经典图。** Recht et al.（ICML 2019，*Do ImageNet Classifiers Generalize to ImageNet?*）与 Taori et al.（NeurIPS 2020，effective robustness）
   用“旧评测 vs 新评测”散点加 $y=x$ 线来展示评测协议改变结论，与本图论点同构。x = Paused SR，y = Native SR，偏离对角线即损失，可用 p95 编码颜色或标记。
   这会把延迟也带进来，与 C 图和 Fig. 5 的分工需要想清楚。请查看原图后再判断。
4. Paused 的视觉编码可以考虑与 Fig. 4(a) 的 “World pauses” 呼应，但数据图里颜色已被方法占用，要避免冲突。
5. 11 个方法、两套名次放进单栏会很挤。可以考虑弱化统计并列的方法，突出稳健变化与 OpenWAM 配对。

## 6. 待决问题（在 NOTES.md 中给出你的判断）

- 哪种编码最能直接支撑“changes the ranking”：哑铃、斜率 / bump、散点 + $y=x$，或其他？至少做 2–3 个候选给用户比较。
- 怎样诚实呈现并列：区间、并列名次、灰化，还是只标稳健交叉？
- 独立单栏图、并入 Fig. 5 作面板，还是用一句正文加 Table 1 取代？

## 7. 交付

按 COMMON §7。若做并入 Fig. 5 的面板版，面板几何参照 `../scripts/fig_latency_wide.py`。
