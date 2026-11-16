# B. 暂停世界改变排序图：说明与提案（2026-11-16）

## 1. 这幅图回答的问题

如果评测在推理期间暂停世界（DOMINO、PhysMani-Bench 的默认做法），方法排序是否与实时（Native）下不同？
支撑正文 `sections/experiments.tex` “Effect of inference latency” 中的
*Paused evaluation therefore overestimates slow policies and changes the ranking of methods.*
Table 1 按方法族排列、不按 SR 排列，读者在表中看不到重新排序；这幅图补的正是这一点。

## 2. 定稿：方向 C（排序哑铃）

文件：`make_rank_shift.py` → `rank_shift.{pdf,svg,png}`，3.25 × 1.86 in（234 × 134 pt）。

- 行按 Paused SR 降序（即 Paused 名次）。空心灰圈 = Paused，方法色实心圆 = Native，箭头从 Paused 指向 Native。
  空心点沿行形成整齐的递减列，实心点错位，错位本身就是重新排序；右侧 “Paused 名次 → Native 名次”给出精确值。
- Paused 用中性灰空心，不用方法色空心：Fig. 5 中“方法色空心”表示 Base/off 变体，避免同一编码在两图中含义不同；
  也不用 Fig. 4 “World pauses” 的红色，避免与 FoveaWAM 的 tab:red 冲突。
- 名次列不用红绿着色（旧 (c) 的红绿暗示“升名次 = 更好”，且与方法红色冲突）。
- 变化小于 4.5 点的行不画箭头（箭头会被标记遮住）：DynamicVLA −3.8、ACT +1.0、DP −0.1。
- 字号 7 pt（表头、名次同），坐标轴 0.55 pt，方法线 0.85 pt，FoveaWAM 1.2 pt 并加粗，网格 `#E5E5E5` 0.35 pt，与 Fig. 5 一致。

名次按 Table 1 一位小数 SR 的序数（用户 11-16 决定，与表格一致）。脚本在出现一位小数并列时报错。

## 3. 比较过的方向（`candidates/`）

| 方向 | 结论 |
|---|---|
| A 斜率图（SR 刻度，两侧名称+数值） | 编码上最直接（线交叉即排序变化），但第一眼文字过多、中间斜线区仅占宽度约 18%，蓝线交错成团，标签被推离真实高度。未采用。 |
| B 散点 + y=x | 留白好、OpenWAM 同策略对照最突出；但排序变化要读者心算，“slow”也未编码，且需近方形（约 184 pt 高）。未采用。 |
| C 哑铃（定稿） | 用户评价最好看、最直观看出 reorder；与 Fig. 5 / 原 (c) 视觉语言一致；最省版面。 |

`fig_rank_disp.png` 被否决的原因用户未说明，本图未据此做推断。

参考论文：本次会话没有浏览器，**没有查看任何参考论文原图**，因此不声称借鉴了 Recht et al. 2019、Taori et al. 2020 等论文的具体图。
B 与“旧评测 vs 新评测 + y=x”的思路同构，仅此而已。

## 4. 数据来源与核对

- `results/realtime_c/table1-20261104.json`（Native/Paused SR、边际区间、p95）；`rank_data.load()` 逐项对照
  `tables/main_results.tex` 一位小数，不一致即报错。
- `results/realtime_c/native-per-task-20261104-scenes.csv`：逐场景结果可精确复现 11 个方法的 Native SR。
- 名次变化：π0.5+SE(3) 2→3，π0.5 3→4，DynamicWAM+SE(3) 4→7，OpenWAM-α 5→6，OpenWAM-α (off) 6→11，DynamicVLA 7→5，PUMA 8→2，ACT 10→8，DP 11→10；FoveaWAM 1→1，DynamicWAM 9→9。

## 5. 解释边界（图注须守住）

- **差距不到 1 点处的先后无意义**：Paused 下 OpenWAM-α 58.7 / (off) 58.4；Native 下 DynamicWAM+SE(3) 41.7、ACT 41.6、DynamicWAM 41.1。
  场景 bootstrap 区间约 ±2 点。图注已写明。
- **交接文档有一处需更正**：B_rank_shift.md 称 PUMA 与 π0.5+SE(3) 的 Native 区间不重叠，实际边际区间重叠（59.4–63.2 与 56.6–60.9）。
  按附录口径（任务内重抽场景、各方法联合）做配对 bootstrap（20,000 次，`rank_data.native_paired_bootstrap`），
  PUMA − π0.5+SE(3) = +2.6，95% 区间 [0.1, 5.1]，差异成立但余量很小。正文“falls behind PUMA”可以保留，不宜加强语气。
