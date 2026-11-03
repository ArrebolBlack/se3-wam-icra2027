"""Fig. 2 — SE(3)-WAM architecture (v3, 2026-10-29).

Reading order: inputs (bottom) -> tokens -> one shared backbone -> outputs (top).
Columns are aligned: every head sits directly above the tokens it reads
(flow head over the patch tokens, pose head over the summary tokens, velocity
head over the action tokens). The training-only region is one dashed box.

All scene pixels come from the recorded Dynamic-14 t1_belt episode used in
Fig. 4 (Blender render, same tick). Geometry overlays are GT labels from
assets/labels.npz, not model predictions; the EEF path is recorded expert states.

Rebuild:  python figures/Fig2/build_fig2.py
Outputs:  fig2_se3wam.pdf / .svg / .png  (6.875 in wide)
"""
from pathlib import Path
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon, Circle, FancyArrowPatch, Arc
from PIL import Image

OUT = Path(__file__).resolve().parent
ASSETS = OUT / "assets"
A = dict(np.load(ASSETS / "labels.npz"))
BEAUTY = np.asarray(Image.open(ASSETS / "rgb_blender.png").convert("RGB"))
DEPTH = np.asarray(Image.open(ASSETS / "depth.png").convert("RGB"))

# ------------------------------------------------------------------ style
_avail = {f.name for f in font_manager.fontManager.ttflist}
FONT = next(f for f in ["Arial", "Liberation Sans", "Helvetica", "DejaVu Sans"] if f in _avail)
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": [FONT], "font.size": 6.5,
    "mathtext.fontset": "custom", "mathtext.rm": FONT, "mathtext.it": f"{FONT}:italic",
    "mathtext.bf": f"{FONT}:bold",
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
})
# semantic palette (preamble.tex): obs/history, prediction, action, neutral
C = dict(obs="#0072B2", obs_mid="#8DBEDF", obs_fill="#E3EFF8",
         pred="#E69F00", pred_dark="#A86F00", pred_light="#F2C66B", pred_fill="#FFF8EA",
         act="#7B61A8", act_mid="#BFB0D9", act_fill="#F1EDF7",
         ink="#222222", muted="#666666", line="#9AA3AA", faint="#E6E9EC", gray="#8C8C8C",
         white="#FFFFFF", band="#F3F5F7")

W, H = 6.875, 2.46
fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W); ax.set_ylim(0, H); ax.set_aspect("equal"); ax.set_axis_off()


def T(x, y, s, size=6.5, color=None, bold=False, ha="center", va="center", z=10, **k):
    ax.text(x, y, s, fontsize=size, color=color or C["ink"], fontweight="bold" if bold else "normal",
            ha=ha, va=va, zorder=z, **k)


def box(x, y, w, h, fc, ec="none", lw=0.6, r=0.03, ls="-", z=2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def arrow(p0, p1, color, lw=0.8, ms=5, ls="-", z=6, style="-|>"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle=style, mutation_scale=ms, lw=lw, color=color,
                                 linestyle=ls, shrinkA=0, shrinkB=0, zorder=z))


def tokens(cx, y, n, ec, fc, cell=0.072, gap=0.022, h=0.075, z=5):
    w = n * cell + (n - 1) * gap
    for i in range(n):
        ax.add_patch(Rectangle((cx - w / 2 + i * (cell + gap), y), cell, h, fc=fc, ec=ec, lw=0.55, zorder=z))
    return cx - w / 2, cx + w / 2


# ------------------------------------------------------------------ camera helpers
def project(points):
    """World points -> pixel coords of the 1024x1024 Blender render (same rule as export)."""
    cam = A["world_from_camera_cv"]
    p = (np.asarray(points) - cam[:3, 3]) @ cam[:3, :3]
    q = p @ A["camera_intrinsics"].T
    return (q[..., :2] / q[..., 2, None] + .5) * (1024 / 224) - .5


