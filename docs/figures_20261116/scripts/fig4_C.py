"""Direction-C mockup for Fig. 4: task gallery as the main body, protocol + speed strip below.
Tiles are cropped from the current (2026-11-16 palette) figure; layout only, not final assets."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch
import numpy as np
from PIL import Image

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "text.color": "#1A1A1A"})
SRC = Image.open("/tmp/otb_hi.png").convert("RGB")
K = SRC.width / 495.0
def crop(x, y, w, h, inset=0.0):
    return np.asarray(SRC.crop((int((x + inset) * K), int((y + inset) * K), int((x + w - inset) * K), int((y + h - inset) * K))))

FAM = {"Grasp": "#2859A3", "Place": "#2E8540", "Pass": "#9467BD", "Capture": "#E69F00", "Impact": "#C0263A"}
POS = {"grasp": (186, 34), "t1_belt": (249, 34), "t1_xyz": (312, 34), "t1_so3": (375, 34), "t1_occ": (438, 34),
       "t2_trans": (186, 107), "t2_se3": (249, 107), "t3_phase": (312, 107), "t3_full": (375, 107), "t5_replan": (438, 107),
       "t4_sphere": (186, 180), "t4_sphere_tabletop": (249, 180), "t4_slider": (312, 180), "t4_can": (375, 180)}
TW, TH = 55.0, 43.44107142857142 * 0.80712788
NAME = {"grasp": "Harmonic", "t1_belt": "Conveyor", "t1_xyz": "Translating", "t1_so3": "Rotating", "t1_occ": "Occluded",
        "t2_trans": "Translating", "t2_se3": "Rotating", "t3_phase": "Passage", "t3_full": "Full passage",
        "t4_sphere": "Ball", "t4_sphere_tabletop": "Tabletop ball", "t4_slider": "Slider", "t4_can": "Can", "t5_replan": "Post-impact"}
ROWS = [[("Grasp", ["grasp", "t1_belt", "t1_xyz", "t1_so3", "t1_occ"]), ("Place", ["t2_trans", "t2_se3"])],
        [("Pass", ["t3_phase", "t3_full"]), ("Capture", ["t4_sphere", "t4_sphere_tabletop", "t4_slider", "t4_can"]), ("Impact", ["t5_replan"])]]
SPEED = {"grasp": (0.03, 0.20), "t1_belt": (0.04, 0.10), "t1_xyz": (0.04, 0.15), "t1_so3": (0.04, 0.15), "t1_occ": (0.04, 0.10),
         "t2_trans": (0.03, 0.06), "t2_se3": (0.03, 0.06), "t4_sphere": (0.67, 1.14), "t4_sphere_tabletop": (0.59, 1.03),
         "t4_slider": (0.55, 1.12), "t4_can": (0.59, 0.97), "t5_replan": (0.12, 0.14)}
FAMOF = {t: f for row in ROWS for f, ts in row for t in ts}

W = 495.0
GAP = 3.0
TILE_W = (W - 6 * GAP) / 7
TILE_H = TILE_W * TH / TW
H = 247.0
fig = plt.figure(figsize=(W / 72, H / 72), dpi=300)
root = fig.add_axes([0, 0, 1, 1]); root.set_xlim(0, W); root.set_ylim(H, 0); root.axis("off")

def text(x, y, s, **kw):
    kw.setdefault("va", "baseline"); root.text(x, y, s, **kw)

# ---------------- (a) gallery
text(0, 8.5, "(a) Fourteen dynamic tasks", fontsize=8.5, fontweight="bold")
text(W, 8.5, "5 families  ·  1,400 held-out test scenes  ·  11,200 demonstrations", fontsize=7, color="#555555", ha="right")
row_y = [14.0, 14.0 + TILE_H + 26.5]
for r, row in enumerate(ROWS):
    col = 0
    y0 = row_y[r]
    for fam, tasks in row:
        x0 = col * (TILE_W + GAP); x1 = (col + len(tasks)) * (TILE_W + GAP) - GAP
        root.add_patch(Rectangle((x0, y0 + 9.2), x1 - x0, 1.6, color=FAM[fam], lw=0))
        text(x0, y0 + 7.2, fam, fontsize=7.5, fontweight="bold", color=FAM[fam])
        text(x0 + len(fam) * 4.25 + 3, y0 + 7.2, f"{len(tasks)}", fontsize=7, color="#777777")
        for t in tasks:
            x = col * (TILE_W + GAP); y = y0 + 12.5
            px, py = POS[t]
            img = crop(px, py, TW, TH, inset=0.25)
            root.imshow(img, extent=(x, x + TILE_W, y + TILE_H, y), interpolation="lanczos", zorder=2)
            text(x + TILE_W / 2, y + TILE_H + 8.0, NAME[t], fontsize=6.8, ha="center")
            col += 1
gal_end = row_y[1] + 12.5 + TILE_H + 9.5

# ---------------- (b) protocol strip
y_b = gal_end + 9.0
text(0, y_b, "(b) Real-time evaluation", fontsize=8.5, fontweight="bold")
PW = 72.0; PH = PW * 72.14018691588785 / 83.0
py0 = y_b + 13.0
for i, (sx, lab, colr, head) in enumerate([(0, "World pauses", "#C0263A", "DOMINO"), (89, "World advances", "#2E8540", "OnTimeBench")]):
    x = i * (PW + 8)
    img = crop(sx, 33, 83, 72.14018691588785, inset=0.3)
    root.imshow(img, extent=(x, x + PW, py0 + PH, py0), interpolation="lanczos", zorder=2)
    text(x + PW / 2, py0 - 2.5, head, fontsize=7.2, ha="center", fontweight="bold")
    text(x + PW / 2, py0 + PH + 8.0, lab, fontsize=6.8, ha="center", color=colr, fontweight="bold")

# ---------------- (c) target speed
cx0 = 2 * PW + 8 + 16
text(cx0, y_b, "(c) What varies across tasks", fontsize=8.5, fontweight="bold")
ax = fig.add_axes([0, 0, 1, 1])
ax_l, ax_r = cx0 + 34, W - 92
ax_t, ax_b = y_b + 6, py0 + PH - 8
ax.set_position([ax_l / W, 1 - ax_b / H, (ax_r - ax_l) / W, (ax_b - ax_t) / H])
ax.set_xscale("log"); ax.set_xlim(0.025, 1.4)
lanes = ["Grasp", "Place", "Impact", "Capture"]
centers=[]; yy=0.0
for li, fam in enumerate(lanes):
    ts = [t for t in SPEED if FAMOF[t] == fam]
    ys=[]
    for k, t in enumerate(ts):
        lo, hi = SPEED[t]
        ax.plot([lo, hi], [yy, yy], color=FAM[fam], lw=1.5, solid_capstyle="round"); ys.append(yy); yy += 1.0
    centers.append(np.mean(ys)); yy += 0.9
ax.set_ylim(yy - 0.6, -0.8)
ax.set_yticks(centers); ax.set_yticklabels(lanes, fontsize=6.8)
for lab, tk in zip(ax.get_yticklabels(), lanes):
    lab.set_color(FAM[tk]); lab.set_fontweight("bold")
ax.set_xticks([0.03, 0.1, 0.3, 1.0]); ax.set_xticklabels(["0.03", "0.1", "0.3", "1"], fontsize=6.5)
ax.minorticks_off()
ax.set_xlabel("Target speed (m/s, log scale)", fontsize=6.8, labelpad=1.5)
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
ax.tick_params(axis="y", length=0, pad=2); ax.tick_params(axis="x", length=2, width=0.5, pad=1.5)
ax.spines["bottom"].set_linewidth(0.5)
ax.grid(axis="x", color="#E6E6E6", lw=0.4); ax.set_axisbelow(True)
ax.patch.set_alpha(0)
nx = W - 84
text(nx, ax_t + 8, "Pass: wire turns", fontsize=6.6, color=FAM["Pass"], fontweight="bold")
text(nx, ax_t + 16, "2.5–7.5°/s", fontsize=6.6, color=FAM["Pass"])
text(nx, ax_t + 30, "Rotation matters:", fontsize=6.6, color="#1A1A1A", fontweight="bold")
text(nx, ax_t + 38, "7 of 14 tasks", fontsize=6.6, color="#555555")
text(nx, ax_t + 52, "Clearance or driver:", fontsize=6.6, color="#1A1A1A", fontweight="bold")
text(nx, ax_t + 60, "9 of 14 tasks", fontsize=6.6, color="#555555")

fig.savefig("/home/claude/fig4_C_mockup.png", dpi=300)
fig.savefig("/home/claude/fig4_C_mockup.pdf")
print(TILE_W, TILE_H, H)
