# C. Target motion during inference: notes (2026-11-16)

**Current direction:** after viewing the numbered history, the user preferred **candidate 1**, the original
`panel_displacement.png`, and requested optimization based on it. The new `target_motion.*` is an English
candidate for review, not a final approval. Only this C directory is changed; main-paper placement and the
Chinese version remain undecided.

**Latest request:** reduce the crowded vertical dashed guides. The current pass keeps five labelled,
representative methods instead of all ten in-axis methods. It continues the requested restrained
Matplotlib/Python appearance and remains a design candidate for review.

## 1. Files and current revision

| File | Content / when to read |
|---|---|
| [make_target_motion.py](make_target_motion.py) | Reproducible source; default generates the current figure. `--variant all` regenerates implemented historical directions. Missing requested fonts fail. |
| [PNG](target_motion.png), [PDF](target_motion.pdf), [SVG](target_motion.svg) | Current refinement of candidate 1, 3.25 × 2.10 in (234 × 151.2 pt), exported directly from Matplotlib with Windows Arial. |
| [Preview source](preview_column.tex), [PDF](preview_column.pdf), [PNG](preview_column.png) | CVPR two-column page with the figure explicitly placed at 3.25 in and the current caption. |
| [candidates/](candidates/) | Historical directions, indexed in §4. |

The refinement preserves the original continuous colored bands, vertical latency guides, rotated method
labels, and direct family labels at the right edge. The title now belongs to the caption. Design decisions:

- Keep five individual p95 guides: ACT, FoveaWAM, π0.5, DynamicVLA, OpenWAM-α. Each has its own label.
  Keep ACT as the fastest reference, and choose one actual method in each of the crowded 60 ms and
  150 ms clusters. The remaining methods appear in Table 1. The caption explicitly identifies a selection.
- Use normal-weight family names and grey method names; reserve bold text for FoveaWAM. Red identifies Impact.
- Remove the repeated plot title. Use the recovered height for the axes and labels rather than a separate header.
- Lighten fills and grey guides, retain crisp range boundaries, and avoid a new legend or decorative background.
  Wide bands are drawn first, narrow bands above them; both speed-range edges remain visible.
- Remove the original `< 2 cm` grey strip, which had no object-size or task-tolerance basis.
  No new physical threshold is added. The Fig. 4(a) circle is omitted in this simpler layout.
- Use Arial at print size: axis/family/FoveaWAM labels 7 pt, other method labels 6.5 pt.

## 2. Encoding and sources

| Element | Definition / source |
|---|---|
| Bands | Continuous $d\,[\mathrm{cm}]=v\,[\mathrm{m/s}]\,L\,[\mathrm{ms}]/10$. Linear speed ranges from `tables/task_definitions.tex`: Grasp 0.03–0.20, Place 0.03–0.06, Capture 0.55–1.14, Impact 0.12–0.14 m/s. Upper/lower edges show maximum/minimum speed. |
| Method guides | Individual p95 time-to-action from `results/realtime_c/table1-20261104.json`. Five selected guides: ACT, FoveaWAM, π0.5, DynamicVLA, OpenWAM-α. Grey dashed 0.40 pt; FoveaWAM black dashed 0.85 pt. |
| Selection | Each retained guide has a label and uses that method's actual p95. PUMA, π0.5+SE(3), DP, DynamicWAM and DynamicWAM+SE(3) are omitted from this plot; their data remain in Table 1. No average replaces a measured value. |
| Off-axis method | OpenWAM-α (off), p95 466.3 ms: caption only. |
| Pass | Omitted from the cm axis: its wire rotates at 2.5–7.5°/s. |
| Axes / palette | Linear, 0–200 ms and 0–26 cm. Core family colors; Capture label uses approved dark amber `#B37C00`. No grid or threshold shading. |

## 3. Interpretation boundaries

This is a **scale concept figure**, not measured displacement or causal evidence for the particular
Paused→Native ranking reversal. PUMA and π0.5+SE(3) have nearly the same p95 but different success-rate
changes. Target travel is not prediction/contact error; `e_p_mm` is not used.

