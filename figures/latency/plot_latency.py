"""Render measured EN/ZH latency curves with opaque lines and pointwise 95% CIs."""
import argparse
import json
import math
import numpy as np
from pathlib import Path
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
XS = [0, 50, 100, 150, 200]
# The figure stops at +150 ms: beyond it the 8- and 10-command chunks no longer cover
# the interval to the next chunk. Table S5 keeps all five verified columns.
PLOT_XS = XS[:4]
LABELS = {
    'ACT': 'ACT', 'Diffusion Policy': 'DP', r'$\pi_{0.5}$': r'$\pi_{0.5}$',
    r'$\pi_{0.5}$ + SE(3)': r'$\pi_{0.5}$+SE(3)', 'DynamicVLA': 'DynamicVLA',
    'PUMA': 'PUMA', r'OpenWAM-$\alpha$': r'OpenWAM-$\alpha$',
    r'OpenWAM-$\alpha$ (off)': r'OpenWAM-$\alpha$ (off)',
    'DynamicWAM': 'DynamicWAM', 'DynamicWAM + SE(3)': 'DynamicWAM+SE(3)',
    r'\ours': 'FoveaWAM',
}
# Match the accepted Research preview: deployments left, SE(3) pairs right.
METHODS = {
    'act': 'ACT', 'dp': 'Diffusion Policy', 'dynamicvla': 'DynamicVLA',
    'openwam': r'OpenWAM-$\alpha$ (off)', 'openwam_official': r'OpenWAM-$\alpha$',
    'pi05': r'$\pi_{0.5}$', 'pi05_se3': r'$\pi_{0.5}$ + SE(3)',
    'dynamicwam': 'DynamicWAM', 'dynamicwam_se3': 'DynamicWAM + SE(3)',
    'puma': 'PUMA',
    'ours': r'\ours',
}
GROUPS = [
    ['act', 'dp', 'dynamicvla', 'openwam', 'openwam_official', 'puma'],
    ['pi05', 'pi05_se3', 'dynamicwam', 'dynamicwam_se3'],
]
SERIES = {
    'act': ('#596270', 'o', '-'),
    'dp': ('#A66F28', 's', '-'),
    'dynamicvla': ('#287F78', '^', '-'),
    'openwam': ('#8264A5', 'D', '--'),
    'openwam_official': ('#8264A5', 'D', '-'),
    'pi05': ('#3274A6', 'o', '--'),
    'pi05_se3': ('#3274A6', 'o', '-'),
    'dynamicwam': ('#B45B46', 's', '--'),
    'dynamicwam_se3': ('#B45B46', 's', '-'),
    'puma': ('#287A54', 'P', '-'),
    'ours': ('#B53058', '*', '-.'),
}
FIGSIZE = (3.25, 2.60)

def load(path):
    rows = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.split('&')]
        if cells[0] not in LABELS:
            continue
        if len(cells) != 6 or cells[0] in rows:
            raise ValueError(f'Invalid latency row: {line}')
        values = []
        for cell in cells[1:]:
            cell = cell.removesuffix(r'\\').strip()
            if cell in (r'\resultplaceholder', '--'):
                values.append(math.nan)
            else:
                cell = re.sub(r'\\(?:bestcell|secondcell)\{([0-9.]+)\}',r'\1',cell)
                value = float(cell)
                if not 0 <= value <= 100:
                    raise ValueError(f'SR outside [0, 100]: {cell}')
                values.append(value)
        rows[cells[0]] = values
    if set(rows) != set(LABELS):
        raise ValueError('Latency table methods changed; update the explicit label mapping.')
    return rows

