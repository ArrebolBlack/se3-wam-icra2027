# C. Target motion during inference: notes (2026-11-16)

**Status:** English final candidate `target_motion.{pdf,svg,png}`; waiting for the user's approval before the Chinese version.
Nothing in `sections/`, `figures/`, `tables/` or the shared specs was changed.

## 1. Files

| File | Content |
|---|---|
| `make_target_motion.py` | `python make_target_motion.py --font Arial` writes `target_motion.*` here; `--variant all` regenerates the exploration candidates into `candidates/`. Fails if the font is missing (no silent fallback). |
| `target_motion.{pdf,svg,png}` | 3.25 × 1.95 in (234 × 140 pt). Methods are range marks on the Capture band, labelled with horizontal text and thin leaders in the empty upper-left region. The repo copy was rendered on Linux with Liberation Sans (metric-compatible with Arial). Re-run with `--font Arial` on Windows before inserting. |
| `preview_column.{tex,pdf,png}` | The figure at print size in a CVPR two-column page (`cvpr.sty`), with the draft caption |
| `candidates/` | Directions explored and set aside (§4) |

## 2. What the figure answers

How far does a target move while a policy infers, and where does each method sit on that scale?

It converts milliseconds into centimetres and makes the cost of latency visible next to each method's own latency.

It is a **concept figure, not evidence**:
- It supports "slower policies must bridge more target motion", e.g. the two OpenWAM-α deployments: same policy, 151.7 vs. 466.3 ms.
- It does **not** explain the specific paused → native reversal in the text. PUMA (60.6 ms) and π0.5+SE(3) (61.2 ms) sit at the
  same point, yet change by +8.3 and −17.3 points. The caption and the text must not say the figure explains the ranking change.

## 3. Encoding and data

| Element | Encoding / source |
|---|---|
| Bands | $d=vL$ for each family's **linear** speed range in `tables/task_definitions.tex`: Grasp 0.03–0.20, Place 0.03–0.06, Capture 0.55–1.14, Impact 0.12–0.14 m/s. Upper line = v_max; thin lower line = v_min. Core-palette family colors, as in Fig. 4 |
| Pass | Omitted: its wire rotates at 2.5–7.5°/s, so it has no place on a cm axis. The caption says "linear speed range" |
| Method marks | p95 time-to-action from `results/realtime_c/table1-20261104.json` (same as Table 1).
- Each method is a vertical bar spanning the Capture band at its p95 (v_min·L to v_max·L), with a dot at v_max·L.
- Baselines are grey (1.1 pt) with 6.5 pt labels; FoveaWAM is black (1.8 pt) with a 7 pt bold label.
- Labels are horizontal and connected by 0.45 pt leaders.
- π0.5, PUMA and π0.5+SE(3) (59.6–61.2 ms) share one mark at their mean; so do DynamicWAM, OpenWAM-α and DynamicWAM+SE(3) (149.6–153.3 ms) |
| FoveaWAM line | Black, 1.2 pt, bold label. Not tab:red, because Impact is red here and one color may carry only one meaning per figure |
| Off-axis method | OpenWAM-α (off), 466 ms: named in the caption, not drawn |
| Fig. 4(a) anchor | Grey hollow circle at (200 ms, 18 cm); grey so that it does not compete with FoveaWAM's black |
| Circle | The Fig. 4(a) example: 200 ms, 18 cm, i.e. 0.9 m/s, inside the Capture range |
| Axes | x 0–200 ms, so the Fig. 4(a) example sits on the right edge; y 0–24 cm, linear. Bands drawn widest first (Capture, Grasp) and narrow families on top with stronger alpha (Place, Impact), so overlaps do not turn muddy; only the v_max edge is stroked. Fonts 7 pt (labels) and 6.5 pt (annotations); axes 0.55 pt; method lines 0.6 pt; grid #E5E5E5 0.35 pt |

**Continuous vs. staircase (decided with the user).** By the appendix executor, a command first executes at
$\lceil L/\Delta_a\rceil\Delta_a$ after capture, not at $L$. The script asserts this against the logged p95 action ages of
FoveaWAM and π0.5+SE(3), native and +150 ms. The user chose the continuous $vL$ for presentation, and I agree:
- it matches Fig. 4(a), which is also stated continuously (200 ms → 18 cm);
- the handover mechanism is A's job.

Consequence: $vL$ is a **lower bound**, and the caption says so. Do not quote cm values read off this figure for the fast methods.
FoveaWAM's Capture value reads ≈ 0.8–1.7 cm here, but the executor's first-command interval of 50 ms gives 2.8–5.7 cm.

**Other limits.**
- Capture speeds come from two frames 50 ms apart at the ramp exit; they are not constant over an episode.
- Bands are speed ranges, not confidence intervals or measured displacements. `e_p_mm` is not used.

## 4. Directions considered

