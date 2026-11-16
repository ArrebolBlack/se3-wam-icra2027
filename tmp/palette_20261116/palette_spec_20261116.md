# 全文绘图配色规范（2026-11-16 定稿）

本轮与用户逐项讨论并确认。原则：全文共用一套核心色板，颜色尽量少；同一颜色在不同图、甚至同一图内重复使用都可以，只要整体协调、符合科研审美。不挑冷门配色，不用浅色底配同色标题的“卡片”样式。

数据图另按第 2.5 节使用 matplotlib 标准 tab10；下列核心色板用于示意图和渲染图。

## 1. 核心色板（6 色）

| 名称 | 色值 | 主要用途 |
|---|---|---|
| 红 | `#C0263A`（文字可用 `#8C1526`） | 目标 SE(3) 预测（位姿、轨迹、线框）；错误（World pauses、消融降幅）；Fig. 2 的 ✗；Impact 族 |
| 蓝 | `#2859A3`（浅：`#7191BF`） | 物体运动（Fig. 4、Fig. 6 的位移/旋转箭头、历史残影）；world；Video WAM；Grasp 族 |
| 绿 | `#2E8540` | 正确（World advances、消融增益）；Fig. 2 的 ✓；Reactive；Place 族。不用偏青的 `#009E73` |
| 琥珀黄 | `#E69F00` | action；VLA；Capture 族 |
| 紫 | `#9467BD` | summary M；Pass 族 |
| 灰 / 黑 | `#6E6E6E` / `#1A1A1A` | 结构线、文字、静态场景、驱动物（撞击器）箭头 |

## 2. 两项领域惯例（不计入核心色板）

- **SE(3) 坐标轴**：经典 RGB 三色 `#D62728` / `#2CA02C` / `#1F77B4`（x / y / z）。不用 RViz 纯色（`#FF0000` 等，太刺眼且与流撞色），不用 Blender 色。Fig. 1、2、3 都保留 RGB。
- **场景流**：统一用 Fig. 1(a) 的画法，turbo 色带截取 0.12–0.66，按时间比例着色，0 为当前帧，1 为 +400 ms。渐变箭身加箭头头部，起点为白点、turbo 0.12 描边；色标为“0 → +400 ms”。有逐时刻标签时沿真实轨迹弯曲，Fig. 2 使用 `labels.npz` 的真实八步 `flow_end_px`（196×8×2），每个 50 ms 段至少细分三段。
- 早期“turbo 0.06–0.62、50–400 ms 点列、无箭头头部”的方案已否决，不再使用。

## 2.5 数据图与示意图的配色边界

- 数据图使用 matplotlib 标准 tab10；示意图和渲染图使用核心色板，坐标轴与场景流保留第 2 节的领域惯例。
- 颜色按图的比较层级分配：Fig. 1(b) 按类别上色，Fig. 5 按方法上色；同一方法的配对变体保持同色，依靠现有线型和空心／实心标记区分。
- 本轮使用的 tab10 色为红 `#D62728`、蓝 `#1F77B4`、橙 `#FF7F0E`、绿 `#2CA02C`、紫 `#9467BD`、灰 `#7F7F7F`。hex 与 matplotlib 的 `tab:red` 等名字等价。
- 仅修改颜色，版式、数据、图例布局、线型、标记、空心规则、线宽和 FoveaWAM 加粗保持不变。Fig. 1(a) 的目标线框与标签固定使用核心红 `#C0263A`，流保持 turbo，不随数据图切换为 tab10。

## 3. 各图用色

### Fig. 1（首图）
- (a) 真机照片：只做全局调色，不做局部修改。目标 +400 ms 线框与 “Target SE(3)” 标签用红；流按第 2 节 turbo 渐变箭头。
- (b) 散点按类别使用 tab10：FoveaWAM 红 `#D62728`（星形）；Video WAM 蓝 `#1F77B4`（方形）；VLA 橙 `#FF7F0E`（三角）；Reactive 绿 `#2CA02C`（圆形）。不用灰色表示任何一类方法。“≈1/10 the p95 latency” 的箭头和文字同用 tab:red。

