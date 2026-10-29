"""Deterministic real-robot Fig. 7 layout (project directory Fig6).
Task photographs and synthetic paired-trial placeholders retain separate identities.
"""
from __future__ import annotations
import argparse, base64, io, json
from pathlib import Path
from xml.sax.saxutils import escape
import pymupdf
from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parent
BLUE,PURPLE,INK,MUTED,FAIL="#0072B2","#7B61A8","#20262D","#505A64","#D55E00"
W,GAP=495.,4.
PW=(W-5*GAP)/6
PH=PW*9/16
TITLES=[["T1 Conveyor","grasping"],["T2 Placement","into moving box"],["T3 Turntable","grasping"],["T4 Toy-car","grasping"],["T5 Tennis-ball","grasping"],["T6 Ramp-cart","grasping"]]
MOTIONS=["Linear travel","Conveyor translation","Circular travel","Planar travel","Tennis ball","Cart on incline"]

class Drawing:
    """One primitive stream drives both SVG and PDF."""
    def __init__(self,h,out,panel_width=PW,font_family="DejaVu Sans",status="layout_preview"):
        self.h,self.out=h,out
        self.pw,self.ph=panel_width,panel_width*9/16
        self.font_family=font_family
        self.status=status
        out.parent.mkdir(parents=True,exist_ok=True)
        if font_family=="Arial":
            fp=Path("C:/Windows/Fonts")
        else:
            import matplotlib
            fp=Path(matplotlib.get_data_path())/"fonts/ttf"
        font_files=("arial.ttf","arialbd.ttf") if font_family=="Arial" else ("DejaVuSans.ttf","DejaVuSans-Bold.ttf")
        for name,f in zip(("Fig6","Fig6Bold"),font_files):
            pdfmetrics.registerFont(TTFont(name,str(fp/f)))
        self.pdf=canvas.Canvas(str(out.with_suffix(".pdf")),pagesize=(W,h))
        self.pdf.setTitle("Fig. 7 - real-robot tasks and paired-trial layout")
        self.svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{h/72:.6f}in" viewBox="0 0 {W} {h}">',
            '<title>Fig. 7: real-robot tasks and paired-trial layout</title>',
            '<desc>Panel sources are identified in manifest.json. Paired-trial records are pending.</desc>',
            f'<rect width="{W}" height="{h}" fill="white"/>']
        faces=[]
        for weight,name in zip((400,700),font_files):
            encoded=base64.b64encode((fp/name).read_bytes()).decode()
            faces.append("@font-face{font-family:'"+font_family+"';font-style:normal;font-weight:"+str(weight)+";src:url(data:font/ttf;base64,"+encoded+") format('truetype');}")
        self.svg.append('<defs><style>'+''.join(faces)+'</style></defs>')
        self.sizes,self.images,self.text_bounds=[],[],[]
    def group(self,n):self.svg.append(f'<g id="{n}">')
    def end(self):self.svg.append('</g>')
    def rect(self,x,y,w,h,color):
        self.svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
        self.pdf.setFillColor(color);self.pdf.rect(x,self.h-y-h,w,h,stroke=0,fill=1)
    def text(self,x,y,s,size=7,color=INK,bold=False,anchor="start"):
        self.sizes.append(size)
        self.svg.append(f'<text x="{x}" y="{y}" font-family="{self.font_family}" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{escape(s)}</text>')
        name="Fig6Bold" if bold else "Fig6"
        self.pdf.setFont(name,size);self.pdf.setFillColor(color)
        width=pdfmetrics.stringWidth(s,name,size)
        x-=width/2 if anchor=="middle" else width if anchor=="end" else 0
        self.text_bounds.append({"text":s,"bbox":[x,y-size,x+width,y+size*.25],"size_pt":size})
        self.pdf.drawString(x,self.h-y,s)
    def line(self,pts,color=MUTED,width=.7,dash=None):
        self.svg.append('<polyline points="'+' '.join(f'{x:.4f},{y:.4f}' for x,y in pts)+
            f'" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"'+
            (f' stroke-dasharray="{dash}"' if dash else '')+'/>')
        self.pdf.setStrokeColor(color);self.pdf.setLineWidth(width)
        self.pdf.setDash([float(x) for x in dash.split(",")] if dash else [])
        p=self.pdf.beginPath();p.moveTo(pts[0][0],self.h-pts[0][1])
        for x,y in pts[1:]:p.lineTo(x,self.h-y)
        self.pdf.drawPath(p);self.pdf.setDash([])
    def event_label(self,cx,y,label,index=None):
        """Editable typographic subscripts; never rely on missing Unicode glyphs."""
        if index is None:return self.text(cx,y,label,7.5,anchor="middle")
        base=label+"  τ"
        width=pdfmetrics.stringWidth(base,"Fig6",7.5)
        subwidth=pdfmetrics.stringWidth(index,"Fig6",7.2)
        xx=cx-(width+subwidth)/2
        self.text(xx,y,base,7.5)
        self.text(xx+width,y+2 if index=="t" else y-3,index,7.2)
    def marker(self,x,y,color=BLUE,r=1.3,shape="circle"):
        if shape=="square":self.rect(x-r,y-r,2*r,2*r,color);return
        self.svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="white" stroke="{color}" stroke-width="0.7"/>')
        self.pdf.setFillColor("white");self.pdf.setStrokeColor(color);self.pdf.setLineWidth(.7)
        self.pdf.circle(x,self.h-y,r,stroke=1,fill=1)
    def photo(self,path,x,y,w=None,h=None,crop=None):
        w,h=self.pw if w is None else w,self.ph if h is None else h
        im=Image.open(path).convert("RGB")
        if crop is None:
            iw,ih=im.size;cw=min(iw,ih*16/9);ch=cw*9/16
            crop=[(iw-cw)/2,(ih-ch)/2,cw,ch]
        cx,cy,cw,ch=crop
        if abs(cw/ch-16/9)>1e-6:raise ValueError("Crop must be 16:9")
        if cx<0 or cy<0 or cx+cw>im.width+.01 or cy+ch>im.height+.01:raise ValueError("Crop outside original")
        if any(abs(v-round(v))>1e-6 for v in crop):raise ValueError("Crop coordinates must be integer source pixels")
        cropped=im.crop((round(cx),round(cy),round(cx+cw),round(cy+ch)))
        # Keep the reviewed native crop in assets; embed only the 600-ppi print raster.
        embedded_width=round(w/72*600)
        if cropped.width>embedded_width:
            cropped=cropped.resize((embedded_width,round(embedded_width*9/16)),Image.Resampling.LANCZOS)
        stream=io.BytesIO();cropped.save(stream,format="PNG");data=stream.getvalue()
        self.svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="none" href="data:image/png;base64,{base64.b64encode(data).decode()}"/>')
        self.pdf.drawImage(ImageReader(io.BytesIO(data)),x,self.h-y-h,w,h)
        self.images.append({"path":str(path),"crop_xywh":crop,"source_px":im.size,"embedded_px":cropped.size,"effective_ppi":cropped.width/(w/72)})
    def save(self):
        self.svg.append('</svg>');self.out.with_suffix(".svg").write_text("\n".join(self.svg),encoding="utf-8")
        self.pdf.showPage();self.pdf.save();doc=pymupdf.open(self.out.with_suffix(".pdf"))
        for dpi,suffix in [(600,""),(144,"_screen"),(96,"_96ppi")]:
            pix=doc[0].get_pixmap(dpi=dpi,alpha=False)
            im=Image.frombytes("RGB",(pix.width,pix.height),pix.samples)
            im.save(self.out.with_name(self.out.name+suffix).with_suffix(".png"),dpi=(dpi,dpi))
        report={"width_in":W/72,"height_in":self.h/72,"panels":len(self.images),"panel_size_pt":[self.pw,self.ph],"aspect":16/9,
            "min_font_pt":min(self.sizes),"font":self.font_family,"pdf_fonts":doc[0].get_fonts(),"raster_dpi":600,"images":self.images,"text_bounds":self.text_bounds,
            "status":self.status}
        self.out.with_suffix(".json").write_text(json.dumps(report,indent=2),encoding="utf-8")
        print(json.dumps({k:report[k] for k in ["width_in","height_in","panels","min_font_pt","status"]}))

