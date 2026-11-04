# 论文工具索引

所有读取 Research 的脚本都接受 `--research-root`，默认取环境变量 `SE3WAM_RESEARCH`，否则为 `C:/workspace/se3-wam-research`。依赖见根目录 `requirements.txt`。

## 构建与检查

- [publish.py](publish.py)：默认发布入口；在 `main` 运行 `python scripts/publish.py`，自动用独立工作树编译四份 PDF、提交全部修改与未忽略的新文件、合并并推送 `origin/main`；`-m` 指定提交说明。也可从已有任务工作树运行。按作者要求不运行测试、页数、引用或翻译检查；失败时保留任务工作树，推送失败后可直接重试 `git push origin main`。
- [build.ps1](build.ps1)：编译英文正文、独立补充、英文完整阅读版和中文审读稿；`-Figures` 先重建插图，`-Check` 运行测试与稿件检查，`-Target` 只编译指定文档；`-Clean` 清理辅助文件并保留四份阅读 PDF。
- [check_build.py](check_build.py)：检查四份文档的编译日志、正文 8 页上限、LLM 声明位置、A–F 编号、参考文献覆盖和中英文对应；报告待填项，`--strict` 拒绝溢出和翻译结构差异，`--final --strict` 另拒绝未填结果与文本。
- [list_fillins.py](list_fillins.py)：列出正文、LLM 声明与附录中全部待填文本、图占位和含待填单元格的表格（含各开关分支）；`--zh` 扫描中文稿，`--markdown <路径>` 输出清单文件。
- [build_figures.py](build_figures.py)：按原名称重建各图项目归档中的旧图，`--only <名称>` 选择单图；当前正文图源与历史入口见[图项目索引](../figures/INDEX.md)。
- [common.py](common.py)：共用的路径解析、任务列表与中英文标签、校验函数，以及 SVG→PDF 打印。

## 从 Research 导出

- [build_evidence_tables.py](build_evidence_tables.py)：读取 FUTURE0 摘要与 BASE2 的 seed 0、三 seed 报告，检查分母、配对与计数后导出 v1 的七张证据表（v2 未引用，保留以便迁移数值）；不运行实验。
- [build_additional_studies.py](build_additional_studies.py)：读取 BATCH0 完整逐场结果与 GRIPPER2 分类/回归报告，核对计数后导出 v1 附录 H 的三张表（v2 未引用）；不执行模型。
- [paired_uncertainty.py](paired_uncertainty.py)：核验配对计数并导出任务内场景 bootstrap 区间；含固定随机种子、重采次数和方法来源，不新增实验或改写原假设检验。
- [build_realtime_per_task.py](build_realtime_per_task.py)：从已验收Native场景导出Table S4，核对Table 1任务等权均值并复算最强基线配对区间；用`--c-native-results`指定BF16 C接收目录、`--research-output`指定INFER0结果目录，不运行模型。
- [history_uncertainty.py](history_uncertainty.py)：核对 HISTORY1 九臂原生结果身份，复算八项配对区间并导出完整逐任务表；GT-history 接收原件单独指定，不运行评测。
- [history_interventions.py](history_interventions.py)：核对八臂历史扰动报告、样本身份与原归档，汇总动作变化；不执行模型，也不冒称原始预测数组复算。
- [build_replay_materials.py](build_replay_materials.py)：从历史原档重建评测器与接受场景本地包，仅改执行路径；材料边界与解析检查见[材料入口](../results/replay_materials/INDEX.md)。
