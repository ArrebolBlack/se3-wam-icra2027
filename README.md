# SE(3)-WAM 论文仓库（目标：CVPR 2027）

SE(3)-WAM 的论文源码、导出脚本和证据副本。仓库名沿用最初的 ICRA 计划，当前目标会议是 CVPR 2027。
实验事实以 Research 仓库为准；本仓库只保存论文文本、表格、图与导出/检查脚本。

**v2 稿件（2026-10-20 起）**按"交互时刻"框架重写：一阶交互误差预算 → 三条原则（记住/预测/行动）→ SE(3)-WAM 实例化 →
检验原则的预测。所有实验数值与统计图为占位，图为复用图、TikZ 草图或带详细规格的占位框。
先读 [v2 作者指南](docs/writing/v2_author_guide.md)（结论开关、填数流程、实验映射）与 [v2 图规格](docs/writing/v2_figure_specs.md)。
v1（Q1–Q3 研究顺序）稿件的完整快照在 `local_private/archived-v1-20261020/`（含当时未提交的修改），Git 历史保留其提交版本。

## 产物

| 入口 | 内容 | 引擎 |
|---|---|---|
| `main.tex` → `main.pdf` | 英文正文：8 页正文，LLM Usage Statement 与参考文献另计 | pdfLaTeX |
| `supplementary.tex` → `supplementary.pdf` | 独立补充材料，附录 A–D | pdfLaTeX |
| `paper_full.tex` → `paper_full.pdf` | 正文、LLM 声明、参考文献与完整附录的连续阅读版 | pdfLaTeX |
| `manuscript_zh.tex` → `manuscript_zh.pdf` | 中文审读稿：正文与附录，不用于投稿 | XeLaTeX |

`paper_config.tex` 集中放置结论开关（`\QtwoCase`、`\QthreeCase`、`\BackboneCase`）与需确认的配置宏；四个入口共用。
PDF 中品红色内容为待填：文本 `\fillin{...}`、表格 `\resultplaceholder`、图 `\figplaceholder`。
当前使用官网发布的 CVPR 2027 模板，来源与构建记录见 [模板说明](docs/CVPR_TEMPLATE.md)。
官方要求在正文后、参考文献前放置匿名 LLM Usage Statement；按当前作者安排，已保留章节，具体披露内容暂缓填写。

## 构建

依赖：MiKTeX 或 TeX Live（含 latexmk；Windows 上的 latexmk 需要 Strawberry Perl；中文稿需要 ctex）、Python 3.12。

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
./scripts/build.ps1 -Check
python scripts/list_fillins.py --markdown tmp/fillins.md   # 待填清单
```

- `build.ps1` 先按"补充 → 正文 → 补充 → 正文"编译，正文与补充材料通过 `xr-hyper` 读取对方的章节、图表编号（`\appref`、`\mainref`）；
  随后编译完整版和中文稿。`-Target main|supplementary|full|zh` 只编译指定文档，`-Clean` 清理辅助文件。
- `-Check` 运行单元测试和 `scripts/check_build.py`：LaTeX 错误、未定义或重复的标签与引用、正文是否超过 8 页、待填表格单元与待填文本，
  以及中英文对应文件之间的数字差异与结构差异（开关分支、待填项、图占位、标签、引用、表格）。投稿前用 `python scripts/check_build.py --final --strict`，此时任何待填内容都会报错。

## 目录

```text
.
├── main.tex  supplementary.tex  paper_full.tex  manuscript_zh.tex   # 四个编译入口
├── preamble.tex       # 英文稿共用的宏包、记号、占位与开关宏
├── paper_config.tex   # 结论开关与配置宏（四个入口共用）
├── sections/          # 英文正文（teaser、introduction、related_work、method、benchmark、experiments、conclusion）
├── appendix/          # 英文附录 A–D
├── zh/                # 中文审读稿（preamble_zh、sections、appendix，与英文一一对应）
├── tables/            # 中英文共用的表格（main_* 正文，supp_* 与协议表为补充；v1 证据表保留）
├── figures/           # 论文图（PDF/SVG）、TikZ 草图、v1 绘图脚本与数据
├── scripts/           # 导出、绘图编排、构建、检查与待填清单
├── results/           # 已接收的最小证据副本与评测复现材料
├── tests/             # 单元测试
├── docs/              # 作者指南、图规格、写作指南、证据路由、模板说明与实验安排
├── references.bib     # 参考文献
└── cvpr.sty  ieeenat_fullname.bst   # 官方 CVPR 2027 author kit v1
```

各目录的 `INDEX.md` 说明其中文件；文档入口见 [docs/INDEX.md](docs/INDEX.md)。

## 约定

1. 实验事实以 Research 为准。数字变化时先更新表格，再改正文和中文稿里引用这些数字的句子。
2. 结论变化先改 `paper_config.tex` 的开关；开关覆盖不到的情况按作者指南 §2 改写，并同步中文稿。
3. 四份编译 PDF 与插图 PDF 纳入版本控制；LaTeX 辅助文件和 `tmp/` 不入库。
4. `local_private/` 存放不入库的本地归档（v1 快照、旧 worktree 和评审渲染）。
5. 作者保持匿名，终稿阶段再恢复作者、单位和致谢。
