# 盲审记录（2026-10-20 起）

**目的。** 检验稿件能否与真实顶会论文放在一起而不被认出是 AI 生成的，并达到高质量标准。
做法与工具见 [scripts/blind_review/README.md](../../scripts/blind_review/README.md)：
- 每轮把本稿与 4 篇真实论文（Motus、GEM-4D/RoMan-4D、Cosmos Policy、DAPL）统一处理成纯文本，交给一个全新的审稿代理。处理包括去模板、去作者、去图、关键数字 mask。
- 其余 14 篇真实论文作为参考池。审稿代理不能联网，只能在参考池里对比。

**防止主线漂移。** 盲审前的版本完整备份在：
- 仓库的 `local_private/archived-v2-20261020-pre-blind/`；
- 云端工作区的 `backups/repo_v2_pre_blindreview_20261020.tgz`。

每轮只改表达、逻辑漏洞、可信度细节和公平性。交互时刻框架、三条原则、SE(3)-WAM 的设计与实验矩阵的主体不变。改动若涉及主线，需单独列出，说明理由。

## 第 1 轮（2026-10-20）

**结论：没有通过。** 审稿代理以约 90% 的置信度判定本稿为 AI 生成，质量评分 5/10（弱拒）。四篇真实论文的 AI 概率在 1–4%，评分 5–7。

**主要理由**（按审稿代理给出的强度排序）：

1. **残留的草稿痕迹。**
   - 表 S8 图注写着 "Values marked as pending…"。
   - 附录 E.1 的随机种子 `20261018` 像日期，再配上 2026 年 10 月的 arXiv 引用，审稿代理据此认为时间线不可能。
2. **"预注册方案"口吻。** 全文多处是"若……则……"式的条件规则（选择规则、交互检验）；还承诺报告某些指标，却没有对应的表。
3. **文体指纹。**

   | 指标 | 本稿 | 真实论文 |
   |---|---|---|
   | 分号（每千词） | 15.5 | 0.4–2.5 |
   | 第一人称 we（每千词） | 3.1 | 8.8–22 |

   此外还有：
   - ", not X" 对照句 16 处，真实论文为 0；
   - 格言句与 "Takeaway" 小结；
   - 成串的 never；
   - 一句话在两处逐字重复；
   - 临床试验式术语（arms、equivalence margin、crossed bootstrap、exposure、program、unresolved）。
4. **核心逻辑矛盾。**
   - 标题是 "Acting on the Future 4D Scene"，但 `\QthreeCase=3` 下部署时动作不读取世界。
   - 图 4a 用动作不读取的世界头误差去"预测失败"。
   - 表 S16 的"替换学到的预测"在 R1 下无从替换。
   - "learned world beats extrapolation" 比较的是两种不同的耦合方式。
5. **基准来源不清。** Dynamic-14 自称是贡献，正文却反复出现 "native/original evaluators"。
6. **细节不足。**
   - 实机部分缺少相机、传送带等设备型号，缺少物体清单、示教数和失败案例。
   - 实验规模（约 50 个变体、三种子、1,400 个留出场景，约 1,800 次实机试验）显得难以置信。
7. **理论包装过度。** "exact decomposition / falsifiable predictions" 实质是恒等式加三角不等式；$\ell^\star$、$\sigma^\star$ 是经典结论，没有引用。
8. **公平性。**
   - 依赖 CAD 先验与 RGB-D，而多数基线只用 RGB；无 CAD 的开放世界结果没有进主表。
   - 腕部相机的使用差异没有说明。
9. **小错误。**
   - "a lead-conditioned commands"（语法）；
   - "MAE encodes the RGB-D frame"（MAE 只编码 RGB）；
   - "eight frames of RGB, flow" 与光流只用 4 个间隔不符；
   - "G.5 Supplementary" 标题被截断。

审稿代理也认可了以下几点：问题重要；实时协议合理；数学推导正确；对参考池论文（如 PointWorld）的引用准确。

**本轮修改（第 1 轮 → 第 2 轮）。**

