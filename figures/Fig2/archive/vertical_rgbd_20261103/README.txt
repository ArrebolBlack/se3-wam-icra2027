FoveaWAM Fig. 2 — accepted vertical layout (2026-11-03)

This directory is the editable base for subsequent Fig.2 refinements.
The paper includes fig2_se3wam.pdf at text width: 174.625 x 93.989 mm.
English and Chinese captions are figure.tex and figure_zh.tex; both include
this one PDF and retain the fig:architecture label.

Current source and assets
- build_fig2.py is the canonical scene source. Edit it, then regenerate.
- fig2_se3wam.svg has editable Arial text, vector shapes and point clouds.
- fig2_se3wam.png is the 300 dpi preview; fig2_paper_width.png is a 96 dpi proof.
- assets/INDEX.md routes to the observed RGB-D, geometry data and source record.
- archive/schematic_overview/ retains the replaced all-schematic formal figure.

The accepted model illustration is the C equalaux01 baseline: 12 layers,
shared QKV/output projections, separate world/action FFNs, and attention
S -> S; M -> S,M; A -> S,M,A. World states never read noisy actions.
Patch states supervise sparse 3D displacement/visibility and the depth,
DINO and dynamic-RGB auxiliaries. Mean M supervises target SE(3) and
current target RGB reconstruction. Forecasts are not decoded Action inputs.
Inference caches world K,V once per query for five Action Euler steps.
Model facts belong to Research P5-DAY1/P5-DAY1.md and its c_equalaux01 recipe.

RGB-D and geometric examples are recorded data from one native OnTimeBench query.
The three examples show 50, 200 and 350 ms of the eight 50-400 ms horizons.
The point clouds show current visible workspace, with true future flow arrows
magnified 3x. Pose translations/rotations are true labels; pose-glyph size and
action icons are schematic. No model prediction or success result is claimed.
assets/source.json records the precise source and display conditions.

Rebuild from the repository root with the existing paper environment:
  .venv/Scripts/python.exe figures/Fig2/build_fig2.py
Dependencies: NumPy, reportlab, Pillow and pypdfium2, already declared in
requirements.txt. Windows Arial is located via WINDIR/Fonts.

Accepted candidate source:
C:/Users/XUE/.codex/visualizations/2026/11/03/01a1a2a4-887f-7893-a5c7-767497a53407
The adopted layout places real inputs below the shared backbone, geometric
readouts/actions above, and the mask plus cached inference on the right.