def load_results(path, table):
    rows = [dict(row, method='ours') if row['method']=='se3_wam' else row
            for row in json.loads(path.read_text(encoding='utf-8'))['rows']]
    expected = {(method, x) for method in METHODS for x in XS}
    if len(rows) != len(expected) or {(r['method'], r['extra_latency_ms']) for r in rows} != expected:
        raise ValueError('Expected 55 records: eleven methods at five delays.')
    data = {method: sorted((r for r in rows if r['method'] == method),
                           key=lambda r: r['extra_latency_ms']) for method in METHODS}
    for method, points in data.items():
        for x, row, value in zip(XS, points, table[METHODS[method]]):
            if row.get('status') == 'missing_t2_v2':
                if not (method == 'puma' and row['episodes'] == row['expected'] == 1400
                        and row['completed'] == 1200 and row['missing'] == 200
                        and row['sr_percent'] is None and row['sr_scene_bootstrap95'] is None
                        and math.isnan(value)):
                    raise ValueError(f'Invalid missing T2 result: {method}, {x} ms')
                continue
            if row.get('status') == 'not_evaluated':
                if not (method == 'ours' and x in (50, 100, 200)
                        and row['expected'] == row['missing'] == 1400
                        and row['episodes'] == row['completed'] == 0
                        and row['successes'] is None and row['sr_percent'] is None
                        and row['sr_scene_bootstrap95'] is None and math.isnan(value)):
                    raise ValueError(f'Invalid unevaluated result: {method}, {x} ms')
                continue
            lo, hi = row['sr_scene_bootstrap95']
            if row['episodes'] != 1400 or not 0 <= lo <= row['sr_percent'] <= hi <= 100:
                raise ValueError(f'Invalid accepted result: {method}, {x} ms')
            if round(row['sr_percent'], 1) != value:
                raise ValueError(f'Figure/table mismatch: {method}, {x} ms')
    return data

STYLE = {
    "font.family": "Arial", "font.size": 7,
    "mathtext.fontset": "custom", "mathtext.rm": "Arial",
    "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
    "mathtext.default": "rm", "text.color": "#181818",
    "axes.edgecolor": "#181818", "axes.labelcolor": "#181818",
    "axes.linewidth": .55, "axes.labelsize": 7,
    "xtick.color": "#181818", "ytick.color": "#181818",
    "xtick.major.size": 2.2, "ytick.major.size": 2.2,
    "xtick.major.width": .5, "ytick.major.width": .5,
    "xtick.major.pad": 2.5, "ytick.major.pad": 2.5,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "savefig.facecolor": "white", "figure.facecolor": "white",
    "path.simplify": False,
}


def line_style(method: str) -> dict:
    color, marker, linestyle = SERIES[method]
    # Solid Ours replaces the dash-dot/star combination. The paired variants
    # retain dashed/open versus solid/filled encoding without changing colors.
    if method == "ours":
        marker, linestyle = "o", "-"
    paired_filled = method in {"pi05_se3", "dynamicwam_se3"}
    return dict(
        color=color, marker=marker, linestyle=linestyle,
        linewidth=1.2 if method == "ours" else .85,
        markersize=3.1 if method == "ours" else (2.3 if paired_filled else 2.8),
        markerfacecolor="white" if linestyle == "--" else color,
        markeredgecolor=color, markeredgewidth=.65,
        solid_capstyle="butt", dash_capstyle="butt",
        solid_joinstyle="round", dash_joinstyle="round",
    )


def legend_sample(fig, method, x, y, width=.052):
    artist = Line2D([x - width / 2, x, x + width / 2], [y] * 3,
                    transform=fig.transFigure, markevery=[1],
                    clip_on=False, **line_style(method))
    fig.add_artist(artist)


