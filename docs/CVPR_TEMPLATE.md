# CVPR 模板来源与工作稿配置

当前稿件面向 CVPR 2027，使用官方 CVPR author kit 的最新正式 LaTeX release
[CVPR2026-v1(latex)](https://github.com/cvpr-org/author-kit/releases/tag/CVPR2026-v1%28latex%29)
作为排版基础。`cvpr.sty` 与 `ieeenat_fullname.bst` 从该 release 原样引入，保留文件内的来源注释。

截至 **2026-10-16**，[CVPR 2027 Call for Papers](https://cvpr.thecvf.com/Conferences/2027/CallForPapers)
已经发布；[2027 Author Guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)
尚不可用，author kit 尚无正式 2027 release。因此，`confYear=2027` 是本项目的工作稿配置，
此版本不称作“官方 CVPR 2027 模板”。正式 2027 author kit 发布后，应按该版本和最终投稿要求
更新、重编译和检查；当前构建成功不证明最终页限或 2027 投稿合规。

## 当前入口与设置

- [main.tex](../main.tex) 与 [supplementary.tex](../supplementary.tex) 各自使用 `article` 的
  `10pt,twocolumn,letterpaper`，从 [preamble.tex](../preamble.tex) 加载共同的 `cvpr` review 配置和记号。
  review 模式保留匿名作者区、行号、页码和 confidential review 标记。
- `\def\confName{CVPR}`、`\def\confYear{2027}` 设置目标会议显示。
- `\def\paperID{*****}` 是未分配投稿编号的占位；获得正式编号后再替换。
- 参考文献使用 `ieeenat_fullname`，正文引用由模板自带 `natbib` 处理。
- 模板替换不改变研究方法、结果输入、图源或待验证状态；红色 pending 占位必须由实际结果解决。

本仓库仅维护这一条模板路径。原 ICRA 专用的 `ieeeconf.cls` 和 `IEEEtran.bst` 已移除。

## 构建与检查

构建依赖和完整命令由[根目录构建入口](../README.md#构建)维护：

```powershell
./scripts/build.ps1
```

该命令读取历史 pending 或指定 manifest，生成图像 PDF，再编译英文正文、独立补充和中文审读稿。
中文稿使用 XeLaTeX 和 Windows 字体，仅供审读，不计入 CVPR 正文页数。当前实测表由 Research 摘要独立导出，见[证据路由](writing/evidence_map.md)。
`-Clean` 清理三份文档的编译产物。只重排英文稿已有输入时可运行：

```powershell
$env:Path = "C:\Strawberry\perl\bin;$env:Path"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex supplementary.tex
```

检查三份 PDF 的所有页：双栏布局、图表可读性、匿名信息、引用和未解决占位。
主文正文边界由 `main:body-end` 标签与 PDF 联合核对，参考文献额外页不得出现正文或附录。
补充材料独立编号 A–G，引用主文章节时使用阅读表中的固定节号；主文章节重排后同步核对。
当前图源由[图索引](../figures/INDEX.md)路由，旧 PPTX 不作为新 Study 图的同步事实源。

改为终稿模式需根据正式会议要求更改 `cvpr` 选项，并填写作者与单位；不可仅删除行号和页码来
模拟终稿。本文档只维护模板来源和配置，写作风格见[写作索引](writing/INDEX.md)。
