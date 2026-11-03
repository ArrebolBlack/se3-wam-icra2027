SE(3)-WAM Fig. 2 — current paper architecture

The paper includes fig2_se3wam.pdf at text width (174.625 x 80.3275 mm).
fig2_se3wam.svg contains editable text and vector groups; build_fig2.py is the
reproducible scene source. fig2_se3wam.png is the 300 dpi preview. These four
files were imported without graphical changes from the accepted figure on
2026-10-25. English and Chinese captions are owned by figure.tex and figure_zh.tex.

Model sources
- ../../sections/method.tex and ../../paper_config.tex in this repository.
- https://github.com/ArrebolBlack/SE3-WAM/blob/master/configs/experiments/p5_dense_dream20.yaml
- https://github.com/ArrebolBlack/SE3-WAM/blob/master/src/se3_wam/models/se3wam_v2/model.py
- https://github.com/ArrebolBlack/SE3-WAM/blob/master/src/se3_wam/models/se3wam_v2/heads.py
- https://github.com/ArrebolBlack/SE3-WAM/blob/master/src/se3_wam/models/se3wam_v2/trunk.py

The diagram represents the current split-FFN, shared-attention backbone, current
RGB-D input, kinematic target history, and training-only geometric readouts.
Patch states supervise sparse motion across the target, robot and surroundings;
the mean summary supervises the separate target SE(3) forecast. Actions read
summary keys/values, not decoded geometric predictions. All scene, object and
trajectory drawings are original schematics, not measured model outputs.

Style references: Seer (ICLR 2025), VideoVLA (NeurIPS 2025), pi0 (RSS 2025),
SpatialVLA (RSS 2025), RDT-1B (ICLR 2025), and the GR-1 author-page encoder/decoder
diagram (ICLR 2024). No third-party artwork is embedded in this figure.

Rebuild from the repository root (Python + reportlab; Arial regular/bold):
  python figures/Fig2/build_fig2.py
  pdftoppm -png -r 300 -singlefile figures/Fig2/fig2_se3wam.pdf figures/Fig2/fig2_se3wam
The script locates Windows Arial through WINDIR; on another platform, set
FONT_DIR to an installed Arial directory before rebuilding. Direct edits in an
SVG editor do not update the Python scene or the PDF automatically.
