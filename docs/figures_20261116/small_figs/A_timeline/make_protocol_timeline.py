"""Native-latency executor of OnTimeBench (Sec. 4.3): generic mechanism diagram.

Single-column figure (3.25 in). Symbolic times only. The example uses k_t = 3 and a chunk
of 8 commands, with L_t ~ 2.4 control periods so the handover visibly rounds up.

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
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import Rectangle

HERE = Path(__file__).resolve().parent

K, H, L_FRAC = 3, 8, 2.4            # k_t, chunk length, L_t / Delta_a (illustrative)

INK, GREY, LGREY = "#1A1A1A", "#6E6E6E", "#A8A8A8"
EXE_FC, EXE_EC = "#E69F00", "#9C6B00"        # core palette: action amber
OVD_FC, OVD_EC, OVD_TX = "#DCDCDC", "#A0A0A0", "#5A5A5A"
REP_EC, REP_TX = "#B4B4B4", "#9A9A9A"

TXT = {
    "en": dict(ovd="Overdue, skipped", exe="Executed", rep="Replaced",
               inf="Inference", prev="Previous chunk", new="New chunk",
               L=r"$L_t$", nxt=r"$L_{t+1}$", prv=r"$L_{t-1}$", open="open loop", time="time"),
    "zh": dict(ovd="已过期，跳过", exe="执行", rep="被替换",
               inf="推理", prev="上一块", new="新块",
               L=r"$L_t$", nxt=r"$L_{t+1}$", prv=r"$L_{t-1}$", open="开环执行", time="时间"),
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


def draw(lang, out_stem):
    T = TXT[lang]
    W, Hh = 234.0, 78.0
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
    u0, u1 = -K, 2 * K + 2
    x0, x1 = 57.0, W - 4.0
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
    y_inf, y_prev, y_new, y_axis = 19.0, 25.0, 39.0, 63.0

    # handover boundaries: thin dashed rules through all rows down to the axis
    for u in (0, K, 2 * K):
        line([X(u)] * 2, [y_inf - 4.5, y_axis], color=GREY, lw=0.45, ls=(0, (2.0, 1.6)), zorder=1)

    # inference lane: one dimension line per query (previous, current, next)
    text(2.0, y_inf, T["inf"], ha="left")
    for u, lab, col in [(-K, T["prv"], LGREY), (0, T["L"], INK), (K, T["nxt"], GREY)]:
        xa, xb = max(X(u), X(u0)), X(u + L_FRAC)
        if u >= u0:
            dim(xa, xb, y_inf, col)
        else:  # previous query started before the window: no left cap
            line([xa, xb - 1.2], [y_inf, y_inf], color=col, lw=0.6)
            ax.annotate("", xy=(xb, y_inf), xytext=(xb - 3, y_inf),
                        arrowprops=dict(arrowstyle="-|>", lw=0.6, color=col, shrinkA=0, shrinkB=0,
                                        mutation_scale=4.2))
            line([xb, xb], [y_inf - 1.1, y_inf + 1.1], color=col, lw=0.6)
        if lab:
            text((xa + xb) / 2, y_inf - 4.2, lab, ha="center", fontsize=7, color=col,
                 bbox=dict(fc="white", ec="none", pad=0.2))

    for y, start, lab in [(y_prev, -K, T["prev"]), (y_new, 0, T["new"])]:
        text(2.0, y + ch / 2, lab, ha="left")
        for j in range(H):
            u = start + j
            if u >= u1:
                break
            cell(u, y, "ovd" if j < K else ("exe" if j < 2 * K else "rep"), str(j))

    # open-loop span of the new chunk
    yb = y_new + ch + 2.2
    xa, xb = X(K) + gap / 2, X(2 * K) - gap / 2
    line([xa, xa, xb, xb], [yb, yb + 2.0, yb + 2.0, yb], color=INK, lw=0.5)
    text((xa + xb) / 2, yb + 6.6, T["open"], ha="center")

    # ---------------------------------------------------------------- time axis
    line([X(u0), X(u1) + 1.5], [y_axis, y_axis], color=INK, lw=0.55)
    ax.annotate("", xy=(X(u1) + 3.0, y_axis), xytext=(X(u1), y_axis),
                arrowprops=dict(arrowstyle="-|>", lw=0.55, color=INK, shrinkA=0, shrinkB=0,
                                mutation_scale=4.5))
    for u in range(u0, u1 + 1):
        major = u in (0, K, 2 * K)
        line([X(u)] * 2, [y_axis, y_axis + (2.4 if major else 1.4)], color=INK, lw=0.55)
    for u, s in [(0, r"$\tau_t$"), (K, r"$\tau_t{+}k_t\Delta_a$"), (2 * K, r"$\tau_t{+}2k_t\Delta_a$")]:
        text(X(u), y_axis + 8.0, s, ha="center")
    text(2.0, y_axis + 8.0, T["time"], ha="left", color=GREY)
    # one tick interval = one control period
    xa, xb = X(u1 - 1), X(u1)
    text((xa + xb) / 2, y_axis + 8.0, r"$\Delta_a$", ha="center", color=GREY)
    dim(xa + 0.4, xb - 0.4, y_axis - 3.0, GREY, lw=0.45, cap=1.6)

    for ext in ("png", "pdf", "svg"):
        fig.savefig(f"{out_stem}.{ext}", dpi=300)
    plt.close(fig)
    return W, Hh


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--font", default="Arial")
    p.add_argument("--lang", choices=["en", "zh"], default="en")
    p.add_argument("--output-dir", type=Path, default=HERE / "out")
    a = p.parse_args()
    setup(a.font, a.lang)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    stem = a.output_dir / ("protocol_timeline" + ("_zh" if a.lang == "zh" else ""))
    w, h = draw(a.lang, stem)
    print(f"{stem}: {w:.0f} x {h:.0f} pt ({w / 72:.2f} x {h / 72:.2f} in)")


if __name__ == "__main__":
    main()
