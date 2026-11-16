"""Native-latency executor of OnTimeBench (Sec. 4.3): generic mechanism diagram.

Single-column figure (3.25 in). Symbolic times only. The example uses k_t = 3 and a chunk
of 8 commands, with equal query latencies of 2.4 control periods so each handover
visibly rounds up. The equal execution spans are illustrative, not a protocol rule.

Protocol (appendix/benchmark.tex, "Executor"):
  * command j of the query captured at tau_t is meant for tau_t + j*Delta_a;
  * the chunk is handed over at the first boundary at/after inference ends,
    k_t = ceil(L_t / Delta_a) periods after capture, and runs from command k_t;
  * the policy then observes again and starts the next query while the current chunk
    keeps running, so commands from the next handover on are replaced.

Visual language: contiguous command strips on one shared time axis; action amber
marks execution. State labels sit next to the new chunk instead of in a separate
legend. Flat grey inference bars show the latency and the wait to the next boundary.
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

INK, GREY = "#1A1A1A", "#6E6E6E"
EXE_FC = "#E69F00"                         # core palette: action amber
OVD_FC, OVD_TX = "#E4E4E4", "#6E6E6E"
RULE, REP_TX, INF_FC = "#929292", "#999999", "#D7D7D7"

TXT = {
    "en": dict(ovd="skipped", exe="executed", rep="replaced",
               inf="Inference", prev="Prev. chunk", new="New chunk",
               L=r"$L_t$", nxt=r"$L_{t+1}$", prv=r"$L_{t-1}$", time="time",
               capture="capture", handover="handover", next_event="next handover"),
    "zh": dict(ovd="过期跳过", exe="执行", rep="被替换",
               inf="推理", prev="上一块", new="新块",
               L=r"$L_t$", nxt=r"$L_{t+1}$", prv=r"$L_{t-1}$", time="时间",
               capture="观测采集", handover="交接", next_event="下次交接"),
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
    W, Hh = 234.0, 82.0
    fig = plt.figure(figsize=(W / 72, Hh / 72), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(Hh, 0); ax.axis("off")

    def text(x, y, s, **kw):
        kw.setdefault("va", "center"); kw.setdefault("fontsize", 7)
        return ax.text(x, y, s, **kw)

    def line(xs, ys, **kw):
        kw.setdefault("solid_capstyle", "butt")
        ax.plot(xs, ys, **kw)

    # time in control periods, tau_t = 0
    u0, u1 = -K, 2 * K + 2
    x0, x1 = 47.0, W - 4.0
    X = lambda u: x0 + (u - u0) / (u1 - u0) * (x1 - x0)
    cw = X(1) - X(0)
    ch = 10.0
    y_axis, y_inf, y_prev, y_new = 23.0, 33.0, 43.0, 58.0

    # One time axis owns both the event names and the physical timestamps.
    line([X(u0), X(u1) + 1.5], [y_axis, y_axis], color=INK, lw=0.55)
    ax.annotate("", xy=(X(u1) + 3.0, y_axis), xytext=(X(u1), y_axis),
                arrowprops=dict(arrowstyle="-|>", lw=0.55, color=INK, shrinkA=0, shrinkB=0,
                                mutation_scale=4.5))
    for u in range(u0, u1 + 1):
        major = u in (0, K, 2 * K)
        line([X(u)] * 2, [y_axis - (2.2 if major else 1.3), y_axis], color=INK, lw=0.55)
    for u, s in [(0, r"$\tau_t$"), (K, r"$\tau_t{+}k_t\Delta_a$"), (2 * K, r"$\tau_t{+}2k_t\Delta_a$")]:
        text(X(u), 15.0, s, ha="center")
    for u, label in [(0, T["capture"]), (K, T["handover"]), (2 * K, T["next_event"])]:
        text(X(u), 5.0, label, ha="center", fontsize=6.8)
    text(2.0, y_axis, T["time"], ha="left", color=GREY)
    xa, xb = X(u0), X(u0 + 1)
    text((xa + xb) / 2, 6.5, r"$\Delta_a$", ha="center", color=GREY)
    line([xa, xa, xb, xb], [17, 14.5, 14.5, 17], color=GREY, lw=0.45)

    # Boundary guides connect the time axis to both command strips.
    for u in (0, K, 2 * K):
        line([X(u)] * 2, [y_axis, y_new + ch + 1.0], color=RULE, lw=0.4,
             ls=(0, (1.7, 1.7)), zorder=1)

    # Flat inference bars leave the rounding-to-boundary gap visible.
    text(2.0, y_inf, T["inf"], ha="left")
    for u, label in [(-K, T["prv"]), (0, T["L"]), (K, T["nxt"])]:
        xa, xb = X(u), X(u + L_FRAC)
        ax.add_patch(Rectangle((xa, y_inf - 4.0), xb - xa, 8.0,
                               fc=INF_FC, ec="none", zorder=2))
        text((xa + xb) / 2, y_inf, label, ha="center", fontsize=6.8, zorder=3)

    # A chunk is a continuous strip: one perimeter, with fine command divisions.
    for y, start, label in [(y_prev, -K, T["prev"]), (y_new, 0, T["new"])]:
        text(2.0, y + ch / 2, label, ha="left")
        for lo, hi, fill in [(0, K, OVD_FC), (K, 2 * K, EXE_FC), (2 * K, H, "white")]:
            ax.add_patch(Rectangle((X(start + lo), y), (hi - lo) * cw, ch,
                                   fc=fill, ec="none", zorder=3))
        ax.add_patch(Rectangle((X(start), y), H * cw, ch, fill=False,
                               ec=RULE, lw=0.55, zorder=4))
        for j in range(1, H):
            line([X(start + j)] * 2, [y, y + ch], color=RULE, lw=0.4, zorder=4)
        for j in range(H):
            color = OVD_TX if j < K else (INK if j < 2 * K else REP_TX)
            text(X(start + j) + cw / 2, y + ch / 2 + 0.1, str(j),
                 ha="center", fontsize=6.8, color=color, zorder=5)

    # Direct labels explain the three spans without a separate legend or bracket.
    for lo, hi, label, color in [(0, K, T["ovd"], GREY),
                                  (K, 2 * K, T["exe"], INK),
                                  (2 * K, H, T["rep"], GREY)]:
        text((X(lo) + X(hi)) / 2, 76.0, label, ha="center", color=color)

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
