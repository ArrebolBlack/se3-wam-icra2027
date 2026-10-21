"""Draw the SE(3)-WAM model family; conceptual geometry, no result data.

The observed image is an existing, unmodified Dynamic14 observation.
Physical size: 6.875 in wide. Text: >= 8.1 pt at final width.
"""
from pathlib import Path
from html import escape
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from common import REVIEW, svg_to_pdf

OUT = ROOT / 'figures'
W, H = 1200, 570
C = {'ink':'#26343D', 'muted':'#56616A', 'line':'#A7AFB5',
     'obs':'#0876AD', 'obs_fill':'#EAF4FA', 'future':'#BD7C0B',
     'future_fill':'#FFF4DF', 'action':'#7753A4', 'action_fill':'#F1EBF7',
     'gray':'#F4F5F5', 'world':'#218579', 'world_fill':'#EAF5F1'}
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{6.875*H/W:.6f}in" viewBox="0 0 {W} {H}">',
     '<defs>']
for name in ('ink','obs','future','action','muted'):
    s.append(f'<marker id="arr_{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="{C[name]}"/></marker>')
s += ['</defs>', '<rect width="1200" height="570" fill="white"/>', '<g font-family="Arial,Helvetica,sans-serif" fill="#26343D" font-size="20">']

def txt(x,y,t,size=20,color='ink',weight='normal',anchor='start'):
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{C.get(color,color)}">{escape(t)}</text>')
def box(x,y,w,h,fill='gray',stroke='line',r=6,sw=1.5):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{C.get(fill,fill)}" stroke="{C.get(stroke,stroke)}" stroke-width="{sw}"/>')
def path(d,color='ink',sw=2,arrow=False,dash=False,start=False):
    end=f' marker-end="url(#arr_{color})"' if arrow else ''
    beg=f' marker-start="url(#arr_{color})"' if start else ''
    ds=' stroke-dasharray="6 4"' if dash else ''
    s.append(f'<path d="{d}" fill="none" stroke="{C[color]}" stroke-width="{sw}"{end}{beg}{ds}/>')
def token(x,y,w=20,h=24,color='obs'):
    box(x,y,w,h,color+'_fill',color,r=3,sw=1.5)
def dot(x,y,r=3,color='future'):
    s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{C[color]}"/>')

txt(8,24,'a',24,weight='bold'); txt(35,24,'From observation history to timed actions',23,weight='bold')

# Observations: one real frame and a symbolic, timestamped sequence.
s.append('<image x="10" y="54" width="112" height="112" href="benchmark_frames/dev84_p15_state010.png"/>')
txt(136,72,'RGB-D',20,'obs',weight='bold')
for yy in (89,112,135):
    for xx in (137,161,185): token(xx,yy,18,16,'obs')
txt(10,192,'t − 7Δ',20,'muted'); txt(162,192,'t',20,'muted')
path('M12 207H196','obs',1.6,True)
for x in (20,44,68,92,116,140,164,188): path(f'M{x} 202V212','obs',1.5)
txt(10,239,'Robot state + task',20)
txt(10,264,'Estimated motion',20)
txt(10,289,'Target prompt +',20,'muted')
txt(10,314,'object prior',20,'muted')
path('M205 55H215V319H205','obs',1.3)
path('M215 146H232','obs',2,True)

# Causal input encoder and the common context token bank.
box(240,75,137,138,'obs_fill','obs')
txt(308,109,'H',29,'obs',weight='bold',anchor='middle')
txt(308,142,'History',21,anchor='middle'); txt(308,168,'encoder',21,anchor='middle')
txt(308,197,'+ time',20,'obs',anchor='middle')
path('M377 144H401','obs',2,True)
txt(424,68,'Xₜ',25,'obs',weight='bold',anchor='middle')
for yy in (92,126,160,194):
    for xx in (407,430): token(xx,yy,17,25,'obs')
txt(425,249,'Causal',20,'obs',anchor='middle'); txt(425,273,'tokens',20,'obs',anchor='middle')

# World-action backbone. Horizontal rows denote states, not three param groups.
box(484,62,283,225,'gray','line',r=7)
txt(625,48,'Transformer B',23,weight='bold',anchor='middle')
for y,lab,col in ((83,'World / meta','world'),(151,'Future Fᵤ','future'),(219,'Action Aᵤ','action')):
    box(521,y,209,46,col+'_fill',col)
    txt(625,y+30,lab,21,col,weight='bold',anchor='middle')
path('M451 145H495V106H516','obs',1.8,True)
path('M495 145V174H516','obs',1.8,True)
path('M495 174V242H516','obs',1.8,True)
path('M747 177V235','muted',1.8,True,False,True)
box(733,196,29,22,'gray','gray',r=0,sw=0); txt(748,214,'G',20,weight='bold',anchor='middle')
txt(626,310,'Fᵤ, Aᵤ: noisy states; u: flow time',20,'muted',anchor='middle')

# Outputs: pose is deterministic; only the scene and action states use FM.
path('M730 106H795','future',2,True)
box(806,78,88,57,'future_fill','future')
txt(850,102,'Pose',20,'future',anchor='middle'); txt(850,125,'readout',20,'future',anchor='middle')
path('M894 106H920','future',2,True)
txt(982,70,'Target SE(3)',21,'future',weight='bold')
path('M938 124V92M938 124H970M938 124L922 139','muted',1.8)
path('M983 117L990 85M983 117L1016 124M983 117L968 130','future',2)
path('M944 108Q960 88 977 99','future',1.5,True)
txt(1033,114,'dₕ, φₕ',22,'future')

