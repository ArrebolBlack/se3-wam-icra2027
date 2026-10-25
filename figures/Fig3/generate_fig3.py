"""Editable Fig. 3. Hypothetical geometry, not measured trajectories.

Run: python generate_fig3.py
Dependencies: svglib, reportlab, pymupdf, pillow.
The SVG is the editing master. Every body, arrow and label is a vector object.
Canvas units are 1/4 pt; output is exactly 3.25 x 2.30 inches.
"""
from pathlib import Path
from math import sin, cos, radians, atan2
from html import escape
import json
import xml.etree.ElementTree as ET
import pymupdf as fitz
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from svglib.svglib import svg2rlg
from svglib.fonts import register_font
from reportlab.graphics import renderPDF

ROOT = Path(__file__).resolve().parent
W, H = 936, 662.4
BLUE, ORANGE, PURPLE = '#0072B2', '#E69F00', '#7B61A8'
INK, GRAY, PALE = '#282828', '#4D4D4D', '#B5B8BB'
parts = []

def add(s): parts.append(s)
def group(name, transform='', opacity=1):
    add(f'<g id="{name}" transform="{transform}" opacity="{opacity}">')
def end(): add('</g>')
def line(x1,y1,x2,y2,c=GRAY,w=2.5,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c}" stroke-width="{w}"{d}/>')
def path(d,c=GRAY,w=2.5,fill='none',dash=None):
    q=f' stroke-dasharray="{dash}"' if dash else ''
    add(f'<path d="{d}" stroke="{c}" stroke-width="{w}" fill="{fill}" stroke-linejoin="round" stroke-linecap="round"{q}/>')
def poly(points,fill,stroke=GRAY,w=2):
    add(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in points)}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" stroke-linejoin="round"/>')
def circle(x,y,r,fill='white',stroke=GRAY,w=2):
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')
def rect(x,y,w,h,fill,stroke='none',sw=2):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
def txt(x,y,s,size=28,c=INK,anchor='start',bold=False,italic=False):
    add(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" fill="{c}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}" font-style="{"italic" if italic else "normal"}">{escape(s)}</text>')
def math(x,y,s,size=30,c=INK,anchor='start'):
    add(f'<text x="{x}" y="{y}" font-family="Cambria" font-size="{size}" fill="{c}" text-anchor="{anchor}">{s}</text>')
def indexed(x,y,base,index,super=False,size=30,c=INK):
    math(x,y,base,size,c)
    math(x+size*.51,y+(-size*.34 if super else size*.22),index,size*.8,c)
def tint(hexcolor,strength):
    v=[int(hexcolor[i:i+2],16) for i in (1,3,5)]
    return '#' + ''.join(f'{round(255+(c-255)*strength):02X}' for c in v)
def arrow(x1,y1,x2,y2,c=GRAY,w=3,head=9,dash=None,both=False):
    line(x1,y1,x2,y2,c,w,dash)
    a=atan2(y2-y1,x2-x1)
    def tip(x,y,a):
        poly([(x,y),(x-head*cos(a)+head*.43*sin(a),y-head*sin(a)-head*.43*cos(a)),(x-head*cos(a)-head*.43*sin(a),y-head*sin(a)+head*.43*cos(a))],c,c,.5)
    tip(x2,y2,a)
    if both: tip(x1,y1,a+3.1415926536)
def triad(x,y,angle=0,c=ORANGE,L=25,lw=3.6,head=9):
    group(f'frame-{len(parts)}',f'translate({x},{y})')
    # Same yaw and oblique projection as the rigid T. Yaw does not tilt z.
    a=radians(angle)
    arrow(0,0,L*(cos(a)+.32*sin(a)),L*.72*sin(a),c,lw,head)
    arrow(0,0,L*(-sin(a)+.32*cos(a)),L*.72*cos(a),c,lw,head)
    arrow(0,0,0,-L,c,lw,head)
    circle(0,0,3.4,c,c,.7)
    end()

