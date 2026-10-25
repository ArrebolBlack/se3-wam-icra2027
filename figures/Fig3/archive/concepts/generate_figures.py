"""CVPR vector figures: conceptual interaction and actual D-reference computation.

Spatial drawings are original illustrations, never rollout evidence. The
framework input is an authentic current benchmark scene (P15 dev84, state 010),
used only to illustrate the observation input, not a P03 prediction.
Text is >=8 pt at 6.875 inches. SVGs retain editable text, geometry and sources.
"""
from pathlib import Path
import argparse
import base64
import math
import sys
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "scripts"))
from common import REVIEW, svg_to_pdf

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
    text(s,4,13,'Acting in physical time',12,weight='bold')
    text(s,656,27,'Conceptual illustration; all positions and trajectories are hypothetical',11,color=COL['gray'],anchor='end')
    for xx in (219,439): line(s,xx,35,xx,216,'#D3DAE0',.8)
    for i,title in enumerate(['(a) Same pose, different motion','(b) Different poses at execution','(c) Resolve contact geometry']):
        text(s,i*220+5,44,title,11.333,weight='bold')
        if i < 2: table(s,i*220+6,49)
    robot(s,24,119); context_block(s,158,118)
    # Hypothetical A/B histories converge to one identical current pose. The
    # branch identity uses line style, preserving blue/history and orange/future.
    t_object(s,96,66,-30,.56,COL['blue'],True)
    t_object(s,111,78,-5,.66,COL['blue'],True)
    t_object(s,80,127,65,.56,COL['blue'],True)
    t_object(s,103,111,45,.66,COL['blue'],True)
    path(s,'M91 73 Q109 84 119 89',COL['blue'],1.5,arrow=True)
    path(s,'M79 135 Q103 118 119 103',COL['blue'],1.5,dash='4 2.6',arrow=True)
    t_object(s,128,95,20,.85)
    text(s,82,62,'A',11,weight='bold',color=COL['blue'])
    text(s,62,138,'B',11,weight='bold',color=COL['blue'])
    line(s,181,75,141,89,COL['gray'],.7); text(s,177,68,'at τ',11); s[-1]=s[-1].replace('τ</text>','τ<tspan baseline-shift="sub" font-size="8">t</tspan></text>')
    text(s,6,159,'Two histories → one current pose',11,color=COL['blue'])
    text(s,6,175,'Past poses at −100, −50, 0 ms',11)
    line(s,8,190,31,190,COL['blue'],1.5); text(s,37,194,'A',11,weight='bold',color=COL['blue'])
    line(s,64,190,87,190,COL['blue'],1.5,dash='4 2.6'); text(s,93,194,'B',11,weight='bold',color=COL['blue'])
    text(s,6,211,'Current pose alone is ambiguous.',11)
    robot(s,244,119,reach=10); context_block(s,280,128,-9,True); context_block(s,280,128)
    t_object(s,348,95,20,.85,COL['blue'],True)
    path(s,'M359 102 Q367 110 372 107',COL['orange'],1.6,arrow=True)
    path(s,'M358 89 Q363 82 365 81',COL['orange'],1.6,dash='4 2.6',arrow=True)
    t_object(s,382,103,52,.85); t_object(s,377,77,-20,.85)
    text(s,403,115,'A',11,weight='bold',color='#AD7100')
    text(s,399,74,'B',11,weight='bold',color='#AD7100')
    text(s,337,117,'τ',11,color=COL['blue']); s[-1]=s[-1].replace('τ</text>','τ<tspan baseline-shift="sub" font-size="8">t</tspan></text>')
    text(s,226,159,'At the same execution time τ',11,color='#AD7100'); s[-1]=s[-1].replace('τ</text>','τ<tspan baseline-shift="super" font-size="8">a</tspan></text>')
    text(s,226,175,'A / B → different position + rotation',11)
    text(s,226,192,'Predict its SE(3) pose at that time.',11)
    text(s,226,211,'Carry the motion history forward.',11)
    # Preserve the original hypothetical geometry in a reduced scene and a
    # separate, uniformly magnified contact view. Only framing/labels change.
    rect(s,364,91,38,28,fill='none',stroke='#A7B2BA',rx=2,sw=.65)
    path(s,'M402 105H429L450 82H486','#A7B2BA',.75,dash='3 2')
    s.append('<g transform="translate(446,78) scale(.44) translate(-446,-57)">')
    table(s,446,49)
    robot(s,459,119,reach=29,contact=True); t_object(s,569,87,52,1.15); context_block(s,596,118)
    rect(s,538,67,73,49,fill='none',stroke='#7F8E98',rx=2,sw=1.4)
    s.append('</g>')
    path(s,'M519 93H537','#7F8E98',.85,dash='3 2')
    text(s,653,61,'Contact detail (A)',11,color='#AD7100',anchor='end')
    rect(s,537,67,117,79,fill='#FAFBFC',stroke='#A7B2BA',rx=2,sw=.8)
    s.append('<defs><clipPath id="contact-detail"><rect x="537" y="67" width="117" height="79" rx="2"/></clipPath></defs>')
    s.append('<g clip-path="url(#contact-detail)"><g transform="translate(540,66) scale(1.3) translate(-533,-65)">')
    robot(s,459,119,reach=29,contact=True); t_object(s,569,87,52,1.15); context_block(s,596,118)
    triad(s,570,87,.75); triad(s,549,89,.65); circle(s,559,91,2.7,'white',COL['purple'],1.2)
    path(s,'M567 72Q575 67 584 72',COL['purple'],1.1,arrow=True)
    line(s,588,98,602,104,COL['gray'],.9,both=True,arrow=True)
    s.append('</g></g>')
    text(s,548,79,'E',11,weight='bold'); line(s,554,81,559,91,'#6E7B85',.65)
    text(s,608,83,'O',11,weight='bold'); line(s,605,85,591,93,'#6E7B85',.65)
    text(s,646,104,'gap ≥ m',11,anchor='end'); line(s,637,106,627,115,'#6E7B85',.65)
    text(s,543,141,'contact',11,color=COL['purple']); line(s,570,132,574,104,COL['purple'],.75)
    text(s,445,159,'At τ: pose error ≤ ε and gap ≥ m',11,color=COL['purple'])
    s[-1]=s[-1].replace('At τ:', 'At τ<tspan baseline-shift="super" font-size="8">a</tspan>:')
    text(s,445,174,'Target: tolerance ε, exact SE(3).',11); text(s,445,188,'Context: margin m ≫ ε, 3D flow.',11)
    text(s,445,210,'O: target; E: end-effector frame',11)
    s.append('</g></svg>'); return '\n'.join(s)

