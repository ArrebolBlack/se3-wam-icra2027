import sys
sys.path.insert(0, 'figures/latency')
import plot_latency as P
import matplotlib.pyplot as plt
from pathlib import Path
T={k:plt.get_cmap('tab10')(i) for i,k in enumerate(['blue','orange','green','red','purple','brown','pink','gray','olive','cyan'])}
hx=lambda c:"#%02X%02X%02X"%tuple(round(x*255) for x in c[:3])
T={k:hx(v) for k,v in T.items()}; print(T)
cm={'act':T['green'],'dp':T['gray'],'dynamicvla':T['purple'],'puma':T['orange'],'openwam_official':T['blue'],'openwam':T['blue'],
    'pi05':T['orange'],'pi05_se3':T['orange'],'dynamicwam':T['blue'],'dynamicwam_se3':T['blue'],'ours':T['red']}
orig=P.line_style
def ls(m):
    s=orig(m); c=cm[m]; s['color']=c; s['markeredgecolor']=c
    if s['markerfacecolor']!='white': s['markerfacecolor']=c
    return s
P.line_style=ls; P.METHOD_COLORS['FoveaWAM']=T['red']
table=P.load(Path('tables/supp_latency.tex')); data=P.load_results(Path('results/realtime_c/latency-five-point-20261104.json'),table)
with plt.rc_context({**P.STYLE,'font.family':['Liberation Sans'],'mathtext.rm':'Liberation Sans','mathtext.it':'Liberation Sans:italic','mathtext.bf':'Liberation Sans:bold'}):
    fig,_=P.draw_figure(data,'en'); fig.savefig('D_tab10.png',dpi=600,facecolor='white'); plt.close(fig)
