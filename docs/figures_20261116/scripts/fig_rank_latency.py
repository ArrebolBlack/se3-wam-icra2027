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
ax = fig.add_axes([0.355, 0.50, 0.50, 0.405])
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
    ax.text(1.03, i, f"{rk_p[n]}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.0, color=GREY)
    ax.text(1.065, i, "→", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=5.6, color=GREY)
    ax.text(1.20, i, f"{rk_n[n]}", transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.0,
            color="#1A1A1A" if ch == 0 else (RED if ch < 0 else "#2CA02C"), fontweight="bold" if ch != 0 else "normal")
ax.text(1.115, -1.25, "Rank", transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=6.0, color=GREY)
ax.set_ylim(len(D) - 0.5, -1.7); ax.set_xlim(10, 95); ax.set_yticks([])
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)
ax.set_xticks([20, 40, 60, 80]); ax.tick_params(labelsize=6.3, pad=1.5)
ax.set_xlabel("Success rate (%)", fontsize=6.6, labelpad=1)
ax.grid(axis="x", color="#EEEEEE", lw=.4); ax.set_axisbelow(True)
ax.plot([], [], "o", ms=2.8, mfc="white", mec=DG, mew=.65, label="World paused")
ax.plot([], [], "o", ms=2.8, color=DG, label="Native latency")
ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 0.955), ncol=2, frameon=False, fontsize=6.3, handletextpad=.2, columnspacing=1.0, borderaxespad=0)
fig.text(0.012, 0.985, "(a) Pausing the world changes the ranking", fontsize=7.6, fontweight="bold", va="top")

# ---------------- (b) SR change vs latency (measured)
bx = fig.add_axes([0.15, 0.085, 0.80, 0.285])
pts = [("ACT", 5.8, 40.6, 41.6), ("FoveaWAM", 15.1, 90.3, 82.1), (r"$\pi_{0.5}$", 59.6, 66.6, 54.4), (r"$\pi_{0.5}$+SE(3)", 61.2, 76.0, 58.7),
       ("PUMA", 60.6, 53.1, 61.4), ("DP", 68.9, 32.0, 31.9), ("DynamicVLA", 97.3, 54.9, 51.1), ("DynamicWAM", 149.6, 49.6, 41.1),
       (r"OpenWAM-$\alpha$", 151.7, 58.7, 46.1), ("DynamicWAM+SE(3)", 153.3, 64.0, 41.7), (r"OpenWAM-$\alpha$ (off)", 466.3, 58.4, 15.8)]
xs = np.array([p[1] for p in pts]); ys = np.array([p[3] - p[2] for p in pts])
k = np.polyfit(np.log10(xs), ys, 1); xx = np.logspace(np.log10(4.5), np.log10(600), 50)
bx.plot(xx, np.polyval(k, np.log10(xx)), color="#BDBDBD", lw=.8, zorder=0)
bx.axhline(0, color="#999999", lw=.5, zorder=0)
bx.plot([151.7, 466.3], [46.1 - 58.7, 15.8 - 58.4], color="#1F77B4", lw=.7, ls=(0, (2, 1.5)), zorder=1)
bx.text(330, -27.5, "same policy,\n3× latency", fontsize=5.6, color="#1F77B4", ha="left", va="center")
POSL = {"ACT": (5.8, 5.0, "center"), "FoveaWAM": (15.1, -14.0, "center"), r"$\pi_{0.5}$": (52, -12.2, "right"),
        r"$\pi_{0.5}$+SE(3)": (54, -17.3, "right"), "PUMA": (60.6, 12.0, "center"), "DP": (63, 3.0, "right"),
        "DynamicVLA": (106, -1.2, "left"), "DynamicWAM": (164, -8.0, "left"), r"OpenWAM-$\alpha$": (140, -15.0, "right"),
        "DynamicWAM+SE(3)": (165, -22.3, "left"), r"OpenWAM-$\alpha$ (off)": (425, -42.6, "right")}
for (n, l, p, nat), y in zip(pts, ys):
    c = RED if n == "FoveaWAM" else DG
    bx.plot(l, y, "o", ms=3.0, color=c, zorder=3)
    tx, ty, ha = POSL[n]
    bx.text(tx, ty, n, fontsize=5.5, ha=ha, va="center", color=c, fontweight="bold" if n == "FoveaWAM" else "normal")
bx.set_xscale("log"); bx.set_xlim(4.5, 600); bx.set_ylim(-46, 15)
bx.set_xticks([5, 10, 20, 50, 100, 200, 500]); bx.set_xticklabels(["5", "10", "20", "50", "100", "200", "500"]); bx.minorticks_off()
bx.tick_params(labelsize=6.3, pad=1.5)
bx.set_xlabel("p95 time-to-action (ms, log scale)", fontsize=6.6, labelpad=1)
bx.set_ylabel("Native − paused SR (pts)", fontsize=6.6, labelpad=1.5)
for s_ in ("top", "right"):
    bx.spines[s_].set_visible(False)
bx.text(0.02, 0.04, "Spearman ρ = −0.66 (n = 11)", transform=bx.transAxes, ha="left", va="bottom", fontsize=5.6, color=GREY)
fig.text(0.012, 0.425, "(b) Slower policies lose more when the world moves", fontsize=7.6, fontweight="bold", va="top")
fig.savefig("/home/claude/fig_rank_latency.png", dpi=300)
fig.savefig("/home/claude/fig_rank_latency.pdf")