def tokens(s,x,y,n,color):
    for j in range(n): rect(s,x+10*j,y,7,11,fill=color,stroke=color,rx=1,sw=.5)

def current_rgb(s,x,y,w,h):
    data=base64.b64encode((ROOT.parents[2]/'Fig4/archive/benchmark/benchmark_frames/dev84_p15_state010.png').read_bytes()).decode('ascii')
    s.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{data}"/>')

def framework():
    s=start(300)
    text(s,4,13,'D reference: auxiliary supervision, action-only inference',12,weight='bold')
    # Each visual patch is projected and enriched before view fusion. The
    # coordinate projection and visual Q/K RoPE are separate uses of geometry.
    current_rgb(s,5,30,56,56)
    rect(s,66,38,76,33,fill='#EDF6FC',stroke='#86B4CF')
    text(s,104,52,'DINOv3',11,weight='bold',anchor='middle')
    text(s,104,65,'frozen',11,anchor='middle')
    line(s,61,54,66,54,COL['blue'],1.1,arrow=True)
    rect(s,153,26,198,68,fill='#EDF6FC',stroke='#86B4CF')
    text(s,163,40,'DINO → 768 + view embedding',11,weight='bold')
    text(s,163,57,'+ Linear(depth: 1 → 768)',11)
    text(s,163,74,'+ Linear(XYZ: 3 → 768)',11)
    text(s,163,88,'sum per visual patch',11,color=COL['gray'])
    line(s,142,54,153,54,COL['blue'],1.1,arrow=True)
    rect(s,364,39,70,39,fill='#EDF6FC',stroke='#86B4CF')
    text(s,399,54,'single view',11,weight='bold',anchor='middle')
    text(s,399,70,'196 visual',11,anchor='middle')
    line(s,351,59,364,59,COL['blue'],1.1,arrow=True)
    rect(s,448,26,207,68,fill='#EDF6FC',stroke='#86B4CF')
    text(s,458,40,'S: scene bank',11,weight='bold',color=COL['blue'])
    text(s,458,58,'196 current visual tokens',11)
    text(s,458,74,'+ 8 EEF-history tokens',11)
    text(s,458,89,'+ 8 GT kinematic tokens',11)
    line(s,434,59,448,59,COL['blue'],1.1,arrow=True)
    text(s,5,105,'agentview RGB, 224²',11)
    text(s,5,121,'P15 dev84 / state 010',11,color=COL['gray'])
    text(s,153,106,'depth: mean metric patch depth (m)',11)
    text(s,153,122,'XYZ: fixed patch centers + depth + K + camera pose → robot base',11)
    # The entire scene bank enters S. Learned meta tokens have independent
    # initialization, and obtain observation information only inside the trunk.
    path(s,'M551 94V131H139V176H146',COL['blue'],1.1,arrow=True)
    text(s,4,143,'Token banks',11.333,weight='bold')
    text(s,219,143,'Shared attention + split FFNs × 4',11.333,weight='bold')
    text(s,478,143,'Readouts and execution',11.333,weight='bold')
    rect(s,5,190,127,23,fill='#EDF5F4',stroke='#8AB9B1')
    text(s,68.5,205,'16 learned meta',11,weight='bold',anchor='middle')
    line(s,132,201.5,146,201.5,COL['teal'],1.1,arrow=True)
    rect(s,5,216,127,23,fill='#FFF6E4',stroke='#DCB76D')
    text(s,68.5,231,'noised F + u (train)',11,anchor='middle')
    line(s,132,227.5,146,227.5,COL['orange'],1.1,arrow=True)
    rect(s,5,242,127,23,fill='#F1ECF7',stroke='#B39DCB')
    text(s,68.5,257,'noised actions + u',11,anchor='middle')
    line(s,132,253.5,146,253.5,COL['purple'],1.1,arrow=True)
    labels=[('scene',COL['blue']),('meta',COL['teal']),('flow',COL['orange']),('action',COL['purple'])]
    for (label,color),y in zip(labels,[170,196,222,248]):
        text(s,150,y+8,label,11,weight='bold',color=color); tokens(s,188,y,2,color); line(s,206,y+5.5,219,y+5.5,color,1.1,arrow=True)
    rect(s,219,154,110,116,fill='#F4F6F7',stroke='#7C8991',sw=.9)
    text(s,274,168,'shared QKV / O',11,weight='bold',anchor='middle'); text(s,274,183,'rows query; cols key',11,anchor='middle')
    mx,my,cell=252,195,15
    for k,l in enumerate('SMFA'):
        text(s,mx+cell*k+6,my-3,l,11,anchor='middle'); text(s,mx-9,my+cell*k+10,l,11,anchor='middle')
    mask=[[1,0,0,0],[1,1,0,0],[1,0,1,0],[0,1,0,1]]
    for row in range(4):
        for col in range(4): rect(s,mx+cell*col,my+cell*row,12,12,fill=labels[row][1] if mask[row][col] else 'white',stroke='#D0D7DC',rx=0,sw=.5)
    text(s,274,265,'access mask',11,anchor='middle')
    rect(s,350,158,78,49,fill='#EDF5F4',stroke='#8AB9B1'); text(s,389,178,'world/meta',11,weight='bold',anchor='middle'); text(s,389,193,'FFN',11,anchor='middle')
    rect(s,350,214,78,22,fill='#FFF6E4',stroke='#DCB76D'); text(s,389,229,'flow FFN',11,weight='bold',anchor='middle')
    rect(s,350,243,78,22,fill='#F1ECF7',stroke='#B39DCB'); text(s,389,258,'action FFN',11,weight='bold',anchor='middle')
    for y,color in [(175,COL['blue']),(201,COL['teal']),(225,COL['orange']),(254,COL['purple'])]: line(s,329,y,350,y,color,1,arrow=True)
    # Predicted readouts and GT labels meet only at explicit training loss nodes.
    rect(s,436,153,218,85,fill='#FFFCF5',stroke='#E2C78E',rx=3)
    text(s,545,165,'Auxiliary objectives (training)',11,weight='bold',color='#9A6808',anchor='middle')
    rect(s,442,171,92,27,fill='white',stroke='#A8BAB8')
    text(s,488,182,'pool 16 meta',11,anchor='middle')
    text(s,488,194,'deterministic pose',11,anchor='middle')
    path(s,'M428 201H434V185H442',COL['teal'],1.1,arrow=True)
    rect(s,545,175,36,19,fill='#EDF5F4',stroke='#8AB9B1',rx=2)
    text(s,563,188,'Lpose',11,anchor='middle')
    line(s,534,185,545,185,COL['teal'],1,arrow=True)
    text(s,621,178,'GT pose',11,anchor='middle')
    text(s,621,190,'+ masks',11,anchor='middle')
    text(s,621,202,'50–400 ms',11,anchor='middle')
    line(s,596,185,582,185,COL['gray'],.9,dash='3 2',arrow=True)
    rect(s,442,207,92,27,fill='white',stroke='#DCB76D')
    text(s,488,218,'scene-flow',11,anchor='middle')
    text(s,488,230,'FM field',11,anchor='middle')
    line(s,428,225,442,221,COL['orange'],1.1,arrow=True)
    rect(s,545,212,36,19,fill='#FFF6E4',stroke='#DCB76D',rx=2)
    text(s,563,225,'LFM',11,anchor='middle')
    line(s,534,221,545,221,COL['orange'],1,arrow=True)
    text(s,621,217,'GT flow',11,anchor='middle')
    text(s,621,229,'+ masks',11,anchor='middle')
    line(s,596,222,582,222,COL['gray'],.9,dash='3 2',arrow=True)
    # The FM field is integrated before it becomes an action chunk.
    rect(s,440,244,79,23,fill='#F1ECF7',stroke='#B39DCB')
    text(s,479.5,259,'action FM field',11,anchor='middle')
    line(s,428,254,440,254,COL['purple'],1.2,arrow=True)
    rect(s,528,244,57,23,fill='#F1ECF7',stroke='#B39DCB')
    text(s,556.5,259,'Euler ×5',11,weight='bold',anchor='middle')
    line(s,519,255,528,255,COL['purple'],1.2,arrow=True)
    line(s,585,255,592,255,COL['purple'],1.2,arrow=True)
    for j in range(8): rect(s,594+7.5*j,249,5,11,fill=COL['purple'],stroke=COL['purple'],rx=1,sw=.5)
    text(s,5,281,'3DRoPE: current visual Q/K',11,color=COL['gray'])
    text(s,5,295,'+ matching flow-query XYZ only',11,color=COL['gray'])
    text(s,219,282,'Online: S + M + A; omit F',11,weight='bold')
    text(s,548,282,'predict 8 → execute 1 → replan',11,color=COL['purple'],anchor='middle')
    text(s,219,296,'A reads M + A; no F → A edge',11)
    text(s,548,296,'Solid: data; dashed: supervision',11,color=COL['gray'],anchor='middle')
    s.append('</g></svg>'); return '\n'.join(s)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--figure',choices=['interaction_timing','study_framework'])
    args=parser.parse_args()
    for name,generate in [('interaction_timing',interaction),('study_framework',framework)]:
        if args.figure and args.figure!=name: continue
        p=ROOT/f'{name}.svg'; p.write_text(generate(),encoding='utf-8'); svg_to_pdf(p,preview_dir=REVIEW); print(p.name)
