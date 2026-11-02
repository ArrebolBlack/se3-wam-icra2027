"""Editable Fig. 2, grounded in the current FoveaWAM manuscript and model.

One scene description produces native-text SVG and vector PDF. No model outputs
or measured results are fabricated; all miniature graphics are schematics.
Run with Python + reportlab. See README.txt for sources and reproduction.
"""
from pathlib import Path
from math import atan2, cos, sin, pi, exp
from html import escape
import json
import os
import re

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

OUT = Path(__file__).resolve().parent
W, H = 1500, 690
WIDTH_PT = 6.875 * 72  # Current CVPR manuscript's double-column text width.
SCALE = WIDTH_PT / W
FONT_DIR = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
pdfmetrics.registerFont(TTFont('FigureArial', str(FONT_DIR / 'arial.ttf')))
pdfmetrics.registerFont(TTFont('FigureArialBold', str(FONT_DIR / 'arialbd.ttf')))

C = dict(ink='#283340', muted='#687580', faint='#E5EAED', line='#8D99A3',
         obs='#487C9F', obs_fill='#EDF4F8', obs_mid='#BBD4E5',
         target='#358C8A', target_fill='#CCE5DF', robot='#8B9CA7',
         world='#AD7A36', world_fill='#FCF6EA', world_mid='#E9CC93',
         act='#8266A7', act_fill='#F3EFF8', act_mid='#CFBFE4', white='#FFFFFF')
svg = []
texts = []
groups = []
pdf = canvas.Canvas(str(OUT / 'fig2_se3wam.pdf'), pagesize=(WIDTH_PT, H*SCALE),
                    pageCompression=1)
pdf.setTitle('FoveaWAM - Fig. 2 method architecture')
pdf.setAuthor('')
pdf.scale(SCALE, SCALE)

def group(name):
    svg.append(f'<g id="{escape(name)}">')
    groups.append(name)

def end():
    svg.append('</g>')
    groups.pop()

def paint(fill=None, stroke=None, sw=2, dash=None):
    if fill: pdf.setFillColor(HexColor(fill))
    if stroke: pdf.setStrokeColor(HexColor(stroke))
    pdf.setLineWidth(sw)
    pdf.setDash(dash or [])

def attrs(fill=None, stroke=None, sw=2, dash=None):
    v = f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'
    if dash: v += ' stroke-dasharray="' + ' '.join(map(str, dash)) + '"'
    return v

