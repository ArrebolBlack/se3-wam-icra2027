# A. Native 协议时间线：工作笔记（候选阶段，2026-11-16）

状态：5 个候选待用户选择（A、B、C 首轮；A2、C2 借鉴 VLASH Fig. 2 后的第二轮）；尚未定稿，无中文版。脚本 `make_timeline.py`（`--variant a|b|c|all --font --lang --output-dir`），
输出在 `out/`。Linux 预览用 Liberation Sans（`--font "Liberation Sans"`），本地 Windows 默认 Arial。

## 1. 这幅图回答的问题

正文 §4.3 用一句话定义了 Native 执行器：“在推理结束后的第一个控制边界交接，从该边界对应的指令开始执行”。
这句话的含义不直观。图要让读者看到：指令按物理时刻编号，所以推理期间到期的指令 $0\dots k_t-1$ 已经过时、被跳过；
旧块在推理期间继续执行，没有停顿；每个块只执行 $k_t\dots 2k_t-1$，后面的被下一块替换。
因此慢策略付出的代价是**开环更长、指令更旧**（每 $k_t\Delta_a$ 才重规划一次，执行的指令基于 $k_t\Delta_a$ 到 $(2k_t-1)\Delta_a$ 之前的观测），
而不是停顿。

Fig. 4(a) 回答的是“世界在推理期间会动”；这幅图回答“执行器怎样把延迟换算成执行哪条指令”。两者互补，不重复。

## 2. 对交接观察的检验

| # | 交接观察 | 结论 | 处理 |
|---|---|---|---|
| 1 | v3 示例参数混用 | 成立：$L$=152 ms 是 OpenWAM-α 的 p95，$H$=10 是 π0.5 的块长 | 示例统一用 OpenWAM-α：$L$=151.7 ms（Table 1 p95），$H_m$=32（`tables/supp_baselines.tex`），$k$=4；B 另用 FoveaWAM：15.1 ms、$H_m$=8、$k$=1 |
| 2 | 视觉重心反了 | 成立 | 执行 = 实心琥珀（核心色板“动作”）；跳过 = 白底灰斜线；被替换 = 浅灰描边并逐渐淡出。最醒目的是实际执行的部分 |
| 3 | 缺少物理时间轴 | 成立 | A/B/C 都把每条指令画在它对应的时刻 $\tau_t+j\Delta_a$，下方有 ms 刻度；152 ms 推理条与 200 ms 交接之间的等待空隙可直接看出 |
| 4 | 应画目标位置细带 | **不同意** | 与 Fig. 4(a)（18 cm 小球）和 C 图（$v\times L$）重复，还会给示意图加第三种编码。改为标注“指令陈旧度”（B 直接写出 50 ms 与 200–350 ms），这正是 C 图应该乘以速度的量（见 §6） |
| 5 | 与 Fig. 4(a) 的关系 | 互补；正是方案 C 的依据 | 见 §4 |
| 6 | 字号过小 | 成立 | 所有文字 ≥ 6.5 pt（格内序号 6.5 pt，标签 7 pt） |

## 3. 候选

| 候选 | 内容 | 尺寸 | 含图注与浮动间距的版面占用（估计） |
|---|---|---|---|
| A 阶梯式 `cand_a_staircase.png` | 每次查询一行，指令画在它对应的时刻；底部是实际执行的指令流 | 234 × 112 pt（3.25 × 1.56 in） | 单栏独立图约 155–165 pt |
| B 快 / 慢双策略 `cand_b_two_policies.png` | FoveaWAM（$k$=1）与 OpenWAM-α（$k$=4）各一条推理泳道和一条执行泳道；右侧注明重规划周期与指令陈旧度 | 234 × 104 pt（3.25 × 1.44 in） | 单栏独立图约 145–155 pt |
| C 替换 Fig. 4(b) `cand_c_fig4b_slot.png`、`cand_c_in_fig4_mock_small.png` | 与 A 相同的内容，按 Fig. 4 左下格（2.40 × 1.45 in）重排 | 173 × 104 pt | **正文净增约 0 pt**（Fig. 4 高度不变；图注改写约 ±1 行） |