def panel(img, crop, x, y, w, fade=0.0, z=3, frame=True):
    """Place crop (u0, v0, u1, v1) of img at (x, y) [bottom-left, inches] with width w.
    Returns a mapping from render pixels (u, v) to figure inches."""
    u0, v0, u1, v1 = crop
    sub = img[v0:v1, u0:u1].astype(float)
    if fade:
        sub = sub * (1 - fade) + 255 * fade
    h = w * (v1 - v0) / (u1 - u0)
    ax.imshow(sub.astype(np.uint8), extent=(x, x + w, y, y + h), zorder=z, interpolation="lanczos")
    if frame:
        ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=C["line"], lw=0.5, zorder=z + 0.5))
    s = w / (u1 - u0)

    def to(uv):
        uv = np.atleast_2d(uv)
        return np.c_[x + (uv[:, 0] - u0) * s, y + h - (uv[:, 1] - v0) * s]
    return to, h


def axes_glyphs(to, poses, color, L, lw=0.8, ms=3.2, z=8, halo=True):
    """Draw projected SE(3) frames (x, y, z axes) at recorded poses."""
    from scipy.spatial.transform import Rotation
    for pose in poses:
        p, R = pose[:3], Rotation.from_quat(pose[3:]).as_matrix()
        o = to(project(p))[0]
        for j in range(3):
            e = to(project(p + R[:, j] * L))[0]
            if halo:
                ax.plot(*zip(o, e), color="white", lw=lw + 1.0, zorder=z - 0.1, solid_capstyle="round")
            arrow(tuple(o), tuple(e), color, lw=lw, ms=ms, z=z)
        ax.add_patch(Circle(o, 0.009, fc=color, ec="white", lw=0.3, zorder=z + 0.2))


def gripper(cx, cy, s, color, lw=0.9, alpha=1.0):
    """Parallel-jaw gripper silhouette: wrist, palm and two fingers (filled)."""
    parts = [Rectangle((cx - 0.08 * s, cy + 0.55 * s), 0.16 * s, 0.35 * s),      # wrist
             Rectangle((cx - 0.45 * s, cy + 0.42 * s), 0.90 * s, 0.14 * s),      # palm
             Rectangle((cx - 0.42 * s, cy), 0.14 * s, 0.43 * s),                 # left finger
             Rectangle((cx + 0.28 * s, cy), 0.14 * s, 0.43 * s)]                 # right finger
    for p in parts:
        p.set(fc=color, ec="none", alpha=alpha, zorder=6)
        ax.add_patch(p)


def snowflake(cx, cy, r, color, lw=0.5):
    for a in (0, np.pi / 3, 2 * np.pi / 3):
        d = r * np.array([np.cos(a), np.sin(a)])
        ax.plot([cx - d[0], cx + d[0]], [cy - d[1], cy + d[1]], color=color, lw=lw, zorder=11)


# crops in render pixels
FULL = (0, 0, 1024, 1024)                    # whole agent view: the 14x14 grid spans it
ZOOM = (336, 500, 556, 620)                  # target neighbourhood, 220 x 120 px
ACTZ = (320, 420, 540, 640)                  # gripper + target, 220 x 220 px

# ------------------------------------------------------------------ geometry of the layout
Y_TOK = 0.80                                 # token row (bottom edge)
Y_B0, Y_B1 = 1.00, 1.33                      # backbone band
COL = dict(patch=0.80, target=2.02, robot=2.98, summary=3.98, action=5.30)

# ================================================================== inputs (bottom)
IMG_Y, IMG = 0.15, 0.52                      # bottom edge and size of the input thumbnails
# RGB and depth -> patch tokens
xr, xd = COL["patch"] - 0.58, COL["patch"] + 0.06
panel(BEAUTY, FULL, xr, IMG_Y, IMG)
panel(np.asarray(Image.fromarray(DEPTH).resize((1024, 1024), Image.NEAREST)), FULL, xd, IMG_Y, IMG)
T(xr + IMG / 2, 0.075, "RGB", color=C["obs"], bold=True)
T(xd + IMG / 2, 0.075, "depth", color=C["obs"], bold=True)
T(xr + IMG / 2 + 0.03, 0.715, "MAE", size=5.4, color=C["obs"], ha="left")
snowflake(xr + IMG / 2 + 0.23, 0.715, 0.02, C["obs"], lw=0.5)
T(xd + IMG / 2 + 0.03, 0.715, "XYZ, 3D RoPE", size=5.4, color=C["obs"], ha="left")
for xc, lab in [(xr + IMG / 2, "frozen MAE"), (xd + IMG / 2, "patch XYZ")]:
    arrow((xc, IMG_Y + IMG + 0.01), (xc, Y_TOK - 0.005), C["obs"], lw=0.7, ms=4)