**Continuous time versus execution age.** The user chose continuous $vL$ for presentation and now prefers
the original layout. The executor still hands over at $\lceil L/\Delta_a\rceil\Delta_a$, with
$\Delta_a=50$ ms; post-impact additionally has a 50 ms task delay. Thus $vL$ is a lower-bound motion estimate
**under the constant-speed approximation**, not observed execution displacement. The caption states
that approximation explicitly.

Do not present FoveaWAM's plotted Capture value (about 0.8–1.7 cm) as its actual first-command displacement.
The Capture first-command interval is 50 ms, corresponding to 2.8–5.7 cm under the same approximation.
Capture speeds were estimated from two samples 50 ms apart at the first ramp exit and are not constant
over a full episode. Bands are speed ranges, not confidence intervals.

The script retains four checks against logged p95 action ages for FoveaWAM and π0.5+SE(3), Native and
+150 ms. These checks do not establish measured action ages for the other methods.

## 4. Historical directions

Numbers refer to the image sequence shown before this refinement.

| Direction | Artifact | Status |
|---|---|---|
| #1: original independent figure | [panel_displacement.png](../../fig4_study/panel_displacement.png) | **User-selected visual basis for this revision.** |
| #2: single-column rank + displacement | [fig_rank_disp.png](../../fig4_study/fig_rank_disp.png) | User rejected the combined layout; reason not recorded. |
| #3: four-panel figure, (d) | [fig_latency_wide.png](../../fig4_study/fig_latency_wide.png) | Grey family bands and method-colored guides; not inserted into the paper. |
| #4 A: staircase, log y | [cand_A_staircase.png](candidates/cand_A_staircase.png) | Not selected; steps/log axis soften the immediate growth in distance. |
| #5 C: family × control-period matrix | [cand_C_matrix.png](candidates/cand_C_matrix.png) | Not selected; effectively a table. |
| #6 D: per-method dumbbell | [cand_D_dumbbell.png](candidates/cand_D_dumbbell.png) | User rejected: reads as a timing chart. |
| #7 E: linear-axis staircase | [cand_E_linear.png](candidates/cand_E_linear.png) | Superseded by the choice of continuous $vL$. |
| #8 E: continuous comparison | [cand_E_compare_vL_timebase.png](candidates/cand_E_compare_vL_timebase.png) | Time-base comparison artifact for #7. |
| #9: first continuous candidate | Git history: `Final candidate: continuous target-motion figure with column preview` | User found it unattractive; mixed label orientations, heavy guides and an off-axis note. |
| #10 F: header labels | [cand_F_header.png](candidates/cand_F_header.png) | Superseded; header used too much height and weakened method emphasis. |
| #11 G: log–log | [cand_G_loglog.png](candidates/cand_G_loglog.png) | Not selected; parallel strips lose the immediate linear-scale reading. |
| #12: Capture-band marks | [previous_capture_marks.png](candidates/previous_capture_marks.png) | Previous English candidate, superseded by the user's preference for #1. |
| First refinement of #1 | [previous_full_labels.png](candidates/previous_full_labels.png) | Complete method labels and bold title/family names; preserved before the current reduction of visual emphasis. |
| Ten-guide refinement of #1 | [previous_all_guides.png](candidates/previous_all_guides.png) | Sparse labels but all ten guides; user found the clustered dashed lines crowded. Replaced by five labelled guides. |

### References actually viewed in this pass

The original PDFs were rendered and viewed, not inferred from abstracts or search thumbnails.