| **A2 两块式** `cand_a2_two_chunk.png` | 借鉴 VLASH Fig. 2：上一块 / 新块两行，加一条推理泳道和 ms 轴；新块执行段下方用括号标“捕获后 200–400 ms 执行” | 234 × 92 pt（3.25 × 1.28 in） | 单栏独立图约 135–145 pt |
| **C2** `cand_c2_fig4b_slot.png`、`cand_c2_in_fig4_mock_small.png` | A2 按 Fig. 4(b) 格重排 | 173 × 104 pt | 正文净增约 0 pt |

A 能看到跳过和替换的机制，B 能看到快慢两类策略的代价，二者各缺一面。
A2 比 A 矮 20 pt，信息基本不减：去掉单独的“执行流”一行，因为两行的琥珀格已经首尾相接；
推理泳道上画出下一次查询（200 ms 开始），新块的 8、9 为何被替换一目了然。当前倾向 A2/C2。

## 3b. 用户偏好与 A3（2026-11-16 第三轮）

用户偏好单栏独立图，C/C2 不再推进。用户另给出一张早期草稿（两行块 + 括号直接标注 “overdue, skipped / executed from command 4”）。对比结论：
- 草稿的优点：括号直接标注，不必查图例；“capture / handover” 用文字点明事件；版面简洁。
- 草稿的问题：新块 8、9 画成已执行，与附录“交接后立即开始下一次查询”矛盾（v3 已纠正过）；$L$=152 ms 配 $H$=10，参数混用；跳过用深灰实心，最抢眼；左端浅灰格无解释；没有 ms 轴；“world keeps moving” 与 Fig. 4(a) 重复。
- **A3 `cand_a3_labelled.png`（234 × 75 pt，1.04 in）**：吸收草稿的直接标注与事件文字，去掉图例行；保留 A2 的协议正确性（8、9 被替换，并画出下一次查询）、OpenWAM-α 真实参数、斜线跳过、ms 轴。推理条改为浅灰（`#D4D4D4`），并把 $L_t$ 写在条内，让视觉重心留在琥珀色执行格上。
  含两行图注与浮动间距估计约 120–130 pt。当前推荐 A3。

## 3c. 通用机制图 `protocol_timeline.*`（第四轮，当前主候选）

用户要求：图只讲协议机制，不对应具体方法；重表达、质量、美观与简洁，借鉴 VLASH 审美。脚本 `make_protocol_timeline.py`。
- 符号化：只标 $\tau_t$、$\tau_t{+}k_t\Delta_a$、$\tau_t{+}2k_t\Delta_a$，示例取 $k_t=3$、块长 8，$L_t\approx2.4\Delta_a$（推理箭头止于边界之前，显示向上取整）；去掉 ms 轴和方法名。
- VLASH 式：顶部单行图例；“上一块 / 新块”两行；一格一个 $\Delta_a$（右侧小括号标出）；新块执行段下方括号，文字用深琥珀斜体，类似 VLASH 用彩色斜体标区间。
- 相对 VLASH 的改动：执行用 Fig. 3 动作 token 的浅琥珀 `#F1CA73`/`#B37C00`，跳过用中浅灰实心（比 VLASH 的深灰轻，避免抢重心）；
  加一条 Policy 泳道，三段推理箭头（上一次、本次、下一次），说明“交接后立即开始下一次查询”，从而解释 6、7 为什么被替换。
- 尺寸 234 × 74 pt（1.03 in）；含两行图注与浮动间距估计约 115–125 pt。
- 从 reviewer 角度自查：跳过、执行、替换三种状态在两行中一致；推理期间上一块继续执行（不停顿）；交接向上取整到边界；
  图中未画首块前 / 块耗尽时的 hold、$k_t\ge H_m$ 整块丢弃、Paused，均放图注一句。

## 3d. 第五轮：去 AI 味的精修（当前定稿候选）

