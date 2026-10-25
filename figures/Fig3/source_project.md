# Fig. 3 制作与复现

正文 PDF、可编辑 SVG 和 600 dpi PNG 直接复制自独立验收后的图，未二次裁切或缩放。
原生形状、文字、轨迹和坐标轴都保留为矢量对象；PDF 无嵌入位图。
图幅为 3.25 × 2.30 in，字号为 7–9 pt，配色来自论文 `preamble.tex`。
当前图注由本目录 `figure.tex` 与 `figure_zh.tex` 维护。

## 复现

在 Windows 的独立 Python 环境安装本图依赖后执行：

```powershell
python -m pip install -r figures/Fig3/requirements.txt
python figures/Fig3/generate_fig3.py
```

生成器使用 `C:/Windows/Fonts` 中的 Arial 和 Cambria，生成 SVG、PDF、PNG，
并输出数字校样和导出检查记录。图中文字保持可编辑，PDF 嵌入字体。
本图依赖独立于论文根目录的历史绘图环境；通常编译论文直接读取已导出的 PDF。

## 科学含义与验收

位姿、轨迹和延迟均是假设性示意，不是实验结果。Issue / Apply 共用物理时间网格：
指令槽从采集时刻索引，推理延迟期间的前缀过期；保留指令再经任务固有延迟后作用于机器人。
示例取两个周期的推理延迟和一个周期的任务延迟。稀疏流覆盖全场景，目标另外接受精细 SE(3) 监督。

完整独立制作与验收工程保留在本机 `C:/workspace/se3-wam-fig3-output/`：

- `visual_review.md`：参考来源、十轮历史迭代与独立验收；第 10 轮对应当前任务延迟版本。
- `review/round_10/`：随机编号完整参考图、候选图和印刷尺寸校样；该轮使用新的无历史评审者。
- `references/`：三篇论文的原始 PDF 和完整图像裁切。

本轮视觉对照和科学内容检查通过；小型末端轮廓、淡时间网格及过期斜线仍需细看。
数字校样经过实际查看，未做实体打印。此验收不证明论文发表或保证录用。

参考图为 [Target-Referenced Reactive Grasping（CVPR 2023）](https://openaccess.thecvf.com/content/CVPR2023/papers/Liu_Target-Referenced_Reactive_Grasping_for_Dynamic_Objects_CVPR_2023_paper.pdf)、
[Diffusion Policy（RSS 2023）](https://roboticsproceedings.org/rss19/p026.pdf) 和
[Reactive Diffusion Policy（RSS 2025）](https://www.roboticsproceedings.org/rss21/p052.pdf)。
参考图仅用于视觉对照，其图像内容未并入本图。
