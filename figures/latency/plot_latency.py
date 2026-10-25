"""SR versus added latency (main-text figure, single column).

Reads data/latency.csv (one row per method and added latency; empty SR = pending) and
writes latency.pdf / latency.svg / latency.png. Six series: the strongest method of each
baseline class plus SE(3)-WAM; every method's numbers stay in Table supp_latency.

    python plot_latency.py --output .
"""
import argparse, csv, math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

# key: (label, color, marker, linewidth, zorder). Colors follow the shared figure palette;
# SE(3)-WAM uses the "better" blue of the ablation heatmap.
SERIES = {
    'ACT':            ('ACT',              '#7F7F7F', 'o', 1.0, 3),
    'pi05_se3':       (r'$\pi_{0.5}$+SE(3)', '#E69F00', 's', 1.0, 3),
    'DynamicVLA':     ('DynamicVLA',       '#009E73', '^', 1.0, 3),
    # Set to the stronger of DreamVLA and OpenWAM-alpha once both are measured.
    'image_wam':      ('OpenWAM-$\\alpha$', '#CC79A7', 'D', 1.0, 3),
    'DynamicWAM_se3': ('DynamicWAM+SE(3)', '#8C564B', 'v', 1.0, 3),
    'ours':           ('SE(3)-WAM',        '#1674AB', 'o', 1.8, 5),
}
XS = [0, 50, 100, 150, 200]


def num(s):
    s = (s or '').strip()
    return float(s) if s else math.nan


def load(path):
    rows = {}
    with open(path, newline='') as f:
        lines = [l for l in f if not l.startswith('#')]
    for r in csv.DictReader(lines):
        rows.setdefault(r['method'], {})[int(r['added_ms'])] = (num(r['sr']), num(r['sr_lo']), num(r['sr_hi']))
    return rows


def font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    return 'Arial' if 'Arial' in names else 'Liberation Sans'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', default=Path(__file__).with_name('data') / 'latency.csv')
    ap.add_argument('--output', default='.')
    a = ap.parse_args()
    data = load(a.data)
    plt.rcParams.update({'font.family': font(), 'font.size': 7.5, 'svg.fonttype': 'none',
                         'pdf.fonttype': 42, 'axes.unicode_minus': True, 'axes.linewidth': .6,
                         'xtick.major.width': .6, 'ytick.major.width': .6,
                         'xtick.major.size': 2.5, 'ytick.major.size': 2.5})
    fig = plt.figure(figsize=(3.25, 1.9), dpi=144)
    ax = fig.add_axes([0.12, 0.2, 0.56, 0.74])
    ax.axvline(150, color='#B0B0B0', lw=.6, ls=(0, (3, 2)), zorder=1)
    ax.text(150, 98, 'Table 1', fontsize=6.5, color='#808080', ha='center', va='top',
            bbox=dict(facecolor='white', edgecolor='none', pad=.6))
    pending, labels = [], []
    for key, (label, color, marker, lw, z) in SERIES.items():
        pts = [(x, *data.get(key, {}).get(x, (math.nan,) * 3)) for x in XS]
        have = [(x, y, lo, hi) for x, y, lo, hi in pts if not math.isnan(y)]
        if not have:
            pending.append(label)
            continue
        bands = [(x, lo, hi) for x, y, lo, hi in have if not (math.isnan(lo) or math.isnan(hi))]
        if bands:
            ax.fill_between([b[0] for b in bands], [b[1] for b in bands], [b[2] for b in bands],
                            color=color, alpha=.18, lw=0, zorder=z - 1)
        # Connect only adjacent measured latencies; an unmeasured point is never interpolated.
        run = []
        for x, y, lo, hi in pts + [(None, math.nan, 0, 0)]:
            if not math.isnan(y):
                run.append((x, y)); continue
            if run:
                ax.plot([r[0] for r in run], [r[1] for r in run], color=color, lw=lw, marker=marker,
                        ms=3.2 if key != 'ours' else 3.8, mec='white', mew=.4, zorder=z, clip_on=False)
            run = []
        labels.append([have[-1][1], have[-1][0], label, color, key == 'ours'])
    # Direct labels at the last measured point, spread to avoid overlap.
    labels.sort(key=lambda t: t[0])
    gap, prev = 7.0, -1e9
    for t in labels:
        t.append(max(t[0], prev + gap)); prev = t[-1]
    for y, x, label, color, bold, yl in labels:
        ax.annotate(label, xy=(x, y), xytext=(206, yl), textcoords='data', fontsize=7,
                    color=color, fontweight='bold' if bold else 'normal', va='center', ha='left',
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle='-', color=color, lw=.4, shrinkA=0, shrinkB=2)
                    if x != 200 or abs(yl - y) > .5 else None)
    ax.set_xlim(0, 200); ax.set_ylim(0, 100)
    ax.set_xticks(XS); ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel('Added latency (ms)', labelpad=1.5)
    ax.set_ylabel('SR (%)', labelpad=1.5)
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='y', color='#E6E6E6', lw=.5, zorder=0)
    if pending:
        fig.text(0.70, 0.94, 'Design preview.\nPending:\n' + '\n'.join(pending), fontsize=6.5,
                 color='#808080', va='top', ha='left', linespacing=1.25)
    out = Path(a.output)
    for ext in ('pdf', 'svg', 'png'):
        fig.savefig(out / f'latency.{ext}', dpi=300 if ext == 'png' else None)


if __name__ == '__main__':
    main()