# target SE(3) history on the zoomed view (blue axes, recorded poses -350..0 ms)
zw = 0.80
to_h, zh = panel(BEAUTY, ZOOM, COL["target"] - zw / 2, IMG_Y, zw)
hist = A["history_pose_world_xyzw"]
o = to_h(project(hist[:, :3]))
ax.plot(o[:, 0], o[:, 1], color=C["obs"], lw=0.6, zorder=7, ls=(0, (1.2, 0.9)))
for p in o:
    ax.add_patch(Circle(p, 0.008, fc=C["obs"], ec="white", lw=0.3, zorder=8))
axes_glyphs(to_h, [hist[0], hist[-1]], C["obs"], L=0.02, lw=0.7, ms=2.8)
T(COL["target"], 0.075, "target SE(3) history", color=C["obs"], bold=True)
arrow((COL["target"], IMG_Y + zh + 0.01), (COL["target"], Y_TOK - 0.005), C["obs"], lw=0.7, ms=4)

# robot EEF history (8 states; drawn as an icon, no image)
for k, a in enumerate([0.25, 0.5, 1.0]):
    gripper(COL["robot"] - 0.22 + 0.22 * k, 0.26 + 0.02 * k, 0.17, C["obs"], alpha=a)
ax.plot([COL["robot"] - 0.22, COL["robot"] + 0.22], [0.25, 0.29], color=C["obs"], lw=0.5, ls=(0, (1.2, 1)), zorder=5)
T(COL["robot"], 0.075, "robot EEF history", color=C["obs"], bold=True)
arrow((COL["robot"], 0.52), (COL["robot"], Y_TOK - 0.005), C["obs"], lw=0.7, ms=4)

# summary tokens: learned, no input
T(COL["summary"], 0.40, "learned\nqueries", color=C["muted"], linespacing=1.0)
T(COL["summary"], 0.075, "summary", color=C["muted"], bold=True)

# action: Gaussian-noise chunk + flow time u
rng = np.random.default_rng(0)
noise = (rng.random((10, 16)) * 90 + 130).astype(np.uint8)
ax.imshow(noise, cmap="gray", vmin=0, vmax=255, extent=(COL["action"] - 0.40, COL["action"] + 0.40, 0.30, 0.48),
          zorder=3, interpolation="nearest")
ax.add_patch(Rectangle((COL["action"] - 0.40, 0.30), 0.80, 0.18, fc="none", ec=C["act"], lw=0.5, zorder=4))
T(COL["action"], 0.225, "+ flow time $u$", size=5.6, color=C["act"])
T(COL["action"], 0.075, "noisy action chunk", color=C["act"], bold=True)
arrow((COL["action"], 0.49), (COL["action"], Y_TOK - 0.005), C["act"], lw=0.7, ms=4)

# ================================================================== tokens
tok_y = Y_TOK
tokens(COL["patch"], tok_y, 10, C["obs"], C["obs_mid"])
T(COL["patch"] + 0.52, tok_y + 0.038, "…", color=C["obs"], ha="left")
tokens(COL["target"], tok_y, 8, C["obs"], C["obs_mid"])
tokens(COL["robot"], tok_y, 8, C["obs"], C["obs_fill"])
tokens(COL["summary"], tok_y, 16, C["gray"], C["faint"], cell=0.036, gap=0.012)
tokens(COL["action"], tok_y, 8, C["act"], C["act_mid"])
lab_y = tok_y + 0.12
for key, s, c in [("patch", "196 patch", C["obs"]), ("target", "8 target", C["obs"]), ("robot", "8 robot", C["obs"]),
                  ("summary", "16 summary $M$", C["muted"]), ("action", "8 action $A$", C["act"])]:
    T(COL[key], lab_y, s, size=6.0, color=c)
