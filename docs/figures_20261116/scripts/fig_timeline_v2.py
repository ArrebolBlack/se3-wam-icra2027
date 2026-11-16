"""Protocol timeline, single column (3.25 in). Facts from appendix/benchmark.tex (Executor, Protocols)."""
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

plt.rcParams.update({"font.family": "Liberation Sans", "font.size": 7, "text.color": "#1A1A1A"})
DT, T_END = 50.0, 450.0
OBS, INF, A1, A2, HOLD = "#2859A3", "#BDBDBD", "#E69F00", "#F3CE7A", "#FFFFFF"
INK, GREY = "#1A1A1A", "#6E6E6E"

fig = plt.figure(figsize=(3.25, 2.7), dpi=300)
ax = fig.add_axes([0.20, 0.10, 0.78, 0.84])
ax.set_xlim(-4, T_END + 4); ax.set_ylim(9.7, -0.55); ax.axis("off")
for t in range(0, int(T_END) + 1, int(DT)):
    ax.plot([t, t], [-0.2, 8.5], color="#E6E6E6", lw=.4, zorder=0)


def lane_title(y, s, color):
    ax.text(-4, y, s, fontsize=6.9, fontweight="bold", color=color, va="center")


def rowlab(y, s):
    ax.text(-10, y, s, ha="right", va="center", fontsize=6.2, color=INK)


def query(t0, L, y, h=.42, label=None):
    ax.plot([t0], [y], marker="o", ms=2.6, color=OBS, zorder=4)
    if L > 0:
        ax.add_patch(Rectangle((t0, y - h / 2), L, h, fc=INF, lw=0, zorder=2))
        if label:
            ax.text(t0 + L / 2, y, label, ha="center", va="center", fontsize=5.4, color=INK, zorder=3)


def cmd(t0, y, j, fc, skipped=False, h=.52):
    w = DT * .9
    x = t0 + (DT - w) / 2
    if skipped:
        ax.add_patch(Rectangle((x, y - h / 2), w, h, fc="white", ec="#B0B0B0", lw=.45, zorder=2))
        ax.plot([x + 6, x + w - 6], [y - .16, y + .16], color="#B0B0B0", lw=.5, zorder=3)
        ax.plot([x + 6, x + w - 6], [y + .16, y - .16], color="#B0B0B0", lw=.5, zorder=3)
    else:
        ax.add_patch(Rectangle((x, y - h / 2), w, h, fc=fc, ec="#B37C00", lw=.45, zorder=2))
        ax.text(x + w / 2, y, str(j), ha="center", va="center", fontsize=5.3, color=INK, zorder=3)


def hold(t0, t1, y, h=.52):
    ax.add_patch(Rectangle((t0 + 2, y - h / 2), t1 - t0 - 4, h, fc="white", ec="#B0B0B0", lw=.45, hatch="////", zorder=2))
    ax.text((t0 + t1) / 2, y, "hold", ha="center", va="center", fontsize=5.2, color=GREY, zorder=3,
            bbox=dict(boxstyle="square,pad=0.15", fc="white", ec="none"))


# ---------------- lane 1: paused reference
lane_title(-0.1, "Paused (reference): inference takes no physics time", "#C0263A")
yq, ye = 0.65, 1.35
rowlab(yq, "query"); rowlab(ye, "executed")
for p in range(int(T_END / DT)):
    query(p * DT, 0, yq)
    cmd(p * DT, ye, 0, A1 if p % 2 == 0 else A2)

# ---------------- lane 2: fast policy, native latency
L_fast = 15.1
lane_title(2.45, f"Native, fast policy (p95 {L_fast:.0f} ms, k = 1)", "#2E8540")
yq, ye = 3.2, 3.9
rowlab(yq, "query"); rowlab(ye, "executed")
hold(0, DT, ye)
for p in range(int(T_END / DT)):
    query(p * DT, L_fast, yq)
    if p >= 1:
        cmd(p * DT, ye, 1, A1 if p % 2 == 1 else A2)

# ---------------- lane 3: slow policy, native latency
L_slow, H = 151.7, 8
k = math.ceil(L_slow / DT)
lane_title(5.0, f"Native, slow policy (p95 {L_slow:.0f} ms, k = {k})", "#2E8540")
yq, yc, ye = 5.75, 6.45, 7.55
rowlab(yq, "query"); rowlab(yc, "chunk 1"); rowlab(ye, "executed")
query(0, L_slow, yq, label=f"{L_slow:.0f} ms")
query(k * DT, L_slow, yq, label=f"{L_slow:.0f} ms")
for j in range(H):
    cmd(j * DT, yc, j, A1, skipped=j < k)
hold(0, k * DT, ye)

for j in range(k, H):
    cmd(j * DT, ye, j, A1)
cmd(2 * k * DT, ye, k, A2)          # chunk 2 (captured at 200 ms) takes over at 400 ms, from its command k
ax.annotate("", xy=(k * DT, ye - .32), xytext=(k * DT, yq + .26),
            arrowprops=dict(arrowstyle="-|>,head_length=0.28,head_width=0.13", lw=.6, color=INK, ls=(0, (2, 1.4))))
ax.text(k * DT / 2, yc + .55, "commands 0–3 overdue, skipped", ha="center", va="center", fontsize=5.0, color=GREY)
ax.annotate("", xy=(2 * k * DT, ye - .32), xytext=(2 * k * DT, yq + .26),
            arrowprops=dict(arrowstyle="-|>,head_length=0.28,head_width=0.13", lw=.6, color=INK, ls=(0, (2, 1.4))))
ax.text(2 * k * DT + 25, ye + .55, "chunk 2", ha="center", va="center", fontsize=5.2, color=GREY)

# ---------------- time axis
ya = 8.55
ax.plot([0, T_END], [ya, ya], color=INK, lw=.6)
for t in range(0, int(T_END) + 1, 100):
    ax.plot([t, t], [ya, ya + .15], color=INK, lw=.5)
    ax.text(t, ya + .55, f"{t}", ha="center", va="center", fontsize=5.8)
ax.text(T_END, ya + 1.05, "physics time (ms); grid = 50 ms control period", ha="right", va="center", fontsize=5.6, color=GREY)

# ---------------- legend
lx, ly = -4, 9.05
fig.savefig("/home/claude/fig_timeline_v2.png", dpi=300)
fig.savefig("/home/claude/fig_timeline_v2.pdf")
