# v4 任务 7：辅助外观目标精简报告

日期：2026-10-23。基线：`paper-v4-20261023`，`afc71e5`。工作分支：`v4-t7-aux`。

正文方法保留一句仅训练使用、部署跳过的外观辅助目标披露和附录链接；总损失中的 `\lambda_{\rm aux}\mathcal L_{\rm aux}` 原样保留。图 2 图注不再列举外观目标，表 3 删除重复消融行，§4.4 保留一句未来外观目标增益及原占位。完整目标、读出、损失和权重保留在附录 A.3，并根据任务 6 的代码核查修正当前目标 RGB 重建头。本文没有填入任何实验结果。

## 需要确认的表注联动

`tables/supp_predict.tex` 的表注当前将“同时出现在表 3 中”的行定义为三个训练种子，其余行为一个种子；`appendix/design.tex` 开头采用同一规则。删除正文的 “no appearance targets” 行后，这一条件式表注会把对应的附录 “none” 行隐含地从三种子归为单种子。实际实验种子数不能由版面移动决定。原行与全部结果占位均保留，表 S-predict 源码未改；但合并精修时须按实际运行记录明确此行种子数，并同步表注和附录开头。`tables/supp_predict.tex` 不在本任务的允许修改清单内，因此没有越界修改。此项不影响编译检查，但属于科学披露的待决事项。

## 搜索与修改范围

对所有 `**/*.tex` 搜索 `appearance|auxiliary|DINO|depth|moving|dynamic RGB|reconstruct|L_aux|lambda_aux|外观|辅助|深度|运动表面|重建`，命中 54 个文件。核对了活动正文、对应中文、附录 A/F/E、共享表格与图 2 标注。其余命中包括 RGB-D 输入、跟踪器、他人方法、DROID 基座、旧表格和写作归档，不因关键词命中而修改。

修改文件仅为 `sections/method.tex`、`sections/experiments.tex`、`sections/conclusion.tex`、`tables/main_design.tex`、`appendix/implementation.tex` 及四个对应中文文件；另新增本报告并在最近一级 `docs/writing/INDEX.md` 加入入口。摘要、引言、图 5/6 图注、损失式、配置宏、架构 TikZ、附录 F/E 和其他段落保持原文。图 5/6 图注只解释 SE(3)、稀疏流和训练期预测，无外观辅助目标的展开，因此无须精简。

## 逐处原文与新文

以下引文保留 LaTeX 源码；摘录完整的受改句子或段落，未展示的相邻内容未改。

### 1. 图 2 图注

英文原文：

```tex
During training, light heads read the world stream out into a role-aware 4D
forecast at physical horizons $\tau_t+\delta_h$: the target's SE(3) trajectory and a
sparse 3D flow with visibility on a \cfgContextGrid{} grid, plus appearance targets
(dashed: training only).
```

英文新文：

```tex
During training, light heads read the world stream out into a role-aware 4D
forecast at physical horizons $\tau_t+\delta_h$: the target's SE(3) trajectory and a
sparse 3D flow with visibility on a \cfgContextGrid{} grid
(dashed: training only).
```

中文原文：

```tex
训练时，轻量读出头把世界流读出为物理时域 $\tau_t+\delta_h$ 上按角色区分精度的 4D 预测：目标的 SE(3) 轨迹、\cfgContextGrid{} 网格上带可见性的稀疏 3D 流，以及外观目标（虚线：仅训练）。
```

中文新文：

```tex
训练时，轻量读出头把世界流读出为物理时域 $\tau_t+\delta_h$ 上按角色区分精度的 4D 预测：目标的 SE(3) 轨迹与 \cfgContextGrid{} 网格上带可见性的稀疏 3D 流（虚线：仅训练）。
```

### 2. 方法 §3.3

英文原文：

```tex
As
further training targets, appearance heads regress the future depth, the features of
a frozen DINOv3 teacher \cite{dinov3}, and the RGB of moving surfaces, and a
reconstruction head restores the target region of the current image
($\mathcal L_{\rm aux}$).
```

英文新文：

```tex
We also
use auxiliary appearance targets ($\mathcal L_{\rm aux}$) only during training,
skipping their heads at deployment (Appendix~\appref{app:world}).
```

中文原文：

