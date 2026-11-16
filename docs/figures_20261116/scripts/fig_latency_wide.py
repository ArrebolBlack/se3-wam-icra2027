"""Full-width mockup: Fig. 5 (a)(b) + paused-vs-native ranking (c) + target displacement (d).
Real data: latency-five-point-20261104.json / supp_latency.tex (a,b), Table 1 (c), task speed ranges (d)."""
import sys, math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = Path("/mnt/user-data/uploads/se3-wam-icra2027")
sys.path.insert(0, str(REPO / "figures/latency"))
import plot_latency as PL  # user's own Fig. 5 script: data loading + line styles

table = PL.load(REPO / "tables/supp_latency.tex")
data = PL.load_results(REPO / "results/realtime_c/latency-five-point-20261104.json", table)
MC = PL.METHOD_COLORS

STYLE = {**PL.STYLE, "font.family": "Liberation Sans", "mathtext.rm": "Liberation Sans",
         "mathtext.it": "Liberation Sans:italic", "mathtext.bf": "Liberation Sans:bold"}
plt.rcParams.update(STYLE)
INK, GREY = "#181818", "#7F7F7F"

W, H = 6.875, 1.90
fig = plt.figure(figsize=(W, H), dpi=300)
def ax_in(x, y, w, h):  # inches -> figure fraction
    return fig.add_axes([x / W, y / H, w / W, h / H])

Y0, PH = 0.80, 0.86        # bottom/height of plot boxes for (a)(b) (legend underneath)
TY = 1.82                  # title baseline
def title(x, letter, text):
    fig.text(x / W, TY / H, f"({letter})", fontsize=8, weight="bold", va="center")
    fig.text((x + 0.2) / W, TY / H, text, fontsize=8, weight="bold", va="center")

# ---------------- (a)(b): Fig. 5 curves, unchanged encoding
axa = ax_in(0.37, Y0, 1.11, PH)
axb = ax_in(1.58, Y0, 1.11, PH)
for ax, group in zip((axa, axb), PL.GROUPS):
    for m in [*group, "ours"]:
        pts = [p for p in data[m] if p["extra_latency_ms"] in PL.PLOT_XS]
        x = np.array([p["extra_latency_ms"] for p in pts]); y = np.array([p["sr_percent"] for p in pts])
        ci = np.array([p["sr_scene_bootstrap95"] for p in pts]); s = PL.line_style(m)
        z = 5 if m == "ours" else 3
        ax.errorbar(x, y, yerr=np.array([y - ci[:, 0], ci[:, 1] - y]), fmt="none", ecolor=s["color"],
                    elinewidth=.5, capsize=1.1, capthick=.5, zorder=z)
        ax.plot(x, y, zorder=z + .2, **s)
    ax.set(xlim=(-8, 158), ylim=(0, 100), xticks=PL.PLOT_XS, yticks=np.arange(0, 101, 20))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E5E5E5", lw=.35); ax.set_axisbelow(True)
    ax.set_xlabel("Added latency (ms)", labelpad=2)
axb.set_yticklabels([])
axa.set_ylabel("Success rate (%)", labelpad=2)
title(0.02, "a", "Policies"); title(1.52, "b", "SE(3) history")

def sample(m, x, y, w=0.20):
    fig.add_artist(Line2D([(x - w / 2) / W, x / W, (x + w / 2) / W], [y / H] * 3, transform=fig.transFigure,
                          markevery=[1], clip_on=False, **PL.line_style(m)))
def key(m, x, y, label, **kw):
    sample(m, x, y); fig.text((x + 0.13) / W, y / H, label, va="center", fontsize=6.6, **kw)
r1, r2, r3 = 0.36, 0.22, 0.08
def sample(m, x, y, w=0.17):
    fig.add_artist(Line2D([(x - w / 2) / W, x / W, (x + w / 2) / W], [y / H] * 3, transform=fig.transFigure,
                          markevery=[1], clip_on=False, **PL.line_style(m)))
