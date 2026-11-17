"""Paused vs. Native SR and ranking on OnTimeBench (small_figs/B).

Rows follow the Paused ranking. Hollow black circle: SR with the world paused during inference;
filled circle in the method colour: SR at native latency; the arrow points from Paused to Native.
Ranks are ordinal positions of the one-decimal SRs in Table 1 (no ties at that precision).
The full rank transition is red for a drop, green for a rise, and black when unchanged.
Method colours follow the shared palette used by Fig. 5, including the original grey DP.
The optional Fig. 5 line-style comparison keeps the same Paused/Native marker encoding.

Usage:
  python make_rank_shift.py                      # Arial (Windows), English
  python make_rank_shift.py --font "Liberation Sans" --lang en
  python make_rank_shift.py --lang zh            # Arial + Microsoft YaHei
  python make_rank_shift.py --line-style fig5    # Base/off dashed, other methods solid
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath

import rank_data as rd
from style import require_font, style

HERE = Path(__file__).resolve().parent
W, H = 3.25, 1.86                     # inches; single CVPR column
BLACK = "#000000"
LEFT, RIGHT = 1.10, 2.56              # SR axis extent (inches from the left edge)
BOTTOM, TOP = 0.315, 0.20             # inches below / above the row block
XLIM = (10, 95)
MIN_ARROW = 4.5                       # SR points; shorter changes show markers only (arrow would be hidden)
SHORT_DASH = (0, (1.5, .9))           # short dashes for the single-column connectors

TEXT = {
    "en": dict(paused="Paused", native="Native", xlabel="Success rate (%)", rank="Rank"),
    "zh": dict(paused="暂停", native="原生", xlabel="成功率（%）", rank="排名"),
}


def ranks(values: dict[str, float]) -> dict[str, int]:
    order = sorted(values, key=lambda m: -values[m])
    if len({values[m] for m in order}) != len(order):
        raise ValueError("Tied one-decimal SRs; ordinal ranks would be ambiguous.")
    return {m: i + 1 for i, m in enumerate(order)}


def draw(lang: str, font: str, line_style: str = "solid"):
    t = TEXT[lang]
    d = rd.load()
    paused = {m: round(d[m]["paused"][0], 1) for m in rd.ORDER}
    native = {m: round(d[m]["native"][0], 1) for m in rd.ORDER}
    rp, rn = ranks(paused), ranks(native)
    rows = sorted(rd.ORDER, key=lambda m: rp[m])

    fig = plt.figure(figsize=(W, H), dpi=144)
    ax = fig.add_axes([LEFT / W, BOTTOM / H, (RIGHT - LEFT) / W, 1 - (BOTTOM + TOP) / H])
    n = len(rows)
    ax.set(xlim=XLIM, ylim=(n - .45, -.55), xticks=[20, 40, 60, 80], yticks=[])
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(False)
    ax.set_xlabel(t["xlabel"], labelpad=2.5)

    drawn = []
    for i, m in enumerate(rows):
        c = rd.color(m)
        ours = m == "se3_wam"
        p, q = d[m]["paused"][0], d[m]["native"][0]
        lw = 1.2 if ours else .85
        dashed = line_style == "fig5" and rd.METHODS[m][3] == "--"
        if abs(q - p) >= MIN_ARROW:
            annotation = ax.annotate("", xy=(q, i), xytext=(p, i), zorder=3,
                                     arrowprops=dict(arrowstyle="-|>,head_length=0.32,head_width=0.16",
                                                     color=c, lw=lw, linestyle="-", capstyle="round",
                                                     shrinkA=2.4, shrinkB=2.7))
            if dashed:
                # Split the same arrow geometry: dash only the shaft, keep the filled head solid.
                # Resolve point sizes at the canvas DPI before converting the paths to data space.
                annotation.draw(fig.canvas.get_renderer())
                arrow = annotation.arrow_patch
                path = ax.transData.inverted().transform_path(
                    arrow.get_transform().transform_path(arrow.get_path()))
                _, head_start = [j for j, code in enumerate(path.codes) if code == MplPath.MOVETO]
                shaft = MplPath(path.vertices[:head_start], path.codes[:head_start])
                head = MplPath(path.vertices[head_start:], path.codes[head_start:])
                annotation.remove()
                ax.add_patch(PathPatch(shaft, transform=ax.transData, fill=False,
                                       edgecolor=c, linewidth=lw, linestyle=SHORT_DASH,
                                       capstyle="butt", joinstyle="round", zorder=3,
                                       gid=f"{m}_shaft"))
                ax.add_patch(PathPatch(head, transform=ax.transData, facecolor=c,
                                       edgecolor=c, linewidth=lw, linestyle="-",
                                       capstyle="round", joinstyle="round", zorder=3,
                                       gid=f"{m}_head"))
        ax.plot(p, i, "o", ms=3.1, mfc="white", mec=BLACK, mew=.7, zorder=4)
        ax.plot(q, i, "o", ms=3.4 if ours else 3.1, mfc=c, mec=c, mew=.7, zorder=5)
        drawn.append((m, p, q))
        ax.text(-.03, i, rd.label(m), transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=7, color=c if ours else BLACK, weight="bold" if ours else "normal")
        # rank column: Paused -> Native, in figure inches converted to axes fraction
        rank_color = "tab:red" if rn[m] > rp[m] else "tab:green" if rn[m] < rp[m] else BLACK
        for xin, s, ha in ((2.82, f"{rp[m]}", "right"), (2.90, "→", "center"),
                           (2.98, f"{rn[m]}", "left")):
            ax.text((xin - LEFT) / (RIGHT - LEFT), i, s, transform=ax.get_yaxis_transform(),
                    ha=ha, va="center", fontsize=7, color=rank_color,
                    weight="bold" if ours else "normal")

    # header: legend over the SR axis, rank title over the rank column
    yh = 1 - (TOP * .42) / H
    x0 = LEFT / W
    fig.add_artist(Line2D([x0 + .012], [yh], transform=fig.transFigure, marker="o", ms=3.1,
                          mfc="white", mec=BLACK, mew=.7, ls="none"))
    fig.text(x0 + .032, yh, t["paused"], va="center", fontsize=7)
    xn = x0 + (.27 if lang == "en" else .17)
    fig.add_artist(Line2D([xn], [yh], transform=fig.transFigure, marker="o", ms=3.1,
                          mfc=BLACK, mec=BLACK, mew=.7, ls="none"))
    fig.text(xn + .020, yh, t["native"], va="center", fontsize=7)
    fig.text(2.90 / W, yh, t["rank"], ha="center", va="center", fontsize=7)
    return fig, drawn, rp, rn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--lang", choices=["en", "zh"], default="en")
    ap.add_argument("--line-style", choices=["solid", "fig5"], default="solid",
                    help="Solid connectors (default), or Fig. 5's Base/off dashed styles.")
    ap.add_argument("--output-dir", type=Path, default=HERE)
    a = ap.parse_args()
    require_font(a.font)
    if a.lang == "zh":
        require_font("Microsoft YaHei")
    plot_style = style(a.font, zh=a.lang == "zh") | {
        "text.color": BLACK, "axes.edgecolor": BLACK, "axes.labelcolor": BLACK,
        "xtick.color": BLACK, "ytick.color": BLACK,
    }
    with plt.rc_context(plot_style):
        fig, drawn, rp, rn = draw(a.lang, a.font, a.line_style)
        d = rd.load()
        for m, p, q in drawn:          # plotted values are exactly the JSON values
            assert p == d[m]["paused"][0] and q == d[m]["native"][0]
        stem = "rank_shift" + ("_fig5_lines" if a.line_style == "fig5" else "")
        stem += "_zh" if a.lang == "zh" else ""
        a.output_dir.mkdir(parents=True, exist_ok=True)
        for ext in ("pdf", "svg", "png"):
            output = a.output_dir / f"{stem}.{ext}"
            fig.savefig(output, dpi=300)
            if ext == "svg":
                output.write_text("\n".join(line.rstrip() for line in output.read_text(encoding="utf-8").splitlines()) + "\n", encoding="utf-8")
        plt.close(fig)
    print(f"{stem}: {len(drawn)} methods; rank changes:",
          ", ".join(f"{m} {rp[m]}->{rn[m]}" for m in rd.ORDER if rp[m] != rn[m]))


if __name__ == "__main__":
    main()