# scene-token brace S = 212 (under the labels, spanning patch..robot)
xs0, xs1 = COL["patch"] - 0.52, COL["robot"] + 0.40
ax.plot([xs0, xs0, xs1, xs1], [tok_y - 0.02, tok_y - 0.035, tok_y - 0.035, tok_y - 0.02], color=C["obs"], lw=0.5,
        zorder=4)
T((COL["target"] + COL["robot"]) / 2 + 0.02, tok_y - 0.06, "scene tokens $S$ = 212", size=5.6, color=C["obs"],
  bbox=dict(fc="white", ec="none", pad=0.4))

# ================================================================== backbone
bx0, bx1 = 0.10, 5.92
box(bx0, Y_B0, bx1 - bx0, Y_B1 - Y_B0, C["band"], "#6F7F8A", lw=0.8, r=0.04, z=2)
mid = (Y_B0 + Y_B1) / 2
# lower tier: shared masked attention (all tokens)
box(bx0 + 0.05, Y_B0 + 0.04, bx1 - bx0 - 0.10, 0.11, C["white"], C["line"], lw=0.5, r=0.02, z=3)
T(2.15, Y_B0 + 0.095, "shared masked attention", size=6.3, color=C["ink"])
# upper tier: split FFNs (world | action)
split = 4.62
box(bx0 + 0.05, Y_B0 + 0.18, split - bx0 - 0.10, 0.11, C["pred_fill"], C["pred_light"], lw=0.5, r=0.02, z=3)
T(2.15, Y_B0 + 0.235, "world FFN  ($S$, $M$)", size=6.3, color=C["pred_dark"])
box(split + 0.03, Y_B0 + 0.18, bx1 - split - 0.08, 0.11, C["act_fill"], C["act_mid"], lw=0.5, r=0.02, z=3)
T((split + bx1) / 2, Y_B0 + 0.235, "action FFN  ($A$)", size=6.3, color=C["act"])
T(bx0 + 0.10, Y_B0 + 0.095, "×24", size=6.5, bold=True, color=C["ink"], ha="left")
T(bx1 - 0.06, Y_B0 + 0.095, "shared $K,V$", size=5.4, color=C["muted"], ha="right")
for key in COL:
    c = C["act"] if key == "action" else (C["gray"] if key == "summary" else C["obs"])
    arrow((COL[key], tok_y + 0.165), (COL[key], Y_B0), c, lw=0.6, ms=3.5)

# attention mask, to the right of the band, rows aligned with nothing else -> keep it compact
mx, my, cs = 6.28, 0.88, 0.095
reads = {"S": "S", "M": "SM", "A": "SMA"}   # baseline C: actions read S, M and A
fill = {"S": C["obs_mid"], "M": "#C9CDD1", "A": C["act_mid"]}
for i, r in enumerate("SMA"):
    for j, c in enumerate("SMA"):
        ax.add_patch(Rectangle((mx + j * cs, my + (2 - i) * cs), cs, cs,
                               fc=fill[r] if c in reads[r] else "white", ec=C["line"], lw=0.45, zorder=4))
    T(mx - 0.05, my + (2 - i) * cs + cs / 2, r, size=5.6, color=C["muted"])
    T(mx + i * cs + cs / 2, my + 3 * cs + 0.05, r, size=5.6, color=C["muted"])
T(mx + 1.5 * cs, my - 0.07, "query reads key", size=5.2, color=C["muted"])

# ================================================================== outputs (top)
OUT_Y = 1.50                                 # bottom edge of output panels
# training-only frame
tx0, tx1 = 0.10, 4.70
box(tx0, 1.365, tx1 - tx0, 1.055, C["pred_fill"], C["pred"], lw=0.7, r=0.05, ls=(0, (4, 2.5)), z=1)

