# v4 T6：模型实现与配置核查（2026-10-23）

核心主张与当前候选代码一致：目标 SE(3) 与稀疏 3D 位移预测只提供训练监督；Action 读取 world 的 meta 隐状态，不读取解码预测；默认 action-only 推理跳过全部预测头。无需停止或改动该主张。

主要更正是场景不能读取 meta、位姿头为 meta 均值上的线性层、丢失目标槽位被掩码而非替换为学习嵌入、流损失不按可见性屏蔽位移项，以及 DROID 训练/验证划分和 S8 监督范围。同步执行与论文其他章节的实时叙述冲突，仍需负责人决定协议；本任务只修正方法附录中获准的实现事实。

## 来源与复核边界

- 论文起点：`paper-v4-20261023` / `afc71e5`；本 worktree：`C:/workspace/se3-wam-icra2027-t6`，分支 `v4-t6-code`。
- 模型：`C:/workspace/SE3-WAM-canonical`，干净的 `master` / `origin/master` = `394fcd7125a581a90279f973775fdc9e71768174`。只读 `git ls-remote origin refs/heads/master` 与本地一致，没有修改或 fetch 模型仓库。
- 研究：`C:/workspace/se3-wam-research`，核查时干净，提交 `6033f256a46c77598f02569f07c4ca3a369f3221`。
- 执行参考：`C:/workspace/se3-wam-dynamic-benchmark-canonical`，干净 `main`，提交 `80b1830e717aed39333a6f08b2c188c10bc084ce`；由本任务主 Agent 只读核验并提供下列原生控制/rollout 证据。
- 下文 `M/` 指模型仓库的 `src/se3_wam/`，`R/` 指研究仓库，`B/` 指 benchmark 的 `src/se3_wam_benchmark/`。行号对应上述提交。配置 `P5` 指模型仓库 `configs/experiments/p5_dense_dream20.yaml`；`DROID` 指研究仓库 `docs/experiments/PW0/results/current_launch/droid_48layers_w64.yaml`。
- 本次为源代码、配置与记录审计，没有运行训练、闭环或重新统计大型模型参数。宿主 Python 无 torch；历史实测计数结合当前参数构造静态对照使用，未把静态核查称为新实验。

## 1. Token 组成与 S8

原写法 → 每个查询 196 patch + 8 target + 8 robot = 212 scene，16 meta，8 Action；未说明 S8 是否互相读取。

代码事实 → `P5:13–19,65–85` 明确 T8/S8/H8/K8、current、eef7/history/current_kinematics。`M/models/se3wam_v2/trunk.py:_window_inputs:464–486,507–541` 只保留当前 196 patch 和历史状态；`model.py:371–372,1593–1595` 创建/广播 16 meta；`tokens.py:_ActionTokenProjection:184–194,245–246` 创建 8 Action，并向已有 token 加 horizon embedding。`layer.py:21–24,226–242` 将 B×S 合并为 batch，S 从不是注意力轴。图像 view/depth/geometry embedding 位于 `frame_encoder.py:241–266,535–584`；相对时间在 `model.py:1408–1419`，不是额外 token。当前配置无语言、额外视角、未来 query 或独立 Flow-FM token。

新写法 → 保留 token 数；附录明确无语言 token、嵌入不增加槽位，以及 S8 各预测位置拥有自己的因果历史且无跨位置注意力。正文把“输入成本不随历史增长”收窄为“视觉编码成本”，因为状态 token 数仍随 T 增长。

## 2. 注意力掩码

原写法 → 场景与 meta 双向读取；图 2 包含 S 行 M 列与双向箭头。

代码事实 → `M/models/se3wam_v2/attention.py:_ThreeStreamAttention.__init__:72–77` 的组顺序为 scene/meta/flow/action，允许键为 `(0,)`、`(0,1)`、`(0,2)`、`(1,3)`；当前 direct-displacement 候选无 Flow-FM token。因而 **S→S；M→S,M；A→M,A**。`attention.py:315–363` 用同一个 allowed-key 集合构造 dense/factorized 注意力；Action 不读取场景，Action 间是双向读取而非因果 mask。`layer.py:67–94,157–193` 只向 Action AdaLN 注入 tau；world 不读取 Action 或其流时间。

