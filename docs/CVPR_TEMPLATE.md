# CVPR 2027 模板来源与稿件配置

当前稿件使用 [CVPR 2027 Author Guidelines](https://cvpr.thecvf.com/Conferences/2027/AuthorGuidelines) 直接链接的
[官方 CVPR 2027 LaTeX author kit v1](https://media.eventhosts.cc/Conferences/CVPR2027/author-kit-CVPR2027-v1-latex.zip)，核验日期为 **2026-10-21**。
`cvpr.sty` 与 `ieeenat_fullname.bst` 均从该压缩包原样引入；后者与原先 2026 版相同。
当日 GitHub 通用 author-kit 页面仍显示 2026，因此本次来源是官网指定下载，不是自行修改年度的旧模板。

## 入口与页限

- [main.tex](../main.tex)：官方 `article` 的 `10pt,twocolumn,letterpaper` 与 `cvpr` review 模式；正文最多 8 页，包含标题、摘要、图表和公式。
- 正文之后、参考文献之前必须有匿名 **LLM Usage Statement**；声明与被引用的参考文献不计入 8 页限制。主 PDF 的额外页面不得放正文或附录。
- [supplementary.tex](../supplementary.tex)：单独提交的 A–G 补充材料，清晰、整洁并保持匿名。
- [paper_full.tex](../paper_full.tex)：正文、声明、参考文献与附录的连续阅读版，不作为 8 页主稿上传。
- [manuscript_zh.tex](../manuscript_zh.tex)：XeLaTeX 中文审读全文，不用于投稿；与英文共用表格、图源和 [paper_config.tex](../paper_config.tex)。

官方 2027 样式不再在匿名标题区和页眉显示 Paper ID，项目已移除闲置的 `\paperID` 定义。
`\confName{CVPR}`、`\confYear{2027}` 保留；匿名作者、审稿行号、页码和 confidential 标记由官方样式生成。
参考文献使用 `ieeenat_fullname` 和模板自带 `natbib`。
正文的 `\appref` 与补充材料的 `\mainref` 经 `xr-hyper` 读取对方编号，完整阅读版直接解析。

本次迁移以本地最新 v2 稿为基础，保留英文研究内容、公式、数值、引用和待填状态。
仅修复了编译暴露的两处排版问题：TikZ 条件虚线选项，以及中文引擎下表格占位破折号的嵌套对齐。
占位符的宽度、颜色和含义保持不变。

## AI 使用声明

英文声明位置为 [sections/llm_usage.tex](../sections/llm_usage.tex)，中文对应位置为
[zh/sections/llm_usage.tex](../zh/sections/llm_usage.tex)。按作者 2026-10-21 的指示，具体披露内容暂不填写，
仅保留官方要求的章节与品红待补标记。投稿前须按实际情况写明工具名称、受影响部分及使用程度，
不能把广泛参与研究或写作的用途缩写成“仅用于语法润色”，也不能把 AI 建议或占位结果称为实验证据。

继续使用其他工具或改变使用范围时，按实际情况补充名称、受影响部分及使用程度；不猜测未记录的模型版本。
声明保持匿名，不写作者、单位、私人对话或内部资源地址。投稿前由作者核对其完整性并对提交内容负责；
camera-ready 按官网要求在 Acknowledgments 披露，可将声明移入并去匿名。

## 构建与检查

```powershell
./scripts/build.ps1 -Check
python scripts/check_build.py --strict
```

构建按“补充 → 正文 → 补充 → 正文”解析交叉引用，再编译英文完整阅读版与中文稿。
`-Target main|supplementary|full|zh` 用于局部构建，`-Clean` 清理可重建辅助文件并保留阅读 PDF。
Python、MiKTeX/TeX Live、latexmk、Windows Perl 与中文字体按仓库构建入口配置。

`check_build.py` 检查 LaTeX/BibTeX 错误与警告、未定义或重复引用、待重跑状态、缺字、正文末页和延迟浮动体，
并检查声明位置、A–G 在三个完整附录版本中的编号，以及引用键与实际参考文献是否对应。
严格模式还要求无溢出、中英文数字与结构对应；检查范围含标题、摘要、正文、附录导读和 AI 声明。
这些检查不代替语义审读、文献真实性核验和最终 PDF 版面检查。

投稿前运行 `python scripts/check_build.py --final --strict`。当前研究草稿仍有结果和图占位，
因此编译与普通严格检查通过不等于已满足最终投稿条件。未选开关分支也会被待填扫描列出，需按实际提交分支核对。

## 本次编译记录（2026-10-22）

当前开关为 `QtwoCase=1`、`QthreeCase=3`、`BackboneCase=1`。英文正文止于第 8 页；
主 PDF 共 11 页，声明与参考文献位于第 9–11 页；独立补充材料 26 页；英文完整阅读版 35 页。
中文完整审读稿 43 页。四份 PDF 的严格检查通过：无 LaTeX/BibTeX 错误、未解析或重复引用、待重跑状态、缺字及溢出；声明位置、A–G 编号和引用覆盖正常，中英文数字与结构差异为零。本次仅验证上述当前开关配置。
已渲染检查四份 PDF 的全部页面，并修正中文稿三处段落溢出及图 S1 占位框高度；主稿引用 58 篇，独立补充引用 24 篇，英文与中文完整版均引用 61 篇。17 项单元测试通过。引用检查覆盖键、编号与解析，不代表重新核验全部文献的内容真实性。

本仓库仅维护这一条模板路径；ICRA 专用类与参考文献样式已移除。