def tpart(x,y,angle=0,color=BLUE,opacity=1,scale=1,dashed=False):
    """A rigid T extruded 5 units, projected in the same oblique view."""
    group(f't-part-{len(parts)}',f'translate({x},{y}) scale({scale})')
    semantic=color
    color=tint(color,opacity)
    a=radians(angle)
    def project(p):
        xx,yy=p; rx=xx*cos(a)-yy*sin(a); ry=xx*sin(a)+yy*cos(a)
        return (rx+.32*ry,.72*ry)
    points=[(-34,-23),(34,-23),(34,-7),(10,-7),(10,29),(-10,29),(-10,-7),(-34,-7)]
    top=[project(p) for p in points]
    for i in range(len(top)):
        p,q=top[i],top[(i+1)%len(top)]
        if q[0]<p[0]: poly([p,q,(q[0],q[1]+6),(p[0],p[1]+6)],tint(semantic,.25*opacity),color,1.8)
    poly(top,tint(semantic,.13*opacity),'none',0)
    pth='M '+' L '.join(f'{x},{y}' for x,y in top)+' Z'
    path(pth,color,3.2,dash='7 5' if dashed else None)
    end()

def conveyor(dx=0):
    group(f'conveyor-{dx}',f'translate({dx},0)')
    poly([(74.3,300),(240.3,300),(283,396),(117,396)],'#F4F5F5','#B8BDC0',2)
    poly([(117,396),(283,396),(283,412),(117,412)],'#E7E9EA','#B8BDC0',2)
    poly([(74.3,300),(117,396),(117,412),(74.3,316)],'#E0E3E5','#B8BDC0',2)
    for y in [321,345,369]:
        shift=(y-300)*42.7/96
        line(74.3+shift,y,240.3+shift,y,'#D6DADC',1.4)
    for x in [127,164,201,238,274]: circle(x,404,3,'#BBC0C3','none',0)
    end()

def gripper(x,y,angle=0,c=GRAY,scale=1):
    group(f'gripper-{len(parts)}',f'translate({x},{y}) rotate({angle}) scale({scale})')
    path('M -17,-19 L -17,-4 L -10,0 M 17,-19 L 17,-4 L 10,0',c,5)
    path('M -17,-19 L 17,-19',c,7)
    end()

def target_gripper(x,y,angle,scale=1.28):
    """Grasp the T stem, using exactly the body's oblique yaw projection."""
    group(f'target-gripper-{len(parts)}',f'translate({x},{y}) scale({scale})')
    a=radians(angle)
    def project(xx,yy):
        rx=xx*cos(a)-yy*sin(a); ry=xx*sin(a)+yy*cos(a)
        return (rx+.32*ry,.72*ry)
    for points in [[(-16,42),(-16,17),(-10,17)],
                   [(16,42),(16,17),(10,17)], [(-16,42),(16,42)]]:
        p=[project(*v) for v in points]
        path('M '+' L '.join(f'{px},{py}' for px,py in p),PURPLE,4)
    end()

def robot(dx=0,grip_shift=0):
    group(f'robot-{dx}',f'translate({dx},0)')
    poly([(17,417),(61,417),(71,430),(8,430)],'#DDE0E2','#8B9297',2)
    path('M 39,414 L 26,341 L 72,306 L 107,326','#737C83',17)
    path('M 39,414 L 26,341 L 72,306 L 107,326','#D8DDE0',11)
    for x,y in [(39,410),(26,341),(72,306),(107,326)]: circle(x,y,9,'#EEF0F1','#737C83',2.5)
    line(107,326,122+grip_shift,334,GRAY,8)
    gripper(131+grip_shift,349,-26,GRAY,.8)
    end()

def title(x,letter,line1,line2):
    txt(x,30,f'({letter}) {line1}',30,bold=True)
    txt(x,64,line2,30,bold=True)

