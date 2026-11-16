# 全文绘图配色规范（2026-11-16 定稿）

本轮与用户逐项讨论并确认。原则：全文共用一套核心色板，颜色尽量少；同一颜色在不同图、甚至同一图内重复使用都可以，只要整体协调、符合科研审美。不挑冷门配色，不用浅色底配同色标题的“卡片”样式。

## 1. 核心色板（6 色，用于示意图与渲染图；数据图见第 2.5 节）

| 名称 | 色值 | 主要用途 |
|---|---|---|
| 红 | `#C0263A`（文字可用 `#8C1526`） | 目标 SE(3) 预测（位姿、轨迹、线框）；错误（World pauses、消融降幅）；Impact 族 |
| 蓝 | `#2859A3`（浅：`#7191BF`） | 物体运动（Fig. 4、Fig. 6 的位移/旋转箭头、历史残影）；world；Grasp 族 |
| 绿 | `#2E8540` | 正确（World advances、消融增益）；Place 族。不用偏青的 `#009E73` |
| 琥珀黄 | `#E69F00` | action；Capture 族 |
| 紫 | `#9467BD` | summary M；Pass 族 |
| 灰 / 黑 | `#6E6E6E` / `#1A1A1A` | 结构线、文字、静态场景、驱动物（撞击器）箭头 |

## 2. 两项领域惯例（不计入核心色板）

- **SE(3) 坐标轴**：经典 RGB 三色 `#D62728` / `#2CA02C` / `#1F77B4`（x / y / z）。不用 RViz 纯色（`#FF0000` 等，太刺眼且与流撞色），不用 Blender 色。Fig. 1、2、3 都保留 RGB。
- **场景流**：turbo 色带截取 0.06–0.62 段（深蓝 → 青 → 绿 → 黄，不含红），颜色表示预测时刻 50 → 400 ms。画法参考 PointWorld：逐时刻点列轨迹，不画箭头头部，需加一条“50 → 400 ms”小色标。正式稿用 `labels.npz` 中真实的 8 步 flow（`flow_end_px`，形状 196×8×2），预览中的直线插值只用于看色。

## 2.5 数据图与示意图的分工（2026-11-16 用户确认）

- **数据图**（matplotlib 直出：Fig. 1(b)、Fig. 5，以及附录中的曲线、条形图、散点图）用 matplotlib 标准 tab10：tab:red `#D62728`、tab:blue `#1F77B4`、tab:orange `#FF7F0E`、tab:green `#2CA02C`、tab:purple `#9467BD`、tab:gray `#7F7F7F`（必要时 tab:brown `#8C564B`）。理由：Python 直出的标准配色读者一眼认得，不像刻意挑的色；与 SE(3) 坐标轴（同为 tab10）和紫色同源。
- **示意图与渲染图**（Fig. 1(a)、Fig. 2、Fig. 3、Fig. 4、Fig. 6）用第 1 节核心色板。
- 两边含义对应：红 = 我们 / 目标，蓝 = Video WAM / 世界，橙或琥珀黄 = VLA / 动作，绿 = Reactive / 正确，紫同值。只是色值略有差别。
- **颜色按图的比较层级分配**：比较方法类别时按类别上色（Fig. 1(b)，点旁已有直接标注）；比较单个方法的曲线时每个方法一个颜色（Fig. 5(a)）；比较成对的原始版与 +SE(3) 版时，同一对同色，靠虚线空心 / 实线实心区分（Fig. 5(b)）。
- Fig. 1(b) 与 Fig. 5 中的同一方法，在可能的情况下沿用同一颜色。

## 3. 各图用色

### Fig. 1（首图）
- (a) 真机照片：只做全局调色，不做局部修改。目标 +400 ms 线框与 “Target SE(3)” 标签用红；流按第 2 节 turbo 点列。
- (b) 散点（数据图，用 matplotlib tab10，见第 2.5 节）：按类别上色。FoveaWAM tab:red `#D62728`（星形）；Video WAM tab:blue `#1F77B4`（方形）；VLA tab:orange `#FF7F0E`（三角）；Reactive tab:green `#2CA02C`（圆形）。不用灰色表示任何一类方法。“≈1/10 latency” 指示线与标注用 tab:red。

### Fig. 2（三种预测方式）
- 目标用红，流按第 2 节 turbo，坐标轴 RGB。仿真渲染与 Fig. 4 同样处理（原版绿色，反光强度 0.10）。

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
- 数据图，用 tab10（第 2.5 节）。(a) 每个方法一个颜色：FoveaWAM tab:red（最粗线）；PUMA tab:orange；DynamicVLA tab:purple；OpenWAM-α tab:blue（off 变体同色，虚线空心）；ACT tab:green；DP tab:gray。
- (b) 成对比较，同一对同色：π0.5 与 π0.5+SE(3) 用 tab:orange，DynamicWAM 与 DynamicWAM+SE(3) 用 tab:blue。Base 用虚线空心，+SE(3) 用实线实心。
- 已否决：同类成员同色只靠标记区分（100–150 ms 的交叉段分不清两条黄线）；同类成员用深浅区分（深黄发橄榄褐色，浅绿发白）。

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

## 5. 自建 benchmark 的 Blender 渲染默认参数（2026-11-16 用户确认）
- **反光强度 specular = 0.10**（原版 0.50），其余参数保持原版：AgX Medium High Contrast、曝光 0、整体饱和度 1、传送带颜色不覆盖、机械臂与其他材质粗糙度 0.34、传送带粗糙度 0.34、灯光不变。
- 依据：调色台 agentview 第 30 帧对比（t1_belt、t2_trans、t5_replan，t4_slider 作对照）。原版传送带近处大片泛白；0.15 基本消除；0.10 最均匀、饱和度最高（传送带绿色平均饱和度 0.46–0.48 → 0.59–0.61）。
- specular 是全局材质参数：无传送带的场景里蓝灰桌面也会略变深、更哑光；机械臂与目标物体无可见变化。
- 不要用提高传送带粗糙度来压反光（0.6、0.8 会把高光打散成整片发白的浅绿）。
- 适用于后续全部自建 benchmark（OnTimeBench）的 Blender 渲染，包括 Fig. 2、Fig. 4 与补充材料中的场景图。

## 6. 预览素材
- 对比图在本对话中给出：流色带 turbo 对比 viridis、坐标轴三方案、Fig. 1(b)/Fig. 5 三套蓝黄绿、Impact 候选色、撞击器箭头六色、反光强度三档、Fig. 3 SE(3) Decoder 红/紫。
- Fig. 4 当前版：`tmp/palette_20261116/ontimebench_palette20261116.svg`，由同目录 `recolor_fig4.py` 从 `figures/Fig4/ontimebench.svg` 生成。
