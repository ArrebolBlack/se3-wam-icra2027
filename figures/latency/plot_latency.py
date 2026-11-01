"""Render EN/ZH latency plots directly from tables/supp_latency.tex.

Run from the repository root: python figures/latency/plot_latency.py
Unmeasured grid points stay NaN; no lines bridge missing observations.
"""
import argparse
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
    r'\ours': 'SE(3)-WAM',
}
# Preserve the original six planned series, plus the now-measured DP baseline.
# Other baselines remain in the complete shared table.
SERIES = {
    'ACT': ('#7F7F7F','o'),
    'Diffusion Policy': ('#C95318','P'),
    r'$\pi_{0.5}$ + SE(3)': ('#E69F00','s'),
    'DynamicVLA': ('#009E73','^'),
    r'OpenWAM-$\alpha$': ('#CC79A7','D'),
    'DynamicWAM + SE(3)': ('#8C564B','v'),
    r'\ours': ('#1674AB','o'),
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--table',type=Path,default=HERE.parents[1]/'tables/supp_latency.tex')
    ap.add_argument('--output',type=Path,default=HERE)
    args=ap.parse_args()
    data=load(args.table)
    font_manager.fontManager.addfont(r'C:\Windows\Fonts\msyh.ttc')
    for lang in ('en','zh'):
        zh=lang=='zh'
        with plt.rc_context({'font.family':'Microsoft YaHei' if zh else 'Arial',
                             'font.size':7.5,'svg.fonttype':'none','pdf.fonttype':42,
                             'axes.linewidth':.6,'xtick.major.size':2.5,'ytick.major.size':2.5}):
            fig=plt.figure(figsize=(3.25,2.45))
            ax=fig.add_axes([.145,.48,.82,.45])
            ax.axvline(150,color='#B5B5B5',lw=.7,ls='--',zorder=1)
            handles,pending_flags=[],[]
            for method,(color,marker) in SERIES.items():
                values=data[method]
                pending=all(math.isnan(v) for v in values)
                pending_flags.append(pending)
                handles.append(Line2D([],[],color=color,marker=marker,ms=3.5,
                                      linestyle='none',markerfacecolor='none' if pending else color,
                                      label=LABELS[method]+(' †' if pending else '')))
                if not pending:
                    ax.plot(XS,values,color=color,marker=marker,ms=3.5,
                            lw=1.8 if method==r'\ours' else 1,
                            clip_on=False,zorder=3)
            ax.set(xlim=(0,200),ylim=(0,100),xticks=XS,yticks=[0,50,100])
            ax.set_xlabel('附加延迟（ms）' if zh else 'Added latency (ms)',labelpad=1.5)
            ax.set_ylabel('SR (%)',labelpad=1.5)
            ax.spines[['top','right']].set_visible(False)
            ax.grid(axis='y',color='#E6E6E6',lw=.5)
            legend=fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.52,.315),
                              ncol=2,frameon=False,borderaxespad=0,handlelength=1,
                              handletextpad=.4,columnspacing=1.5,labelspacing=.4,fontsize=7)
            for label,pending in zip(legend.get_texts(),pending_flags):
                label.set_color('#666666' if pending else '#222222')
            fig.text(.52,.015,'† 结果待出' if zh else '† Results pending',
                     fontsize=7,color='#666666',ha='center')
            suffix='_zh' if zh else ''
            for ext in ('pdf','svg','png'):
                output=args.output/f'latency{suffix}.{ext}'
                fig.savefig(output,dpi=300,facecolor='white')
                if ext=='svg':
                    output.write_text('\n'.join(line.rstrip() for line in output.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
            plt.close(fig)
    print(f'{len(SERIES)} method identities retained, including {sum(pending_flags)} pending methods; no pending values plotted. EN/ZH exported.')

if __name__=='__main__':
    main()
