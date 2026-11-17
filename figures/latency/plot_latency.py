"""Render EN/ZH latency sweeps and paused/native rankings from accepted results."""
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
COLORS = json.loads((HERE.parent / 'method_colors.json').read_text(encoding='utf-8'))
METHOD_COLORS = COLORS['methods']
CATEGORY_COLORS = COLORS['categories']
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
    'act': ('ACT', 'o', '-'),
    'dp': ('DP', 's', '-'),
    'dynamicvla': ('DynamicVLA', '^', '-'),
    'openwam': ('OpenWAM-α (off)', 'D', '--'),
    'openwam_official': ('OpenWAM-α', 'D', '-'),
    'pi05': ('π0.5', 'o', '--'),
    'pi05_se3': ('π0.5+SE(3)', 'o', '-'),
    'dynamicwam': ('DynamicWAM', 's', '--'),
    'dynamicwam_se3': ('DynamicWAM+SE(3)', 's', '-'),
    'puma': ('PUMA', 'P', '-'),
    'ours': ('FoveaWAM', 'o', '-'),
}
FIGSIZE = (3.25, 4.50)
CLASSES = {
    'act': 'Reactive', 'dp': 'Reactive',
    'pi05': 'VLA', 'pi05_se3': 'VLA', 'dynamicvla': 'VLA', 'puma': 'VLA',
    'openwam': 'Video WAM', 'openwam_official': 'Video WAM',
    'dynamicwam': 'Video WAM', 'dynamicwam_se3': 'Video WAM',
    'ours': 'FoveaWAM',
}

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
    color_key, marker, linestyle = SERIES[method]
    color = METHOD_COLORS[color_key]
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


def load_comparison(path, data):
    rows = [dict(row, method='ours') if row['method'] == 'se3_wam' else row
            for row in json.loads(path.read_text(encoding='utf-8'))['rows']
            if row['protocol'] in ('native', 'paused')]
    records = {(row['method'], row['protocol']): row for row in rows}
    expected = {(method, protocol) for method in METHODS for protocol in ('native', 'paused')}
    if len(rows) != len(expected) or set(records) != expected:
        raise ValueError('Expected native and paused results for all eleven methods.')
    comparison = []
    for method in METHODS:
        native, paused = (records[method, protocol] for protocol in ('native', 'paused'))
        if any(row['episodes'] != 1400 or not 0 <= row['sr_percent'] <= 100
               for row in (native, paused)):
            raise ValueError(f'Invalid Table 1 result: {method}')
        if native['sr_percent'] != data[method][0]['sr_percent']:
            raise ValueError(f'Table 1/latency sweep mismatch: {method}')
        comparison.append((method, paused['sr_percent'], native['sr_percent'],
                           native['measured_5090_p95_ms']))
    return sorted(comparison, key=lambda row: -row[1])


