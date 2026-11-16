"""Candidate A: slopegraph on a shared SR scale (Paused -> Native)."""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rank_data as rd  # noqa: E402
from style import INK, MUTED, repel, require_font, style  # noqa: E402

W, H = 3.25, 2.05
TOP, BOT = 0.20, 0.06          # inches reserved above / below the SR scale
YLIM = (14, 92)
XP, XN = 1.33, 1.92            # column positions (inches)
NUM_W = 0.05                   # gap between column and value text
LAB_W = 0.33                   # gap between column and method label
TIES = {"native": [["dynamicwam_se3", "act", "dynamicwam"]],
        "paused": [["openwam_official", "openwam"]]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    require_font(a.font)
    d = rd.load()
    with plt.rc_context(style(a.font)):
        fig = plt.figure(figsize=(W, H), dpi=144)
        ax = fig.add_axes([0, BOT / H, 1, 1 - (TOP + BOT) / H])
        ax.set_xlim(0, W)
        ax.set_ylim(*YLIM)
        ax.axis("off")
        unit_pt = (H - TOP - BOT) * 72 / (YLIM[1] - YLIM[0])
        for x, t in ((XP, "Paused"), (XN, "Native")):
            ax.plot([x, x], YLIM, color="#C8C8C8", lw=.5, zorder=0)
            ax.text(x, YLIM[1] + 4.5 / unit_pt, t, ha="center", va="bottom", fontsize=7, weight="bold")

        for m in rd.ORDER:
            c = rd.color(m)
            ours = m == "se3_wam"
            p, pc = d[m]["paused"]
            n, nc = d[m]["native"]
            ax.plot([XP, XN], [p, n], color=c, lw=1.2 if ours else .85,
                    ls="--" if rd.hollow(m) else "-", zorder=5 if ours else 3,
                    dash_capstyle="butt", solid_capstyle="butt")
            for x, v, ci in ((XP, p, pc), (XN, n, nc)):
                ax.plot([x, x], ci, color=c, lw=.5, zorder=4, solid_capstyle="butt")
                ax.plot(x, v, marker=rd.marker(m), ms=3.1 if ours else 2.8, mec=c, mew=.65,
                        mfc="white" if rd.hollow(m) else c, zorder=6 if ours else 4.5, ls="none")

        gap = 7.2 / unit_pt
        for key, x, sgn in (("paused", XP, -1), ("native", XN, 1)):
            ys = [d[m][key][0] for m in rd.ORDER]
            pos = dict(zip(rd.ORDER, repel(ys, gap, lo=YLIM[0], hi=YLIM[1])))
            ha = "right" if sgn < 0 else "left"
            for m, y in zip(rd.ORDER, ys):
                ours = m == "se3_wam"
                yl = pos[m]
                # value next to the column, label outside it; short elbow if displaced
                xv = x + sgn * (NUM_W + .03)
                if abs(yl - y) > 0.3:
                    ax.plot([x + sgn * .03, xv - sgn * .01], [y, yl], color="#A0A0A0", lw=.35,
                            zorder=1, clip_on=False)
                ax.text(xv, yl, f"{d[m][key][0]:.1f}", ha=ha, va="center", fontsize=6.5,
                        color=MUTED, clip_on=False)
                ax.text(x + sgn * LAB_W, yl, rd.label(m),
                        ha=ha, va="center", fontsize=7,
                        color=rd.color(m) if ours else INK, weight="bold" if ours else "normal",
                        clip_on=False)
            # bracket statistically tied groups on the outside of the labels' value column
            for grp in TIES[key]:
                ylo, yhi = min(pos[m] for m in grp), max(pos[m] for m in grp)
                bx = x + sgn * (LAB_W - .025)
                ax.plot([bx, bx], [ylo - gap * .35, yhi + gap * .35], color=MUTED, lw=.5,
                        clip_on=False, solid_capstyle="butt")
        fig.savefig(a.output_dir / "cand_A_slope.png", dpi=300)
        fig.savefig(a.output_dir / "cand_A_slope.pdf")


if __name__ == "__main__":
    main()
