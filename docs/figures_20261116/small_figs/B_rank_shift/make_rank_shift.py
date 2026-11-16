"""Paused vs. Native SR and ranking on OnTimeBench (small_figs/B, candidate C, final).

Rows follow the Paused ranking. Hollow grey circle: SR with the world paused during inference;
filled circle in the method colour: SR at native latency; the arrow points from Paused to Native.
Ranks are ordinal positions of the one-decimal SRs in Table 1 (no ties at that precision).

Usage:
  python make_rank_shift.py                      # Arial (Windows), English
  python make_rank_shift.py --font "Liberation Sans" --lang en
  python make_rank_shift.py --lang zh            # Arial + Microsoft YaHei
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

import rank_data as rd
from style import GRID, INK, MUTED, require_font, style

HERE = Path(__file__).resolve().parent
W, H = 3.25, 1.86                     # inches; single CVPR column
PAUSED_EDGE = "#8C8C8C"
LEFT, RIGHT = 1.10, 2.56              # SR axis extent (inches from the left edge)
BOTTOM, TOP = 0.315, 0.20             # inches below / above the row block
XLIM = (10, 95)
MIN_ARROW = 4.5                       # SR points; shorter changes show markers only (arrow would be hidden)

TEXT = {
    "en": dict(paused="Paused", native="Native", xlabel="Success rate (%)", rank="Rank"),
    "zh": dict(paused="暂停", native="原生", xlabel="成功率（%）", rank="排名"),
}


def ranks(values: dict[str, float]) -> dict[str, int]:
    order = sorted(values, key=lambda m: -values[m])
    if len({values[m] for m in order}) != len(order):
        raise ValueError("Tied one-decimal SRs; ordinal ranks would be ambiguous.")
    return {m: i + 1 for i, m in enumerate(order)}


def draw(lang: str, font: str):
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
    ax.grid(axis="x", color=GRID, lw=.35)
    ax.set_axisbelow(True)
    ax.set_xlabel(t["xlabel"], labelpad=2.5)

    drawn = []
    for i, m in enumerate(rows):
        c = rd.color(m)
        ours = m == "se3_wam"
        p, q = d[m]["paused"][0], d[m]["native"][0]
        lw = 1.2 if ours else .85
        if abs(q - p) >= MIN_ARROW:
            ax.annotate("", xy=(q, i), xytext=(p, i), zorder=3,
                        arrowprops=dict(arrowstyle="-|>,head_length=0.32,head_width=0.16",
                                        color=c, lw=lw, shrinkA=2.4, shrinkB=2.7))
        ax.plot(p, i, "o", ms=3.1, mfc="white", mec=PAUSED_EDGE, mew=.7, zorder=4)
        ax.plot(q, i, "o", ms=3.4 if ours else 3.1, mfc=c, mec=c, mew=.7, zorder=5)
        drawn.append((m, p, q))
        ax.text(-.03, i, rd.label(m), transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=7, color=c if ours else INK, weight="bold" if ours else "normal")
        # rank column: Paused -> Native, in figure inches converted to axes fraction
        for xin, s, ha, col in ((2.82, f"{rp[m]}", "right", MUTED), (2.90, "→", "center", MUTED),
                                (2.98, f"{rn[m]}", "left", INK)):
            ax.text((xin - LEFT) / (RIGHT - LEFT), i, s, transform=ax.get_yaxis_transform(),
                    ha=ha, va="center", fontsize=7, color=col,
                    weight="bold" if ours else "normal")

    # header: legend over the SR axis, rank title over the rank column
    yh = 1 - (TOP * .42) / H
    x0 = LEFT / W
    fig.add_artist(Line2D([x0 + .012], [yh], transform=fig.transFigure, marker="o", ms=3.1,
                          mfc="white", mec=PAUSED_EDGE, mew=.7, ls="none"))
    fig.text(x0 + .032, yh, t["paused"], va="center", fontsize=7)
    xn = x0 + (.27 if lang == "en" else .17)
    fig.add_artist(Line2D([xn], [yh], transform=fig.transFigure, marker="o", ms=3.1,
                          mfc=MUTED, mec=MUTED, mew=.7, ls="none"))
    fig.text(xn + .020, yh, t["native"], va="center", fontsize=7)
    fig.text(2.90 / W, yh, t["rank"], ha="center", va="center", fontsize=7)
    return fig, drawn, rp, rn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--font", default="Arial")
    ap.add_argument("--lang", choices=["en", "zh"], default="en")
    ap.add_argument("--output-dir", type=Path, default=HERE)
    a = ap.parse_args()
    require_font(a.font)
    if a.lang == "zh":
        require_font("Microsoft YaHei")
    with plt.rc_context(style(a.font, zh=a.lang == "zh")):
        fig, drawn, rp, rn = draw(a.lang, a.font)
        d = rd.load()
        for m, p, q in drawn:          # plotted values are exactly the JSON values
            assert p == d[m]["paused"][0] and q == d[m]["native"][0]
        stem = "rank_shift" + ("_zh" if a.lang == "zh" else "")
        a.output_dir.mkdir(parents=True, exist_ok=True)
        for ext in ("pdf", "svg", "png"):
            fig.savefig(a.output_dir / f"{stem}.{ext}", dpi=300)
        plt.close(fig)
    print(f"{stem}: {len(drawn)} methods; rank changes:",
          ", ".join(f"{m} {rp[m]}->{rn[m]}" for m in rd.ORDER if rp[m] != rn[m]))


if __name__ == "__main__":
    main()
