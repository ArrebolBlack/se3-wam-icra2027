"""Generate editable CVPR concept SVGs, and render PDF/PNG with Chromium.

All geometry is conceptual. No experimental trajectories or results are used.
SVG coordinates are CSS pixels, at 96 px/in. Main text is 8--9 pt at 6.875 in.
The SVGs are the editable figure sources; this script documents construction.
"""
from pathlib import Path
import base64
import math
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
W = 660
COL = dict(blue="#0072B2", orange="#E69F00", purple="#7B61A8",
           gray="#4D4D4D", ink="#26343D", light="#F2F2F2", line="#CBD1D5")

def start(h):
    return [f'''<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{h/96:.6f}in" viewBox="0 0 {W} {h}">
<title>SE(3)-WAM conceptual research illustration</title>
<defs>
<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="context-stroke"/></marker>
<pattern id="hatch" width="5" height="5" patternUnits="userSpaceOnUse"><path d="M-1 1L1 -1M0 5L5 0M4 6L6 4" stroke="#9EA5AA" stroke-width=".6"/></pattern>
</defs>
<rect width="660" height="{h}" fill="white"/>
<g font-family="Arial, Helvetica, sans-serif" font-size="11.333" fill="{COL['ink']}">''']

def text(s,x,y,body,size=11.333,weight="normal",color=None,anchor="start"):
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color or COL["ink"]}" text-anchor="{anchor}">{escape(body)}</text>')

def rect(s,x,y,w,h,fill="white",stroke=None,rx=4,sw=.9):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke or COL["line"]}" stroke-width="{sw}"/>')

