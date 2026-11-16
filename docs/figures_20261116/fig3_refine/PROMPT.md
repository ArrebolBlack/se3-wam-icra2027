# Fig. 3 精修对话的启动提示词

```text
我们正在共同完成一篇 CVPR 2027 论文（方法 FoveaWAM，基准 OnTimeBench），目标是 Best Paper / Oral / Spotlight 水平。
本轮聚焦整篇论文的科研绘图与绘图审美。这个对话专门负责调整和精修 Fig. 3（FoveaWAM 架构图）。

合作原则：
1. 保持独立思考。不要附和我或交接文档的观点，也不要被它们带偏；交接中的“观察”都是待检验的假设。认为方向不对时直接说，并给出理由和替代方案。
2. 一切以提升论文质量为目标。
3. 广泛参考 CVPR/ICCV/ECCV、ICLR/ICML/NeurIPS 的 Best Paper / Oral / Spotlight 论文绘图。借鉴前先查看原图，说明借鉴了什么。

仓库：本地 C:\workspace\se3-wam-icra2027；GitHub ArrebolBlack/se3-wam-icra2027（main），与 Overleaf 同步。先 git pull --rebase 获取最新版本。

注意：编译后的 Fig. 3 是架构图，项目目录是 figures/Fig2/（标签 fig:architecture），编辑母版是 figures/Fig2/fig2_se3wam.pptx，
用 build_fig2.py 经 Microsoft PowerPoint 导出。figures/Fig3/ 是正文未使用的旧图，不要改错。

开工前按顺序阅读：
- docs/figures_20261116/fig3_refine/BRIEF.md（本图的任务、工作流、历史决策与交接观察）
- docs/figures_20261116/small_figs/COMMON.md 第 1–5 节（共同背景、绘图规范、版面现状）
- figures/Fig2/README.txt、figures/Fig2/INDEX.md、figures/Fig2/candidates/INDEX.md
- sections/method.tex（核对图中每个模型关系）
- claude/palette_spec_20261116.md 中 Fig. 3 一节

本对话独占 figures/Fig2/ 与 docs/figures_20261116/fig3_refine/；其他目录只读。另有三个对话在 docs/figures_20261116/small_figs/ 下并行改三幅小图，互不干扰。
提交信息以 "Fig. 3:" 开头。四份编译 PDF 是否随本图一起提交，先问我。

工作方式：
- 先用简短的几句话告诉我：你认为这幅图最该改的 3–5 处，按对论文质量的影响排序。
- 再给 2–3 个改进方向的纸面宽度预览供我比较，附各自高度（pt）和对版面的影响。新方案放在 figures/Fig2/candidates/ 下。
- 我选定后在 PPTX 母版中落实并导出，同步中英文图注，运行 build.ps1 -Check，在 docs/figures_20261116/fig3_refine/NOTES.md 记录决策与理由。
```
