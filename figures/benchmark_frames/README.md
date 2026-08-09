# DB0 benchmark figure frames

These images are frozen environment-review frames used only to illustrate the
task geometry in `benchmark_suite.svg`. They are not learned-policy rollouts and
must not be cited as empirical SE(3)-WAM results.

The canonical DB0 environment revision is
`5564f479e77b4cda90116f8cdae6ace85989038e`. The final T-shaped-object frames
come from the visually identical `99b4739` review capture; the later canonical
revision contains test-only changes. The P0 frame is an environment anchor from
the final owner-review handoff, not the current formal P0 dataset showcase.

| File | Source review artifact | RGB crop in source |
|---|---|---|
| `p0.png` | `p0-handoff/final-owner-review-9d98321/p0__key_00__event-target_enters_observation_region.png` | `(0, 88, 224, 224)` |
| `t1_belt.png` | `dbd1/v2_157277f_gallery/t1_belt.png` | `(0, 72, 224, 224)` |
| `t1_so3.png` | `dbd1/tshape_fix_99b4739_review/t1_so3__key_00__event-target_enters_observation_region.png` | `(0, 88, 224, 224)` |
| `t1_occ.png` | `dbd1/v2_157277f_gallery/t1_occ.png` | `(0, 72, 224, 224)` |
| `t2_se3.png` | `dbd1/tshape_fix_99b4739_review/t2_se3__key_02__event-containment_entry.png` | `(0, 88, 224, 224)` |
| `t3_phase.png` | `dbd1/v2_157277f_gallery/t3_phase.png` | `(0, 72, 224, 224)` |
| `t4_can.png` | `dbd1/v2_157277f_gallery/t4_can.png` | `(0, 72, 224, 224)` |
| `t5_replan.png` | `dbd1/tshape_fix_99b4739_review/t5_replan__key_03__event-striker_impact_end__event-postevent_state_validated__t5_impact_end_observe.png` | `(0, 88, 224, 224)` |

The SVG intentionally uses T4-Can as the representative free-physics image;
the historical `t4_sphere` cell remains in Active-Full-13-v0.3 for compatibility
but is not used as the hero view.
