"""FUTURE0: grouped design comparison and discordant paired outcomes.

Reads Research's accepted independent1260 analysis. Adds descriptive paired
scene-bootstrap intervals; no fixed140 pooling or new hypothesis tests.
Order follows design, not score. Outputs: SVG, vector PDF, CSVs and review PNGs.
Physical size: 7 x 3.25 inches; minimum type: 8.25 pt (8.10 pt at 6.875 in).
"""
from pathlib import Path
import argparse
import csv
import sys
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from common import REVIEW, add_research_argument, research_root, svg_to_pdf
from paired_uncertainty import export_csv, future0_intervals

ANALYSIS = Path("docs/experiments/FUTURE0/results/independent1260/analysis")
W, H = 672, 312  # 96 CSS px/in; exported without cropping or rescaling.
FONT = 11  # 8.25 pt; remains above 8 pt if placed at CVPR's 6.875 in text width.
C = dict(ink="#252A30", gray="#555B62", line="#D7D9DD", band="#F5F5F6",
         purple="#7B61A8", pale="#E6DEEF", orange="#E69F00")
ARMS = ["P00", "P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08",
        "P09", "Aalpha", "P12", "P13", "P14", "P15"]
# Structured labels use FUTURE0 design definitions. Scene flow includes target.
GROUPS = [
    (("Core", "targets"), [("P00", "No future supervision"), ("P01", "3-D scene flow"),
        ("P02", "Target pose"), ("P03", "Scene flow + target pose")]),
    (("Scene", "+ target pose"), [("P04", "Wan latent"), ("P05", "Dense 2-D displacement"),
        ("P06", "Codec motion"), ("P07", "Sparse scene tracks")]),
    (("Target", "+ scene flow"), [("P08", "Object DINO"), ("P09", "Target tracks")]),
    (("Add to P03",), [("Aalpha", "Motion magnitude"), ("P12", "Depth"),
        ("P13", "DINO"), ("P14", "Dynamic RGB"), ("P15", "Depth + DINO + dyn. RGB")]),
]
PAIRED_ARMS = ["P03", "P05", "P07", "P09", "P15"]


def text(s, x, y, body, size=FONT, weight="normal", color=None, anchor="start"):
    s.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" font-weight="{weight}" '
             f'fill="{color or C["ink"]}" text-anchor="{anchor}">{escape(str(body))}</text>')


def line(s, x1, y1, x2, y2, color=None, width=.8, dash=None):
    s.append(f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" '
             f'stroke="{color or C["line"]}" stroke-width="{width:g}"'
             + (f' stroke-dasharray="{dash}"' if dash else "") + '/>')


