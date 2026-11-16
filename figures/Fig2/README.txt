FoveaWAM architecture, v27

This directory contains the adopted architecture figure. LaTeX assigns the
figure number and includes fig2_se3wam.pdf at text width, 174.625 x 103.684 mm.

v27 updates the recorded illustrations and native vector overlays in the v26
PowerPoint layout. RGB and the flow context use the shared specular 0.10 and
roughness 0.34 defaults, with original material colors and the saved cameras.
Flow follows the recorded 50 ms tracks using turbo 0.12–0.66, a dark 0.82-opacity
edge, arrowheads and white origins. The three readouts end at +50, +200, +400 ms.
Target meshes retain their original orange, face shading and temporal fading,
matching the scene illustrations. SE(3) annotations use core red #C0263A;
origins are white with red rims.
Pose axes retain #D62728 / #2CA02C / #1F77B4 with white support for contrast.
The existing history path remains gray; the future path remains red and dashed,
with white support and 50 ms ticks. The architecture, existing text and geometry
are unchanged. A small time-arrow legend is added inside the flow readout.

Editable files
- fig2_se3wam.pptx is the editable master, based on the author's v24 revision.
- build_fig2.py exports the master using PowerPoint and PyMuPDF.
- render_assets.py updates the saved Blender context and the RGB asset.
- update_assets.py updates only the illustration groups and their styles in the
  native PowerPoint, using geometry_labels.npz; it preserves the adopted layout.
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
Both LN labels are centered in their world-stream normalization blocks.

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
RGB is the validated specular-0.10 agentview frame 29 from figures/paradigms;
Depth is original
recorded depth. They illustrate modalities and are not a pixel-registered pair.
The flow context is a Blender rendering of the same recorded current state.
Flow starts and the 3x display scale are preserved. The third readout now ends at
+400 ms (previously +350 ms); intermediate points follow the recorded trajectory.
Context clipping affects presentation only. The old figure-specific robot
darkening and roughness 0.60 have been replaced by the shared studio defaults.
The target history and future supervision use the same T-shaped target mesh
and share the current pose at 0 ms. The two panels use the same orthographic
view and fit trajectory translation to their own widths. Red, green and blue
arrows show positive local X, Y and Z. The future trajectory and sparse flow
show supervision from the recorded rollout. Robot icons and pose-glyph sizes
are schematic. Sources are in assets/source.json and assets/blender/source.json.

Export from the repository root
  # Blender environment (Research):
  <research>/.envs/blender-paper/mujoco-blender-render/Scripts/python.exe <paper>/figures/Fig2/render_assets.py --research-root <research>
  # Paper environment:
  .venv/Scripts/python.exe figures/Fig2/update_assets.py
  .venv/Scripts/python.exe figures/Fig2/build_fig2.py
This entry point requires Microsoft PowerPoint on Windows and PyMuPDF in the
Python environment. Save edits to fig2_se3wam.pptx before running the export.

The author-supplied v24 deck and its paper asset are in archive/author_v24_20261107/.
The six assets before palette unification are in archive/pre_palette_v25_20261116/.
The v26 source and illustrations remain available in Git history.
