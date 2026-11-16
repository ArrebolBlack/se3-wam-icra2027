# 绘图工作交接（2026-11-16）

本目录保存 Claude 的配色讨论、Fig. 4 版式探索、timeline 和延迟小图。当前可继续编辑的候选是通栏四联图与 timeline v3；均未替换进正文。此次整理已保存全部 45 个原始文件，并在后续提交中修正当前候选的运行路径、字体依赖和 timeline 标注。原始版本可从 Git 的 “Preserve Claude's November 16 figure studies and handoff” 提交取回。

## 1. 从哪里继续

- [样图索引](fig4_study/INDEX.md)：当前候选、早期方案和被否决的版式。
- [脚本与复现方式](scripts/INDEX.md)：当前两个候选可跨机器运行；其余历史脚本的依赖与限制。
- [配色素材](palette/INDEX.md)：已确认决策的对比图和讨论快照。现行规范以 [claude/palette_spec_20261116.md](../../claude/palette_spec_20261116.md) 为准。
- Fig. 2 的实现状态从 [paradigms 索引](../../figures/paradigms/INDEX.md) 和 Git 历史读取。旧交接提到的 `claude/figures_handoff_20261116.md`、`claude/fig2_paradigms_handoff_20261116.md` 不在本次收到的仓库材料中，不能当作可用入口。

图号和目录不同：Fig. 1 → `figures/Fig1/`，Fig. 2 → `figures/paradigms/`，Fig. 3 → `figures/Fig2/`，Fig. 4 → `figures/Fig4/`，Fig. 5 → `figures/latency/`，Fig. 6 → `figures/Fig6/`。

## 2. 最新候选与讨论结论

### 通栏四联图：拟替换 Fig. 5，尚未插入正文

文件：[PNG](fig4_study/fig_latency_wide.png)、[PDF](fig4_study/fig_latency_wide.pdf)、[脚本](scripts/fig_latency_wide.py)。尺寸为 **6.875 × 1.90 in**，不是已批准的最终版式。

- (a)(b) 沿用现有 Fig. 5 的数据加载器、方法颜色、线型、空心/实心标记与逐点 95% 场景 bootstrap 区间。横轴保留原图的 0–150 ms 范围；55 个原始点仍由加载器对照表格验证，图中不显示 +200 ms。图例共三行。
- (c) 每方法一行：灰色空心点为 paused，方法色实心点为 native，箭头为变化方向。移除了初稿右侧的 p95 列，保留排名变化；升名次为绿，降名次为红。π0.5+SE(3)：2→3；PUMA：8→2；OpenWAM-α (off)：6→11。
- (d) 按任务族的线速度范围画灰度带，方法色竖线标 p95。横轴 0–160 ms，纵轴 0–6 cm。它提供运动量级的解释，不能单独证明 (c) 的排名变化由延迟造成。
- Claude 的叙事顺序是：附加延迟降低成功率 → paused 与 native 排名不同 → 推理等待期间运动的量级。保留 (c) 的优先级高于 (d)；(c) 与 Table 1 数字重复，但强调排序变化。
- 尚未执行的替代方案：用 (c) 方法名兼作图例，仅保留 Base/off 的小图例，估计最多省约 0.15 in；或去掉 (d)，改三联图并把高度降至约 1.75 in。当前没有三联图文件。

复现修正使用 Matplotlib 自带 DejaVu Sans，原稿为 Liberation Sans。为适应字体宽度，(a) 左边距稍增，(d) 标题缩为 “Target motion”；数据、颜色、范围和三行图例保留。脚本支持显式指定已安装字体，不静默回退。

### timeline v3：拟放 §4.3，尚未插入正文

文件：[PNG](fig4_study/fig_timeline_v3.png)、[PDF](fig4_study/fig_timeline_v3.pdf)、[脚本](scripts/fig_timeline_v3.py)。尺寸 **234 × 112 pt，即 3.25 × 1.556 in**，不含 paused 行。

固定示例为 L=152 ms、控制周期 Δ=50 ms、示意块长 H=10，因此 k=4。上一块继续执行，新块在捕获后 200 ms 接管，跳过指令 0–3。附录明确写明在交接后观察并开始下一查询，因此固定延迟示例在 400 ms 再次交接；当前新块只执行 4–7，8、9 被替换。本次纠正了原稿把 4–9 全部标为已执行的问题，补画下一次交接，并缩短原本被裁切的注释。

