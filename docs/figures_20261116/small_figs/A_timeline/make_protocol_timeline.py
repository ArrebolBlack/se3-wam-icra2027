"""Native-latency executor of OnTimeBench (Sec. 4.3): generic mechanism diagram.

Single-column figure (3.25 in). Symbolic times only; the example uses k_t = 3 and a chunk of
H_m = 8 commands, with L_t between 2 and 3 control periods to show the rounding-up.
Protocol (appendix/benchmark.tex, "Executor"):
  * command j of the query captured at tau_t is meant for tau_t + j*Delta_a;
  * the chunk is handed over at the first boundary at/after inference ends,
    k_t = ceil(L_t / Delta_a) periods after capture, and runs from command k_t;
  * the policy then observes again and starts the next query; the previous chunk keeps
    running meanwhile, so commands from the next handover on are replaced.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

HERE = Path(__file__).resolve().parent

K, H, L_FRAC = 3, 8, 2.4          # k_t, H_m, L_t / Delta_a  (illustrative)

INK, GREY, MID = "#1A1A1A", "#6E6E6E", "#9A9A9A"
EXE_FC, EXE_EC, EXE_TXT = "#F1CA73", "#B37C00", "#8A5F00"   # action amber (Fig. 3 tokens)
SKIP_FC, SKIP_EC = "#C9C9C9", "#8C8C8C"
REP_EC = "#BDBDBD"

TXT = {
    "en": dict(skip="Skipped (overdue)", exe="Executed", rep="Replaced",
               prev="Prev. chunk", new="New chunk", policy="Policy",
               infer=r"inference $L_t$", nxt="next query",
               exe_iv="executed open-loop"),
    "zh": dict(skip="跳过（已过期）", exe="执行", rep="被替换",
               prev="上一块", new="新块", policy="策略",
               infer=r"推理 $L_t$", nxt="下一次查询",
               exe_iv="开环执行"),
}


def setup(font, lang):
    fonts = [font, "Microsoft YaHei"] if lang == "zh" else [font]
    for f in fonts:
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
    W, Hh = 234.0, 74.0
    fig = plt.figure(figsize=(W / 72, Hh / 72), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W); ax.set_ylim(Hh, 0); ax.axis("off")

    def text(x, y, s, **kw):
        kw.setdefault("va", "center"); kw.setdefault("fontsize", 7)
        return ax.text(x, y, s, **kw)

    def line(xs, ys, **kw):
        ax.plot(xs, ys, solid_capstyle="butt", **kw)

    # time in units of Delta_a; tau_t = 0
    u0, u1 = -K, 2 * K + 2            # previous chunk starts at -K; show new chunk to H
    x0, x1 = 44.0, W - 2.5
    X = lambda u: x0 + (u - u0) / (u1 - u0) * (x1 - x0)
    cw = X(1) - X(0)
    ch, gap = 10.0, 1.1

    def cell(u, y, state, label):
        fc, ec, tc = {"skip": (SKIP_FC, SKIP_EC, "#4D4D4D"),
                      "exe": (EXE_FC, EXE_EC, INK),
                      "rep": ("white", REP_EC, MID)}[state]
        ax.add_patch(FancyBboxPatch((X(u) + gap / 2, y), cw - gap, ch,
                                    boxstyle="round,pad=0,rounding_size=1.2",
                                    fc=fc, ec=ec, lw=0.5, zorder=3))
        if label is not None:
            text(X(u) + cw / 2, y + ch / 2 + 0.2, label, ha="center", fontsize=6.8, color=tc, zorder=4)

    # ---- legend (VLASH-style single row)
    lx, ly = 2.0, 5.5
    for state, s in [("skip", T["skip"]), ("exe", T["exe"]), ("rep", T["rep"])]:
        ax.add_patch(FancyBboxPatch((lx, ly - 3.3), 7.5, 6.6, boxstyle="round,pad=0,rounding_size=1.0",
                                    fc={"skip": SKIP_FC, "exe": EXE_FC, "rep": "white"}[state],
                                    ec={"skip": SKIP_EC, "exe": EXE_EC, "rep": REP_EC}[state], lw=0.5))
        t = text(lx + 10.0, ly, s, fontsize=7)
        bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
        lx += 10.0 + bb.width * 72 / fig.dpi + 9.0

    # ---- rows
    y_mark, y_pol, y_prev, y_new = 15.5, 29.0, 34.5, 48.0
    y_bot = y_new + ch

    # boundary markers
    marks = [(0, r"$\tau_t$"), (K, r"$\tau_t{+}k_t\Delta_a$"), (2 * K, r"$\tau_t{+}2k_t\Delta_a$")]
    for u, s in marks:
        line([X(u)] * 2, [y_mark + 4.0, y_bot + 2.0], color=GREY, lw=0.5, ls=(0, (2.4, 1.6)), zorder=1)
        text(X(u), y_mark, s, ha="center", fontsize=7)

    # policy lane: inference spans as capped arrows
    text(2.0, y_pol - 1.5, T["policy"], ha="left")
    for u, lab, col in [(-K, None, "#B0B0B0"), (0, T["infer"], INK), (K, T["nxt"], GREY)]:
        xa, xb = max(X(u), X(u0)) + 0.3, X(u + L_FRAC)
        ax.annotate("", xy=(xb, y_pol), xytext=(xa, y_pol),
                    arrowprops=dict(arrowstyle="-|>", lw=0.8, color=col, shrinkA=0, shrinkB=0,
                                    mutation_scale=5), zorder=4)
        ax.plot([xa], [y_pol], marker="o", ms=2.6, mfc=col, mec="white", mew=0.4, zorder=5)
        if lab:
            text((xa + xb) / 2, y_pol - 4.3, lab, ha="center", fontsize=6.6, color=col)
    # one cell = one control period (VLASH-style span mark)
    xa, xb = X(2 * K + 1) + 0.6, X(2 * K + 2) - 0.6
    yd = y_new - 2.2
    line([xa, xa, xb, xb], [yd + 1.4, yd, yd, yd + 1.4], color=GREY, lw=0.5)
    text((xa + xb) / 2, yd - 4.0, r"$\Delta_a$", ha="center", fontsize=6.6, color=GREY)

    # previous chunk (captured at tau_t - k Delta_a) and new chunk (captured at tau_t)
    for y, start, lab in [(y_prev, -K, T["prev"]), (y_new, 0, T["new"])]:
        text(2.0, y + ch / 2, lab, ha="left")
        for j in range(H):
            u = start + j
            if u >= u1:
                break
            state = "skip" if j < K else ("exe" if j < 2 * K else "rep")
            cell(u, y, state, str(j))

    # execution-interval bracket under the new chunk's executed commands (VLASH-style)
    yb = y_bot + 2.0
    xa, xb = X(K) + 0.8, X(2 * K) - 0.8
    line([xa, xa, xb, xb], [yb, yb + 2.2, yb + 2.2, yb], color=EXE_EC, lw=0.6)
    text((xa + xb) / 2, yb + 7.6, T["exe_iv"], ha="center", fontsize=7, color=EXE_TXT, style="italic")

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
