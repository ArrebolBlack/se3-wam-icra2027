import sys
sys.path.insert(0, 'figures/latency')
import plot_latency as P
import matplotlib.pyplot as plt
from pathlib import Path
def mix(h, t, w):
    a=[int(h[i:i+2],16) for i in (1,3,5)]; c=[round(x*(1-w)+t*w) for x in a]; return "#%02X%02X%02X"%tuple(c)
R,B,A,G,PU,GR="#C0263A","#2859A3","#E69F00","#2E8540","#9467BD","#6E6E6E"
VAR={
 'A_class_same': {},
 'B_class_shade': {'act':mix(G,0,.15),'dp':mix(G,255,.5),'dynamicvla':mix(A,255,.25),'puma':mix(A,0,.35),
                   'openwam_official':B,'openwam':B,'pi05':A,'pi05_se3':A,'dynamicwam':B,'dynamicwam_se3':B},
 'C_per_method': {'act':G,'dp':GR,'dynamicvla':PU,'puma':A,'openwam_official':B,'openwam':B,
                  'pi05':A,'pi05_se3':A,'dynamicwam':B,'dynamicwam_se3':B},
}
orig=P.line_style
table=P.load(Path('tables/supp_latency.tex')); data=P.load_results(Path('results/realtime_c/latency-five-point-20261104.json'),table)
for name,cmap in VAR.items():
    def ls(m, cmap=cmap):
        s=orig(m)
        if m in cmap:
            s['color']=cmap[m]; s['markeredgecolor']=cmap[m]
            if s['markerfacecolor']!='white': s['markerfacecolor']=cmap[m]
        return s
    P.line_style=ls
    with plt.rc_context({**P.STYLE,'font.family':['Liberation Sans'],'mathtext.rm':'Liberation Sans','mathtext.it':'Liberation Sans:italic','mathtext.bf':'Liberation Sans:bold'}):
        fig,_=P.draw_figure(data,'en'); fig.savefig(f'{name}.png',dpi=600,facecolor='white'); plt.close(fig)
    print(name)
