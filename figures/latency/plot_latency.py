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

HERE = Path(__file__).resolve().parent
XS = [0, 50, 100, 150, 200]
LABELS = {
    'ACT': 'ACT', 'Diffusion Policy': 'DP', r'$\pi_{0.5}$': r'$\pi_{0.5}$',
    r'$\pi_{0.5}$ + SE(3)': r'$\pi_{0.5}$+SE(3)', 'DynamicVLA': 'DynamicVLA',
    'PUMA': 'PUMA', r'OpenWAM-$\alpha$': r'OpenWAM-$\alpha$',
    r'OpenWAM-$\alpha$ (off)': r'OpenWAM-$\alpha$ (off)',
    'DynamicWAM': 'DynamicWAM', 'DynamicWAM + SE(3)': 'DynamicWAM+SE(3)',
    r'\ours': 'SE(3)-WAM',
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
    'act': ('#4D4D4D', 'o', '-'),
    'dp': ('#B64342', 's', '-'),
    'dynamicvla': ('#42949E', '^', '-'),
    'openwam': ('#9A4D8E', 'v', '--'),
    'openwam_official': ('#9A4D8E', 'D', '-'),
    'pi05': ('#3775BA', 'o', '--'),
    'pi05_se3': ('#0F4D92', 'o', '-'),
    'dynamicwam': ('#E9A6A1', 's', '--'),
    'dynamicwam_se3': ('#B64342', 's', '-'),
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--table',type=Path,default=HERE.parents[1]/'tables/supp_latency.tex')
    ap.add_argument('--results',type=Path,default=HERE.parents[1]/'results/realtime_c/latency-five-point-20261102.json')
    ap.add_argument('--output',type=Path,default=HERE)
    args=ap.parse_args()
    table=load(args.table)
    data=load_results(args.results, table)
    if not all(math.isnan(v) for method in ('PUMA', r'\ours') for v in table[method]):
        raise ValueError('PUMA/Ours results are now available; update the figure groups and pending note.')
    font_manager.fontManager.addfont(r'C:\Windows\Fonts\msyh.ttc')
    for lang in ('en','zh'):
        zh=lang=='zh'
        with plt.rc_context({'font.family':'Microsoft YaHei' if zh else 'Arial',
                             'font.size':7,'svg.fonttype':'none','pdf.fonttype':42,
                             'axes.linewidth':.6,'xtick.major.size':2.5,'ytick.major.size':2.5}):
            fig,axes=plt.subplots(1,2,figsize=(3.25,2.65),sharey=True)
            fig.subplots_adjust(left=.115,right=.98,bottom=.45,top=.895,wspace=.20)
            titles = (['(a) 基线部署', '(b) SE(3) 输入'] if zh else
                      ['(a) Deployments', '(b) SE(3) inputs'])
            for ax,group,title in zip(axes,GROUPS,titles):
                for method in group:
                    points=data[method]
                    values=[r['sr_percent'] for r in points]
                    lo,hi=zip(*(r['sr_scene_bootstrap95'] for r in points))
                    color,marker,line=SERIES[method]
                    ax.plot(XS,values,color=color,marker=marker,ms=2.5,ls=line,
                            lw=1.1,label=LABELS[METHODS[method]],zorder=3)
                    ax.fill_between(XS,lo,hi,color=color,alpha=.10,linewidth=0,zorder=2)
                ax.set(xlim=(-6,206),ylim=(0,60),xticks=XS,yticks=range(0,61,20))
                ax.set_title(title,fontsize=7.5,pad=5)
                ax.set_xlabel('附加延迟（ms）' if zh else 'Added latency (ms)',labelpad=3)
                ax.spines[['top','right']].set_visible(False)
                ax.grid(axis='y',color='#E6E6E6',lw=.5)
                ax.set_axisbelow(True)
                ax.legend(loc='upper center',bbox_to_anchor=(.5,-.36),frameon=False,
                          fontsize=7,handlelength=1.6,handletextpad=.45,
                          labelspacing=.4,borderaxespad=0)
            axes[0].set_ylabel('成功率（%）' if zh else 'SR (%)',labelpad=3)
            suffix='_zh' if zh else ''
            for ext in ('pdf','svg','png'):
                output=args.output/f'latency{suffix}.{ext}'
                fig.savefig(output,dpi=300,facecolor='white')
                if ext=='svg':
                    output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
            plt.close(fig)
    print('EN/ZH exported: two panels, nine configurations, 45 measured points and 95% scene-bootstrap intervals; PUMA/Ours pending.')

if __name__=='__main__':
    main()