新写法 → 英中方法图注、主干段、附录与图 2 均修正；删除图中 S 读 M 格子，将 S/meta 双向箭头改为 scene 向 meta 的信息箭头。核心训练监督/部署跳过结论保持。

## 3. 主干、归一化与参数

原写法 → shared attention / split FFN，24×1024/16 heads/ratio4，504.0M backbone、523.8M trainable；冻结 MAE-B/16 与 DINOv3-L/16。

代码事实 → `P5:66–76` 与上述结构一致。`M/models/se3wam_v2/attention.py:78–101` 对 split_ffn 共用 QKV 与 output linear；`layer.py:67–94,300–317` 分别使用 world 与 Action 的两层 SiLU FFN（1024→4096→1024、dropout 0），world scene/meta 共用普通 LN；Action 的 attention/FFN 前均为独立 AdaLN。`M/models/common/adaln.py:74–82,111–119` 是无 affine LN，再由 `SiLU(tau)→Linear(1,2d)` 得到 scale/shift，作用为 LN(x)×(1+scale)+shift。

`R/docs/experiments/P5-DAY1/dense_candidate.md:45–62` 的实测计数：主干 503,955,456；可训练 523,802,967；MAE 冻结 85,798,656；策略总量 609,601,623；独立 DINO teacher 303,129,600。按本次源代码每层 20,998,144 ×24 可复算主干计数。`git diff 4171b84a..master -- src/se3_wam/models src/se3_wam/perception` 表明 P5 参数构造没有变化；变更为对象关闭条件、数据绑定与执行优化。没有再次实例化计数。

`M/perception/future_targets.py:185–193` 明确 `identity="dinov3_vitl16"`；不是 DINOv2 或 ViT-L/14。`P5:204–208` 明确 frozen `mae_vitb16` /224。

新写法 → 保留数值与宏，补充 shared Q/K/V/output 和 SiLU；未将 teacher 计入可训练策略规模。参数宏无需改动。

## 4. 输入编码与丢失处理

原写法 → patch view/depth/XYZ +3D RoPE，目标 25D、三 flags、28→d→d GELU；丢失目标由 learned embedding 替代；加速度只说相邻速度之差。

代码事实 → `M/models/se3wam_v2/frame_encoder.py:241–266,535–584` 实现 view bias、无 bias depth/geometry linear；`M/perception/geometry.py:_patch_average:107–110` 有效像素平均深度；`_robot_base_patch_source_points:114–169` 固定中心像素反投影；`attention.py:138–153` 只在有效几何位置执行 3D RoPE，非 patch token 的几何掩码关闭。`object_tokens.py:_object_motion_descriptors:19–30,65–110` 顺序为 p3/logR3/dp3/logdR3/dt1/v3/omega3/a3/alpha3；槽0–6为区间，槽7为当前绝对位姿。a/alpha 除以区间中心间隔，首个区间没有加速度。`_ObjectMotionTokens:116–137` 标准化25D并拼接pose/interval/acceleration flags，经28→d→d GELU。`model.py:1408–1419` 添加相对时间并将无有效 feature 的 token 清零，`trunk.py:514–526` 屏蔽键。没有 learned lost-target token。

`frame_encoder.py:_robot_state:446–470` eef7 = 基座位置3 + rotation vector3 + gripper_open_fraction1，不含关节。当前配置只用 agentview；没有语言输入。

新写法 → 修正无效槽位/加速度，机器人开度改为比例；保留其余已核实编码。跟踪器的实时线程、丢失判据与真机插值规则不是该模型仓库提供的可运行实现证据，保留在待确认列表，没有把它们当成本次模型验证结果。

## 5. 预测头与外观目标（外观段仅记录）

原写法 → 位姿头为 target/meta 池化上的 MLP；流头为 patch linear；目标 RGB 重建误写为当前 patch linear。

