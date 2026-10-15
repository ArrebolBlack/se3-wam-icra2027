# CVPR 模板来源与工作稿配置

当前稿件面向 CVPR 2027，使用官方 CVPR author kit 的最新正式 LaTeX release
[CVPR2026-v1(latex)](https://github.com/cvpr-org/author-kit/releases/tag/CVPR2026-v1%28latex%29)
作为排版基础。`cvpr.sty` 与 `ieeenat_fullname.bst` 从该 release 原样引入，保留文件内的来源注释。

截至 **2026-10-15**，[CVPR 2027 Call for Papers](https://cvpr.thecvf.com/Conferences/2027/CallForPapers)
已经发布；[2027 Author Guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines)
尚不可用，author kit 尚无正式 2027 release。因此，`confYear=2027` 是本项目的工作稿配置，
此版本不称作“官方 CVPR 2027 模板”。正式 2027 author kit 发布后，应按该版本和最终投稿要求
更新、重编译和检查；当前构建成功不证明最终页限或 2027 投稿合规。

## 当前入口与设置

- [main.tex](../main.tex) 使用 `article` 的 `10pt,twocolumn,letterpaper` 和 `\usepackage[review]{cvpr}`。
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

该命令导入 pending 或指定 manifest、生成图像 PDF，再用 `latexmk -pdf` 编译 `main.tex`。
只重新排版已有输入时也可运行根索引中的直接编译命令。检查实际生成的 `main.pdf`：所有页的
双栏布局、图表可读性、匿名信息、引用和未解决占位；页数及正文／参考文献边界以编译产物为准。

改为终稿模式需根据正式会议要求更改 `cvpr` 选项，并填写作者与单位；不可仅删除行号和页码来
模拟终稿。本文档只维护模板来源和配置，写作风格见[写作索引](writing/INDEX.md)。