文件：`protocol_timeline.{pdf,svg,png}`，234 × 78 pt（3.25 × 1.08 in）；单栏版面预览 `out/layout_preview_column.png`（源 `layout_preview_column.tex`，Times 10 pt 双栏模拟）。

改动与理由：
- **方角格子，取消圆角和浅奶油色。** 圆角加粉彩填充是生成式图的典型样子；方角更像排版好的时序图。
- **全图只用一种强调色。** 只有“执行”用动作琥珀 `#E69F00`；过期为浅灰实心，替换为白底灰框。视觉重心落在真正执行的指令上。
- **时长统一画成尺寸线** |←→|：$L_{t-1}$、$L_t$、$L_{t+1}$ 与 $\Delta_a$ 用同一种符号。取消上一版的圆点加箭头和彩色斜体注释。
- **时间轴移到底部，每个控制周期一个刻度**，主刻度标 $\tau_t$、$\tau_t{+}k_t\Delta_a$、$\tau_t{+}2k_t\Delta_a$，右端尺寸线标出一格等于 $\Delta_a$。
  新块第 $j$ 格正好落在 $\tau_t{+}j\Delta_a$ 上方，直接回应“为何执行 3、4、5 而不是 0、1、2”的误读。
- **推理泳道画出三次查询。** 读者能看出：上一块的 0–2 同样因过期被跳过；$L_t$ 结束后要等到边界才交接（向上取整）；下一次查询紧接着开始，所以 6、7 被替换。
- **图例按重要性排序**（Executed 在前），与格子起点左对齐；文字 7 pt，格内序号 6.8 pt，次要标注不低于 6.5 pt。
- **注释收敛为一句** “open loop”，黑色正体，不再使用彩色斜体。

参考：除用户提供的 VLASH Fig. 2 外，本会话仍无法查看其他论文的原图，因此不声称借鉴。尺寸线和甘特式泳道属于工程制图与系统论文中的通用画法。

### 英文图注草稿（3 行）

> **Native-latency executor.** Command $j$ is meant for $\tau_t{+}j\Delta_a$. A chunk takes over $k_t{=}\lceil L_t/\Delta_a\rceil$ periods after capture, skipping overdue commands, until the next query replaces it.

图中未画、图注里也不写，留给附录：首块到达前与块耗尽时 hold；$k_t\ge H_m$ 时整块丢弃；post-impact 的 $d_{\rm task}$；Paused。
建议正文 Native latency 段末尾加 “(Fig.~X)”。图注较短，可以考虑把正文中 “executes it from the command indexed to that boundary” 一句与图注合并，省 1 行。

### 版面占用

图 78 pt + 图注 3 行约 33 pt + 图注间距与浮动间距约 30 pt，**合计约 140 pt**（单栏独立图，放 §4.3 顶部）。比第 8 页右栏余量（约 117 pt）多约 2 行，需主对话统一删减。

## 4. 放置建议（初判）

推荐方案 C：用这幅图替换 Fig. 4(b) 的任务族环形图。理由如下。
- 环形图只给出各族任务数（5/2/2/4/1），(c) 已按族分组展示了全部 14 个任务，信息重复；“每任务 100 个测试场景”已在图注和 §4.2 中。
- (a) “世界会动”与 (b) “执行器怎样处理延迟”并排，正好组成 \bench 的协议定义。这是 \bench 区别于 DOMINO 的核心贡献，值得占正文。
- 不需要删正文。三幅小图共需约 400–500 pt，而第 8 页右栏只剩约 117 pt。

风险：Fig. 4 不归本对话所有，需由主对话决定；Fig. 4 的字更大更粗，C 需要统一字重；C 的格子较窄，两位数序号偏挤，定稿时只画到序号 11 或去掉序号 ≥ 10 的格子。
若不采用 C，可退而选 A 或 B 作单栏独立图，代价约 150–165 pt；完整版（加 Paused 与 hold 示例）放附录。

## 5. 协议核对（图中元素 ↔ `appendix/benchmark.tex` Executor 段）