| 问题 | 改法 |
|---|---|
| 标题 | 改为 "Learning to Act on the Future 4D Scene"，三种耦合情况下都成立 |
| 摘要与引言 | 按"问题—方法—结果—真机设置"重写，恢复第一人称 |
| 分解的定位 | 改称误差预算（error budget），并说明它是初等的；$\ell^\star$、$\sigma^\star$ 引用经典跟踪文献 |
| 图 4a | 改为所有方法的成功率对"未补偿位移/容差"作图，不再使用世界头误差 |
| 外推对照 | 明确是"以外推结果作输入"与"以学到的未来作监督"两种做法之比较，并补一行"同样的辅助监督 + 外推输入" |
| 草稿痕迹与"预注册"条件句 | 全部删除或改写为陈述 |
| 文体与术语 | 降低分号，删去对照句、格言、Takeaway 与重复句，替换临床试验术语 |
| Dynamic-14 | 说明基准由我们构建，去掉 native/original 措辞，补任务示例图 |
| 实机 | 实机矩阵缩小并写明设备与物体 |
| 主表 | 加入开放世界位姿一行 |
| 正文 | 补一段实现细节 |
| 附录 | 精简附录表格 |

## 第 2 轮（2026-10-21）

分配：A=Motus，B=GEM-4D，C=DAPL，D=本稿，E=Cosmos Policy。完整报告：云端工作区 `scratchpad/review_r2/report.md`。

**结论：没有通过。** 本稿被认出（置信度约 85%，第 1 轮为 90%），按面值质量评分 6/10（第 1 轮 5/10）。文体指标已与真实论文相当，审稿代理改用以下理由：

1. **时间线。** 引用 2026 年 10 月的 arXiv 论文；8–9 月的 DynamicWAM、OpenWAM-α 被当作完成复现、调参、三种子、真机微调的主基线；6–10 月文献多，且有两篇同名 "OpenWAM"。
2. **过于一致。** 约 2.7 万词零笔误，数字逐位自洽（审稿代理明确表示不建议靠加错字来躲检测，我们也不这么做）。
3. **用词回避。** e.g.、i.e.、破折号、significant、state-of-the-art 全为 0。
4. **每条预测都被证实，"负结果"其实支持本文设计。**
5. **审计式防御写作**（"测试前固定""种子 3、4 后再决定"等）。
6. **工作量与配置不合常理**：8 个基线各自复现/调参/三种子、约 60 个变体 × 三种子、四套定制真机装置；4 层小模型用 8 卡、batch 16。

**本轮修改（第 2 轮 → 第 3 轮），主线不变：**

| 问题 | 改法（依据） |
|---|---|
| 时间线 | 删去 Long-WAM、同名 OpenWAM（组合框架）、DC-WAM、DELE、FlowWAM、AffordTrajDP 等外围新文献；保留与"物理时间"高度相关的 Chronos（标注 concurrent） |
| 基线规模 | 按 Research BASE1：每个基线用官方配方训练一次（seed 0），不再写调参预算与复现对照；DreamVLA 的 40/20 轮两种调度取开发集较好者 |
| 设计研究规模 | 按 HISTORY1/FUTURE0（单种子筛选）与 SCALE0、BACKBONE0、Q3-INFO0（三种子）：筛选单种子，表 3、编码器与耦合比较三种子；bootstrap 改为 1 万次 |
| 真实的不完美结果 | 写入 Research 开发集事实（数值均为 `\fillin`）：同配置三种子相差最多 7.4 点（主要来自 t3_phase 的 0–71%）；MAE 三种子 63.7–71.1%；目标点轨迹总体略高于 SE(3)（+1.7）、稠密 2D 位移 −3.6；R3 均值最高但全部来自 t3_phase，两方向效应随种子变号；R1−R0 平均 +3.1、逐种子 −1.3 到 +9.6；B64 快 2.5 倍但一个种子掉 3.6 点 |
| 预测与负结果 | 预测检验改为中性措辞（"对比预测值 1"）；新增"未解决的任务"（t2_se3 所有方法失败；t3_full 本方法全部失败而 OpenWAM-α 成功）与"预测偏差"两段；LIBERO 改为"落后 π0.5" |
| 公平性 | 表 2 新增"暂停物理"列，正文说明暂停时 DreamVLA 领先（Research BASE1 开发集：DreamVLA 约 80%，本方法约 64–67%）；脚本拦截器升级为卡尔曼滤波拦截器 |
| 真机 | 按 Research RR0 改为单一传送带抓取：Franka + D435，盒/细罐/带柄杯三物体 × 0.04/0.08/0.12 m/s × 20 次 = 每方法 180 次，三组共享试验键、每组一个微调种子；方法为 π0.5、无 DROID 基座、本方法 |
| 防御写作 | 删去"测试前计算/固定""种子 3、4 后再决定""约束了选择效应""身份拷贝验证"等；删去附录开头的对应表 |
| 表格 | 删去历史编码定义表与耦合定义表（内容并入正文）；任务-误差项表并入角色表；按任务结果表去掉旋转表头 |
| 文风 | 自然地使用 e.g.、i.e.、破折号与统计意义上的 significantly；引言发现压缩为三条，结论扩为一段 |
| 训练配置 | 附录 C.6 解释 batch 16 与 8 卡（BATCH0） |

