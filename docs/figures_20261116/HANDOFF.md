# 绘图工作交接（2026-11-16）：全文配色已定稿，Fig. 4 与 benchmark 节配图讨论进行中

给在新机器上接手的对话。本文同时存于项目文档 `claude/figures_handoff_20261116.md` 和仓库 `docs/figures_20261116/HANDOFF.md`。

## 0. 先读什么

1. 项目文档 `claude/palette_spec_20261116.md`：全文配色规范，**已定稿**，仓库副本在 `docs/figures_20261116/palette/palette_spec_20261116.md`。
2. 本文第 2–4 节：Fig. 4 与 benchmark 节配图的讨论状态。
3. Fig. 2（paradigms）的优化另有交接：项目文档 `claude/fig2_paradigms_handoff_20261116.md`。

图号与目录：Fig. 1 在 `figures/Fig1/`，Fig. 2 在 `figures/paradigms/`，Fig. 3（架构）在 `figures/Fig2/`，Fig. 4 在 `figures/Fig4/`，Fig. 5（延迟曲线）在 `figures/latency/`，Fig. 6 在 `figures/Fig6/`。

## 1. 工作方式（用户偏好）

- 先讨论、出预览对比，用户确认后再改文件；修改由单独的“执行对话”完成编译、提交、同步 GitHub 与 Overleaf。
- 保持独立判断，不附和用户；但用户指出问题时，要认真复核，判断错了就直接承认。本轮有几次：一次是在没看原图的情况下断言“同类基准首图都是什么样”；一次是把位移图判为“不如散点图”，后来承认散点图只是把 (a) 的数据换个角度重画；一次是先建议时间线加 paused 行，看到渲染效果后改为不加；一次是先说图下的 capture / handover 文字该保留，复核后改为去掉。
- 用户反感“AI 味”：自选的冷门配色、浅色底配同色标题的卡片、图标堆砌、海报式排版、灰色副标题式的层级、带间隙的格子。偏好标准、常见、含义直观的配色，以及 matplotlib 直出的数据图。
- 拿不准的地方，给 2–3 版并排的设计图让用户选；用户需要看到图才能判断。
- 引用别人论文的图时，必须先看原图，看不到就请用户截图，不要只凭图注推断。
- 加图时要同步精简正文：图和图注负责“怎么做”，正文只写图里没有的内容。

## 2. 已定的事项

- **全文配色**：见规范。示意图和渲染图用核心色板（红 `#C0263A`、蓝 `#2859A3`、绿 `#2E8540`、琥珀黄 `#E69F00`、紫 `#9467BD`，加灰和黑）；数据图用 matplotlib tab10；SE(3) 坐标轴用 tab10 的 RGB 三色；场景流用截取的 turbo 色带。
- **场景流箭头一律不描边**（2026-11-16 用户确认，见规范第 2 节）。已给执行对话提示词：去掉 `draw_real_scene.py` 与 `build_paradigms.py` 中的 `FLOW_BORDER`。
- **Blender 默认渲染参数**：specular 改为 0.10（原为 0.50），其余参数保持原样。传送带泛白是反光太强造成的，不要靠降低饱和度来处理。
- **已经交给执行对话的任务**：Fig. 4 换色（过渡版）、specular 改默认值并重渲染 Fig. 4、Fig. 3 换色（SE(3) Decoder 改为红色）、Fig. 1(b) 和 Fig. 5 改用 tab10 并让 Fig. 5 按方法上色、流箭头去描边、§4.3 协议时间线（见第 4 节）。执行结果以仓库为准，接手时先看 `git log`。
- **benchmark 节配图的拆分方案（用户同意）**：
  - **Fig. 4（通栏，§4.1 Overview）**放两个小图：机制对比（DOMINO 暂停对 OnTimeBench 推进，必须保留）和任务族。14 个任务的图块是否继续作为第三部分保留，用户没有明说，需要确认；按上下文判断应当保留。
  - **新增单栏图，放在 §4.3 Evaluation Protocol**：协议时间线，已定稿为 v6，见第 4 节。

## 3. 讨论过但被否决或悬而未决的

**被否决的：**
- Fig. 4 的方向 C（任务图库为主，下面一条窄带放速度图），见 `fig4_study/fig4_C_mockup.png`。
- Fig. 4 的三种总体架构：中心辐射式、论证链式、按族分列，见 `fig4_study/fig4_arch{1,2,3}.png`。
- “What varies across tasks”速度区间图：信息量低。
- 把排名图和位移图并进 Fig. 4 做成 5 图大图：排名是实验结果，会让 11 个 baseline 和 FoveaWAM 在 §4 提前出场，并与 Table 1 重复。
- 排名图 + 位移图单独做单栏图放正文：第 8 页只剩约 117 pt（约 10 行）空白，放不下。