path('M730 174H795','future',2,True)
box(806,145,88,57,'future_fill','future')
txt(850,170,'FM',21,'future',anchor='middle'); txt(850,194,'solve',20,'future',anchor='middle')
path('M894 174H920','future',2,True)
for i in range(3):
    yy=160+i*14
    path(f'M930 {yy}C949 {yy-8} 966 {yy+6} 994 {yy-1}','future',1.7)
    for xx,dy in ((930,0),(951,-3),(972,1),(994,-1)):dot(xx,yy+dy,2.5)
txt(1015,167,'Scene tracks',21,'future',weight='bold'); txt(1015,194,'+ visibility',20,'future')

path('M730 242H795','action',2,True)
box(806,220,88,57,'action_fill','action')
txt(850,245,'FM',21,'action',anchor='middle'); txt(850,269,'solve',20,'action',anchor='middle')
path('M894 248H920','action',2,True)
for i in range(5):token(930+i*47,226,37,45,'action')
txt(948.5,256,'a₁',21,'action',anchor='middle'); txt(996,256,'a₂',21,'action',anchor='middle')
txt(1067,256,'⋯',25,'action',anchor='middle');txt(1137,256,'a₈',21,'action',anchor='middle')
txt(934,301,'First command at',20,'action')
txt(1095,301,'τ',20,'action')
txt(1107,291,'apply',14,'action')
txt(1107,309,'t,0',14,'action')
path('M1160 249H1184V338H65V323','muted',1.8,True)
box(463,324,324,27,'#FFFFFF','#FFFFFF',r=0,sw=0)
txt(625,345,'execute → observe → replan',20,'muted',anchor='middle')

# Mechanism insets with the same semantic colors, not a project status diagram.
path('M8 366H1192','muted',0.7)
txt(8,398,'b',24,weight='bold');txt(35,398,'Parameter grouping B',23,weight='bold')
txt(443,398,'c',24,weight='bold');txt(470,398,'Generation program G',23,weight='bold')
txt(950,398,'d',24,weight='bold');txt(977,398,'Training only',23,weight='bold')

# D/E are parameter organizations; the program independently sets access.
txt(12,435,'D',22,weight='bold')
box(40,414,151,34,'gray','line',r=4);txt(115,438,'Shared attention',20,anchor='middle')
path('M191 431H208','muted',1.6,True)
for xx,lab,col in ((220,'W','world'),(278,'F','future'),(336,'A','action')):
    box(xx,414,46,34,col+'_fill',col,r=4);txt(xx+23,438,lab,20,col,anchor='middle')
txt(300,473,'Separate FFNs',20,'muted',anchor='middle')
txt(12,519,'E',22,weight='bold')
box(40,496,151,40,'world_fill','world',r=4);txt(115,522,'World group',20,'world',anchor='middle')
box(220,496,162,40,'action_fill','action',r=4);txt(301,522,'Action group',20,'action',anchor='middle')
txt(211,561,'Separate attention, AdaLN, FFNs',20,'muted',anchor='middle')

# R1 uses future losses during learning but generates actions only at inference.
txt(445,435,'Auxiliary',20,weight='bold');txt(445,463,'R1',20,'muted')
token(555,417,38,34,'action');txt(574,441,'A',20,'action',anchor='middle')
path('M601 433H628','action',1.7,True);txt(642,440,'execute',20,'action')
txt(445,499,'Joint',20,weight='bold');txt(445,527,'R2–R4',20,'muted')
token(555,481,38,34,'future');txt(574,505,'F',20,'future',anchor='middle')
path('M603 498H635','muted',1.8,True,False,True)
token(647,481,38,34,'action');txt(666,505,'A',20,'action',anchor='middle')
txt(617,554,'access set by G',20,'muted',anchor='middle')
txt(735,435,'Sequential',20,weight='bold');txt(735,463,'R5 / R6',20,'muted')
token(738,481,38,34,'future');txt(757,505,'F',20,'future',anchor='middle')
path('M784 498H816','muted',1.8,True)
token(828,481,38,34,'action');txt(847,505,'A',20,'action',anchor='middle')
txt(802,554,'F→A or A→F',20,'muted',anchor='middle')

# Losses are outside the deployment graph. No GT-future edge into inference.
txt(1069,435,'Future labels',20,'future',anchor='middle')
path('M1069 443V461','future',1.7,True,True)
s.append('<text x="1069" y="487" font-size="20" fill="#BD7C0B" text-anchor="middle">λ<tspan font-size="14" baseline-shift="sub">F</tspan>ℒ<tspan font-size="14" baseline-shift="sub">F</tspan> + λ<tspan font-size="14" baseline-shift="sub">P</tspan>ℒ<tspan font-size="14" baseline-shift="sub">P</tspan> + λ<tspan font-size="14" baseline-shift="sub">V</tspan>ℒ<tspan font-size="14" baseline-shift="sub">V</tspan></text>')
txt(953,524,'Expert actions',20,'action')
path('M1091 518H1124','action',1.7,True,True)
s.append('<text x="1138" y="526" font-size="22" fill="#7753A4">ℒ<tspan font-size="15" baseline-shift="sub">A</tspan></text>')
txt(953,561,'Robot demos / DROID',20,'muted')

s.extend(['</g>','</svg>'])
dest=OUT/'model_design.svg'
dest.write_text('\n'.join(s)+'\n',encoding='utf-8')
print(svg_to_pdf(dest, preview_dir=REVIEW))