def rect(s, x, y, w, h, fill, stroke="none", sw=.65):
    s.append(f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="{sw:g}"/>')


def number(value):
    return "0.00" if abs(value) < 1e-10 else f"{value:+.2f}".replace("-", "−")


def load_data(source):
    with (source / "arm-summary.csv").open(encoding="utf-8", newline="") as f:
        raw = list(csv.DictReader(f))
    with (source / "paired-summary.csv").open(encoding="utf-8", newline="") as f:
        pairs = {r["arm"]: r for r in csv.DictReader(f)
                 if r["scope"] == "overall" and r["reference_arm"] == "P00"}
    assert [r["arm"] for r in raw] == ARMS
    assert [a for _, members in GROUPS for a, _ in members] == ARMS
    assert all(int(r["n"]) == 1260 for r in raw)
    assert len(pairs) == 14
    rows = {r["arm"]: r for r in raw}
    base = int(rows["P00"]["successes"])
    for arm, r in rows.items():
        n, successes = int(r["n"]), int(r["successes"])
        assert abs(float(r["sr"]) - successes / n) < 1e-12
        r["delta_pp"] = 100 * (successes - base) / n
        if arm == "P00":
            continue
        p = pairs[arm]
        gain, loss = int(p["arm_only_success"]), int(p["reference_only_success"])
        assert gain - loss == successes - base
        assert int(p["both_success"]) + gain == successes
        assert int(p["both_success"]) + loss == base
        assert sum(int(p[k]) for k in ("both_success", "arm_only_success",
                                      "reference_only_success", "both_failure")) == n
        assert abs(float(p["sr_difference"]) * 100 - r["delta_pp"]) < 1e-12
    return rows, pairs


def export_data(rows, pairs, intervals):
    # A generated visual export; Research remains the owner of experiment facts.
    fields = ["arm", "design_group", "structured_label", "n", "successes", "sr",
              "delta_pp_vs_P00", "ci95_low_pp", "ci95_high_pp",
              "gain_vs_P00", "loss_vs_P00", "net_vs_P00",
              "paired_panel", "arm_source", "paired_source"]
    with (ROOT / "future_supervision_data.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for group, members in GROUPS:
            for arm, label in members:
                r, p = rows[arm], pairs.get(arm)
                ci = intervals.get(arm)
                gain = int(p["arm_only_success"]) if p else ""
                loss = int(p["reference_only_success"]) if p else ""
                writer.writerow(dict(arm=arm, design_group=" / ".join(group),
                    structured_label=label, n=r["n"], successes=r["successes"], sr=r["sr"],
                    delta_pp_vs_P00=r["delta_pp"], gain_vs_P00=gain, loss_vs_P00=loss,
                    ci95_low_pp=ci["ci95_low_pp"] if ci else "",
                    ci95_high_pp=ci["ci95_high_pp"] if ci else "",
                    net_vs_P00=gain-loss if p else "", paired_panel=arm in PAIRED_ARMS,
                    arm_source="FUTURE0/results/independent1260/analysis/arm-summary.csv",
                    paired_source="FUTURE0/results/independent1260/analysis/paired-summary.csv" if p else ""))


def draw(rows, pairs, intervals):
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="7in" height="{H/96:g}in" '
         f'viewBox="0 0 {W} {H}">',
         '<title>Future supervision: grouped differences and paired scene outcomes</title>',
         '<desc>Fifteen conditions, one training seed each, 1260 paired scenes. '
         'Dots show success-rate differences versus P00; whiskers are 95% pointwise '
         'task-stratified paired percentile bootstrap intervals from 100000 resamples. '
         'Intervals condition on current checkpoints and exclude training-seed variability '
         'and multiplicity adjustment. P00 has no interval.</desc>',
         '<defs><pattern id="loss-hatch" width="4" height="4" patternUnits="userSpaceOnUse">'
         f'<rect width="4" height="4" fill="{C["pale"]}"/>'
         '<path d="M-1 1L1 -1M0 4L4 0M3 5L5 3" '
         f'stroke="{C["purple"]}" stroke-width=".45" opacity=".6"/>'
         '</pattern></defs>', f'<rect width="{W}" height="{H}" fill="white"/>',
         '<g font-family="Arial, Helvetica, sans-serif">']
    text(s, 6, 14, "(a) Future supervision by design axis", 12, "bold")
    text(s, 455, 14, "(b) Paired outcomes vs P00", 12, "bold")
    line(s, 444, 7, 444, 292, width=.8)
    x0, scale = 345, 12.5  # delta_pp [-6, 4] -> [270, 395].
    text(s, 82, 35, "ID", color=C["gray"])
    text(s, 112, 35, "Future targets / additions", color=C["gray"])
    text(s, 334, 35, "95% pointwise CI", color=C["gray"], anchor="middle")
    text(s, 435, 35, "Δ pp", color=C["gray"], anchor="end")
    row_y, y = {}, 51
    for group, members in GROUPS:
        top, bottom = y-9, y+14*(len(members)-1)+7
        rect(s, 76, top, 360, bottom-top, C["band"])
        center = (top+bottom)/2
        for j, label in enumerate(group):
            text(s, 3, center+3.3+(j-(len(group)-1)/2)*12, label,
                 weight="bold" if j == 0 else "normal", color=C["gray"])
        line(s, 70, top+1, 70, bottom-1, C["orange"], 1.1)
        line(s, 70, top+1, 74, top+1, C["orange"], 1.1)
        line(s, 70, bottom-1, 74, bottom-1, C["orange"], 1.1)
        for arm, label in members:
            row_y[arm] = y
            text(s, 82, y+3.3, "Aα" if arm == "Aalpha" else arm)
            text(s, 112, y+3.3, label)
            y += 14
        y += 4
    for tick in (-6, -4, -2, 0, 2, 4):
        xpos = x0+scale*tick
        line(s, xpos, 42, xpos, 266, C["gray"] if tick == 0 else C["line"],
             .85 if tick == 0 else .6, None if tick == 0 else "2 2")
        line(s, xpos, 273, xpos, 276, C["gray"], .8)
        text(s, xpos, 287, str(tick).replace("-", "−"), anchor="middle", color=C["gray"])
    line(s, 270, 273, 395, 273, C["gray"], .8)
    for arm in ARMS:
        y, delta = row_y[arm], rows[arm]["delta_pp"]
        xpos = x0+scale*delta
        if arm == "P00":
            s.append(f'<path d="M{x0} {y-3.4}L{x0+3.4} {y}L{x0} {y+3.4}L{x0-3.4} {y}Z" '
                     f'fill="{C["gray"]}"/>')
        else:
            ci = intervals[arm]
            low, high = ci["ci95_low_pp"], ci["ci95_high_pp"]
            assert -6 <= low <= delta <= high <= 4
            left, right = x0+scale*low, x0+scale*high
            line(s, left, y, right, y, C["purple"], 1.2)
            line(s, left, y-2.5, left, y+2.5, C["purple"], 1.2)
            line(s, right, y-2.5, right, y+2.5, C["purple"], 1.2)
            s.append(f'<circle cx="{xpos:g}" cy="{y:g}" r="2.6" fill="{C["purple"]}"/>')
        text(s, 435, y+3.3, "ref." if arm == "P00" else number(delta), anchor="end")
    base = float(rows["P00"]["sr"])*100
    text(s, 6, 287, f"P00: {base:.2f}% · 1,260 scenes · 1 seed", color=C["gray"])
    text(s, 334, 304, "Δ SR vs P00 (pp)", anchor="middle", color=C["gray"])
    text(s, 6, 304, "CI: scene sampling only", color=C["gray"])

    # Pale hatch = reference-only success; solid = candidate-only success.
    zero, paired_scale = 560, .63
    text(s, 525, 35, "Losses", anchor="middle", color=C["gray"])
    text(s, 595, 35, "Gains", anchor="middle", color=C["gray"])
    text(s, 666, 35, "Net", anchor="end", color=C["gray"])
    for tick in (-100, -50, 0, 50, 100):
        xpos = zero+paired_scale*tick
        line(s, xpos, 42, xpos, 248, C["gray"] if tick == 0 else C["line"],
             .85 if tick == 0 else .6, None if tick == 0 else "2 2")
        line(s, xpos, 259, xpos, 262, C["gray"], .8)
        text(s, xpos, 275, str(abs(tick)), anchor="middle", color=C["gray"])
    line(s, 497, 259, 623, 259, C["gray"], .8)
    for index, arm in enumerate(PAIRED_ARMS):
        y = 63+index*43
        gain, loss = int(pairs[arm]["arm_only_success"]), int(pairs[arm]["reference_only_success"])
        text(s, 455, y+3.5, arm)
        rect(s, zero-loss*paired_scale, y-7, loss*paired_scale, 14, "url(#loss-hatch)", C["purple"])
        rect(s, zero, y-7, gain*paired_scale, 14, C["purple"], C["purple"])
        text(s, zero-loss*paired_scale/2, y+3.5, loss, anchor="middle")
        text(s, zero+gain*paired_scale/2, y+3.5, gain, anchor="middle", color="white")
        text(s, 666, y+3.5, f"{gain-loss:+d}".replace("-", "−"), anchor="end")
    text(s, 560, 290, "Discordant scenes", anchor="middle", color=C["gray"])
    text(s, 455, 304, "Net = gains − losses", color=C["gray"])
    s.append('</g></svg>')
    return '\n'.join(s)


def main(source):
    rows, pairs = load_data(source)
    all_intervals = future0_intervals(source)
    intervals = {r["arm"]: r for r in all_intervals if r["reference_arm"] == "P00"}
    assert len(intervals) == 14
    assert all(abs(rows[a]["delta_pp"]-ci["delta_pp"]) < 1e-12 for a, ci in intervals.items())
    export_csv(all_intervals, ROOT/"future_supervision_uncertainty.csv")
    export_data(rows, pairs, intervals)
    path = ROOT/"future_supervision.svg"
    path.write_text(draw(rows, pairs, intervals), encoding="utf-8")
    svg_to_pdf(path, preview_dir=REVIEW)
    print(f"{path.name}: 7 x {H/96:g} in; minimum text 8.25 pt; review PNGs: {REVIEW}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_research_argument(parser)
    parser.add_argument("--source", type=Path,
                        help="FUTURE0 analysis directory (default: under the Research checkout)")
    args = parser.parse_args()
    main(args.source or research_root(args.research_root) / ANALYSIS)
