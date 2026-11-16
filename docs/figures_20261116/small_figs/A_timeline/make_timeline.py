"""Native-protocol executor timeline (OnTimeBench, Sec. 4.3) -- candidate directions.

Protocol facts drawn here (appendix/benchmark.tex, "Executor"):
  * command j of query t is meant for tau_t + j*Delta_a, Delta_a = 50 ms;
  * a query with latency L_t hands over at the first boundary at/after it ends,
    k_t = ceil(L_t / Delta_a) periods after capture; execution starts at command k_t;
  * the policy then observes again and starts the next query while the previous
    chunk keeps running, so (for a fixed L) each chunk executes commands k..2k-1;
  * a chunk holds H_m commands; commands beyond the next handover are superseded.

Example parameters are real configurations (Table 1 p95, Table S-baselines H) but the
latency is held fixed at the p95 for illustration; in the benchmark L_t is drawn per query.

Variants
  a  time-indexed staircase: one row per query, every command at its intended time
  b  two policies, inference lane + executed lane (fast vs slow)
  c  variant a re-laid out for the Fig. 4(b) slot (2.40 x 1.45 in)
"""
import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent

DT = 50.0                                   # control period Delta_a (ms)
SLOW = dict(name="OpenWAM-α", L=151.7, H=32)  # Table 1 p95; supp_baselines H
FAST = dict(name="FoveaWAM", L=15.1, H=8)

INK, GREY, LIGHT, GRID = "#1A1A1A", "#6E6E6E", "#BDBDBD", "#E5E5E5"
AMBER, AMBER_EDGE = "#E69F00", "#A86F00"
INFER = "#8C8C8C"

TXT = {
    "en": dict(
        inference="Inference", skipped="Skipped (overdue)", executed="Executed",
        superseded="Superseded", query="Query", exec_row="Executed",
        axis=r"Time since capture $\tau_t$ (ms)", axis_short="Time (ms)",
        replan="replan {r:.0f} ms", age="age {a}",
        prev="Prev. chunk", new="New chunk", prev_s="Previous", new_s="New", skipped_short="Skipped",
        open_loop="executed {a:.0f}–{b:.0f} ms after capture",
        open_loop_short="{a:.0f}–{b:.0f} ms after capture",
    ),
    "zh": dict(
        inference="推理", skipped="跳过（已过期）", executed="执行",
        superseded="被替换", query="查询", exec_row="实际执行",
        axis=r"距捕获时刻 $\tau_t$ 的时间（ms）", axis_short="时间（ms）",
        replan="每 {r:.0f} ms 重规划", age="指令陈旧 {a}",
        prev="上一块", new="新块", skipped_short="跳过",
        open_loop="在捕获后 {a:.0f}–{b:.0f} ms 执行",
        open_loop_short="捕获后 {a:.0f}–{b:.0f} ms",
    ),
}


def setup(font, lang):
    fonts = [font, "Microsoft YaHei"] if lang == "zh" else [font]
    for f in fonts:  # fail loudly instead of silently falling back
        font_manager.findfont(font_manager.FontProperties(family=f), fallback_to_default=False)
    plt.rcParams.update({
        "font.family": fonts, "font.size": 7, "text.color": INK,
        "mathtext.fontset": "custom", "mathtext.rm": font,
        "mathtext.it": f"{font}:italic", "mathtext.bf": f"{font}:bold",
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.facecolor": "white", "hatch.linewidth": 0.35,
    })


class Canvas:
    """Axes in points, y pointing down."""

    def __init__(self, w_pt, h_pt):
        self.fig = plt.figure(figsize=(w_pt / 72, h_pt / 72), dpi=300)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, w_pt)
        self.ax.set_ylim(h_pt, 0)
        self.ax.axis("off")
        self.w, self.h = w_pt, h_pt

    def text(self, x, y, s, **kw):
        kw.setdefault("va", "center")
        kw.setdefault("fontsize", 7)
        return self.ax.text(x, y, s, **kw)

    def rect(self, x, y, w, h, **kw):
        self.ax.add_patch(Rectangle((x, y), w, h, **kw))

    def line(self, xs, ys, **kw):
        self.ax.plot(xs, ys, solid_capstyle="butt", **kw)

    def save(self, stem):
        for ext in ("png", "pdf", "svg"):
            self.fig.savefig(f"{stem}.{ext}", dpi=300)
        plt.close(self.fig)


