"""Editable vector Fig.2 around measured Dynamic-14 images and GT geometry."""
from pathlib import Path
from math import atan2, cos, sin, pi
from html import escape
import base64
import io
import json
import os
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image, ImageDraw
from scipy.spatial.transform import Rotation
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

OUT = Path(__file__).resolve().parent
ASSETS = OUT/'assets'
W, H = 1500, 540
WIDTH_PT = 6.875*72
SCALE = WIDTH_PT/W
FONT_DIR = Path(os.environ.get('FIGURE_FONT_DIR', 'C:/Windows/Fonts'))
for name, file in [('Arial', 'arial.ttf'), ('ArialBold', 'arialbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(FONT_DIR/file)))
C = dict(ink='#273442', muted='#66737C', line='#ACB7BE', faint='#DCE3E8',
         blue='#286E9D', blue_mid='#BAD5E7', blue_fill='#EDF5FA',
         orange='#D3771E', orange_light='#E6B87C', orange_fill='#FFF9F0',
         purple='#8157A8', purple_mid='#D7C5E8', purple_fill='#F4EFF9',
         gray='#AEB6BD', gray_fill='#E7EAED', white='#FFFFFF')
A = dict(np.load(ASSETS/'labels.npz'))
svg, texts, groups = [], [], []
pdf = canvas.Canvas(str(OUT/'fig2_se3wam.pdf'), pagesize=(WIDTH_PT, H*SCALE), initialFontName='Arial')
pdf.setTitle('SE(3)-WAM: role-aware geometry and shared world-action backbone')
pdf.scale(SCALE, SCALE)


def group(name):
    svg.append(f'<g id="{name}">'); groups.append(name)


def end():
    svg.append('</g>'); groups.pop()


def paint(fill=None, stroke=None, sw=1, dash=None):
    if fill: pdf.setFillColor(HexColor(fill))
    if stroke: pdf.setStrokeColor(HexColor(stroke))
    pdf.setLineWidth(sw); pdf.setDash(dash or [])


def attrs(fill=None, stroke=None, sw=1, dash=None):
    a = f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'
    if dash: a += ' stroke-dasharray="'+' '.join(map(str,dash))+'"'
    return a


def rect(x,y,w,h,fill=None,stroke=None,sw=1,r=0,dash=None):
    svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" {attrs(fill,stroke,sw,dash)}/>')
    paint(fill,stroke,sw,dash)
    pdf.roundRect(x,H-y-h,w,h,r,stroke=int(bool(stroke)),fill=int(bool(fill)))


def poly(points,stroke=None,sw=1,fill=None,close=False,dash=None):
    points=np.asarray(points); tag='polygon' if close else 'polyline'
    s=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
    svg.append(f'<{tag} points="{s}" {attrs(fill,stroke,sw,dash)} stroke-linecap="round" stroke-linejoin="round"/>')
    paint(fill,stroke,sw,dash); p=pdf.beginPath(); p.moveTo(points[0,0],H-points[0,1])
    for x,y in points[1:]: p.lineTo(x,H-y)
    if close:p.close()
    pdf.setLineCap(1);pdf.setLineJoin(1)
    pdf.drawPath(p,stroke=int(bool(stroke)),fill=int(bool(fill)))


def arrow(points,color,sw=2,head=7,dash=None):
    points=np.asarray(points);poly(points,color,sw,dash=dash)
    x,y=points[-1];dx,dy=points[-1]-points[-2];ang=atan2(dy,dx)
    poly([(x,y),(x-head*cos(ang)+head*.37*sin(ang),y-head*sin(ang)-head*.37*cos(ang)),
          (x-head*cos(ang)-head*.37*sin(ang),y-head*sin(ang)+head*.37*cos(ang))],fill=color,close=True)


def dot(x,y,r,fill,stroke=None,sw=1):
    svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{r}" {attrs(fill,stroke,sw)}/>')
    paint(fill,stroke,sw);pdf.circle(x,H-y,r,stroke=int(bool(stroke)),fill=1)


def text(x,y,t,size=21,color=None,bold=False,anchor='start'):
    color=color or C['ink'];font='ArialBold' if bold else 'Arial'
    assert all(ord(c) in pdfmetrics.getFont(font).face.charToGlyph for c in t),t
    width=pdfmetrics.stringWidth(t,font,size)
    left=x if anchor=='start' else x-width if anchor=='end' else x-width/2
    texts.append(dict(text=t,x=left,y=y-size*.8,width=width,height=size,group='/'.join(groups)))
    svg.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{escape(t)}</text>')
    pdf.setFillColor(HexColor(color));pdf.setFont(font,size);pdf.drawString(left,H-y,t)


def bitmap(im,x,y,w,h):
    stream=io.BytesIO();im.save(stream,format='PNG');encoded=base64.b64encode(stream.getvalue()).decode()
    svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{encoded}"/>')
    pdf.drawImage(ImageReader(im),x,H-y-h,w,h,mask='auto')


def project(points):
    cam=A['world_from_camera_cv'];p=(np.asarray(points)-cam[:3,3])@cam[:3,:3]
    q=p@A['camera_intrinsics'].T
    return (q[...,:2]/q[...,2,None]+.5)*(1024/224)-.5


beauty=Image.open(ASSETS/'rgb_blender.png').convert('RGB')


def scene(x,y,w,crop):
    im=beauty.crop(crop);h=w*im.height/im.width;bitmap(im,x,y,w,h)
    scale=w/(crop[2]-crop[0])
    return lambda points:(project(points)-crop[:2])*scale+[x,y]


def pose_overlay(to_canvas,kind):
    poses=A['history_pose_world_xyzw' if kind=='history' else 'future_pose_world_xyzw']
    color=C['blue' if kind=='history' else 'orange'];size=.003 if kind=='future' else .007
    origins=to_canvas(poses[:,:3]);poly(origins,color,1.5)
    for pose in poses:
        p=pose[:3];R=Rotation.from_quat(pose[3:]).as_matrix();o=to_canvas(p)
        for j in range(3):
            endpoint=to_canvas(p+R[:,j]*size)
            poly([o,endpoint],C['white'],3.6 if kind=='future' else 3.0)
            arrow([o,endpoint],color,2.4 if kind=='future' else 1.8,3.1)
        dot(*o,1.5,color)


def tokens(cx,y,n,color,fill,cell=12,gap=4,h=16):
    width=n*cell+(n-1)*gap
    for i in range(n):rect(cx-width/2+i*(cell+gap),y,cell,h,fill,color,.8,r=1)


def snow(cx,cy,r=8):
    for a in (0,pi/3,2*pi/3):
        v=np.array([cos(a),sin(a)]);poly([np.array([cx,cy])-r*v,np.array([cx,cy])+r*v],C['blue'],1.5)
        for sign in (-1,1):
            p=np.array([cx,cy])+sign*r*.65*v
            for da in (-pi/4,pi/4):poly([p,p-sign*r*.35*np.array([cos(a+da),sin(a+da)])],C['blue'],1.2)


def gripper(cx,cy,s=1,color=None):
    color=color or C['purple']
    poly([(cx,cy-14*s),(cx,cy)],color,3*s)
    poly([(cx-13*s,cy+17*s),(cx-19*s,cy+12*s),(cx-19*s,cy),(cx+19*s,cy),(cx+19*s,cy+12*s),(cx+13*s,cy+17*s)],color,2.6*s)


rect(0,0,W,H,C['white'])
group('training-only-geometry')
rect(16,12,990,295,C['orange_fill'],'#C2B39E',1.6,r=10,dash=[8,6])
rect(244,0,534,28,C['white'])
text(511,21,'Training only · skipped at inference',23,C['muted'],True,'middle')
text(250,51,'Sparse 3D flow · GT',25,C['orange'],True,'middle')
text(755,51,'Target SE(3) · GT',25,C['orange'],True,'middle')

group('backprojected-cloud-and-sparse-flow')
crop=(0,300,1024,660);x0,y0,ww,hh=36,64,430,430*360/1024
cloud=A['cloud_world_m'].reshape(-1,3);uv=project(cloud)
inside=(uv[:,0]>=crop[0])&(uv[:,0]<crop[2])&(uv[:,1]>=crop[1])&(uv[:,1]<crop[3])
sc=ww/(crop[2]-crop[0]);out=Image.new('RGB',(1290,454),'#F7F9FA');draw=ImageDraw.Draw(out)
beauty_array=np.asarray(beauty)
for point in uv[inside]:
    ux,uy=np.clip(np.rint(point).astype(int),0,1023);cc=beauty_array[uy,ux]
    cc=np.rint(.94*cc+.06*255).astype(int);xx,yy=(point-crop[:2])*sc*3
    draw.ellipse((xx-2.3,yy-2.3,xx+2.3,yy+2.3),fill=tuple(cc))
out.save(ASSETS/'pointcloud.png');bitmap(out,x0,y0,ww,hh)
source=project(A['source_world_m']);future=project(A['future_world_m'][:,-1]);motion=np.linalg.norm(A['flow_robot_base_m'][:,-1],axis=1)
shown=0
for p,q,d in zip(source,future,motion):
    if not(crop[0]<=p[0]<crop[2] and crop[1]<=p[1]<crop[3]):continue
    a=(p-crop[:2])*sc+[x0,y0];b=(q-crop[:2])*sc+[x0,y0]
    if d>.001:
        poly([a,b],C['white'],3.4);arrow([a,b],C['orange_light'],1.5,4);dot(*a,1.8,C['orange_light']);shown+=1
    else:dot(*a,1.55,'#8C989F')
text(252,239,'14 × 14 samples · 400 ms',19,C['muted'],anchor='middle')
end()

group('eight-measured-future-poses')
to=scene(510,64,472,(365,525,605,602));pose_overlay(to,'future')
text(753,239,'8 horizons · 50–400 ms',19,C['muted'],anchor='middle')
end();end()

group('action-branch')
text(1259,35,'Action chunk',25,C['purple'],True,'middle')
to=scene(1073,51,398,(260,360,900,641));eef=to(A['eef_world_m'][:8])
poly(eef,C['white'],6);poly(eef,C['purple'],3.2)
for p in eef:dot(*p,2.8,C['purple'],C['white'],.8)
arrow(eef[-2:],C['purple'],3.2,8);gripper(*eef[-1],.4)
rect(1084,205,377,25,C['white'])
text(1271,225,'Recorded EEF · GT illustration',19,C['purple'],anchor='middle')
tokens(1243,261,8,C['purple'],C['purple_mid'],cell=16,gap=5,h=15)
arrow([(1243,260),(1243,232)],C['purple'],1.7,6)
text(1147,274,'a',20,C['purple'],anchor='end')
arrow([(1325,268),(1459,268),(1459,293),(1280,293),(1280,302),(1243,302)],C['purple'],1.7,6)
text(1395,287,'Euler ×5',19,C['purple'],anchor='middle')
arrow([(1243,312),(1243,278)],C['purple'],2.4,7)
end()

group('linear-geometry-readouts')
for cx,label in [(250,'Linear (patch)'),(753,'Linear (mean M)')]:
    arrow([(cx,312),(cx,252)],C['orange'],2.1,7,dash=[5,4]);rect(cx-98,274,196,27,C['orange_fill'])
    text(cx,295,label,20,C['orange'],anchor='middle')
end()

group('single-shared-world-action-trunk')
rect(20,314,1280,73,'#F4F7F9','#708695',1.8,r=8)
text(660,345,'World–Action Transformer ×24',29,C['ink'],True,'middle')
text(660,375,'Shared masked attention   ·   World FFN | Action FFN',21,C['muted'],anchor='middle')
end()

group('local-attention-mask')
mx,my,cell=1361,322,24
for i,k in enumerate('SMA'):
    text(mx+i*cell+cell/2,my-7,k,19,anchor='middle');text(mx-9,my+i*cell+19,k,19,anchor='end')
for r in range(3):
    for c in range(3):
        fill=[C['blue_mid'],C['gray_fill'],C['purple_mid']][r] if (r,c) in [(0,0),(1,0),(1,1),(2,1),(2,2)] else C['white']
        rect(mx+c*cell,my+r*cell,cell,cell,fill,C['line'],.8)
text(1394,423,'Q rows · K cols',19,C['muted'],anchor='middle');end()

group('scene-summary-action-inputs')
for cx in [220,540,756,981,1226]:arrow([(cx,401),(cx,388)],C['blue'] if cx<800 else C['gray'] if cx==981 else C['purple'],2,6)
tokens(220,401,9,C['blue'],C['blue_mid'],cell=14,gap=5)
tokens(540,401,8,C['blue'],C['blue_mid']);tokens(756,401,8,C['blue'],C['blue_mid'])
tokens(981,401,16,C['gray'],C['gray_fill'],cell=8,gap=3)
tokens(1226,401,8,C['purple'],C['purple_mid'],cell=14,gap=4)
for cx,label,col in [(220,'196 patch',C['blue']),(540,'8 target',C['blue']),(756,'8 robot',C['blue']),(981,'16 summary M',C['muted']),(1226,'8 action + u',C['purple'])]:text(cx,449,label,21,col,True,'middle')
poly([(27,421),(27,426),(831,426),(831,421)],C['blue'],1.1)
rect(380,416,97,22,C['white']);text(429,433,'S = 212',19,C['blue'],anchor='middle')
bitmap(beauty.crop((0,300,900,900)),25,474,90,60)
text(25,466,'Capture τt',19,C['blue'])
depth=Image.open(ASSETS/'depth.png').resize((1024,1024),Image.Resampling.NEAREST).crop((0,300,900,900));bitmap(depth,215,474,90,60)
rect(43,514,50,21,C['white']);rect(231,514,59,21,C['white'])
text(68,531,'RGB',19,C['blue'],anchor='middle');text(260,531,'Depth',19,C['blue'],anchor='middle')
arrow([(115,490),(124,490),(124,409),(137,409)],C['blue'],1.5,5)
arrow([(305,490),(370,490),(370,409),(304,409)],C['blue'],1.5,5)
text(139,500,'MAE',19,C['blue']);snow(200,493,7)
text(375,532,'XYZ / 3D RoPE',19,C['blue'],anchor='middle')
to=scene(451,461,178,(300,460,785,660));pose_overlay(to,'history')
arrow([(630,495),(646,495),(646,409),(603,409)],C['blue'],1.5,5)
gripper(756,491,.8,C['blue']);text(756,531,'EEF history',19,C['blue'],anchor='middle')
arrow([(777,491),(843,491),(843,409),(819,409)],C['blue'],1.5,5)
text(981,484,'Learnable',21,C['muted'],anchor='middle');text(981,517,'world once / query',19,C['muted'],anchor='middle')
arrow([(1034,478),(1094,478),(1094,409),(1068,409)],C['gray'],1.5,5)
for row in range(7):
    for col in range(7):
        val=150+(row*53+col*29)%96;rect(1147+col*4,463+row*4,4,4,'#'+format(val,'02x')*3)
arrow([(1178,476),(1187,476)],C['purple'],1.7,3)
tokens(1250,466,8,C['purple'],C['purple_mid'],cell=12,gap=4,h=21)
arrow([(1313,476),(1322,476),(1322,409),(1296,409)],C['purple'],1.5,5)
text(1226,521,'Noisy actions',20,C['purple'],anchor='middle');end()

assert not groups
outside=[t for t in texts if t['x']<0 or t['x']+t['width']>W or t['y']<0 or t['y']+t['height']>H+1]
assert not outside,outside
assert min(t['height'] for t in texts)*SCALE >= 6
pdf.showPage();pdf.save()
doc=(f'<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{H/W*6.875}in" viewBox="0 0 {W} {H}">\n'
     '<title>SE(3)-WAM architecture</title>\n<desc>Real Dynamic-14 conveyor episode. Geometry and EEF illustrations are GT, not model predictions. Scene pixels are raster; geometry overlays, mask, tokens, arrows and text are editable vectors.</desc>\n'+'\n'.join(svg)+'\n</svg>\n')
(OUT/'fig2_se3wam.svg').write_text(doc,encoding='utf-8')
(OUT/'layout_text_boxes.json').write_text(json.dumps(texts,indent=2),encoding='utf-8')
# Reusable calibrated panels for Fig.1/Fig.3, with all arrows and axes editable.
ET.register_namespace('', 'http://www.w3.org/2000/svg')
root=ET.fromstring(doc)
for name,gid,box in [('flow_gt','backprojected-cloud-and-sparse-flow',(36,64,430,430*360/1024)),
                     ('target_se3_gt','eight-measured-future-poses',(510,64,472,472*77/240))]:
    x,y,w,h=box
    element=root.find(f'.//{{http://www.w3.org/2000/svg}}g[@id="{gid}"]')
    for label in list(element.findall('{http://www.w3.org/2000/svg}text')):
        element.remove(label)
    panel=ET.Element('{http://www.w3.org/2000/svg}svg',{'viewBox':f'{x} {y} {w} {h}',
                      'width':f'{w*SCALE}pt','height':f'{h*SCALE}pt'})
    panel.append(element)
    ET.ElementTree(panel).write(ASSETS/f'{name}.svg',encoding='utf-8',xml_declaration=True)
print(json.dumps(dict(width_in=6.875,height_in=H/W*6.875,minimum_text_pt=min(t['height'] for t in texts)*SCALE,text_objects=len(texts),moving_flow_arrows_in_crop=shown),indent=2))
