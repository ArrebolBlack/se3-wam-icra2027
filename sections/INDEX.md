# 正文源码索引（v4 方法论文版，2026-10-23）

[main.tex](../main.tex) 按下列顺序装配英文正文；中文对应文件在 [zh/sections/](../zh/INDEX.md)。
随实验结论变化的表述由 [paper_config.tex](../paper_config.tex) 的开关控制，见 [v2 作者指南](../docs/writing/v2_author_guide.md)。

- [teaser.tex](teaser.tex)：首页首图（图 1，真机占位与详细规格）。
- [introduction.tex](introduction.tex)：与 Notion《SE(3)-WAM论文10.23》终稿一致：共性难点 → 信息与速度的权衡 → 关键观察与方法 → 实验 → 三条贡献。
- [related_work.tex](related_work.tex)：动态操作、世界模型与世界—动作模型、结构化 3D/4D 表示（约 100 篇引用，新增条目已逐条核对）。
- [formulation.tex](formulation.tex)：**自 2026-10-22 起不再使用**（方法论文结构下并入 `method.tex` 第 3.1 节）。
- [method.tex](method.tex)：作用于运动目标、当前帧与运动历史、按角色区分精度的 4D 预测、动作与共享主干（场景/摘要/动作 token、预测只作监督）、真机预训练（图 2–3）。不含领先时长条件化。
- [experiments.tex](experiments.tex)：设置、主结果、五个真机任务、消融（表 1–3、图 4–6）。
- [conclusion.tex](conclusion.tex)：结论与局限。
- [llm_usage.tex](llm_usage.tex)：正文之后、参考文献之前的匿名 AI 使用声明；具体披露暂缓填写，不计入正文页限，与中文同步。

引用附录用 `\appref{app:...}`：独立正文经 `xr-hyper` 读取 `supplementary.aux`，合并稿直接解析。