```tex
作为额外的训练目标，外观头回归未来深度、冻结 DINOv3 教师 \cite{dinov3} 的特征与运动表面的 RGB，重建头恢复当前图像中的目标区域（$\mathcal L_{\rm aux}$）。
```

中文新文：

```tex
我们还使用仅用于训练的辅助外观目标（$\mathcal L_{\rm aux}$），部署时跳过其读出头（附录~\appref{app:world}）。
```

保留下一句的轻量读出、有效标签等信息，且未改 §3.4 的总损失式和权重。DINOv3 引用在附录 A.3 保留；独立英文正文因此少一个参考文献条目，合订版仍包含该引用。

### 3. 实验 §4.4 “What to predict / 预测什么”

英文原文：

```tex
As auxiliary targets next to the 4D
forecast, however, depth, DINO features, and moving-region RGB add \fillin{X.X}
points, and like the 4D heads they are skipped at deployment.
```

英文新文：

```tex
Future appearance targets add
\fillin{X.X} points (Appendix~\appref{app:design_predict}).
```

中文原文：

```tex
不过，作为 4D 预测之外的辅助目标，深度、DINO 特征和运动区域 RGB 带来 \fillin{X.X} 个百分点；与 4D 预测头一样，它们在部署时被跳过。
```

中文新文：

```tex
未来外观目标带来 \fillin{X.X} 个百分点（附录~\appref{app:design_predict}）。
```

“Future / 未来”保留原句对三个未来目标的归因，没有将该占位增益扩大解释为包含当前帧重建。完整解释仍见附录 E.2 的 “Image-space futures / 图像空间的未来”，消融条件见 F.3 及表 S-predict。

### 4. 表 3

中英共用原行：

```tex
\tablelang{no appearance targets}{去除外观辅助目标} & \resultplaceholder & \resultplaceholder & \resultplaceholder & \resultplaceholder & \resultplaceholder \\
```

新文：删除此行，不加替代行；英文 “no appearance targets” 和中文“去除外观辅助目标”同时移出正文。原有表注只定义一般消融、指标与单位，不含需删除的外观目标说明；`tab:design` 标签与引用保持有效。

对应控制仍在 `tables/supp_predict.tex` 最后一组 “Training-only appearance targets on the selected representation (SE(3) + flow) / 选定表示（SE(3) + 流）上的仅训练外观目标” 的 “none / 无” 行。原表 3 的五个待填单元随重复行删除，附录的该行及其他外观行所有占位保持原样。种子数表注的联动见本报告开头。

### 5. 结论

英文原文：

```tex
Our ablations attribute the gains to the metric motion
history and to role-aware forecasts used as a training signal, rather than to richer
appearance models or to reading the forecast online.
```

英文新文：

```tex
Our ablations attribute the gains to the metric motion
history and to role-aware forecasts used as a training signal, rather than to
reading the forecast online.
```

中文原文：

```tex
消融把收益归因于度量运动历史以及作为训练信号使用的按角色区分的预测，而非更丰富的外观模型或在线读取预测。
```

中文新文：

```tex
消融把收益归因于度量运动历史以及作为训练信号使用的按角色区分的预测，而非在线读取预测。
```

删去外观模型的再次比较。附录 E.2 仍保留“外观作为辅助目标有帮助，但不能替代度量预测”的原有解释及占位，结论方向没有反转。

### 6. 附录 A.3 “Appearance targets / 外观目标”

英文原文：

```tex
\paragraph{Appearance targets.} Patch decoders on the final patch tokens predict
three targets at every horizon: the metric depth of their patch (squared error on
valid depth), the features of a frozen DINOv3 ViT-L/16 teacher \cite{dinov3} on the
$14\times14$ grid after channel-wise layer normalization (squared error), and the
RGB of moving surfaces (i.e., surfaces that move by more than 1\,mm, including the
robot), with a squared error inside that mask. A linear decoder on the current patch
tokens reconstructs the RGB inside the target's current box, which ties the patch
features to the target without adding an input. Each of these four targets enters
$\mathcal L_{\rm aux}$ with weight 0.1.
```

英文新文：

