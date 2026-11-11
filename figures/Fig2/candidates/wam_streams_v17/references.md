# 主干参考与取舍

2026-11-05 重看[专项原图合集](C:/Users/XUE/.codex/visualizations/2026/11/03/01a1a260-b262-7993-8ec3-51be2f1ecdc9/INDEX.md)，并核对近期论文原文与原图。下表是构图阅读，不是性能或论文质量排名。

| 论文与原图 | 实际画法 | 本候选借用的部分 |
|---|---|---|
| [AW-0, Fig.2, 2026-10-21](https://arxiv.org/html/2610.30136v1) | 三个宽大的专家区域并排，一条共享注意力带贯穿；总览不反复展开每层残差。 | 用区域说明角色分工，共享注意力成为贯穿两区的视觉主体。 |
| [OpenWAM（Stanford）, Fig.2, 2026-10-06](https://arxiv.org/html/2610.07922v1) | 两条完整专家分支由 joint attention 联结；×L Blocks 标记层重复，后方平面与斜向时间轴表示 History Context。 | 借用成组的完整分支与 ×L 标记。原图的后方平面具有历史语义；本候选沿用原稿的轮廓堆叠，以 ×L 明确其层深含义。 |
| [LAW, Fig.5, v2 2026-10-25](https://arxiv.org/html/2610.23334v2) | Video/Action 两个底色区域，共享 Joint Attention 横跨两支；旁边单独展开其 MoTE 路由。 | 以两区为骨架、共享算子贯穿；图中不引入 LAW 的路由或额外专家。 |
| [GigaWorld-Policy-0.5, Fig.2, v3](https://arxiv.org/html/2607.13960v3) | 将 MoT Causal DiT Blocks 作为大的主干容器，内部用两组专家模块条；训练/推理另列，缓存属于推理视图。 | 主干作为一个整体；保留既定 b/c，不把缓存和 mask 塞进主干。 |
| [Fast-WAM, Fig.2, v2](https://arxiv.org/html/2603.16666v2) | Video DiT/Action DiT 直接作为主体，训练与推理 mask 另列。 | 总览与可见性说明分开，保持短标签和角色身份贯穿。 |

同时查看了专项合集的 InternW0-Δ Fig.3、OpenWAM-α Fig.2 与 StreamingWAM（Oct）Fig.2，分别对照单层、架构选项和主干与推理视图的主次。另核对了 [CausalWAM（2026-10-30）](https://arxiv.org/html/2610.42096v1)：其新意在输出侧的稀疏路由，本轮不借用该模块。

这些工作中的“专家”不等于我们的 S/M/A 三类状态。AW-0 和 Stanford OpenWAM 的模态分支拥有各自的投影参数；我们当前实现共享 QKV/输出投影，S/M 共用 World FFN，A 使用独立 Action FFN，mask 为 S→S、M→{S,M}、A→{S,M,A}。因此采用两个区域、一条共享注意力、三行状态，不画成三个独立 Transformer，也不添加预训练来源、参数规模或路由器。

v16 的问题是重复了三套可见算子，但整体主干的层级被细线和重复残差削弱。本候选只完整展开一个层面，以共同的 World 区域和独立的 Action 区域建立主体，背后轮廓与 ×L 表达深度。模型规模、预训练和泛化能力应由实际配置与证据支持；图中只表达已有结构。
