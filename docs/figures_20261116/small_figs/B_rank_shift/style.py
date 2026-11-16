"""Shared Matplotlib style for small_figs/B, matching figures/latency/plot_latency.py (Fig. 5)."""
from __future__ import annotations

import matplotlib
from matplotlib import font_manager

matplotlib.use("Agg")

GRID = "#E5E5E5"
INK = "#181818"
MUTED = "#6E6E6E"


def require_font(name: str) -> None:
    names = {f.name for f in font_manager.fontManager.ttflist}
    if name not in names:
        raise SystemExit(f"Font '{name}' is not installed; pass --font with an installed family "
                         f"(Arial on Windows, Liberation Sans on Linux). No silent fallback.")


def style(font: str, zh: bool = False) -> dict:
    fams = [font, "Microsoft YaHei"] if zh else [font]
    return {
        "font.family": fams, "font.size": 7,
        "mathtext.fontset": "custom", "mathtext.rm": font,
        "mathtext.it": f"{font}:italic", "mathtext.bf": f"{font}:bold",
        "mathtext.default": "rm", "text.color": INK,
        "axes.edgecolor": INK, "axes.labelcolor": INK,
        "axes.linewidth": .55, "axes.labelsize": 7,
        "xtick.color": INK, "ytick.color": INK,
        "xtick.major.size": 2.2, "ytick.major.size": 2.2,
        "xtick.major.width": .5, "ytick.major.width": .5,
        "xtick.major.pad": 2.5, "ytick.major.pad": 2.5,
        "xtick.labelsize": 7, "ytick.labelsize": 7,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.facecolor": "white", "figure.facecolor": "white",
        "path.simplify": False,
    }


def repel(ys, gap, lo=-1e9, hi=1e9):
    """Place labels at target heights `ys` with at least `gap` between neighbours.

    Clusters of overlapping labels are spread evenly around their mean target. Returns list in input order.
    """
    order = sorted(range(len(ys)), key=lambda i: -ys[i])
    clusters = [[i] for i in order]

    def centre(c):
        return sum(ys[i] for i in c) / len(c)

    def span(c):
        top = min(max(centre(c) + gap * (len(c) - 1) / 2, lo + gap * (len(c) - 1)), hi)
        return top, top - gap * (len(c) - 1)

    merged = True
    while merged:
        merged = False
        for k in range(len(clusters) - 1):
            _, bottom = span(clusters[k])
            top_next, _ = span(clusters[k + 1])
            if bottom - top_next < gap - 1e-9:
                clusters[k] = clusters[k] + clusters.pop(k + 1)
                merged = True
                break
    pos = [0.0] * len(ys)
    for c in clusters:
        top, _ = span(c)
        for j, i in enumerate(c):
            pos[i] = top - j * gap
    return pos
