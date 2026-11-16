"""Candidate sub-panels for Fig. 4: (4) target displacement during inference, (5) protocol timeline."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "text.color": "#1A1A1A",
                     "axes.linewidth": .5, "xtick.major.width": .5, "ytick.major.width": .5,
                     "xtick.major.size": 2, "ytick.major.size": 2, "axes.edgecolor": "#1A1A1A",
                     "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic"})
FAM = {"Grasp": "#2859A3", "Place": "#2E8540", "Capture": "#E69F00", "Impact": "#C0263A"}
SPEED = {"Capture": (0.55, 1.14), "Grasp": (0.03, 0.20), "Impact": (0.12, 0.14), "Place": (0.03, 0.06)}
LAT = [("ACT", 5.8), ("Ours", 15.1), (r"$\pi_{0.5}$ / PUMA", 60.1), ("DynamicVLA", 97.3), (r"OpenWAM-$\alpha$", 151.7)]


# ---------------------------------------------------------------- (4) displacement during inference
def displacement(path):
    fig, ax = plt.subplots(figsize=(2.75, 1.95), dpi=300)
    L = np.linspace(0, 200, 200)
    for fam in ("Capture", "Grasp", "Impact", "Place"):
        lo, hi = SPEED[fam]
        ax.fill_between(L, lo * L / 10, hi * L / 10, color=FAM[fam], alpha=.28, lw=0)
        ax.plot(L, hi * L / 10, color=FAM[fam], lw=.8)
        ax.plot(L, lo * L / 10, color=FAM[fam], lw=.5, alpha=.8)
    for fam, yl, yd in (("Capture", 17.0, 16.9), ("Grasp", 5.6, 0.12 * 200 / 10), ("Impact", 3.2, 0.13 * 200 / 10), ("Place", 0.9, 0.045 * 200 / 10)):
        c = "#B37C00" if fam == "Capture" else FAM[fam]
        ax.annotate(fam, xy=(200, yd), xytext=(207, yl), fontsize=6.4, color=c, fontweight="bold", va="center",
                    annotation_clip=False, arrowprops=dict(arrowstyle="-", lw=.4, color=c, shrinkA=0, shrinkB=0))
    for name, l in LAT:
        c = "#D62728" if name == "Ours" else "#8C8C8C"
        ax.axvline(l, color=c, lw=.6 if name != "Ours" else .9, ls=(0, (2, 1.5)), zorder=0)
        ax.text(l + 1.5, 24.2, name, rotation=90, fontsize=5.6, color=c, va="top", ha="left",
                fontweight="bold" if name == "Ours" else "normal")
    ax.axhspan(0, 2, color="#EEEEEE", zorder=-1, lw=0)
    ax.text(4, 0.55, "< 2 cm", fontsize=5.6, color="#6E6E6E")
    ax.set_xlim(0, 200); ax.set_ylim(0, 24.5)
    ax.set_xticks([0, 50, 100, 150, 200]); ax.set_yticks([0, 5, 10, 15, 20])
    ax.set_xlabel("Inference latency (ms)", labelpad=1.5); ax.set_ylabel("Target moves (cm)", labelpad=1.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.set_title("Target displacement during inference", fontsize=7.2, fontweight="bold", loc="left", pad=4)
    fig.subplots_adjust(left=0.15, right=0.80, top=0.88, bottom=0.17)
    fig.savefig(path, dpi=300); plt.close(fig)


# ---------------------------------------------------------------- (5) protocol timeline (VLASH / StreamingVLA style)
def timeline(path):
    DT = 50.0           # control period (ms)
    L = 152.0           # example latency (OpenWAM-alpha p95 151.7 ms)
    H = 8               # commands per chunk
    k = math.ceil(L / DT)
    W_ms = 560.0
    fig = plt.figure(figsize=(4.6, 2.25), dpi=300)
    ax = fig.add_axes([0.13, 0.04, 0.70, 0.90]); ax.set_xlim(-10, W_ms); ax.set_ylim(12.4, -0.4); ax.axis("off")
    OBS, INF, ACT, ACT_L, SKIP = "#2859A3", "#BDBDBD", "#E69F00", "#F7DDA0", "#FFFFFF"
    cw, ch = DT * 0.86, 0.62

    def chunk(x0, y, n, colors, hatch=None, edge="#B37C00"):
        for i in range(n):
            c = colors[i] if isinstance(colors, list) else colors
            ax.add_patch(Rectangle((x0 + i * DT + (DT - cw) / 2, y - ch / 2), cw, ch, fc=c, ec=edge if c != SKIP else "#9E9E9E",
                                   lw=.5, hatch=hatch if c == SKIP else None, zorder=3))
            if c == SKIP:
                xx = x0 + i * DT + DT / 2
                ax.plot([xx - 7, xx + 7], [y - .2, y + .2], color="#9E9E9E", lw=.6, zorder=4)
                ax.plot([xx - 7, xx + 7], [y + .2, y - .2], color="#9E9E9E", lw=.6, zorder=4)

    def label(y, s, bold=True, color="#1A1A1A"):
        ax.text(-16, y, s, ha="right", va="center", fontsize=6.6, fontweight="bold" if bold else "normal", color=color)

    # ---------------- row block 1: world paused
    ax.text(-10, 0.2, "World paused (default DOMINO evaluator)", fontsize=7.2, fontweight="bold", color="#C0263A", va="center")
    y1, y2, y3 = 1.4, 2.3, 3.2
    label(y1, "Policy")
    ax.add_patch(Rectangle((0, y1 - .3), 10, .6, fc=OBS, lw=0))
    ax.add_patch(Rectangle((10, y1 - .3), L, .6, fc=INF, lw=0, zorder=2))
    ax.text(10 + L / 2, y1, f"inference {L:.0f} ms", ha="center", va="center", fontsize=5.8, color="#1A1A1A")
    label(y2, "Physics")
    ax.plot([0, 10], [y2, y2], color="#1A1A1A", lw=1.2)
    ax.add_patch(Rectangle((10, y2 - .22), L, .44, fc="white", ec="#9E9E9E", lw=.5, hatch="////", zorder=2))
    ax.text(10 + L / 2, y2 + 0.62, "clock stopped", ha="center", va="center", fontsize=5.6, color="#6E6E6E")
    ax.plot([10 + L, W_ms], [y2, y2], color="#1A1A1A", lw=1.2)
    label(y3, "Executed")
    chunk(10 + L, y3, H, ACT)
    ax.text(10 + L + H * DT + 6, y3, "from command 1", va="center", fontsize=5.8, color="#6E6E6E")

    # ---------------- row block 2: native latency
    off = 4.6
    ax.text(-10, off + 0.2, "OnTimeBench: native latency", fontsize=7.2, fontweight="bold", color="#2E8540", va="center")
    y1, y2, y3, y4 = off + 1.8, off + 2.7, off + 3.6, off + 4.5
    label(y1, "Policy")
    ax.add_patch(Rectangle((0, y1 - .3), 10, .6, fc=OBS, lw=0))
    ax.add_patch(Rectangle((10, y1 - .3), L, .6, fc=INF, lw=0, zorder=2))
    ax.text(10 + L / 2, y1, f"inference {L:.0f} ms", ha="center", va="center", fontsize=5.8)
    label(y2, "Physics")
    ax.plot([0, W_ms], [y2, y2], color="#1A1A1A", lw=1.2)
    for t in np.arange(0, W_ms, DT):
        ax.plot([t, t], [y2 - .14, y2 + .14], color="#1A1A1A", lw=.5)
    ax.text(W_ms + 6, y2, "ticks: 50 ms", va="center", fontsize=5.6, color="#6E6E6E")
    label(y3, "New chunk")
    cols = [SKIP] * k + [ACT] * (H - k)
    chunk(0, y3, H, cols)
    label(y4, "Executed")
    chunk(0, y4, k, ACT_L, edge="#D9B25C")
    chunk(k * DT, y4, H - k, ACT)
    ax.text(H * DT + 6, y4, "previous chunk runs until takeover", va="center", fontsize=5.6, color="#6E6E6E")
    ax.annotate("", xy=(k * DT, y4 + 0.45), xytext=(k * DT, y1 - 0.6),
                arrowprops=dict(arrowstyle="-|>,head_length=0.3,head_width=0.15", lw=.6, color="#1A1A1A", ls=(0, (2, 1.5))))
    ax.text(k * DT + 5, y1 - 0.75, f"new chunk takes over at the first boundary after inference (k = {k})", fontsize=5.8, color="#1A1A1A", va="center")
    ax.text(H * DT + 6, y3, f"first {k} commands overdue, skipped", va="center", fontsize=5.6, color="#6E6E6E")
    # legend
    ly = 11.8
    items = [(OBS, "observe"), (INF, "inference"), (ACT, "command executed"), (ACT_L, "previous chunk"), (SKIP, "skipped")]
    x = 0
    for c, t in items:
        ax.add_patch(Rectangle((x, ly - .22), 18, .44, fc=c, ec="#9E9E9E" if c == SKIP else "none", lw=.5, zorder=3))
        ax.text(x + 22, ly, t, va="center", fontsize=5.8)
        x += 22 + len(t) * 7.2 + 14
    fig.savefig(path, dpi=300); plt.close(fig)


displacement("/home/claude/panel_displacement.png")
timeline("/home/claude/panel_timeline.png")
