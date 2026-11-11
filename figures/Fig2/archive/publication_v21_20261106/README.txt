FoveaWAM architecture — publication refinement v21 (2026-11-06)

This directory contains the adopted architecture figure. LaTeX assigns the
figure number and includes fig2_se3wam.pdf at text width, 174.625 x 103.684 mm.
Existing English/Chinese figure captions and manuscript text are preserved.

Editable files
- build_fig2.py is the canonical, self-contained vector drawing source.
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
- layout_metadata.json and export_report.json describe generated objects,
  sizes, flow endpoints and export properties.

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
Historical SE(3) glyphs share one scale, projection and earliest-pose reference.
Geometric examples are recorded supervision, not model-prediction evidence.
Robot icons and pose-glyph sizes are schematic. Precise sources and display
parameters are in assets/source.json and assets/blender/source.json.

Rebuild from repository root
  .venv/Scripts/python.exe figures/Fig2/build_fig2.py
Dependencies are NumPy, reportlab, Pillow, pypdf and pypdfium2; Windows Arial
is read from C:/Windows/Fonts. The figure builder does not edit manuscript text.

PPTX rebuild (uppercase placeholders are runtime paths; WORK_DIR is new):
  RUNTIME_NODE figures/Fig2/build_fig2_pptx.mjs --work-dir WORK_DIR
    --runtime-modules RUNTIME_NODE_MODULES --python RUNTIME_PYTHON
    --skill-dir PRESENTATIONS_SKILL_DIR --output OUTPUT_PPTX
Use the paths returned by load_workspace_dependencies and a new output path.

Previous adopted v15 is preserved in archive/bc_cache_v15_20261106/.
Accepted source: C:/Users/XUE/.codex/visualizations/2026/11/04/01a1a532-c313-7110-871b-1bfea8239bc5/fig2_publication_v21