# --- sparse 3D flow on the full agent view (all 196 samples, 400 ms)
fw = 0.70
fx = COL["patch"] - fw / 2
to_f, fh = panel(BEAUTY, FULL, fx, OUT_Y, fw, fade=0.55)
src = project(A["source_world_m"])
fut = project(A["future_world_m"][:, -1])
mag = np.linalg.norm(A["flow_robot_base_m"][:, -1], axis=1)
P0, P1 = to_f(src), to_f(fut)
for p, q, m in zip(P0, P1, mag):
    if m > 0.005:   # visibly moving (robot arm ~70 mm, target ~36 mm at 400 ms)
        ax.plot(*zip(p, q), color="white", lw=1.4, zorder=7, solid_capstyle="round")
        arrow(tuple(p), tuple(q), C["pred"], lw=0.7, ms=2.8, z=8)
    else:
        ax.add_patch(Circle(p, 0.0065, fc=C["gray"], ec="none", zorder=7))
T(COL["patch"], OUT_Y + fh + 0.075, "sparse 3D flow", size=6.8, bold=True, color=C["pred_dark"])
T(fx + fw + 0.05, OUT_Y + 0.55, "14×14 points", size=5.6, color=C["muted"], ha="left")
T(fx + fw + 0.05, OUT_Y + 0.45, "+ visibility", size=5.6, color=C["muted"], ha="left")
T(fx + fw + 0.05, OUT_Y + 0.35, "400 ms shown", size=5.6, color=C["muted"], ha="left")
arrow((COL["patch"], Y_B1), (COL["patch"], OUT_Y - 0.005), C["pred"], lw=0.8, ms=4.5, ls=(0, (2.5, 1.5)))
T(COL["patch"] + 0.05, 1.432, "linear (patch)", size=5.6, color=C["pred_dark"], ha="left")

# --- target SE(3) forecast on the zoomed view (orange axes, recorded poses +50..400 ms)
sw = 1.28
sx = COL["summary"] - sw / 2
to_s, sh = panel(BEAUTY, ZOOM, sx, OUT_Y, sw)
futp = A["future_pose_world_xyzw"]
o = to_s(project(futp[:, :3]))
o0 = to_s(project(hist[-1, :3]))[0]
ax.plot([o0[0]] + list(o[:, 0]), [o0[1]] + list(o[:, 1]), color=C["pred"], lw=0.7, zorder=7, ls=(0, (1.2, 0.9)))
for p in o:
    ax.add_patch(Circle(p, 0.010, fc=C["pred"], ec="white", lw=0.35, zorder=8))
axes_glyphs(to_s, [futp[0], futp[7]], C["pred"], L=0.016, lw=0.9, ms=3.0)
for k, lab, dx, dy, ha in [(0, "+50", -0.03, -0.07, "right"), (7, "+400 ms", 0.05, -0.03, "left")]:
    T(o[k][0] + dx, o[k][1] + dy, lab, ha=ha, size=5.2, color=C["pred_dark"], bbox=dict(fc="white", ec="none", pad=0.3, alpha=0.8))
ax.add_patch(Circle(o0, 0.011, fc=C["obs"], ec="white", lw=0.4, zorder=9))
# 20 mm scale bar along the belt direction, measured from the recorded displacement
mm_per_in = (np.linalg.norm(A["target_displacement_robot_base_m"][-1]) * 1000) / np.linalg.norm(o[-1] - o0)
bar = 20.0 / mm_per_in
bx, by = sx + 0.07, OUT_Y + 0.07
ax.add_patch(Rectangle((bx - 0.03, by - 0.04), max(bar, 0.30) + 0.06, 0.14, fc="white", ec="none", alpha=0.85, zorder=8))
ax.plot([bx, bx + bar], [by, by], color=C["ink"], lw=1.0, zorder=9, solid_capstyle="butt")
T(bx + max(bar, 0.30) / 2, by + 0.05, "20 mm", size=5.2, color=C["ink"], z=10)
T(COL["summary"], OUT_Y + sh + 0.075, "target SE(3) forecast", size=6.8, bold=True, color=C["pred_dark"])
T(sx + sw - 0.03, OUT_Y + sh - 0.07, "8 horizons", size=5.4, color=C["ink"], ha="right",
  bbox=dict(fc="white", ec="none", pad=0.6, alpha=0.85))
