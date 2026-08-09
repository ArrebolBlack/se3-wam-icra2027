# SE(3)-WAM — ICRA 2027 paper

这是 SE(3)-WAM 的独立论文仓库。当前版本已经形成一篇可编译、双匿名、
ICRA 风格的完整英文论文：问题定义、相关工作、方法、DB0 协议、实验问题、
消融设计、三幅矢量图、六张表、局限性和参考文献均已写入。尚未运行或冻结的
实验值统一显示为红色方括号占位符，不代表观测结果。

## 当前状态

- 主稿：`main.tex`，当前编译为 8 页 US Letter IEEE 双栏 PDF。
- 结果唯一入口：`results.tex`。最终实验结束前不要在正文中手填数值。
- 实验收尾顺序：`EXPERIMENT_PLAN.md`。
- 可编辑图源：`figures/*.svg`；论文使用的矢量 PDF 与图源一同版本控制。
- 作者保持匿名；接收或转入终稿阶段后再恢复作者、单位和致谢。

论文描述的是待完整实现并验证的目标方法，不把原项目中已有的单帧/辅助预测
实现误写成已验证系统。任何核心结论都必须由 `EXPERIMENT_PLAN.md` 中的
冻结清单、成对评测和因果干预支持。

## 投稿边界

- [ICRA 2027 Call for Papers](https://2027.ieee-icra.org/contribute/call-for-icra-2027-papers-now-accepting-submissions/)
- [PaperCept IEEE LaTeX support](https://ras.papercept.net/conferences/support/tex.php)
- 模板文件 `ieeeconf.cls` 与 `IEEEtran.bst` 来自 PaperCept IEEE 支持包。
- 当前稿件按 US Letter、10 pt、IEEE 双栏和双匿名评审准备，总页数不超过
  8 页（含参考文献）。投稿前仍需以当时的最终 CFP 和 PaperCept PDF 检查器为准。

## 构建

环境：Python 3、CairoSVG、MiKTeX/TeX Live、BibTeX、latexmk；Windows 上的
MiKTeX `latexmk` 还需要 Perl。

```powershell
python -m pip install cairosvg
./scripts/build.ps1
```

脚本先由 SVG 重建图像 PDF，再运行 `latexmk -pdf`。也可以直接编译：

```powershell
$env:Path = "C:\Strawberry\perl\bin;$env:Path"
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

根目录生成的 `main.pdf` 与 LaTeX 辅助文件被 `.gitignore` 忽略；图像 PDF 是
论文源资产，允许进入 Git。

## 目录

```text
.
├── figures/                 # 三幅 SVG/PDF 矢量图
├── scripts/                 # 图像转换和一键构建
├── sections/                # 六个正文分节
├── tables/                  # 五张论文表格
├── EXPERIMENT_PLAN.md       # 关键实验与停止规则
├── results.tex              # 全部数值占位符的唯一登记表
├── references.bib           # 参考文献
├── main.tex                 # 论文装配入口
├── ieeeconf.cls
└── IEEEtran.bst
```

## 写作和结果约定

1. 先冻结数据、代码提交、评测 manifest、随机种子和延迟配置，再解锁结果。
2. 所有 headline 比较使用相同数据、动作空间、参数/算力包络和成对测试场景。
3. 先填 `results.tex`，再检查摘要、实验段落和表 III–V 是否自动同步。
4. 若 oracle、P-Detach 或因果干预未通过预注册门槛，收缩论文主张，而不是挑选
   有利子任务或把辅助预测描述成推理时使用。
5. Residual-SPDF 仅是等 NFE 的世界解码器候选；没有闭环证据时不作为贡献。
