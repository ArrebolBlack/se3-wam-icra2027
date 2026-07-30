# SE(3)-WAM ICRA 2027 Paper

`se3-wam-icra2027` 是 SE(3)-WAM 动态场景操作研究的独立论文仓库。
仓库使用 ICRA 2027 指定的 IEEE 双栏 LaTeX 样式，并提供 UTF-8 中文示例骨架。

## 模板与投稿边界

- 会议：IEEE International Conference on Robotics and Automation (ICRA) 2027。
- 官方征稿页：<https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/>
- 官方 LaTeX 支持页：<https://ras.papercept.net/conferences/support/tex.php>
- 本仓库中的 `ieeeconf.cls` 与 `IEEEtran.bst` 来自上述 PaperCept 官方包。
- 当前官方要求为 US Letter、IEEE 双栏、完整论文不超过 8 页，并采用双匿名评审。

此仓库的中文内容仅用于本地起稿和验证 XeLaTeX 工作流。PaperCept 的 PDF
合规说明不接受东亚文字字体，正式投稿稿件必须改为英文、移除 CJK 字体依赖，
并通过官方 PDF 合规检查。

## 环境

- UTF-8
- XeLaTeX
- latexmk
- BibTeX
- VS Code + LaTeX Workshop

Windows 上使用 MiKTeX 的 `latexmk` 时还需要 Perl。本机配置使用
`C:\Strawberry\perl\bin`；VS Code 配置已在构建工具环境中加入该路径。

## 编译

在仓库根目录运行：

```powershell
latexmk -xelatex main.tex
```

如果当前终端尚未刷新系统 `PATH`，可在 PowerShell 中临时运行：

```powershell
$env:Path = "C:\Strawberry\perl\bin;$env:Path"
latexmk -xelatex main.tex
```

清理生成文件：

```powershell
latexmk -C
```

生成的根目录 PDF、辅助文件和编辑器临时文件不会进入 Git；`figures/`
中的 PDF 被视为必要图源，可以纳入版本控制。

## 目录结构

```text
.
├── .gitattributes
├── .vscode/settings.json
├── figures/
├── sections/
│   ├── introduction.tex
│   ├── related_work.tex
│   ├── method.tex
│   ├── experiments.tex
│   └── conclusion.tex
├── tables/
│   └── example_table.tex
├── ieeeconf.cls
├── IEEEtran.bst
├── main.tex
├── references.bib
├── .gitignore
└── README.md
```

## 写作约定

- `main.tex` 只维护导言区、标题、章节装配与参考文献入口。
- 正文按主题写入 `sections/`，表格片段写入 `tables/`。
- 图像及其可编辑源文件放入 `figures/`。
- 引文统一维护在 `references.bib`。
- 初稿保持匿名作者信息；接收后再按官方终稿要求恢复作者与致谢。