def overlay(d,prepared,x,y):
    PW,PH=d.pw,d.ph
    cx,cy,cw,ch=prepared["crop_xywh"]
    def xy(p):return x+(p[0]-cx)/cw*PW,y+(p[1]-cy)/ch*PH
    cid=f'clip-{len(d.svg)}'
    d.svg.append(f'<defs><clipPath id="{cid}"><rect x="{x}" y="{y}" width="{PW}" height="{PH}"/></clipPath></defs><g clip-path="url(#{cid})">')
    d.pdf.saveState();p=d.pdf.beginPath();p.rect(x,d.h-y-PH,PW,PH);d.pdf.clipPath(p,stroke=0)
    for key,color,dash in [("history_segments",BLUE,None),("command_segments",PURPLE,"2,1")]:
        for seg in prepared.get(key,[]):
            pts=[xy(p) for p in seg]
            if len(pts)>1:d.line(pts,"white",1.8,dash);d.line(pts,color,.85,dash)
    for p in prepared.get("history_markers",[]):d.marker(*xy(p))
    if prepared.get("closure_uv") is not None:d.marker(*xy(prepared["closure_uv"]),color=PURPLE,r=1.7,shape="square")
    e=prepared.get("separation")
    if e:
        pts=[xy(e["gripper_uv"]),xy(e["target_uv"])]
        d.line(pts,"white",2);d.line(pts,FAIL,.9)
    d.pdf.restoreState();d.svg.append('</g>')