def draw_figure(data, language):
    zh = language == "zh"
    fonts = ["Arial", "Microsoft YaHei"] if zh else ["Arial"]
    with plt.rc_context({**STYLE, "font.family": fonts}):
        fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, sharey=True, dpi=144)
        fig.subplots_adjust(left=.126, right=.982, bottom=.425, top=.93, wspace=.16)
        titles = ["策略对比", "SE(3) 历史"] if zh else ["Policies", "SE(3) history"]
        rendered = []
        for ax, group, letter, title in zip(axes, GROUPS, "ab", titles):
            for method in [*group, "ours"]:
                points = [p for p in data[method] if p["extra_latency_ms"] in PLOT_XS]
                x = np.array([p["extra_latency_ms"] for p in points])
                y = np.array([p["sr_percent"] for p in points])
                ci = np.array([p["sr_scene_bootstrap95"] for p in points])
                s = line_style(method)
                z = 5 if method == "ours" else 3
                # No ribbons or smoothing: intervals live at measured x only.
                bars = ax.errorbar(x, y, yerr=np.array([y - ci[:, 0], ci[:, 1] - y]),
                                  fmt="none", ecolor=s["color"],
                                  elinewidth=.5, capsize=1.15, capthick=.5,
                                  zorder=z, alpha=1)
                line, = ax.plot(x, y, zorder=z + .2, **s)
                np.testing.assert_array_equal(line.get_xdata(), x)
                np.testing.assert_array_equal(line.get_ydata(), y)
                expected_segments = np.array([[[xx, lo], [xx, hi]]
                                              for xx, (lo, hi) in zip(x, ci)])
                np.testing.assert_allclose(bars.lines[2][0].get_segments(),
                                           expected_segments, rtol=0, atol=1e-12)
                rendered.extend((method, int(xx)) for xx in x)
            ax.set(xlim=(-7, 157), ylim=(0, 100), xticks=PLOT_XS,
                   yticks=np.arange(0, 101, 20))
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="y", color="#E5E5E5", linewidth=.35)
            ax.set_axisbelow(True)
            x0 = ax.get_position().x0
            fig.text(x0, .977, f"({letter})", va="center", fontsize=8, weight="bold")
            fig.text(x0 + .061, .977, title, va="center", fontsize=8)
        axes[0].set_ylabel("成功率（%）" if zh else "Success rate (%)", labelpad=3)
        # Repeat short axis labels to make each panel self-contained.
        for ax in axes:
            ax.set_xlabel("附加延迟（ms）" if zh else "Added latency (ms)", labelpad=4)

        rows = (.266, .211, .156, .101)
        for yy, methods in zip(rows, [("act", "dp"), ("dynamicvla", "puma"),
                                      ("openwam_official",), ("openwam",)]):
            for col, method in enumerate(methods):
                xx = .125 + .258 * col
                legend_sample(fig, method, xx, yy, width=.050)
                fig.text(xx + .039, yy, LABELS[METHODS[method]],
                         va="center", fontsize=7)
        fig.text(.824, rows[0], "原始" if zh else "Base", va="center", ha="center", fontsize=7)
        fig.text(.943, rows[0], "+SE(3)", va="center", ha="center", fontsize=7)
        for yy, (base, extended) in zip(rows[1:], [("pi05", "pi05_se3"),
                                                  ("dynamicwam", "dynamicwam_se3")]):
            fig.text(.566, yy, LABELS[METHODS[base]], va="center", fontsize=7)
            legend_sample(fig, base, .824, yy, width=.059)
            legend_sample(fig, extended, .943, yy, width=.059)
        # One uncertainty key for the shared interval encoding.
        ex, ey = .600, rows[3]
        fig.add_artist(Line2D([ex, ex], [ey - .015, ey + .015],
                             transform=fig.transFigure, color="#444444", lw=.5))
        for yy in (ey - .015, ey + .015):
            fig.add_artist(Line2D([ex - .008, ex + .008], [yy, yy],
                                 transform=fig.transFigure, color="#444444", lw=.5))
        fig.text(.635, ey, "95% 区间" if zh else "95% CI", va="center", fontsize=7)
        legend_sample(fig, "ours", .330, .036, width=.065)
        fig.text(.378, .036, "FoveaWAM (Ours)", va="center", fontsize=7,
                 weight="bold", color=SERIES["ours"][0])
        return fig, rendered



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--table', type=Path, default=HERE.parents[1]/'tables/supp_latency.tex')
    ap.add_argument('--results', type=Path, default=HERE.parents[1]/'results/realtime_c/latency-five-point-20261104.json')
    ap.add_argument('--output', type=Path, default=HERE)
    args = ap.parse_args()
    table = load(args.table)
    data = load_results(args.results, table)
    font_manager.fontManager.addfont(r'C:\Windows\Fonts\msyh.ttc')
    with plt.rc_context(STYLE):
        for lang in ('en', 'zh'):
            fig, rendered = draw_figure(data, lang)
            expected = {(method, x) for method in METHODS for x in PLOT_XS}
            if set(rendered) != expected or len(rendered) != 48:
                raise ValueError("Expected 44 unique points, with Ours repeated in both panels.")
            suffix = '_zh' if lang == 'zh' else ''
            for ext in ('pdf', 'svg', 'png'):
                output = args.output/f'latency{suffix}.{ext}'
                fig.savefig(output, dpi=600, facecolor='white')
                if ext == 'svg':
                    output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
            plt.close(fig)
    plotted = sum(row['sr_percent'] is not None and row['extra_latency_ms'] in PLOT_XS
                  for points in data.values() for row in points)
    print(f'EN/ZH exported: {plotted} points at 0-150 ms with scene-bootstrap intervals; all 55 verified against Table S5.')

if __name__=='__main__':
    main()
