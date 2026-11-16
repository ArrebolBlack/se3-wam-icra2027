# D. Fig. 3（FoveaWAM 架构图）调整与精修：交接（2026-11-16）

先读 [../small_figs/COMMON.md](../small_figs/COMMON.md) 的第 1–5 节（项目背景、协作原则、必读材料、统一规范、版面现状）。
本文件只写 Fig. 3 特有的内容。

## 1. 先认清是哪幅图

- **编译后的 Fig. 3 是架构图**：项目目录 `figures/Fig2/`，标签 `fig:architecture`，由 `sections/related_work.tex` `\input`，排在第 4 页，
  通栏 495 × 293.9 pt（6.875 × 4.08 in）。
- `figures/Fig3/` 是旧的“作用于运动目标的原理示意”（`fig:principles`），**当前正文没有使用**，不要改错目录。
- 今天作者已在这幅图上提交过：v27 素材更新、目标网格改橙色、流按时间着色、specular 0.10，以及“LN 标签居中”（`fa6aea6`）。开工前先 `git pull --rebase`。

## 2. 这幅图要承担什么

方法节开头写的是：*We present \ours, a native 4D world–action model that allocates precision by role (Fig. 3).*
读者看完应能回答：

1. 输入按角色分成哪几类：当前 RGB-D 给静态场景，目标位姿历史给目标运动，机器人状态，以及 summary $M$ 和带噪动作 $A$。
2. 世界流与动作流怎样共享注意力（掩码 $S\to S$；$M\to S,M$；$A\to S,M,A$）。
3. 预测按角色分配精度：场景只做稀疏 3D 流，目标做精确的 SE(3) 轨迹。
4. 部署时跳过预测头，世界流每次查询只预填一次 K/V，动作流复用这些 K/V。这一点是 15.1 ms 延迟的来源。

模型事实的权威来源是 `sections/method.tex` 与 `figures/Fig2/README.txt` 的 “Model relationships” 一节。凡是改动画了什么，都要逐条对照这两处。

## 3. 文件与工作流

| 文件 | 作用 |
|---|---|
| `figures/Fig2/fig2_se3wam.pptx` | **唯一编辑母版**（单页原生对象，作者 v24 修订版基础上的 v27） |
| `figures/Fig2/build_fig2.py` | 用 Microsoft PowerPoint（Windows COM）导出 PDF/SVG/PNG，并写 `export_report.json` |
| `figures/Fig2/update_assets.py` | 只按 `assets/geometry_labels.npz` 更新 PPTX 内的示例组与样式，保留版式 |
| `figures/Fig2/render_assets.py` | 用 Research 仓库的 Blender 环境重渲染背景（specular 0.10、roughness 0.34） |
| `figures/Fig2/figure.tex`、`figure_zh.tex` | 中英文图注与标签；两者必须同步（`check_build.py` 会比对） |
| `figures/Fig2/fig2_paper_width.png` | 144 dpi、纸面实际宽度的校样 |
| `figures/Fig2/candidates/INDEX.md` | v14–v17 的排版候选及采纳状态 |
| `figures/Fig2/archive/INDEX.md` | v15–v25 各正式版及更早方案 |

- 最终导出需要本地 Windows 上的 Microsoft PowerPoint。没有 PowerPoint 的环境（例如云端）只能用 python-pptx 修改，再用 LibreOffice 出**预览**；
  预览字体和版式可能有偏差，不能当作终稿导出。
- 新方案先放进 `figures/Fig2/candidates/<主题>_v28/`（带 INDEX.md 与前后对照），用户采纳后再改母版。
  被替代的正式版按目录约定移入 `archive/<主题>_<日期>/` 并更新索引；同时更新 `README.txt`、`INDEX.md`。
- 不改模型事实、不造示例数据；RGB、深度、流、目标轨迹都是实录或其渲染，见 `assets/source.json`。

## 4. 历史决策（避免回到已否决的方向）

- 已采纳：v14 输入与 token 重排；v15 b/c 与 M 角色配色；v23 输入与读出用虚线框分组；v24 作者修订（子图标题下置）；
  v25→v26 全文配色统一；v27 素材更新（见 `README.txt`）。
