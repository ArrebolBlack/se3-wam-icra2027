"""Protocol timeline v3, VLASH Fig. 2 idiom: one handover, two chunk rows, three cell states.
Example: latency L = 152 ms, control period 50 ms -> k = 4; chunk length H = 10."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "text.color": "#1A1A1A",
                     "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic"})
INK, GREY = "#1A1A1A", "#6E6E6E"
EXE, SKIP, DISC = "#E69F00", "#7A7A7A", "#FFFFFF"
L_MS, DT, H = 152.0, 50.0, 10
k = math.ceil(L_MS / DT)

W_PT, H_PT = 234.0, 112.0
fig = plt.figure(figsize=(W_PT / 72, H_PT / 72), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W_PT); ax.set_ylim(H_PT, 0); ax.axis("off")

c = 13.4                 # one control period in pt
x0 = 82.0                # x of tau_t (capture of the new query)
X = lambda j: x0 + j * c  # boundary j periods after capture
ch = 9.0                 # cell height
y_prev, y_new = 52.0, 68.0


def cell(j, y, state, label=None):
    fc = {"exe": EXE, "skip": SKIP, "disc": DISC}[state]
    ax.add_patch(Rectangle((X(j) + .5, y), c - 1.0, ch, fc=fc, ec=INK, lw=.45, zorder=2))
    if label is not None:
        ax.text(X(j) + c / 2, y + ch / 2 + .2, label, ha="center", va="center", fontsize=4.9,
                color="white" if state == "skip" else INK, zorder=3)


# legend (as in VLASH)
lx, ly = 4.0, 8.0
for i, (state, name) in enumerate([("skip", "Skipped"), ("exe", "Executed"), ("disc", "Discarded")]):
    xx = lx + i * 52
    ax.add_patch(Rectangle((xx, ly - 3.6), 7.5, 7.0, fc={"exe": EXE, "skip": SKIP, "disc": DISC}[state], ec=INK, lw=.45))
    ax.text(xx + 10, ly, name, va="center", fontsize=6.6)

# rows
ax.text(4, y_prev + ch / 2, "Previous chunk", ha="left", va="center", fontsize=6.6)
ax.text(4, y_new + ch / 2, "New chunk", ha="left", va="center", fontsize=6.6)
# previous chunk was captured at tau_t - k*DT and handed over at tau_t; commands indexed from its own capture
for j in range(H):
    jj = j - k                       # position relative to tau_t
    if jj < -1:
        continue
    state = "skip" if j < k else ("exe" if jj < k else "disc")
    if jj < 0:
        # before tau_t: drawn faint, belongs to the chunk before
        ax.add_patch(Rectangle((X(jj) + .5, y_prev), c - 1.0, ch, fc="#EDEDED", ec="#BDBDBD", lw=.4, zorder=1))
        continue
    cell(jj, y_prev, state, str(j))
for j in range(H):
    cell(j, y_new, "skip" if j < k else "exe", str(j))

# time markers above the rows
yt = 28.0
ax.plot([X(0), X(0)], [yt - 2, y_new + ch + 3], color=INK, lw=.5, ls=(0, (1.5, 1.2)), zorder=0)
ax.plot([X(k), X(k)], [yt - 2, y_new + ch + 3], color=INK, lw=.7, ls=(0, (3, 1.5)), zorder=0)
ax.text(X(0), yt - 4.5, r"capture $\tau_t$", ha="center", va="bottom", fontsize=6.2)
ax.text(X(k), yt - 4.5, r"handover $\tau_t + k\Delta$", ha="center", va="bottom", fontsize=6.2)
# inference bar and latency bracket
yi = 38.5
Lpt = L_MS / DT * c
ax.add_patch(Rectangle((X(0), yi), Lpt, 6.0, fc="#D9D9D9", ec="none", zorder=1))
ax.text(X(0) + Lpt / 2, yi + 3.2, f"L = {L_MS:.0f} ms", ha="center", va="center", fontsize=5.8)
ax.text(4, yi + 3.2, "Inference", ha="left", va="center", fontsize=6.6)
ax.text(X(k) + 4, yi + 3.2, "the world keeps moving during inference", ha="left", va="center", fontsize=5.8, color=GREY, style="italic")

# braces below
def brace(xa, xb, y, text, color=INK):
    ax.plot([xa + .5, xa + .5, xb - .5, xb - .5], [y, y + 2.2, y + 2.2, y], color=color, lw=.5)
    ax.text((xa + xb) / 2, y + 7.2, text, ha="center", va="center", fontsize=5.9, color=color)

yb = y_new + ch + 2.0
brace(X(0), X(k), yb, "overdue, skipped")
brace(X(k), X(H), yb, f"executed from command {k}")
ax.text(4, 100.5, r"$k=\lceil L/\Delta\rceil$,  $\Delta$ = 50 ms control period", fontsize=5.9, color=GREY, va="center")

fig.savefig("/home/claude/fig_timeline_v3.png", dpi=300)
fig.savefig("/home/claude/fig_timeline_v3.pdf")
print("k", k, "right edge", X(H))
