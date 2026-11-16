"""Candidate C: the (c) dumbbell, revised (tie-aware ranks, no red/green rank colours)."""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rank_data as rd  # noqa: E402
from style import GRID, INK, MUTED, require_font, style  # noqa: E402

W, H = 3.25, 2.05


def rng_txt(r):
    return f"{r[0]}" if r[0] == r[1] else f"{r[0]}–{r[1]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    require_font(a.font)
    d = rd.load()
    _, srs = rd.native_paired_bootstrap()
    nr, pr = rd.native_rank_intervals(srs), rd.paused_rank_ranges(d)
    rows = sorted(rd.ORDER, key=lambda m: -d[m]["paused"][0])
    with plt.rc_context(style(a.font)):
        fig = plt.figure(figsize=(W, H), dpi=144)
        ax = fig.add_axes([0.335, 0.16, 0.43, 0.73])
        ax.set(xlim=(10, 95), ylim=(len(rows) - .4, -.6), xticks=[20, 40, 60, 80], yticks=[])
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.grid(axis="x", color=GRID, lw=.35)
        ax.set_axisbelow(True)
        ax.set_xlabel("Success rate (%)", labelpad=2)
        for i, m in enumerate(rows):
            c = rd.color(m)
            ours = m == "se3_wam"
            p, n = d[m]["paused"][0], d[m]["native"][0]
            ax.annotate("", xy=(n, i), xytext=(p, i), arrowprops=dict(
                arrowstyle="-|>", color=c, lw=1.2 if ours else .85, mutation_scale=4.5,
                shrinkA=2.2, shrinkB=2.6), zorder=3)
            ax.plot(p, i, "o", ms=3.0, mfc="white", mec=c, mew=.7, zorder=4)
            ax.plot(n, i, "o", ms=3.0, mfc=c, mec=c, mew=.7, zorder=4)
            ax.text(-0.025, i, rd.label(m), transform=ax.get_yaxis_transform(), ha="right",
                    va="center", fontsize=7, color=c if ours else INK,
                    weight="bold" if ours else "normal")
            for xx, txt in ((1.11, rng_txt(pr[m])), (1.34, rng_txt(nr[m]))):
                ax.text(xx, i, txt, transform=ax.get_yaxis_transform(), ha="center",
                        va="center", fontsize=7, color=INK)
        tr = ax.get_yaxis_transform()
        ax.text(1.225, -1.45, "Rank", transform=tr, ha="center", va="center", fontsize=6.5, color=MUTED)
        ax.text(1.11, -0.8, "Paused", transform=tr, ha="center", va="center", fontsize=6.5, color=MUTED)
        ax.text(1.34, -0.8, "Native", transform=tr, ha="center", va="center", fontsize=6.5, color=MUTED)
        # legend for hollow/filled
        for x0, fill, t in ((0.36, "white", "Paused"), (0.55, MUTED, "Native")):
            fig.add_artist(Line2D([x0], [0.955], transform=fig.transFigure, marker="o", ms=3,
                                  mfc=fill, mec=MUTED, mew=.7, ls="none"))
            fig.text(x0 + .025, 0.955, t, va="center", fontsize=7)
        fig.text(0.08, 0.955, "", va="center")
        fig.savefig(a.output_dir / "cand_C_dumbbell.png", dpi=300)
        fig.savefig(a.output_dir / "cand_C_dumbbell.pdf")


if __name__ == "__main__":
    main()
