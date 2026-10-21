# 正文源码索引（v2）

[main.tex](../main.tex) 按下列顺序装配英文正文；中文对应文件在 [zh/sections/](../zh/INDEX.md)。
随实验结论变化的表述由 [paper_config.tex](../paper_config.tex) 的开关控制，见 [v2 作者指南](../docs/writing/v2_author_guide.md)。

- [teaser.tex](teaser.tex)：首页首图（图 1，真机占位与详细规格）。
- [introduction.tex](introduction.tex)：情境 → 表示错配 → 误差预算与设计选择 → 模型 → 实时协议下的证据；三条贡献。
- [related_work.tex](related_work.tex)：动态操作、世界—动作模型、结构化 3D/4D 运动。
- [formulation.tex](formulation.tex)：物理时间、按精度划分的角色、交互误差分解、定量预测、三原则（图 2、表 1）。
- [method.tex](method.tex)：SE(3)-WAM 的记住/预测/行动（四组 token 与掩码）、物理时间执行、4D 提升预训练（图 3）。
- [experiments.tex](experiments.tex)：设置、主结果、原则检验、消融与预训练、真机（表 2–5、图 4）。
- [conclusion.tex](conclusion.tex)：结论与局限。
- [llm_usage.tex](llm_usage.tex)：正文之后、参考文献之前的匿名 AI 使用声明；具体披露暂缓填写，不计入正文页限，与中文同步。

引用附录用 `\appref{app:...}`：独立正文经 `xr-hyper` 读取 `supplementary.aux`，合并稿直接解析。
