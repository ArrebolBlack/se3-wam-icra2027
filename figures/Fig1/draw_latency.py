"""Selected linear Fig.1c, reading Paused SR and native p95 from Table 1."""
from pathlib import Path
from html import escape
import json
import math
import re

ROOT = Path(__file__).resolve().parent


def table_rows():
    rows = []
    for line in (ROOT.parents[1]/'tables/main_results.tex').read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.rstrip().rstrip('\\').split('&')]
        if len(cells) != 9:
            continue
        name = re.sub(r'\s*\\cite\{[^}]*\}', '', cells[0])
        display = name.replace('$', '').replace(r'\pi_{0.5}', 'π0.5').replace(r'\alpha', 'α')
        display = display.replace('+SE(3)', ' + SE(3)')
        if name.startswith(r'\ours'):
            rows.append(dict(method=name, display='FoveaWAM', family='ours', pending=r'\resultplaceholder' in line))
            continue
        if not display.startswith(('ACT', 'DP', 'π0.5', 'DynamicVLA', 'PUMA', 'OpenWAM', 'DynamicWAM')):
            continue
        def value(c): return float(re.sub(r'\\(?:best|second)cell\{([^}]*)\}', r'\1', c))
        family = 'Reactive' if display in ('ACT', 'DP') else 'Video WAM' if display.startswith(('OpenWAM', 'DynamicWAM')) else 'VLA'
        rows.append(dict(method=name, display=display, family=family, sr=value(cells[5]), paused_sr=value(cells[7]), p95=value(cells[8])))
    assert len(rows) == 11
    return rows


