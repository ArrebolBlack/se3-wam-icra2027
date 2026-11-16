"""Native-latency executor of OnTimeBench (Sec. 4.3): generic mechanism diagram.

Single-column figure (3.25 in). The illustrative query latencies are 2.4, 2.4,
and 1.6 control periods, giving k_t = 3 and k_{t+1} = 2 for chunks of 8 commands.
Observation age is measured continuously during command holding (d_task = 0),
not only at discrete command issue times. An optional row shows one Paused chunk.

Protocol (appendix/benchmark.tex, "Executor"):
  * command j of the query captured at tau_t is meant for tau_t + j*Delta_a;
  * the chunk is handed over at the first boundary at/after inference ends,
    k_t = ceil(L_t / Delta_a) periods after capture, and runs from command k_t;
  * the policy then observes again and starts the next query while the current chunk
    keeps running, so commands from the next handover on are replaced.

Visual language: square cells on a shared time axis (cell = one control period);
one accent colour (action amber) for what the robot actually executes; durations drawn
as engineering dimension lines (|<--->|); no rounded boxes, icons or coloured prose.
"""
import argparse
from math import ceil
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent

H = 8
L_PREV, L_CURRENT, L_NEXT = 2.4, 2.4, 1.6  # in control periods; illustrative
K_PREV, K_CURRENT, K_NEXT = (ceil(value) for value in (L_PREV, L_CURRENT, L_NEXT))
NEXT_HANDOVER = K_CURRENT + K_NEXT

INK, GREY, LGREY = "#1A1A1A", "#6E6E6E", "#A8A8A8"
EXE_FC, EXE_EC = "#E69F00", "#9C6B00"        # core palette: action amber
OVD_FC, OVD_EC, OVD_TX = "#DCDCDC", "#A0A0A0", "#5A5A5A"
REP_EC, REP_TX = "#B4B4B4", "#9A9A9A"

TXT = {
    "en": dict(ovd="Skipped", exe="Executed", rep="Replaced",
               inf="Inference", prev="Previous chunk", new="New chunk",
               L=r"$L_t$", nxt=r"$L_{t+1}$", prv=r"$L_{t-1}$", age="obs. age: ", time="time",
               capture="capture", handover="handover = capture", next_event="next handover",
               paused="Paused", replan=r"one chunk; replan every $\Delta_a$"),
    "zh": dict(ovd="已过期，跳过", exe="执行", rep="被替换",
               inf="推理", prev="上一块", new="新块",
               L=r"$L_t$", nxt=r"$L_{t+1}$", prv=r"$L_{t-1}$", age="观测年龄：", time="时间",
               capture="观测采集", handover="交接 = 再次观测", next_event="下次交接",
               paused="Paused", replan=r"单个动作块；每 $\Delta_a$ 重新规划"),
}


def setup(font, lang):
    fonts = [font, "Microsoft YaHei"] if lang == "zh" else [font]
    for f in fonts:  # fail loudly; never fall back silently
        font_manager.findfont(font_manager.FontProperties(family=f), fallback_to_default=False)
    plt.rcParams.update({
        "font.family": fonts, "font.size": 7, "text.color": INK,
        "mathtext.fontset": "custom", "mathtext.rm": font,
        "mathtext.it": f"{font}:italic", "mathtext.bf": f"{font}:bold",
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
        "savefig.facecolor": "white",
    })