### Fig. 2（三种预测方式）
- 以 `tmp/fig2_20261116/fig2_preview_D2.svg` 为定稿。版式、字号、文字和放大区域不变，正式生成脚本直接实现，不依赖 monkey-patch。
- 流按第 2 节沿真实八步轨迹画 turbo 0.12–0.66 渐变箭头，头部取 turbo 0.66；深色细边 `#142039`、不透明度 0.82。全图箭身 / 头长 / 细边为 0.62 / 1.9 / 0.16 pt，放大图为 0.95 / 3.0 / 0.22 pt。
- 运动采样起点为白点、turbo 0.12 描边；静止采样为稍小的白点、`#6E6E6E` 灰色细边。删除原单色蓝箭头与蓝点。目标 patch 的流保留，在 (c) 放大图中位于目标 SE(3) 图层下面。
- “Sparse 3D flow” 标签用深蓝 `#263E74`。(c) 标题行右侧放右对齐色标：“0”、约 22 pt 长的同款渐变箭头、“+400 ms”；字号 6.8 pt，文字 `#31455C`。
- 目标轮廓、原点轨迹、“Target SE(3)” 标签与引线均用核心红 `#C0263A`，标签不使用深红版。原点轨迹加白色衬底，50 ms 刻度及两个位姿原点用白点红边；坐标轴保留 RGB `#D62728` / `#2CA02C` / `#1F77B4`。
- (a)(b) 下方 ✓ 用绿 `#2E8540`、✗ 用红 `#C0263A`，只给符号上色，文字保持黑色；删除原 `BAD = #C4262E`。
- 四帧仿真底图使用共享 `studio_controls.py` 的 `DEFAULTS`，全局 specular 0.10，其余参数保持原版；保留传送带原版绿色，不覆盖颜色、不降饱和。

### Fig. 3（架构，`figures/Fig2/fig2_se3wam.*`，编辑源为 pptx）——已确认
按组件含义上色，版式与文字不变。浅底统一为主色与白按约 88% 白混合。

| 组件 | 线 / 字 | 填充 |
|---|---|---|
| World stream 区块、Vision Encoder、patch token S、World FFN、Flow Decoder、(b) S 行、(c) World / World prefill | 蓝 `#2859A3` | `#E5EBF4`（区块大底 `#F4F7FA`） |
| Action stream 区块、Action Encoder / FFN / AdaLN / Decoder、token A、(b) A 行、(c) Action / Action update、Flow time u 连线 | 深琥珀 `#B37C00` | token 与 (b) A 行 `#F1CA73`；区块 `#FBF1D9`（大底 `#FDF8ED`） |
| Summary M：token、M 行文字、残差连线、(b) M 行、(c) M 方块 | 紫 `#9467BD` | `#F2EDF7`（(b) 中 M 行可加深到约 18% 浓度，提高与斜线格的对比，可选） |
| 目标：SE(3) Encoder、target token、**SE(3) Decoder**、预测轨迹虚线 | 红 `#C0263A` | `#F9E9EB` |
| State Encoder、robot token、LN、Shared attention、Output proj.、Q/K/V、目标历史箭头 | 中性灰（原样；历史箭头 `#6E6E6E`） | 原样 |
| 位姿坐标轴 | `#D62728` / `#2CA02C` / `#1F77B4` | — |

- SE(3) Decoder 用红（2026-11-16 用户确认）：它输出目标的 SE(3) 预测，与 SE(3) Encoder、预测轨迹同色，突出“目标被单独精确处理”。原图按“从 M 读出”用 M 色，已否决。
- 原图的灰蓝 `#557A9C`、土黄 `#9C8223`、墨绿灰 `#4D7169`、砖粉 `#C7685D`、棕橙轨迹 `#AE6547` 全部替换。
- 预览：`tmp/palette_20261116/fig3_arch_palette20261116.svg`（由 `recolor_fig3.py` 从 `figures/Fig2/fig2_se3wam.svg` 生成，仅供核对；正式修改在 pptx 中进行）。

