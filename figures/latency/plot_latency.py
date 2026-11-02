"""Render EN/ZH two-panel latency plots from accepted five-point results.

Run from the repository root: python figures/latency/plot_latency.py
PUMA and final Ours remain pending; their table cells stay NaN and are not plotted.
"""
import argparse
import json
import math
from pathlib import Path
import re
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D

HERE = Path(__file__).resolve().parent
XS = [0, 50, 100, 150, 200]
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
}
GROUPS = [
    ['act', 'dp', 'dynamicvla', 'openwam', 'openwam_official'],
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
}
FIGSIZE = (3.25, 2.38)
INK = '#30363D'

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
            if cell == r'\resultplaceholder':
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
    rows = json.loads(path.read_text(encoding='utf-8'))['rows']
    expected = {(method, x) for method in METHODS for x in XS}
    if len(rows) != len(expected) or {(r['method'], r['extra_latency_ms']) for r in rows} != expected:
        raise ValueError('Expected 45 accepted points: nine methods at five delays.')
    data = {method: sorted((r for r in rows if r['method'] == method),
                           key=lambda r: r['extra_latency_ms']) for method in METHODS}
    for method, points in data.items():
        for x, row, value in zip(XS, points, table[METHODS[method]]):
            lo, hi = row['sr_scene_bootstrap95']
            if row['episodes'] != 1400 or not 0 <= lo <= row['sr_percent'] <= hi <= 100:
                raise ValueError(f'Invalid accepted result: {method}, {x} ms')
            if round(row['sr_percent'], 1) != value:
                raise ValueError(f'Figure/table mismatch: {method}, {x} ms')
    return data

def line_style(method):
    color, marker, line = SERIES[method]
    return dict(color=color, marker=marker, linestyle=line, linewidth=1.1,
                markersize=2.8, markeredgewidth=.65, markeredgecolor=color,
                markerfacecolor='white' if line == '--' else color,
                dash_capstyle='butt', solid_capstyle='round')


def legend_sample(fig, method, x, y, width=.055):
    sample = Line2D([x-width/2, x, x+width/2], [y]*3,
                    transform=fig.transFigure, markevery=[1],
                    clip_on=False, **line_style(method))
    fig.add_artist(sample)


def draw_figure(data, lang):
    zh = lang == 'zh'
    with plt.rc_context({
        'font.family': 'Microsoft YaHei' if zh else 'Arial',
        'font.size': 7, 'text.color': INK, 'axes.labelcolor': INK,
        'xtick.color': INK, 'ytick.color': INK,
        'svg.fonttype': 'none', 'pdf.fonttype': 42,
        'mathtext.fontset': 'stixsans',
        'axes.edgecolor': '#65717C', 'axes.linewidth': .55,
        'xtick.major.width': .5, 'ytick.major.width': .5,
        'xtick.major.size': 2, 'ytick.major.size': 2,
        'xtick.major.pad': 2, 'ytick.major.pad': 2,
    }):
        fig, axes = plt.subplots(1, 2, figsize=FIGSIZE, sharey=True)
        fig.subplots_adjust(left=.12, right=.975, bottom=.32, top=.93, wspace=.17)
        titles = ['基线部署', 'SE(3) 历史'] if zh else ['Baselines', 'SE(3) history']
        for ax, group, letter, title in zip(axes, GROUPS, 'ab', titles):
            for method in group:
                points = data[method]
                values = [r['sr_percent'] for r in points]
                lo, hi = zip(*(r['sr_scene_bootstrap95'] for r in points))
                ax.fill_between(XS, lo, hi, color=SERIES[method][0],
                                alpha=.11, linewidth=0, zorder=2)
                ax.plot(XS, values, label=method, zorder=3, **line_style(method))
            ax.set(xlim=(-7, 207), ylim=(0, 60), xticks=XS, yticks=range(0, 61, 20))
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(axis='y', color='#DDE2E6', linewidth=.4)
            ax.set_axisbelow(True)
            left = ax.get_position().x0
            fig.text(left, .965, f'({letter})', fontsize=7.5, weight='bold', va='center')
            fig.text(left+.065, .965, title, fontsize=7.5, va='center')
        axes[0].set_ylabel('成功率（%）' if zh else 'Success rate (%)', labelpad=3)
        fig.text(.5475, .237, '附加延迟（ms）' if zh else 'Added latency (ms)',
                 ha='center', va='center', fontsize=7.2)

        # The left legend groups short labels on one row. The right matrix
        # factors method identity from history input, instead of repeating names.
        for method, x, y in [('act', .155, .190), ('dp', .365, .190),
                             ('dynamicvla', .155, .142),
                             ('openwam_official', .155, .094), ('openwam', .155, .046)]:
            legend_sample(fig, method, x, y)
            fig.text(x+.04, y, LABELS[METHODS[method]], fontsize=7,
                     fontfamily='Arial', va='center')
        fig.text(.82, .190, '原始' if zh else 'Base', fontsize=7, ha='center', va='center')
        fig.text(.94, .190, '+SE(3)', fontsize=7, ha='center', va='center')
        for base, extended, y in [('pi05', 'pi05_se3', .126),
                                  ('dynamicwam', 'dynamicwam_se3', .062)]:
            fig.text(.58, y, LABELS[METHODS[base]], fontsize=7,
                     fontfamily='Arial', va='center')
            legend_sample(fig, base, .82, y, width=.06)
            legend_sample(fig, extended, .94, y, width=.06)
        return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--table', type=Path, default=HERE.parents[1]/'tables/supp_latency.tex')
    ap.add_argument('--results', type=Path, default=HERE.parents[1]/'results/realtime_c/latency-five-point-20261102.json')
    ap.add_argument('--output', type=Path, default=HERE)
    args = ap.parse_args()
    table = load(args.table)
    data = load_results(args.results, table)
    if not all(math.isnan(v) for method in ('PUMA', r'\ours') for v in table[method]):
        raise ValueError('PUMA/Ours results are now available; update the figure groups and pending note.')
    font_manager.fontManager.addfont(r'C:\Windows\Fonts\msyh.ttc')
    for lang in ('en', 'zh'):
        fig = draw_figure(data, lang)
        suffix = '_zh' if lang == 'zh' else ''
        with plt.rc_context({'svg.fonttype': 'none', 'pdf.fonttype': 42}):
            for ext in ('pdf', 'svg', 'png'):
                output = args.output/f'latency{suffix}.{ext}'
                fig.savefig(output, dpi=600, facecolor='white')
                if ext == 'svg':
                    output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
        plt.close(fig)
    print('EN/ZH exported: two panels, nine configurations, 45 measured points and 95% scene-bootstrap intervals; PUMA/Ours pending.')

if __name__=='__main__':
    main()