def draw(lang, out_stem, paused=False):
    T = TXT[lang]
    W, Hh = 234.0, 132.0 if paused else 94.0
    fig = plt.figure(figsize=(W / 72, Hh / 72), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(Hh, 0); ax.axis("off")

    def text(x, y, s, **kw):
        kw.setdefault("va", "center"); kw.setdefault("fontsize", 7)
        return ax.text(x, y, s, **kw)

    def line(xs, ys, **kw):
        kw.setdefault("solid_capstyle", "butt")
        ax.plot(xs, ys, **kw)

    def dim(xa, xb, y, color, lw=0.6, cap=2.2):
        """Dimension line |<--->| between xa and xb."""
        line([xa, xa], [y - cap / 2, y + cap / 2], color=color, lw=lw)
        line([xb, xb], [y - cap / 2, y + cap / 2], color=color, lw=lw)
        ax.annotate("", xy=(xb, y), xytext=(xa, y),
                    arrowprops=dict(arrowstyle="<|-|>", lw=lw, color=color, shrinkA=0, shrinkB=0,
                                    mutation_scale=4.2))

    # time in control periods, tau_t = 0
    u0, u1 = -K_PREV, H
    x0, x1 = 57.0, W - 8.0
    X = lambda u: x0 + (u - u0) / (u1 - u0) * (x1 - x0)
    cw = X(1) - X(0)
    ch, gap = 10.0, 1.0

    def cell(u, y, state, label):
        fc, ec, tc = {"ovd": (OVD_FC, OVD_EC, OVD_TX),
                      "exe": (EXE_FC, EXE_EC, INK),
                      "rep": ("white", REP_EC, REP_TX)}[state]
        ax.add_patch(Rectangle((X(u) + gap / 2, y), cw - gap, ch, fc=fc, ec=ec, lw=0.5, zorder=3))
        text(X(u) + cw / 2, y + ch / 2 + 0.2, label, ha="center", fontsize=6.8, color=tc, zorder=4)

    # ---------------------------------------------------------------- legend
    lx, ly = x0 + gap / 2, 5.0
    for state, s in [("exe", T["exe"]), ("ovd", T["ovd"]), ("rep", T["rep"])]:
        fc, ec = {"ovd": (OVD_FC, OVD_EC), "exe": (EXE_FC, EXE_EC), "rep": ("white", REP_EC)}[state]
        ax.add_patch(Rectangle((lx, ly - 3.2), 6.4, 6.4, fc=fc, ec=ec, lw=0.5))
        t = text(lx + 9.0, ly + 0.2, s)
        lx += 9.0 + t.get_window_extent(renderer=fig.canvas.get_renderer()).width * 72 / fig.dpi + 10.0

    # ---------------------------------------------------------------- rows
    y_inf, y_prev, y_new = 19.0, 25.0, 39.0
    y_axis = 68.0

    # handover boundaries: thin dashed rules through all rows down to the axis
    for u in (0, K_CURRENT, NEXT_HANDOVER):
        line([X(u)] * 2, [y_inf - 4.5, y_axis], color=GREY, lw=0.45, ls=(0, (2.0, 1.6)), zorder=1)

    # inference lane: one dimension line per query (previous, current, next)
    text(2.0, y_inf, T["inf"], ha="left")
    for u, duration, lab, col in [(-K_PREV, L_PREV, T["prv"], LGREY),
                                  (0, L_CURRENT, T["L"], INK),
                                  (K_CURRENT, L_NEXT, T["nxt"], GREY)]:
        xa, xb = X(u), X(u + duration)
        dim(xa, xb, y_inf, col)
        if lab:
            text((xa + xb) / 2, y_inf - 4.2, lab, ha="center", fontsize=7, color=col,
                 bbox=dict(fc="white", ec="none", pad=0.2))

    for y, start, skipped, executed, lab in [
            (y_prev, -K_PREV, K_PREV, K_CURRENT, T["prev"]),
            (y_new, 0, K_CURRENT, K_NEXT, T["new"])]:
        text(2.0, y + ch / 2, lab, ha="left")
        for j in range(H):
            u = start + j
            if u >= u1:
                break
            cell(u, y, "ovd" if j < skipped else ("exe" if j < skipped + executed else "rep"), str(j))

    # This bracket locates execution; its label gives observation age, not duration.
    yb = y_new + ch + 2.2
    xa, xb = X(K_CURRENT) + gap / 2, X(NEXT_HANDOVER) - gap / 2
    line([xa, xa, xb, xb], [yb, yb + 2.0, yb + 2.0, yb], color=INK, lw=0.5)
    text((xa + xb) / 2, yb + 7.0,
         T["age"] + r"$[k_t,\,k_t{+}k_{t+1})\Delta_a$",
         ha="center", fontsize=6.5, bbox=dict(fc="white", ec="none", pad=0.15))

    if paused:
        line([2.0, X(u1)], [98.0, 98.0], color=LGREY, lw=0.4)
        y_paused = 106.0
        text(2.0, y_paused + ch / 2, T["paused"], ha="left")
        for j in range(H):
            cell(j, y_paused, "exe" if j == 0 else "rep", str(j))
        text((X(0) + X(H)) / 2, 124.0, T["replan"], ha="center", fontsize=6.5,
             bbox=dict(fc="white", ec="none", pad=0.15))

    # ---------------------------------------------------------------- time axis
    line([X(u0), X(u1) + 1.5], [y_axis, y_axis], color=INK, lw=0.55)
    ax.annotate("", xy=(X(u1) + 3.0, y_axis), xytext=(X(u1), y_axis),
                arrowprops=dict(arrowstyle="-|>", lw=0.55, color=INK, shrinkA=0, shrinkB=0,
                                mutation_scale=4.5))
    for u in range(u0, u1 + 1):
        major = u in (0, K_CURRENT, NEXT_HANDOVER)
        line([X(u)] * 2, [y_axis, y_axis + (2.4 if major else 1.4)], color=INK, lw=0.55)
    for u, s in [(0, r"$\tau_t$"), (K_CURRENT, r"$\tau_{t+1}$")]:
        text(X(u), y_axis + 8.0, s, ha="center")
    text(X(NEXT_HANDOVER) + 4.0, y_axis + 8.0,
         r"$\tau_{t+1}{+}k_{t+1}\Delta_a$", ha="left", fontsize=6.5)
    for u, label in [(0, T["capture"]), (K_CURRENT, T["handover"])]:
        text(X(u), y_axis + 18.0, label, ha="center", fontsize=6.5)
    text(X(NEXT_HANDOVER) + 4.0, y_axis + 18.0, T["next_event"], ha="left", fontsize=6.5)
    text(2.0, y_axis + 8.0, T["time"], ha="left", color=GREY)

    for ext in ("png", "pdf", "svg"):
        fig.savefig(f"{out_stem}.{ext}", dpi=300)
    plt.close(fig)
    return W, Hh


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--font", default="Arial")
    p.add_argument("--lang", choices=["en", "zh"], default="en")
    p.add_argument("--paused", action="store_true", help="add one Paused chunk as an optional comparison")
    p.add_argument("--output-dir", type=Path, default=HERE / "out")
    a = p.parse_args()
    setup(a.font, a.lang)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    stem = a.output_dir / ("protocol_timeline" + ("_paused" if a.paused else "")
                           + ("_zh" if a.lang == "zh" else ""))
    w, h = draw(a.lang, stem, paused=a.paused)
    print(f"{stem}: {w:.0f} x {h:.0f} pt ({w / 72:.2f} x {h / 72:.2f} in)")


if __name__ == "__main__":
    main()
