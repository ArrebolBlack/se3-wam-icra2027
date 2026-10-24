# v4 任务 5：真机任务与图片核实

核查日期：2026-10-23。分支 `v4-t5-real`，起点 `afc71e560f2837ca2704789941c6ab375e3f62c4`。只修改授权的真机段落、共享真机表、机器人宏、图片和最近一级索引；未合并或推送。

## 结论

用户补充来源对应**五类场景、六个计划任务**，不是原稿的五任务。六张现成图片都是带 `AI-GENERATED DRAFT` 标记的概念图；可以说明任务意图，不能证明装置、真实配置、成功案例或运行结果。正文与附录的真机部分改为六任务设计，图 `fig:real_setup` 用六张图片替换纯文字占位。图 `fig:real_trials` 仍待真实同步帧和轨迹日志。

当前资料不足以确认六任务的速度、成功/失败阈值、示范数、试验数、随机化、基线、在线跟踪器和检查点。上述字段保留 `\fillin`；所有结果单元格继续占位，去掉没有结果支持的优势、失败模式和预训练收益归因。

## 依据及版本

| 来源 | 本次使用的范围与证据状态 |
|---|---|
| 用户指定对话 `codex://threads/01a1435b-0781-7d51-91fd-15f7485fdd8c`（规划论文真机实验） | 用户补充的任务与图片来源；六任务及 AI 概念图属性由父任务核对并转交。 |
| [Notion《10.16》](https://app.notion.com/p/3fb7e1a21323802b9078d41130996b87)，本次直接读取 | “真机实验／实验设计／物品采购／购物清单”；页面最后编辑时间 `2026-10-22T17:42:00.188Z`。设计列出两种传送带任务、转盘、小车、碰撞球、斜坡滚/滑落；采购表明确尚未下单，转速和最低稳定车速要到货实测。不是运行记录。 |
| `C:/workspace/se3-wam-research`，读取时 HEAD `6033f256a46c77598f02569f07c4ca3a369f3221` | 下述研究文档来自本地工作树，本次只读。 |
| `docs/experiments/RR0/RR0.md:21` | 历史单传送带候选 `RealConveyor-180-v1`；三种物体×三种速度×20 次，180 次/方法，配对键、分组随机化与 0.5 s 抬升保持只适用于该计划。不能推广为六任务协议。文档末尾仍列现场和模型阻塞。 |
| `docs/real_robot_deployment/FLOW_LABEL_PIPELINE.md:26` | 固定 D435 是用户已报告条件；分辨率、帧率、双机布置、机器人型号、接口及状态频率未确认。 |
| `docs/real_robot_deployment/PREFLIGHT_RUNBOOK.md:25` | 明确不能把 DROID 15 Hz 或仿真默认周期当成真机控制频率；硬件与相机参数需要现场填写。 |
| `docs/experiments/POSE0/POSE0.md:9` | 当前离线链为 GroundingDINO＋SAM2.1＋WildDet3D；原生 box SE(3) 不保证固定物体坐标系，在线闭环及共卡部署未实测。Any6D＋FP++ 为备选，FoundationPose 为历史比较。 |
| `docs/PROJECT_BRIEFING.md:32` | 5090 是目标部署约束，真机数据尚待采集；DROID 基座与仿真权重分开，任务后续独立微调。 |
| 图片原目录 `C:/Users/XUE/.codex/visualizations/2026/10/16/01a1435b-0781-7d51-91fd-15f7485fdd8c/real-robot-paper-placeholders/individual/` | `INDEX.md` 及六个 PNG 明确 AI 概念图身份。已逐图目视；保留全部画面和标记。最初只读查看的素材工作树随后由其负责对话清理；论文仓库素材提交 `4e403d1` 保留原始资产。 |

## 逐项最终写法

任务编号按已有六图顺序指定，在正文、两个结果表和附录任务表中一致。名称与装置来自 Notion 任务设计；具体方块、盒子、球、小车的图示来自现成图片，并明确为计划物体。

| 任务 | 最终名称与运动装置 | 物体与任务意图 | 保留占位 |
|---|---|---|---|
| T1 | Conveyor grasping／传送带抓取；传送带 | 运输可抓方块，机器人抓取 | 带速；稳定抓取/抬升阈值；失败规则；N |
| T2 | Moving-receptacle placement／移动容器放置；传送带 | 移动无盖盒，机械臂放入方块 | 带速；放入/留存阈值；失败规则；N |
| T3 | Turntable grasping／转盘抓取；转盘 | 方块绕转轴运动 | 角速度、半径；抓取/抬升阈值；失败规则；N |
| T4 | Moving-car grasping／移动小车抓取；遥控小车 | 抓取桌面行驶的微型小车 | 速度及路径；抓取/抬升阈值；失败规则；N |
| T5 | Post-collision interception／碰撞后拦截；球杆触发球间碰撞 | 拦截被碰撞后的第二个台球 | 碰撞及出射速度；捕获阈值；失败规则；N |
| T6 | Ramp interception／斜坡拦截；重力与斜坡 | 网球滚落或方块滑落；图片只画滚球 | 坡度、释放条件、速度；捕获/保持阈值；失败规则；N |

不把采购尺寸、图片比例或提示词中的几何当成实测设置，不把小车当作第二个圆周任务，也不把所有非匀速任务合并成一个加速任务。可采购的圆柱、球和方块不等于最终每任务物体库存。

| 项目 | 最终写法与原因 |
|---|---|
| 机器人、夹爪 | Franka 计划平台；具体型号和夹爪型号占位。RR0 支持 Franka 家族，资料不能核实 Panda/FR3 等具体型号，也不能凭生成图片推定夹爪。去掉已确认七自由度/平行夹爪配置的口气。 |
| 相机 | 固定 RealSense D435；分辨率、帧率、标定过程、外参和每基线视角配置占位。第二台及腕部布置未获现场证据。 |
| 控制频率 | 在真机段落独立占位，不沿用仿真的 `\cfgControlRate` 20 Hz。 |
| 部署 GPU | 保留 `\cfgGPU` RTX 5090，但真机段落明确为目标部署硬件，未声称测得延迟。该共享宏未修改。 |
| 示范数 | 六任务各 N 占位，不用 POSE0 的泛指 200+ episode 或其他数据集数量代替。 |
| 试验与随机化 | 各方法、各任务 n；试验键、物体/起点/速度采样、方法顺序、reset、起止和数据划分均占位。原稿每任务 20 不再暗示正式次数；表格的 `00/20` 改为 `s/n`。 |
| 基线 | π0.5、DynamicWAM 两行包入 `\fillin` 并说明是候选；未自行确定或删除候选集合。无 DROID 基座行保留为比较模板。 |
| 在线跟踪器 | 跟踪器名称占位，FoundationPose 只作为候选提及；没有用离线 WildDet 替代在线已验证跟踪器。 |
| CAD/参考视图 | 方块、盒子、小车、台球/网球与滑动物体的参考资产、固定 frame 和初始化统一逐物体占位；没有任何每物体映射可核实。 |
| 预训练与结果 | 真机微调所用检查点、DROID 对照、仅动作预训练对照待确认/待运行，SR、CI、延迟及接触误差仍占位。移除收益归因和“晚闭合是主要失败”等无实验证据的文字。 |

## 图片与双盲核查

- 六张图按原始 1536×1024 等比缩为 900×600 PNG，使用 Pillow LANCZOS 和无损 PNG 保存；没有裁剪、补绘、修饰内容或移除标签。每图约 2.24 英寸宽，约 402 ppi。
- 六图大小依次为 696451、623298、580655、607049、581005、686370 bytes；全部低于 1.5 MB。
- 逐图目视无人物、人脸、实验室/机构标识、姓名或可识别真实地点；小车的商品徽标不是机构身份。所有 AI 标记可见，图注再次声明概念图和非实验依据。
- 图 `fig:real_setup` 改为跨双栏 3×2 任务示意，没有把它描述为现场照片、传感器布置或第一指令时刻。
- 图 `fig:real_trials` 保留占位：仍缺同一试验键的成功与失败、基线对照、同步 query/执行/接触帧、跟踪和控制日志；单帧生成概念图不支持这些内容。

## 超出授权范围的冲突

以下只记录，未越界修改；集成时应统一修订。

- `main.tex:40`、`manuscript_zh.tex:13`，`sections/introduction.tex` 及中文，引言贡献条目，`sections/conclusion.tex:10` 及中文仍称五个真机任务或写为已取得优越结果；六任务计划不能支持该结论。
- `appendix/results.tex:111`、`zh/appendix/results.tex:48` 仍声称视频覆盖全部五任务；现有素材不是试验视频。
- `tables/supp_pretraining.tex:5` 的 DROID 对照仍称五任务；该表不在本任务允许范围。
- `sections/method.tex:107`、`appendix/implementation.tex:47` 及中文，`tables/supp_tracker.tex:5` 仍把 FoundationPose 写作真机部署事实；当前资料仅支持候选，逐物体 CAD/参考设置未定。
- `appendix/evaluation.tex` 的 Timing 小节在本次修改区间外，仍把共享 RTX 5090 计时直接称为机器人已部署硬件，并描述记录了时序日志。当前真机资料没有相应部署实测。
- `appendix/pretraining.tex`、预训练表中的真机收益叙事要等待真实配对试验，不可由预训练已启动推出；本任务只修正正文 §4.3 的 Pretraining 段。
- `docs/writing/v4_open_questions.md` A5 仍是提交时的五任务状态；本报告供集成者更新该历史待确认条目，不改越界文档。

## 验证

原稿 `afc71e5` 在同一 Windows/MiKTeX 26.5 环境先做完整编译：英文 main/supplementary/paper_full 为 13/24/36 页，中文 44 页；正文结束于第 8 页。错误、未定义/重复引用、待重编译、溢出、缺字均为 0，中英数字/结构差异均为 0，strict 通过。

最终按以下顺序完成构建：

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error supplementary.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error paper_full.tex
latexmk -xelatex -interaction=nonstopmode -halt-on-error manuscript_zh.tex
python scripts/check_build.py --strict
python -m unittest discover -s tests
```

| 交付物 | 总页数 | 错误／未定义／重复引用／待重编译／溢出／缺字 |
|---|---:|---|
| `main.pdf` | 13 | 全部 0 |
| `supplementary.pdf` | 24 | 全部 0 |
| `paper_full.pdf` | 36 | 全部 0 |
| `manuscript_zh.pdf` | 44 | 全部 0 |

正文仍在第 8 页结束，没有正文浮动体落到第 8 页之后。`check_build.py --strict` 输出 `All checks passed.`；中英数字差异 0、结构差异 0，声明/附录/参考文献检查 0 问题。17 个单元测试全部通过，`git diff --check` 通过。首轮新增的两处中文溢出已通过缩小图格列间距及调整中文硬件句序修复，最后完整重编译验证为 0。

占位统计：正文结果 251 格，附录结果 1156 格；正文文字 59 处，附录文字 105 处。真机主表 24→28 格，真机附表 31→35 格，均因为从五任务增加到六任务（四个方法各增一格）。原来只有示例的统一试验数换成未知 n，未填入数值结果。

图 `fig:real_setup` 与任务定义表位于补充 PDF 第 12 页，成功次数表位于第 13 页；正文真机表在第 7 页，真实试验占位图在第 6 页。父任务独立目视检查正文第 7 页与补充第 12 页，确认图表没有裁切、重叠和身份信息，AI 图注与面板标记可见。

数值占位是本任务要求；未运行 `--final`，没有把占位视作真实结果。四份 PDF 重新编译留在工作树中供审阅，不进入源文件提交。完整临时日志放在忽略目录 `tmp/`，本报告仅保留摘要。