代码事实 → `M/models/se3wam_v2/model.py:1613–1634` 将最终16个 meta 的均值送至位姿/目标重建头，将最终当前196 patch送至 future readouts。`heads.py:_ObjectPoseDeltaHead:148–178` 是单个 `Linear(d,8×6)`，当前关闭 late injection（`P5:144`）。`_FutureReadouts:297–326,340–364` 为每 patch 的 `Linear(d,8×4)` 位移xyz+visibility；future depth 为8×16×16、DINO为8×1024、dynamic RGB为8×3×16×16；depth/RGB拼回224×224，不是每 patch 一个均值。

`_CurrentObjectRegionHead:207–225` 为 **meta mean→Linear(d,256)→GELU→Linear(256,3×32×32)→Sigmoid**；目标当前框裁剪重建，损失是 L1（`M/objectives/object_reconstruction.py:60–75`），不是 patch线性解码或MSE。`M/training/step.py:1156–1159` 对 DINO teacher目标做1024通道LN；`M/data/future_targets.py:147–179` 运动掩码为世界位移大于1mm，包括机器人。

仿真 visibility 权重为 **1**：`P5:178–180`未覆盖默认值，`M/config/schema.py:328–330` / `training/trainer.py:731` 默认1；DROID显式0（`DROID:126–129`）。

新写法 → 修改位姿读出与仿真流损失说明；外观目标句子/Appearance段按任务边界保持原样。上述证据已交给 T7，最终合并应由 T7 的段落纠正当前RGB读出/损失；图中辅助标注保持 T6 原范围，不自行删改。

## 6. 损失、归一化与 noise8

原写法 → pose平移平方范数+0.1 geodesic平方；flow为可见性门控平方范数+BCE；noise8描述为每窗口8个样本。

代码事实 → 当前分支调用 `M/training/step.py:962–973` / `1311–1319` 的 `evaluate_object_pose`，不是旧 `evaluate_pose`。`M/objectives/pose.py:329–348,397–459` 计算平移三维平方范数及SO(3) atan2测地角平方，分别除以有效horizon数，权重1/0.1；原pose公式正确。

`M/objectives/future.py:evaluate_future_displacements:59–76` 位移目标除以 `P5:147` 的0.7154604845734799m，**三通道平均MSE**+权重1的逐位置visibility BCE；位移项没有乘visible，仍在有效但不可见点回归3D位移。`M/training/step.py:1113–1123` 使用future_scene_tracks_valid与visible；`M/data/future_targets.py:113–126,305–314` 区分几何有效与可见。不是“遮挡点只监督visibility”。

`P5:149–195`：Action1、future_environment1、pose1（translation1/rotation.1）、depth/DINO/dynamicRGB/reconstruction各.1；legacy Flow-FM、alpha、future_object通用项关闭，SE(3)由pose项负责。`M/objectives/future.py:14–44` 按有效位置数归一化，回归先通道平均；`M/training/trainer.py:1155–1198` 使用完整累积组计数并在DDP梯度归约后clip；`P5:270` 为accumulation_global。`training/step.py:762–767,873–900` 每个预测位置抽8对独立高斯噪声/均匀tau，复用world，平均Action损失；不会把global512变成4096原始窗口。

新写法 → pose式保留；流式改为normalized xyz/3 +逐位置BCE，去掉visible门控；动作式明确MSE_valid；noise8改为每query position的8对噪声/时间。外观损失权重关联文字由T7负责。

## 7. 动作与执行解码

原写法 → base-frame delta xyz/left rotvec/gripper，默认执行0.10m/0.5rad，夹爪sign。

代码事实 → `P5:47–57,79–83` E7/delta/discrete、rotvec，候选motion_limits为 **0.05m×3/0.5rad×3**。`M/models/io.py:327–330,360–382` 定义单位与base frame；`M/data/db0_v06_migrated.py:570–591` 的绝对动作转换在applied_tick读取测得EEF，并左乘旋转。`B/control/action.py:201–241` 将delta传给controller；`B/envs/base.py:624–635,1257–1261` 与benchmark `tests/unit/test_action_control.py:1480–1493` 验证非零旋转相对当前测得姿态；**零旋转可保留上次orientation goal**，不能把所有command统一写成query当前位姿的累计增量。

