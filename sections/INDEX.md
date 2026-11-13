# 正文源码索引（v4 方法论文版，2026-10-23）

[main.tex](../main.tex) 按下列顺序装配英文正文；中文对应文件在 [zh/sections/](../zh/INDEX.md)。
随实验结论变化的表述由 [paper_config.tex](../paper_config.tex) 的开关控制，见 [v2 作者指南](../docs/writing/v2_author_guide.md)。

正文的图体、图注和标签通过 `\input` 引入，单图修改从 [Fig1–Fig6 图项目](../figures/INDEX.md)进入。

- [teaser.tex](teaser.tex)：首页首图（图 1，真机占位与详细规格）。
- [introduction.tex](introduction.tex)：与 Notion《SE(3)-WAM论文10.23》终稿一致：共性难点 → 信息与速度的权衡 → 关键观察与方法 → 实验 → 三条贡献。
- [related_work.tex](related_work.tex)：动态操作、世界模型与世界—动作模型、结构化 3D/4D 表示；书目来源与取舍见[参考文献核对](../docs/writing/reference_audit_20261025.md)。
- `formulation.tex`：自 2026-10-22 起不再使用，2026-10-24 已移至 `local_private/archived-v4-sections-20261024/`（内容并入 `method.tex` 第 3.1 节）。
- [method.tex](method.tex)：3.1 问题形式化（目标、环境、静态三种角色）；3.2 按角色编码场景动态（当前帧 + 目标位姿历史）；3.3 按角色预测 4D 未来（稀疏 3D 流 + 目标 SE(3) 轨迹）；3.4 世界—动作联合学习与推理（图 2）。
- [benchmark.tex](benchmark.tex)：OnTimeBench 独立一节：4.1 概览（与暂停世界的基准对比、五个任务族）；4.2 构建；4.3 评测协议（图 4）。
- [experiments.tex](experiments.tex)：5.1 实现细节；5.2 OnTimeBench 与 DOMINO 结果（表 1–2、延迟图）；5.3 消融（表 3）；5.4 六任务真机（表 4、图 6）。
- [conclusion.tex](conclusion.tex)：结论（一段，不含局限）。
- [llm_usage.tex](llm_usage.tex)：正文之后、参考文献之前的匿名 AI 使用声明；披露 Codex 的研究、代码、实验、写作与绘图辅助，不计入正文页限，与中文同步。

引用附录用 `\appref{app:...}`：独立正文经 `xr-hyper` 读取 `supplementary.aux`，合并稿直接解析。