| 图中元素 | 附录依据 |
|---|---|
| 指令 $j$ 画在 $\tau_t+j\Delta_a$，$\Delta_a$=50 ms 网格 | “Command $j$ of query $t$ is meant for $\tau_t+j\Delta_a$” |
| 152 ms 推理 → 在 200 ms 交接，$k_t$=4 | “first boundary at or after it ends, $k_t=\lceil L_t/\Delta_a\rceil$” |
| 序号 0–3 斜线（跳过），从 4 开始执行 | “execution continues from command $k_t$” |
| 下一次查询在交接时刻捕获；推理期间旧块继续执行 | “The policy then observes again and starts the next query; meanwhile the previous chunk continues” |
| 8 及以后被替换（$H_m$=32 时大部分指令从不执行） | 由上一条推得：下一块在 $2k_t$ 交接 |
| 固定 $L$ | **示意**：实际每次查询从实测分布中抽样 $L_t$，$k_t$ 会变化（图注需写明） |
| 未画：首块之前 / 块耗尽时 hold；$k_t\ge H_m$ 丢弃；post-impact $d_{\rm task}$=50 ms | 本例中 $2k=8\le H_m=32$，不会出现 hold；写入图注或附录完整版 |
| Paused 未画 | 稳态下等价于 $k$=0：每 50 ms 执行新块的第 0 条，陈旧度为 0。一句图注即可，不必单独占一行 |

## 6. 与 C 图（目标位移）的对齐提案

C 图按 $v\times$p95 计算位移。按本协议，第 $j$ 条指令在 $\tau_t+j\Delta_a$ 下发，并保持到 $\tau_t+(j+1)\Delta_a$；
所以一个块的执行段落在捕获后 $k_t\Delta_a$ 到 $2k_t\Delta_a$ 之间：OpenWAM-α 为 200–400 ms，FoveaWAM 为 50–100 ms，
均远大于 p95（152 / 15 ms）。下发时的陈旧度为 $k_t\Delta_a$ 到 $(2k_t-1)\Delta_a$（OpenWAM-α 200–350 ms）。若 C 图想标“动作陈旧度”，应使用这个区间（仍按固定 p95 示意），
或在图注中说明 $v\times$p95 是下界。请主对话转告 C。

## 7. 参考论文

**VLASH Fig. 2**（Tang et al., arXiv 2512.01031；原图由用户提供，已查看）。该图以 “Prev. action chunk / New action chunk” 两行格子、
顶部一行 Skipped/Executed/Discarded 图例，加上 prediction interval $[t,t+K)$ 与 execution interval $[t+\Delta,t+\Delta+K)$
两个括号，说明朴素异步推理中预测区间与执行区间错位。

- 借鉴：两行“上一块 / 新块”版式、顶部单行图例、短行标签；用括号标出执行区间（A2/C2 的“捕获后 200–400 ms 执行”）。
- 不借鉴：(1) 错位的论点。本基准的执行器按时刻索引指令，跳过过期指令，所以不存在 VLASH 所说的错位；剩下的代价是开环与陈旧，括号据此改写。
  (2) 配色。VLASH 跳过用深灰实心，在小图里比执行更抢眼（即交接观察 2）；本图改为白底斜线，执行用核心色板的动作琥珀。
  (3) 无时间轴的抽象位置。本图加 ms 轴，并把每条指令画在它对应的时刻。

StreamingVLA、RTC、DynamicVLA：本会话无法打开浏览器或下载 arXiv 图片，**尚未查看原图**，不声称借鉴。
目前只读过 arXiv HTML 的图注：StreamingVLA Fig. 1 对比 action chunking 的 halting gap 与流式执行。

## 8. 待用户决定

1. 用户偏好单栏独立图；当前推荐 A3，待确认后定稿。
2. C 方案需要主对话同意改 Fig. 4。
3. 示例是否点名方法（OpenWAM-α、FoveaWAM），还是只写“慢策略 / 快策略”、在图注中给出真实配置。