`M/data/normalization.py:166–217` 用去重有效命令的训练总体均值/std，`41–78`为逐维标准化/反标准化。`M/inference/policy.py:_physical_action_chunk:259–295` 按bundle motion_limits逐轴裁剪，`cli/export.py:57–59`允许显式0.10m override。gripper反标准化后为|g|≤deadband输出0，否则sign；原生默认deadband=0。

`R/docs/experiments/GRIPPER2/GRIPPER2.md:375–411` 当前已验证的**旧E5**部署是t4_sphere阈值.5/其他13任务.1、0.10m限幅、FP32/TF32/temporal+conditioning+compile；未知任务拒绝，不能自动外推到本次P5最终候选。

新写法 → 附录区分候选配置与显式override，说明application参考及零旋转例外，给出原生deadband公式并标明E5证据边界。没有将E5默认静默写成P5已部署事实。

## 8. 推理、缓存与同步协议

原写法 → Euler5、world cache、跳过heads；附录同时说规划期间继续旧chunk；S-hyper写FP16。

代码事实 → `P5:35–44` conditioning_cache=true；execution synchronous_receding_horizon/steps_per_replan1；Euler/nfe5；velocity_cache=false；temporal_cache=false。`M/inference/policy.py:1216–1243` select_action调用capture(action_only=True)，`989–999,1054–1059`传给solver并每query缓存conditioning。`solver.py:226–234,265–299`绑定action-only methods，`model.py:1596–1600`直接走trunk._prepare_action_conditioning，整个readout分支`1608–1641`不执行。`solver.py:972`起执行Euler更新。`executor.py:384–413`同步planning_snapshot并每条指令重新规划。

`P5:1–6`为FP32/compile=false/TF32=false；`solver.py:213–216,256–257`的fp32关闭autocast。E5 FP16测速不等于候选默认。`B/evaluation/rollout.py:351–377`同步先policy.act（363）后environment.step（374）；wall pacing（301–302）不让物理在推理期间推进。

新写法 → 保留Euler/cache/跳过头；附录纠正同步执行、推理暂停与FP32，删除“规划期间继续执行旧chunk”。摘要、引言、实验协议、附录C–G、结论的“共同物理时钟/推理持续运动”均不在授权修改范围，未改；方法§3.1的实时动机方程仍是条件性理论设定，不能作为现行评测协议的证明。

## 9. 仿真训练配方与表 S-hyper

原写法 → AdamW2e-4/wd1e-4/betas(.9,.999)/eps1e-8，warmup5174，cosine→0，global512，20epochs/51740updates，clip.1，主体FP32/MAE BF16；正式训练卡数/小时占位。

代码事实 → `P5:210–235,263–272`逐项一致，非fused、全局累积归一化、DINO episode cache。`R/docs/experiments/P5-DAY1/dense_candidate.md:3–7,18–34`明确该current/T8/24×1024/MLP4候选尚未正式训练；N800×14=11200 demos、stride1/valid_tail/drop_last=false、1324374训练窗口，350独立验证episode/41533窗口；每轮ceil(1324374/512)=2587，末次342，20轮51740，2轮warmup5174。`M/data/windowing.py:54–105`构造T−1+S=15观察轴，S8预测尾部mask，不跨S注意力。精度是冻结MAE BF16、输入/返回特征与可学习主体FP32、teacher FP32缓存；不应写“冻结teacher每训练步都计算”。

新写法 → 保留训练超参数与硬件/时长占位，明确最终仿真未启动，修正teacher计算描述、S8、noise8与推理FP32。没有用PW0的64卡填入P5训练硬件。`tables/supp_baselines.tex`仅修改ours行为“robot histories”，把未运行的3 seeds标为待填，预算仍是候选配方。

## 10. DROID 基座

原写法 → current RGB-D/T8 robot，no target pose，Action+XYZ+DINO，48层/1.02B；把598889窗口/42087episode写为训练量，缺少连续S8监督边界，暗示最终checkpoint已取得。

