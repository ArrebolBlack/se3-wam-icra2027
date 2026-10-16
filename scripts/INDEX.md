# 论文工具索引

- [build.ps1](build.ps1)：渲染矢量图，编译英文正文、独立补充、英文完整阅读版和中文审读稿。
- [build_evidence_tables.py](build_evidence_tables.py)：读取 Research 的 FUTURE0/BASE2 摘要，检查分母与计数后导出五张补充表；不运行实验。
- [paired_uncertainty.py](paired_uncertainty.py)：核验配对计数并导出任务内场景 bootstrap 区间；含固定随机种子、重采次数和方法来源，不新增实验或改写原假设检验。
- [render_figures.py](render_figures.py)：将已有 SVG 渲染为 PDF。
- [import_results.py](import_results.py)：旧 publication manifest 导入器；当前默认使用空 pending 输入，见[接口说明](../results/INDEX.md)。
- [history_uncertainty.py](history_uncertainty.py)：核对 HISTORY1 八臂原生结果身份并复算主文的七项配对场景区间；不运行评测。