def draw():
    add(f'<svg xmlns="http://www.w3.org/2000/svg" width="3.25in" height="2.3in" viewBox="0 0 {W} {H}">')
    add('<title>Acting on a moving target — schematic</title><desc>Three equal-width panels show ambiguous motion from the same current pose, different future target poses at the same physical application time, and task-role-dependent precision. Command issue times are anchored to capture, uniformly spaced by 50 ms; commands whose issue slots precede chunk arrival expire. Task delay shifts the application time after issue. The illustrated inference latency is two periods and task delay one period, not measured delays. Sparse scene flow covers every role; target SE(3) is additional supervision. Hypothetical geometry, not experimental data.</desc>')
    rect(0,0,W,H,'white')
    # Equal-width panels are separated by whitespace, not cards.
    title(8,'a','Same pose,','different motion')
    title(324,'b','Pose at','execution')
    title(640,'c','Precision','by role')
    group('panel-a')
    conveyor(); robot()
    # Two different causal histories ending at exactly one rigid pose.
    path('M 58,171 C 75,205 90,244 113,277 C 133,305 145,325 161,346',BLUE,3.8)
    path('M 252,171 C 235,205 214,247 193,284 C 177,311 169,331 161,346',BLUE,3.8,dash='10 7')
    tpart(58,171,-28,BLUE,.55,.85)
    tpart(104,258,-12,BLUE,.8,.85)
    tpart(252,171,55,BLUE,.55,.85,True)
    tpart(207,258,28,BLUE,.8,.85,True)
    tpart(161,346,0,BLUE,1,1.02)
    txt(47,140,'A',28,BLUE,bold=True)
    txt(244,140,'B',28,BLUE,bold=True)
    txt(154,202,'−100',28,GRAY,'middle')
    txt(154,233,'ms',28,GRAY,'middle')
    txt(157,292,'−50',28,GRAY,'middle')
    rect(220,324,86,30,'white')
    txt(226,347,'0 ms',28,BLUE)
    line(205,343,190,343,BLUE,2)
    txt(154,479,'Same pose at',28,INK,'middle')
    indexed(140,513,'τ','t',size=36,c=BLUE)
    txt(154,556,'Motion remains',28,GRAY,'middle')
    txt(154,589,'ambiguous',28,GRAY,'middle')
    end()
    group('panel-b')
    conveyor(316); robot(316)
    tpart(477,346,0,GRAY,.3,1.02)
    # Future geometry and action are distinct overlays, no model-input arrows.
    tpart(472,197,-34,ORANGE,1,1.28)
    tpart(559,294,38,ORANGE,1,1.28,True)
    triad(472,193,-34,ORANGE,40,lw=4.2,head=10)
    triad(559,289,38,ORANGE,40,lw=4.2,head=10)
    txt(428,153,'A',28,INK,bold=True)
    txt(578,246,'B',28,INK,bold=True)
    # Action paths end at two correspondingly oriented grippers.
    path('M 446,343 C 410,279 458,252 516,229',PURPLE,4)
    path('M 446,343 C 473,379 518,363 539,325',PURPLE,4,dash='10 6')
    arrow(491,240,503,235,PURPLE,3.6,9)
    arrow(527,345,532,337,PURPLE,3.6,9)
    target_gripper(472,197,-34)
    target_gripper(559,294,38)
    txt(324,113,'At',28)
    indexed(362,113,'τ','a',True,size=36)
    txt(405,113,'for A / B',28)
    # Shared physical clock. Issue at tau_t+j*Delta_a; apply after d_task.
    # Illustrative ell_t=2*Delta_a, d_task=Delta_a, NOT measured performance.
    # The paper expires by issue slot j*Delta_a < ell_t, not application time.
    issue_y,apply_y=488,588
    ticks=[410+40*j for j in range(6)]
    for x in ticks:
        line(x,issue_y,x,apply_y,'#E0E3E5',1.2)
        line(x,issue_y-8,x,issue_y+8,GRAY,1.8)
        line(x,apply_y-6,x,apply_y+6,'#B5B8BB',1.6)
    txt(324,497,'Issue',28,GRAY)
    txt(324,597,'Apply',28,GRAY)
    arrow(404,issue_y,623,issue_y,GRAY,2.2,7)
    arrow(404,apply_y,623,apply_y,GRAY,2.2,7)
    for x in ticks[:2]:
        rect(x-5,issue_y-5,10,10,'#B5B8BB')
        line(x-8,issue_y+8,x+8,issue_y-8,'#7C858C',2.2)
    for x in ticks[2:5]: rect(x-6,issue_y-6,12,12,PURPLE)
    for x in ticks[3:]: circle(x,apply_y,6,PURPLE,PURPLE,1)
    txt(382,526,'expired',28,GRAY)
    # Latency is capture to handover, whereas d_task is issue to application.
    arrow(410,455,490,455,GRAY,2.2,6,both=True)
    indexed(431,444,'ℓ','t',size=36,c=GRAY)
    arrow(530,455,570,455,PURPLE,2.2,6,both=True)
    indexed(494,444,'Δ','a',size=36)
    txt(531,444,'= 50 ms',28)
    path('M 490,498 L 490,550 L 530,550 L 530,578',PURPLE,2.8)
    arrow(530,566,530,580,PURPLE,2.8,8)
    indexed(540,549,'d','task',size=36,c=GRAY)
    indexed(396,574,'τ','t',size=36,c=BLUE)
    indexed(516,624,'τ','a',True,size=36,c=PURPLE)
    end()
    group('panel-c')
    # Background remains present, with sparse stationary scene samples.
    txt(640,115,'Background',28,GRAY)
    poly([(810,153),(880,130),(921,156),(852,180)],'#FAFAFA','#D6DADC',1.6)
    poly([(830,134),(862,124),(890,135),(858,147)],'#F1F2F2','#C6CACD',2)
    poly([(830,134),(858,147),(858,170),(830,157)],'#ECEEEF','#C6CACD',2)
    poly([(858,147),(890,135),(890,158),(858,170)],'#E1E4E6','#C6CACD',2)
    path('M 800,120 L 820,133','#92989C',1.8)
    conveyor(632); robot(632,grip_shift=12)
    # Obstacle at the same depth as the target and with a wide safety clearance.
    poly([(891,251),(907,241),(907,340),(891,350)],'#D1D5D8','#7C858C',2.4)
    poly([(907,241),(923,249),(923,348),(907,340)],'#E4E7E9','#7C858C',2.4)
    poly([(891,251),(907,241),(923,249),(907,260)],'#F3F4F4','#7C858C',2.4)
    txt(818,204,'Context:',28,GRAY)
    txt(818,234,'obstacle',28,GRAY)
    line(886,240,900,261,GRAY,1.8)
    tpart(793,330,0,ORANGE,1,1.02)
    txt(743,262,'Target',28,INK,bold=True)
    line(785,268,793,307,GRAY,1.8)
    # The horizontal bar, not the narrower stem, is the nearest target surface.
    line(827,316,827,334,GRAY,2.2)
    line(891,316,891,334,GRAY,2.2)
    arrow(829,325,889,325,GRAY,2.4,7,both=True)
    math(845,295,'m ≫ ε',32,GRAY,'middle')
    # Whole-scene sparse samples: robot, target, belt, wall and background.
    for x,y in [(855,140),(871,158),(903,275),(903,311)]:
        circle(x,y,4,ORANGE,'#9B6900',1.3)
    for x,y in [(660,350),(823,386),(866,382)]:
        line(x,y,x+20,y+2,'white',5)
        arrow(x,y,x+20,y+2,ORANGE,3.2,7)
    line(802,351,828,351,'white',6)
    arrow(802,351,828,351,ORANGE,3.6,8)
    txt(710,444,'Context: driver',28,GRAY)
    # Local contact magnification is tied directly to the scene contact.
    circle(788,343,11,'none',GRAY,1.8)
    circle(788,343,3.2,INK,INK,.7)
    path('M 798,348 L 931,449 L 931,469',GRAY,1.8,dash='5 5')
    # A full-width local contact view separates the two coordinate frames.
    # The purple pad touches the orange surface. E and O differ tangentially
    # within epsilon, not through a physical free-space gap. Parallel triads
    # explicitly show orientation alignment. This is a magnified schematic.
    rect(645,469,286,171,'white','#BBC0C4',1.8)
    txt(655,495,'Contact',28,INK)
    rect(741,548,174,24,'#FFF4D8',ORANGE,2.5)
    rect(668,525,123,23,'#EBE5F3',PURPLE,2.8)
    triad(770,548,0,PURPLE,42,lw=4.4,head=10)
    triad(824,548,0,ORANGE,42,lw=4.4,head=10)
    circle(770,548,5.3,PURPLE,PURPLE,.7)
    circle(824,548,5.3,INK,INK,.7)
    math(759,495,'E',34,PURPLE)
    math(813,495,'O',34,'#8C6200')
    line(770,554,770,604,GRAY,2.4)
    line(824,554,824,604,GRAY,2.4)
    arrow(772,600,822,600,GRAY,2.6,7,both=True)
    math(797,628,'≤ ε',34,INK,'middle')
    end()
    arrow(11,643,31,643,ORANGE,3.2,7)
    circle(44,643,4,ORANGE,'#9B6900',1.3)
    txt(56,652,'All roles: sparse flow; target adds SE(3).',28,GRAY)
    add('</svg>')
    return '\n'.join(parts)

