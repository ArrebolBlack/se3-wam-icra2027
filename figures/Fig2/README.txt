FoveaWAM architecture, v25

This directory contains the adopted architecture figure. LaTeX assigns the
figure number and includes fig2_se3wam.pdf at text width, 174.625 x 103.684 mm.

Editable files
- fig2_se3wam.pptx is the editable master, based on the author's v24 revision.
- build_fig2.py exports the master using PowerPoint and PyMuPDF.
- fig2_se3wam.svg and fig2_se3wam.pptx contain editable text, shapes, arrows,
  tokens, geometric glyphs, noise and original robot-arm icons.
- Five small images are placed: RGB, Depth and three instances of one Blender
  context rendering. The full figure is never flattened into a picture.
- The PPTX retains native object groups. Select inside a group or ungroup it.
  It has been opened and rendered in Microsoft PowerPoint.
- fig2_se3wam.pdf is the paper asset; the 300 dpi and 600 dpi PNGs are previews.
  fig2_paper_width.png is the 144 dpi proof at the physical paper width.
- assets/INDEX.md routes to inputs, recorded supervision and the editable
  Blender scene. assets/blender/flow_context.blend packs the required assets.
- export_report.json records the physical dimensions, vector paths, images,
  and SVG text elements in the exports.

Layout
Dashed outlines group the input illustrations with their encoders and the
output examples with their decoders. A dashed leader links Summary M to its
token. The right-side readouts use larger illustrations. The a/b/c titles
sit below their panels, and the attention mask has a dashed outer frame.

Model relationships
RGB-D, Target history and Robot state form S. Learned summaries form M;
noisy actions form A. Vision/SE(3)/State/Action encoders denote existing input
mappings. Summary M has no additional encoder. Token counts are schematic.
Each layer shares Q/K/V, masked attention and its output projection.
S/M use the same World FFN; A uses Action FFN and AdaLN conditioned on scalar
flow time u. Both residual updates and layer-wise state updates are retained.
The external mask is S -> S; M -> S,M; A -> S,M,A.
Flow/SE(3)/Action decoders denote existing final-state readout projections.
Decoded geometry never becomes an Action input. Geometry readouts are
training-only (dashed); deployment prefills S/M once and reuses fixed
layer-wise attention-input K/V during Action updates.

Image and supervision scope
RGB is the accepted Blender frame-29 illustration; Depth is original
recorded depth. They illustrate modalities and are not a pixel-registered pair.
The flow context is a Blender rendering of the same recorded current state.
All displayed flow starts, endpoints and the 3x display scale are preserved.
Context clipping and robot material adjustments affect presentation only.
The target history and future supervision use the same T-shaped target mesh
and share the current pose at 0 ms. The two panels use the same orthographic
view and fit trajectory translation to their own widths. Red, green and blue
arrows show positive local X, Y and Z. The future trajectory and sparse flow
show supervision from the recorded rollout. Robot icons and pose-glyph sizes
are schematic. Sources are in assets/source.json and assets/blender/source.json.

Export from the repository root
  .venv/Scripts/python.exe figures/Fig2/build_fig2.py
This entry point requires Microsoft PowerPoint on Windows and PyMuPDF in the
Python environment. Save edits to fig2_se3wam.pptx before running the export.

The author-supplied v24 deck and its paper asset are in archive/author_v24_20261107/.
