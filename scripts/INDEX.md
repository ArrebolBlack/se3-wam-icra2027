# 论文工具索引

- [build.ps1](build.ps1)：渲染矢量图，编译英文正文、独立补充、英文完整阅读版和中文审读稿。
- [build_evidence_tables.py](build_evidence_tables.py)：读取 Research 的 FUTURE0/BASE2 摘要，检查分母与计数后导出五张补充表；不运行实验。
- [paired_uncertainty.py](paired_uncertainty.py)：核验配对计数并导出任务内场景 bootstrap 区间；含固定随机种子、重采次数和方法来源，不新增实验或改写原假设检验。
- [render_figures.py](render_figures.py)：将已有 SVG 渲染为 PDF。
- [import_results.py](import_results.py)：旧 publication manifest 导入器；当前默认使用空 pending 输入，见[接口说明](../results/INDEX.md)。
- [history_uncertainty.py](history_uncertainty.py)：核对 HISTORY1 九臂原生结果身份，复算八项配对区间并导出完整逐任务表；GT-history 接收原件单独指定，不运行评测。
- [history_interventions.py](history_interventions.py)：核对八臂历史扰动报告、样本身份与原归档，汇总动作变化；不执行模型，也不冒称原始预测数组复算。
- [build_replay_materials.py](build_replay_materials.py)：从历史原档重建评测器与接受场景本地包，仅改执行路径；材料边界与解析检查见[材料入口](../results/replay_materials/INDEX.md)。