def key(m, x, y, label, **kw):
    sample(m, x, y); fig.text((x + 0.11) / W, y / H, label, va="center", fontsize=6.6, **kw)
key("ours", 0.44, r1, "FoveaWAM", weight="bold", color=MC["FoveaWAM"])
key("act", 1.20, r1, "ACT"); key("dp", 1.68, r1, "DP"); key("dynamicvla", 2.06, r1, "DynamicVLA")
key("puma", 0.44, r2, "PUMA"); key("openwam_official", 1.02, r2, r"OpenWAM-$\alpha$"); key("openwam", 1.82, r2, r"OpenWAM-$\alpha$ (off)")
fig.text(0.36 / W, r3 / H, "Base / +SE(3):", va="center", fontsize=6.6)
sample("pi05", 1.12, r3, .13); sample("pi05_se3", 1.27, r3, .13)
fig.text(1.37 / W, r3 / H, r"$\pi_{0.5}$", va="center", fontsize=6.6)
sample("dynamicwam", 1.74, r3, .13); sample("dynamicwam_se3", 1.89, r3, .13)
fig.text(1.99 / W, r3 / H, "DynamicWAM", va="center", fontsize=6.6)

# ---------------- (c): paused vs native, Table 1
T1 = [("FoveaWAM", "FoveaWAM", 90.3, 82.1, 15.1), (r"$\pi_{0.5}$+SE(3)", "π0.5+SE(3)", 76.0, 58.7, 61.2),
      (r"$\pi_{0.5}$", "π0.5", 66.6, 54.4, 59.6), ("DynamicWAM+SE(3)", "DynamicWAM+SE(3)", 64.0, 41.7, 153.3),
      (r"OpenWAM-$\alpha$", "OpenWAM-α", 58.7, 46.1, 151.7), (r"OpenWAM-$\alpha$ (off)", "OpenWAM-α (off)", 58.4, 15.8, 466.3),
      ("DynamicVLA", "DynamicVLA", 54.9, 51.1, 97.3), ("PUMA", "PUMA", 53.1, 61.4, 60.6),
      ("DynamicWAM", "DynamicWAM", 49.6, 41.1, 149.6), ("ACT", "ACT", 40.6, 41.6, 5.8), ("DP", "DP", 32.0, 31.9, 68.9)]
rk_p = {r[0]: i + 1 for i, r in enumerate(sorted(T1, key=lambda r: -r[2]))}
rk_n = {r[0]: i + 1 for i, r in enumerate(sorted(T1, key=lambda r: -r[3]))}
axc = ax_in(3.73, 0.30, 0.92, 1.40)
for i, (n, ck, p, nat, lat) in enumerate(T1):
    c = MC[ck]; ours = n == "FoveaWAM"
    axc.annotate("", xy=(nat, i), xytext=(p, i), arrowprops=dict(arrowstyle="-|>,head_length=0.28,head_width=0.14",
                 lw=.7, color=c, shrinkA=2.0, shrinkB=0.3))
    axc.plot(p, i, "o", ms=2.6, mfc="white", mec=GREY, mew=.6, zorder=4)
    axc.plot(nat, i, "o", ms=2.8, color=c, zorder=5)
    axc.text(-0.03, i, n, transform=axc.get_yaxis_transform(), ha="right", va="center", fontsize=6.3,
             color=MC["FoveaWAM"] if ours else INK, weight="bold" if ours else "normal")
    d = rk_p[n] - rk_n[n]
    axc.text(1.16, i, f"{rk_p[n]}", transform=axc.get_yaxis_transform(), ha="right", va="center", fontsize=6.0, color=GREY)
    axc.text(1.185, i, "→", transform=axc.get_yaxis_transform(), ha="left", va="center", fontsize=5.4, color=GREY)
    axc.text(1.40, i, f"{rk_n[n]}", transform=axc.get_yaxis_transform(), ha="right", va="center", fontsize=6.0,
             color=INK if d == 0 else ("#2CA02C" if d > 0 else "#D62728"), weight="normal" if d == 0 else "bold")
