# C. Target motion during inference: notes (candidate stage, 2026-11-16)

Status: after user feedback ("the original read better"), candidate E keeps the original layout with the executor time base; A/C/D are kept for the record. Awaiting the user's choice. Nothing in `sections/`, `figures/`
or shared specs was changed.

## 1. What the figure answers, and whether it earns space

Question: how far does the target move between capturing an observation and executing the commands
computed from it?

**The handoff version, panel (d) (band of v × p95), is trivial and also misleading.**
- It only multiplies the speeds in Table S1 by the p95 in Table 1; Fig. 4(a) already shows the scale (18 cm in 200 ms).
- It uses the wrong time. Per the appendix executor, the first command of a query executes at
  $k\Delta_a$ after capture, with $k=\lceil L/\Delta_a\rceil$. Later commands of the chunk run up to $(2k-1)\Delta_a$
  under steady replanning. For the fast methods, v × p95 therefore understates the open-loop interval
  3–9×. ACT: 5.8 ms vs. 50 ms; FoveaWAM: 15.1 vs. 50.

**What is not in Table 1 or Fig. 4(a): the executor turns latency into a staircase.**

| k | first command | methods (p95, ms) |
|---|---|---|
| 1 | 50 ms | ACT 5.8, FoveaWAM 15.1 |
| 2 | 100 ms | π0.5 59.6, PUMA 60.6, π0.5+SE(3) 61.2, DP 68.9, DynamicVLA 97.3 |
| 3 | 150 ms | DynamicWAM 149.6 (max 153.3, so a few queries have k=4) |
| 4 | 200 ms | OpenWAM-α 151.7 (p50 150.02, so at least half of queries have k=4), DynamicWAM+SE(3) 153.3 (p50 151.6) |
| 10 | 500 ms | OpenWAM-α (off) 466.3 |

Two consequences follow:
- ACT's lower latency buys nothing over FoveaWAM.
- p95 values from 60 to 97 ms are equivalent. DynamicWAM and OpenWAM-α differ by 2 ms but by one control period.

**Validation against logged data.** The executor logs action age only for FoveaWAM and π0.5+SE(3). Its logged p95 age
equals $(2k-1)\Delta_a$ in all four cases:

| Method | Native | +150 ms |
|---|---|---|
| FoveaWAM | 50 | 350 |
| π0.5+SE(3) | 150 | 450 |

The script asserts this. It does **not** validate the other nine methods; for them, k comes from their measured latency distribution.

**Placement judgment.** Main-text space is ~117 pt, and A (protocol) and B (ranking change) carry more of the argument.
I recommend:
1. **Main text:** one sentence (proposal in §6), no figure.
2. **Appendix:** the figure, next to "Real-Time Evaluation and Metrics" or the latency results (Table S5).
3. **Optional:** the cm scale folded into A's time axis.

If the user wants it in the main text, D is the only candidate that adds evidence rather than arithmetic.

## 2. Candidates (`candidates/`)

Space = figure height + caption (~3 lines ≈ 30 pt) + float spacing (~20 pt).

| | File | Size (pt) | With caption | Encoding | Cost |
|---|---|---|---|---|---|
| A | `cand_A_staircase` | 234 × 151 | ≈ 200 | x = time-to-action L; y = target travel (log); family bands are step functions of k; v_max·L dashed for contrast; p95 rug on top | Methods are only a rug (three groups of overlapping ticks); log axis softens the steps; Impact/Grasp bands overlap; Pass absent |
| D | `cand_D_dumbbell` | 234 × 153 | ≈ 205 | One row per method in tab10 colors (as Fig. 5): hollow = p95, filled = first command kΔ, light bar = later commands; black tick = logged p95 action age; top axis = travel of the Fig. 4(a) ball at 0.9 m/s; broken axis for OpenWAM-α (off) | Shows only one speed (other families need the caption); 11 rows |
| C | `cand_C_matrix` | 234 × 107 | ≈ 155 | Families × k groups, cell text = travel range at the first command (cm; Pass in deg), grey shade by upper value | Really a table; reviewers may ask why it is a figure. If chosen, I would rather set it as a LaTeX table in the appendix |

**Recommendation: D.**
- Method colors and row identity match Fig. 5, and family colors are not used, so there is no tab10 vs. core-palette conflict.
- It draws the quantization (the p95 → kΔ segment) and carries the only measured validation (logged ages).
- The cm axis is anchored to the paper's own Fig. 4(a) example, so 200 ms ↔ 18 cm is visible directly.
- Capture no longer squashes the other families, because only one representative speed is drawn.

