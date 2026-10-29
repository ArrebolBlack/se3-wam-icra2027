# Fig.6 论文集成

2026-10-25：先在 `codex/fig6-paper-layout` 验证候选排版，随后按用户“重新替换”要求集成到实际主论文目录 `C:/workspace/se3-wam-icra2027` 的 `main` 分支。图中仍保留 AI 标识；没有真实配对 key、方法结果、轨迹或时间测量。

## 来源和可编辑工程

来源为研究工作树 `C:/Users/XUE/.codex/worktrees/fig6-real-trials/se3-wam-research/docs/research_notes/assets/fig6_real_trials/` 的 `outputs/polished` 版本。独立设计、六轮评审、来源审计与真实日志导入接口保留在该工程的 `EVIDENCE.md`、`reviews/` 和 `DATA_CONTRACT.md`。

本目录带入生成原图、面板清单、提示词、排版脚本及 PDF/SVG/PNG，能够独立复现当前布局。脚本仅在重建历史 DejaVu 版本时才需要 matplotlib；当前 Arial 版使用本机字体。生成式素材本身不通过重建脚本重新生成。

## 本次改动

- 双语图源用 `includegraphics[width=\textwidth]` 替换占位，保留标签 `fig:real_trials`。图保持 6.875 × 2.375 in、最小 7.2 pt，不缩小文字、不挤压照片。
- 图注说明六任务和 T5 三事件组织，同时明确两组重复的是 AI 故事板，不是实测配对。
- 删除真机结果句中将 Fig.6b 当作总体任务优势证据的引用。
- 首轮正文溢出到第九页；将图注压缩为两行，并精简相邻真机设置段的重复措辞。保留六任务、三基线、100 条示范、20 次试验、共享 key、FoundationPose 更新位置及含跟踪的端到端口径，中英文同步。未修改全局字号、页边距或其它图。
- 原双语占位进入 archive/placeholder-20261025。

## 复现

```powershell
python figures/Fig6/build_figure.py
./scripts/build.ps1 -Target all
python scripts/check_build.py
```

最终页码、构建检查和独立上下文验收见本文件末尾的验证结果。真实材料和测量接入后仍需重新检查图注、事件语义和最终尺寸；本次不构成科学验收。

## 早期候选稿的验证结果

- 英文主稿 11 页，正文和全部正文浮动体在第 8 页内；Fig.6 在第 8 页。完整稿 24 页，Fig.6 同在第 8 页；中文阅读稿 30 页，图在第 10 页。
- `scripts/check_build.py` 通过：无编译错误、未定义引用、重复标签、缺字或待重编译；中英文数字、结构差异均为 0。英文与完整稿没有 overfull。中文既有附录状态 token 段的 119.94092 pt overfull 在未修改的原仓库同样存在。
- 17 项仓库单测中 16 项通过，`test_every_table_states_its_provenance` 因 `tables/task_definitions.tex` 的既有首行注释不满足前缀约定而失败；在原 main 工作区复现了同一失败，故未顺带修改该表。
- PDF 实际嵌入 12 张照片，图内最小字为 7.20014 pt，保持 495 × 171 pt 比例。已查看英文第 7、8 页和中文图页。
- 无历史独立评审 `/root/fig6_paper_integration_review` 实际查看论文第 7、8 页，确认无拉伸、裁切、文字碰撞，图注为两行、引用正确、AI 身份清楚。发现“六个任务”压缩成“六种运动类型”的轻微措辞回归，已同步改回六个任务；100 条示范、20 次试验和延迟口径保留。
- 整页预览与构建日志位于仓库 `build/fig6-integration/`；主阅读文件为根目录 `main.pdf`、`paper_full.pdf` 和 `manuscript_zh.pdf`。

## 实际主目录替换与最新整稿验证

此前交付只存在于独立工作树，主目录仍调用占位框；这正是用户看到替换失败的原因。本次将已验证的 Fig.6 资产、图源及局部正文调整集成到主目录，保留主线上后来更新的 Fig.2–4 和参考文献，不复制旧候选稿的整篇 PDF。所有阅读 PDF 均从最新主目录重新构建。

- 当前 `figures/Fig6/figure.tex` 与 `figure_zh.tex` 均使用 `includegraphics`，不再调用 `figplaceholder`。
- 实际 `main.pdf` 第 8 页包含 12 个照片对象、合成标识和新的两行图注；标签仍为 `fig:real_trials`。可编辑资产和原图已在本主目录保留。
- 四份 PDF 编译成功，英文无溢出、引用错误、缺字或待重编译；中英文数字、结构差异均为 0。中文原有附录溢出仍存在。
- **最新主稿的正文页数检查未通过：正文结束于第 9 页。** 读取替换前主线 PDF 后确认，它此前也已有第 9 页正文；这是后续全稿集成状态，不可沿用早期候选稿“正文八页”的结论。本次主稿总页数仍为 12 页，完整稿 25 页，中文阅读稿 30 页。
- 当前构建与检查记录为 `build/fig6-integration/main-integration-build.log`、`main-check-build.txt`；实际页预览为 `main-fig6-page8.png`。本次已完成主目录 Fig.6 替换，不宣称全稿通过页数限制或科学验收。