- 未采纳：v16 多层 Transformer 主干（连续层组与显式重复残差）。v17 WAM 主干分组是中间候选，后续精修已并入正式图。
- 配色已定稿（`claude/palette_spec_20261116.md` Fig. 3 一节）：世界流蓝 `#2859A3`，动作流深琥珀 `#B37C00`，$M$ 紫 `#9467BD`，
  目标与 **SE(3) Decoder** 红 `#C0263A`（用户确认），位姿轴 RGB，流用 turbo 0.12–0.66。重新讨论配色需有充分理由。

## 5. 交接方观察（未验证的假设，请独立判断）

1. **面积分配与贡献不匹配。** 通用 Transformer 内部（LN、Q/K/V、Output proj.、残差 ⊕、×L 括号）占面板 (a) 中部约三分之一宽，
   而贡献所在的按角色输入与读出被挤到两侧。顶会架构图常把通用模块压缩成一个块、放大新颖部分。但 v16 的“多层主干”已被否决，改动前先读 v16/v17 的 INDEX，弄清当时否决的是什么。
2. **印刷尺寸下可读性。** 由 SVG 估算：时间标签（−350/−200/0 ms，+150/+300/+400 ms）和色标约 5.7–5.8 pt，下标 ℓ、+1、u 约 5.0 pt；
   竖排文字约十几处（各编码器/解码器、LN、Q/K/V、Output proj.、两条流名）。请在 `fig2_paper_width.png` 和打印稿上自行确认。
3. **虚线一线多义。** 输入/读出分组框、(b)(c) 外框、Summary M 引线、仅训练使用的读出箭头、红色未来轨迹、(b) 的 K 方向箭头都用虚线。
   而 README 规定“虚线读出 = 仅训练”，读者很难单凭线型分辨。
4. **“部署时跳过预测头”不够醒目。** 这是延迟优势的关键，目前主要靠 (c) 的文字和图注传达。
5. **子图标题位置。** 本图标题放在面板下方（v24 作者决定），Fig. 4、Fig. 5 用左上角 “(a) Title”。是否统一请询问用户，不要自行改。
6. **与 Fig. 1、Fig. 2 的视觉词汇一致性。** 三图都画了目标 SE(3) 与稀疏流，请核对目标网格、坐标轴、流箭头、时间标注是否一致。
7. **高度与全文版面相关。** 通栏图跨两栏，每降低 0.25 in（18 pt），两栏合计约省 36 pt，约 3 行正文。三幅小图正缺版面（COMMON §5），
   但不能以牺牲可读性为代价换空间。
8. 深度图在缩印后几乎是一片浅蓝，信息量存疑；token 列的颜色按来源（蓝/红/灰）分，但它们同属 $S$，请判断这样是否清楚。

## 6. 参考

写作指南“精读来源按用途路由”一节列出的 NWM、PointWorld、LPWM、Cosmos Policy 等，是本项目已精读的架构图范例。
另请自行检索近年 CVPR/ICCV/NeurIPS/ICLR 的 Oral / Best Paper 中世界模型、VLA、扩散 Transformer 的架构图（例如 DiT 的 block 设计图、π0 的架构图）。
核实其获奖或口头报告状态、查看原图后，说明借鉴了什么。

## 7. 协作与提交

- 本对话独占 `figures/Fig2/`（含 `figure.tex`、`figure_zh.tex`）及 `docs/figures_20261116/fig3_refine/`；其余目录只读，对正文的修改建议写进 `docs/figures_20261116/fig3_refine/NOTES.md`。
- 另有三个对话在 `docs/figures_20261116/small_figs/` 下改三幅小图，与本目录不重叠。
- 提交信息以 `Fig. 3:` 开头（与作者现有习惯一致）；推送前 `git pull --rebase`；不 force push。
  四份编译 PDF（main/supplementary/paper_full/manuscript_zh）是否随本图提交，先问用户。

## 8. 交付

1. 先简短给出判断：这幅图最该改的 3–5 处，按对论文质量的影响排序。
2. 2–3 个改进方向的预览图（纸面宽度），附各自高度（pt）与对版面的影响。
3. 用户选定后在 PPTX 母版落实，用 `build_fig2.py` 导出，并更新 `README.txt`、`INDEX.md`、`export_report.json`；
   图注有变化时中英文同步，最后用 `scripts/build.ps1 -Check` 检查。
4. `NOTES.md`：采纳与否决的方向及理由（含参考论文与图号）、模型事实核对清单、待用户决定的问题。