**需要作者特别注意（结果可能与稿件写法相反）：** Research 开发集（同步协议、仿真真值位姿）上 DreamVLA 约 80%，SE(3)-WAM 约 64–67%。稿件"实时协议下本方法领先"的主结论依赖实时协议对慢模型的惩罚，尚未实测；"等延迟"对照下 DreamVLA 很可能仍领先，届时需把结论改为"优势主要来自速度与生效时刻对齐"。

## Round 4 (2026-10-21)

Assignment: A=GEM-4D, B=ours, C=Motus, D=Cosmos Policy, E=DAPL. Ours identified at ~65% (same as round 3); quality 6/10 (decoys 4, 6, 7, 6).

| Reviewer finding | Change |
|---|---|
| Exact parameter/update counts read as generated consistency | Method: "about 40k updates"; D: "both at about 47.3M parameters" |
| Reviewer-preempting appendix (Close calls, Where the predictions were off, What remains hard, identity copy) | "Close calls" headings removed; G.3 intro sentence removed; last two paragraphs merged into "Other failures"; identity-copy sentence removed, table rows renamed "none" |
| Verbatim repetition of the Q3 claim and of "extends the finding of [fastwam]" | Intro sentence reworded; experiments repetition removed |
| Contribution 1 is "a triangle inequality" | Bullet now "a simple error budget … that motivates the design and makes predictions we can check, including where they fail" |
| 0.14 m/s example inconsistent with t1 belt 0.04–0.10 m/s | Example unified to 0.10 m/s (15 mm in intro, 20 mm in App. A, 5 mm in Table 1) |
| Cluster of 2607–2610 preprints framing the work | DynaWM/PhysMani/DynamicManip folded into one sentence; ForeTime dropped; PhysMani removed from intro |
| Privileged simulator mesh on LIBERO/DOMINO | Stated as privileged; detector-pose row pointed to |
| Fig. 1 "drawn from the world head used in training" | "predicted only during training" |
| Workload / baseline set | Not changed (experimental plan; user decision) |

## Round 5 (2026-10-21)

Assignment: A=Cosmos Policy, B=DAPL, C=Motus, D=GEM-4D, E=ours. Ours identified at ~70%; quality 6/10 (decoys 7, 6, 6, 5).
Note: the reviewer recognized Cosmos Policy and Motus from prior knowledge, so ours was "the only CVPR-template paper that matches no known work". This structural signal cannot be removed by editing.

| Reviewer finding | Change |
|---|---|
| Title "Act on the Future 4D Scene" contradicts action-only deployment (case 3) | Title and Fig. 1 caption title switched by `\QthreeCase`; case 3: "Learning Dynamic Manipulation from Forecasts at Action Time" |
| DreamVLA called a "video model" | "its larger model and richer forecasts"; intro "a larger model" |
| Bootstrap that resamples three seeds; tied/significant/inconclusive rules | Seed means; scene bootstrap with seeds averaged per scene; only the ±2 tie rule kept |
| Detector-pose pretraining vs tracker fine-tuning not discussed | E.6 states the shift and that it was not measured separately |
| Contribution 1 rhetoric | "whose predictions we test" |
| Workload, weeks-old baselines | Not changed (experimental plan) |

## Round 6 (2026-10-21) and stopping point

Assignment: A=Motus, B=GEM-4D, C=ours, D=DAPL, E=Cosmos Policy. Ours identified at ~78%; quality 6/10 (decoys 6, 4.5, 5.5, 7.5).
Detection over rounds: 90% → 85% → 65–70% → 65% → 70% → 78%. Quality at face value has stayed at 6, level with the real papers (4–7.5).
Remaining reasons are no longer wording problems:
1. Experimental scope and baselines released weeks before the deadline (plan-level; author decision).
2. 2026 preprint cluster in the bibliography and uniformly clean BibTeX/text (fixing would mean adding errors on purpose; not done).
3. Decoys Cosmos Policy and Motus are recognized from reviewer prior knowledge.
4. 8 RTX PRO 6000 for a 4-layer model at global batch 16 (true configuration; explain the reason or change it).
Further GAN-style rounds were stopped to avoid drifting the main line; backup of the pre-round version is unchanged.
