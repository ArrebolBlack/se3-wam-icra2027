"""Three architecture mockups for Fig. 4 (layout study only; tiles cropped from the current figure)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import numpy as np
from PIL import Image

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "text.color": "#1A1A1A",
                     "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic"})
SRC = Image.open("/tmp/otb_hi.png").convert("RGB")
K = SRC.width / 495.0
INK, GREY, LG = "#1A1A1A", "#6E6E6E", "#D6D6D6"
FAM = {"Grasp": "#2859A3", "Place": "#2E8540", "Pass": "#9467BD", "Capture": "#E69F00", "Impact": "#C0263A"}
TASKS = {"Grasp": ["grasp", "t1_belt", "t1_xyz", "t1_so3", "t1_occ"], "Place": ["t2_trans", "t2_se3"],
         "Pass": ["t3_phase", "t3_full"], "Capture": ["t4_sphere", "t4_sphere_tabletop", "t4_slider", "t4_can"],
         "Impact": ["t5_replan"]}
# draft one-line "what it tests" phrases (need author confirmation)
PHRASE = {"Grasp": "Same grasp, five target motions", "Place": "Place into a moving receptacle",
          "Pass": "Thread a rotating wire, no contact", "Capture": "Catch a fast target before a deadline",
          "Impact": "Re-plan after the target is struck"}
SPEED = {"Grasp": "0.03–0.20 m/s", "Place": "0.03–0.06 m/s", "Pass": "2.5–7.5°/s", "Capture": "0.55–1.14 m/s", "Impact": "0.12–0.14 m/s"}
POS = {"grasp": (186, 34), "t1_belt": (249, 34), "t1_xyz": (312, 34), "t1_so3": (375, 34), "t1_occ": (438, 34),
       "t2_trans": (186, 107), "t2_se3": (249, 107), "t3_phase": (312, 107), "t3_full": (375, 107), "t5_replan": (438, 107),
       "t4_sphere": (186, 180), "t4_sphere_tabletop": (249, 180), "t4_slider": (312, 180), "t4_can": (375, 180)}
NAME = {"grasp": "Harmonic", "t1_belt": "Conveyor", "t1_xyz": "Translating", "t1_so3": "Rotating", "t1_occ": "Occluded",
        "t2_trans": "Translating", "t2_se3": "Rotating", "t3_phase": "Passage", "t3_full": "Full passage",
        "t4_sphere": "Ball", "t4_sphere_tabletop": "Tabletop ball", "t4_slider": "Slider", "t4_can": "Can", "t5_replan": "Post-impact"}
TW, TH = 55.0, 43.44107142857142 * 0.80712788
AR = TH / TW
PROT = [(0, "DOMINO", "World pauses", "#C0263A"), (89, "OnTimeBench", "World advances", "#2E8540")]
PAR = 72.14018691588785 / 83.0
# Table 1: (name, paused, native, p95)
T1 = [("FoveaWAM", 90.3, 82.1, 15.1), (r"$\pi_{0.5}$+SE(3)", 76.0, 58.7, 61.2), (r"$\pi_{0.5}$", 66.6, 54.4, 59.6),
      ("DynamicWAM+SE(3)", 64.0, 41.7, 153.3), (r"OpenWAM-$\alpha$", 58.7, 46.1, 151.7), (r"OpenWAM-$\alpha$ (off)", 58.4, 15.8, 466.3),
      ("DynamicVLA", 54.9, 51.1, 97.3), ("PUMA", 53.1, 61.4, 60.6), ("DynamicWAM", 49.6, 41.1, 149.6), ("ACT", 40.6, 41.6, 5.8),
      ("DP", 32.0, 31.9, 68.9)]


def crop(x, y, w, h, inset=0.25):
    return np.asarray(SRC.crop((int((x + inset) * K), int((y + inset) * K), int((x + w - inset) * K), int((y + h - inset) * K))))


class Canvas:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.fig = plt.figure(figsize=(W / 72, H / 72), dpi=300)
        self.ax = self.fig.add_axes([0, 0, 1, 1]); self.ax.set_xlim(0, W); self.ax.set_ylim(H, 0); self.ax.axis("off")

    def text(self, x, y, s, **kw):
        kw.setdefault("va", "baseline"); self.ax.text(x, y, s, **kw)

    def img(self, a, x, y, w, h, z=2):
        self.ax.imshow(a, extent=(x, x + w, y + h, y), interpolation="lanczos", zorder=z)

    def tile(self, t, x, y, w, label=True, fs=6.4):
        h = w * AR
        self.img(crop(*POS[t], TW, TH), x, y, w, h)
        if label:
            self.text(x + w / 2, y + h + 7.0, NAME[t], fontsize=fs, ha="center")
        return h

    def protocol(self, i, x, y, w, head=True, fs=7):
        sx, name, lab, col = PROT[i]
        h = w * PAR
        self.img(crop(sx, 33, 83, 72.14018691588785, inset=0.3), x, y, w, h)
        if head:
            self.text(x + w / 2, y - 2.5, name, fontsize=fs, ha="center", fontweight="bold")
        self.text(x + w / 2, y + h + 7.5, lab, fontsize=fs - 0.3, ha="center", color=col, fontweight="bold")
        return h

    def axes(self, x, y, w, h):
        a = self.fig.add_axes([x / self.W, 1 - (y + h) / self.H, w / self.W, h / self.H]); a.patch.set_alpha(0); return a

    def save(self, path):
        self.fig.savefig(path, dpi=300); plt.close(self.fig)


def dumbbell(cv, x, y, w, h, fs=6.3, show_lat=True):
    D = sorted(T1, key=lambda r: -r[1])
    rk_p = {r[0]: i + 1 for i, r in enumerate(D)}
    rk_n = {r[0]: i + 1 for i, r in enumerate(sorted(D, key=lambda r: -r[2]))}
    lab_w = 62
    ax = cv.axes(x + lab_w, y + 9, w - lab_w - 34, h - 22)
    for i, (n, p, nat, lat) in enumerate(D):
        c = "#D62728" if n == "FoveaWAM" else "#4D4D4D"
        ax.annotate("", xy=(nat, i), xytext=(p, i), arrowprops=dict(arrowstyle="-|>,head_length=0.28,head_width=0.14", lw=0.7, color=c, shrinkA=2, shrinkB=0.4))
        ax.plot(p, i, "o", ms=2.6, mfc="white", mec=c, mew=.6)
        ax.plot(nat, i, "o", ms=2.6, color=c)
        ax.text(-0.02, i, n, transform=ax.get_yaxis_transform(), ha="right", va="center", fontsize=fs, color=c,
                fontweight="bold" if n == "FoveaWAM" else "normal")
        ch = rk_p[n] - rk_n[n]
        ax.text(1.02, i, f"{rk_p[n]}→{rk_n[n]}", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=fs - 0.2,
                color="#1A1A1A" if ch == 0 else ("#2CA02C" if ch > 0 else "#D62728"))
    ax.text(1.02, -1.2, "rank", transform=ax.get_yaxis_transform(), fontsize=fs - 0.4, color=GREY, va="center")
    ax.set_ylim(len(D) - 0.5, -1.6); ax.set_xlim(10, 95); ax.set_yticks([])
    for s in ("left", "right", "top"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_linewidth(.5)
    ax.tick_params(axis="x", labelsize=fs, length=2, width=.5, pad=1.5)
    ax.set_xlabel("Success rate (%)", fontsize=fs, labelpad=1)
    ax.grid(axis="x", color="#EEEEEE", lw=.4); ax.set_axisbelow(True)
    ax.plot([], [], "o", ms=2.6, mfc="white", mec="#4D4D4D", mew=.6, label="World paused")
    ax.plot([], [], "o", ms=2.6, color="#4D4D4D", label="Native latency")
    ax.legend(loc="lower right", bbox_to_anchor=(1.0, 0.95), ncol=2, frameon=False, fontsize=fs, handletextpad=.2, columnspacing=.9, borderaxespad=0)


# ============================================================ Architecture 1: hub and spokes (LIBERO-like)
def arch1(path):
    W, H = 495.0, 290.0
    cv = Canvas(W, H)
    cv.text(0, 8.5, "OnTimeBench", fontsize=9, fontweight="bold")
    cv.text(W, 8.5, "14 tasks  ·  5 families  ·  1,400 held-out test scenes  ·  11,200 demonstrations", fontsize=6.8, color="#555555", ha="right")
    # center
    cx0, cw = 172.0, 151.0
    cv.ax.add_patch(FancyBboxPatch((cx0, 16), cw, 112, boxstyle="round,pad=0,rounding_size=2.5", fc="#F5F5F5", ec="none", zorder=0))
    cv.text(cx0 + cw / 2, 27.5, "The world never pauses", fontsize=7.6, ha="center", fontweight="bold")
    cv.text(cx0 + cw / 2, 36.5, "Physics advances by each policy's own latency", fontsize=6.2, ha="center", color="#555555")
    pw = 69.0
    for i in range(2):
        cv.protocol(i, cx0 + 5 + i * (pw + 3), 50, pw, fs=6.6)
    # cards
    def card(fam, x, y, w, ntile, anchor):
        tw = (w - 8 - (ntile - 1) * 3 - (10 if ntile < len(TASKS[fam]) else 0)) / ntile
        th = tw * AR
        hgt = 11 + th + 14
        cv.ax.add_patch(FancyBboxPatch((x, y), w, hgt, boxstyle="round,pad=0,rounding_size=2.5", fc="white", ec=LG, lw=0.6, zorder=0))
        cv.text(x + 4, y + 8.5, fam, fontsize=7.4, fontweight="bold", color=FAM[fam])
        nt=len(TASKS[fam]); cv.text(x + 4 + len(fam) * 4.15 + 3, y + 8.5, f"{nt} task{"s" if nt>1 else ""} · {SPEED[fam]}", fontsize=6.0, color=GREY)
        for k, t in enumerate(TASKS[fam][:ntile]):
            cv.tile(t, x + 4 + k * (tw + 3), y + 11, tw, label=False)
        if ntile < len(TASKS[fam]):
            cv.text(x + w - 8, y + 11 + th / 2 + 2, "···", fontsize=8, ha="center", color=GREY)
        cv.text(x + 4, y + 11 + th + 9.5, PHRASE[fam], fontsize=6.4, color=INK)
        ax_, ay_ = (x + w, y + hgt / 2) if anchor == "R" else (x, y + hgt / 2)
        if anchor == "U":
            cv.ax.plot([x + w / 2, x + w / 2], [y, 128], color="#BDBDBD", lw=0.6, zorder=0)
            cv.ax.plot([x + w / 2], [y], "o", ms=2.6, color=FAM[fam], zorder=3)
            return hgt
        tx_ = cx0 if anchor == "R" else cx0 + cw
        cv.ax.plot([ax_, tx_], [ay_, min(max(ay_, 30), 120)], color="#BDBDBD", lw=0.6, zorder=0)
        cv.ax.plot([ax_], [ay_], "o", ms=2.6, color=FAM[fam], zorder=3)
        return hgt
    y = 16
    for fam in ("Grasp", "Place"):
        y += card(fam, 0, y, 165, 2, "R") + 6
    y = 16
    for fam in ("Capture", "Pass"):
        y += card(fam, 330, y, 165, 2, "L") + 6
    card("Impact", cx0 + 30, 134, cw - 60, 1, "U")
    # bottom: what it reveals (data instead of icons)
    yb = 214
    cv.ax.plot([0, W], [yb - 6, yb - 6], color=LG, lw=0.6)
    cv.text(0, yb + 2, "What it measures", fontsize=7.6, fontweight="bold")
    boxes = [("Native latency", "every method at its own p95"), ("Added delay", "0–150 ms on top of native"),
             ("Paused vs native", "does pausing change rankings?"), ("Motion input", "does SE(3) history still help?")]
    bw = (W - 3 * 6) / 4
    for i, (t, s) in enumerate(boxes):
        bx = i * (bw + 6)
        cv.ax.add_patch(FancyBboxPatch((bx, yb + 7), bw, 60, boxstyle="round,pad=0,rounding_size=2.5", fc="white", ec=LG, lw=0.6))
        cv.text(bx + 4, yb + 16, t, fontsize=7, fontweight="bold")
        cv.text(bx + 4, yb + 24.5, s, fontsize=6.1, color="#555555")
        a = cv.axes(bx + (28 if i == 0 else 14), yb + 30, bw - (34 if i == 0 else 20), 29)
        for sp in ("top", "right"):
            a.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            a.spines[sp].set_linewidth(.4)
        a.tick_params(labelsize=5.2, length=1.5, width=.4, pad=1)
        if i == 0:
            names = ["Ours", "ACT", "DP", "PUMA", "OWα", "DWAM"]; vals = [15.1, 5.8, 68.9, 60.6, 151.7, 149.6]
            a.barh(range(6), vals, color=["#D62728"] + ["#9E9E9E"] * 5, height=.6); a.set_xscale("log"); a.invert_yaxis()
            a.set_yticks(range(6)); a.set_yticklabels(names); a.set_xlabel("p95 ms", fontsize=5.2, labelpad=0)
        elif i == 1:
            X = [0, 50, 100, 150]
            a.plot(X, [82.1, 72.5, 53.7, 34.1], color="#D62728", lw=1); a.plot(X, [61.4, 53.2, 36.4, 31.1], color="#FF7F0E", lw=.8)
            a.set_xticks(X); a.set_ylim(20, 90); a.set_ylabel("SR", fontsize=5.2, labelpad=0)
        elif i == 2:
            for n, p, nn, _ in T1:
                c = "#D62728" if n == "FoveaWAM" else "#9E9E9E"
                a.plot([0, 1], [p, nn], color=c, lw=.7 if n != "FoveaWAM" else 1.1, marker="o", ms=1.6)
            a.set_xticks([0, 1]); a.set_xticklabels(["paused", "native"]); a.set_xlim(-.25, 1.25)
        else:
            g = [("π0.5", 66.6, 76.0, 54.4, 58.7), ("DWAM", 49.6, 64.0, 41.1, 41.7)]
            for j, (n, pb, ps, nb, ns) in enumerate(g):
                a.bar(j * 3 + 0, ps - pb, color="#BDBDBD", width=.8); a.bar(j * 3 + 1, ns - nb, color="#4D4D4D", width=.8)
            a.set_xticks([0.5, 3.5]); a.set_xticklabels(["π0.5", "DynWAM"]); a.axhline(0, color="#999999", lw=.4)
            a.set_ylabel("+SE(3) gain", fontsize=5.2, labelpad=0)
    cv.save(path)


# ============================================================ Architecture 2: argument chain (a) mechanism (b) consequence (c) coverage
def arch2(path):
    W = 495.0
    gap = 3.0
    tw = (W - 6 * gap) / 7; th = tw * AR
    top_h = 112.0
    H = top_h + 2 * (12.5 + th + 9.5) + 26
    cv = Canvas(W, H)
    cv.text(0, 8.5, "(a) The world never pauses", fontsize=8.5, fontweight="bold")
    pw = 76.0
    for i in range(2):
        cv.protocol(i, i * (pw + 6), 22, pw)
    bx = 2 * pw + 6 + 20
    cv.text(bx, 8.5, "(b) Pausing the world misranks methods", fontsize=8.5, fontweight="bold")
    dumbbell(cv, bx, 11, W - bx, top_h - 6)
    y0 = top_h + 6
    cv.text(0, y0 + 8.5, "(c) Fourteen tasks in five families", fontsize=8.5, fontweight="bold")
    cv.text(W, y0 + 8.5, "1,400 held-out test scenes  ·  11,200 demonstrations", fontsize=6.8, color="#555555", ha="right")
    rows = [["Grasp", "Place"], ["Pass", "Capture", "Impact"]]
    y = y0 + 13
    for row in rows:
        col = 0
        for fam in row:
            n = len(TASKS[fam])
            x0 = col * (tw + gap); x1 = (col + n) * (tw + gap) - gap
            cv.ax.add_patch(Rectangle((x0, y + 9.3), x1 - x0, 1.4, color=FAM[fam], lw=0))
            cv.text(x0, y + 7.3, fam, fontsize=7.3, fontweight="bold", color=FAM[fam])
            if n >= 2:
                cv.text(x0 + len(fam) * 4.1 + 3, y + 7.3, PHRASE[fam], fontsize=6.1, color="#555555")
            for t in TASKS[fam]:
                cv.tile(t, col * (tw + gap), y + 12.5, tw, fs=6.3)
                col += 1
        y += 12.5 + th + 10.5
    cv.save(path)


# ============================================================ Architecture 3: protocol band + families as columns
def arch3(path):
    W = 495.0
    cols = {"Grasp": 3, "Place": 1, "Pass": 1, "Capture": 2, "Impact": 1}
    fam_gap, gap = 9.0, 3.0
    ncol = sum(cols.values())
    tw = (W - (len(cols) - 1) * fam_gap - (ncol - len(cols)) * gap) / ncol
    th = tw * AR
    band_h = 96.0
    H = band_h + 37 + 2 * (th + 10) + 4
    cv = Canvas(W, H)
    # band
    cv.ax.add_patch(FancyBboxPatch((0, 0), W, band_h - 8, boxstyle="round,pad=0,rounding_size=2.5", fc="#F5F5F5", ec="none", zorder=0))
    cv.text(6, 12, "(a) The world never pauses", fontsize=8.5, fontweight="bold")
    cv.text(6, 23, "Physics advances by each policy's own", fontsize=6.6, color="#333333")
    cv.text(6, 31, "measured latency. One executor, one clock.", fontsize=6.6, color="#333333")
    cv.text(6, 47, "14 tasks · 5 families", fontsize=6.6, color="#555555")
    cv.text(6, 55, "1,400 held-out test scenes", fontsize=6.6, color="#555555")
    cv.text(6, 63, "11,200 demonstrations", fontsize=6.6, color="#555555")
    pw = 70.0
    for i in range(2):
        cv.protocol(i, 140 + i * (pw + 5), 12, pw, fs=6.6)
    dumbbell(cv, 300, 13, W - 302, band_h - 19, fs=5.6)
    cv.text(306, 12, "(b) Paused vs native", fontsize=7.6, fontweight="bold")
    # columns
    y0 = band_h + 2
    x = 0.0
    for fam, nc in cols.items():
        w = nc * tw + (nc - 1) * gap
        SH = {"Grasp": "Same grasp, five target motions", "Place": "Moving receptacle", "Pass": "Rotating wire",
              "Capture": "Fast target, hard deadline", "Impact": "Re-plan after a hit"}
        cv.text(x, y0 + 8, fam, fontsize=7.6, fontweight="bold", color=FAM[fam])
        cv.ax.add_patch(Rectangle((x, y0 + 10.8), w, 1.4, color=FAM[fam], lw=0))
        cv.text(x, y0 + 19.0, SH[fam], fontsize=5.9, color="#333333")
        cv.text(x, y0 + 26.0, SPEED[fam], fontsize=5.6, color=GREY)
        for k, t in enumerate(TASKS[fam]):
            r, c = divmod(k, nc)
            cv.tile(t, x + c * (tw + gap), y0 + 30 + r * (th + 10), tw, fs=5.9)
        x += w + fam_gap
    cv.save(path)


arch1("/home/claude/fig4_arch1.png")
arch2("/home/claude/fig4_arch2.png")
arch3("/home/claude/fig4_arch3.png")