这是协议示意，不是执行器实测轨迹：实际延迟按每次查询的测量分布抽样，各方法块长不同。图注还需说明首次到达前/块耗尽后的 hold、k≥H 时整块丢弃，以及 post-impact 的额外 50 ms 执行延迟。查询时机已能由现有附录确认，不再列为待作者确认的问题；本次没有检查真实 executor 代码。

`fig_timeline_v2` 保留为历史草稿（3.25 × 2.7 in），同时画 paused、快速策略与慢策略三条泳道。其 200/400 ms 交接与现有附录吻合。更早的 `panel_timeline.png` 仅供追溯，不能代替当前协议定义。

**v3p（含 paused）仅出现在版面讨论中，本次仓库材料没有对应脚本或 PNG/PDF；不能把它记作已完成。**

## 3. 数据来源与解释边界

| 内容 | 仓库内来源 | 使用方式 |
|---|---|---|
| 延迟曲线与区间 | [latency-five-point-20261104.json](../../results/realtime_c/latency-five-point-20261104.json)、[supp_latency.tex](../../tables/supp_latency.tex) | 调用 [plot_latency.py](../../figures/latency/plot_latency.py) 的加载器和线型函数 |
| paused/native SR、p95 | [main_results.tex](../../tables/main_results.tex)、[table1-20261104.json](../../results/realtime_c/table1-20261104.json) | (c) 及历史排名脚本保存当日一位小数快照；后续改数据时需同步 |
| 任务运动范围 | [task_definitions.tex](../../tables/task_definitions.tex) | Grasp 0.03–0.20、Place 0.03–0.06、Capture 0.55–1.14、Impact 0.12–0.14 m/s |
| 方法颜色 | [method_colors.json](../../figures/method_colors.json) | 经 plot_latency 导入 |
| 运行协议和指标 | [正文 benchmark](../../sections/benchmark.tex)、[附录 benchmark](../../appendix/benchmark.tex) | Executor、Protocols、Latency measurement、Metrics 段落 |

这些输入均已在论文仓库中受 Git 跟踪，新机器不依赖 Claude 云端路径或 Research 仓库即可生成当前两个候选。

(d) 的计算是 `d_cm = v_m_per_s × L_ms / 10`，按恒速近似。Capture 的速度取自离坡前后相邻 50 ms 两帧，不能当成整个运动过程的恒定速度；在 60 ms 处得到 3.30–6.84 cm。色带表示任务速度范围，不是统计置信区间，也不是策略查询期间实际位移的观测分布。p95 为首次命令可用时间，执行器交接还会向上取整到 50 ms 边界。

未来图注必须保留这些省略与截断：OpenWAM-α (off) 的 466.3 ms 超出横轴；Pass 的 2.5–7.5°/s 为角速度，不能直接放入厘米纵轴；Capture 超过 6 cm 的部分被截在图外。同色的约 60 ms/150 ms 方法线位置接近，不能声称依靠颜色能逐一辨认所有方法。

Table 1 中 OpenWAM 两种部署保持同一策略：paused 为 58.7%/58.4%，native 为 46.1%/15.8%，p95 为 151.7/466.3 ms。与此同时，p95 都约 61 ms 的 PUMA 和 π0.5+SE(3) 分别变化 +8.3/−17.3 点，说明跨方法相关性并非单变量因果对照。历史散点方案的 Spearman ρ 重算为 −0.663636（11 方法），去掉 off 后 −0.551515（10 方法）；旧记录的 p≈0.03/0.10 本次未复核，不作为已验证证据。

`e_p_mm` 不是目标在推理期间的位移，而是发生接触的回合中，末端相对专家接触位姿的位置误差（placement 有对应定义）。OpenWAM-off/native、DynamicWAM+SE(3)/paused 为 null，另有六个 +150 ms 条目缺失。不能沿用旧交接“每方法、每协议都有，能作为位移实测佐证”的说法。

## 4. 版面估算及尚未执行的工作

下表保留用户转交的 Claude 估算，采用每行约 12 pt；它们**不是插图后实际编译的结果**。本次检查的 `main.pdf` 共 11 页，正文结束于第 8 页，参考文献从第 9 页开始；第 7 页左栏仍是原 Fig. 5，第 8 页右栏仍是 Conclusion。正文文件及这份 PDF 未改动。

