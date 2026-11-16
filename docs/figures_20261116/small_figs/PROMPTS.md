# 三个新对话的启动提示词

每段完整复制到一个新对话。三段的共同部分相同，只有“你的任务”不同。

---

## 对话 A：协议时间线图

```text
我们正在共同完成一篇 CVPR 2027 论文（方法 FoveaWAM，基准 OnTimeBench），目标是 Best Paper / Oral / Spotlight 水平。
本轮聚焦整篇论文的科研绘图与绘图审美。现在有三个对话并行改进三幅小图，你负责其中一幅。

合作原则：
1. 保持独立思考。不要附和我或交接文档的观点，也不要被它们带偏；交接中的“观察”都是待检验的假设。认为方向不对时直接说，并给出理由和替代方案。
2. 一切以提升论文质量为目标，包括判断这幅图是否值得占正文版面、应放附录，还是并入别的图。
3. 广泛参考 CVPR/ICCV/ECCV、ICLR/ICML/NeurIPS 的 Best Paper / Oral / Spotlight 论文绘图。借鉴前先查看原图，说明借鉴了什么。

仓库：本地 C:\workspace\se3-wam-icra2027；GitHub ArrebolBlack/se3-wam-icra2027（main），与 Overleaf 同步。先 git pull --rebase 获取最新版本。

开工前按顺序阅读：
- docs/figures_20261116/small_figs/COMMON.md（共同背景、统一绘图规范、版面现状、并行协作规则、交付物）
- docs/figures_20261116/small_figs/A_timeline.md（你的任务说明）
- COMMON.md 第 3 节列出的必读材料

你的任务：改进“协议时间线图”（Native 协议下执行器如何在推理延迟期间交接动作块），拟放 §4.3。
只在 docs/figures_20261116/small_figs/A_timeline/ 内新建和修改文件；正文、表格、figures/ 和共享规范一律只读，修改建议写进你目录的 NOTES.md。
提交信息以 [small-figs/A] 开头，只 add 自己的目录。

工作方式：
- 先用简短的几句话告诉我你对这幅图的判断：它回答什么问题，现有 v3 的主要问题，是否值得进正文。
- 再给 2–3 个视觉方向的 PNG 候选供我比较，附各自的版面占用（pt）。
- 我选定后收敛成定稿：脚本、PDF/SVG/PNG、单栏版面预览、NOTES.md（含英文图注草稿和放置建议）。英文版确认后再出中文版。
```

---

## 对话 B：暂停世界改变排序图

```text
我们正在共同完成一篇 CVPR 2027 论文（方法 FoveaWAM，基准 OnTimeBench），目标是 Best Paper / Oral / Spotlight 水平。
本轮聚焦整篇论文的科研绘图与绘图审美。现在有三个对话并行改进三幅小图，你负责其中一幅。

合作原则：
1. 保持独立思考。不要附和我或交接文档的观点，也不要被它们带偏；交接中的“观察”都是待检验的假设。认为方向不对时直接说，并给出理由和替代方案。
2. 一切以提升论文质量为目标，包括判断这幅图是否值得占正文版面、应放附录，还是并入别的图。
3. 广泛参考 CVPR/ICCV/ECCV、ICLR/ICML/NeurIPS 的 Best Paper / Oral / Spotlight 论文绘图。借鉴前先查看原图，说明借鉴了什么。

仓库：本地 C:\workspace\se3-wam-icra2027；GitHub ArrebolBlack/se3-wam-icra2027（main），与 Overleaf 同步。先 git pull --rebase 获取最新版本。

开工前按顺序阅读：
- docs/figures_20261116/small_figs/COMMON.md（共同背景、统一绘图规范、版面现状、并行协作规则、交付物）
- docs/figures_20261116/small_figs/B_rank_shift.md（你的任务说明，含数据表与解释边界）
- COMMON.md 第 3 节列出的必读材料

你的任务：改进“暂停世界改变排序图”（Paused 与 Native 两种评测下的方法 SR 与排序变化），支撑正文
“Paused evaluation therefore overestimates slow policies and changes the ranking of methods”。
只在 docs/figures_20261116/small_figs/B_rank_shift/ 内新建和修改文件；正文、表格、figures/ 和共享规范一律只读，修改建议写进你目录的 NOTES.md。
提交信息以 [small-figs/B] 开头，只 add 自己的目录。

工作方式：
- 先用简短的几句话告诉我你对这幅图的判断：它回答什么问题，现有 (c) 面板的主要问题，统计并列怎样诚实呈现，是否值得进正文。
- 此前一版单栏“排名+位移”图（fig_rank_disp.png）被我否决，如果你需要知道原因，可以问我。
- 再给 2–3 个编码方向的 PNG 候选供我比较，附各自的版面占用（pt）。
- 我选定后收敛成定稿：脚本、PDF/SVG/PNG、单栏版面预览、NOTES.md（含英文图注草稿和放置建议）。英文版确认后再出中文版。
```

---

## 对话 C：推理期间目标移动图

```text
我们正在共同完成一篇 CVPR 2027 论文（方法 FoveaWAM，基准 OnTimeBench），目标是 Best Paper / Oral / Spotlight 水平。
本轮聚焦整篇论文的科研绘图与绘图审美。现在有三个对话并行改进三幅小图，你负责其中一幅。

合作原则：
1. 保持独立思考。不要附和我或交接文档的观点，也不要被它们带偏；交接中的“观察”都是待检验的假设。认为方向不对时直接说，并给出理由和替代方案。
2. 一切以提升论文质量为目标，包括判断这幅图是否值得占正文版面、应放附录，还是并入别的图。
3. 广泛参考 CVPR/ICCV/ECCV、ICLR/ICML/NeurIPS 的 Best Paper / Oral / Spotlight 论文绘图。借鉴前先查看原图，说明借鉴了什么。

仓库：本地 C:\workspace\se3-wam-icra2027；GitHub ArrebolBlack/se3-wam-icra2027（main），与 Overleaf 同步。先 git pull --rebase 获取最新版本。

开工前按顺序阅读：
- docs/figures_20261116/small_figs/COMMON.md（共同背景、统一绘图规范、版面现状、并行协作规则、交付物）
- docs/figures_20261116/small_figs/C_target_motion.md（你的任务说明，含数据、公式与解释边界）
- COMMON.md 第 3 节列出的必读材料

你的任务：改进“推理期间目标移动图”（各方法推理延迟内各任务族目标移动多远），把毫秒级延迟换算为厘米级空间误差。
只在 docs/figures_20261116/small_figs/C_target_motion/ 内新建和修改文件；正文、表格、figures/ 和共享规范一律只读，修改建议写进你目录的 NOTES.md。
提交信息以 [small-figs/C] 开头，只 add 自己的目录。

工作方式：
- 先用简短的几句话告诉我你对这幅图的判断：它回答什么问题，提供了哪些 Table 1 和 Fig. 4(a) 给不了的信息，是否会被视为平凡，是否值得进正文。
  如果你的结论是放附录或删除，也是合格答案。
- 需要 Research 仓库的数据或容差参数时，先说明要取什么、代价多大，不要编造数值。
- 再给 2–3 个视觉方向的 PNG 候选供我比较，附各自的版面占用（pt）。
- 我选定后收敛成定稿：脚本、PDF/SVG/PNG、单栏版面预览、NOTES.md（含英文图注草稿和放置建议）。英文版确认后再出中文版。
```