| Direction | File | Outcome |
|---|---|---|
| Handoff panel (d) | v × p95 grey bands in the four-panel figure | Grey family bands lose the Fig. 4 family identity; method lines in tab10 colors clash with family colors |
| A: staircase | `cand_A_staircase` | Log y; methods as a rug. Correct, but the steps add noise and the log axis hides the growth |
| D: per-method dumbbell | `cand_D_dumbbell` | Rejected by the user: it reads as a timing chart and loses "error grows with latency" |
| C: family × k matrix | `cand_C_matrix` | A table in disguise |
| F: label header (superseded) | `cand_F_header` | The methods, the most important information, were the weakest element: faint guides plus a rotated grey header taking ~25 % of the height. Replaced by marks on the Capture band |
| G: log–log | `cand_G_loglog` | Solves the squashed bottom families and fits OpenWAM-α (off). Rejected: every family becomes a parallel diagonal, so the figure reads as a scaling plot and loses the immediate "error grows with latency" |
| First continuous final (superseded 2026-11-16) | — | User: not attractive. Full-height dashed lines cut the bands; labels mixed rotated/horizontal inside the data area; empty upper-left; muddy overlaps; floating off-axis note. Fixed in the current version |
| E: original layout with steps | `cand_E_linear`, `cand_E_compare_vL_timebase` | Superseded by the continuous final, per the user's preference |

**References actually viewed.** This workspace reaches only files committed to public GitHub repositories; arXiv, OpenReview and README image hosts are blocked, and no browser was available.
Award-paper repositories checked (VAR, VGGT, ConvNeXt, Segment Anything) keep their figures outside git, so none could be viewed.
Two files were viewed, both below award level:
- **DC-AE poster** (ICLR 2025, `mit-han-lab/efficientvit/assets/dc_ae_poster.pdf`). Borrowed: grey for every baseline and one emphasis for the authors' own method; labels placed directly on the data instead of a legend.
  Considered and **not** borrowed: its ratio callouts ("19.1× speedup"). Here the motion ratio equals the latency ratio, which Fig. 1(b) already states ("≈1/10 the p95 latency"), so a callout would repeat it.
- **StreamingLLM talk slides** (ICLR 2024, `mit-han-lab/streaming-llm/assets/StreamingLLM.pdf`, slide 9). A derived cost curve, KV-cache size vs. sequence length, becomes meaningful only against a reference threshold (the dashed "Model Size" line).
  The analogue here would be a horizontal "ball diameter" or "grasp margin" line. That needs object sizes from the Research repo, which have not been fetched (§8).

For broader references (CVPR / NeurIPS award figures), the user would need to connect a browser.

## 5. Caption draft (EN)

> **Target motion during inference.** Distance $vL$ that a target travels in an inference latency $L$, over the linear
> speed range of each task family (Table~S1). Marks span the Capture band at each method's p95 time-to-action (Table~1);
> OpenWAM-$\alpha$ (off), at 466\,ms, lies off the axis. Since chunks are handed over at the next 50\,ms boundary, $vL$ is a lower bound.

In the preview this runs 6 lines; dropping the OpenWAM-α (off) clause saves one. Optional additions, at about one line each:
- "Capture speeds are measured at the ramp exit."
- "OpenWAM-α (off), at 466 ms, lies off the axis." (The figure already labels it.)

## 6. Placement and space (measured in `preview_column.pdf`)

As a single-column float at the top of a column, the block from the text top to the next text line is **≈ 243 pt (≈ 20 lines)**:
- figure 140 pt;
- caption 6 lines ≈ 63 pt;
- float separation ≈ 30 pt in `cvpr.sty`.

Recommendation, in order:
1. **Appendix**, next to "Real-Time Evaluation and Metrics" or Table S5, with one main-text sentence:
   > A ball rolling at 0.9\,m/s, as in Fig.~\ref{fig:bench_overview}(a), travels about 5\,cm during the 50\,ms in which
   > \ours's first command takes effect and 9--14\,cm for methods with a p95 of 60--150\,ms
   > (Fig.~\ref{fig:target_motion}).

   Numbers: 0.9 m/s × 50 / 100 / 150 ms = 4.5 / 9 / 13.5 cm, i.e. the executor's handover times, not v × p95.
2. **Main text**, only if roughly 19 lines can be cut. Of the three small figures it carries the least evidence.
   A (protocol) and B (ranking change) support claims the text makes; C illustrates a scale that Fig. 4(a) already shows once.
3. Not recommended: panel (d) of the Fig. 5 four-panel figure. Its tab10 method colors and the core family colors would clash in one figure.

## 7. Coordination

- **A:** A's example L = 152 ms is OpenWAM-α's p95. If A keeps it, use OpenWAM-α's $H_m = 32$, or label it schematic.
  A cm hint on A's time axis is optional now that C exists.
- **B:** shares p95 values. B's method colors are tab10; C deliberately does not color methods, so the two figures do not conflict.

## 8. Open items for the user

1. Approve the English figure and caption, then I produce `--lang zh` (fonts `["Arial", "Microsoft YaHei"]`).
2. Placement: appendix (recommended) or main text.
3. **Recommended next step:** fetch the Capture objects' sizes (ball diameter, slider and can widths) and the finger opening from the Research repo. A few file reads.
   A horizontal "ball diameter" line would turn the curve from arithmetic into a threshold:
   - methods whose mark rises above the line wait long enough for the target to move more than its own size;
   - methods below it do not.

   This is the StreamingLLM "Model Size" device, and the only change I see that adds information rather than polish.
