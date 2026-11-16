"""Single-column candidate: (a) paused vs native ranking, (b) target displacement during inference. Real Table 1 / task-table numbers."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "text.color": "#1A1A1A", "axes.linewidth": .5,
                     "xtick.major.width": .5, "ytick.major.width": .5, "xtick.major.size": 2, "ytick.major.size": 2,
                     "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic"})
RED, GREY, DG = "#D62728", "#7F7F7F", "#4D4D4D"
T1 = [("FoveaWAM", 90.3, 82.1, 15.1), (r"$\pi_{0.5}$+SE(3)", 76.0, 58.7, 61.2), (r"$\pi_{0.5}$", 66.6, 54.4, 59.6),
      ("DynamicWAM+SE(3)", 64.0, 41.7, 153.3), (r"OpenWAM-$\alpha$", 58.7, 46.1, 151.7), (r"OpenWAM-$\alpha$ (off)", 58.4, 15.8, 466.3),
      ("DynamicVLA", 54.9, 51.1, 97.3), ("PUMA", 53.1, 61.4, 60.6), ("DynamicWAM", 49.6, 41.1, 149.6), ("ACT", 40.6, 41.6, 5.8),
      ("DP", 32.0, 31.9, 68.9)]
FAMC = {"Capture": "#FF7F0E", "Grasp": "#1F77B4", "Impact": "#8C564B", "Place": "#2CA02C"}   # tab10; Impact uses brown here because red is FoveaWAM
SPEED = {"Capture": (0.55, 1.14), "Grasp": (0.03, 0.20), "Impact": (0.12, 0.14), "Place": (0.03, 0.06)}

fig = plt.figure(figsize=(3.25, 3.75), dpi=300)
# ---------------- (a)
ax = fig.add_axes([0.355, 0.50, 0.375, 0.405])
D = sorted(T1, key=lambda r: -r[1])
rk_p = {r[0]: i + 1 for i, r in enumerate(D)}
rk_n = {r[0]: i + 1 for i, r in enumerate(sorted(D, key=lambda r: -r[2]))}
for i, (n, p, nat, lat) in enumerate(D):
    c = RED if n == "FoveaWAM" else DG
    ax.annotate("", xy=(nat, i), xytext=(p, i), arrowprops=dict(arrowstyle="-|>,head_length=0.3,head_width=0.15", lw=.75, color=c, shrinkA=2.1, shrinkB=0.4))
    ax.plot(p, i, "o", ms=2.8, mfc="white", mec=c, mew=.65)
    ax.plot(nat, i, "o", ms=2.8, color=c)
    ax.text(-0.03, i, n, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.3, color=c,
            fontweight="bold" if n == "FoveaWAM" else "normal")
    ch = rk_p[n] - rk_n[n]
    ax.text(1.16, i, f"{lat:.0f}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.0, color=GREY)
    ax.text(1.35, i, f"{rk_p[n]}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.0, color=GREY)
    ax.text(1.38, i, "→", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=5.6, color=GREY)
    ax.text(1.555, i, f"{rk_n[n]}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.0,
            color="#1A1A1A" if ch == 0 else (RED if ch < 0 else "#2CA02C"), fontweight="bold" if ch != 0 else "normal")
ax.text(1.10, -1.25, "p95 ms", transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=6.0, color=GREY)
ax.text(1.45, -1.25, "Rank", transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=6.0, color=GREY)
ax.set_ylim(len(D) - 0.5, -1.7); ax.set_xlim(10, 95); ax.set_yticks([])
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)
ax.set_xticks([20, 40, 60, 80]); ax.tick_params(labelsize=6.3, pad=1.5)
ax.set_xlabel("Success rate (%)", fontsize=6.6, labelpad=1)
ax.grid(axis="x", color="#EEEEEE", lw=.4); ax.set_axisbelow(True)
ax.plot([], [], "o", ms=2.8, mfc="white", mec=DG, mew=.65, label="World paused")
ax.plot([], [], "o", ms=2.8, color=DG, label="Native latency")
fig.legend(loc="upper left", bbox_to_anchor=(0.012, 0.955), ncol=2, frameon=False, fontsize=6.3, handletextpad=.2, columnspacing=1.0, borderaxespad=0)
fig.text(0.012, 0.985, "(a) Pausing the world changes the ranking", fontsize=7.6, fontweight="bold", va="top")

# ---------------- (b)
bx = fig.add_axes([0.13, 0.085, 0.62, 0.285])
L = np.linspace(0, 200, 200)
for fam in ("Capture", "Grasp", "Impact", "Place"):
    lo, hi = SPEED[fam]
    bx.fill_between(L, lo * L / 10, hi * L / 10, color=FAMC[fam], alpha=.22, lw=0)
    bx.plot(L, hi * L / 10, color=FAMC[fam], lw=.8); bx.plot(L, lo * L / 10, color=FAMC[fam], lw=.45)
for fam, yl, yd in (("Capture", 17.0, 16.9), ("Grasp", 6.6, 0.115 * 200 / 10), ("Impact", 3.7, 0.13 * 200 / 10), ("Place", 0.8, 0.045 * 200 / 10)):
    bx.annotate(fam, xy=(200, yd), xytext=(207, yl), fontsize=6.3, color=FAMC[fam], fontweight="bold", va="center",
                annotation_clip=False, arrowprops=dict(arrowstyle="-", lw=.4, color=FAMC[fam], shrinkA=0, shrinkB=0))
for l in (5.8, 15.1, 59.6, 60.6, 61.2, 68.9, 97.3, 149.6, 151.7, 153.3):
    ours = abs(l - 15.1) < 1e-6
    bx.axvline(l, color=RED if ours else "#B0B0B0", lw=.9 if ours else .5, ls=(0, (2, 1.5)), zorder=0)
for name, l in [("ACT", 5.8), ("FoveaWAM", 15.1), (r"$\pi_{0.5}$, PUMA", 60.1), ("DP", 68.9), ("DynamicVLA", 97.3), (r"OpenWAM-$\alpha$, DWAM", 151.5)]:
    ours = name == "FoveaWAM"
    bx.text(l + 1.8, 24.3, name, rotation=90, fontsize=5.4, color=RED if ours else GREY, va="top", ha="left", fontweight="bold" if ours else "normal")
bx.set_xlim(0, 200); bx.set_ylim(0, 24.5); bx.set_xticks([0, 50, 100, 150, 200]); bx.set_yticks([0, 10, 20])
bx.tick_params(labelsize=6.3, pad=1.5)
bx.set_xlabel("Inference latency (ms)", fontsize=6.6, labelpad=1); bx.set_ylabel("Target moves (cm)", fontsize=6.6, labelpad=1.5)
for s in ("top", "right"):
    bx.spines[s].set_visible(False)
fig.text(0.012, 0.425, "(b) How far the target moves during inference", fontsize=7.6, fontweight="bold", va="top")
fig.savefig("/home/claude/fig_rank_disp.png", dpi=300)
fig.savefig("/home/claude/fig_rank_disp.pdf")
