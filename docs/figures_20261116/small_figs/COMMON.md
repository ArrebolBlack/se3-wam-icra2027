# 三幅小图并行改进：共同交接（2026-11-16）

三个新对话各负责一幅小图，同时进行。本文件是三者共享的背景、规范与协作规则；各图的具体任务见
[A_timeline.md](A_timeline.md)、[B_rank_shift.md](B_rank_shift.md)、[C_target_motion.md](C_target_motion.md)。

## 1. 项目与目标

- 论文：FoveaWAM（仓库名沿用 SE(3)-WAM），投 **CVPR 2027**，目标是 Best Paper / Oral / Spotlight 水平。
  基准名 **OnTimeBench**（宏 `\bench`），方法名宏 `\ours`。
- 本地仓库：`C:\workspace\se3-wam-icra2027`（Windows，有 Arial 字体）；GitHub `ArrebolBlack/se3-wam-icra2027` 的 `main`；
  GitHub 与 Overleaf 同步。实验事实以 Research 仓库（`ArrebolBlack/se3-wam-research`）为准，本仓库保存已接收的证据副本。
- 本轮聚焦整篇论文的科研绘图与绘图审美。

## 2. 协作原则（用户要求，三幅图都适用）

1. **独立思考。** 不附和用户或交接方的观点，也不让本文件的倾向左右判断。交接中的“观察”都是待检验的假设；
   认为方向不对时直说并给出理由与替代方案。
2. **一切以提升论文质量为目标。** 包括判断这幅图是否值得占正文版面、该放附录还是并入别的图；不是只把图画漂亮。
3. **广泛参考** CVPR/ICCV/ECCV、ICLR/ICML/NeurIPS 的 Best Paper / Oral / Spotlight 论文绘图。引用某篇论文的图之前**先查看原图**，
   不凭记忆描述；说明借鉴了什么（编码、版式、标注方式），不复制他人图像。
4. 用户偏好（来自此前讨论）：先给可视候选再定稿；标准、常见、直观的配色与 Matplotlib 数据图；
   避免浅底同色标题“卡片”、图标堆砌和海报式排版。

## 3. 必读材料（按顺序）

| 文件 | 读什么 |
|---|---|
| [../HANDOFF.md](../HANDOFF.md) | 此前的候选、版面估算、数据解释边界、已否决方案（第 2–5 节） |
| [../../../claude/palette_spec_20261116.md](../../../claude/palette_spec_20261116.md) | **现行配色规范**（核心色板、tab10 数据图规则、被否决方向）。`docs/writing/v2_figure_specs.md` 与写作指南中的旧语义色表已过时，冲突时以本规范为准 |
| [../../writing/cvpr_ai_writing_figure_guide.md](../../writing/cvpr_ai_writing_figure_guide.md) | “科研画图风格”“Caption 的职责”“交付前的直接检查”三节 |
| `sections/benchmark.tex` §4.3、`sections/experiments.tex` “Effect of inference latency” | 图要支撑的正文论点 |
| `appendix/benchmark.tex` “Real-Time Evaluation and Metrics” | 执行器、协议、延迟测量与指标的权威定义 |
| `tables/main_results.tex`、`results/realtime_c/table1-20261104.json` | Native/+150 ms/Paused SR、95% 区间、p95 |
| `figures/Fig4/ontimebench.png` 与 `figures/latency/`（正文 Fig. 5） | 已在正文的相关图，新图必须与之风格一致且不重复 |

图号与目录不一致：Fig. 1 → `figures/Fig1/`，Fig. 2 → `figures/paradigms/`，Fig. 3 → `figures/Fig2/`，Fig. 4 → `figures/Fig4/`，
Fig. 5 → `figures/latency/`，Fig. 6 → `figures/Fig6/`。

## 4. 统一绘图规范（三幅图必须一致）

正文现有数据图（Fig. 1(b)、Fig. 5）的实际设置，新图沿用：

- **字体**：Arial（本地 Windows 自带）；Linux 上用度量兼容的 Liberation Sans 预览。脚本用 `--font` 参数，缺字体时报错，不静默回退。
  中文版用 `["Arial", "Microsoft YaHei"]`，参见 `figures/latency/plot_latency.py`。
- **字号**（按最终放置尺寸）：正文标签 7 pt；面板标题 8 pt 粗体 `(a) Title`；次要注释不低于 6.5 pt。
  timeline v3 现有 4.9–6.6 pt 的文字低于此线。