**悬而未决：排名变化与位移图的去处**
- 当前方案：与 Fig. 5 合并为通栏 4 块图，(a) Policies、(b) SE(3) history（原 Fig. 5）、(c) Paused vs. native 排名哑铃图、(d) 推理期间目标位移。样图 `fig4_study/fig_latency_wide.png`，脚本 `scripts/fig_latency_wide.py`（直接调用仓库 `figures/latency/plot_latency.py` 读数据），尺寸 6.875 × 1.90 in。
- 估算：比现 Fig. 5 净增约 90 pt（7–8 行），§5 “Effect of inference latency” 一段可删回约 4 行。若最终放不下，先把 (d) 移到附录，保留 (c)。
- 用户还没对这版表态。
- 相关数据：原生减暂停的成功率差与 p95 的 Spearman ρ = −0.66（n = 11，p ≈ 0.03）；去掉 OpenWAM-α (off) 后 ρ = −0.55。OpenWAM-α 同一策略 p95 152 / 466 ms 时，暂停 58.7 / 58.4%，原生 46.1 / 15.8%。`results/realtime_c/table1-20261104.json` 有 `e_p_mm`，尚未用上。

## 4. 已定稿：协议时间线单栏图（§4.3）

- **定稿 v6**：`fig4_study/fig_protocol_v6.{png,pdf}`，脚本 `scripts/fig_protocol_v6.py`。正式版本已接入 [figures/protocol](../../figures/protocol/INDEX.md)，单栏 3.25 × 1.125 in。
  - VLASH 式画法：格子相邻、细黑边、直角；图例在顶部，文字在前、色块在后；行标签右对齐。
  - 颜色：Skipped 中灰底，Executed 浅琥珀 `#F1CA73`（与 Fig. 3 action token 一致），Replaced 白底；两行格内数字、两个推理区间标签及双向箭头统一使用黑色 `INK`。唯一的强调是红色括号 “planned from the frame at τ_t”。
  - 字体：文字 Arial（与其他图一致），数学符号 Computer Modern（与正文公式一致，mathtext `cm`）。
  - 内容：k_t = 3、k_{t+1} = 2（体现延迟按查询采样），H = 8；推理箭头不拉满，体现 k = ⌈L/Δa⌉ 的取整；下一次查询在交接点开始（appendix 原文 “The policy then observes again”）；底部只有 τ 符号，不加 capture / handover 文字。
  - **不加 paused 参考行**（用户同意）：会切断单一论点，且 Fig. 4(a) 已在世界层面画出暂停。带 paused 行的 v7A（每格都是新 chunk 的 0 号命令）可放附录协议一节，图注要说明“每个周期重新规划、只执行 0 号”。
- **正文与图注**：§4.3 已按用户提供的 LaTeX 将两段合并为一段 “Settings and metrics”，交接规则只留半句并引用图；图注负责交接、跳过、上一个 chunk 继续、下一次查询时刻。正文与附录未引用被删除的 “Native latency” 段落标题，`sec:bench_protocol` 保留。
- **2026-11-16 本地编译检查**：运行 `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/build.ps1 -Target main`。正文超出 8 页，结论末尾 3 行（审稿行号 489–491，约 36 pt 行高）落在第 9 页；第 8 页两栏排满，剩余可用空白约 0 pt。按要求没有继续删减正文。
- **浮动体与字形**：新协议图为 Fig. 5，位于第 6 页右栏顶部。Table 1 仍在第 7 页左栏顶部，Table 2 仍在第 7 页右栏顶部，原 Fig. 5（现 Fig. 6）仍在第 7 页左栏 Table 1 下方；三者位置与修改前一致。新图数学使用 Cmmi10/Cmr10，与正文的 CMMI/CMR 同属 Computer Modern；图中文字为 Arial。
- 早期草稿（v2、v3、v3p、v4、v5）均已被取代。

## 5. 素材与工具

- `docs/figures_20261116/palette/`：配色规范、换色脚本、各项配色决策的对比图。
- `docs/figures_20261116/fig4_study/`：本轮 Fig. 4 和 benchmark 节的全部设计稿。
- `docs/figures_20261116/scripts/`：生成这些设计稿的脚本。它们是在 Claude 的云端工作区里写的，路径（`/home/claude/...`、`/mnt/user-data/...`）需要改成本机路径；字体 Liberation Sans 在 Windows 上换成 Arial。
- 调色台 `http://127.0.0.1:8788/`（在用户本机运行），用法见 Fig. 2 交接文档第 5 节。
- 仓库 `tmp/` 被 gitignore，新机器上不会有；需要的内容已经复制到 `docs/figures_20261116/`。
- `pdffonts main.pdf` 与逐张输入图检查确认：4 个 Type 3 字体对象全部来自 Fig. 1(b) 的 `figures/Fig1/native_tradeoff.pdf`（ArialMT 与 Arial-BoldMT）；协议图没有 Type 3。按本次要求只定位，尚未修复。