def cell(cv, x, y, w, h, state, label=None, fs=6.5, alpha=1.0):
    pad = 0.45
    if state == "exe":
        cv.rect(x + pad, y, w - 2 * pad, h, fc=AMBER, ec=AMBER_EDGE, lw=0.45, zorder=3)
        col = INK
    elif state == "skip":
        cv.rect(x + pad, y, w - 2 * pad, h, fc="white", ec=GREY, lw=0.45, hatch="//////", zorder=3)
        # white box behind the label keeps the digit legible on the hatch
        col = GREY
    else:  # superseded
        cv.rect(x + pad, y, w - 2 * pad, h, fc="white", ec=LIGHT, lw=0.45, zorder=3, alpha=alpha)
        col = "#9A9A9A"
    if label is not None:
        t = cv.text(x + w / 2, y + h / 2 + 0.15, label, ha="center", fontsize=fs, color=col,
                    zorder=4, alpha=alpha if state == "disc" else 1.0)
        if state == "skip":
            t.set_bbox(dict(fc="white", ec="none", pad=0.25))


def legend(cv, x, y, items, fs=7, gap=7.0, sw=8.0, sh=6.0):
    """items: list of (kind, text). Returns end x."""
    for kind, s in items:
        if kind == "infer":
            cv.rect(x, y - 1.6, sw + 2, 3.2, fc=INFER, ec="none")
        else:
            cell(cv, x - 0.45, y - sh / 2, sw + 0.9, sh, kind)
        tx = x + sw + (5.0 if kind == "infer" else 3.0)
        t = cv.text(tx, y, s, fontsize=fs)
        bb = t.get_window_extent(renderer=cv.fig.canvas.get_renderer())
        width_pt = bb.width * 72 / cv.fig.dpi
        x = tx + width_pt + gap
    return x


# --------------------------------------------------------------------------- a / c
def staircase(cv, T, geo, fs=7, fs_cell=6.5, show_k=True):
    """Rows: query t-1, t, t+1 and the executed stream, on one physical time axis."""
    L, H = SLOW["L"], SLOW["H"]
    k = math.ceil(L / DT)
    t0, t1 = geo["t0"], geo["t1"]
    x0, x1 = geo["x0"], geo["x1"]
    X = lambda t: x0 + (t - t0) / (t1 - t0) * (x1 - x0)
    cw = X(DT) - X(0)
    ch = geo["ch"]

    rows = geo["rows"]          # y of command cells for query t-1, t, t+1
    y_exe = geo["y_exe"]
    y_axis = geo["y_axis"]
    top = rows[0] - geo["bar_gap"] - 3.5

    # clock grid: every control boundary
    t = t0
    while t <= t1 + 1e-6:
        if t >= t0:
            cv.line([X(t)] * 2, [top, y_exe + ch], color=GRID, lw=0.35, zorder=0)
        t += DT
    # handover boundaries (= captures of the next query)
    for m in range(-1, 4):
        th = m * k * DT
        if t0 <= th <= t1:
            cv.line([X(th)] * 2, [top, y_exe + ch], color=GREY, lw=0.5,
                    ls=(0, (2.2, 1.6)), zorder=1)

    labels = [f"{T['query']} $t{{-}}1$", f"{T['query']} $t$", f"{T['query']} $t{{+}}1$"]
    for r, (y, lab) in enumerate(zip(rows, labels)):
        cap = (r - 1) * k * DT          # capture time of this query
        cv.text(geo["xlab"], y + ch / 2, lab, ha="left", fontsize=fs)
        # inference bar above the cells
        yb = y - geo["bar_gap"] - 3.0
        a, b = max(cap, t0), min(cap + L, t1)
        if b > a:
            cv.rect(X(a), yb, X(b) - X(a), 3.0, fc=INFER, ec="none", zorder=2)
        if cap >= t0:
            cv.ax.plot([X(cap)], [yb + 1.5], marker="o", ms=2.6, mfc=INK, mec="white",
                       mew=0.4, zorder=5, clip_on=False)
        for j in range(H):
            ts = cap + j * DT
            if ts + DT <= t0 + 1e-6 or ts >= t1 - 1e-6:
                continue
            state = "skip" if j < k else ("exe" if j < 2 * k else "disc")
            alpha = 1.0
            if state == "disc":
                alpha = max(0.25, 1.0 - 0.22 * (j - 2 * k))
            # clip partially visible cells at the left edge
            xa = max(X(ts), X(t0))
            w = X(ts + DT) - xa
            if w < cw - 0.1:
                if state != "skip":
                    continue
                cv.rect(xa, y, w - 0.45, ch, fc="white", ec=GREY, lw=0.45, hatch="//////", zorder=3)
                continue
            cell(cv, xa, y, cw, ch, state, str(j), fs=fs_cell, alpha=alpha)
        if show_k and r == 1:
            cv.text(X(cap + L) + 1.5, yb + 1.4,
                    rf"$L_t$ = {L:.0f} ms $\rightarrow$ $k_t$ = {k}",
                    ha="left", fontsize=fs_cell, color=INK, zorder=6,
                    bbox=dict(fc="white", ec="none", pad=0.4))

    # executed stream
    cv.text(geo["xlab"], y_exe + ch / 2, T["exec_row"], ha="left", fontsize=fs, weight="bold")
    t = 0.0
    while t < t1 - 1e-6:
        j = k + int(round((t % (k * DT)) / DT))
        cell(cv, X(t), y_exe, cw, ch, "exe", str(j), fs=fs_cell)
        t += DT
    # thicker separators between chunks in the executed stream
    for m in range(0, 4):
        th = m * k * DT
        if 0 < th < t1:
            cv.line([X(th)] * 2, [y_exe - 1.2, y_exe + ch + 1.2], color=INK, lw=0.9, zorder=6)

    # axis
    cv.line([X(t0), X(t1)], [y_axis, y_axis], color=INK, lw=0.55)
    for tt in range(int(math.ceil(t0 / 100) * 100), int(t1) + 1, 100):
        cv.line([X(tt)] * 2, [y_axis, y_axis + 2.0], color=INK, lw=0.55)
        cv.text(X(tt), y_axis + 6.3, f"{tt}", ha="center", fontsize=fs)
    return X, k


