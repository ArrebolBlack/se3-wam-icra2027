"""Paused-vs-native ranking panel. Variant A: method colours (Fig. 5). Variant B': grey baselines, FoveaWAM tab:red,
colour only on changed ranks. Data: Table 1 (results/realtime_c/table1-20261104.json)."""
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "mathtext.fontset": "custom",
                     "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic",
                     "axes.linewidth": .55, "xtick.major.width": .5, "xtick.major.size": 2.2,
                     "xtick.labelsize": 7, "pdf.fonttype": 42, "text.color": "#181818"})
MC = json.load(open("/mnt/user-data/uploads/se3-wam-icra2027/figures/method_colors.json"))["methods"]
INK, GREY, BASE = "#181818", "#7F7F7F", "#6E6E6E"
UP, DOWN = "#2CA02C", "#D62728"
T1 = [("FoveaWAM", "FoveaWAM", 90.3, 82.1), (r"$\pi_{0.5}$+SE(3)", "π0.5+SE(3)", 76.0, 58.7),
      (r"$\pi_{0.5}$", "π0.5", 66.6, 54.4), ("DynamicWAM+SE(3)", "DynamicWAM+SE(3)", 64.0, 41.7),
      (r"OpenWAM-$\alpha$", "OpenWAM-α", 58.7, 46.1), (r"OpenWAM-$\alpha$ (off)", "OpenWAM-α (off)", 58.4, 15.8),
      ("DynamicVLA", "DynamicVLA", 54.9, 51.1), ("PUMA", "PUMA", 53.1, 61.4),
      ("DynamicWAM", "DynamicWAM", 49.6, 41.1), ("ACT", "ACT", 40.6, 41.6), ("DP", "DP", 32.0, 31.9)]
rk_p = {r[0]: i + 1 for i, r in enumerate(sorted(T1, key=lambda r: -r[2]))}
rk_n = {r[0]: i + 1 for i, r in enumerate(sorted(T1, key=lambda r: -r[3]))}


def draw(variant, out):
    fig = plt.figure(figsize=(3.25, 1.95), dpi=300)
    ax = fig.add_axes([0.335, 0.17, 0.47, 0.72])
    for i, (n, ck, p, nat) in enumerate(T1):
        ours = ck == "FoveaWAM"
        if variant == "A":
            c = MC[ck]
        else:
            c = MC["FoveaWAM"] if ours else BASE
        ax.annotate("", xy=(nat, i), xytext=(p, i), arrowprops=dict(arrowstyle="-|>,head_length=0.32,head_width=0.15",
                    lw=.75, color=c, shrinkA=2.2, shrinkB=0.3))
        ax.plot(p, i, "o", ms=3.0, mfc="white", mec=c if variant == "B" else GREY, mew=.65, zorder=4)
        ax.plot(nat, i, "o", ms=3.2, color=c, zorder=5)
        ax.text(-0.03, i, n, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=6.8,
                color=MC["FoveaWAM"] if ours else INK, weight="bold" if ours else "normal")
        d = rk_p[n] - rk_n[n]
        col = INK if d == 0 else (UP if d > 0 else DOWN)
        w = "normal" if d == 0 else "bold"
        tr = ax.get_yaxis_transform()
        ax.text(1.13, i, f"{rk_p[n]}", transform=tr, ha="right", va="center", fontsize=6.8, color=GREY)
        ax.text(1.155, i, "→", transform=tr, ha="left", va="center", fontsize=6.0, color=GREY)
        ax.text(1.30, i, f"{rk_n[n]}", transform=tr, ha="right", va="center", fontsize=6.8, color=col, weight=w)
    ax.text(1.215, -1.25, "Rank", transform=ax.get_yaxis_transform(), ha="center", va="center", fontsize=6.8)
    ax.set_ylim(len(T1) - 0.5, -1.75); ax.set_xlim(10, 95); ax.set_yticks([])
    ax.spines[["left", "right", "top"]].set_visible(False)
    ax.set_xticks([20, 40, 60, 80]); ax.set_xlabel("Success rate (%)", labelpad=2)
    ax.grid(axis="x", color="#E5E5E5", lw=.35); ax.set_axisbelow(True)
    kc = GREY if variant == "A" else BASE
    ax.plot(14, -1.25, "o", ms=3.0, mfc="white", mec=kc, mew=.65, clip_on=False)
    ax.text(17.5, -1.25, "Paused", va="center", fontsize=6.8)
    ax.plot(46, -1.25, "o", ms=3.2, color=BASE, clip_on=False)
    ax.text(49.5, -1.25, "Native", va="center", fontsize=6.8)
    fig.savefig(f"{out}.png", dpi=300); fig.savefig(f"{out}.pdf")


draw("A", "/home/claude/rank_A")
draw("B", "/home/claude/rank_B")
from PIL import Image, ImageDraw, ImageFont
a, b = Image.open("/home/claude/rank_A.png"), Image.open("/home/claude/rank_B.png")
pad = 70
c = Image.new("RGB", (a.width * 2 + 60, a.height + pad), "white"); c.paste(a, (0, pad)); c.paste(b, (a.width + 60, pad))
d = ImageDraw.Draw(c); f = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 34)
d.text((20, 15), "A  Method colours (Fig. 5)", fill="#181818", font=f)
d.text((a.width + 80, 15), "B'  Grey + FoveaWAM red", fill="#181818", font=f)
c.save("/home/claude/rank_AB.png")
print("ok")