- **线宽**：坐标轴 0.55 pt；普通方法线 0.85 pt；FoveaWAM 1.2 pt；网格 `#E5E5E5` 0.35 pt。
- **颜色**：数据图按方法使用 `figures/method_colors.json`（tab10；FoveaWAM `#D62728`；同一方法的配对变体同色，
  用线型与空心/实心区分）。示意图用核心色板：动作琥珀 `#E69F00`，物体运动/world 蓝 `#2859A3`，结构灰 `#6E6E6E`、文字 `#1A1A1A`，
  “World pauses”红 `#C0263A`，“World advances”绿 `#2E8540`；任务族 Grasp 蓝、Place 绿、Pass 紫、Capture 琥珀、Impact 红（同 Fig. 4）。
  新增颜色需说明理由；同一图内一种颜色只表达一种含义。
- **记号**：与附录一致——控制周期 $\Delta_a=50$ ms，捕获时刻 $\tau_t$，延迟 $L_t$，交接周期数 $k_t=\lceil L_t/\Delta_a\rceil$，
  方法块长 $H_m$；设置名 Native / +150 ms / Paused；指标 SR（%）与 p95 time-to-action。
- **导出**：PDF（`pdf.fonttype 42`，纯矢量）+ SVG（`svg.fonttype none`）+ 300 dpi PNG 预览；脚本可重复运行，路径相对脚本位置。
- **数据**：只用真实数据或明确标注的示意；示意值取自真实配置（例如真实的 $H_m$、p95），不造曲线。

## 5. 版面现状（决定三幅图能否都进正文）

- 正文上限 8 页。当前 `main.pdf` 11 页：正文到第 8 页，第 7 页有 Table 1/2 与 Fig. 5，第 8 页右栏为 Conclusion。
  此前测得第 8 页右栏约剩 **117 pt（9–10 行）**，需重新编译测量。
- 一幅单栏小图含图注和浮动间距通常占 130–180 pt。三幅都以独立单栏图进正文，约需 400–500 pt，即要删约 25–30 行正文。
  因此每个对话都要给出**放置建议**：正文独立小图 / 并入 Fig. 5 成为面板（此前的 6.875 × 1.90 in 四联候选）/ 移入附录，并说明论文质量上的理由。
- 最终取舍由用户与主对话统一决定；子对话不改正文。

## 6. 并行协作规则（避免三个对话互相冲突）

- **文件归属**：每个对话只在自己的目录内新建和修改文件：
  - A：`docs/figures_20261116/small_figs/A_timeline/`
  - B：`docs/figures_20261116/small_figs/B_rank_shift/`
  - C：`docs/figures_20261116/small_figs/C_target_motion/`
- **只读**：`sections/`、`appendix/`、`tables/`、`figures/`（含 `method_colors.json`、`latency/plot_latency.py`，可 import 不可改）、
  `main.tex` 等入口、`claude/palette_spec_20261116.md`、本目录的共享文档。认为需要改它们（图注、正文句子、配色规范）时，写进自己目录的 `NOTES.md` 作为提案。
- **Git**：开工前 `git pull --rebase`；只 `git add` 自己的目录；提交信息以 `[small-figs/A]`、`[small-figs/B]`、`[small-figs/C]` 开头；
  推送前再 `git pull --rebase`；不 force push，不提交 `tmp/`。
- **第四个对话**：另有一个对话精修 Fig. 3（架构图），独占 `figures/Fig2/` 与 `docs/figures_20261116/fig3_refine/`，见 [../fig3_refine/BRIEF.md](../fig3_refine/BRIEF.md)。
  Fig. 3 的高度若有变化，会改变正文可用版面（通栏图每降低 18 pt，两栏约省 3 行）。
- **交叉一致性**：B 与 C 共用方法颜色和 p95；A 与 C 都在讲“推理期间世界在动”，A 的示例延迟与 C 的方法标线要能对上。
  需要对齐时在 `NOTES.md` 写明，由主对话汇总。

## 7. 每个对话的交付物

在自己目录内：

1. `make_<name>.py`：可重复生成的绘图脚本（默认 Arial，`--font`、`--lang en|zh`、`--output-dir` 参数）。
2. 定稿候选的 PDF/SVG/PNG；如有 2–3 个方向，各给一张 PNG 供用户比较，再收敛到一个。
3. 把图放进真实单栏宽度（3.25 in）的版面预览，按印刷尺寸检查可读性。
4. `NOTES.md`：这幅图回答的问题；采用与否决的方向及理由（含参考论文与其图号）；数据来源与解释边界；
   英文图注草稿（遵循写作指南“Caption 的职责”）；放置建议与版面占用（pt）；需要用户决定的问题；对正文或其他图的修改提案。
5. 用户认可英文版后再出中文版（`--lang zh`）。

## 8. 交付前自查

数据与源文件一致；记号、单位、时间与附录一致；按最终尺寸文字不小于 6.5 pt、线条与图例可辨；
颜色语义与全文一致且与 Fig. 4、Fig. 5 不冲突；图注不夸大证据（相关不写成因果，Paused 不是上界）；
导出 PDF 可打开、字体已嵌入（`pdffonts` 检查）；只提交了自己目录的文件。
