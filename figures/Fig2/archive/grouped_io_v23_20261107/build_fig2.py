"""Publication Fig.2 asset (Fig.3 in the manuscript), grouped inputs/readouts v23.

Standalone vector drawing source. Run in this directory with the provided
assets. Structural components, symbols, noise and geometric references are
native vectors; RGB/Depth inputs and Blender context thumbnails are raster.
"""
from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi
from contextlib import contextmanager
import base64
import json
import copy
import xml.etree.ElementTree as ET

import numpy as np
import pypdfium2 as pdfium
from pypdf import PdfReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader

OUT = Path(__file__).resolve().parent
ASSETS = OUT / 'assets'
W, H = 1600, 950
WIDTH_MM = 174.625
SCALE = WIDTH_MM / 25.4 * 72 / W
BB_X, BB_Y, BB_K = 448.0, 108.0, .8
BB_RIGHT = BB_X + 547*BB_K
PORT_Y = {s:BB_Y+BB_K*(590-x) for s,x in [('S',460),('M',300),('A',140)]}
BB_INPUT = BB_X + 45*BB_K
BODY_FONT_SCALE = .87
MIN_BODY_SIZE = 21.5
INPUT_ROWS = dict(visual=126, target=266, robot=406, action=546)
TOKEN_X, TOKEN_SIZE, TOKEN_GAP, SEGMENT_GAP = 484, 26, 4, 8
BACKBONE_SHIFT = 80
OUTPUT_COLS = [1213, 1353, 1493]
# The glyph counts only fill the illustrative column; they are not parameters.
TOKEN_SEGMENTS = [('visual', 'world', 4), ('target', 'target', 5),
                  ('robot', 'robot', 4), ('summary', 'meta', 1),
                  ('action', 'action', 3)]
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)
for name, filename in [('F2','arial.ttf'), ('F2B','arialbd.ttf'), ('F2I','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+filename))
C = dict(ink='#202020', muted='#626262', line='#777777', faint='#D5D5D5',
         world='#557A9C', world_fill='#E7EFF7', world_mid='#B9D0E4',
         meta='#4D7169', meta_fill='#E7F0EB', meta_mid='#ADC4BA',
         target='#C7685D', target_fill='#FBF0ED', target_mid='#E9BBB7',
         robot='#777777', robot_fill='#F2F2F2', robot_mid='#D6D6D6',
         action='#9C8223', action_fill='#FFF5D6', action_mid='#F4D87B',
         attention='#EEEEEE', white='#FFFFFF', frozen='#626262')


data = np.load(ASSETS/'geometry_labels.npz')
view = np.array([1.15,-1.75,1.30]); view /= np.linalg.norm(view)
right = np.cross([0,0,1],view); right /= np.linalg.norm(right)
up = np.cross(view,right)


def project(p):
    p = np.asarray(p)
    return np.stack([p@right, -p@up], axis=-1)


def fit(points,x,y,w,h,padding=5):
    lo,hi = np.min(points,axis=0), np.max(points,axis=0)
    scale = min((w-2*padding)/(hi[0]-lo[0]),(h-2*padding)/(hi[1]-lo[1]))
    center = (lo+hi)/2
    return lambda p: (np.asarray(p)-center)*scale+[x+w/2,y+h/2]


corners = np.array([[i,j,k] for i in [-.5,.5] for j in [-.5,.5] for k in [-.5,.5]])*np.array([.060,.040,.035])
edges = [(i,j) for i in range(8) for j in range(i+1,8) if np.sum(corners[i]!=corners[j])==1]
pose_vertices = [corners@r.T+p for r,p in zip(data['target_R_world'],data['target_pos_world'])]
pose_bounds = np.concatenate([project(pose_vertices[j]) for j in [0,1,4,7]])
HISTORY_GLYPHS = [1,4,7]
HISTORY_REFERENCE = 0
history_vertices=[corners@rotation.T+position for rotation,position in
                  zip(data['target_history_R_world'],data['target_history_pos_world'])]
history_pairs=[(history_vertices[HISTORY_REFERENCE],history_vertices[index]) for index in HISTORY_GLYPHS]
history_bounds=np.concatenate([project(history_vertices[index]) for index in [HISTORY_REFERENCE]+HISTORY_GLYPHS])
cloud = data['cloud_xyz_world']; cloud2 = project(cloud)
patch = data['patch_xyz_world']; patch2 = project(patch)
flow = data['flow_xyz_world']; valid = data['flow_valid']; keep = data['patch_keep']
flow_scale = 3.0
all_cloud = np.concatenate([cloud2]+[project(patch+flow[:,j]*flow_scale)[keep & valid[:,j]] for j in [0,3,6]])
cloud_colors = ['#'+''.join(f'{int(v):02x}' for v in row) for row in data['cloud_rgb']]
cloud_order = np.argsort(cloud@view)


class Scene:
    def __init__(self,stem):
        self.stem = stem
        self.svg,self.texts,self.arrows,self.boxes,self.groups = [],[],[],[],[]
        self.flow_annotations=[]
        self.pdf = canvas.Canvas(str(OUT/(stem+'.pdf')),pagesize=(W*SCALE,H*SCALE),pageCompression=1,initialFontName='F2')
        self.pdf.setTitle('FoveaWAM: shared states, supervision and cached action generation')
        self.pdf.setAuthor('')
        self.pdf.scale(SCALE,SCALE)

    def group(self,name):
        self.groups.append(name); self.svg.append(f'<g id="{escape(name)}">')

    def end(self):
        self.groups.pop(); self.svg.append('</g>')

    def paint(self,fill=None,stroke=None,sw=1.8,dash=None):
        if fill: self.pdf.setFillColor(HexColor(fill))
        if stroke: self.pdf.setStrokeColor(HexColor(stroke))
        self.pdf.setLineWidth(sw); self.pdf.setDash(dash or [])
        self.pdf.setLineCap(1); self.pdf.setLineJoin(1)
        a=f'fill="{fill or "none"}" stroke="{stroke or "none"}" stroke-width="{sw}"'
        if dash: a+=' stroke-dasharray="'+' '.join(map(str,dash))+'"'
        return a

    def rect(self,x,y,w,h,fill=None,stroke=None,sw=1.8,radius=0,dash=None,name=None):
        attr=self.paint(fill,stroke,sw,dash)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" {attr}/>')
        if radius: self.pdf.roundRect(x,H-y-h,w,h,radius,stroke=bool(stroke),fill=bool(fill))
        else: self.pdf.rect(x,H-y-h,w,h,stroke=bool(stroke),fill=bool(fill))
        if name: self.boxes.append(dict(name=name,x=x,y=y,w=w,h=h))

    def poly(self,points,fill=None,stroke=None,sw=1.8,closed=False,dash=None):
        points=[tuple(map(float,p)) for p in points]
        attr=self.paint(fill,stroke,sw,dash); tag='polygon' if closed else 'polyline'
        xy=' '.join(f'{x:.3f},{y:.3f}' for x,y in points)
        self.svg.append(f'<{tag} points="{xy}" {attr} stroke-linejoin="round" stroke-linecap="round"/>')
        p=self.pdf.beginPath(); p.moveTo(points[0][0],H-points[0][1])
        for x,y in points[1:]: p.lineTo(x,H-y)
        if closed: p.close()
        self.pdf.drawPath(p,stroke=bool(stroke),fill=bool(fill))

    def arrow(self,points,role='ink',sw=2.1,dash=None,head=7,record=True,destination=None):
        color=C.get(role,role); self.poly(points,stroke=color,sw=sw,dash=dash)
        x,y=points[-1]; px,py=points[-2]; a=atan2(y-py,x-px)
        self.poly([(x,y),(x-head*cos(a)+.42*head*sin(a),y-head*sin(a)-.42*head*cos(a)),
                   (x-head*cos(a)-.42*head*sin(a),y-head*sin(a)+.42*head*cos(a))],fill=color,closed=True)
        if record: self.arrows.append(dict(points=points,group='/'.join(self.groups),destination=destination))

    def circle(self,x,y,r,fill=None,stroke=None,sw=1.8):
        a=self.paint(fill,stroke,sw)
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" {a}/>')
        self.pdf.circle(x,H-y,r,stroke=bool(stroke),fill=bool(fill))

    def text(self,x,y,value,size=30,role='ink',bold=False,anchor='start',italic=False,angle=0,preserve_size=False):
        color=C.get(role,role); font='F2B' if bold else 'F2I' if italic else 'F2'
        if not preserve_size:
            previous=size
            size=max(MIN_BODY_SIZE,size*BODY_FONT_SCALE)
            center_shift=(pdfmetrics.getAscent(font)+pdfmetrics.getDescent(font))*(previous-size)/2000
            x+=center_shift*sin(angle*pi/180)
            y-=center_shift*cos(angle*pi/180)
        missing=[ch for ch in value if ord(ch) not in pdfmetrics.getFont(font).face.charToGlyph]
        if missing: raise ValueError((value,missing))
        width=pdfmetrics.stringWidth(value,font,size)
        left=0 if anchor=='start' else -width/2 if anchor=='middle' else -width
        asc=pdfmetrics.getAscent(font)*size/1000; desc=pdfmetrics.getDescent(font)*size/1000
        pts=np.array([[left,-asc],[left+width,-asc],[left+width,-desc],[left,-desc]])
        r=np.array([[cos(angle*pi/180),-sin(angle*pi/180)],[sin(angle*pi/180),cos(angle*pi/180)]])
        pts=pts@r.T+[x,y]; lo=pts.min(0); hi=pts.max(0)
        self.texts.append(dict(text=value,x=float(lo[0]),y=float(lo[1]),width=float(hi[0]-lo[0]),height=float(hi[1]-lo[1]),size=size,angle=angle,group='/'.join(self.groups)))
        transform=f' transform="rotate({angle} {x} {y})"' if angle else ''
        self.svg.append(f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" font-size="{size}" font-weight="{700 if bold else 400}" font-style="{"italic" if italic else "normal"}" text-anchor="{anchor}" fill="{color}"{transform}>{escape(value)}</text>')
        self.pdf.saveState(); self.pdf.setFillColor(HexColor(color)); self.pdf.setFont(font,size)
        self.pdf.translate(x,H-y); self.pdf.rotate(-angle); self.pdf.drawString(left,0,value); self.pdf.restoreState()

    def raster(self,name,x,y,w,h):
        path=ASSETS/name; image=base64.b64encode(path.read_bytes()).decode('ascii')
        self.svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" href="data:image/png;base64,{image}"/>')
        self.pdf.drawImage(ImageReader(str(path)),x,H-y-h,w,h,mask='auto')

    def pose(self,cx,y,w,h,horizon):
        screen=fit(pose_bounds,cx-w/2,y,w,h,10)
        for j,col,dash in [(0,'#CDD7DC',[4,4]),(horizon,C['target'],None)]:
            p=screen(project(pose_vertices[j]))
            for a,b in edges: self.poly([p[a],p[b]],stroke=col,sw=1.2 if j==0 else 1.9,dash=dash)
        origin=data['target_pos_world'][horizon]; rotation=data['target_R_world'][horizon]
        p=screen(project(origin))
        for axis in range(3):
            q=screen(project(origin+.022*rotation[:,axis]))
            self.arrow([p.tolist(),q.tolist()],'target',1.7,head=4.2,record=False)

    def history_pose(self,cx,cy,index):
        """Show cumulative past motion against one fixed historical reference."""
        screen=fit(history_bounds,cx-26,cy-23,52,46,3)
        previous,selected=history_pairs[HISTORY_GLYPHS.index(index)]
        for vertices,color,sw,dash in [(previous,'#CDD7DC',1.0,[2.5,2.5]),(selected,C['target'],1.4,None)]:
            points=screen(project(vertices))
            for a,b in edges: self.poly([points[a],points[b]],stroke=color,sw=sw,dash=dash)
        rotation=data['target_history_R_world'][index]
        origin=data['target_history_pos_world'][index]
        center=screen(project(origin))
        for axis in range(3):
            endpoint=screen(project(origin+.022*rotation[:,axis]))
            self.arrow([center,endpoint],'target',1.2,head=3.1,record=False)

    def robot_icon(self,name,x,y,w,h):
        """Replay the original transparent SVG as native editable drawing objects."""
        root=ET.parse(ASSETS/'robot_arm.svg').getroot()
        k=min(w,h)/100; ox=x+(w-100*k)/2; oy=y+(h-100*k)/2
        self.group(name)
        def draw(element):
            tag=element.tag.rsplit('}',1)[-1]
            if tag in ('title','desc'): return
            assert element.get('transform') is None
            if tag in ('svg','g'):
                for child in element: draw(child)
                return
            fill=element.get('fill','none'); fill=None if fill=='none' else fill
            stroke=element.get('stroke','none'); stroke=None if stroke=='none' else stroke
            sw=float(element.get('stroke-width',1))*k
            if tag in ('polyline','polygon'):
                points=[tuple(map(float,p.split(','))) for p in element.get('points').split()]
                self.poly([(ox+k*px,oy+k*py) for px,py in points],fill,stroke,sw,closed=tag=='polygon')
            elif tag=='circle':
                self.circle(ox+k*float(element.get('cx')),oy+k*float(element.get('cy')),
                            k*float(element.get('r')),fill,stroke,sw)
            elif tag=='rect':
                self.rect(ox+k*float(element.get('x')),oy+k*float(element.get('y')),
                          k*float(element.get('width')),k*float(element.get('height')),
                          fill,stroke,sw,radius=k*float(element.get('rx',0)))
            else: raise ValueError(tag)
        draw(root)
        self.end()

    def flow_panel(self,cx,y,w,h,index):
        context=json.loads((ASSETS/'blender/source.json').read_text(encoding='utf-8'))
        bounds=np.array(context['projection_bounds'])
        screen=fit(bounds,cx-w/2,y,w,h,3*w/165)
        self.raster('blender/flow_context.png',cx-w/2,y,w,h)
        start=screen(patch2); finish=screen(project(patch+flow[:,index]*flow_scale))
        mag=np.linalg.norm(flow[:,index],axis=-1)
        for k in np.flatnonzero(keep & valid[:,index]):
            if mag[k]>.002:
                length=float(np.linalg.norm(finish[k]-start[k]))
                head=min(3.2,.5*length)
                if length<.75:
                    self.poly([start[k],finish[k]],stroke=C['white'],sw=2.6)
                    self.poly([start[k],finish[k]],stroke=C['world'],sw=1.2)
                else:
                    self.arrow([start[k],finish[k]],'white',2.6,head=min(.78*length,head+.7),record=False)
                    self.arrow([start[k],finish[k]],'world',1.2,head=head,record=False)
                self.flow_annotations.append(dict(patch_index=int(k),horizon_index=int(index),
                    start=start[k].tolist(),end=finish[k].tolist(),projected_length=length,
                    head=0. if length<.75 else head))
            else: self.circle(*start[k],.68,'#B3C0C4')


    def plain_link(self,x0,y,x1,destination=None,dash=None):
        self.poly([(x0,y),(x1,y)],stroke=C['line'],sw=1.9,dash=dash)
        self.arrows.append(dict(points=[(x0,y),(x1,y)],group='/'.join(self.groups),
                                destination=destination,head=False))

    def token_column(self):
        top=68
        self.group('representative-tokens')
        for name,role,count in TOKEN_SEGMENTS:
            self.group(name+'-tokens')
            for index in range(count):
                self.rect(TOKEN_X,top+index*(TOKEN_SIZE+TOKEN_GAP),TOKEN_SIZE,TOKEN_SIZE,
                          C[role+'_fill'] if role!='action' else C['action_mid'],
                          C[role],1.5,radius=4.5)
            self.end()
            top+=count*TOKEN_SIZE+(count-1)*TOKEN_GAP+SEGMENT_GAP
        self.end()

    def label_lines(self,x,cy,lines,size=26.5,anchor='start'):
        size=max(MIN_BODY_SIZE,size*BODY_FONT_SCALE)
        asc=pdfmetrics.getAscent('F2B')*size/1000
        desc=pdfmetrics.getDescent('F2B')*size/1000
        step=asc-desc+5
        for index,label in enumerate(lines):
            baseline=cy+(index-(len(lines)-1)/2)*step+(asc+desc)/2
            self.text(x,baseline,label,size,bold=True,anchor=anchor,preserve_size=True)

    def role_token(self,name,x,cy,role,label):
        self.group(name)
        self.rect(x,cy-15,30,30,C[role+'_fill'] if role!='action' else C['action_mid'],
                  C[role],1.4,radius=4)
        self.label_lines(x+15,cy,[label],size=25,anchor='middle')
        self.end()

    def noise_square(self,name,x,y,size):
        self.group(name)
        noise=np.clip(np.random.default_rng(73).normal(150,38,(32,32)),0,255).astype(int)
        pitch=size/32
        for row in range(32):
            for col in range(32):
                value=int(noise[row,col]); gray=f'#{value:02x}{value:02x}{value:02x}'
                self.rect(x+pitch*col,y+pitch*row,pitch,pitch,gray,sw=0)
        self.rect(x,y,size,size,stroke=C['line'],sw=.9)
        self.end()

    def rotated_lines(self,cx,cy,lines,size,bold=False,gap=7):
        """Rotate a multiline label counterclockwise, keeping its ink centered."""
        font='F2B' if bold else 'F2'
        asc=pdfmetrics.getAscent(font)*size/1000
        desc=pdfmetrics.getDescent(font)*size/1000
        step=asc-desc+gap
        for i,label in enumerate(lines):
            column=cx+(i-(len(lines)-1)/2)*step
            self.text(column+(asc+desc)/2,cy,label,size,bold=bold,
                      anchor='middle',angle=-90)


ROOT=OUT
PORT=PORT_Y


class Figure(Scene):
    @contextmanager
    def shifted(self, name, dx=0, dy=0):
        """Place one intact native group; keep PDF/SVG and review coordinates equal."""
        starts = [len(self.texts), len(self.arrows), len(self.boxes), len(self.flow_annotations)]
        self.group(name)
        self.svg[-1] = f'<g id="{escape(name)}" transform="matrix(1 0 0 1 {dx} {dy})">'
        self.pdf.saveState()
        self.pdf.translate(dx, -dy)
        try:
            yield
        finally:
            for item in self.texts[starts[0]:] + self.boxes[starts[2]:]:
                item['x'] += dx
                item['y'] += dy
            for item in self.arrows[starts[1]:]:
                item['points'] = (np.asarray(item['points']) + [dx, dy]).tolist()
            for item in self.flow_annotations[starts[3]:]:
                for key in ['start', 'end']:
                    item[key] = (np.asarray(item[key]) + [dx, dy]).tolist()
            self.pdf.restoreState()
            self.end()

    def panel_title(self, name, x, y, label):
        self.group(name)
        self.t(x, y, label, 27.5, bold=True, anchor='middle')
        self.end()

    def t(self, x, y, value, size=22, role='ink', bold=False, anchor='start', italic=False, angle=0):
        self.text(x, y, value, size, role, bold, anchor, italic, angle, preserve_size=True)

    def centered(self, x, cy, value, size=22, role='ink', bold=False, italic=False):
        font = 'F2B' if bold else 'F2I' if italic else 'F2'
        shift = (pdfmetrics.getAscent(font) + pdfmetrics.getDescent(font)) * size / 2000
        self.t(x, cy + shift, value, size, role, bold, 'middle', italic)

    def vertical(self, cx, cy, lines, size=21.5, role='ink', bold=False, italic=False):
        font = 'F2B' if bold else 'F2I' if italic else 'F2'
        asc, desc = pdfmetrics.getAscent(font), pdfmetrics.getDescent(font)
        step = (asc - desc) * size / 1000 + 3
        for i, value in enumerate(lines):
            xx = cx + (i - (len(lines) - 1) / 2) * step + (asc + desc) * size / 2000
            self.t(xx, cy, value, size, role, bold, 'middle', italic, -90)

    def math_runs(self, name, cx, cy, runs, role='ink', angle=0):
        """Center native text fragments, retaining genuine baseline-shifted scripts."""
        self.group(name)
        widths=[pdfmetrics.stringWidth(text,font,size)+gap for text,font,size,dy,gap in runs]
        y0=min(dy-pdfmetrics.getAscent(font)*size/1000 for text,font,size,dy,gap in runs)
        y1=max(dy-pdfmetrics.getDescent(font)*size/1000 for text,font,size,dy,gap in runs)
        theta=angle*pi/180
        cursor=-sum(widths)/2
        for (text,font,size,dy,gap),width in zip(runs,widths):
            yy=dy-(y0+y1)/2
            x=cx+cos(theta)*cursor-sin(theta)*yy
            y=cy+sin(theta)*cursor+cos(theta)*yy
            self.t(x,y,text,size,role,bold=font=='F2B',italic=font=='F2I',angle=angle)
            self.texts[-1]['subscript']=dy>0
            cursor+=width
        self.end()

    def state_label(self, cx, cy, label, role, output=False):
        runs=[(label,'F2I',23.5,0,.6),('ℓ','F2I',16.2,5.5,0)]
        if output: runs.append(('+1','F2',16.2,5.5,0))
        self.math_runs(('updated-' if output else 'input-')+label,cx,cy,runs,role,-90)

    def role_token(self, name, x, cy, role, label, subscript=None):
        self.group(name)
        self.rect(x,cy-15,30,30,C[role+'_fill'] if role!='action' else C['action_mid'],
                  C[role],1.4,radius=4)
        if subscript:
            self.math_runs(name+'-symbol',x+15,cy,
                           [(label,'F2B',21.75,0,.3),(subscript,'F2I',16.2,5,0)])
        else:
            self.centered(x+15,cy,label,21.75,bold=True)
        self.end()

    def plus(self, x, y, role):
        self.circle(x, y, 8, C['white'], C[role], 1.3)
        self.poly([(x-4.5, y), (x+4.5, y)], stroke=C[role], sw=1.2)
        self.poly([(x, y-4.5), (x, y+4.5)], stroke=C[role], sw=1.2)

    def short_link(self, x0, x1, y, role):
        self.poly([(x0, y), (x1, y)], stroke=C[role], sw=1.45)

    def numeric_encoder(self, name, cy, label, role):
        self.group(name)
        self.poly([(388,cy-50),(464,cy-42),(464,cy+42),(388,cy+50)],
                  C[role+'_fill'],C[role],1.4,closed=True)
        self.vertical(426,cy,[label,'Encoder'],21.5)
        self.end()

    def numeric_decoder(self, name, cy, label, role, train):
        self.group(name)
        self.arrow([(1042,cy),(1070,cy)],'ink',1.8,
                   dash=[5,4] if train else None,head=5.5,destination=name)
        self.poly([(1074,cy-38),(1140,cy-54),(1140,cy+54),(1074,cy+38)],
                  C[role+'_fill'],C[role],1.4,closed=True)
        self.vertical(1107,cy,[label,'Decoder'],21.5)
        self.end()

    def source_boundary(self, name, cy):
        """One observation and its mapping share a joined, unfilled silhouette."""
        self.group(name+'-boundary')
        self.rect(34,cy-50,354,100,None,'#C6CDD2',.95)
        self.end()

    def readout_boundary(self, name, cy, title):
        """The three examples belong to one readout, joined to its decoder."""
        self.group(name+'-boundary')
        self.rect(1140,cy-54,426,108,None,'#C6CDD2',.95)
        self.t(1353,cy-32,title,22.5,bold=True,anchor='middle')
        self.end()

    def inputs(self):
        self.group('observed-inputs')
        self.group('rgbd-to-vision-tokens')
        self.source_boundary('rgbd-source',INPUT_ROWS['visual'])
        self.label_lines(50, INPUT_ROWS['visual'], ['Current', 'RGB-D'])
        for xx, name in [(182, 'rgb.png'), (262, 'depth.png')]:
            self.raster(name, xx, INPUT_ROWS['visual']-36, 72, 72)
            self.rect(xx, INPUT_ROWS['visual']-36, 72, 72, stroke='#B5B5B5', sw=.9)
        self.numeric_encoder('vision-encoder',INPUT_ROWS['visual'],'Vision','robot')
        self.end()
        self.group('target-history')
        self.source_boundary('target-source',INPUT_ROWS['target'])
        self.label_lines(50, INPUT_ROWS['target'], ['Target', 'history'])
        for number, (xx, index) in enumerate(zip([181,247,313], HISTORY_GLYPHS)):
            self.group('historical-pose-' + str(number))
            self.history_pose(xx, INPUT_ROWS['target'], index)
            self.end()
        self.numeric_encoder('target-history-encoder',INPUT_ROWS['target'],'SE(3)','target')
        self.end()
        self.group('robot-state-to-scene-tokens')
        self.source_boundary('robot-source',INPUT_ROWS['robot'])
        self.label_lines(50, INPUT_ROWS['robot'], ['Robot', 'state'])
        self.robot_icon('robot-state', 203, INPUT_ROWS['robot']-42, 88, 84)
        self.numeric_encoder('robot-state-encoder',INPUT_ROWS['robot'],'State','robot')
        self.end()
        self.label_lines(474, 483, ['Summary M'], size=25, anchor='end')
        self.group('noise-to-action-tokens')
        self.source_boundary('noise-source',INPUT_ROWS['action'])
        self.label_lines(50, INPUT_ROWS['action'], ['Noisy', 'actions A'])
        self.noise_square('action-noise', 209, INPUT_ROWS['action']-38, 76)
        self.numeric_encoder('action-input-encoder',INPUT_ROWS['action'],'Action','action')
        self.end()
        self.end()
        self.token_column()

    def backbone(self):
        self.group('coupled-world-action-backbone')
        # WorldBridge/SelfWAM grammar: coherent stream bodies crossed by shared bands.
        self.group('stream-bodies')
        self.rect(452, 104, 530, 298, '#F3F7FA', '#ADC0CF', 1.05, radius=8)
        self.rect(452, 420, 530, 144, '#FFFAEA', '#C9B879', 1.05, radius=8)
        self.vertical(463, 253, ['World stream'], 21.5, 'world')
        self.vertical(463, 492, ['Action stream'], 21.5, 'action')
        self.end()

        # A single bracket spans the complete coupled layer, without a numeric depth.
        self.group('layer-repetition')
        self.poly([(478, 65), (478, 58), (958, 58), (958, 65)], stroke=C['line'], sw=1.4)
        self.math_runs('layer-count',718,43,[('×','F2',23,0,5),('L','F2I',23,0,0)])
        self.end()

        # Two whole-state identity paths, one per sublayer. Keep their ports separate.
        self.group('attention-residual')
        self.arrow([(492, 118), (492, 94), (761, 94), (761, 118)],'line',1.35,
                   head=4.0,destination='first-residual-bank')
        self.end()
        self.group('ffn-residual')
        self.arrow([(773, 118), (773, 78), (903, 78), (903, 118)],'line',1.35,
                   head=4.0,destination='second-residual-bank')
        self.end()

        self.group('layer-input-states')
        self.rect(476, 118, 32, 426, C['white'], '#B7C0C6', 1.0, radius=3)
        for label, role in [('S', 'world'), ('M', 'meta'), ('A', 'action')]:
            self.state_label(492, PORT[label], label, role)
        self.end()

        self.group('attention-normalization')
        self.rect(516, 118, 29, 266, C['white'], '#ABB9C5', 1.0, radius=3)
        self.vertical(530.5, 251, ['LN'], 21.5)
        self.rect(516, 426, 29, 118, C['white'], '#BAA35C', 1.0, radius=3)
        self.vertical(530.5, 485, ['AdaLN'], 21.5)
        self.end()

        self.group('shared-qkv')
        self.rect(557, 118, 70, 426, C['white'], '#A2ADB5', 1.1, radius=3)
        self.vertical(610,331,['Q / K / V'],21.5)
        self.group('representative-qkv-tokens')
        for yy,role in [(169,'world'),(199,'target'),(229,'robot'),(327,'meta'),
                        (440,'action'),(470,'action')]:
            self.rect(563,yy,TOKEN_SIZE,TOKEN_SIZE,
                      C[role+'_fill'] if role!='action' else C['action_mid'],
                      C[role],1.4,radius=4.5)
        self.end()
        self.end()
        self.group('shared-masked-attention')
        self.rect(639, 118, 56, 426, '#E8ECF0', '#7E8A94', 1.4, radius=3)
        self.vertical(667, 331, ['Shared attention'], 23.5, bold=True)
        self.end()
        self.group('shared-output-projection')
        self.rect(707, 118, 39, 426, C['white'], '#A2ADB5', 1.0, radius=3)
        self.vertical(726.5, 331, ['Output proj.'], 21.5)
        self.end()

        self.group('first-residual-sum')
        self.rect(756, 118, 22, 426, C['white'], '#C3C7CA', 1.0, radius=3)
        for label, role in [('S', 'world'), ('M', 'meta'), ('A', 'action')]:
            self.plus(767, PORT[label], role)
        self.end()

        self.group('ffn-normalization')
        self.rect(788, 118, 29, 266, C['white'], '#ABB9C5', 1.0, radius=3)
        self.vertical(802.5, 251, ['LN'], 21.5)
        self.rect(788, 426, 29, 118, C['white'], '#BAA35C', 1.0, radius=3)
        self.vertical(802.5, 485, ['AdaLN'], 21.5)
        self.end()
        self.group('world-ffn-shared-by-s-m')
        self.rect(829, 118, 51, 266, C['world_fill'], C['world'], 1.4, radius=3)
        self.vertical(854.5, 251, ['World FFN'], 23, bold=True)
        self.end()
        self.group('private-action-ffn')
        self.rect(829, 426, 51, 118, C['action_fill'], C['action'], 1.4, radius=3)
        self.vertical(854.5, 485, ['Action', 'FFN'], 22, bold=True)
        self.end()
        self.group('second-residual-sum')
        self.rect(892, 118, 22, 426, C['white'], '#C3C7CA', 1.0, radius=3)
        for label, role in [('S', 'world'), ('M', 'meta'), ('A', 'action')]:
            self.plus(903, PORT[label], role)
        self.end()
        self.group('layer-output-states')
        self.rect(926, 118, 32, 426, C['white'], '#B7C0C6', 1.0, radius=3)
        for label, role in [('S', 'world'), ('M', 'meta'), ('A', 'action')]:
            self.state_label(942, PORT[label], label, role, output=True)
        self.end()

        self.group('local-state-links')
        for label, role in [('S', 'world'), ('M', 'meta'), ('A', 'action')]:
            for start, stop in [(508,516),(545,557),(627,639),(695,707),
                                (746,756),(778,788),(817,829),(880,892),(914,926)]:
                self.short_link(start, stop, PORT[label], role)
        self.end()

        self.group('flow-time-conditioning')
        self.poly([(530.5,580),(802.5,580)], stroke=C['action'], sw=1.4)
        for x in [530.5,802.5]:
            self.arrow([(x,580),(x,547)], 'action', 1.4, head=4.7,
                       destination='Action-AdaLN-only')
        self.rect(606,568,121,24,C['white'],sw=0)
        self.math_runs('flow-time-label',666.5,580,[('Flow time ','F2',21.5,0,0),('u','F2I',21.5,0,0)])
        self.end()
        self.end()

    def outputs(self):
        cols=OUTPUT_COLS
        self.group('training-supervision-readouts')
        for label,title,indices in [('S','Sparse 3D flow',[0,3,6]),('M','Target SE(3)',[1,4,7])]:
            self.group(label+'-readout-unit')
            self.readout_boundary(label+'-forecast',PORT[label],title)
            self.numeric_decoder('flow-decoder' if label=='S' else 'se3-decoder',PORT[label],
                                 'Flow' if label=='S' else 'SE(3)',
                                 'world' if label=='S' else 'meta',True)
            for j,(xx,index) in enumerate(zip(cols,indices)):
                self.group(label+'-supervision-example-'+str(j))
                if label=='S': self.flow_panel(xx,PORT[label]-21,126,67.2,index)
                else: self.pose(xx,PORT[label]-22,106,72,index)
                self.end()
            self.end()
        self.end()
        self.group('action-chunk-readout')
        self.readout_boundary('action-chunk',PORT['A'],'Action chunk')
        self.numeric_decoder('action-decoder',PORT['A'],'Action','action',False)
        for number,xx in enumerate(cols):
            self.robot_icon('action-chunk-'+str(number),xx-29,PORT['A']-12.5,58,57)
        for xx in [1283,1423]: self.text(xx,PORT['A']+22,'…',27,'muted',anchor='middle')
        self.end()

    def mask(self):
        self.group('b-attention-mask')
        mx,my,cell=112,746,48
        self.centered(182,687,'K',22,bold=True)
        self.arrow([(203,687),(250,687)],'ink',1.4,head=5,record=False)
        self.centered(48,801,'Q',22,bold=True)
        self.arrow([(48,820),(48,852)],'ink',1.4,head=5,record=False)
        for i,(label,role) in enumerate([('S','world'),('M','meta'),('A','action')]):
            self.t(mx+(i+.5)*cell,my-14,label,24,role,bold=True,anchor='middle')
            self.centered(mx-21,my+(i+.5)*cell,label,24,role,bold=True)
        for rr in range(3):
            for cc in range(3):
                fill=C[['world_fill','meta_fill','action_mid'][rr]]
                self.rect(mx+cc*cell,my+rr*cell,cell,cell,fill if cc<=rr else C['white'],'#969696',1.05)
                if cc>rr:
                    x,y=mx+cc*cell,my+rr*cell
                    for offset in range(-36,48,12):
                        u0=max(3,offset+3); u1=min(cell-3,offset+cell-3)
                        if u1>u0:
                            self.poly([(x+u0,y+cell-(u0-offset)),(x+u1,y+cell-(u1-offset))],stroke='#D4DADD',sw=.9)
        self.end()

    def cache_glyph(self,x,y):
        for dy,role in [(0,'world'),(20,'meta')]:
            for offset in [5,2.5,0]:
                self.rect(x+offset,y+dy-offset/2,30,12,C[role+'_fill'],C[role],.8,radius=1)

    def execution(self):
        self.group('c-training-and-cached-inference')
        # Faster-WAM execution-view grammar; both views describe this same model.
        self.group('training-view')
        self.rect(356,710,548,220,None,'#B0B3B6',1.2,radius=8,dash=[6,5])
        self.t(376,695,'Training',23,bold=True)
        self.rect(387,769,187,88,C['world_fill'],C['world'],1.4,radius=6)
        self.centered(480.5,813,'World',22.5,bold=True)
        self.rect(632,769,187,88,C['action_fill'],C['action'],1.4,radius=6)
        self.centered(725.5,813,'Action',22.5,bold=True)
        self.arrow([(578,813),(628,813)],'world',1.8,head=5.5,destination='differentiable-layer-wise-conditioning')
        self.centered(480.5,736,'World loss',21.5)
        self.centered(725.5,736,'Flow matching',21.5)
        self.arrow([(480.5,765),(480.5,750)],'ink',1.6,dash=[4,3],head=4.8,destination='world-readouts-supervision')
        self.arrow([(725.5,765),(725.5,750)],'ink',1.6,head=4.8,destination='action-velocity-supervision')
        self.role_token('train-input-S',444,899,'world','S')
        self.role_token('train-input-M',487,899,'meta','M')
        self.arrow([(480.5,881),(480.5,860)],'ink',1.6,head=4.8,destination='training-world-input')
        self.role_token('train-input-Au',675,899,'action','A',subscript='u')
        self.centered(761,899,'u',23,italic=True)
        self.arrow([(690,881),(690,860)],'ink',1.6,head=4.8,destination='training-noisy-action')
        self.arrow([(761,881),(761,860)],'action',1.6,head=4.8,destination='training-flow-time')
        self.end()

        self.group('cached-inference-view')
        self.rect(944,710,622,220,None,'#B0B3B6',1.2,radius=8,dash=[6,5])
        self.t(964,695,'Inference',23,bold=True)
        self.rect(974,769,228,88,C['world_fill'],C['world'],1.4,radius=6)
        self.centered(1088,792,'World prefill',22,bold=True)
        self.cache_glyph(990,815)
        self.centered(1112,832,'Layer-wise K/V',21.5)
        self.rect(1250,769,190,88,C['action_fill'],C['action'],1.4,radius=6)
        self.centered(1345,792,'Action update',22,bold=True)
        # The iteration symbol is local to Action, with no return to World/cache.
        loop=[(1345+14*cos(a),829+14*sin(a)) for a in np.linspace(-.48*pi,1.18*pi,25)]
        self.arrow(loop,'action',1.8,head=5.5,destination='action-only-iteration')
        self.arrow([(1206,813),(1246,813)],'world',1.8,head=5.5,destination='fixed-layer-wise-world-kv')
        self.arrow([(1444,813),(1476,813)],'ink',1.8,head=5.5,destination='deployed-action-chunk')
        self.label_lines(1509,747,['Action','chunk'],size=25,anchor='middle')
        self.robot_icon('inference-action-chunk',1480,784.5,58,57)
        self.role_token('infer-input-S',1051.5,899,'world','S')
        self.role_token('infer-input-M',1094.5,899,'meta','M')
        self.arrow([(1088,881),(1088,860)],'ink',1.6,head=4.8,destination='single-world-prefill-input')
        self.noise_square('inference-noise',1274,877,44)
        self.arrow([(1296,874),(1296,860)],'ink',1.6,head=4.8,destination='initial-action-noise')
        self.centered(1394,899,'u',23,italic=True)
        self.arrow([(1394,881),(1394,860)],'action',1.6,head=4.8,destination='inference-flow-time')
        self.end()
        self.end()

    def draw(self):
        self.rect(0,0,W,H,C['white'])
        self.group('a-method')
        with self.shifted('balanced-overview', dy=-12):
            self.inputs()
            with self.shifted('backbone-placement', dx=BACKBONE_SHIFT):
                self.backbone()
            self.outputs()
        self.panel_title('a-panel-title',800,615,'(a) FoveaWAM')
        self.end()
        with self.shifted('mask-placement',dy=-10):
            self.mask()
        with self.shifted('execution-placement',dy=-25):
            self.execution()
        self.panel_title('b-panel-title',172,934,'(b) Attention mask')
        self.panel_title('c-panel-title',961,934,'(c) Training and inference')

    def export(self):
        assert not self.groups
        outside=[t for t in self.texts if t['x']<0 or t['y']<0 or t['x']+t['width']>W or t['y']+t['height']>H]
        if outside: raise ValueError(outside)
        self.pdf.setTitle('FoveaWAM architecture: World/Action coupled Transformer')
        self.pdf.showPage(); self.pdf.save()
        desc=('Grouped inputs/readouts v23, preserving the adopted v21 topology. Reference layout: WorldBridge Fig.3 and SelfWAM Fig.2; '
              'whole-layer repetition follows LAW Fig.5; execution views follow the bottom-right of Faster-WAM Fig.2. '
              'Scene S and Summary M retain distinct states but share World normalization and FFN weights. '
              'Action A has its own flow-time-conditioned AdaLN and FFN. QKV and output projection weights are shared across S/M/A. '
              'Shared attention obeys S-to-S, M-to-S/M, A-to-S/M/A masks. Two residual additions and layer input/output states are shown. '
              'The bracket repeats the complete coupled layer; multiplicities are schematic. Flow time u conditions Action AdaLN before attention and before FFN, not World. '
              'Training uses differentiable World conditioning and supervises World readouts and Action velocity. '
              'Inference computes World once per query, stores S/M attention-input K/V per layer, and iterates only Action. '
              'Geometric examples are recorded supervision references; decoded geometry is not an Action input. '
              'RGB and flow context are Blender renderings of the recorded frame-29 state; depth remains recorded. Flow annotations, diagram structure and text remain editable vectors. The context meshes are editable in the accompanying Blender scene.')
        svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_MM}mm" height="{WIDTH_MM*H/W:.6f}mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">\n'
             '<title id="title">FoveaWAM architecture</title>\n'
             f'<desc id="desc">{escape(desc)}</desc>\n'+'\n'.join(self.svg)+'\n</svg>\n')
        (ROOT/(self.stem+'.svg')).write_text(svg,encoding='utf-8')
        (ROOT/'layout_metadata.json').write_text(json.dumps(dict(texts=self.texts,arrows=self.arrows,boxes=self.boxes,
             flow_annotations=self.flow_annotations),ensure_ascii=False,indent=2),encoding='utf-8')
        doc=pdfium.PdfDocument(str(ROOT/(self.stem+'.pdf')))
        page=doc[0]
        for filename,dpi in [(self.stem+'.png',300),(self.stem+'_600dpi.png',600),('fig2_paper_width.png',144)]:
            bitmap=page.render(scale=dpi/72)
            bitmap.to_pil().save(ROOT/filename,dpi=(dpi,dpi))
            bitmap.close()
        page.close();doc.close()
        tree=ET.fromstring(svg)
        vector_count=sum(e.tag.rsplit('}',1)[-1] in ('rect','circle','polyline','polygon') for e in tree.iter())
        report=dict(release='v23',width_mm=WIDTH_MM,height_mm=WIDTH_MM*H/W,
                    native_text_objects=len(self.texts),native_vector_objects=vector_count,
                    raster_image_placements=5,backbone_rotation_degrees=-90,
                    backbone_side_padding=[24,24],output_column_centers=OUTPUT_COLS,
                    input_area_extra_width=BACKBONE_SHIFT,panel_titles='centered-below',
                    input_source_encoder_groups=4,decoder_example_groups=3,
                    token_to_backbone_arrows=0,
                    input_encoders=['Vision','SE(3)','State','Action'],
                    output_decoders=['Flow','SE(3)','Action'],summary_encoder=False,
                    minimum_body_font_pt=min(t['size'] for t in self.texts if not t.get('subscript'))*SCALE,
                    minimum_subscript_font_pt=min(t['size'] for t in self.texts if t.get('subscript'))*SCALE,
                    state_order=['S','M','A'],shared_weights=['QKV','attention-output','S/M World FFN'],
                    action_private=['attention AdaLN(u)','FFN AdaLN(u)','Action FFN'],
                    residual_stages=2,attention_mask=[[1,0,0],[1,1,0],[1,1,1]],
                    display_flow_counts={str(i):sum(a['horizon_index']==i for a in self.flow_annotations) for i in [0,3,6]},
                    adaptive_flow_head_limit=3.2,
                    references=['WorldBridge Fig.3','SelfWAM Fig.2','LAW Fig.5','Faster-WAM Fig.2(b)'],
                    manuscript_modified=False)
        (ROOT/'export_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report))


if __name__ == '__main__':
    candidate=Figure('fig2_se3wam')
    candidate.draw()
    candidate.export()
