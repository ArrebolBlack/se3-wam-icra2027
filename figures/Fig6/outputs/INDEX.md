# Fig. 6 排版导出

- 单栏两列三行，3.281 × 2.809 in，正文使用，标注接触前的运动方向示例与运动类型。[PDF](single-column/fig6.pdf) · [可编辑 SVG](single-column/fig6.svg) · [可编辑 PPTX](single-column/Fig6-editable.pptx) · [600 dpi PNG](single-column/fig6.png)
- 通栏横排，6.875 × 0.958 in，供版面比较。[PDF](polished/fig6.pdf) · [可编辑 SVG](polished/fig6.svg) · [600 dpi PNG](polished/fig6.png)

横排在现有照片内做横向裁切，单栏沿用完整 16:9 裁剪。网球演示帧在两版中的有效分辨率分别约为 469 ppi 和 414 ppi。

从论文仓库根目录运行 [排版脚本](../build_figure.py)，依赖 Pillow、reportlab、PyMuPDF 和 Windows Arial 字体。

```powershell
python figures/Fig6/build_figure.py
python figures/Fig6/build_figure.py --layout single-column
```