```tex
\paragraph{Appearance targets.} Linear readouts of the final patch tokens predict
three targets at every horizon: metric depth and moving-surface RGB through
$16\times16$ pixel readouts per patch, and 1024-dimensional features of a frozen
DINOv3 ViT-L/16 teacher \cite{dinov3} on the $14\times14$ grid. Depth uses squared
error on valid pixels; DINO features use squared error after channel-wise layer
normalization; RGB uses squared error on surfaces that move by more than 1\,mm,
including the robot. These losses average channels and then valid positions.
A $\cfgWidth\to256\to3072$ MLP with GELU and a final sigmoid reads the mean of the
final summary tokens to reconstruct the current target's $32\times32$ RGB region,
using absolute error averaged over valid RGB elements. This ties the summary
features to the target without adding an input. The four losses form
$\mathcal L_{\rm aux}$; $\lambda_{\rm aux}=0.1$ gives each a weight of 0.1 in the
total objective. All four heads are used only in training and skipped at deployment;
their outputs never enter the action stream.
```

中文原文：

```tex
\paragraph{外观目标。}最终 patch token 上的 patch 解码器在每个时域预测三个目标：其 patch 的度量深度（在有效深度上取平方误差）、冻结 DINOv3 ViT-L/16 教师 \cite{dinov3} 在 $14\times14$ 网格上经通道层归一化后的特征（平方误差），以及运动表面的 RGB（即移动超过 1\,mm 的表面，包括机器人），在该掩码内取平方误差。当前 patch token 上的线性解码器重建目标当前框内的 RGB，使 patch 特征与目标关联而不增加输入。这四个目标各以 0.1 的权重计入 $\mathcal L_{\rm aux}$。
```

中文新文：

```tex
\paragraph{外观目标。}最终 patch token 上的线性读出在每个时域预测三个目标：通过每个 patch 的 $16\times16$ 像素读出预测度量深度与运动表面 RGB，以及冻结 DINOv3 ViT-L/16 教师 \cite{dinov3} 在 $14\times14$ 网格上的 1024 维特征。深度在有效像素上取平方误差；DINO 特征经通道层归一化后取平方误差；RGB 在移动超过 1\,mm 的表面（包括机器人）上取平方误差。这些损失先对通道取平均，再对有效位置取平均。一个带 GELU 和末端 sigmoid 的 $\cfgWidth\to256\to3072$ MLP 读取最终摘要 token 的均值，重建当前目标的 $32\times32$ RGB 区域，并对有效 RGB 元素的绝对误差取平均。这使摘要特征与目标关联而不增加输入。四项损失构成 $\mathcal L_{\rm aux}$；$\lambda_{\rm aux}=0.1$ 使每项在总目标中的权重为 0.1。四个头都仅用于训练，部署时跳过，其输出从不进入动作流。
```

这里的数值补充是读出结构与维度的代码事实，不是新实验结果。四个目标各 0.1 的实际总权重不变；旧文同时写“在 L_aux 内各 0.1”和正文外乘 `lambda_aux=0.1`，容易被误读为重复加权，新文明确只加权一次。

代码核对以 `C:/workspace/SE3-WAM-canonical` 的 `master` 提交 `394fcd7125a581a90279f973775fdc9e71768174` 为准：

- `src/se3_wam/models/se3wam_v2/heads.py:207`，`_CurrentObjectRegionHead`：最终 meta 均值，`Linear(d,256) → GELU → Linear(256,3072) → Sigmoid`，输出 `3×32×32`，而非原文的 patch token 线性重建。
- `src/se3_wam/models/se3wam_v2/heads.py:288`，`_FutureReadouts`，特别是 317–338、360–364 行：深度与动态 RGB 为每 patch 的 16×16 像素读出，DINO 为每时域 1024 维。
- `src/se3_wam/training/step.py:1156`：DINO 的 1024 维通道层归一化、有效深度和运动 RGB 掩码；RGB 转为 `[0,1]` 后监督。
- `src/se3_wam/objectives/future.py:34`，`evaluate_future_regression`：先平均通道平方误差，再按全局有效位置数归一化。
- `src/se3_wam/objectives/object_reconstruction.py:60`，`evaluate_object_reconstruction`：按有效 RGB 元素数归一化的绝对误差，即 L1；不是未来目标所用的 MSE。
- `src/se3_wam/data/future_targets.py:179`：运动表面阈值为 `0.001 m`。

### 7. 最近一级索引

