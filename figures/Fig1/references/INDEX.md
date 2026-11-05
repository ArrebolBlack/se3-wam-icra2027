# VLA／WAM 的二维性能图参考

**主参考：TinyVLA Fig.1**，华东师范大学、美的等单位合作，RA-L 2025。以下图片均已查看原始 PDF，再按具体子图裁切。

[五图总览](reference_overview.png) · [TinyVLA 与本图并排](reference_vs_fig1.png) · [设计取舍](design_notes.md) · [来源与裁切数据](sources.json) · [重新提取](collect_references.py) · [完整 PDF](papers/INDEX.md)

| 参考与出处 | 对应二维图 | 横轴／纵轴 |
|---|---|---|
| **[TinyVLA](https://tiny-vla.github.io/) · RA-L 2025** | **[Fig.1／PDF p.1](01_tinyvla.png)** | 推理时延／五项真机任务平均 SR；气泡直径表示参数量 |
| [DeeR-VLA](https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b0e7c7c2a5780aeefe3b79caac106e-Abstract-Conference.html) · NeurIPS 2024 | [Fig.3 上排／p.8](03_deervla.png) · [完整 Fig.3](03_deervla_full.png) | 平均 LLM GFLOPs／CALVIN 平均成功链长 |
| [Faster-WAM](https://arxiv.org/abs/2608.02365v2) · arXiv 作者稿 | [Fig.1(b)／p.2](04_fasterwam.png) · [完整 Fig.1](04_fasterwam_full.png) | 对数推理时延／RoboTwin SR；气泡另编码 action expert 规模 |
| [TurboWAM](https://turbowam.github.io/) · arXiv 作者稿 | [Fig.1(b)／p.1](05_turbowam.png) · [完整 Fig.1](05_turbowam_full.png) | 每个 action chunk 推理时间／LIBERO SR |
| [Fast-WAM](https://arxiv.org/abs/2603.16666v2) · arXiv 作者稿 | [Fig.4 左图／p.9](06_fastwam.png) · [完整 Fig.4](06_fastwam_full.png) | 实际任务平均完成时间／真机 SR；横轴不是模型推理时延 |

页面与图号对应 `sources.json` 指定版本；TinyVLA 用 arXiv v5（首页注明 RA-L 接收），另保留 NeurIPS 正式论文与三篇 WAM 作者稿的不同身份。子图裁切只去掉其他面板和正文，未重绘、改色或修改原图标注，450 dpi 导出。原图及 PDF 权利归原作者和相应权利人。

已有 PDF 时运行 `python collect_references.py`；重新下载指定版本加 `--download`。