def variant_a(T, out):
    W, Hh = 234.0, 112.0
    cv = Canvas(W, Hh)
    legend(cv, 3.0, 6.0, [("infer", T["inference"]), ("skip", T["skipped"]),
                          ("exe", T["executed"]), ("disc", T["superseded"])], fs=6.6, gap=5.0, sw=7.0)
    geo = dict(t0=-50, t1=600, x0=44.0, x1=W - 7.0, xlab=2.0, ch=9.0, bar_gap=1.2,
               rows=[21.0, 40.0, 59.0], y_exe=76.5, y_axis=90.0)
    X, k = staircase(cv, T, geo, fs=7, fs_cell=6.5)
    cv.text((X(-50) + X(600)) / 2, 106.0, T["axis"], ha="center", fontsize=7)
    cv.save(out / "cand_a_staircase")
    return W, Hh


def variant_c(T, out):
    # Fig. 4(b) slot: Fig. 4 is set at \textwidth (6.875 in); its left column is ~2.40 in wide
    # and (b) occupies ~1.45 in. Fig. 4 text is ~9-10 pt at print size, so use 8 pt here.
    W, Hh = 2.40 * 72, 1.45 * 72
    cv = Canvas(W, Hh)
    cv.text(0.0, 6.5, "(b) Native executor", ha="left", fontsize=9.5, weight="bold")
    geo = dict(t0=-50, t1=600, x0=40.0, x1=W - 7.0, xlab=0.0, ch=9.5, bar_gap=1.4,
               rows=[25.0, 43.5, 62.0], y_exe=80.0, y_axis=93.5)
    X, k = staircase(cv, T, geo, fs=7.5, fs_cell=6.5)
    cv.text(0.0, 93.5 + 6.3, T["axis_short"], ha="left", fontsize=7.5)
    cv.save(out / "cand_c_fig4b_slot")
    return W, Hh