axc.text(1.26, -1.15, "Rank", transform=axc.get_yaxis_transform(), ha="center", va="center", fontsize=6.0, color=GREY)
axc.set_ylim(len(T1) - 0.5, -1.6); axc.set_xlim(10, 95); axc.set_yticks([])
axc.spines[["left", "right", "top"]].set_visible(False)
axc.set_xticks([20, 40, 60, 80]); axc.set_xlabel("Success rate (%)", labelpad=2)
axc.grid(axis="x", color="#E5E5E5", lw=.35); axc.set_axisbelow(True)
axc.plot(13, -1.15, "o", ms=2.6, mfc="white", mec=GREY, mew=.6, clip_on=False)
axc.text(16, -1.15, "Paused", va="center", fontsize=6.3)
axc.plot(50, -1.15, "o", ms=2.8, color=INK, clip_on=False)
axc.text(53, -1.15, "Native", va="center", fontsize=6.3)
title(2.80, "c", "Paused vs. native")

# ---------------- (d): how far the target moves during inference
axd = ax_in(5.44, 0.30, 0.98, 1.40)
L = np.linspace(0, 160, 300)
axd.fill_between(L, 0.55 * L / 10, 1.14 * L / 10, color="#BDBDBD", lw=0)                  # Capture
axd.fill_between(L, 0.03 * L / 10, 0.20 * L / 10, color="#E3E3E3", lw=0)                  # Grasp
axd.fill_between(L, 0.12 * L / 10, 0.14 * L / 10, color="#8C8C8C", lw=0)                  # Impact
axd.fill_between(L, 0.03 * L / 10, 0.06 * L / 10, color="#A8A8A8", lw=0)                  # Place
for v in (0.55, 1.14, 0.20):
    axd.plot(L, v * L / 10, color="#6E6E6E", lw=.35)
YM = 6.0
for fam, y, yd in (("Grasp", 3.25, 3.2), ("Impact", 2.15, 2.08), ("Place", 0.75, 0.72)):
    axd.annotate(fam, xy=(160, yd), xytext=(166, y), fontsize=6.3, va="center", color=INK, annotation_clip=False,
                 arrowprops=dict(arrowstyle="-", lw=.35, color="#6E6E6E", shrinkA=0, shrinkB=0))
axd.text(36, 5.35, "Capture", fontsize=6.3, color=INK, ha="left", va="center", zorder=7)
VL = [("ACT", 5.8), ("FoveaWAM", 15.1), ("π0.5", 59.6), ("PUMA", 60.6), ("π0.5+SE(3)", 61.2), ("DP", 68.9),
      ("DynamicVLA", 97.3), ("DynamicWAM", 149.6), ("OpenWAM-α", 151.7), ("DynamicWAM+SE(3)", 153.3)]
for n, l in VL:
    ours = n == "FoveaWAM"
    axd.axvline(l, color=MC[n], lw=1.0 if ours else .6, ls="-" if ours else (0, (2.2, 1.4)), zorder=3)
axd.text(17.5, YM - 0.15, "FoveaWAM", rotation=90, fontsize=5.8, color=MC["FoveaWAM"], weight="bold", va="top", ha="left", zorder=6)
axd.set_xlim(0, 160); axd.set_ylim(0, YM); axd.set_xticks([0, 50, 100, 150]); axd.set_yticks([0, 2, 4, 6])
axd.spines[["top", "right"]].set_visible(False)
axd.set_xlabel("p95 latency (ms)", labelpad=2); axd.set_ylabel("Displacement (cm)", labelpad=2)
title(5.00, "d", "Target motion during inference")

out = Path("/home/claude/fig_latency_wide")
fig.savefig(f"{out}.png", dpi=300); fig.savefig(f"{out}.pdf")
print("ok")
