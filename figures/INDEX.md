# 论文图项目

各图目录保留项目名称，每个目录包含中英文图源、当前资产和按主题归档的旧资产。正文图号以当前编译 PDF 和 LaTeX 标签为准；制作或改进单张图，从对应项目进入。

| 项目 | 用途 | 当前状态 |
|---|---|---|
| [Fig1](Fig1/INDEX.md) | 首页两块首图：真机场景与成功率—时延 | P040 真机 RGB 与示意未来运动；右图读取主表 Native SR／p95 |
| [paradigms](paradigms/INDEX.md) | 引言单栏：按角色分配预测精度 | 同一录制场景的三种预测（Video WAMs、目标中心预测器、FoveaWAM），Blender 帧加投影的录制标签；脚本生成的可编辑 SVG、PDF 与中英文图注 |
| [Fig2](Fig2/INDEX.md) | SE(3)-WAM 架构 | 作者修订 PPTX 为编辑源，输入与读出虚线分组，子图标题下置，配套矢量 SVG 和 PDF |
| [Fig3](Fig3/INDEX.md) | 作用于运动目标的原理示意 | 已验收的可编辑矢量示意图 |
| [Fig4](Fig4/INDEX.md) | OnTimeBench 总览 | 实时评测机制对比、五个任务族与十四项任务的场景 |
| [Fig5](Fig5/INDEX.md) | 六个消融对照的旧版热图占位 | 当前正文采用[消融表](../tables/main_analysis.tex) |
| [Fig6](Fig6/INDEX.md) | 六项真机任务总览 | 正文单栏两列三行，带运动示意 |
| [FigS3](FigS3/INDEX.md) | 附录 D.4 真机失败：按类别条形图与配对条带 | 规格已定；占位，待真机试验 |
| [latency](latency/INDEX.md) | 附加延迟下的成功率扫描（正文单栏内左右双面板） | 含 BF16 Full 的十一配置五点均已验收 |
| [design_studies](design_studies/INDEX.md) | 附录 E 的历史表征、测试时历史干预与预测路径比较 | 真实数据；中英文矢量图及复现脚本 |

[共享绘图规范与补充图入口](../docs/writing/v2_figure_specs.md)说明尺寸、颜色和替换方式；[目录约定](README.md)说明资产如何归入项目。

各项目的 `archive/` 按**当前主题**收纳旧稿图源、PPTX、输出、数据与来源说明；目录编号不表示旧稿当时的图号，也不把历史结果当作当前实验。完整历史稿件快照仍保留在本机 `local_private/archived-*/`，不拆散其内部引用。