- Native 配对名次区间：除上述三方并列为 7–9 外，其余均为单一名次。Paused 逐场景数据仓库内只有 ACT、DP，未做 Paused 配对分析。
- Paused 不是上界（重规划频率也变了，PUMA 在 Native 下反而高 8.3）；跨方法差异不是单变量因果，唯一干净对照是 OpenWAM-α 两种部署。
  图注只说“改变排序”，不说“由延迟造成”。

## 6. 英文图注草稿（见 `figure.tex`）

> **Pausing the world changes the ranking.** SR on \bench with the world paused during inference (hollow) and at native latency (filled), sorted by Paused SR. Right: ranks by the SRs in Table~\ref{tab:main}; gaps below 1 point are within the 95\% intervals.

单栏排版为 3 行。若版面允许，可在第二句后加 “Arrows point from Paused to Native.”（+1 行）。

## 7. 放置建议与实测版面

在本仓库副本中把 `figure.tex` 插到 “Effect of inference latency” 段前，完整编译 `main.tex` 实测（未改动仓库正文）：

- 浮动体落在第 7 页右栏顶部；图 + 3 行图注 + 浮动间距 **约 201 pt**（Table 2 标题由 y=73.6 下移到 274.9）。
- 原第 8 页右栏空余约 117 pt；插图后正文溢出到第 9 页约 **116 pt（约 10 行）**，Conclusion 落在第 9 页。
  比“201 − 117”多出的约 35 pt 来自浮动体重排（Fig. 7 真机图与 Table 2 位置变化）。
- 预览：`layout_preview_p7.png`（第 7 页整页）、`layout_preview_crop.png`（右栏局部，印刷尺寸可读性检查）。

建议：**正文独立单栏小图**，放在第 7 页 “Effect of inference latency” 旁。理由：排序改变是 OnTimeBench 存在意义的核心证据之一，
这幅图提供 Table 1 给不了的重新排序信息；放附录会让这句论点只剩文字。代价是需删约 10 行正文，由主对话统一取舍。

备选：
1. 并入通栏 Fig. 5 作为面板（参照 `../scripts/fig_latency_wide.py` 的 (c)）。省掉单独的图注与浮动间距，但 Fig. 5 要改成跨栏图，
   需要与 A/C 图的放置一并重排，尚未实测。
2. 移入附录，正文保留现有句子与 Table 1。版面零成本，但论点只剩文字支撑。

## 8. 对正文的修改提案（不直接改）

- `sections/experiments.tex` 第 48 行：在 “changes the ranking of methods” 后加 `(Fig.~\ref{fig:rank_shift})`。
- 同段 “For example, $\pi_{0.5}$+SE(3), the strongest baseline with the world paused (76.0\%), loses 17.3 points at native latency and falls behind PUMA.”
  图已显示这一交叉，可压缩为 “e.g., $\pi_{0.5}$+SE(3) falls from second to third, behind PUMA (Fig.~\ref{fig:rank_shift})”，约省 1 行。
- 若采用本图，它成为 Fig. 6，原 Fig. 6（真机，`figures/Fig6/`）顺延为 Fig. 7；图号与目录的对照表需更新。

## 9. 与其他图的一致性

- 方法颜色读自 `figures/method_colors.json`，与 Fig. 5、C 图一致；本图不用 p95，与 C 图无数值重叠。
- 若 C 图用方法色标 p95，本图的方法色含义一致（方法身份），不冲突。

## 10. 需要用户决定

1. 放置：正文独立小图（删约 10 行）/ 并入通栏 Fig. 5 / 附录。
2. 图注是否加 “Arrows point from Paused to Native.”（+1 行）。
3. 英文版确认后出中文版（`--lang zh`，需本机 Microsoft YaHei）。

## 11. 复现

```
python make_rank_shift.py                          # Windows，Arial，英文
python make_rank_shift.py --font "Liberation Sans" # Linux 预览（本目录现有导出即此字体）
python make_rank_shift.py --lang zh                # 中文
python rank_data.py                                # 打印数据、配对名次区间与核对结果
```
当前 PDF/SVG/PNG 在 Linux 上用 Liberation Sans 生成（`pdffonts`：字体已嵌入），提交 Overleaf 前请在 Windows 上用默认 Arial 重新生成一次。