### Fig. 4（OnTimeBench）——已确认，当前版见 `tmp/palette_20261116/`
- (a) “World pauses” 红 + ⏸ 图标；“World advances” 绿 + → 图标；去掉胶囊底色。“18 cm” 位移箭头与标注属于物体运动，用蓝。
- (b) 环形图与 (c) 卡片边框用族色：Grasp 蓝、Place 绿、Pass 紫、Capture 琥珀黄、Impact 红。卡片白底，标题黑字。
- (c) 物体运动（位移、旋转、历史残影）用蓝；撞击器箭头用黑 `#1A1A1A`；图例同步。
- 渲染图：保留原版渲染与原版绿色（饱和度不降）；传送带泛白是表面反光过强造成的，精修时在 Blender 里把反光强度（specular）从 0.5 降到 0.10（见第 5 节）；DOMINO / OnTimeBench 两格与 Capture 一排的蓝灰桌面改为中性深灰（与 Pass 族桌面一致）。当前版本是在像素上近似处理，精修时应改 Blender 材质并重渲染。

### Fig. 5（延迟曲线）
- 按方法使用 tab10：(a) ACT 绿 `#2CA02C`、DP 灰 `#7F7F7F`、DynamicVLA 紫 `#9467BD`、PUMA 橙 `#FF7F0E`、OpenWAM-α 与 OpenWAM-α (off) 蓝 `#1F77B4`。OpenWAM 两个变体同色，off 保留虚线空心。
- (b) π0.5 与 π0.5+SE(3) 同橙色 `#FF7F0E`，DynamicWAM 与 DynamicWAM+SE(3) 同蓝色 `#1F77B4`；Base 用虚线空心，+SE(3) 用实线实心。
- 两面板的 FoveaWAM 及图例 “FoveaWAM (Ours)” 文字用 tab:red `#D62728`，保留现有实线圆点与加粗；其余线型、标记、线宽和图例位置不变。

### Fig. 6（真机）
- 运动箭头保持蓝 `#2859A3`，加白色描边。

### 表格
- Table 3 消融：降幅红、增益绿，保持现有约定。

## 4. 被否决的方向（不要回退）
- 赭橙 + 暖奶油底 + 石板蓝（像 Claude 品牌色，AI 味）。
- “只有目标有颜色、其余全黑灰”的单色方案。
- 物体运动用红色（红箭头贴在红/橙目标上会融在一起，在绿色传送带上刺眼）。
- 传送带降饱和（任何幅度都不需要；泛白来自反光，不是颜色）。
- 偏青的绿 `#009E73`；Tableau 浅黄做线条色；ColorBrewer 橙（与红太近）。
- 场景流的早期 turbo 0.06–0.62 点列、无箭头头部方案；现用 Fig. 1(a) 的 turbo 0.12–0.66 渐变箭头。

## 5. 自建 benchmark 的 Blender 渲染默认参数（2026-11-16 用户确认）
- **反光强度 specular = 0.10**（原版 0.50），其余参数保持原版：AgX Medium High Contrast、曝光 0、整体饱和度 1、传送带颜色不覆盖、机械臂与其他材质粗糙度 0.34、传送带粗糙度 0.34、灯光不变。
- 依据：调色台 agentview 第 30 帧对比（t1_belt、t2_trans、t5_replan，t4_slider 作对照）。原版传送带近处大片泛白；0.15 基本消除；0.10 最均匀、饱和度最高（传送带绿色平均饱和度 0.46–0.48 → 0.59–0.61）。
- specular 是全局材质参数：无传送带的场景里蓝灰桌面也会略变深、更哑光；机械臂与目标物体无可见变化。
- 不要用提高传送带粗糙度来压反光（0.6、0.8 会把高光打散成整片发白的浅绿）。
- 适用于后续全部自建 benchmark（OnTimeBench）的 Blender 渲染，包括 Fig. 2、Fig. 4 与补充材料中的场景图。

## 6. 预览素材
- 对比图在本对话中给出：流色带 turbo 对比 viridis、坐标轴三方案、Fig. 1(b)/Fig. 5 三套蓝黄绿、Impact 候选色、撞击器箭头六色、反光强度三档、Fig. 3 SE(3) Decoder 红/紫。
- Fig. 4 当前版：`tmp/palette_20261116/ontimebench_palette20261116.svg`，由同目录 `recolor_fig4.py` 从 `figures/Fig4/ontimebench.svg` 生成。
