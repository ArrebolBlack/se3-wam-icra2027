# A. 协议时间线图（timeline）

先读 [COMMON.md](COMMON.md)。工作目录：`docs/figures_20261116/small_figs/A_timeline/`。

## 1. 这幅图要回答的问题

在 Native 协议下，推理耗时 $L_t$ 期间世界继续运动时，执行器怎样交接动作块：
在捕获后第一个控制周期边界 $k_t=\lceil L_t/\Delta_a\rceil$ 交接，跳过已过期的指令 $0\dots k_t-1$，
旧块在推理期间继续执行，新块交接后又开始下一次查询。读者看完应能明白：这个协议对所有方法一视同仁，
慢策略的代价就是“过期指令被跳过”和“更长的开环执行”。

拟放位置：§4.3 Evaluation Protocol 的 “Native latency” 段（`sections/benchmark.tex` 第 36–40 行，目前只有文字）。是否进正文仍待定。

## 2. 必须正确的协议事实（来源：`appendix/benchmark.tex` Executor、Protocols 段）

- 指令 $j$ 对应时刻 $\tau_t+j\Delta_a$；$\Delta_a=50$ ms。交接发生在推理结束后（含恰好结束时）的第一个边界，
  即捕获后 $k_t$ 个周期；从指令 $k_t$ 开始执行。
- 交接后策略重新观测、开始下一次查询；同时上一块继续执行。因此重规划频率由延迟决定。
- 块长为方法自身的 $H_m$（`tables/supp_baselines.tex`：ACT 100、DP 15、π0.5 10、DynamicVLA 20、PUMA 16、OpenWAM-α 32、DynamicWAM 16、FoveaWAM 8）；
  $k_t\ge H_m$ 时整块丢弃。
- 首块到达前、块耗尽时，控制器保持当前手臂目标与夹爪指令，**不重复**任何指令。
- 撞击后抓取任务另有 $d_{\rm task}=50$ ms 执行延迟。没有任何方法做跨块 inpainting（不同于 RTC）。
- Paused：推理不占物理时间，每 50 ms 重规划一次。它同时提高了反馈频率，所以只是参考，**不是上界**。

## 3. 现有材料

- 当前候选 v3：`../fig4_study/fig_timeline_v3.png|pdf`，脚本 `../scripts/fig_timeline_v3.py`，234 × 112 pt，无 Paused 行。
- 较早的 v2：`../fig4_study/fig_timeline_v2.png|pdf`，Paused / 快策略 / 慢策略三条泳道，3.25 × 2.7 in。
- 最早草稿：`../fig4_study/panel_timeline.png`，只能用于追溯。
- 正文 Fig. 4(a) 已用“200 ms 延迟、小球滚 18 cm”对比 DOMINO（世界暂停）与 OnTimeBench（世界前进）。
- 版面讨论中提过含 Paused 的 v3p，但没有文件。

## 4. 交接方观察（未验证的假设，请独立判断）

1. **示例参数混用。** v3 用 $L=152$ ms（OpenWAM-α 的 p95）配 $H=10$（π0.5 的块长）。OpenWAM-α 实际 $H_m=32$。
   示例应取自同一个真实方法，或明确标为示意。
2. **视觉重心可能反了。** “Skipped” 用深灰实心，比 “Executed” 更抢眼；旧块与新块都标 4–7，容易被读成同一组指令；
   旧块左端的浅灰小块没有解释。
3. **缺少物理时间轴。** 只有 $\tau_t$、$\tau_t+k\Delta$ 标签，没有 ms 刻度；“$L$=152 ms”条与 200 ms 交接之间的等待缺口没被点明。
4. **“world keeps moving” 只是一行斜体字。** 论文核心是世界在推理期间运动，图中却没有画出来。可以考虑加一条目标位置细带
   （注意与 C 图的分工，避免重复）。
5. **与 Fig. 4(a) 的关系。** 4(a) 讲“世界会动”，这幅图讲“执行器如何处理延迟”。两者不应重复；若这幅图讲的只是附录文字，可能更适合放附录。
6. 字号 4.9–6.6 pt，低于统一规范。

## 5. 参考方向（需查看原图后再借鉴）

用户此前指定参考 VLASH Fig. 2 与 StreamingVLA 的观测 / 推理 / 执行 / 动作块画法。另可看 RTC（Black et al., 2025，本文引用为 `rtc`）
与 DynamicVLA（本文引用）中的异步执行 / 推理延迟示意，以及顶会论文中的系统时序图。
请自行检索更多 Best Paper / Oral / Spotlight 例子，比较它们怎样处理时间轴、泳道和“被丢弃的部分”。

## 6. 待决问题（在 NOTES.md 中给出你的判断）

- 是否画 Paused 对照行？加了更完整，但会更高，且与 Fig. 4(a) 部分重复。
- 是否画两种延迟（快 / 慢方法）来说明 $k_t$ 的作用，还是只画一个代表性方法？
- 正文还是附录？如果进正文，单栏高度能否控制在约 1.2–1.6 in，图注两行以内？

## 7. 交付

按 COMMON §7。另外需在 NOTES.md 中逐条核对图中每个元素与附录协议的对应关系。