| Paper and status | Figures actually viewed | Design judgment |
|---|---|---|
| [VAR, NeurIPS 2024](https://proceedings.neurips.cc/paper_files/paper/2024/file/9a24e284b187f662681440ba15c416fb-Paper-Conference.pdf), [Best Paper](https://blog.neurips.cc/2024/12/10/announcing-the-neurips-2024-best-paper-awards/) | Figs. 2/3 (PDF p. 2), Fig. 5 (p. 8) | Borrow the restrained axes and typography of Fig. 5. Do not copy Fig. 2's pictorial rendering or Fig. 3's shaded background/highlight box; those serve different comparisons. |
| [SAM 2, ICLR 2025](https://arxiv.org/pdf/2408.00714), [Outstanding Paper Honorable Mention](https://blog.iclr.cc/2025/04/22/announcing-the-outstanding-paper-awards-at-iclr-2025/) | Fig. 5, PDF p. 9 | Ordinary line plots, conventional typography, restrained line hierarchy. Its three-series legend is useful there; our family names already label the bands directly, so no second legend is added. |
| [The Value of Prediction in Identifying the Worst-Off, ICML 2025](https://proceedings.mlr.press/v267/fischer-abaigar25a.html), [Outstanding Paper](https://www.stat.lmu.de/en/latest-news/news-overview/news/outstanding-paper-award-at-icml-2025-94159132.html) | Conference PDF Fig. 1 (p. 5), Figs. 2/3 (p. 7) | Fig. 1 separates clear line boundaries from subordinate fill. Borrow that visual hierarchy, not its threshold semantics. Its heat-map styling is unnecessary here. |
| [VGGT, CVPR 2025](https://arxiv.org/pdf/2503.11651), [Best Paper](https://cvpr.thecvf.com/Conferences/2025/News/Awards_Press) | Fig. 2, PDF p. 3 | Inspected but not used as this plot's template: it is an architecture diagram, with a different information structure. |

Earlier work reported viewing a DC-AE poster and StreamingLLM slides; those are historical references.
No generated illustration, texture, icon, shadow, or external figure image is incorporated into this plot.

## 5. Caption draft (EN)

> **Target motion during inference.** Bands show $vL$ over each task family's linear speed range (Table~S1).
> Guides mark p95 time-to-action for selected methods (Table~1).
> OpenWAM-$\alpha$ (off), at 466\,ms, lies off the axis. Under a constant-speed approximation, $vL$ is a
> lower bound on motion up to the next 50\,ms control boundary.

This exact text is in `preview_column.tex` and occupies six lines in the compiled preview.

## 6. Placement, verification and reproduction

The exported figure is **234 × 151.2 pt**. In the CVPR preview, the block from the nominal column top
(72 pt) to the next body-text line (328.97 pt) is **about 257 pt**, or about 22 body-text lines.
The caption is approximately 64 pt high. The preview is one page with placeholder body text.

The **appendix recommendation remains a proposal**, not a user decision. This figure conveys a derived
scale; A's protocol and B's ranking results carry more direct evidence. No main-paper insertion or
fresh measurement of available main-text space was performed.

Verified on Windows:

- Four family ranges match the minima/maxima in the actual task table.
- Five guide x-coordinates equal the selected methods' individual result-JSON values; off-axis p95 is 466.3 ms.
- Four existing logged-age assertions pass. Normal text is at least 6.5 pt; method/family label boxes
  neither overlap each other nor extend outside the canvas.
- PNG is 975 × 630 pixels at 300 dpi. SVG retains editable text. PDF contains vector graphics and no raster
  images; Arial regular, bold and italic are embedded (`pdffonts`).
- The CVPR preview compiles to one page and is visually checked at its 3.25 in figure width.

From this directory in PowerShell (the shared paper venv has Matplotlib):

```powershell
& 'C:/workspace/se3-wam-icra2027/.venv/Scripts/python.exe' make_target_motion.py --font Arial
$taskPaperRoot = (Resolve-Path -LiteralPath '../../../..').Path
$env:TEXINPUTS = "$taskPaperRoot;$env:TEXINPUTS"
pdflatex -interaction=nonstopmode -halt-on-error preview_column.tex
python -c "import pymupdf; d=pymupdf.open('preview_column.pdf'); d[0].get_pixmap(dpi=150).save('preview_column.png')"
pdffonts target_motion.pdf
```

## 7. Remaining decisions

- Feedback on this refinement of #1 and its English caption.
- Appendix versus main-text placement; Chinese version after the English design is settled.
- Object-size/grasp-margin thresholds remain an unimplemented suggestion. No sizes were fetched or invented.

C shares p95 data with B and leaves the handover mechanism to A. Black method emphasis is deliberate
because the core colors already identify task families.