def line(s,x1,y1,x2,y2,color=None,width=1,dash=None,arrow=False,both=False):
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color or COL["gray"]}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arrow)"' if arrow else '')+(' marker-start="url(#arrow)"' if both else '')+'/>')

def target(s,x,y,angle,color):
    s.append(f'<g transform="translate({x},{y}) rotate({angle})"><path d="M-15 -10H10L16 -4V10H-15Z" fill="white" stroke="{color}" stroke-width="1.8"/><path d="M-7 0H7" stroke="{color}" stroke-width="1.3"/><circle cx="-8" cy="-5" r="1.6" fill="{color}"/></g>')

def eef(s,x,y,angle=0):
    s.append(f'<g transform="translate({x},{y}) rotate({angle})" fill="none" stroke="{COL["purple"]}" stroke-width="2"><path d="M-20 0H-8M-8 -12V12M-8 -12H5M-8 12H5"/></g>')

def interaction():
    s = start(184)
    text(s,7,13,"Why physical time matters",12,weight="bold")
    text(s,653,13,"Conceptual illustration",10.667,color=COL["gray"],anchor="end")
    for i, title in enumerate(["(a) Observation  t", "(b) Execution  t + δ", "(c) Contact  t"]):
        x=7+i*219
        rect(s,x,23,208,128,fill="#FAFAFA")
        text(s,x+9,39,title,12,weight="bold")
        if i == 2:
            s[-1] = s[-1].replace('</text>', '<tspan baseline-shift="sub" font-size="9">c</tspan></text>')
        # The same obstacle and scene footprint are repeated across all times.
        rect(s,x+10,48,188,73,fill="white",stroke="#E2E5E7",rx=0,sw=.7)
        rect(s,x+142,95,29,19,fill="url(#hatch)",stroke=COL["gray"],rx=1,sw=.9)
        if i==0:
            target(s,x+106,79,-14,COL["blue"])
            eef(s,x+50,96,-12)
            # Competing motions pass through the identical current pose.
            line(s,x+108,59,x+146,54,COL["orange"],1.2,arrow=True)
            line(s,x+100,59,x+65,54,COL["orange"],1.2,arrow=True)
            text(s,x+104,139,"One pose, ambiguous motion",10.667,anchor="middle")
        elif i==1:
            target(s,x+127,73,-29,COL["orange"])
            eef(s,x+90,90,-23)
            line(s,x+57,97,x+75,91,COL["purple"],1.1,arrow=True)
            text(s,x+104,139,"State evolves during the delay",10.667,anchor="middle")
        else:
            target(s,x+149,68,-42,COL["orange"])
            eef(s,x+129,82,-42)
            # Clearance is a geometric question, not a measured success marker.
            line(s,x+149,82,x+149,95,COL["gray"],.8,dash="2 2")
            text(s,x+24,112,"clearance",10.667,color=COL["gray"])
            line(s,x+75,108,x+139,91,COL["gray"],.7)
            text(s,x+104,139,"Contact geometry + clearance",10.667,anchor="middle")
    # Roles are stated explicitly; fill and color never encode a success outcome.
    s.append('<g transform="translate(20,169) scale(.8)">')
    target(s,0,0,-14,COL["blue"])
    s.append('</g>')
    text(s,41,174,"target: contact pose",10.667)
    rect(s,208,161,19,15,fill="url(#hatch)",stroke=COL["gray"],rx=1)
    text(s,234,174,"relevant context: clearance",10.667)
    eef(s,439,169)
    text(s,453,174,"EEF",10.667,color=COL["purple"])
    line(s,502,169,523,169,COL["orange"],1.2,arrow=True)
    text(s,529,174,"possible future",10.667)
    s.append('</g></svg>')
    return '\n'.join(s)

def framework():
    s = start(184)
    text(s,7,13,"Controlled Q1–Q3 design study",12,weight="bold")
    text(s,653,13,"Candidate framework",10.667,color=COL["gray"],anchor="end")
    rect(s,7,39,126,104,fill="#F5FAFD",stroke="#A7C8DA")
    text(s,15,56,"Q1  History encoding",11.333,weight="bold")
    for i in range(3):
        x=18+33*i
        rect(s,x,67,26,22,fill="white",stroke="#A7C8DA",rx=1,sw=.8)
        s.append(f'<circle cx="{x+7+4*i}" cy="79" r="3.2" fill="{COL["blue"]}"/>')
    text(s,70,104,"timestamped",10.667,anchor="middle")
    text(s,70,117,"observations",10.667,anchor="middle")
    text(s,70,133,"→ history encoder",10.667,color=COL["blue"],anchor="middle")
    rect(s,151,28,421,115,fill="white",stroke=COL["gray"],rx=4,sw=.9)
    text(s,361.5,44,"Common world/action framework",11.333,weight="bold",anchor="middle")
    rect(s,160,54,194,79,fill="#FFFAEE",stroke="#E6C990")
    text(s,168,70,"Q2  Future representation",11.333,weight="bold")
    text(s,168,88,"Target: pose / tracks / features",10.667)
    text(s,168,104,"Scene: geometry / flow / latent",10.667)
    text(s,168,120,"Granularity: uniform / mixed",10.667)
    rect(s,362,54,201,79,fill="#F8F5FC",stroke="#C9BBDC")
    text(s,370,70,"Q3  Backbone + information flow",11.333,weight="bold")
    text(s,370,88,"Select D / E, then compare",10.667)
    text(s,370,104,"Auxiliary · W→A · A→W",10.667)
    text(s,370,120,"Bidirectional · FTA",10.667)
    rect(s,592,71,61,42,fill="#F8F5FC",stroke=COL["purple"],sw=1)
    text(s,622.5,88,"Action",11.333,weight="bold",color=COL["purple"],anchor="middle")
    text(s,622.5,103,"chunk",10.667,color=COL["purple"],anchor="middle")
    line(s,133,92,151,92,COL["blue"],1.3,arrow=True)
    line(s,572,92,592,92,COL["purple"],1.3,arrow=True)
    text(s,257,160,"Future labels (train)",10.667,anchor="middle")
    line(s,257,150,257,134,COL["gray"],.9,dash="3 2",arrow=True)
    text(s,565,160,"Action labels (train)",10.667,anchor="middle")
    # Labels supervise action outputs; routed away from candidate-box text.
    s.append(f'<path d="M565 150V141H623V114" fill="none" stroke="{COL["gray"]}" stroke-width=".9" stroke-dasharray="3 2" marker-end="url(#arrow)"/>')
    line(s,8,160,29,160,COL["blue"],1.2,arrow=True)
    text(s,34,164,"data / computation",10.667)
    line(s,8,176,29,176,COL["gray"],.9,dash="3 2",arrow=True)
    text(s,34,180,"training supervision",10.667)
    text(s,440,180,"Report and control data, timing, capacity and inference cost",10.667,color=COL["gray"],anchor="middle")
    s.append('</g></svg>')
    return '\n'.join(s)

def render(svg):
    browser = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
    if not browser.exists():
        raise RuntimeError("Expected Chromium renderer is unavailable")
    payload=base64.b64encode(svg.read_bytes()).decode("ascii")
    _, _, width, height = ET.parse(svg).getroot().attrib['viewBox'].split()
    html=f'''<!doctype html><meta charset="utf-8"><style>@page{{size:{width}px {height}px;margin:0}}html,body{{width:{width}px;height:{height}px;margin:0;overflow:hidden}}img{{display:block;width:{width}px;height:{height}px}}</style><img src="data:image/svg+xml;base64,{payload}">'''
    with tempfile.TemporaryDirectory(prefix="se3wam-concept-") as tmp:
        tmp=Path(tmp)
        p=tmp/"figure.html"
        p.write_text(html,encoding="utf-8")
        common=[str(browser),"--headless=new","--disable-gpu",f"--user-data-dir={tmp/'profile'}","--no-pdf-header-footer"]
        result=subprocess.run(common+[f"--print-to-pdf={svg.with_suffix('.pdf')}",p.as_uri()],capture_output=True,text=True)
        if result.returncode or not svg.with_suffix('.pdf').exists():
            raise RuntimeError(result.stderr)
        # Independent raster of exactly the same vector source at 3x display scale.
        result=subprocess.run(common+["--force-device-scale-factor=3",f"--window-size={width},{height}",f"--screenshot={svg.with_suffix('.png')}",p.as_uri()],capture_output=True,text=True)
        if result.returncode or not svg.with_suffix('.png').exists():
            raise RuntimeError(result.stderr)

if __name__=="__main__":
    ROOT.mkdir(parents=True,exist_ok=True)
    for name,content in [("interaction_timing",interaction()),("study_framework",framework())]:
        path=ROOT/f"{name}.svg"
        path.write_text(content,encoding="utf-8")
        render(path)
        print(path.name)