arrow((COL["summary"], Y_B1), (COL["summary"], OUT_Y - 0.005), C["pred"], lw=0.8, ms=4.5, ls=(0, (2.5, 1.5)))
T(COL["summary"] + 0.05, 1.432, "linear (mean $M$)", size=5.6, color=C["pred_dark"], ha="left")

# --- role-aware key in the middle of the training region
kx = 1.85
T(kx, 2.27, "Training only · skipped at inference", size=6.3, bold=True, color=C["pred_dark"], ha="left")
arrow((kx + 0.02, 2.06), (kx + 0.20, 2.06), C["pred"], lw=0.7, ms=2.8)
T(kx + 0.27, 2.06, "coarse: every body,\none point per patch", size=5.8, color=C["ink"], ha="left", linespacing=1.05)
for j, (dx, dy) in enumerate([(0.10, 0.0), (0.0, 0.08)]):
    arrow((kx + 0.06, 1.78), (kx + 0.06 + dx, 1.78 + dy), C["pred"], lw=1.0, ms=3.2)
T(kx + 0.27, 1.81, "fine: target pose,\nmm-level, 8 horizons", size=5.8, color=C["ink"], ha="left")
T(kx + 0.27, 1.57, "(appearance auxiliaries omitted)", size=5.2, color=C["muted"], ha="left")

# --- action chunk: recorded expert EEF states, capture + 0..350 ms
aw = 0.70
ax_ = COL["action"] - aw / 2
to_a, ah = panel(BEAUTY, ACTZ, ax_, OUT_Y, aw)
eef = to_a(project(A["eef_world_m"][:8]))
ax.plot(eef[:, 0], eef[:, 1], color="white", lw=2.0, zorder=7, solid_capstyle="round")
ax.plot(eef[:, 0], eef[:, 1], color=C["act"], lw=1.0, zorder=8, solid_capstyle="round")
for p in eef:
    ax.add_patch(Circle(p, 0.012, fc=C["act"], ec="white", lw=0.35, zorder=9))
arrow(tuple(eef[-2]), tuple(eef[-1] + (eef[-1] - eef[-2]) * 0.6), C["act"], lw=1.0, ms=4, z=9)
T(COL["action"], OUT_Y + ah + 0.075, "action chunk", size=6.8, bold=True, color=C["act"])
T(ax_ + aw + 0.05, OUT_Y + 0.55, "8 commands", size=5.6, color=C["act"], ha="left")
T(ax_ + aw + 0.05, OUT_Y + 0.45, "Δ$_a$ = 50 ms", size=5.6, color=C["act"], ha="left")
T(ax_ + aw + 0.05, OUT_Y + 0.35, "used at inference", size=5.6, color=C["act"], ha="left", bold=True)
arrow((COL["action"], Y_B1), (COL["action"], OUT_Y - 0.005), C["act"], lw=0.9, ms=4.5)
# Euler loop: small circular arrow beside the velocity head
lx, ly = COL["action"] + 0.12, (Y_B1 + OUT_Y) / 2
ax.add_patch(Arc((lx, ly), 0.10, 0.10, theta1=40, theta2=330, color=C["act"], lw=0.7, zorder=7))
ang = np.deg2rad(40)
arrow((lx + 0.05 * np.cos(ang) - 0.012, ly + 0.05 * np.sin(ang) - 0.02), (lx + 0.05 * np.cos(ang), ly + 0.05 * np.sin(ang)),
      C["act"], lw=0.7, ms=3.0, z=8)
T(lx + 0.08, ly, "velocity $v_\\psi$ · Euler ×5", size=5.6, color=C["act"], ha="left")

for ext in ("pdf", "svg"):
    fig.savefig(OUT / f"fig2_se3wam.{ext}")
fig.savefig(OUT / "fig2_se3wam.png", dpi=300)
print(f"saved fig2_se3wam.* ({W} x {H} in, font {FONT})")