def rect(x,y,w,h,fill=None,stroke=None,sw=2,r=0,dash=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {attrs(fill,stroke,sw,dash)}/>')
    paint(fill,stroke,sw,dash)
    if r: pdf.roundRect(x,H-y-h,w,h,r,stroke=int(bool(stroke)),fill=int(bool(fill)))
    else: pdf.rect(x,H-y-h,w,h,stroke=int(bool(stroke)),fill=int(bool(fill)))

def poly(points,fill=None,stroke=None,sw=2,close=False,dash=None):
    tag = 'polygon' if close else 'polyline'
    ps=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
    svg.append(f'<{tag} points="{ps}" {attrs(fill,stroke,sw,dash)} stroke-linejoin="round" stroke-linecap="round"/>')
    paint(fill,stroke,sw,dash)
    p=pdf.beginPath();p.moveTo(points[0][0],H-points[0][1])
    for x,y in points[1:]:p.lineTo(x,H-y)
    if close:p.close()
    pdf.setLineJoin(1);pdf.setLineCap(1)
    pdf.drawPath(p,stroke=int(bool(stroke)),fill=int(bool(fill)))

def arrow(points,color=None,sw=2.6,dash=None,head=10):
    color=color or C['ink']
    poly(points,stroke=color,sw=sw,dash=dash)
    x,y=points[-1];px,py=points[-2];ang=atan2(y-py,x-px)
    poly([(x,y),(x-head*cos(ang)+head*.43*sin(ang),y-head*sin(ang)-head*.43*cos(ang)),
          (x-head*cos(ang)-head*.43*sin(ang),y-head*sin(ang)+head*.43*cos(ang))],
         fill=color,close=True)

def circle(x,y,r,fill=None,stroke=None,sw=2):
    svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" {attrs(fill,stroke,sw)}/>')
    paint(fill,stroke,sw)
    pdf.circle(x,H-y,r,stroke=int(bool(stroke)),fill=int(bool(fill)))

def text(x,y,t,size=27,color=None,bold=False,anchor='start'):
    color=color or C['ink'];font='FigureArialBold' if bold else 'FigureArial'
    missing=[ch for ch in t if ord(ch) not in pdfmetrics.getFont(font).face.charToGlyph]
    if missing:raise ValueError(f'Font lacks glyphs {missing} in {t!r}')
    width=pdfmetrics.stringWidth(t,font,size)
    left=x if anchor=='start' else x-width if anchor=='end' else x-width/2
    texts.append(dict(text=t,x=left,y=y-size*.8,width=width,height=size,group='/'.join(groups)))
    svg.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{escape(t)}</text>')
    pdf.setFillColor(HexColor(color));pdf.setFont(font,size)
    pdf.drawString(left,H-y,t)

def mathtext(x,y,t,size=27,color=None,anchor='start'):
    # Native, independently editable text spans; no unsupported Unicode subscripts.
    parts=[]
    for match in re.finditer(r'(_.)|([^_]+)',t):
        part=match.group()
        sub=part.startswith('_')
        value=part[1:] if sub else part
        fs=size*.72 if sub else size
        parts.append((value,fs,6 if sub else 0,pdfmetrics.stringWidth(value,'FigureArial',fs)))
    width=sum(p[3] for p in parts)
    cursor=x if anchor=='start' else x-width if anchor=='end' else x-width/2
    for value,fs,dy,pw in parts:
        text(cursor,y+dy,value,fs,color)
        cursor+=pw

def tokenrow(x,y,n,w=18,h=25,gap=6,fill=None,stroke=None):
    for i in range(n):rect(x+i*(w+gap),y,w,h,fill or C['obs_mid'],stroke or C['obs'],1.2,r=2)

def triad(x,y,s=25,color=None,angle=0):
    color=color or C['target']
    for a,l in [(angle,1),(angle-pi/2,.85),(angle+2.45,.65)]:
        arrow([(x,y),(x+s*l*cos(a),y+s*l*sin(a))],color,1.8,head=5)
    circle(x,y,2.2,color)

def title(x,y,index,t):
    text(x,y,f'({index})',31,bold=True)
    text(x+49,y,t,31,bold=True)

def input_scene(x,y,w,h):
    # Original vector vignette: workspace, conveyor, target and robot gripper.
    rect(x,y,w,h,C['obs_fill'],C['obs_mid'],1.6,r=3)
    poly([(x+10,y+h-23),(x+w-21,y+h-23),(x+w-5,y+h-42),(x+26,y+h-42)],
         fill='#D8E3EA',stroke='#9EB2C0',sw=1.2,close=True)
    for k in range(5):
        xx=x+20+k*17
        poly([(xx,y+h-24),(xx+15,y+h-41)],stroke='#B7C8D3',sw=1.1)
    # Target cube.
    poly([(x+69,y+49),(x+86,y+43),(x+99,y+50),(x+82,y+57)],
         fill='#A9CDE0',stroke=C['obs'],sw=1.4,close=True)
    poly([(x+69,y+49),(x+82,y+57),(x+82,y+75),(x+69,y+66)],
         fill='#6FA5C0',stroke=C['obs'],sw=1.4,close=True)
    poly([(x+82,y+57),(x+99,y+50),(x+99,y+68),(x+82,y+75)],
         fill='#C6DCE9',stroke=C['obs'],sw=1.4,close=True)
    poly([(x+21,y+61),(x+37,y+29),(x+61,y+22),(x+77,y+33)],stroke=C['muted'],sw=6)
    for px,py in [(21,61),(37,29),(61,22)]:circle(x+px,y+py,4,C['white'],C['muted'],2)
    poly([(x+73,y+29),(x+70,y+39),(x+75,y+42)],stroke=C['muted'],sw=2.6)
    poly([(x+81,y+33),(x+83,y+41),(x+78,y+45)],stroke=C['muted'],sw=2.6)

# Compact, bottom-to-top model overview. The geometry drawings are schematics.
def cube(x,y,s=28,col=None,angle=0):
    col=col or C['target']
    a=(s*cos(angle),s*sin(angle))
    b=(s*.62*cos(angle-2.15),s*.62*sin(angle-2.15))
    c=(0,-s*.84)
    pt=lambda i,j,k:(x+i*a[0]+j*b[0]+k*c[0],y+i*a[1]+j*b[1]+k*c[1])
    poly([pt(0,0,0),pt(1,0,0),pt(1,0,1),pt(0,0,1)],'#D9E9E3',col,1.4,True)
    poly([pt(0,0,0),pt(0,1,0),pt(0,1,1),pt(0,0,1)],'#B5D7CC',col,1.4,True)
    poly([pt(0,0,1),pt(1,0,1),pt(1,1,1),pt(0,1,1)],'#ECF5F0',col,1.4,True)

def grip(x,y,s=1,col=None):
    col=col or C['act']
    poly([(x-17*s,y-10*s),(x+17*s,y-10*s)],stroke=col,sw=3*s)
    poly([(x-15*s,y-10*s),(x-15*s,y+12*s),(x-7*s,y+17*s)],stroke=col,sw=3*s)
    poly([(x+15*s,y-10*s),(x+15*s,y+12*s),(x+7*s,y+17*s)],stroke=col,sw=3*s)
    poly([(x,y-27*s),(x,y-10*s)],stroke=col,sw=4*s)

rect(0,0,W,H,C['white'])

# Training outputs: two geometric roles, with only a single open bracket.
group('role-aware-geometry')
poly([(240,35),(240,22),(1010,22),(1010,35)],stroke='#BA9A65',sw=1.6,dash=[6,5])
rect(398,5,454,33,C['white'])
text(625,28,'Role-aware geometry · training only',26,C['world'],True,'middle')
text(430,73,'Sparse 3D scene motion',27,C['world'],True,'middle')
text(845,73,'Target SE(3) trajectory',27,C['target'],True,'middle')
# A perspective surface, with both moving target and gripper scene points.
grid=[]
for row in range(4):
    rr=[]
    for col in range(8):
        xx=292+col*29+row*16; yy=145+row*14-col*4.2
        rr.append((xx,yy))
        circle(xx,yy,2.2,'#C5B493')
    poly(rr,stroke='#E3D8C4',sw=.9)
    grid.append(rr)
for col in range(8):poly([grid[r][col] for r in range(4)],stroke='#E3D8C4',sw=.9)
cube(420,131,27,C['world'],-.15)
grip(344,119,.65,C['world'])
for xx,yy,dx,dy in [(326,134,18,-8),(343,146,22,-7),(355,133,20,-8),
                   (414,137,23,-6),(429,132,23,-7),(436,150,21,-7),
                   (451,139,23,-6),(465,169,15,-4),(489,158,12,-3)]:
    circle(xx,yy-20,2.3,C['world'])
    arrow([(xx,yy-20),(xx+dx,yy+dy-20)],C['world'],1.8,head=5)
text(430,211,'3D displacement + visibility',24,C['muted'],anchor='middle')
# A rigid object rotates and translates along a forecast trajectory.
trajectory=[(727,161),(795,147),(866,139),(935,119)]
poly(trajectory,stroke='#B7D6CC',sw=2,dash=[5,4])
for i,(xx,yy) in enumerate(trajectory):
    cube(xx,yy,25,C['target'],-.12-i*.18)
    triad(xx-4,yy+5,20,C['target'],-.12-i*.18)
mathtext(845,211,'(d_h, φ_h)   50–400 ms',24,C['muted'],'middle')
# Lightweight readout glyphs instead of extra nested head boxes.
poly([(382,246),(478,246),(492,226),(368,226)],C['world_fill'],'#C7A46F',1.4,True)
text(430,242,'Patch',22,C['world'],anchor='middle')
poly([(797,246),(893,246),(907,226),(783,226)],'#EAF4EF','#77AEA0',1.4,True)
text(845,242,'Mean M',22,C['target'],anchor='middle')
arrow([(430,315),(430,248)],C['world'],2.2,[6,4],8)
arrow([(845,315),(845,248)],C['target'],2.2,[6,4],8)
end()

group('action-readout')
text(1260,73,'Action chunk',27,C['act'],True,'middle')
# Eight compact command vectors and the corresponding end-effector path.
path=[(1156+i*28,161-26*sin(i*.21)) for i in range(8)]
poly(path,stroke='#CAB9DD',sw=2)
for i,(xx,yy) in enumerate(path):
    circle(xx,yy,3.3,C['act'])
    if i in (0,3,7):grip(xx,yy-9,.63,C['act'])
tokenrow(1145,183,8,23,19,6,C['act_mid'],C['act'])
poly([(1212,246),(1308,246),(1322,226),(1198,226)],C['act_fill'],'#BCA9D3',1.4,True)
text(1260,242,'Velocity',22,C['act'],anchor='middle')
arrow([(1260,315),(1260,248)],C['act'],2.4,head=8)
arrow([(1260,226),(1260,207)],C['act'],1.8,head=6)
# Integration is an action-only loop; the world never depends on flow time.
arrow([(1323,237),(1436,237),(1436,484),(1402,484)],C['act'],1.8,head=7)
text(1421,218,'Euler ×5',23,C['act'],anchor='end')
end()

group('world-action-transformer')
# A single repeated layer, sharing attention and separating only the FFNs.
rect(258,293,1150,145,'#FFFFFF','#D5DCE1',1.3,r=8)
rect(252,299,1150,145,'#F8FAFB','#B8C3CA',1.6,r=8)
text(1400,282,'×24',24,C['muted'],anchor='end')
rect(272,315,735,45,C['world_fill'],'#CCB17C',1.5,r=5)
text(640,346,'World FFN',27,C['world'],True,'middle')
rect(1042,315,340,45,C['act_fill'],'#B8A4CE',1.5,r=5)
text(1212,346,'Action FFN',27,C['act'],True,'middle')
for xx,col in [(430,C['obs']),(845,C['target']),(1260,C['act'])]:
    arrow([(xx,385),(xx,362)],col,1.8,head=7)
rect(272,386,1110,42,'#EAF0F3','#A5B5C0',1.5,r=5)
text(620,415,'Shared masked attention',27,C['ink'],True,'middle')
# The scene/summary cache belongs to each layer's attention, not to a prediction head.
arrow([(1007,407),(1181,407)],C['act'],2,head=7)
text(1093,380,'cached S,M K,V',23,C['act'],anchor='middle')
for xx,col in [(430,C['obs']),(845,C['target']),(1260,C['act'])]:
    arrow([(xx,477),(xx,430)],col,2.2,head=8)
end()

group('structured-attention-mask')
text(124,321,'Attention mask',24,C['ink'],True,'middle')
mx,my,cs=88,355,32
for i,l in enumerate(['S','M','A']):
    text(mx+i*cs+cs/2,my-9,l,23,C['ink'],anchor='middle')
    text(mx-15,my+i*cs+24,l,23,C['ink'],anchor='end')
for r in range(3):
    for c in range(3):
        fill=[C['obs_mid'],C['world_mid'],C['act_mid']][r] if (r,c) in [(0,0),(1,0),(1,1),(2,0),(2,1),(2,2)] else '#FFFFFF'
        rect(mx+c*cs,my+r*cs,cs,cs,fill,'#ACBAC4',1)
text(124,480,'Rows read columns',21,C['muted'],anchor='middle')
end()

group('input-tokens')
text(477,535,'Scene S',26,C['obs'],True,'middle')
tokenrow(279,479,6,22,24,6,C['obs_mid'],C['obs'])
text(452,499,'…',26,C['obs'])
tokenrow(492,479,3,22,24,6,C['target_fill'],C['target'])
tokenrow(609,479,3,22,24,6,'#D8E1E6',C['robot'])
text(845,535,'Summary M',26,C['world'],True,'middle')
tokenrow(740,479,8,20,24,7,C['world_mid'],C['world'])
mathtext(1260,535,'Action A(u)',26,C['act'],'middle')
tokenrow(1134,479,8,25,24,7,C['act_mid'],C['act'])
text(845,566,'16 learned tokens',24,C['muted'],anchor='middle')
text(1260,566,'Noisy actions + flow time u',24,C['act'],anchor='middle')
# The current-only visual observation plus short target and robot histories.
text(158,678,'Current RGB-D',25,C['obs'],True,'middle')
input_scene(52,556,130,93)
# Depth plane, visually distinct from the RGB thumbnail.
poly([(195,617),(225,602),(225,641),(195,655)],'#D2E3ED',C['obs'],1.2,True)
for i in range(1,4):
    poly([(195+i*7.5,617-i*3.75),(195+i*7.5,655-i*3.5)],stroke='#94B7CF',sw=.9)
text(325,563,'Frozen MAE',24,C['obs'],anchor='middle')
text(325,594,'XYZ / 3D RoPE',23,C['obs'],anchor='middle')
arrow([(184,576),(220,576),(220,534),(349,534),(349,505)],C['obs'],2,head=7)
poly([(210,608),(220,608),(220,576)],stroke=C['obs'],sw=1.5)
# Pose-plus-motion history uses 8 samples; the miniature shows a subsampled path.
hist=[(464,621),(492,614),(520,604),(549,600)]
poly(hist,stroke='#A1C9C0',sw=1.8)
for i,(xx,yy) in enumerate(hist):
    triad(xx,yy,19,C['target'],-.2+i*.12)
arrow([(530,576),(530,505)],C['target'],2,head=7)
text(502,653,'Target history',24,C['target'],True,'middle')
text(502,678,'SE(3) + motion',22,C['muted'],anchor='middle')
tokenrow(621,591,4,14,23,5,'#D8E1E6',C['robot'])
poly([(624,628),(646,622),(666,625),(687,616)],stroke=C['robot'],sw=1.6)
arrow([(649,576),(649,505)],C['robot'],2,head=7)
text(687,653,'Robot history',24,C['muted'],True,'middle')
end()

group('compact-inference-note')
# A single note replaces the duplicate deployment flowchart.
poly([(767,595),(1387,595)],stroke=C['faint'],sw=1.4)
text(1076,631,'World once per query · action-only denoising',24,C['muted'],anchor='middle')
text(1076,668,'Geometry readouts are omitted at inference',23,C['muted'],anchor='middle')
end()

assert not groups
pdf.showPage();pdf.save()
description=('FoveaWAM method architecture. Current RGB-D and target/robot histories '
             'form scene tokens; a shared-attention transformer uses separate world and '
             'action FFNs. Training-only heads predict scene flow and target SE(3). '
             'Actions read scene and summary tokens. World conditioning is cached for five Euler '
             'action steps. All graphics are editable schematic vector objects.')
document=(f'<svg xmlns="http://www.w3.org/2000/svg" width="174.625mm" height="{H/W*174.625:.6f}mm" '
          f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">\n'
          '<title id="title">FoveaWAM Fig. 2</title>\n'
          f'<desc id="desc">{escape(description)}</desc>\n'+'\n'.join(svg)+'\n</svg>\n')
(OUT/'fig2_se3wam.svg').write_text(document,encoding='utf-8')
(OUT/'layout_text_boxes.json').write_text(json.dumps(texts,indent=2,ensure_ascii=False),encoding='utf-8')
outside=[t for t in texts if t['x']<0 or t['x']+t['width']>W or t['y']<0 or t['y']+t['height']>H+2]
if outside:raise ValueError(f'Text outside canvas: {outside}')
print(json.dumps({'pdf':str(OUT/'fig2_se3wam.pdf'),'svg':str(OUT/'fig2_se3wam.svg'),
                  'width_mm':174.625,'height_mm':H/W*174.625,'text_objects':len(texts),
                  'minimum_text_pt':min(t['height'] for t in texts)*SCALE},indent=2))
