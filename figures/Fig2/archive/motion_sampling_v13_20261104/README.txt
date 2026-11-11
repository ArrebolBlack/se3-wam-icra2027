FoveaWAM architecture — continuous target history and compact sampling (2026-11-04)

This directory is the editable architecture-figure base; LaTeX assigns its number.
The paper includes fig2_se3wam.pdf at text width: 174.625 x 103.684 mm.
English and Chinese captions are figure.tex and figure_zh.tex; both include
this one PDF and retain the fig:architecture label.

Current source and assets
- build_fig2.py is the canonical scene source. Edit it, then regenerate.
- fig2_se3wam.svg has editable Arial text, vector shapes and point clouds.
- fig2_se3wam.pptx is a one-slide editable export of that same adopted SVG.
  Text, arrows, tokens, noise squares, robot icons and geometric examples are
  native PowerPoint objects. Only the RGB and depth tiles are embedded images.
  Related objects retain named groups; select inside a group to edit a component,
  or ungroup it. The 1600 x 950 px canvas preserves the figure's aspect ratio.
- build_fig2_pptx.mjs and pptx_scene.py rebuild the PPTX from the existing SVG
  using the bundled Artifact Tool runtime. They do not change the paper PDF.
- fig2_se3wam.png is the 300 dpi preview; fig2_paper_width.png is a 96 dpi proof.
- assets/INDEX.md routes to the RGB/depth illustrations, geometry data and source record.
- assets/backbone_v2.svg and backbone_v2_layout.json retain the accepted compact
  layer. Its native objects are rotated counterclockwise 90 degrees and stream
  positions are reordered to S, M, A from top to bottom. Operators, both residual
  updates and connectivity are retained; glyphs and math subscripts are not mirrored.
- RGB-D, target pose history and robot-state tokens merge into S; learned summaries
  enter M and noisy action tokens enter A. Token counts are schematic.
- Scene branches start at the center token's right edge and join one collector;
  its S arrow and the matching M/A arrows end at their aligned state-band ports.
- Flow readouts are at top, target SE(3) in the middle and actions at bottom.
- The middle scene-input branch is collinear with the S ingress arrow. Token
  glyphs are slightly tighter to retain spacing between target, robot and M.
- Patches, Mean M and the Training only label/bracket are omitted. Dashed
  geometric readout arrows retain their training-only meaning in the caption.
- No outer panel frames are used. Titles, a/b/c labels and whitespace group the
  overview with its lower details.
- The external attention mask uses S/M/A row/column labels and a colored matrix.
- Training branches to world/action heads and their losses. Inference bypasses
  those heads: a fixed world K/V cache conditions a repeated Action update loop;
  a noise square initializes its action state. The loop never reruns world prefill.
- Explanatory gray footnotes are removed; lower-panel module/row labels are black.
- Target history uses scaled SE(3) wireframes in one fixed historical reference,
  projection and scale. Cumulative motion is retained across the three past states.
- Robot state and all action symbols read the original transparent robot_arm.svg
  as native editable vectors; no cropped robot image is used. Panel c uses one
  robot icon to represent the whole chunk, matching the icon and size in a.
- The noise square is centered above Action update and enters its top port;
  cached world conditioning enters from the left. A circular arrow inside the
  block denotes repetition without external feedback wires.
- archive/vertical_rgbd_20261103/ retains the replaced vertical formal figure.

The accepted model illustration is the C equalaux01 baseline: 12 layers,
shared QKV/output projections, separate world/action FFNs, and attention
S -> S; M -> S,M; A -> S,M,A. World states never read noisy actions.
Patch states supervise sparse 3D displacement/visibility and the depth,
DINO and dynamic-RGB auxiliaries. Mean M supervises target SE(3) and
current target RGB reconstruction. Forecasts are not decoded Action inputs.
Inference caches world K,V once per query for five Action Euler steps.
Model facts belong to Research P5-DAY1/P5-DAY1.md and its c_equalaux01 recipe.

RGB is the accepted Blender frame-29 rendering of the same recorded state.
Depth and geometric labels come from the original OnTimeBench recording.
The RGB/depth tiles illustrate modalities, rather than a pixel-registered render pair.
History miniatures use indices 1,4,7 with the same earliest state 0 as the pale
reference. A shared frame and bounds preserve the recorded accumulated motion;
the historical poses are not independently recentered. The arm is an original vector.
The three examples show 50, 200 and 350 ms of the eight 50-400 ms horizons.
The point clouds show current visible workspace, with true future flow arrows
magnified 3x. Pose translations/rotations are true labels; pose-glyph size and
action icons are schematic. No model prediction or success result is claimed.
assets/source.json records the precise source and display conditions.

Rebuild from the repository root with the existing paper environment:
  .venv/Scripts/python.exe figures/Fig2/build_fig2.py
Dependencies: NumPy, reportlab, Pillow, pypdf and pypdfium2, already declared in
requirements.txt. Windows Arial is located via WINDIR/Fonts.

PPTX rebuild from the repository root (replace the uppercase path placeholders;
WORK_DIR is a new private build directory; join these lines into one command):
  RUNTIME_NODE figures/Fig2/build_fig2_pptx.mjs --work-dir WORK_DIR
    --runtime-modules RUNTIME_NODE_MODULES --python RUNTIME_PYTHON
    --skill-dir PRESENTATIONS_SKILL_DIR --output figures/Fig2/fig2_se3wam.pptx
Use the Node.js, Python and module paths supplied by load_workspace_dependencies.
The Python environment needs reportlab. The current file was opened and rendered
in Microsoft PowerPoint, compared with the paper figure, and checked for native
text/shapes and exactly two small embedded modality images.

Accepted refinement source:
C:/Users/XUE/.codex/visualizations/2026/11/04/01a1a532-c313-7110-871b-1bfea8239bc5/fig3_motion_v13
The adopted layout aligns input/token rows at left, the accepted rotated
compact backbone at center, and final-state readouts at right. The external
mask and cached training/inference panels are below. English/Chinese captions
identify the Blender RGB illustration; the manuscript body is unchanged.