def panel(d,m,key,x,y):
    p=m["panels"][key]
    if p["status"] in {"synthetic","task_photo"}:d.photo(ROOT/p["image"],x,y,crop=p.get("crop_xywh"))
    elif p["status"]=="real":
        prep=json.loads((ROOT/p["prepared"]).read_text(encoding="utf-8"))
        d.photo(Path(prep["frame_path"]),x,y,crop=prep["crop_xywh"]);overlay(d,prep,x,y)
    else:
        d.rect(x,y,d.pw,d.ph,"#F0F2F4");d.text(x+d.pw/2,y+d.ph/2,"pending asset/data",7,anchor="middle")

def conceptual_roles(d,x,y):
    # Labels identify the two balls in the synthetic illustration, not tracker output.
    # Source crop is fixed by manifest; these guides must never be reused on real photos.
    d.group("synthetic-t5-object-roles")
    for label,lx,tx,ty in [("Striker",2,16.5,24),("Target",47,51,23)]:
        d.line([(x+tx,y+ty),(x+lx+11,y+32)],"white",1.5)
        d.line([(x+tx,y+ty),(x+lx+11,y+32)],INK,.5)
        d.rect(x+lx-1,y+32,28,9.1,"#FFFFFF")
        d.text(x+lx,y+39.3,label,7)
    d.end()

def draw(manifest,variant,out):
    if variant=="polished":return draw_polished(manifest,out)
    m=json.loads(manifest.read_text(encoding="utf-8"));compact=variant=="compact"
    d=Drawing(129.6 if compact else 180.,out,status=m["status"])
    d.group("status");d.text(0,7,"(a) Six task concepts",7,bold=True)
    d.text(W,7,"Task sources in manifest; paired-trial data pending",7,color="#8B3C00",anchor="end");d.end()
    top=11
    d.group("task-images")
    for i in range(6):panel(d,m,f"t{i+1}",i*(PW+GAP),top)
    if not compact and m["panels"]["t5"]["status"]=="synthetic":conceptual_roles(d,4*(PW+GAP),top)
    d.end();d.group("task-labels")
    for i in range(6):
        x=i*(PW+GAP)
        if compact:
            d.rect(x,top,PW,16,"#FFFFFF")
            d.text(x+2,top+6.7,TITLES[i][0],6.7,bold=True);d.text(x+2,top+14.1,TITLES[i][1],6.7,bold=True)
            d.text(x+PW/2,top+PH+7,MOTIONS[i],6.1,color=MUTED,anchor="middle")
        else:
            for j,s in enumerate(TITLES[i]):d.text(x,top+PH+8+7.8*j,s,7,bold=True)
            d.text(x,top+PH+24,MOTIONS[i],7,color=MUTED)
    if compact:bhead,low=72.,76.5
    else:
        d.text(0,89,"(b) T5 paired-trial template · repeated images, no recorded comparison",7,bold=True)
        bhead,low=100.,105.
    d.end();d.group("method-labels")
    if compact:
        d.text(0,bhead,"(b) SE(3)-WAM · outcome pending",6.5,bold=True)
        d.text(3*(PW+GAP),bhead,"Baseline pending · outcome pending",6.5,bold=True)
    else:
        d.text(0,bhead,"SE(3)-WAM — outcome pending",7.3,bold=True)
        d.text(3*(PW+GAP),bhead,"Baseline TBD — outcome pending",7.3,bold=True)
    d.end();d.group("paired-images")
    if not compact:d.line([(W/2,94),(W/2,166)],"#B7BDC3",.4)
    for i in range(6):
        x=i*(PW+GAP);panel(d,m,f'pair_{i}',x,low)
        if compact:
            d.rect(x,low,PW,9.2,"#FFFFFF")
            d.text(x+PW/2,low+7.1,["Query slot  τₜ","Execution slot  τᵃ","Terminal slot"][i%3],6.7,bold=True,anchor="middle")
    d.end();d.group("timeline-placeholders")
    if compact:d.text(W/2,128.5,"Capture → execution → terminal: timestamps, tracking, commands and results pending",6.2,color=MUTED,anchor="middle")
    else:
        for j in range(2):
            x=j*3*(PW+GAP);yy=low+PH+5
            centers=[x+PW/2+i*(PW+GAP) for i in range(3)]
            d.line([(centers[0],yy),(centers[-1],yy)],"#75818D",.6,"2,2")
            for px,label in zip(centers,["Query / capture τₜ","First execution τᵃ","Terminal event"]):
                d.marker(px,yy,MUTED,r=1)
                d.text(px,yy+10,label,7,color=INK,anchor="middle")
        d.text(W/2,177,"Not to scale · trial key, criteria, measured timing and trajectories pending",7,color=MUTED,anchor="middle")
    d.end();d.save()

