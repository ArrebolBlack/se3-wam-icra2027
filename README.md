# SE(3)-WAM — ICRA 2027 paper

这是 SE(3)-WAM 的独立论文仓库。当前版本已经形成一篇可编译、双匿名、
ICRA 风格的完整英文论文：问题定义、相关工作、方法、DB0 协议、实验问题、
消融设计、三幅论文图、五张表、局限性和参考文献均已写入。尚未运行或冻结的
实验值统一显示为红色方括号占位符，不代表观测结果。

## 当前状态

- 主稿：`main.tex`，当前编译为 8 页 US Letter IEEE 双栏 PDF。
- 结果唯一输入：Dynamic Benchmark 生成的 `se3wam-publication-result-manifest-v1`；
  `results.tex` 由 `scripts/import_results.py` 生成，禁止手填。
- 实验收尾顺序：`EXPERIMENT_PLAN.md`。
- 论文图源：`figures/*.svg`；论文使用的 PDF 与图源一同版本控制。
- 独立图项目：`figure_projects/`；每幅论文图各有一个可编辑、已渲染验收的 PPTX。
- 作者保持匿名；接收或转入终稿阶段后再恢复作者、单位和致谢。

主稿按完整工作的论文叙事呈现 SE(3)-WAM、DB0、因果干预和外部/实机验证。
尚未提供的精确统计量由 `results/pending.json` 显式登记并渲染为红色占位符；
该 manifest 不含提交、实验、证据、媒体或可用数值。最终替换时继续遵循
`EXPERIMENT_PLAN.md` 的成对评测口径。

## 投稿边界

- [ICRA 2027 Call for Papers](https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/)
- [PaperCept IEEE LaTeX support](https://ras.papercept.net/conferences/support/tex.php)
- 模板文件 `ieeeconf.cls` 与 `IEEEtran.bst` 来自 PaperCept IEEE 支持包。
- 当前稿件按 US Letter、10 pt、IEEE 双栏和双匿名评审准备，总页数不超过
  8 页（含参考文献）。投稿前仍需以当时的最终 CFP 和 PaperCept PDF 检查器为准。

## 构建

环境：Python 3、CairoSVG、MiKTeX/TeX Live、BibTeX、latexmk；Windows 上的
MiKTeX `latexmk` 还需要 Perl。

默认构建先校验无主张的 pending manifest、重建 `results.tex`，再由 SVG 重建
图像 PDF 并运行 `latexmk -pdf`：

```powershell
python -m pip install cairosvg
./scripts/build.ps1
```

使用已审阅且全部结果齐备的发布 manifest 构建终稿：

```powershell
./scripts/build.ps1 `
  -ResultManifest C:\path\to\publication-result-manifest.json `
  -RequireReviewed -RequireComplete
```

也可以直接编译：

```powershell
$env:Path = "C:\Strawberry\perl\bin;$env:Path"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

根目录生成的最终 `main.pdf` 与图像 PDF 均进入 Git，便于直接核对当前投稿稿；
其余 LaTeX 辅助文件仍由 `.gitignore` 忽略。

## 目录

```text
.
├── figures/                 # 三幅论文图及 benchmark 冻结环境帧
├── figure_projects/         # 每幅图一个独立的可编辑 PPTX 项目
├── results/                 # 结果 ID 绑定与无主张 pending 输入
├── scripts/                 # 图像转换和一键构建
├── sections/                # 六个正文分节
├── tables/                  # 五张论文表格
├── EXPERIMENT_PLAN.md       # 关键实验与停止规则
├── results.tex              # manifest 生成的 LaTeX 宏，不手改
├── references.bib           # 参考文献
├── main.tex                 # 论文装配入口
├── ieeeconf.cls
└── IEEEtran.bst
```

## 写作和结果约定

1. 先冻结数据、代码提交、评测 manifest、随机种子和延迟配置，再由 Dynamic
   Benchmark 生成并审阅发布 manifest。
2. 所有 headline 比较使用相同数据、动作空间、参数/算力包络和成对测试场景。
3. `results/bindings.json` 是 result ID、单位、精度与 LaTeX 宏的唯一映射；导入器
   同时校验 review 状态、提交与证据闭包、payload 身份和完整性。
4. 先用同一份 reviewed manifest 生成 `results.tex`，再检查摘要、实验段落和表
   III–V 是否自动同步；Gallery 也只消费这份 manifest。
5. 同时报告 oracle、P-Detach 与因果干预，使预测质量、动作使用和闭环收益形成
   同一条证据链，不用有利子任务替代 Core 结果。
6. Residual-SPDF 作为等 NFE 世界解码器对照单独报告，不与主方法贡献混写。
