# Fig. 6 排版导出

- DROID 式通栏横排，6.875 × 0.958 in，正文引用。[PDF](polished/fig6.pdf) · [可编辑 SVG](polished/fig6.svg) · [600 dpi PNG](polished/fig6.png)
- DemoGen 式单栏两列三行，3.281 × 2.809 in。[PDF](single-column/fig6.pdf) · [可编辑 SVG](single-column/fig6.svg) · [600 dpi PNG](single-column/fig6.png)

横排在现有照片内做横向裁切，单栏沿用完整 16:9 裁剪。网球演示帧在两版中的有效分辨率分别约为 469 ppi 和 414 ppi。

从论文仓库根目录运行 [排版脚本](../build_figure.py)，依赖 Pillow、reportlab、PyMuPDF 和 Windows Arial 字体。

```powershell
python figures/Fig6/build_figure.py
python figures/Fig6/build_figure.py --layout single-column
```