def draw_polished(manifest,out):
    """Photo-led two-row composition, with one disclosure and no invented data."""
    m=json.loads(manifest.read_text(encoding="utf-8"))
    left,gap=14.,4.
    pw=(W-left-5*gap)/6
    d=Drawing(171.,out,panel_width=pw,font_family="Arial",status=m["status"])
    xs=[left+i*(pw+gap) for i in range(6)]
    titles=[("Conveyor","grasping"),("Moving-box","placement"),("Turntable","grasping"),
            ("Toy-car","grasping"),("Tennis-ball","grasping"),("Ramp-cart","grasping")]
    motions=MOTIONS
    d.group("task-labels")
    d.text(0,8,"(a)",8,bold=True)
    for i,(x,(first,second)) in enumerate(zip(xs,titles)):
        d.text(x,8,f"T{i+1}",7.5,color=MUTED,bold=True)
        d.text(x+14,8,first,8,bold=True)
        d.text(x+14,16.5,second,8)
    d.end();d.group("task-images")
    top=21.
    for i,x in enumerate(xs):panel(d,m,f"t{i+1}",x,top)
    d.end();d.group("motion-labels")
    for x,label in zip(xs,motions):d.text(x+pw/2,top+d.ph+10,label,7.4,color=MUTED,anchor="middle")
    d.end();d.group("method-labels")
    d.text(0,89,"(b)",8,bold=True)
    d.text(xs[0],89,"SE(3)-WAM",8.5,bold=True)
    d.text(xs[3],89,"Baseline",8.5,bold=True)
    for start in (0,3):d.line([(xs[start],92.5),(xs[start+2]+pw,92.5)],"#CBD0D4",.45)
    d.end();d.group("paired-images")
    low=96.
    for i,x in enumerate(xs):panel(d,m,f"pair_{i}",x,low)
    d.end();d.group("event-order")
    for start in (0,3):
        centers=[xs[start+i]+pw/2 for i in range(3)]
        yy=low+d.ph+5
        d.line([(centers[0],yy),(centers[-1],yy)],"#7D8790",.5)
        for cx,(label,index) in zip(centers,[("Query","t"),("First execution","a"),("Terminal event",None)]):
            d.marker(cx,yy,INK,r=1.1)
            d.event_label(cx,yy+9,label,index)
    d.end();d.group("disclosure")
    d.text(W/2,168,"Paired-trial panels: AI-generated placeholders · event order only",7.2,color=MUTED,anchor="middle")
    d.end();d.save()

if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--manifest",type=Path,default=ROOT/"manifest.json")
    ap.add_argument("--variant",choices=["compact","readable","polished"],default="polished")
    ap.add_argument("--output",type=Path,default=ROOT/"outputs/polished/fig6")
    a=ap.parse_args();draw(a.manifest,a.variant,a.output)