`docs/writing/INDEX.md` 原无任务 7 条目；新增：

```markdown
- [v4 辅助外观目标精简报告](v4_t7_aux_report.md)：任务 7 的中英逐处改写、附录披露与编译版面检查；合并和验收该分支时读取。
```

## 附录保留位置与图 2 建议

| 正文被压缩或移除的内容 | 保留位置 |
|---|---|
| 未来深度、DINO、运动表面 RGB、当前目标重建的枚举 | 附录 A.3 `app:world`，Appearance targets 完整段落 |
| 部署跳过外观头、输出不进入动作 | 方法 §3.3 一句与附录 A.3 |
| no appearance targets 控制及各单项/组合消融 | 附录 F.3 `app:design_predict`、表 `tab:supp_predict` 最后一组 |
| 三个未来外观目标带来的 `\fillin{X.X}` 增益 | 正文 §4.4 保留一行；附录 E.2 “Image-space futures” 保留完整解释 |
| 外观辅助与度量预测的关系 | 附录 E.2 原句 “Appearance therefore helps as an auxiliary target, although it does not replace the metric forecast.” 及对应中文 |

建议任务 6 或合并者将图 2 的 `+ depth, DINO, RGB` 改为小字号的 `+ auxiliary targets`（中文可对应“+ 辅助目标”），保留虚线和 “World outputs (training only)” 标识。外观仍被如实披露，但视觉主线突出 SE(3) 与 sparse 3D flow。本分支没有修改 `figures/Fig2/architecture_tikz.tex`。

## 编译、版面与测试

基线先完整编译四个入口，随后运行严格检查与单元测试；修改后在同一 Windows / MiKTeX 环境执行相同流程。中文使用本机 ctex 字体，基线和修改后均无溢出或缺字。

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error paper_full.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
python scripts/check_build.py --strict
python -m unittest discover -s tests
git diff --check
```

| 指标 | 修改前 | 修改后 |
|---|---:|---:|
| 正文终止页 `main:body-end` | 8 | 8 |
| `main.pdf` 总页数（含 LLM 声明、参考文献） | 13 | 12 |
| `supplementary.pdf` 页数 | 24 | 24 |
| `paper_full.pdf` 页数 | 36 | 36 |
| `manuscript_zh.pdf` 页数 | 44 | 44 |
| 第 8 页右栏正文末字底部（距页顶，pt） | 571.91 | 524.09 |
| 第 8 页右栏至正文版心底部余量（pt） | 139.09 | 186.91 |
| 正文待填结果单元 | 247 | 242 |
| 其中表 3 待填结果单元 | 80 | 75 |
| 附录待填结果单元 | 1152 | 1152 |
| 正文/附录待填文本 | 64 / 82 | 64 / 82 |
| 单元测试 | 17 通过 | 17 通过 |

页末余量用 `pdfplumber` 提取正文最终一栏的文字边界测量，排除页眉、页脚、行号。CVPR 模板版心从距页顶 72 pt 起，高 8.875 in，即底部 711 pt。右栏余量增加 47.82 pt（约 16.87 mm，约四行正文）；左栏仍排满，末字底部为 713.15 pt（包含字形下伸部分），不能把右栏余量理解为整页通宽空白。独立正文总页数减一来自移除正文中的 DINOv3 引用后参考文献重排，正文依然是八页。

严格检查输出：四份 PDF 的 errors、undefined、multiply_defined、rerun、overfull、missing_glyphs 均为 0；LLM 声明、附录 A–G、参考文献检查 0 问题；中英数字差异 0 组，结构差异 0；`All checks passed.`。17 个单元测试全部通过，不改测试或检查脚本。待填单元恰少五个，是正文重复行移除的预期结果，其他数值与占位未填改。

使用 Poppler 渲染并检查正文第 8 页、附录第 2 页和中文第 19 页，表格、跨栏段落与字体显示正常，没有新增溢出、遮挡或未定义引用。基线第 8 页及修改后渲染暂存于本 worktree 被忽略的 `tmp/t7/`，可用于复查。

四份新编译 PDF 保留在本 worktree 供审阅，作为未提交的构建产物；提交只包含上述授权源码、报告和最近一级索引。未合并、未推送；后续按任务 6 → 任务 7 → 任务 5 的顺序集成，并在合并后重新编译核查。
