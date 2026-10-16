"""CVPR vector figures: conceptual interaction and actual D-reference computation.

Spatial drawings are original illustrations, never rollout evidence. The tiny
framework input image is a legacy scene illustration, not a current evaluation.
Text is >=8 pt at 6.875 inches. SVGs retain editable text, geometry and sources.
"""
from pathlib import Path
import base64
import math
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT=Path(__file__).resolve().parent
W=660
COL=dict(blue='#0072B2',orange='#E69F00',purple='#7B61A8',gray='#4D4D4D',ink='#26343D',light='#F2F2F2',line='#CBD1D5',teal='#26887D')

def start(h):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{h/96:.6f}in" viewBox="0 0 660 {h}">
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker></defs>
<rect width="660" height="{h}" fill="white"/><g font-family="Arial, Helvetica, sans-serif" font-size="11" fill="{COL['ink']}">''']

def text(s,x,y,body,size=11,weight='normal',color=None,anchor='start'):
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color or COL["ink"]}" text-anchor="{anchor}">{escape(body)}</text>')

def rect(s,x,y,w,h,fill='white',stroke=None,rx=3,sw=.8):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke or COL["line"]}" stroke-width="{sw}"/>')

def line(s,x1,y1,x2,y2,color=None,width=1,dash=None,arrow=False,both=False):
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or COL["gray"]}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+(' marker-start="url(#arrow)"' if both else '')+'/>')

def path(s,d,color=None,width=1,fill='none',dash=None,arrow=False):
    s.append(f'<path d="{d}" fill="{fill}" stroke="{color or COL["gray"]}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+'/>')

def polygon(s,points,fill,stroke='#73818B',sw=.7):
    s.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def circle(s,x,y,r,fill,stroke='none',sw=.8):
    s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

def t_object(s,x,y,angle=0,scale=1,color=None,ghost=False):
    color=color or COL['orange']
    p=[(-17,-10),(17,-10),(17,0),(6,0),(6,17),(-6,17),(-6,0),(-17,0)]
    a=math.radians(angle)
    q=[(x+scale*(u*math.cos(a)-v*math.sin(a)),y+scale*.62*(u*math.sin(a)+v*math.cos(a))) for u,v in p]
    if ghost:
        polygon(s,q,'white',color,1)
        s[-1]=s[-1].replace('/>',' stroke-dasharray="2 2" opacity=".7"/>')
        return
    lower=[(u,v+scale*5) for u,v in q]
    for i,j in [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7)]: polygon(s,[q[i],q[j],lower[j],lower[i]],'#BE7D18',color,.5)
    polygon(s,q,'#F1B643',color,.9)
    circle(s,x-7*scale,y-2*scale,1.8*scale,'#6F4B12')

def gripper(s,x,y,angle=0,scale=1):
    s.append(f'<g transform="translate({x},{y}) rotate({angle}) scale({scale})">')
    rect(s,-11,-7,21,14,fill='#D6DDE1',stroke='#5C6871',rx=1)
    rect(s,8,-12,7,8,fill='#F2F4F6',stroke=COL['purple'],rx=1)
    rect(s,8,4,7,8,fill='#F2F4F6',stroke=COL['purple'],rx=1)
    line(s,13,-8,21,-8,COL['purple'],2.4); line(s,13,8,21,8,COL['purple'],2.4)
    line(s,-5,-6,-5,6,'#A4ADB4',1); s.append('</g>')

def robot(s,x,y,reach=0,contact=False):
    pts=[(x,y),(x+1,y-22),(x+26,y-43),(x+48+reach,y-35)]
    polygon(s,[(x-11,y+7),(x+10,y+7),(x+15,y),(x-6,y)],'#A6AFB6')
    for (a,b),(c,d) in zip(pts,pts[1:]):
        line(s,a,b,c,d,'#687680',10); line(s,a-1,b-1,c-1,d-1,'#D2D9DE',7)
    for a,b in pts[:-1]:
        circle(s,a,b,5.7,'#EEF1F3','#60717B',1); circle(s,a,b,2,'#7F8C95')
    gripper(s,pts[-1][0]+9,pts[-1][1],-12 if contact else 12,.75)

def table(s,x,y):
    polygon(s,[(x,y+48),(x+125,y+8),(x+196,y+52),(x+63,y+94)],'#F0F3F5','#BAC4CB',.8)
    polygon(s,[(x+63,y+94),(x+196,y+52),(x+196,y+57),(x+63,y+100)],'#D9E0E5','#BAC4CB',.6)
    for f in (.25,.5,.75): line(s,x+125*f,y+48-40*f,x+63+133*f,y+94-42*f,'#DEE4E8',.6)
    line(s,x+31,y+70,x+161,y+29,'#DEE4E8',.6)

def context_block(s,x,y,shift=0,ghost=False):
    pts=[(x+shift,y),(x+shift+26,y-8),(x+shift+38,y+1),(x+shift+11,y+10)]
    if ghost:
        polygon(s,pts,'none','#A8AFB5',.8); s[-1]=s[-1].replace('/>',' stroke-dasharray="2 2"/>'); return
    polygon(s,[(u,v-11) for u,v in pts],'#D4DBE0','#7B8993')
    polygon(s,[pts[1],pts[2],(pts[2][0],pts[2][1]-11),(pts[1][0],pts[1][1]-11)],'#9AA7B1','#7B8993')
    polygon(s,[pts[2],pts[3],(pts[3][0],pts[3][1]-11),(pts[2][0],pts[2][1]-11)],'#B6C1C9','#7B8993')

def triad(s,x,y,scale=1,label=None):
    line(s,x,y,x+12*scale,y+3*scale,'#C5544E',.9,arrow=True)
    line(s,x,y,x-8*scale,y+6*scale,'#3F9471',.9,arrow=True)
    line(s,x,y,x,y-13*scale,'#4D80B5',.9,arrow=True)
    if label: text(s,x+13*scale,y-5*scale,label,11,weight='bold')

def interaction():
    s=start(224)
    text(s,4,13,'What must be remembered and predicted for interaction?',12,weight='bold')
    text(s,656,27,'Conceptual illustration; all positions and trajectories are hypothetical',11,color=COL['gray'],anchor='end')
    for xx in (219,439): line(s,xx,35,xx,216,'#D3DAE0',.8)
    for i,title in enumerate(['(a) Remember motion','(b) Predict the relevant future','(c) Resolve contact geometry']):
        text(s,i*220+5,44,title,11.333,weight='bold'); table(s,i*220+6,49)
    robot(s,24,119); context_block(s,158,118)
    t_object(s,88,104,-25,.7,COL['blue'],True); t_object(s,108,100,-5,.8,COL['blue'],True); t_object(s,128,95,20,.9)
    path(s,'M79 112 C94 112 113 104 121 101',COL['blue'],1.4,arrow=True)
    text(s,10,159,'history: t − 2Δ, t − Δ, t',11,color=COL['blue'])
    line(s,169,70,140,87,COL['gray'],.7); text(s,143,66,'same target',11)
    text(s,6,174,'One current pose can hide',11); text(s,6,188,'direction, speed or occlusion.',11)
    line(s,11,206,63,206,COL['blue'],1.2,arrow=True); text(s,73,210,'pose + Δt + visibility',11)
    robot(s,244,119,reach=10); context_block(s,378,118,-10,True); context_block(s,378,118)
    t_object(s,348,95,20,.9,COL['blue'],True); t_object(s,371,85,52,.9)
    path(s,'M346 102 Q365 105 376 93',COL['orange'],1.4,arrow=True); path(s,'M365 121L386 115',COL['orange'],1.2,arrow=True)
    text(s,228,159,'future offset δ: target and scene',11,color='#AD7100')
    t_object(s,240,181,30,.42); triad(s,252,188,.6)
    text(s,267,178,'target pose',11); text(s,267,192,'Δp, log ΔR',11)
    for j in range(3):
        for k in range(2):
            circle(s,348+j*13,176+k*12,1.2,'#7D8E99'); line(s,348+j*13,176+k*12,354+j*13,173+k*12,COL['orange'],.9,arrow=True)
    text(s,342,210,'scene flow / tracks',11)
    robot(s,459,119,reach=29,contact=True); t_object(s,569,87,52,1.15); context_block(s,596,118)
    triad(s,570,87,.75,'O'); triad(s,549,89,.65,'E'); circle(s,559,91,2.7,'white',COL['purple'],1.2)
    path(s,'M567 72Q575 67 584 72',COL['purple'],1.1,arrow=True)
    line(s,588,98,602,104,COL['gray'],.9,both=True,arrow=True)
    text(s,445,159,'contact t: relative pose and gap',11,color=COL['purple'])
    s[-1]=s[-1].replace('contact t:', 'contact t<tspan baseline-shift="sub" font-size="11">c</tspan>:')
    text(s,445,174,'Target role: align the contact.',11); text(s,445,188,'Context role: preserve clearance.',11)
    text(s,445,210,'O: target; E: end-effector frame',11)
    s.append('</g></svg>'); return '\n'.join(s)

def tokens(s,x,y,n,color):
    for j in range(n): rect(s,x+10*j,y,7,11,fill=color,stroke=color,rx=1,sw=.5)

def legacy_rgb(s,x,y,w,h):
    data=base64.b64encode((ROOT/'benchmark_frames/t1_so3.png').read_bytes()).decode('ascii')
    s.append(f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 88 224 224"><image width="448" height="630" href="data:image/png;base64,{data}"/></svg>')

def framework():
    s=start(224)
    text(s,4,13,'D reference: auxiliary supervision, action-only inference',12,weight='bold')
    text(s,4,31,'Inputs',11.333,weight='bold'); text(s,198,31,'Shared attention + split FFNs  × 4',11.333,weight='bold'); text(s,478,31,'Readouts and execution',11.333,weight='bold')
    legacy_rgb(s,5,40,56,56)
    rect(s,64,48,66,33,fill='#EDF6FC',stroke='#86B4CF'); text(s,97,62,'DINOv3',11,weight='bold',anchor='middle'); text(s,97,75,'frozen',11,anchor='middle')
    line(s,61,64,64,64,COL['blue'],1,arrow=True)
    text(s,6,109,'current RGB',11); text(s,6,122,'legacy scene image',11,color=COL['gray'])
    text(s,7,140,'8 EEF states + GT',11); text(s,7,154,'target pose / motion',11)
    labels=[('scene',COL['blue']),('meta',COL['teal']),('flow',COL['orange']),('action',COL['purple'])]
    for (label,color),y in zip(labels,[59,85,111,137]):
        text(s,150,y+8,label,11,weight='bold',color=color); tokens(s,188,y,2,color); line(s,206,y+5.5,219,y+5.5,color,1.1,arrow=True)
    path(s,'M130 64H146',COL['blue'],1.1,arrow=True); path(s,'M117 144H140V90H146',COL['teal'],1.1,arrow=True)
    text(s,6,175,'noised states + u',11)
    path(s,'M120 171H137V117H146',COL['orange'],.9,arrow=True); path(s,'M131 171H143V143H146',COL['purple'],.9,arrow=True)
    rect(s,219,43,110,116,fill='#F4F6F7',stroke='#7C8991',sw=.9)
    text(s,274,57,'shared QKV / O',11,weight='bold',anchor='middle'); text(s,274,72,'rows query; cols key',11,anchor='middle')
    mx,my,cell=252,84,15
    for k,l in enumerate('SMFA'):
        text(s,mx+cell*k+6,my-3,l,11,anchor='middle'); text(s,mx-9,my+cell*k+10,l,11,anchor='middle')
    mask=[[1,0,0,0],[1,1,0,0],[1,0,1,0],[0,1,0,1]]
    for row in range(4):
        for col in range(4): rect(s,mx+cell*col,my+cell*row,12,12,fill=labels[row][1] if mask[row][col] else 'white',stroke='#D0D7DC',rx=0,sw=.5)
    text(s,274,154,'access mask',11,anchor='middle')
    rect(s,350,47,78,49,fill='#EDF5F4',stroke='#8AB9B1'); text(s,389,67,'world/meta',11,weight='bold',anchor='middle'); text(s,389,82,'FFN',11,anchor='middle')
    rect(s,350,103,78,22,fill='#FFF6E4',stroke='#DCB76D'); text(s,389,118,'flow FFN',11,weight='bold',anchor='middle')
    rect(s,350,132,78,22,fill='#F1ECF7',stroke='#B39DCB'); text(s,389,147,'action FFN',11,weight='bold',anchor='middle')
    for y,color in [(64,COL['blue']),(90,COL['teal']),(114,COL['orange']),(143,COL['purple'])]: line(s,329,y,350,y,color,1,arrow=True)
    # Predicted readouts and GT labels meet only at explicit training loss nodes.
    rect(s,436,42,218,85,fill='#FFFCF5',stroke='#E2C78E',rx=3)
    text(s,545,54,'Auxiliary objectives (training)',11,weight='bold',color='#9A6808',anchor='middle')
    rect(s,442,60,92,27,fill='white',stroke='#A8BAB8')
    text(s,488,71,'pool 16 meta',11,anchor='middle')
    text(s,488,83,'deterministic pose',11,anchor='middle')
    path(s,'M428 90H434V74H442',COL['teal'],1.1,arrow=True)
    rect(s,545,64,36,19,fill='#EDF5F4',stroke='#8AB9B1',rx=2)
    text(s,563,77,'Lpose',11,anchor='middle')
    line(s,534,74,545,74,COL['teal'],1,arrow=True)
    text(s,621,67,'GT pose',11,anchor='middle')
    text(s,621,79,'+ masks',11,anchor='middle')
    text(s,621,91,'50–400 ms',11,anchor='middle')
    line(s,596,74,582,74,COL['gray'],.9,dash='3 2',arrow=True)
    rect(s,442,96,92,27,fill='white',stroke='#DCB76D')
    text(s,488,107,'scene-flow',11,anchor='middle')
    text(s,488,119,'FM field',11,anchor='middle')
    line(s,428,114,442,110,COL['orange'],1.1,arrow=True)
    rect(s,545,101,36,19,fill='#FFF6E4',stroke='#DCB76D',rx=2)
    text(s,563,114,'LFM',11,anchor='middle')
    line(s,534,110,545,110,COL['orange'],1,arrow=True)
    text(s,621,106,'GT flow',11,anchor='middle')
    text(s,621,118,'+ masks',11,anchor='middle')
    line(s,596,111,582,111,COL['gray'],.9,dash='3 2',arrow=True)
    # The FM field is integrated before it becomes an action chunk.
    rect(s,440,133,79,23,fill='#F1ECF7',stroke='#B39DCB')
    text(s,479.5,148,'action FM field',11,anchor='middle')
    line(s,428,143,440,143,COL['purple'],1.2,arrow=True)
    rect(s,528,133,57,23,fill='#F1ECF7',stroke='#B39DCB')
    text(s,556.5,148,'Euler ×5',11,weight='bold',anchor='middle')
    line(s,519,144,528,144,COL['purple'],1.2,arrow=True)
    line(s,585,144,592,144,COL['purple'],1.2,arrow=True)
    for j in range(8): rect(s,594+7.5*j,138,5,11,fill=COL['purple'],stroke=COL['purple'],rx=1,sw=.5)
    text(s,548,175,'8 × E7 → execute first → replan',11,color=COL['purple'],anchor='middle')
    text(s,219,175,'A reads M + A; no F → A edge.',11,weight='bold')
    line(s,4,185,656,185,'#C9D0D5',.8)
    text(s,5,199,'Q1  Replace history encoding',11,weight='bold',color=COL['blue']); text(s,5,215,'Reference: zero visual-history queries',11)
    text(s,241,199,'Q3  Backbone / access / program',11,weight='bold',color=COL['purple']); text(s,241,215,'Planned D/E + access / generation',11)
    text(s,475,199,'Q2  Replace future targets',11,weight='bold',color='#9A6808'); text(s,475,215,'Solid: data; dashed: supervision',11)
    s.append('</g></svg>'); return '\n'.join(s)

def render(svg):
    browser=Path(r'C:\Program Files\Google\Chrome\Application\chrome.exe')
    if not browser.exists(): raise RuntimeError('Chromium renderer unavailable')
    payload=base64.b64encode(svg.read_bytes()).decode('ascii'); _,_,width,height=ET.parse(svg).getroot().attrib['viewBox'].split()
    html=f'''<!doctype html><meta charset="utf-8"><style>@page{{size:{width}px {height}px;margin:0}}html,body{{width:{width}px;height:{height}px;margin:0;overflow:hidden}}img{{display:block;width:{width}px;height:{height}px}}</style><img src="data:image/svg+xml;base64,{payload}">'''
    review=ROOT.parent/'tmp'/'visual-review'; review.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='se3wam-figure-') as tmp:
        tmp=Path(tmp); p=tmp/'figure.html'; p.write_text(html,encoding='utf-8')
        common=[str(browser),'--headless=new','--disable-gpu',f'--user-data-dir={tmp/"profile"}','--no-pdf-header-footer']
        result=subprocess.run(common+[f'--print-to-pdf={svg.with_suffix(".pdf")}',p.as_uri()],capture_output=True,text=True)
        if result.returncode or not svg.with_suffix('.pdf').exists(): raise RuntimeError(result.stderr)
        preview=review/(svg.stem+'.png')
        result=subprocess.run(common+['--force-device-scale-factor=3',f'--window-size={width},{height}',f'--screenshot={preview}',p.as_uri()],capture_output=True,text=True)
        if result.returncode or not preview.exists(): raise RuntimeError(result.stderr)

if __name__=='__main__':
    for name,content in [('interaction_timing',interaction()),('study_framework',framework())]:
        p=ROOT/f'{name}.svg'; p.write_text(content,encoding='utf-8'); render(p); print(p.name)
