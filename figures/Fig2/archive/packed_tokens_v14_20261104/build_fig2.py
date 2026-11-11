"""Fig.3 v14: quieter labels and four evenly spaced input rows.

A packed column of larger token glyphs replaces all external ingress wiring.
Token multiplicity is schematic; the accepted backbone geometry is retained.
"""
from pathlib import Path
from html import escape
from math import atan2, cos, sin, pi
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
TOKEN_X, TOKEN_SIZE, TOKEN_GAP, SEGMENT_GAP = 404, 26, 4, 8
# The glyph counts only fill the illustrative column; they are not parameters.
TOKEN_SEGMENTS = [('visual', 'world', 4), ('target', 'target', 5),
                  ('robot', 'robot', 4), ('summary', 'world', 1),
                  ('action', 'action', 3)]
SVG_NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG_NS)
for name, filename in [('F2','arial.ttf'), ('F2B','arialbd.ttf'), ('F2I','ariali.ttf')]:
    pdfmetrics.registerFont(TTFont(name, 'C:/Windows/Fonts/'+filename))
C = dict(ink='#202020', muted='#626262', line='#777777', faint='#D5D5D5',
         world='#557A9C', world_fill='#E7EFF7', world_mid='#B9D0E4',
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
        screen=fit(history_bounds,cx-39,cy-30,78,60,4)
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
        screen=fit(all_cloud,cx-w/2,y,w,h,3)
        for k in cloud_order:
            xx,yy=screen(cloud2[k]); self.circle(xx,yy,.91,cloud_colors[k])
        start=screen(patch2); finish=screen(project(patch+flow[:,index]*flow_scale))
        mag=np.linalg.norm(flow[:,index],axis=-1)
        for k in np.flatnonzero(keep & valid[:,index]):
            if mag[k]>.002:
                self.arrow([start[k],finish[k]],'white',3.8,head=5.2,record=False)
                self.arrow([start[k],finish[k]],'world',1.8,head=4.4,record=False)
            else: self.circle(*start[k],1.05,'#99A8A5')


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

    def readout(self,y,train=False,destination='action-output'):
        self.arrow([(BB_RIGHT,y),(962,y)],'ink',2,dash=[5,4] if train else None,
                   head=6.5,destination=destination)

    def import_backbone(self):
        """Replay the original SVG as editable SVG objects and native PDF paths."""
        root=ET.parse(ASSETS/'backbone_v2.svg').getroot()

        def reorder(e,group=''):
            """Reverse stream positions while retaining glyphs and math-label order."""
            tag=e.tag.rsplit('}',1)[-1]
            group=e.get('id',group)
            if tag=='g':
                for child in e: reorder(child,group)
            elif tag=='rect':
                e.set('x',str(600-float(e.get('x'))-float(e.get('width'))))
            elif tag=='circle':
                e.set('cx',str(600-float(e.get('cx'))))
            elif tag in ('polyline','polygon'):
                pts=[tuple(map(float,p.split(','))) for p in e.get('points').split()]
                e.set('points',' '.join(f'{600-x:.6f},{y:.6f}' for x,y in pts))
            elif tag=='text':
                x=float(e.get('x'))
                if group in ('bb-input-states','bb-updated-states'):
                    center=min((140,300,460),key=lambda c:abs(x-c))
                    e.set('x',str(x+2*(300-center)))
                else:
                    assert e.get('text-anchor')=='middle',e.attrib
                    e.set('x',str(600-x))
            else:
                raise ValueError(tag)

        children=[]
        for original in root:
            tag=original.tag.rsplit('}',1)[-1]
            if tag in ('title','desc') or original.get('id')=='next-layer': continue
            if tag=='rect' and original.get('width')=='600' and original.get('height')=='655': continue
            element=copy.deepcopy(original)
            for parent in element.iter():
                for child in list(parent):
                    if child.tag.rsplit('}',1)[-1]=='text' and ''.join(child.itertext())=='Transformer layer ℓ':
                        parent.remove(child)
                if 'id' in parent.attrib: parent.set('id','bb-'+parent.attrib['id'])
            reorder(element)
            def shrink_cluster(texts):
                if not texts: return
                boxes=[]
                for text in texts:
                    size=float(text.get('font-size'))
                    font='F2B' if text.get('font-weight')=='700' else 'F2I' if text.get('font-style')=='italic' else 'F2'
                    width=pdfmetrics.stringWidth(''.join(text.itertext()),font,size)
                    x,y=float(text.get('x')),float(text.get('y'))
                    left=0 if text.get('text-anchor')=='start' else -width/2 if text.get('text-anchor')=='middle' else -width
                    boxes.append((x+left,y-pdfmetrics.getAscent(font)*size/1000,
                                  x+left+width,y-pdfmetrics.getDescent(font)*size/1000))
                cx=(min(b[0] for b in boxes)+max(b[2] for b in boxes))/2
                cy=(min(b[1] for b in boxes)+max(b[3] for b in boxes))/2
                for text in texts:
                    text.set('x',str(cx+(float(text.get('x'))-cx)*BODY_FONT_SCALE))
                    text.set('y',str(cy+(float(text.get('y'))-cy)*BODY_FONT_SCALE))
                    text.set('font-size',str(float(text.get('font-size'))*BODY_FONT_SCALE))
            texts=[child for child in element if child.tag.rsplit('}',1)[-1]=='text']
            if element.get('id') in ('bb-input-states','bb-updated-states'):
                for center in (140,300,460):
                    shrink_cluster([text for text in texts if min((140,300,460),key=lambda c:abs(float(text.get('x'))-c))==center])
            else:
                shrink_cluster(texts)
            children.append(element)
        transform=f'matrix(0 {-BB_K} {BB_K} 0 {BB_X-30*BB_K} {BB_Y+590*BB_K})'
        self.svg.append('<defs><clipPath id="backbone-core-clip" clipPathUnits="userSpaceOnUse"><rect x="10" y="30" width="580" height="547"/></clipPath></defs>')
        self.svg.append(f'<g id="rotated-backbone-core" transform="{transform}"><g clip-path="url(#backbone-core-clip)">')
        self.svg.extend(ET.tostring(e,encoding='unicode') for e in children)
        self.svg.append('</g></g>')

        def paint(e):
            fill=e.get('fill','none'); stroke=e.get('stroke','none')
            if fill!='none': self.pdf.setFillColor(HexColor(fill))
            if stroke!='none': self.pdf.setStrokeColor(HexColor(stroke))
            self.pdf.setLineWidth(float(e.get('stroke-width',1)))
            self.pdf.setLineCap(1); self.pdf.setLineJoin(1)
            self.pdf.setDash([float(v) for v in e.get('stroke-dasharray','').split()])
            return fill!='none',stroke!='none'

        def replay(e):
            tag=e.tag.rsplit('}',1)[-1]
            assert not e.get('transform'),(tag,e.attrib)
            if tag=='g':
                for child in e: replay(child)
                return
            fill,stroke=paint(e)
            if tag=='rect':
                args=[float(e.get(k,0)) for k in ('x','y','width','height')]
                radius=float(e.get('rx',0))
                if radius: self.pdf.roundRect(*args,radius,stroke=stroke,fill=fill)
                else: self.pdf.rect(*args,stroke=stroke,fill=fill)
            elif tag=='circle':
                self.pdf.circle(float(e.get('cx')),float(e.get('cy')),float(e.get('r')),stroke=stroke,fill=fill)
            elif tag in ('polyline','polygon'):
                pts=[tuple(map(float,p.split(','))) for p in e.get('points').split()]
                path=self.pdf.beginPath(); path.moveTo(*pts[0])
                for p in pts[1:]: path.lineTo(*p)
                if tag=='polygon': path.close()
                self.pdf.drawPath(path,stroke=stroke,fill=fill)
            elif tag=='text':
                value=''.join(e.itertext()); size=float(e.get('font-size'))
                font='F2B' if e.get('font-weight')=='700' else 'F2I' if e.get('font-style')=='italic' else 'F2'
                width=pdfmetrics.stringWidth(value,font,size)
                dx=0 if e.get('text-anchor')=='start' else -width/2 if e.get('text-anchor')=='middle' else -width
                self.pdf.saveState(); self.pdf.translate(float(e.get('x')),float(e.get('y')))
                self.pdf.scale(1,-1); self.pdf.setFont(font,size); self.pdf.drawString(dx,0,value); self.pdf.restoreState()
            else: raise ValueError(tag)

        self.pdf.saveState()
        self.pdf.transform(0,BB_K,BB_K,0,BB_X-30*BB_K,H-BB_Y-590*BB_K)
        clip=self.pdf.beginPath(); clip.rect(10,30,580,547); self.pdf.clipPath(clip,stroke=0,fill=0)
        for e in children: replay(e)
        self.pdf.restoreState()

        def point(x,y): return (BB_X+BB_K*(y-30),BB_Y+BB_K*(590-x))
        source=json.loads((ASSETS/'backbone_v2_layout.json').read_text(encoding='utf-8'))
        for parent in children:
            for text in parent.iter():
                if text.tag.rsplit('}',1)[-1]!='text': continue
                value=''.join(text.itertext()); size=float(text.get('font-size'))
                font='F2B' if text.get('font-weight')=='700' else 'F2I' if text.get('font-style')=='italic' else 'F2'
                width=pdfmetrics.stringWidth(value,font,size)
                x,y=float(text.get('x')),float(text.get('y'))
                left=0 if text.get('text-anchor')=='start' else -width/2 if text.get('text-anchor')=='middle' else -width
                asc,desc=pdfmetrics.getAscent(font)*size/1000,pdfmetrics.getDescent(font)*size/1000
                corners=[point(px,py) for px,py in [(x+left,y-asc),(x+left+width,y-asc),(x+left+width,y-desc),(x+left,y-desc)]]
                x0=min(p[0] for p in corners); x1=max(p[0] for p in corners)
                y0=min(p[1] for p in corners); y1=max(p[1] for p in corners)
                self.texts.append(dict(text=value,x=x0,y=y0,width=x1-x0,height=y1-y0,
                                       size=size*BB_K,angle=-90,group='a-method/shared-backbone/'+parent.get('id','')))
        for edge in source['edges']:
            pts=[]
            for x,y in edge['points']:
                pts.append(point(600-max(10,min(590,x)),max(30,min(577,y))))
            if len(set(pts))>1:
                self.arrows.append(dict(points=pts,group='a-method/shared-backbone/'+edge['group'],
                                        destination=edge['name'],head=edge['head']))

    def draw(self):
        self.rect(0,0,W,H,C['white'])
        self.group('a-method')
        self.text(34,54,'(a) FoveaWAM',31.5,bold=True,preserve_size=True)

        self.group('observed-inputs')
        self.label_lines(36,INPUT_ROWS['action'],['Noisy actions A'])
        self.group('gaussian-noise-glyph')
        noise=np.clip(np.random.default_rng(73).normal(128,48,(32,32)),0,255).astype(int)
        for row in range(32):
            for col in range(32):
                v=int(noise[row,col]); gray=f'#{v:02x}{v:02x}{v:02x}'
                self.rect(230+2*col,INPUT_ROWS['action']-32+2*row,2,2,gray,sw=0)
        self.rect(230,INPUT_ROWS['action']-32,64,64,stroke='#777777',sw=1)
        self.end()
        self.label_lines(382,483,['Summary M'],anchor='end')
        self.label_lines(36,INPUT_ROWS['visual'],['Current','RGB-D'])
        for xx,name in [(142,'rgb.png'),(214,'depth.png')]:
            self.raster(name,xx,INPUT_ROWS['visual']-32,64,64)
            self.rect(xx,INPUT_ROWS['visual']-32,64,64,stroke='#B5B5B5',sw=.9)
        self.group('vision-encoder')
        cy=INPUT_ROWS['visual']
        self.poly([(306,cy-56),(382,cy-44),(382,cy+44),(306,cy+56)],
                  '#F1F3F5','#777777',1.7,closed=True)
        self.rotated_lines(344,cy,['Vision','Encoder'],23.5)
        self.end()
        self.group('target-pose-history')
        self.label_lines(36,INPUT_ROWS['target'],['Target','history'])
        for number,(xx,index) in enumerate(zip([179,262,345],HISTORY_GLYPHS)):
            self.group('historical-pose-'+str(number))
            self.history_pose(xx,INPUT_ROWS['target'],index)
            self.end()
        self.end()
        self.group('robot-state-input')
        self.label_lines(36,INPUT_ROWS['robot'],['Robot state'])
        self.robot_icon('robot-state-glyph',229,INPUT_ROWS['robot']-31.5,66,63)
        self.end()
        self.end()

        self.token_column()

        self.group('shared-backbone')
        self.group('repeated-transformer-blocks')
        self.rect(BB_X+12,BB_Y-12,547*BB_K,580*BB_K,'#FAFAFA','#B8B8B8',1.3,radius=8)
        self.rect(BB_X+6,BB_Y-6,547*BB_K,580*BB_K,'#FAFAFA','#A0A0A0',1.3,radius=8)
        self.end()
        self.import_backbone()
        self.end()

        columns=[1060,1260,1460]
        self.group('action-chunk')
        self.readout(PORT_Y['A'])
        self.text(978,PORT_Y['A']-55,'Action chunk',28.5,bold=True)
        for number,xx in enumerate(columns):
            self.robot_icon('robot-action-'+str(number),xx-29,PORT_Y['A']-28.5,58,57)
        for xx in [1160,1360]:
            self.text(xx,PORT_Y['A']+6,'…',27,'muted',anchor='middle')
        self.end()

        self.group('training-supervision')
        self.readout(PORT_Y['M'],train=True,destination='pose-output')
        self.text(978,PORT_Y['M']-55,'Target SE(3)',28.5,bold=True)
        for xx,index,tag in zip(columns,[1,4,7],['near','mid','far']):
            self.group('pose-example-'+tag)
            self.pose(xx,PORT_Y['M']-44,143,88,index)
            self.end()
        self.readout(PORT_Y['S'],train=True,destination='flow-output')
        self.text(978,PORT_Y['S']-55,'Sparse 3D flow',28.5,bold=True)
        for xx,index,tag in zip(columns,[0,3,6],['near','mid','far']):
            self.group('flow-example-'+tag)
            self.flow_panel(xx,PORT_Y['S']-44,165,88,index)
            self.end()
        self.end()
        self.end()

        self.group('b-attention-mask')
        self.text(34,644,'(b) Attention mask',31.5,bold=True,preserve_size=True)
        mx,my,cell=102,725,50
        for i,label in enumerate(['S','M','A']):
            self.text(mx+(i+.5)*cell,my-12,label,27.5,bold=True,anchor='middle')
            self.text(mx-17,my+i*cell+34,label,27.5,bold=True,anchor='end')
        for rr in range(3):
            for cc in range(3):
                fill=C['world_fill'] if rr<2 else C['action_mid']
                self.rect(mx+cc*cell,my+rr*cell,cell,cell,
                          fill if cc<=rr else C['white'],'#969696',1.05)
        self.end()

        self.group('c-training-inference')
        self.text(356,644,'(c) Training and inference',31.5,bold=True,preserve_size=True)
        self.group('training-path')
        self.text(356,739,'Training',26.5,bold=True)
        self.rect(490,698,225,66,'#F5F5F5',C['line'],1.4,radius=2)
        self.text(602.5,739,'Joint forward',26.5,bold=True,anchor='middle')
        self.plain_link(717,731,738,'training-branch')
        self.circle(738,731,2,C['ink'])
        self.arrow([(738,731),(738,699),(758,699)],'ink',1.9,dash=[5,4],head=5.5,destination='world-readouts')
        self.arrow([(738,731),(738,757),(758,757)],'ink',1.9,head=5.5,destination='action-head')
        for yy,label,role in [(681,'World readouts','world'),(739,'Action head','action')]:
            self.rect(760,yy,210,36,C[role+'_fill'],C[role],1.4,radius=2)
            self.text(865,yy+26,label,24.5,anchor='middle')
        self.arrow([(972,699),(1024,699)],'ink',1.9,dash=[5,4],head=5.5,destination='auxiliary-loss')
        self.arrow([(972,757),(1024,757)],'ink',1.9,head=5.5,destination='flow-matching-loss')
        self.text(1040,708,'Auxiliary loss',26.5,bold=True)
        self.text(1040,766,'Flow matching',26.5,bold=True)
        self.end()

        self.group('inference-path')
        self.text(356,903,'Inference',26.5,bold=True)
        self.rect(490,860,225,66,C['world_fill'],C['world'],1.4,radius=2)
        self.text(602.5,902,'World prefill',26.5,bold=True,anchor='middle')
        self.arrow([(717,893),(758,893)],'ink',1.9,head=5.5,destination='kv-cache')
        self.rect(760,860,210,66,C['white'],C['world'],1.4,radius=2)
        for dx,dy in [(6,-4),(3,-2),(0,0)]:
            self.rect(777+dx,881+dy,20,28,C['world_fill'],C['world'],.9,radius=.8)
        self.text(886,902,'K/V cache',26.5,anchor='middle')
        self.arrow([(972,893),(1038,893)],'ink',1.9,head=5.5,destination='cached-world-conditioning')
        self.group('repeated-action-update')
        self.rect(1040,860,260,66,C['action_fill'],C['action'],1.4,radius=2)
        self.text(1060,902,'Action update',26.5,bold=True)
        self.group('sampling-repeat-symbol')
        angles=np.linspace(-pi/3,4*pi/3,33)
        points=[(1268+13*cos(angle),893+13*sin(angle)) for angle in angles]
        self.arrow(points,'ink',1.8,head=7,record=False)
        self.end()
        self.end()
        self.group('noise-seed')
        noise=np.clip(np.random.default_rng(73).normal(128,48,(32,32)),0,255).astype(int)
        for row in range(32):
            for col in range(32):
                value=int(noise[row,col]); gray=f'#{value:02x}{value:02x}{value:02x}'
                self.rect(1144+1.625*col,790+1.625*row,1.625,1.625,gray,sw=0)
        self.rect(1144,790,52,52,stroke=C['line'],sw=.9)
        self.end()
        self.arrow([(1170,844),(1170,858)],'ink',1.9,head=5.5,destination='action-state-input')
        self.arrow([(1302,893),(1416,893)],'ink',1.9,head=5.5,destination='deployed-action-chunk')
        self.text(1460,838,'Action chunk',26.5,bold=True,anchor='middle')
        self.robot_icon('deployed-action-robot',1431,864.5,58,57)
        self.end()
        self.end()

    def export(self):
        assert not self.groups
        outside=[t for t in self.texts if t['x']<0 or t['y']<0 or t['x']+t['width']>W or t['y']+t['height']>H]
        if outside: raise ValueError(outside)
        self.pdf.showPage(); self.pdf.save()
        desc=('FoveaWAM architecture with aligned input-token rows and the accepted compact v2 layer, rotated counterclockwise by 90 degrees. '
              'Stream positions are reordered to Scene, Summary, Action from top to bottom, preserving shared attention and both residual stages. '
              'RGB is a Blender illustration of the recorded state; depth remains from the original recording. Current RGB-D, target history, robot state and noisy actions occupy four equally spaced input rows. '
              'Larger token glyphs form one packed column: visual, target and robot segments form S, learned summaries form M, and noisy actions form A. Color and small gaps separate segments; no collector or external ingress arrows are drawn. '
              'Only the visual frontend is shown as a Vision Encoder, contracting toward tokens. Scene and Summary share one World FFN; Action uses its own FFN. '
              'Panel labels and whitespace group the unframed overview and two lower details. The attention mask uses aligned S/M/A row and column labels. '
              'Final patch and pooled-summary states support geometric readouts; dashed arrows denote training-only readouts, as explained in the caption. Actions are generated from hidden states, not decoded geometry. '
              'Training uses auxiliary supervision and flow matching; inference bypasses readouts and conditions repeated action updates on one fixed world K/V cache. An internal circular arrow denotes iteration; a centered noise square initializes the action state and one robot icon denotes the output chunk. '
              'Target history uses miniature SE(3) glyphs from recorded past states in one shared reference frame and display scale, retaining cumulative motion against the same pale historical reference. Robot symbols are original editable vectors with no image background. '
              'Geometric examples are recorded supervision labels and token glyph multiplicity is schematic.')
        svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH_MM}mm" height="{WIDTH_MM*H/W:.6f}mm" viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">\n'
             '<title id="title">FoveaWAM conceptual architecture</title>\n'
             f'<desc id="desc">{escape(desc)}</desc>\n'+'\n'.join(self.svg)+'\n</svg>\n')
        (OUT/(self.stem+'.svg')).write_text(svg,encoding='utf-8')
        (OUT/'layout_metadata.json').write_text(json.dumps(dict(texts=self.texts,arrows=self.arrows,boxes=self.boxes),ensure_ascii=False,indent=2),encoding='utf-8')
        document=pdfium.PdfDocument(str(OUT/(self.stem+'.pdf')))
        page=document[0]
        for filename,dpi in [(self.stem+'.png',300),('fig2_paper_width.png',96)]:
            bitmap=page.render(scale=dpi/72)
            bitmap.to_pil().save(OUT/filename)
            bitmap.close()
        page.close(); document.close()
        pdf_page=PdfReader(OUT/(self.stem+'.pdf')).pages[0]
        xobjects=pdf_page['/Resources'].get('/XObject',{})
        images=[v for v in xobjects.values() if v.get_object().get('/Subtype')=='/Image']
        report=dict(width_mm=WIDTH_MM,height_mm=WIDTH_MM*H/W,
                    minimum_body_font_pt=min(t['size'] for t in self.texts)*SCALE,
                    native_text_objects=len(self.texts),unique_raster_assets=len(images),
                    raster_image_placements=sum(1 for x in self.svg if x.startswith('<image ')),
                    native_vector_objects=sum(e.tag.rsplit('}',1)[-1] in ('rect','circle','polyline','polygon','path') for e in ET.fromstring(svg).iter()),
                    backbone_source='compact_v2',rotation_degrees=-90,
                    backbone_matrix=[0,-BB_K,BB_K,0,BB_X-30*BB_K,BB_Y+590*BB_K],
                    backbone_core_clip=[10,30,580,547],state_port_y=PORT_Y,
                    readout_source_x=BB_RIGHT,body_font_scale=BODY_FONT_SCALE,
                    input_row_centers=INPUT_ROWS,token_size=TOKEN_SIZE,
                    token_segments=TOKEN_SEGMENTS,external_ingress_arrows=False)
        (OUT/'export_report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report))

scene=Scene('fig2_se3wam')
scene.draw()
scene.export()