def render_latency():
    rows = [dict(method=r['display'], family=r['family'], paused_sr=r['paused_sr'], p95_ms=r['p95'])
            for r in table_rows() if r['family'] != 'ours' and r['display'] != 'OpenWAM-α (off)']
    ours = json.loads((ROOT/'data/ours_paused.json').read_text(encoding='utf-8'))
    assert ours['status'] == 'placeholder', 'Replace the provisional configuration with verified Table 1 values before finalizing.'
    reference = next(r for r in rows if r['method']=='OpenWAM-α')
    ratio = reference['p95_ms']/ours['p95_ms']
    ax, ay, aw, ah = 2050, 190, 720, 615
    def X(ms): return ax+ms/200*aw
    def Y(sr): return ay+ah*(1-sr/100)
    C = dict(ink='#2D3638', gray='#677170', muted='#87908D', coral='#D85A30', grid='#E8EDE9', base='#8B9890', dark='#596960')
    S = []
    def attr(a): return ''.join(f' {k.replace("_", "-")}="{v}"' for k,v in a.items())
    def text(x,y,t,fs=28,c=None,b=False,anchor='start',**a): S.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{fs}" fill="{c or C["gray"]}" font-weight="{700 if b else 400}" text-anchor="{anchor}"{attr(a)}>{escape(t)}</text>')
    def path(d,c=None,sw=2,fill='none',**a): S.append(f'<path d="{d}" fill="{fill}" stroke="{c or C["gray"]}" stroke-width="{sw}"{attr(a)}/>')
    def line(x,y,u,v,**kw): path(f'M{x:.3f},{y:.3f} L{u:.3f},{v:.3f}',**kw)
    def circle(x,y,r,fill,stroke='none',sw=2): S.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def rect(x,y,w,h,fill,stroke='none',sw=2): S.append(f'<rect x="{x:.3f}" y="{y:.3f}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    def triangle(x,y,r,c): path(f'M{x:.3f},{y-r:.3f} L{x+r*.9:.3f},{y+r*.65:.3f} L{x-r*.9:.3f},{y+r*.65:.3f} Z',c,2.5,'#FFFFFF')
    def star(x,y,r,c):
        pts=[(x+(r if i%2==0 else r*.43)*math.cos(-math.pi/2+i*math.pi/5),y+(r if i%2==0 else r*.43)*math.sin(-math.pi/2+i*math.pi/5)) for i in range(10)]
        path('M'+' L'.join(f'{u:.3f},{v:.3f}' for u,v in pts)+' Z','#FFFFFF',2.2,c)

    S.append('<g id="C_Success_Latency">')
    text(1930,62,'(c) Success vs. latency',40,C['ink'],True)
    text(1930,119,'Physics paused during inference',32)
    for sr in [0,25,50,75,100]:
        yy=Y(sr);line(ax,yy,ax+aw,yy,c=C['grid'],sw=1.6);text(ax-18,yy+10,str(sr),28,anchor='end')
    line(ax,ay,ax,ay+ah,sw=2.3);line(ax,ay+ah,ax+aw,ay+ah,sw=2.3)
    for ms in [0,50,100,150,200]:
        xx=X(ms);line(xx,ay+ah,xx,ay+ah+9,sw=1.8);text(xx,ay+ah+44,str(ms),28,anchor='middle')
    line(X(50),ay,X(50),ay+ah,c='#C2CBC5',sw=1.8,stroke_dasharray='6 7')
    text(X(50)+62,ay+30,'50 ms',23,C['muted'])
    text(1966,525,'Success rate (%)',32,anchor='middle',transform='rotate(-90 1966 525)')
    text(ax+aw/2,885,'p95 time-to-action (ms)',30,anchor='middle')
    labels={'ACT':(2100,563,'start',28),'DP':(2300,645,'middle',28),'π0.5':(2235,409,'end',28),
        'π0.5 + SE(3)':(2240,358,'end',26),'PUMA':(2235,506,'end',27),'DynamicVLA':(2425,557,'end',26),
        'OpenWAM-α':(2650,475,'start',27),'DynamicWAM':(2650,550,'start',26),'DynamicWAM + SE(3)':(2620,365,'start',24)}
    leaders={'DP':[(2300,620)],'π0.5':[(2248,401)],'π0.5 + SE(3)':[(2252,350)],'PUMA':[(2248,498)],
        'DynamicVLA':[(2400,525),(2414,540)],'OpenWAM-α':[(2630,467),(2638,467)],
        'DynamicWAM':[(2625,542),(2638,542)],'DynamicWAM + SE(3)':[(2610,388),(2610,357)]}
    for r in rows:
        if r['method'] in leaders:
            pts=[(X(r['p95_ms']),Y(r['paused_sr']))]+leaders[r['method']]
            path('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in pts),'#AEBAB2',1.5)
    op=(X(reference['p95_ms']),Y(reference['paused_sr']));fp=(X(ours['p95_ms']),Y(ours['paused_sr']))
    dx,dy=fp[0]-op[0],fp[1]-op[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
    tail=(op[0]+ux*15,op[1]+uy*15);tip=(fp[0]-ux*21,fp[1]-uy*21)
    lx,ly=tip[0]-tail[0],tip[1]-tail[1];ll=math.hypot(lx,ly);gaps=[]
    for r in rows:
        if r['method']=='OpenWAM-α':continue
        px,py=X(r['p95_ms']),Y(r['paused_sr']);t=((px-tail[0])*lx+(py-tail[1])*ly)/(ll*ll)
        if not 0<t<1:continue
        distance=abs((px-tail[0])*ly-(py-tail[1])*lx)/ll
        if distance<17:
            dt=math.sqrt(17*17-distance*distance)/ll;gaps.append((max(0,t-dt),min(1,t+dt)))
    last=0
    for g0,g1 in sorted(gaps)+[(1,1)]:
        if g0>last:line(tail[0]+last*lx,tail[1]+last*ly,tail[0]+g0*lx,tail[1]+g0*ly,c=C['coral'],sw=2.8,stroke_dasharray='7 6')
        last=max(last,g1)
    base1=(tip[0]-ux*13-uy*6,tip[1]-uy*13+ux*6);base2=(tip[0]-ux*13+uy*6,tip[1]-uy*13-ux*6)
    path('M'+' L'.join(f'{x:.3f},{y:.3f}' for x,y in [tip,base1,base2])+' Z',C['coral'],0,C['coral'])
    theta=math.degrees(math.atan2(-dy,-dx));label_x=(op[0]+fp[0])/2-uy*37;label_y=(op[1]+fp[1])/2+ux*37
    text(label_x,label_y,f'≈{ratio:.1f}× faster',35,C['coral'],True,'middle',transform=f'rotate({theta:.6f} {label_x:.6f} {label_y:.6f})')
    positions=[]
    for r in rows:
        xx,yy=X(r['p95_ms']),Y(r['paused_sr']);positions.append(dict(**r,x=xx,y=yy))
        col=C['dark'] if r['method']=='OpenWAM-α' else C['base']
        if r['family']=='Reactive':circle(xx,yy,9,col)
        elif r['family']=='VLA':triangle(xx,yy,10,col)
        elif r['method']=='OpenWAM-α':rect(xx-10,yy-10,20,20,'#FFFFFF',col,3.3)
        else:rect(xx-8,yy-8,16,16,col)
        tx,ty,anchor,fs=labels[r['method']];text(tx,ty,r['method'],fs,C['dark'] if r['method']=='OpenWAM-α' else C['gray'],r['method']=='OpenWAM-α',anchor)
    star(*fp,16,C['coral']);rect(fp[0]-90,fp[1]-96,220,78,'#FFFFFF')
    text(fp[0]+20,fp[1]-65,'FoveaWAM',34,C['coral'],True,'middle')
    text(fp[0]+20,fp[1]-28,f'{ours["paused_sr"]:g}% · {ours["p95_ms"]:g} ms*',28,C['coral'],False,'middle')
    circle(2070,928,8,C['base']);text(2090,938,'Reactive',25)
    triangle(2285,928,9,C['base']);text(2305,938,'VLA',25)
    rect(2407,920,16,16,C['base']);text(2442,938,'Video WAM',25)
    text(2050,975,'* Ours: provisional layout values.',24,C['muted'])
    S.append('</g>')
    metadata=dict(sr_column='Paused',axis=dict(scale='linear',minimum=0,maximum=200),plotted=positions,
        omitted=['OpenWAM-α (off)'],ours=ours,speedup=dict(reference='OpenWAM-α',p95_ms=reference['p95_ms'],ratio=ratio),
        timing_note='Native deployment settings from Table 1; PUMA uses the official three-camera budget, other baselines use two-camera timing inputs.')
    return '\n'.join(S),metadata
