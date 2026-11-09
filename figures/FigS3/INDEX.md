# FigS3 目录：真机失败分析（附录 D.4，规格 2026-11-03）

当前为占位；图体与图注在 `appendix/real.tex`、`zh/appendix/real.tex` 的 `fig:real_failures`。
出图后把 `\figplaceholder{...}` 替换为 `\includegraphics[width=\textwidth]{figures/FigS3/figS3.pdf}`，
`\caption` 与 `\label` 不动；如需改图注，先告知论文文字会话。

## 用途

用真机失败的构成，直接检验“时延是动态操作的瓶颈”：若高时延基线的失败以“过晚”为主，
而 \ours 的失败来自其他类别，即为真机上的直接证据。图只呈现事实；结论写在 D.4 正文。

## 总体

- 跨栏 `figure*`，宽 6.875 in（`\textwidth`），高约 2.1 in；(a) 约 35%，(b) 约 65%，栏间 0.15 in。
- 栏标题（加粗）：(a) **Failures by category**；(b) **One paired trial key**。
- 字体与正文图一致（Arial/Helvetica），打印后不小于 7 pt；矢量 PDF，(b) 中照片可嵌入位图（≥300 dpi）。
- 禁止：生成或修饰图像；“best”“first”等字样。

## (a) 按类别的失败

- 数据：D.4 失败分类表的原始计数（每方法 120 次测试试验），类别在测试前固定。
- 形式：每个方法一根横向堆叠条，行序 π0.5、DynamicWAM、ACT、\ours（与表一致，\ours 在最下并以细分隔线隔开）。
- 条长 = 失败次数；横轴 “failed test trials (of 120)”，0–120 固定刻度，各方法可直接比较。
- 分段顺序固定：late、misaligned、slip/drop、collision or safety stop、timeout、tracking lost（仅 \ours 有此段）。
- 配色：late 用珊瑚色（#D85A30）突出；其余五类用由深到浅的灰/蓝灰；tracking lost 用青绿（#1D9E75），与首图“流/感知”区分。配色需可在灰度打印下区分（同时加细白分隔线）。
- 段内数字：≥5 次才标注；图例放在 (a) 上方一行。

## (b) 配对条带图

- 选键规则（写进图注，不得事后挑选）：选一个任务和试验键，使 \ours 成功、且某个基线以其**最常见**的失败类别失败；若有多个，取试验键编号最小者。优先使用 late 最多的基线。
- 两行各五帧：上行 \ours（成功），下行该基线（失败）；同一试验键、同一第三人称相机、相同裁剪。
- 时刻：相对于各自第一条指令执行时刻的相同偏移（例如 0、0.25、0.5、0.75 s、夹爪闭合后 0.3 s；按任务时长调整，两行严格一致），每帧左上角标时间。
- 标注：夹爪闭合帧加细框；下行失败帧右下角标类别名（如 “late”）；目标位置可用细圆圈标出，不做其他修饰。
- 行首标签：方法名；行尾标签：success / 失败类别。

## 交付

- `figures/FigS3/figS3.pdf`（中英文共用；文字差异另出 `figS3_zh.pdf`）、生成脚本与可编辑源。
- 在本文件补充数据来源、所选任务与试验键、帧号。
- 不提交 git；旧文件移入 `figures/FigS3/archive/`，不删除；用 `git --no-optional-locks`。