The family ranges go in the caption, or as an appendix table (C's numbers).

Dropped during exploration:
- a log-x range chart grouped by k: each row is just a horizontal shift, so it hides the growth;
- colored family bands vs. p95 (`panel_displacement.png`): wrong time base, as in (d).

## 2b. Revision after user feedback (candidate E)

The user preferred the original `panel_displacement.png` reading: target error grows with latency, and each method's own
latency is marked on the same axis. That reading is the point of the figure; D replaced it with a timing chart, which was a mistake.
**E** (`cand_E_linear`, 234 × 158 pt, ≈ 205 pt with caption) keeps that layout:
- x = inference latency; linear y; family bands in core-palette colors; method lines at p95;
- FoveaWAM in black (not red) to avoid two reds in one figure (Impact is red).

The only change is the time base: travel = v · ⌈L/Δ⌉Δ, giving steps at 50 ms boundaries instead of v · L.
`cand_E_compare_vL_timebase.png` is the same layout with v · L, for comparison.

**Caption limit (disagreement recorded).** The figure supports "slower methods must bridge more target motion", e.g. OpenWAM-α vs. (off).
It does **not** explain the specific paused→native reversal in the text:
- PUMA and π0.5+SE(3) have p95 60.6 vs. 61.2 ms, so the same step and the same travel;
- yet they change by +8.3 and −17.3 points.

The caption must not claim the figure explains the ranking change.

## 3. Data sources and interpretation limits

- Speeds: `tables/task_definitions.tex`.
  - Capture: speed from two samples 50 ms apart at the first ramp exit, **not** a constant speed over the episode.
  - Impact: adds $d_{\rm task}=50$ ms (used in A and C).
  - Pass: angular, 2.5–7.5 °/s; C reports degrees.
- Latency: `results/realtime_c/table1-20261104.json`, RTX 5090, 900 samples (p50/p95/max). k is computed from p95.
  The per-query k can differ where p50 and p95 straddle a boundary (OpenWAM-α, DynamicWAM+SE(3), rarely DynamicWAM);
  the 900 raw samples (Research repo) would give the exact split.
- **Derived, not measured:**
  - Travel = v × age, assuming constant speed over the interval.
  - Bands are speed ranges, not confidence intervals or observed displacements.
  - `e_p_mm` is not used: it is an end-effector contact error, not target displacement.
- **Open-loop interval ≠ error.** A policy that extrapolates target motion can compensate. The figure shows how far ahead each
  policy must predict, not how far it misses. Cross-method SR differences within one k group (e.g. π0.5 −12.2 vs. PUMA +8.3
  native − paused, both k=2) show that k alone does not decide SR.
- Paused replans every 50 ms and executes command 0 (logged age 0); it is a reference, not an upper bound.

## 4. Open data items (Research repo, not fetched; awaiting the user's decision)

- Object half-widths and finger opening per task → a "lateral grasp margin" reference line. Cost: a few `gh api` file reads.
  No such tolerance exists in this repo except Pass "align within 30 mm", which needs the wire radius to convert from deg/s.
- The 900 latency samples per method → the exact k=3/4 split for OpenWAM-α and DynamicWAM(+SE(3)). Cheap.
- Per-task Paused SR for nine methods → a travel vs. SR-drop scatter. Not recommended: correlational and overlaps B.

## 5. Coordination

- **A:** A's example L=152 ms gives k=4, which is the OpenWAM-α / DynamicWAM+SE(3) row of D. If A keeps that example, use
  OpenWAM-α's real $H_m=32$, or mark the example as schematic.
  Proposal to A: label A's time axis with a secondary cm scale, e.g. "1 period = 50 ms ≈ 4.5 cm of the Fig. 4(a) ball",
  instead of a target-position band. That keeps C out of the main text without losing the cm conversion.
- **B:** uses the same p95 and method colors. If B orders methods by native rank, D could share that order;
  currently D sorts by p95, which matches its x-axis.

## 6. Proposed main-text sentence (for the main conversation; not applied)

In §5 "Effect of inference latency", or §4.3 after the executor sentence:

> Because the executor hands over chunks at control-period boundaries, the first command of a query executes 50 ms after
> capture for ACT and \ours, 100 ms for the five methods with p95 between 60 and 97 ms, and 150–200 ms for the video WAMs;
> a ball rolling at 0.9 m/s, as in Fig.~\ref{fig:bench_overview}(a), travels 4.5, 9, and 13.5–18 cm in these intervals.

## 7. References

No external figure was used as a reference. The browser was unavailable, and the user asked to continue without one.
None of the candidates claims to borrow from a specific paper.

## 8. Questions for the user

1. Which direction (A / D / C), and should it target the appendix (my recommendation) or the main text?
2. Fetch the Research-repo items in §4: grasp margins, raw latency samples, or both?
3. Should the cm scale be proposed to A as described in §5?