# --------------------------------------------------------------------------- b
def variant_b(T, out):
    W, Hh = 234.0, 104.0
    cv = Canvas(W, Hh)
    t0, t1 = 0.0, 600.0
    x0, x1 = 3.0, W - 7.0
    X = lambda t: x0 + (t - t0) / (t1 - t0) * (x1 - x0)
    cw = X(DT) - X(0)
    ch, bh = 9.0, 3.0

    legend(cv, 3.0, 6.0, [("infer", T["inference"]), ("exe", T["executed"])], fs=6.6, gap=8.0, sw=7.0)
    cv.text(W - 3.0, 6.0, r"cell: command index $j$" if T is TXT["en"]
            else r"格内为指令序号 $j$", ha="right", fontsize=6.5, color=GREY)

    blocks = [(FAST, 22.0), (SLOW, 57.0)]
    y_axis = 88.0
    # grid
    t = t0
    while t <= t1 + 1e-6:
        cv.line([X(t)] * 2, [blocks[0][1] + 4, y_axis], color=GRID, lw=0.35, zorder=0)
        t += DT
    for m, yy in blocks:
        k = math.ceil(m["L"] / DT)
        period = k * DT
        age = (f"{k * DT:.0f} ms" if k == 1 else f"{k * DT:.0f}–{(2 * k - 1) * DT:.0f} ms")
        head = rf"{m['name']}  $L_t$ = {m['L']:.0f} ms, $k_t$ = {k}"
        cv.text(X(0), yy, head, ha="left", fontsize=7, weight="normal")
        cv.text(X(t1), yy, T["replan"].format(r=period) + " · " + T["age"].format(a=age),
                ha="right", fontsize=6.5, color=GREY)
        yb = yy + 5.0
        ye = yb + bh + 2.0
        cap = 0.0
        while cap < t1 - 1e-6:
            cv.rect(X(cap), yb, X(min(cap + m["L"], t1)) - X(cap), bh, fc=INFER, ec="none", zorder=2)
            cv.ax.plot([X(cap)], [yb + bh / 2], marker="o", ms=2.4, mfc=INK, mec="white", mew=0.4,
                       zorder=5, clip_on=False)
            cap += period
        t = 0.0
        while t < t1 - 1e-6:
            j = k + int(round((t % period) / DT))
            cell(cv, X(t), ye, cw, ch, "exe", str(j), fs=6.5)
            t += DT
        for c_ in range(1, int(t1 // period) + 1):
            th = c_ * period
            if th < t1:
                cv.line([X(th)] * 2, [ye - 1.2, ye + ch + 1.2], color=INK, lw=0.9, zorder=6)
    cv.line([X(t0), X(t1)], [y_axis, y_axis], color=INK, lw=0.55)
    for tt in range(0, 601, 100):
        cv.line([X(tt)] * 2, [y_axis, y_axis + 2.0], color=INK, lw=0.55)
        cv.text(X(tt), y_axis + 6.3, f"{tt}", ha="center", fontsize=7)
    cv.text(X(t1), y_axis + 13.2, T["axis_short"], ha="right", fontsize=7)
    cv.save(out / "cand_b_two_policies")
    return W, Hh


# --------------------------------------------------------------------------- a2 / c2 (VLASH-informed)
def two_chunk(cv, T, geo, fs=7, fs_cell=6.5, max_label=99):
    """VLASH Fig. 2 layout (legend row, previous / new chunk rows, interval bracket),
    on a physical time axis with one inference lane."""
    L, H = SLOW["L"], SLOW["H"]
    k = math.ceil(L / DT)
    t0, t1 = geo["t0"], geo["t1"]
    X = lambda t: geo["x0"] + (t - t0) / (t1 - t0) * (geo["x1"] - geo["x0"])
    cw, ch = X(DT) - X(0), geo["ch"]
    y_inf, y_prev, y_new, y_axis = geo["y_inf"], geo["y_prev"], geo["y_new"], geo["y_axis"]
    top, bottom = geo["y_sym"] + 3.5, y_new + ch

    t = t0
    while t <= t1 + 1e-6:
        cv.line([X(t)] * 2, [y_inf - 2, bottom], color=GRID, lw=0.35, zorder=0)
        t += DT
    sym = [r"$\tau_t$", r"$\tau_t{+}k_t\Delta_a$", r"$\tau_t{+}2k_t\Delta_a$"]
    for m, lab in enumerate(sym):
        th = m * k * DT
        cv.line([X(th)] * 2, [top, bottom + 1.5], color=GREY, lw=0.5, ls=(0, (2.2, 1.6)), zorder=1)
        cv.text(X(th), geo["y_sym"], lab, ha="center", fontsize=fs_cell)

    # inference lane: one query per handover; capture dot at the start of each bar
    cv.text(geo["xlab"], y_inf + 1.5, T["inference"], ha="left", fontsize=fs)
    for m in range(-1, 3):
        cap = m * k * DT
        a, b = max(cap, t0), min(cap + L, t1)
        if b <= a:
            continue
        cv.rect(X(a), y_inf, X(b) - X(a), 3.0, fc=INFER, ec="none", zorder=2)
        if cap >= t0:
            cv.ax.plot([X(cap)], [y_inf + 1.5], marker="o", ms=2.6, mfc=INK, mec="white",
                       mew=0.4, zorder=5)
    # latency label sits in the symbol row, between tau_t and the handover
    lat = geo.get("lat_fmt", r"$L_t$ = {L:.0f} ms").format(L=L)
    cv.text(X(L / 2) + geo.get("lat_dx", 2.0), geo["y_sym"], lat, ha="center", fontsize=fs_cell, color=GREY)

    for y, cap, lab in [(y_prev, -k * DT, T["prev"]), (y_new, 0.0, T["new"])]:
        cv.text(geo["xlab"], y + ch / 2, lab, ha="left", fontsize=fs)
        for j in range(H):
            ts = cap + j * DT
            if ts < t0 - 1e-6 or ts >= t1 - 1e-6:
                continue
            state = "skip" if j < k else ("exe" if j < 2 * k else "disc")
            alpha = max(0.3, 1.0 - 0.2 * (j - 2 * k)) if state == "disc" else 1.0
            cell(cv, X(ts), y, cw, ch, state, str(j) if j <= max_label else None,
                 fs=fs_cell, alpha=alpha)

    # bracket under the executed part of the new chunk (VLASH's interval bracket)
    yb = y_new + ch + 1.6
    xa, xb = X(k * DT) + 0.6, X(2 * k * DT) - 0.6
    cv.line([xa, xa, xb, xb], [yb, yb + 2.0, yb + 2.0, yb], color=INK, lw=0.5)
    cv.text((xa + xb) / 2, yb + 7.4,
            T[geo.get("ol_key", "open_loop")].format(a=k * DT, b=2 * k * DT), ha="center", fontsize=fs_cell)

    cv.line([X(t0), X(t1)], [y_axis, y_axis], color=INK, lw=0.55)
    for tt in range(0, int(t1) + 1, 100):
        cv.line([X(tt)] * 2, [y_axis, y_axis + 2.0], color=INK, lw=0.55)
        cv.text(X(tt), y_axis + 6.3, f"{tt}", ha="center", fontsize=fs)
    cv.text(geo["xlab"], y_axis + 6.3, T["axis_short"], ha="left", fontsize=fs)
    return X


def variant_a2(T, out):
    W, Hh = 234.0, 92.0
    cv = Canvas(W, Hh)
    legend(cv, 2.0, 5.5, [("infer", T["inference"]), ("skip", T["skipped"]),
                          ("exe", T["executed"]), ("disc", T["superseded"])], fs=6.6, gap=5.0, sw=7.0)
    geo = dict(t0=-100, t1=500, x0=44.0, x1=W - 7.0, xlab=2.0, ch=9.0,
               y_sym=18.0, y_inf=26.0, y_prev=34.0, y_new=48.0, y_axis=77.0)
    two_chunk(cv, T, geo)
    cv.save(out / "cand_a2_two_chunk")
    return W, Hh


def variant_c2(T, out):
    W, Hh = 2.40 * 72, 1.45 * 72
    cv = Canvas(W, Hh)
    cv.text(0.0, 6.5, "(b) Native executor", ha="left", fontsize=9.5, weight="bold")
    legend(cv, 0.0, 19.0, [("skip", T["skipped_short"]), ("exe", T["executed"]),
                           ("disc", T["superseded"])], fs=6.6, gap=4.5, sw=7.0)
    geo = dict(t0=-50, t1=450, x0=40.0, x1=W - 6.0, xlab=0.0, ch=9.5,
               y_sym=31.0, y_inf=39.5, y_prev=47.5, y_new=62.0, y_axis=90.0, ol_key="open_loop_short",
               lat_fmt="{L:.0f} ms", lat_dx=3.0)
    two_chunk(cv, T, geo, fs=7.0, fs_cell=6.5)
    cv.save(out / "cand_c2_fig4b_slot")
    return W, Hh


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--font", default="Arial")
    p.add_argument("--lang", choices=["en", "zh"], default="en")
    p.add_argument("--variant", choices=["a", "b", "c", "a2", "c2", "all"], default="all")
    p.add_argument("--output-dir", type=Path, default=HERE / "out")
    a = p.parse_args()
    setup(a.font, a.lang)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    T = TXT[a.lang]
    fns = dict(a=variant_a, b=variant_b, c=variant_c, a2=variant_a2, c2=variant_c2)
    for v in (fns if a.variant == "all" else [a.variant]):
        w, h = fns[v](T, a.output_dir)
        print(f"variant {v}: {w:.0f} x {h:.0f} pt ({w / 72:.2f} x {h / 72:.2f} in)")


if __name__ == "__main__":
    main()
