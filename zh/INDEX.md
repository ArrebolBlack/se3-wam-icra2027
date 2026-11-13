# 中文审读稿索引（v4 方法论文版，2026-10-23）

[manuscript_zh.tex](../manuscript_zh.tex) 用 XeLaTeX（ctexart）编译，导言区在 [preamble_zh.tex](preamble_zh.tex)，
与英文共用 [paper_config.tex](../paper_config.tex) 的开关与配置宏。数值表与英文共用 `tables/`，由 `\tablelang{英文}{中文}` 选择语言。

- `zh/sections/`：与 `sections/` 对应的中文正文（teaser、introduction、related_work、method、benchmark、experiments、conclusion）及 `llm_usage.tex` 使用声明；formulation 自 2026-10-22 起不再使用，2026-10-24 已移至 `local_private/archived-v4-sections-20261024/zh/`。
- `zh/appendix/`：按 A–E 装配 implementation、benchmark、results、real、design，与英文顺序一致（2026-10-25）。

当前为 2026-10-23 更新的方法论文译稿（按 Notion 终稿同步摘要与引言，正文与附录改为真实架构），包括标题、摘要、正文、附录导读与 A–G 及未选中的结论分支。表格与插图源由两种语言共用；共享插图内保留英文标注，图注和占位图规格采用中文。

修改英文时同步修改对应中文文件；`scripts/check_build.py` 会报告中英文之间的数字差异和结构差异（开关分支、待填项、图占位、标签、引用、表格），并检查声明与附录导读。自动检查不替代逐段语义核对。中文稿仅供审读，不用于投稿。