def export():
    svg=ROOT/'fig3.svg'; svg.write_text(draw(),encoding='utf-8')
    fonts=Path('C:/Windows/Fonts')
    for name,file in [('Arial','arial.ttf'),('Arial-Bold','arialbd.ttf'),('Arial-Italic','ariali.ttf'),('Times New Roman','times.ttf'),('Times New Roman-Italic','timesi.ttf')]:
        pdfmetrics.registerFont(TTFont(name,str(fonts/file)))
    pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial-Italic',boldItalic='Arial-Bold')
    pdfmetrics.registerFontFamily('Times New Roman',normal='Times New Roman',italic='Times New Roman-Italic')
    pdfmetrics.registerFont(TTFont('Cambria',str(fonts/'cambria.ttc'),subfontIndex=0))
    register_font('Arial',str(fonts/'arial.ttf'),weight='normal',rlgFontName='Arial')
    register_font('Arial',str(fonts/'arialbd.ttf'),weight='bold',rlgFontName='Arial-Bold')
    register_font('Cambria',str(fonts/'cambria.ttc'),rlgFontName='Cambria')
    drawing=svg2rlg(str(svg)); renderPDF.drawToFile(drawing,str(ROOT/'fig3.pdf'))
    pdf=fitz.open(ROOT/'fig3.pdf')
    assert abs(pdf[0].rect.width-234)<.01 and abs(pdf[0].rect.height-165.6)<.01
    assert not pdf[0].get_images(), 'Unexpected rasterization in the vector PDF'
    spans=[s for b in pdf[0].get_text('dict')['blocks'] if 'lines' in b
           for line in b['lines'] for s in line['spans']]
    assert all(s['bbox'][0]>=0 and s['bbox'][1]>=0 and
               s['bbox'][2]<=234.1 and s['bbox'][3]<=165.7 and
               '\ufffd' not in s['text'] for s in spans), 'Text outside page or missing glyph'
    for dpi,name in [(600,'fig3.png'),(288,'fig3_preview.png'),(192,'fig3_print_check.png')]:
        pix=pdf[0].get_pixmap(dpi=dpi,alpha=False); pix.save(ROOT/name)
    Image.open(ROOT/'fig3_print_check.png').convert('L').save(ROOT/'fig3_grayscale.png')
    info={'physical_inches':[pdf[0].rect.width/72,pdf[0].rect.height/72],
          'embedded_raster_images':len(pdf[0].get_images()),'vector_paths':len(pdf[0].get_drawings()),
          'svg_text_objects':len(ET.parse(svg).findall('.//{http://www.w3.org/2000/svg}text')),
          'text_bounds':'pass','font_sizes_pt':sorted(set(round(s['size'],2) for s in spans)),
          'fonts':pdf[0].get_fonts(),'schematic':True}
    (ROOT/'export_check.json').write_text(json.dumps(info,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in info.items() if k!='fonts'}))

if __name__=='__main__': export()
