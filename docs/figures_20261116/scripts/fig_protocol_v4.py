"""§4.3 protocol timeline, VLASH idiom. Single column (3.25 in).
Steady state: query t has k_t = 3, query t+1 has k_{t+1} = 2, chunk H = 8, Delta_a = 50 ms."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "mathtext.fontset": "custom", "mathtext.rm": "Liberation Sans", "mathtext.it": "Liberation Sans:italic", "mathtext.sf": "Liberation Sans",
                     "text.color": "#1A1A1A", "pdf.fonttype": 42})
INK, MID = "#1A1A1A", "#5A5A5A"
EXE, SKIP, REP = "#F1CA73", "#9A9A9A", "#FFFFFF"     # executed = action amber (Fig. 3 token fill); skipped = grey
RED = "#C0263A"

W, H = 234.0, 92.0          # points
fig = plt.figure(figsize=(W / 72, H / 72), dpi=300)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis("off")

c, ch, x0 = 13.6, 10.0, 105.0          # cell width, cell height, x of tau_t
H_CH, KT, KT1 = 8, 3, 2
X = lambda j: x0 + j * c               # j in control periods relative to tau_t
yP, yN = 32.0, 44.5                    # previous / new chunk rows

def cell(j, y, kind, label):
    fc = {"exe": EXE, "skip": SKIP, "rep": REP}[kind]
    ax.add_patch(Rectangle((X(j), y), c, ch, fc=fc, ec=INK, lw=.45, zorder=2))
    ax.text(X(j) + c / 2, y + ch / 2 + .3, label, ha="center", va="center", fontsize=5.6,
            color="#FFFFFF" if kind == "skip" else (INK if kind == "exe" else "#8A8A8A"), zorder=3)

# previous chunk: issued at tau_t - k_t*Delta, skipped 0..2, executed 3..5 until tau_{t+1}, rest replaced
for i in range(H_CH):
    j = i - KT
    cell(j, yP, "skip" if i < KT else ("exe" if i < 2 * KT else "rep"), str(i))
# new chunk: issued at tau_t, skipped 0..k_t-1, executed k_t..k_t+k_{t+1}-1, rest replaced
for i in range(H_CH):
    cell(i, yN, "skip" if i < KT else ("exe" if i < KT + KT1 else "rep"), str(i))

ax.text(4, yP + ch / 2, "Previous chunk", va="center", fontsize=7)
ax.text(4, yN + ch / 2, "New chunk", va="center", fontsize=7)

# guide lines at tau_t, tau_{t+1}, tau_{t+1}+k_{t+1}Delta
for j in (0, KT, KT + KT1):
    ax.plot([X(j), X(j)], [14, yN + ch + 1.5], color=MID, lw=.4, ls=(0, (1.2, 1.2)), zorder=1)

# inference intervals (dimension lines with end ticks)
def dim(xa, xb, y, label, color, lw=.6):
    ax.annotate("", xy=(xb, y), xytext=(xa, y), arrowprops=dict(arrowstyle="<->,head_length=.25,head_width=.12",
                lw=lw, color=color, shrinkA=0, shrinkB=0))
    for xx in (xa, xb):
        ax.plot([xx, xx], [y - 2.2, y + 2.2], color=color, lw=lw)
    ax.text((xa + xb) / 2, y - 3.2, label, ha="center", va="bottom", fontsize=7.6, color=color)
dim(X(0), X(0) + 2.55 * c, 22, r"$L_t$", INK)
dim(X(KT), X(KT) + 1.6 * c, 22, r"$L_{t+1}$", MID, lw=.5)
ax.text(4, 22, "Inference", va="center", fontsize=7)

# key point: actions of query t act on an observation that is k_t .. k_t+k_{t+1} periods old
yb = yN + ch + 2.2
xa, xb = X(KT), X(KT + KT1)
ax.plot([xa, xa, xb, xb], [yb, yb + 2.2, yb + 2.2, yb], color=RED, lw=.6)
ax.text((xa + xb) / 2 + 1, yb + 4.0, r"planned from the frame at $\tau_t$",
        ha="center", va="top", fontsize=6.4, color=RED, style="italic")

# time labels under the guide lines
ty = 70.5
ax.text(X(0), ty, r"$\tau_t$", ha="center", va="top", fontsize=7.4)
ax.text(X(KT), ty, r"$\tau_{t+1}$", ha="center", va="top", fontsize=7.4)
ax.text(X(KT + KT1) - 1.5, ty, r"$\tau_{t+1}{+}k_{t+1}\Delta_a$", ha="left", va="top", fontsize=7.4)
ax.text(X(0), ty + 9.5, "capture", ha="center", va="top", fontsize=6.4, color=MID)
ax.text(X(KT), ty + 9.5, "handover", ha="center", va="top", fontsize=6.4, color=MID)
ax.text(X(KT + KT1) - 1.5, ty + 9.5, "next handover", ha="left", va="top", fontsize=6.4, color=MID)
ax.text(4, ty + 4.5, "Time", va="center", fontsize=7, color=MID)

# legend (VLASH: small swatches in one line at the top)
lx, ly = 70.0, 5.0
for lab, fc in (("Skipped", SKIP), ("Executed", EXE), ("Replaced", REP)):
    ax.add_patch(Rectangle((lx, ly - 3.2), 6.4, 6.4, fc=fc, ec=INK, lw=.45))
    ax.text(lx + 8.6, ly + .3, lab, va="center", fontsize=6.8)
    lx += 8.6 + {"Skipped": 30, "Executed": 33, "Replaced": 30}[lab] + 6

fig.savefig("/home/claude/fig_protocol_v4.png", dpi=300)
fig.savefig("/home/claude/fig_protocol_v4.pdf")
print("ok")
