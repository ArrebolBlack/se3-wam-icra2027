# Fig.1 二维性能图参考

[原图总览](reference_overview.png) · [设计取舍与数据核对](design_notes.md) · [来源与裁切坐标](sources.json) · [重新提取](collect_references.py)

以下均为实际下载原文、查看后从 PDF 裁切的原图；页码按 PDF 页序计。不是获奖名单。

| 论文／会议 | 独立原图 | 官方论文入口 |
|---|---|---|
| EfficientNet · ICML 2019 | [Fig.1／p.1](01_efficientnet.png) | [PMLR](https://proceedings.mlr.press/v97/tan19a.html) |
| DeiT · ICML 2021 | [Fig.1／p.1](02_deit.png) | [PMLR](https://proceedings.mlr.press/v139/touvron21a.html) |
| MobileViT · ICLR 2022 | [Fig.2／p.2](03_mobilevit.png) | [OpenReview](https://openreview.net/forum?id=vh-0sUt8HlG)；裁图采用[作者 v2](https://arxiv.org/abs/2110.02178v2)，首页注明 ICLR 2022 |
| EfficientFormer · NeurIPS 2022 | [Fig.1／p.2](04_efficientformer.png) | [会议论文集](https://proceedings.neurips.cc/paper_files/paper/2022/hash/5452ad8ee6ea6e7dc41db1cbd31ba0b8-Abstract-Conference.html) |
| MobileOne · CVPR 2023 | [Fig.1／p.2](05_mobileone.png) | [CVF](https://openaccess.thecvf.com/content/CVPR2023/html/Vasu_MobileOne_An_Improved_One_Millisecond_Mobile_Backbone_CVPR_2023_paper.html) |
| FastViT · ICCV 2023 | [Fig.1／p.2](06_fastvit.png) | [CVF](https://openaccess.thecvf.com/content/ICCV2023/html/Vasu_FastViT_A_Fast_Hybrid_Vision_Transformer_Using_Structural_Reparameterization_ICCV_2023_paper.html) |
| RepViT · CVPR 2024 | [Fig.1／p.1](07_repvit.png) | [CVF](https://openaccess.thecvf.com/content/CVPR2024/html/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.html) |
| FastVLM · CVPR 2025 | [Fig.1／p.1](08_fastvlm.png) | [CVF](https://openaccess.thecvf.com/content/CVPR2025/html/Vasu_FastVLM_Efficient_Vision_Encoding_for_Vision_Language_Models_CVPR_2025_paper.html) |

450 dpi 裁图不改变原图颜色、文字或布局；多面板图保留完整面板。[完整来源 PDF](papers/INDEX.md)仅供本次研究参考。原图及 PDF 权利归原作者和相应权利人，不并入本项目的原创图许可。

本地已有 PDF 时运行 `python collect_references.py`；重新获取原文加 `--download`。OpenReview 直接下载受验证页限制，因此 MobileViT 使用作者公开的 ICLR 成稿。