def draw_figure(data, comparison, language):
    """Use the author's fig6_full.py layout, with the existing EN/ZH export path."""
    zh = language == "zh"
    fonts = ["Arial", "Microsoft YaHei"] if zh else ["Arial"]
    with plt.rc_context({**STYLE, "font.family": fonts}):
        fig = plt.figure(figsize=FIGSIZE, dpi=300)
        w, h = FIGSIZE

        def ax_in(x, y, width, height):
            return fig.add_axes([x / w, y / h, width / w, height / h])

        def text(x, y, label, **kwargs):
            return fig.text(x / w, y / h, label, va="center", **kwargs)

        def title(x, y, letter, label):
            text(x, y, f"({letter})", fontsize=8, weight="bold")
            text(x + .2, y, label, fontsize=8, weight="bold")

        def sample(method, x, y, width=.17):
            fig.add_artist(Line2D([(x - width / 2) / w, x / w, (x + width / 2) / w],
                                 [y / h] * 3, transform=fig.transFigure, markevery=[1],
                                 clip_on=False, **line_style(method)))

        def dot(x, y, filled, color="#555555"):
            fig.add_artist(Line2D([x / w], [y / h], transform=fig.transFigure,
                                 ls="", marker="o", ms=3.2 if filled else 3.0,
                                 mfc=color if filled else "white", mec=color, mew=.7))

        # (a, b): measured latency sweeps; preserve the accepted line/CI encoding.
        ab_y, ab_h, ab_w = 3.06, 1.22, 1.38
        axa = ax_in(.41, ab_y, ab_w, ab_h)
        axb = ax_in(1.84, ab_y, ab_w, ab_h)
        rendered = []
        for ax, group in zip((axa, axb), GROUPS):
            for method in [*group, "ours"]:
                points = [p for p in data[method] if p["extra_latency_ms"] in PLOT_XS]
                x = np.array([p["extra_latency_ms"] for p in points])
                y = np.array([p["sr_percent"] for p in points])
                ci = np.array([p["sr_scene_bootstrap95"] for p in points])
                s = line_style(method)
                z = 5 if method == "ours" else 3
                bars = ax.errorbar(x, y, yerr=np.array([y - ci[:, 0], ci[:, 1] - y]),
                                  fmt="none", ecolor=s["color"], elinewidth=.5,
                                  capsize=1.15, capthick=.5, zorder=z)
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
            ax.set_xlabel("附加延迟（ms）" if zh else "Added latency (ms)", labelpad=3)
        axb.tick_params(labelleft=False)
        axa.set_ylabel("成功率（%）" if zh else "Success rate (%)", labelpad=3)
        title(.41, ab_y + ab_h + .13, "a", "策略对比" if zh else "Policies")
        title(1.84, ab_y + ab_h + .13, "b", "SE(3) 历史" if zh else "SE(3) history")

        lg = 2.68
        rows = [lg, lg - .13, lg - .26, lg - .39]
        for yy, methods in zip(rows, [("act", "dp"), ("dynamicvla", "puma"),
                                      ("openwam_official",), ("openwam",)]):
            for col, method in enumerate(methods):
                xx = .50 + .80 * col
                sample(method, xx, yy)
                text(xx + .13, yy, LABELS[METHODS[method]])
        text(2.68, rows[0], "原始" if zh else "Base", ha="center")
        text(3.06, rows[0], "+SE(3)", ha="center")
        for yy, (base, extended) in zip(rows[1:3], [("pi05", "pi05_se3"),
                                                    ("dynamicwam", "dynamicwam_se3")]):
            text(1.86, yy, LABELS[METHODS[base]])
            sample(base, 2.68, yy, .19)
            sample(extended, 3.06, yy, .19)
        ex, ey = 1.95, rows[3]
        fig.add_artist(Line2D([ex / w] * 2, [(ey - .05) / h, (ey + .05) / h],
                             transform=fig.transFigure, color="#444444", lw=.5))
        for yy in (ey - .05, ey + .05):
            fig.add_artist(Line2D([(ex - .025) / w, (ex + .025) / w], [yy / h] * 2,
                                 transform=fig.transFigure, color="#444444", lw=.5))
        text(ex + .09, ey, "95% 区间" if zh else "95% CI")
        sample("ours", 1.05, lg - .52, .21)
        text(1.21, lg - .52, "FoveaWAM（本文）" if zh else "FoveaWAM (Ours)",
             weight="bold", color=CATEGORY_COLORS["FoveaWAM"])

        # (c): Table 1, ordered by paused SR and colored by the Fig. 1 classes.
        rank_p = {r[0]: i + 1 for i, r in enumerate(comparison)}
        rank_n = {r[0]: i + 1 for i, r in enumerate(sorted(comparison, key=lambda r: -r[2]))}
        c_y, c_h, c_x, c_w = .47, 1.18, 1.02, 1.40
        axc = ax_in(c_x, c_y, c_w, c_h)
        n = len(comparison)
        axc.set_ylim(n - .5, -.5)
        x_p95, x_rp, x_rn = 2.60, 2.86, 3.07
        for i, (method, paused, native, latency) in enumerate(comparison):
            color = CATEGORY_COLORS[CLASSES[method]]
            yy = c_y + c_h * (n - .5 - i) / n
            axc.annotate("", xy=(native, i), xytext=(paused, i),
                         arrowprops=dict(arrowstyle="-|>,head_length=0.32,head_width=0.15",
                                         lw=.8, color=color, shrinkA=2.3, shrinkB=.4))
            axc.plot(paused, i, "o", ms=3.0, mfc="white", mec=color, mew=.7, zorder=4)
            axc.plot(native, i, "o", ms=3.2, color=color, zorder=5)
            text(c_x - .05, yy, LABELS[METHODS[method]], ha="right",
                 weight="bold" if method == "ours" else "normal")
            text(x_p95, yy, f"{latency:.0f}", ha="center")
            delta = rank_p[method] - rank_n[method]
            text(x_rp + .06, yy, str(rank_p[method]), ha="right", color="#7F7F7F")
            text(x_rp + .13, yy, "→", ha="center", color="#7F7F7F")
            text(x_rn + .15, yy, str(rank_n[method]), ha="right",
                 color="#181818" if delta == 0 else ("#2CA02C" if delta > 0 else "#D62728"),
                 weight="normal" if delta == 0 else "bold")
        hy1, hy2 = c_y + c_h + .07, c_y + c_h + .20
        text(x_p95, hy2, "p95", ha="center")
        text(x_p95, hy1, "(ms)", ha="center")
        text(x_rp + .13, hy2, "名次" if zh else "Rank", ha="center")
        dot(x_rp + .03, hy1, False)
        text(x_rp + .13, hy1, "→", ha="center", color="#7F7F7F")
        dot(x_rn + .10, hy1, True)
        kx = c_x + .02
        dot(kx, hy1, False)
        text(kx + .06, hy1, "暂停" if zh else "Paused")
        dot(kx + .55, hy1, True)
        text(kx + .61, hy1, "原生" if zh else "Native")
        axc.set_xlim(10, 95)
        axc.set_yticks([])
        axc.spines[["left", "right", "top"]].set_visible(False)
        axc.set_xticks([20, 40, 60, 80])
        axc.set_xlabel("成功率（%）" if zh else "Success rate (%)", labelpad=3)
        axc.grid(axis="x", color="#E5E5E5", lw=.35)
        axc.set_axisbelow(True)
        title(.02, hy2, "c", "暂停与原生延迟" if zh else "Paused vs. native")
        kx, ky = .80, .07
        for cls in ("Video WAM", "VLA", "Reactive"):
            dot(kx, ky, True, CATEGORY_COLORS[cls])
            text(kx + .06, ky, {"Video WAM": "视频 WAM", "VLA": "VLA",
                                "Reactive": "反应式"}[cls] if zh else cls)
            kx += .06 + {"Video WAM": .62, "VLA": .33, "Reactive": .5}[cls] + .12
        return fig, rendered



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--table', type=Path, default=HERE.parents[1]/'tables/supp_latency.tex')
    ap.add_argument('--results', type=Path, default=HERE.parents[1]/'results/realtime_c/latency-five-point-20261104.json')
    ap.add_argument('--comparison', type=Path, default=HERE.parents[1]/'results/realtime_c/table1-20261104.json')
    ap.add_argument('--output', type=Path, default=HERE)
    args = ap.parse_args()
    table = load(args.table)
    data = load_results(args.results, table)
    comparison = load_comparison(args.comparison, data)
    font_manager.fontManager.addfont(r'C:\Windows\Fonts\msyh.ttc')
    with plt.rc_context(STYLE):
        for lang in ('en', 'zh'):
            fig, rendered = draw_figure(data, comparison, lang)
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
    print(f'EN/ZH exported: {plotted} points at 0-150 ms with scene-bootstrap intervals; '
          f'all 55 verified against Table S5; {len(comparison)} paused/native comparisons from Table 1.')

if __name__=='__main__':
    main()
