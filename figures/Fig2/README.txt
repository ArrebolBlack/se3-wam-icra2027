SE(3)-WAM Fig.2 — simulation + editable vector revision, 2026-10-29

Deliverables
  fig2_se3wam.svg       editable text, tokens, projected axes, flow arrows, mask
  fig2_se3wam.pdf       paper export, 6.875 x 2.475 in
  fig2_se3wam.png       300 dpi preview
  build_fig2.py        common SVG/PDF scene source
  export_labels.py     CPU export from the original HDF5 + Fig.4 Blender render
  verify_labels.py     independent comparisons to recorded native labels
  assets/INDEX.md      data, provenance, and validation route
  figure.tex / figure_zh.tex   English/Chinese captions

Data and scientific scope
  Dynamic-14 t1_belt, test_id scene 000000, seed 2, native-oracle episode.
  Same episode and current Blender RGB as Fig.4: tick 38, capture 1.90 s.
  History: 1.55..1.90 s. Future poses/flow: 1.95..2.30 s, 50 ms spacing.
  Target contact occurs later, at 2.462 s; no contact event is invented here.
  sources.json records this capture as tau_t for reuse in Fig.1/Fig.3.
  issue and first execution tau_a depend on actual policy latency and are not
  assigned synthetic timestamps in this diagram. EEF illustration: recorded
  states at capture + 0..350 ms, not a decoded policy action or an action forecast.

  Native metric depth, K, world_from_camera_cv, geom IDs and geom transforms
  reconstruct persistent material points; cumulative 3D displacement is expressed
  in the robot base frame. The exact adapter grid rule selects 196 real pixels.
  All 196x8 labels and visibility flags are retained. The flow panel is a workspace
  crop, showing 8 of the 19 moving sources at 400 ms; the complete grid includes
  177 sources with motion <=1 mm. Gray dots denote these near-zero samples.
  Cloud points are back-projected from measured depth, colored from the matching
  clean Blender render, and reprojected in the original calibrated camera.
  Raster cloud sampling is denser than the supervised 14x14 flow grid.
  One target patch point exists at this capture. The separate eight SE(3) labels
  remain exact, so their contrast with the sparse scene grid is data-driven.

  Orange and blue axes have true recorded origins/orientations. Axis glyph length
  is a display choice, not an error tolerance. Future crops are enlarged without
  magnifying motion. All annotations remain vector objects. No AI-created scene,
  model prediction, RGB forecast, invented path, or synthetic data is embedded.
  Only the two geometric heads are expanded; appearance auxiliaries are omitted.

Verified on the project-funded single-card development instance
  dv-c2ad9fd63a; hostname and execution platform in assets/sources.json.
  Persistent source/output: /public_fast_storage/se3wam/yjq/figures/fig2-20261029/
  Export and verify were actually run there, and the output was copied back.
  assets/validation.json: native adjacent-flow projection difference 1.172e-7 px;
  native visibility equal; static flow max 7.692e-16 m; EEF frame roundtrip 0;
  target-flow vs pose difference 1.682e-9 m.

Rebuild with Python + numpy/scipy/h5py/Pillow/reportlab and Arial regular/bold:
  python figures/Fig2/build_fig2.py
  pdftoppm -png -r 300 -singlefile figures/Fig2/fig2_se3wam.pdf figures/Fig2/fig2_se3wam
  FIGURE_FONT_DIR selects another installed Arial directory on non-Windows hosts.

Re-export on the development machine:
  ROOT=/public_fast_storage/se3wam/yjq/figures/fig2-20261029
  python "$ROOT/input/export_labels.py" --episode "$ROOT/input/v1%3Atest_id%3At1_belt%3A000000~r000000.hdf5" --beauty "$ROOT/input/beauty_clean.png" --output "$ROOT/output"
  python "$ROOT/input/verify_labels.py" --episode "$ROOT/input/v1%3Atest_id%3At1_belt%3A000000~r000000.hdf5" --assets "$ROOT/output"

Original local Fig.4 project (recording is not duplicated in Git):
  C:/Users/XUE/.codex/visualizations/2026/10/25/01a172e5-a1e5-7ba3-90bd-3b76c482a936/fig4-dynamic14/
  recordings/t1_belt/recording/episodes/*.hdf5
  blender/panels/t1_belt/beauty_clean.png and scene.blend
  Original simulator-renderer geometry cache can lag one 2 ms physics step;
  labels deliberately use the native HDF5 geometry that owns their semantics.
  Blender RGB uses the exact recorded current state, as in the accepted Fig.4.

Architecture sources
  ../../paper_config.tex, ../../sections/method.tex
  C:/workspace/SE3-WAM-canonical/src/se3_wam/models/se3wam_v2/heads.py
  C:/workspace/SE3-WAM-canonical/src/se3_wam/data/dynamic_benchmark.py
  Paper configuration: 24 layers; S=196+8+8; M=16; A=8; Euler=5.
  Mask Q rows / K columns: S->S, M->S/M, A->M/A. World never reads actions.

Design references (viewed as independent full-resolution figures)
  DreamVLA Fig.2: single wide backbone, top training-only readouts, right actions.
  VGGT Fig.2: consistent token colors and aligned groups.
  PointWorld Fig.2: measured RGB-D cloud as a geometric output illustration.
  Local atlas: architecture-reference-atlas-20261029 under the 2026/10/24
  visualization project 01a16f6a-9765-7240-b284-677c3817213c, figures 07/13/16.
  No artwork from those papers is embedded.

Shared visual interface for Fig.1 / Fig.3
  Blue #286E9D: observation/history axes and tokens.
  Orange #D3771E: precise target SE(3) supervision.
  Pale orange #E6B87C: sparse scene-flow arrows. Gray #8C989F: near-zero flow.
  Purple #8157A8: actions and gripper. Neutral summary M: #E7EAED.
  Time symbols: capture tau_t -> issue -> first execution tau_a -> contact.
  Reuse labels.npz + sources.json, never infer future labels from an RGB crop.

Real-robot replacement
  Keep the layout, colors and token contracts. Replace the calibrated RGB-D,
  history and measured trajectory bundle together. A photograph alone supplies
  no metric flow or SE(3) GT; Fig.6 photographs are not relabeled as such.
