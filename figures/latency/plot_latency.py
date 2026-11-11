"""Render EN/ZH latency results, plotting only accepted points."""
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

def line_style(method):
    color, marker, line = SERIES[method]
    return dict(color=color, marker=marker, linestyle=line,
                linewidth=1.25 if method == 'ours' else 1.0,
                markersize=3.8 if method == 'ours' else 2.6,
                markeredgewidth=.6, markeredgecolor=color,
                markerfacecolor='white' if line == '--' else color,
                dash_capstyle='butt', solid_capstyle='round')


def legend_sample(fig, method, x, y, width=.055, *, connected=True):
    style = line_style(method)
    if not connected:
        style['linestyle'] = 'none'
    sample = Line2D([x-width/2, x, x+width/2], [y]*3,
                    transform=fig.transFigure, markevery=[1],
                    clip_on=False, **style)
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
        fig.subplots_adjust(left=.12, right=.975, bottom=.40, top=.945, wspace=.17)
        titles = ['策略对比', 'SE(3) 历史'] if zh else ['Policies', 'SE(3) history']
        ymax = 100
        for ax, group, letter, title in zip(axes, GROUPS, 'ab', titles):
            for method in [*group, 'ours']:
                points = [row for row in data[method] if row['sr_percent'] is not None]
                if not points:
                    continue
                delays = [r['extra_latency_ms'] for r in points]
                values = [r['sr_percent'] for r in points]
                lo, hi = zip(*(r['sr_scene_bootstrap95'] for r in points))
                style = line_style(method)
                zorder = 4 if method == 'ours' else 3
                if len(points) == len(XS):
                    ax.fill_between(delays, lo, hi, color=style['color'],
                                    alpha=.09, linewidth=0, zorder=2)
                    ax.plot(delays, values, label=method, zorder=zorder, **style)
                else:
                    style['linestyle'] = 'none'
                    yerr = [[v - l for v, l in zip(values, lo)], [h - v for v, h in zip(values, hi)]]
                    ax.errorbar(delays, values, yerr=yerr, label=method, zorder=zorder,
                                elinewidth=.65, capsize=1.4, **style)
            ax.set(xlim=(-7, 207), ylim=(0, ymax), xticks=XS, yticks=list(range(0, ymax+1, 20)))
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(axis='y', color='#DDE2E6', linewidth=.4)
            ax.set_axisbelow(True)
            left = ax.get_position().x0
            fig.text(left, .975, f'({letter})', fontsize=7.5, weight='bold', va='center')
            fig.text(left+.065, .975, title, fontsize=7.5, va='center')
        axes[0].set_ylabel('成功率（%）' if zh else 'Success rate (%)', labelpad=3)
        fig.text(.5475, .323, '附加延迟（ms）' if zh else 'Added latency (ms)',
                 ha='center', va='center', fontsize=7.2)

        # Smaller labels and wider breathing room in the original four rows.
        for method, x, y in [('act', .153, .270), ('dp', .436, .270),
                             ('dynamicvla', .153, .219), ('puma', .436, .219),
                             ('openwam_official', .153, .168), ('openwam', .153, .117)]:
            if all(row.get('status') == 'missing_t2_v2' for row in data[method]):
                continue
            compact = method in ('dp', 'puma')
            legend_sample(fig, method, x, y, width=.038 if compact else .046)
            fig.text(.470 if compact else .190, y, LABELS[METHODS[method]],
                     fontsize=6.2, fontfamily='Arial', va='center')
        fig.text(.82, .270, '原始' if zh else 'Base', fontsize=6.2, ha='center', va='center')
        fig.text(.94, .270, '+SE(3)', fontsize=6.2, ha='center', va='center')
        for base, extended, y in [('pi05', 'pi05_se3', .219),
                                  ('dynamicwam', 'dynamicwam_se3', .168)]:
            fig.text(.590, y, LABELS[METHODS[base]], fontsize=6.2,
                     fontfamily='Arial', va='center')
            legend_sample(fig, base, .82, y, width=.054)
            legend_sample(fig, extended, .94, y, width=.054)
        legend_sample(fig, 'ours', .422, .073, width=.065,
                      connected=all(row['sr_percent'] is not None for row in data['ours']))
        fig.text(.469, .073, 'FoveaWAM (Ours)', fontsize=6.5,
                 fontfamily='Arial', weight='bold', va='center', color=SERIES['ours'][0])
        return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--table', type=Path, default=HERE.parents[1]/'tables/supp_latency.tex')
    ap.add_argument('--results', type=Path, default=HERE.parents[1]/'results/realtime_c/latency-five-point-20261104.json')
    ap.add_argument('--output', type=Path, default=HERE)
    args = ap.parse_args()
    table = load(args.table)
    data = load_results(args.results, table)
    font_manager.fontManager.addfont(r'C:\Windows\Fonts\msyh.ttc')
    for lang in ('en', 'zh'):
        fig = draw_figure(data, lang)
        suffix = '_zh' if lang == 'zh' else ''
        stem = 'latency'
        with plt.rc_context({'svg.fonttype': 'none', 'pdf.fonttype': 42}):
            for ext in ('pdf', 'svg', 'png'):
                output = args.output/f'{stem}{suffix}.{ext}'
                fig.savefig(output, dpi=600, facecolor='white')
                if ext == 'svg':
                    output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
        plt.close(fig)
    complete = sum(row['sr_percent'] is not None for points in data.values() for row in points)
    print(f'EN/ZH exported: {complete} complete points with scene-bootstrap intervals; {55-complete} missing points omitted.')

if __name__=='__main__':
    main()