代码/记录事实 → `DROID:17–25,43–95`：单agentview/T8/S8/H8/K8，48×1024/16heads/ratio4/split_ffn，anchor=false/object_input_mode=none/se3_rotation=disabled/future_object=none。scene为196+8=204，meta16，Action8。`DROID:97–144` Action1/noise8、XYZ1/visibility0、DINO.1；其他heads/objectives关闭，位移尺度1m。`M/models/se3wam_v2/model.py:219–225,497–536`支持object-free分支；`M/data/pointworld.py:_window:437–477`以每个anchor扩展连续8个native image位置，仅原anchor保留世界记录；`read_frames:228–282`无观测深度的位置明确无效，不补假深度。

`R/docs/experiments/PW0/PW0.md:194,311–328,344–350`：训练37874episode/538740anchors，验证4213/60149；S8训练4309920预测位置，验证481192，原XYZ/DINO仅538740/60149位置监督，其他位置仅Action。48层可训练1,017.181M，MAE85.799M与DINO303.130M冻结另计。`DROID:160–219` global=64rank×micro8×accum1=512；20轮×1053=21060更新，warmup2106，AdamW/clip/precision同仿真、teacher cache绑定DROID。

`R/docs/experiments/PW0/PW0.md:15–38`记录正式训练已启动并保存10轮/update10530，从该点恢复继续；20轮尚未完成验收。不能把“configured20epochs”写成已完成预训练或真实机器人成功。

新写法 → 方法§3.6与附录B更正训练划分，保留全语料总量；补充连续S8/anchor-only世界监督、204scene、深度mask，明确ongoing及final checkpoint pending；宏48/1.02B/21060/64保持。真实机器人最终是否采用该基座与试点12层对照是否运行仍需负责人确认。

## 未改的冲突与待确认

1. 摘要/引言/§4.1实验协议/附录C–G/结论的连续物理时钟，不符合当前同步rollout；需作者明确最终协议。方法§3.1实时lead分析是动机，不代表已有实时实验。
2. T7负责的Appearance段仍需合并纠正：当前RGB来自meta均值、32×32 MLP/L1；depth与RGB是逐像素读出。已提供具体证据，T6未越界修改该段。合并紧邻的§3.3总结句时保留T6的“motion labels are cumulative / 运动标签从当前状态累计”，避免T7段落替换恢复成“all labels”，因为外观标签是绝对值。
3. `appendix/pretraining.tex` 仍有12/24/48科学规模选择、12层试点对照与fine-tuning成果式叙述；本次仅修正DROID配置事实，没有把尚未完成的对照写成已验证。相关结果仍为占位，需最终实验验收。
4. 跟踪器SAM2.1/Hiera-small、GroundingDINO初始化、跨两相机周期插值等，在所核模型代码中无可运行证据；真机部署规格由T5/负责人核实。论文已有tracker精度表不能视为本次实证。
5. P5最终训练卡数、时长、seed数、闭环结果、p95保持占位；E5的夹爪路由/10cm/FP16或FP32测速不自动适用于P5。
6. `paper_config.tex`的参数/候选配方宏与证据一致，所以没有无意义改写；硬件宏留给T5。默认图2物理时间示意仍表达实时问题设定，不作为同步仿真实测时序。

## 编译、检查与交付

执行命令（在本worktree）：

```text
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

首轮产生一处流公式6.25183pt溢出，已将公式拆行并同步中文。修复后四份编译成功；严格检查输出：main 13页（正文第8页结束）、supplementary 24页、paper_full 36页、manuscript_zh 43页；每份errors/undefined/multiply_defined/rerun/overfull/missing_glyphs均为0。EN/ZH数字差异0、结构差异0、LLM声明/附录A–G/引用检查0问题，`All checks passed.`。17项单元测试全部通过，`git diff --check`通过。结果占位保持：正文结果247格、补充结果1152格，正文文字64处、补充文字82处；ours的seed预算另显式标为待填。

架构图在main第4页；implementation在supplementary第1–2页，DROID在第3页起。主Agent已视觉检查main第4页与supplementary第2页：架构矩阵S行仅S格、公式拆行与动作协议排版清楚，无重叠或溢出。以上页数包含参考文献/附录，正文仍满足8页上限。

PDF为本地重新生成的验收产物，按用户源码修改范围不纳入提交。模型、研究、benchmark仓库均只读；未合并、未推送。
