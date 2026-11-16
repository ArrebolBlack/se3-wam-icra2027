"""Candidate B: Paused SR (x) vs. Native SR (y) with the y = x reference."""
import argparse
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rank_data as rd  # noqa: E402
from style import GRID, INK, MUTED, require_font, style  # noqa: E402

W, H = 3.25, 2.55
LIM = (10, 95)
# label offsets in points (dx, dy, ha)
OFF = {
    "se3_wam": (-5, 0, "right"),
    "pi05_se3": (4, -4, "left"),
    "pi05": (4, 2, "left"),
    "dynamicwam_se3": (5, 0, "left"),
    "openwam_official": (5, 0, "left"),
    "openwam": (5, 0, "left"),
    "dynamicvla": (-4, 4, "right"),
    "puma": (-5, 0, "right"),
    "dynamicwam": (1, -7, "left"),
    "act": (-5, 2, "right"),
    "dp": (5, -3, "left"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    a = ap.parse_args()
    require_font(a.font)
    d = rd.load()
    with plt.rc_context(style(a.font)):
        fig = plt.figure(figsize=(W, H), dpi=144)
        ax = fig.add_axes([0.14, 0.135, 0.83, 0.84])
        ax.set(xlim=LIM, ylim=LIM, xticks=range(20, 100, 20), yticks=range(20, 100, 20))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color=GRID, lw=.35)
        ax.set_axisbelow(True)
        ax.plot(LIM, LIM, color=MUTED, lw=.6, ls=(0, (3, 2)), zorder=1)
        ax.text(17.5, 19.5, "y = x", rotation=45, rotation_mode="anchor", ha="left",
                va="bottom", fontsize=6.5, color=MUTED, transform_rotates_text=True)
        ax.set_xlabel("SR with the world paused (%)", labelpad=3)
        ax.set_ylabel("SR at native latency (%)", labelpad=3)
        # The one clean latency-only contrast: same OpenWAM-alpha policy, two deployments.
        a1, a2 = d["openwam_official"], d["openwam"]
        ax.annotate("", xy=(a2["paused"][0], a2["native"][0]), xytext=(a1["paused"][0], a1["native"][0]),
                    arrowprops=dict(arrowstyle="-|>", color=rd.color("openwam"), lw=.6,
                                    mutation_scale=5, shrinkA=3, shrinkB=3), zorder=2)
        ax.text(a1["paused"][0] + 1.3, 30.5, "same policy,\np95 152 → 466 ms", fontsize=6.5,
                color=rd.color("openwam"), va="center", ha="left", linespacing=1.0)
        for m in rd.ORDER:
            c = rd.color(m)
            ours = m == "se3_wam"
            (p, pc), (n, nc) = d[m]["paused"], d[m]["native"]
            ax.errorbar(p, n, xerr=[[p - pc[0]], [pc[1] - p]], yerr=[[n - nc[0]], [nc[1] - n]],
                        fmt="none", ecolor=c, elinewidth=.5, capsize=0, zorder=3)
            ax.plot(p, n, marker=rd.marker(m), ms=3.4 if ours else 3.0, mec=c, mew=.7,
                    mfc="white" if rd.hollow(m) else c, ls="none", zorder=5 if ours else 4)
            dx, dy, ha = OFF[m]
            ax.annotate(rd.label(m), (p, n), xytext=(dx, dy), textcoords="offset points",
                        ha=ha, va="center", fontsize=7, color=c if ours else INK,
                        weight="bold" if ours else "normal")
        fig.savefig(a.output_dir / "cand_B_scatter.png", dpi=300)
        fig.savefig(a.output_dir / "cand_B_scatter.pdf")


if __name__ == "__main__":
    main()
