# 盲审工具

用于"真伪辨别式"盲审：把本稿与若干篇真实的顶会论文统一处理成纯文本，交给一个全新的审稿代理，
看它能否认出哪篇是 AI 生成的，并给出质量评分。流程与历次结论见
[docs/writing/blind_review_20261020.md](../../docs/writing/blind_review_20261020.md)。

## 统一处理（对所有论文完全相同）

- 去模板：PDF 转纯文本，按两栏/单栏版面重排阅读顺序；去掉页眉页脚、页码、水印和边注。
- 去身份：删除作者、单位、脚注中的联系方式、致谢与所有链接。
- 去图：图片与图中文字一律删除，只保留图注，并在原位置写 `[figure graphics omitted]`。
- 表格按行重建，表内所有数值替换为 `[MASK]`；正文中的小数、百分比、倍数和带物理单位的数值替换为 `[MASK]`，
  普通整数（数量、年份、章节号）、arXiv 编号与 DOI 保留。

## 本稿的盲审副本

`make_blind_source.py <repo> <out>` 生成只用于盲审的源码副本（不回写仓库）：CVPR 终稿样式（无行号）、无作者行；
数值类 `\fillin` 变为 `[MASK]`，配置建议值与预期结论短语按原文输出；`\resultplaceholder` 输出其宽度模板（如 `00.0`），
随后由转换器与其他论文的表格数值一样替换为 `[MASK]`；图占位变为同高的空白，图注保留；给作者的待填说明被删去。

```bash
python3 -I scripts/blind_review/make_blind_source.py . /tmp/blind_src
(cd /tmp/blind_src && latexmk -pdf paper_full.tex)
python3 -I scripts/blind_review/pdf2blind.py /tmp/blind_src/paper_full.pdf ours.txt
python3 -I scripts/blind_review/pdf2blind.py <real_paper.pdf> real_x.txt
```

依赖：poppler 的 `pdftotext`（`-bbox-layout`）与 Python 包 `pdfplumber`。

## 参考论文

真实论文取自 Research 仓库 `local_private/cvpr_writing_materials_2026_10_13/papers/`（Git 忽略）。
每轮从中取 4 篇（Motus、GEM-4D/RoMan-4D、Cosmos Policy、DAPL）作为待判断的真实论文，并从参考池中移除；
其余 14 篇（另列 VGGT 题目）以未改动的全文文本作为审稿人唯一可检索、对比的参考池。

## 审稿提示词要点

沿用作者给出的提示词：审稿人得知其中恰好有一篇是 AI 生成的假论文，须依据正文、参考文献、附录、图注、表格判断并给出详细理由；
不得搜索论文题目、不得联网，只能在参考池中检索对比。另要求逐篇给出 AI 生成概率、1–10 的质量评分与主要优缺点，
并对判定为假的论文给出具体修改建议。每一轮都使用全新的审稿代理，论文顺序重新打乱。

通过标准：审稿人没有把本稿判为 AI 生成，本稿的"像 AI 程度"不是最高，且质量评分不低于真实论文的中位数并达到"接收"（≥ 8）。
通过后再用一个全新审稿代理、换一种顺序复核一次。

## 第 2 轮起的工具改动（2026-10-21）

转换器的改动对所有论文同样生效，每轮都用同一版本重新生成全部 5 篇文本：

- 用 booktabs 的粗线（≥0.75 pt）判断表格边界：高表格在顶线与底线之间不再被切开；两线之间若有表注或图注，则视为两张表。
  此前，超过 260 pt 的长表（如任务定义表）只识别到表头，正文单元格被当成散文。
- 表格中紧跟 "Sec./Table/Fig./Appendix" 的编号视为引用，不再 mask。
- 正文中以小数点开头的小数（如 ".08"）与其他小数一样 mask。
- 链接残留标签（"Project Page:"、"Code:"）只在独占一行或带冒号时删除；此前会把小节标题 "Supplementary Video" 的
  "Video" 误删，第 1 轮审稿人因此认为该标题被截断。
- 多余的空行合并为一个。

本稿的盲审副本：

- 数值类 `\fillin` 输出 `\textnormal{[MASK]}`，在公式中也呈现为 "[MASK]"（此前为 "[M ASK]"）。
- 指名类 `\fillin`（"name of the strongest baseline" 等）在盲审副本中输出一个合理的方法名，仓库原文不变。

辅助脚本：

- `fix_smallcaps.py`：Cosmos Policy 使用小型大写标题，转出的文字被拆成 "C OSMOS P OLICY"；重新生成后用它恢复第 1 轮时的可读标题。
- `style_metrics.py`：分别统计正文（参考文献之前）与附录（参考文献之后）的分号、"we"、", not" 频率和审稿人点名过的词。
- `make_round.sh N "A=… B=ours …"`：重建本稿文本并组装第 N 轮材料。脚本中的路径是云端工作区的路径，在其他环境使用时需要修改。
