"""Accepted vertical Fig.2; edit this scene and run to regenerate SVG/PDF/PNG.

Input images are raw observed RGB and a declared depth color map. Geometric
outputs illustrate ground-truth training labels, never claimed predictions.
"""
from pathlib import Path
from math import atan2, cos, sin
from html import escape
import base64
import json
import os

import numpy as np
import pypdfium2 as pdfium
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

OUT = Path(__file__).resolve().parent
ASSETS = OUT/'assets'
W, H = 1700, 915
WIDTH_MM = 174.625
SCALE = WIDTH_MM/25.4*72/W
FONT_DIR = Path(os.environ.get('WINDIR', 'C:/Windows'))/'Fonts'
for name, filename in [('F2Arial','arial.ttf'),('F2ArialBold','arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR/filename)))
C = dict(ink='#293840', muted='#657580', line='#90A5AD', faint='#D7E2E5',
         world='#1D8D78', world_fill='#EEF7F3', world_mid='#BCDCD0',
         target='#D26942', target_fill='#FBF0E9', target_mid='#ECC3B0',
         robot='#8D9DA8', robot_mid='#DCE4E9',
         act='#8160A9', act_fill='#F4EFF9', act_mid='#D5C4E6',
         white='#FFFFFF', attention='#EEF2F5')
svg, texts, arrows, group_stack = [], [], [], []
pdf = canvas.Canvas(str(OUT/'fig2_se3wam.pdf'),
                    pagesize=(W*SCALE,H*SCALE), pageCompression=1)
pdf.setTitle('FoveaWAM: vertical architecture with observed inputs and true training labels')
pdf.setAuthor('')
pdf.scale(SCALE,SCALE)


def group(name):
    group_stack.append(name)
    svg.append(f'<g id="{escape(name)}">')


def end():
    svg.append('</g>')
    group_stack.pop()


def paint(fill=None, stroke=None, sw=1.8, dash=None):
    if fill:
        pdf.setFillColor(HexColor(fill))
    if stroke:
        pdf.setStrokeColor(HexColor(stroke))
    pdf.setLineWidth(sw)
    pdf.setDash(dash or [])
    pdf.setLineCap(1)
    pdf.setLineJoin(1)


def attrs(fill=None, stroke=None, sw=1.8, dash=None):
    s=f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'
    if dash:
        s+=' stroke-dasharray="'+' '.join(map(str,dash))+'"'
    return s


def rect(x,y,w,h,fill=None,stroke=None,sw=1.8,r=0,dash=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {attrs(fill,stroke,sw,dash)}/>')
    paint(fill,stroke,sw,dash)
    if r:
        pdf.roundRect(x,H-y-h,w,h,r,stroke=int(bool(stroke)),fill=int(bool(fill)))
    else:
        pdf.rect(x,H-y-h,w,h,stroke=int(bool(stroke)),fill=int(bool(fill)))


def poly(points,fill=None,stroke=None,sw=1.8,close=False,dash=None):
    points=[tuple(map(float,p)) for p in points]
    tag='polygon' if close else 'polyline'
    ps=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
    svg.append(f'<{tag} points="{ps}" {attrs(fill,stroke,sw,dash)} stroke-linejoin="round" stroke-linecap="round"/>')
    paint(fill,stroke,sw,dash)
    p=pdf.beginPath();p.moveTo(points[0][0],H-points[0][1])
    for x,y in points[1:]:
        p.lineTo(x,H-y)
    if close:
        p.close()
    pdf.drawPath(p,stroke=int(bool(stroke)),fill=int(bool(fill)))


def arrow(points,col=None,sw=2.2,dash=None,head=8,record=True):
    col=col or C['ink']
    poly(points,stroke=col,sw=sw,dash=dash)
    x,y=points[-1];px,py=points[-2]
    a=atan2(y-py,x-px)
    poly([(x,y),(x-head*cos(a)+head*.42*sin(a),y-head*sin(a)-head*.42*cos(a)),
          (x-head*cos(a)-head*.42*sin(a),y-head*sin(a)+head*.42*cos(a))],fill=col,close=True)
    if record:
        arrows.append(dict(points=points,group='/'.join(group_stack)))


def circle(x,y,r,fill,stroke=None,sw=1):
    svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r:.3f}" {attrs(fill,stroke,sw)}/>')
    paint(fill,stroke,sw)
    pdf.circle(float(x),H-float(y),r,stroke=int(bool(stroke)),fill=1)


def text(x,y,value,size=27,col=None,bold=False,anchor='start'):
    col=col or C['ink']
    font='F2ArialBold' if bold else 'F2Arial'
    missing=[ch for ch in value if ord(ch) not in pdfmetrics.getFont(font).face.charToGlyph]
    if missing:
        raise ValueError((value,missing))
    width=pdfmetrics.stringWidth(value,font,size)
    left=x if anchor=='start' else x-width/2 if anchor=='middle' else x-width
    ascent=pdfmetrics.getAscent(font)*size/1000
    descent=pdfmetrics.getDescent(font)*size/1000
    texts.append(dict(text=value,x=left,y=y-ascent,width=width,height=ascent-descent,
                      size=size,group='/'.join(group_stack)))
    svg.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{col}">{escape(value)}</text>')
    pdf.setFillColor(HexColor(col));pdf.setFont(font,size)
    pdf.drawString(left,H-y,value)


def image_file(path,x,y,w,h):
    data=base64.b64encode(path.read_bytes()).decode('ascii')
    svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{data}"/>')
    pdf.drawImage(ImageReader(str(path)),x,H-y-h,w,h,mask='auto')


def tokens(x,y,n,w=25,h=20,gap=8,col='world'):
    for i in range(n):
        rect(x+i*(w+gap),y,w,h,C[col+'_mid'],C[col],1.3,r=2)


def readout(x,y,w,label,col):
    poly([(x,y),(x+w,y),(x+w-10,y+36),(x+10,y+36)],C['white'],col,1.7,True)
    text(x+w/2,y+26,label,26,col,anchor='middle')


def gripper(x,y,s=1):
    poly([(x,y-22*s),(x,y-8*s)],stroke=C['act'],sw=3*s)
    poly([(x-15*s,y-8*s),(x+15*s,y-8*s)],stroke=C['act'],sw=2.5*s)
    for side in [-1,1]:
        poly([(x+side*14*s,y-8*s),(x+side*14*s,y+12*s),(x+side*7*s,y+17*s)],stroke=C['act'],sw=2.5*s)


data=np.load(ASSETS/'geometry_labels.npz')
view=np.array([1.15,-1.75,1.30]);view/=np.linalg.norm(view)
right=np.cross([0,0,1],view);right/=np.linalg.norm(right)
up=np.cross(view,right)


def project(points):
    p=np.asarray(points)
    return np.stack([p@right,-p@up],axis=-1)


def fit_transform(points,x,y,w,h,padding=5):
    lo=np.min(points,axis=0);hi=np.max(points,axis=0)
    scale=min((w-2*padding)/(hi[0]-lo[0]),(h-2*padding)/(hi[1]-lo[1]))
    center=(lo+hi)/2
    return lambda p: (np.asarray(p)-center)*scale+[x+w/2,y+h/2]


POSE_SIZE=np.array([.060,.040,.035])  # glyph dimensions, not object geometry
corners=np.array([[i,j,k] for i in [-.5,.5] for j in [-.5,.5] for k in [-.5,.5]])*POSE_SIZE
edges=[(i,j) for i in range(8) for j in range(i+1,8) if np.sum(corners[i]!=corners[j])==1]
pose_vertices=[corners@r.T+p for r,p in zip(data['target_R_world'],data['target_pos_world'])]
pose_bounds=np.concatenate([project(pose_vertices[j]) for j in [0,1,4,7]])


def pose_panel(cx,y,w,h,horizon):
    to_screen=fit_transform(pose_bounds,cx-w/2,y,w,h,12)
    for j,col,dash in [(0,'#CED6DA',[4,4]),(horizon,C['target'],None)]:
        pts=to_screen(project(pose_vertices[j]))
        for a,b in edges:
            poly([pts[a],pts[b]],stroke=col,sw=1.25 if j==0 else 1.9,dash=dash)
    origin=data['target_pos_world'][horizon]
    r=data['target_R_world'][horizon]
    p=to_screen(project(origin))
    for axis in range(3):
        q=to_screen(project(origin+.022*r[:,axis]))
        arrow([p.tolist(),q.tolist()],C['target'],1.8,head=4.5,record=False)


cloud=data['cloud_xyz_world'];cloud2=project(cloud)
patch=data['patch_xyz_world'];patch2=project(patch)
flow=data['flow_xyz_world'];valid=data['flow_valid'];visible=data['flow_visible']
patch_keep=data['patch_keep']
flow_scale=3.0
all_cloud=np.concatenate([cloud2]+[project(patch+flow[:,j]*flow_scale)[patch_keep & valid[:,j]] for j in [0,3,6]])
cloud_colors=['#'+''.join(f'{int(v):02x}' for v in row) for row in data['cloud_rgb']]
cloud_order=np.argsort(cloud@view)


def flow_panel(cx,y,w,h,j):
    to_screen=fit_transform(all_cloud,cx-w/2,y,w,h,5)
    points=to_screen(cloud2)
    for k in cloud_order:
        x0,y0=points[k]
        circle(x0,y0,.92,cloud_colors[k])
    start=to_screen(patch2)
    finish=to_screen(project(patch+flow[:,j]*flow_scale))
    mag=np.linalg.norm(flow[:,j],axis=-1)
    for k in np.flatnonzero(patch_keep & valid[:,j]):
        if mag[k]>.002:
            arrow([start[k].tolist(),finish[k].tolist()],C['white'],3.7,head=5.2,record=False)
            arrow([start[k].tolist(),finish[k].tolist()],C['world'],1.8,head=4.5,record=False)
        else:
            circle(*start[k],1.12,'#9CAAA8')


rect(0,0,W,H,C['white'])
text(24,37,'(a) FoveaWAM',34,bold=True)

group('training-only-geometric-labels')
# The top row uses the same three geometric label snapshots as the horizontal.
poly([(40,86),(40,61),(1015,61),(1015,86)],stroke='#9BC7B7',sw=1.7,dash=[6,5])
rect(194,43,548,37,C['white'])
text(468,69,'Role-aware supervision · labels shown',27,C['world'],True,'middle')
rect(850,45,150,33,'#EDF5F0')
text(925,69,'TRAIN ONLY',25,C['world'],True,'middle')
text(275,111,'Sparse 3D scene flow',30,C['world'],True,'middle')
text(770,111,'Target SE(3) trajectory',30,C['target'],True,'middle')
flow_columns=[110,275,440]
pose_columns=[610,770,930]
for centers in [flow_columns,pose_columns]:
    for cx,ms in zip(centers,[50,200,350]):
        text(cx,151,f'τ + {ms} ms',25,C['muted'],anchor='middle')
for cx,j in zip(flow_columns,[0,3,6]):
    flow_panel(cx,164,150,126,j)
for cx,j in zip(pose_columns,[1,4,7]):
    pose_panel(cx,171,138,124,j)
text(275,325,'Displacement + visibility · arrows ×3',25,C['muted'],anchor='middle')
text(275,354,'+ depth · DINO · dynamic RGB',25,C['muted'],anchor='middle')
text(770,325,'8 horizons · 50–400 ms',25,C['muted'],anchor='middle')
text(770,354,'+ current target RGB',25,C['muted'],anchor='middle')
readout(180,370,190,'Patches',C['world'])
readout(675,370,190,'Mean M',C['target'])
for x,col in [(275,C['world']),(770,C['target'])]:
    arrow([(x,369),(x,361)],col,1.8,[5,4],4.5)
end()

group('action-readout')
text(1175,111,'Action chunk',30,C['act'],True,'middle')
text(1175,153,'Time-indexed',26,C['act'],anchor='middle')
path=[(1067+i*31,229-25*sin(i*.22)) for i in range(8)]
poly(path,stroke='#B79BCF',sw=2.2)
for i,(x,y) in enumerate(path):
    circle(x,y,3.3,C['act'])
    if i in [0,3,7]:
        gripper(x,y-12,.72)
tokens(1063,281,8,w=22,h=21,gap=6,col='act')
readout(1090,370,170,'Velocity',C['act'])
arrow([(1175,369),(1175,305)],C['act'],2.1,head=7)
end()

group('shared-twelve-layer-backbone')
text(24,429,'Backbone ×12',26,C['muted'])
rect(31,439,1294,194,C['white'],'#D8E2E5',1.5,r=7)
rect(24,446,1294,194,'#F9FBFB','#A8BEC2',1.8,r=7)
rect(44,463,948,58,C['world_fill'],'#9EC5B6',1.7,r=5)
text(518,502,'World FFN',31,C['world'],True,'middle')
rect(1050,463,250,58,C['act_fill'],'#B9A0D3',1.7,r=5)
text(1175,502,'Action FFN',30,C['act'],True,'middle')
for x,col in [(275,C['world']),(770,C['target']),(1175,C['act'])]:
    arrow([(x,462),(x,408)],col,2.2,[6,4] if x!=1175 else None,7)
    arrow([(x,563),(x,523)],col,2.1,head=7)
rect(44,565,1256,53,C['attention'],'#A5B8C2',1.7,r=5)
text(672,601,'Masked attention · shared QKV / output',29,C['ink'],True,'middle')
for x,col in [(341,C['world']),(519,C['target']),(724,C['robot']),
              (878,C['world']),(1188,C['act'])]:
    arrow([(x,658),(x,620)],col,2.1,head=7)
end()

group('typed-input-tokens')
tokens(45,660,13,w=20,h=24,gap=6,col='world')
text(408,680,'…',28,C['world'])
tokens(450,660,4,w=22,h=24,gap=7,col='target')
tokens(665,660,4,w=18,h=24,gap=7,col='robot')
text(44,724,'Scene S · 212 tokens',28,C['world'],True)
tokens(800,660,8,w=17,h=24,gap=6,col='world')
text(889,724,'Summary M',29,C['world'],True,'middle')
text(889,757,'16 learned tokens',25,C['muted'],anchor='middle')
tokens(1065,660,8,w=22,h=24,gap=6,col='act')
text(1175,724,'Action A(u)',29,C['act'],True,'middle')
text(1175,757,'Noisy actions',26,C['act'],anchor='middle')
text(1175,790,'+ flow time u',25,C['muted'],anchor='middle')
text(1175,824,'Action flow matching',25,C['act'],anchor='middle')
end()

group('observed-metric-inputs')
text(77,755,'RGB',25,C['muted'],anchor='middle')
text(194,755,'Depth',25,C['muted'],anchor='middle')
image_file(ASSETS/'rgb.png',25,768,105,105)
image_file(ASSETS/'depth.png',142,768,105,105)
rect(25,768,105,105,stroke='#C7D4D8',sw=1.4)
rect(142,768,105,105,stroke='#C7D4D8',sw=1.4)
text(136,905,'Current RGB-D',27,C['ink'],True,'middle')
arrow([(249,820),(265,820)],C['world'],2.1,head=6)
rect(267,793,206,76,C['world_fill'],'#B2D2C5',1.5,r=5)
text(370,824,'Frozen MAE',27,C['world'],True,'middle')
text(370,856,'XYZ · 3D RoPE',25,C['world'],anchor='middle')
arrow([(341,791),(341,686)],C['world'],2.1,head=7)

for i in range(8):
    x=492+i*23
    rect(x,787,17,32,C['target_fill'],C['target'],1.1,r=2)
    origin=np.array([x+8,804])
    rotation=data['target_history_R_world'][i]
    for axis in range(3):
        d=project(rotation[:,axis])
        d=d/max(np.linalg.norm(d),.01)*5.5
        arrow([origin.tolist(),(origin+d).tolist()],C['target'],1.1,head=2.2,record=False)
arrow([(519,785),(519,686)],C['target'],2.1,head=7)
text(580,875,'SE(3) history',27,C['target'],True,'middle')
text(580,905,'8 samples · 350 ms',25,C['muted'],anchor='middle')

for i in range(8):
    x=720+i*19
    rect(x,787,13,32,C['robot_mid'],C['robot'],1.1,r=2)
    for y in [797,806]:
        poly([(x+3,y),(x+10,y)],stroke='#A9B8C2',sw=1)
arrow([(724,785),(724,686)],C['robot'],2.1,head=7)
text(792,875,'Robot history',27,C['muted'],True,'middle')
text(792,905,'8 states',25,C['muted'],anchor='middle')
end()

# Two compact mechanism panels follow the user's vertical reference.
poly([(1345,24),(1345,910)],stroke=C['faint'],sw=1.5)
group('directed-attention-mask')
text(1375,37,'(b) Attention mask',32,bold=True)
text(1534,102,'keys →',25,C['muted'],anchor='middle')
mx,my,cell=1450,148,50
colors=[C['world_mid'],C['world_mid'],C['act_mid']]
for i,label in enumerate(['S','M','A']):
    col=[C['world'],C['world'],C['act']][i]
    text(mx+i*cell+cell/2,my-12,label,28,col,True,'middle')
    text(mx-17,my+i*cell+33,label,28,col,True,'end')
for r in range(3):
    for c in range(3):
        rect(mx+c*cell,my+r*cell,cell,cell,colors[r] if c<=r else C['white'],'#AABBC6',1.3)
text(1450,335,'queries ↓',25,C['muted'])
text(1380,380,'World never reads actions',25,C['muted'])
text(1380,415,'A attends to S, M, A',25,C['act'])
end()

group('cached-inference')
text(1375,473,'(c) Cached inference',32,bold=True)
text(1380,512,'Forecast readouts skipped',25,C['muted'])
rect(1410,545,245,68,C['world_fill'],'#A2C6B7',1.7,r=5)
text(1532.5,575,'World ×1',29,C['world'],True,'middle')
text(1532.5,602,'per query',25,C['world'],anchor='middle')
arrow([(1532.5,615),(1532.5,650)],C['world'],2.1,head=7)
rect(1410,652,245,42,'#F5F8F9','#B4C5CD',1.5,r=4)
text(1532.5,681,'Cache S, M K / V',26,C['ink'],anchor='middle')
arrow([(1532.5,696),(1532.5,732)],C['act'],2.1,head=7)
rect(1410,734,245,68,C['act_fill'],'#BAA2D2',1.7,r=5)
text(1532.5,764,'Action ×5',29,C['act'],True,'middle')
text(1532.5,793,'Euler integration',25,C['act'],anchor='middle')
arrow([(1532.5,804),(1532.5,848)],C['act'],2.1,head=7)
tokens(1431,850,8,w=20,h=20,gap=6,col='act')
text(1532.5,905,'Time-indexed commands',25,C['act'],anchor='middle')
end()

assert not group_stack
outside=[t for t in texts if t['x']<0 or t['x']+t['width']>W or t['y']<0 or t['y']+t['height']>H]
if outside:
    raise ValueError(outside)
pdf.showPage();pdf.save()
desc=('Vertical FoveaWAM architecture with the same real inputs, labels and baseline as '
      'the horizontal candidate. Current RGB-D and histories form S, 16 learned tokens form M. '
      'The shared-projection 12-layer backbone has separate world/action FFNs. '
      'Training-only patch readouts predict sparse 3D displacement/visibility and visual '
      'auxiliaries; mean M predicts SE(3) and current target RGB. Ground-truth labels '
      'at 50,200,350 ms are shown, with flow arrows at 3x display scale. '
      'The directed mask is S->S, M->S,M, A->S,M,A. World K,V are cached once '
      'for five Euler action steps. Action icons and pose-glyph size are schematic.')
document=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_MM}mm" '
          f'height="{WIDTH_MM*H/W:.6f}mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">\n'
          '<title id="title">FoveaWAM architecture</title>\n'
          f'<desc id="desc">{escape(desc)}</desc>\n'+'\n'.join(svg)+'\n</svg>\n')
(OUT/'fig2_se3wam.svg').write_text(document,encoding='utf-8')
(OUT/'layout_metadata.json').write_text(json.dumps(dict(texts=texts,arrows=arrows),ensure_ascii=False,indent=2),encoding='utf-8')
doc=pdfium.PdfDocument(str(OUT/'fig2_se3wam.pdf'));page=doc[0]
page.render(scale=300/72).to_pil().save(OUT/'fig2_se3wam.png')
page.render(scale=96/72).to_pil().save(OUT/'fig2_paper_width.png')
print(json.dumps(dict(width_mm=WIDTH_MM,height_mm=WIDTH_MM*H/W,
                      minimum_text_pt=min(t['size'] for t in texts)*SCALE,
                      native_texts=len(texts),embedded_images=sum(s.startswith('<image ') for s in svg),
                      dense_points_per_flow_panel=len(cloud)),indent=2))