Claude 当时量得第 8 页右栏 Conclusion 到 y≈596 pt，栏底≈713 pt，空余≈117 pt（约 9–10 行）。前 8 页缺少可直接回收的零碎短行，因此其建议是删减实质文字，而不是仅压间距。

| 方案 | Claude 当时的空间估计 |
|---|---|
| timeline v3，不含 paused | 图约112 pt，含两行图注/间距约150 pt；相对117 pt空白约差3行 |
| timeline v3p，含 paused | 含图注/间距约170 pt；约差5行，尚无文件 |
| 排名+位移另做单栏图 | 约210 pt；与 v3p 合计约380 pt，约需再删22行，因而未推荐 |
| 最初设想：通栏四联图，高1.75 in、一行图例 | 折成单栏约324 pt，相对旧 Fig. 5 约272 pt净增约4行；加 timeline 后曾估需删5–6行 |
| 实际四联样图：高1.90 in、三行图例 | Claude 估含图注折成单栏约360 pt，相对旧图约270 pt多约90 pt，即7–8行；结果节预计可省4行，再加 timeline，最新总估计需删7–9行 |
| 去掉 (d) 的三联备选 | 设想图高1.75 in，加 timeline 后约需删5行；没有实际排版验证 |

最新的 7–9 行估算取代最初“合并图只净增4行”的乐观估算。跨栏图的真实图注、浮动体间距和双栏换页不能用这张估算表精确推出，迁移字体后的结果也应重编译测量。

下一轮候选操作尚未执行：把通栏图替入 Fig. 5、把 timeline 放入 §4.3、缩短 Native latency 段与 §5 “Effect of inference latency” 段，然后检查第 7、8 页。第 7 页顶部已有 Table 1、Table 2；跨栏浮动体可能挤占其位置。若空间不足，优先保留排名 (c)，将 (d) 移至附录或采用三联版。是否采用这些正文修改仍待下一轮设计决定。

## 5. 此前讨论与决策

- 已确认的配色采用现行规范；Fig. 3、Fig. 4、Fig. 1(b)/Fig. 5 的改色与 specular=0.10 重渲染已经进入当前主线。实现事实从各图项目和 Git 历史读取，不把本目录过渡预览当成当前正文图。
- Fig. 4 的讨论方向为“机制对比必须保留，另一块可放任务族”。14 个任务图块是否继续单列尚未明确，本次没有替作者决定。
- §4.3 增加协议时间线是此前同意的方向，参考 VLASH Fig. 2/StreamingVLA 的观测、推理、执行与动作块画法；当前仍在细化候选。
- 被否决的 Fig. 4 方向 C（任务图库+窄速度带）和三版架构（辐射、论证链、按族分列）均保留在样图目录。“What varies across tasks”速度区间图被认为只重复任务定义表。
- `fig_rank_disp.png` 单栏排名+位移方案收到“不可以”的反馈，原因未明确；后续转向与 Fig. 5 合并的四联图，不能把单栏版的不接受自动解释为四联版已通过或已否决。
- `fig_rank_latency.png` 把 (b) 改为 SR 变化对 p95 的散点，是较早的备选；Claude 后来认为它主要重画 (a) 的数据，价值不如位移解释。

绘图偏好：先给可视候选再定稿；标准、常见、直观的配色和 Matplotlib 数据图；避免浅底同色标题卡片、图标堆砌和海报式排版。引用他人图像需先看原图。当前用户已明确授权检查、保存、提交、合并和推送，无须为这些归档步骤重新确认。

## 6. 本次验证与未覆盖范围

独立只读复核核对了 11 方法的 SR/p95、排名、55 个延迟记录、任务速度范围和附录协议。当前两个候选在本机实际生成 PNG/PDF，核对物理尺寸并查看渲染；全部原始 PNG/PDF 可读取，Python 脚本通过语法检查。目录索引和仓库内数据链接一并补齐。

本次只整理绘图交接和当前候选，没有替换正文插图、压缩论文段落或编译包含新图的全文，没有验证真实 executor。历史方案仅保存，不承诺所有旧云端脚本开箱即用；具体缺失依赖见脚本索引。`tmp/` 是本机临时材料，迁移不依赖其中的文件。
