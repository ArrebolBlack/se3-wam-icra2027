"""Build the real-robot task strip from setup photographs and the T5 demo frame."""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

import pymupdf
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT, GAP = 495.0, 80.0, 4.0
PANEL_WIDTH = (WIDTH-5*GAP)/6
PANEL_HEIGHT = PANEL_WIDTH*9/16
INK, MUTED = '#20262D', '#505A64'
TASK_TITLES = [
    ('Conveyor','grasping'), ('Moving-box','placement'),
    ('Turntable','grasping'), ('Toy-car','grasping'),
    ('Tennis-ball','interception'), ('Ramp-cart','grasping'),
]
TASK_CONTEXT = [
    'Linear travel', 'Conveyor translation', 'Circular travel',
    'Planar travel', 'Tabletop roll', 'Cart on incline',
]


def draw(manifest_path: Path, output: Path):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['status'] == 'task_photographs'
    assert set(manifest['panels']) == {f't{i}' for i in range(1,7)}
    output.parent.mkdir(parents=True,exist_ok=True)
    font_root = Path('C:/Windows/Fonts')
    font_files = [('Fig6','arial.ttf',400),('Fig6Bold','arialbd.ttf',700)]
    styles = []
    for name, filename, weight in font_files:
        pdfmetrics.registerFont(TTFont(name,str(font_root/filename)))
        encoded = base64.b64encode((font_root/filename).read_bytes()).decode()
        styles.append(f"@font-face{{font-family:'Arial';font-weight:{weight};src:url(data:font/ttf;base64,{encoded}) format('truetype');}}")
    pdf = canvas.Canvas(str(output.with_suffix('.pdf')),pagesize=(WIDTH,HEIGHT))
    pdf.setTitle('Fig. 7 - real-robot task setups')
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="6.875in" height="{HEIGHT/72:.6f}in" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<title>Fig. 7: six real-robot task setups</title>',
        '<desc>One row of real-robot task images from photographs and a T5 demo frame. Sources are recorded in manifest.json.</desc>',
        '<defs><style>'+''.join(styles)+'</style></defs>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="white"/>',
    ]
    images, text_bounds, font_sizes = [], [], []

    def text(x,y,value,size=8,color=INK,bold=False,anchor='start'):
        font = 'Fig6Bold' if bold else 'Fig6'
        width = pdfmetrics.stringWidth(value,font,size)
        left = x-width/2 if anchor=='middle' else x
        assert left >= -0.01 and left+width <= WIDTH+0.01, value
        assert y-size >= -0.01 and y+size*.25 <= HEIGHT, value
        pdf.setFillColor(color)
        pdf.setFont(font,size)
        pdf.drawString(left,HEIGHT-y,value)
        svg.append(f'<text x="{x}" y="{y}" font-family="Arial" font-size="{size}" font-weight="{700 if bold else 400}" text-anchor="{anchor}" fill="{color}">{escape(value)}</text>')
        text_bounds.append({'text':value,'bbox':[left,y-size,left+width,y+size*.25],'size_pt':size})
        font_sizes.append(size)

    for i, ((first,second),context) in enumerate(zip(TASK_TITLES,TASK_CONTEXT)):
        task = f't{i+1}'
        panel = manifest['panels'][task]
        assert panel['status'] == 'task_photo'
        x, top = i*(PANEL_WIDTH+GAP), 21.0
        text(x,8,task.upper(),7.5,MUTED,True)
        text(x+14,8,first,8,bold=True)
        text(x+14,16.5,second)
        path = ROOT/panel['image']
        with Image.open(path) as image:
            image.load()
            assert image.mode == 'RGB' and image.width*9 == image.height*16
            source_px = list(image.size)
            # Use a multiple of 16 for an exact 16:9 embedded raster at >=600 ppi.
            embedded_width = math.ceil(PANEL_WIDTH/72*600/16)*16
            embedded_height = embedded_width*9//16
            assert image.width >= embedded_width
            embedded = image.resize((embedded_width,embedded_height),Image.Resampling.LANCZOS)
        stream = io.BytesIO()
        embedded.save(stream,format='PNG')
        data = stream.getvalue()
        svg.append(f'<image id="{task}" x="{x}" y="{top}" width="{PANEL_WIDTH}" height="{PANEL_HEIGHT}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{base64.b64encode(data).decode()}"/>')
        pdf.drawImage(ImageReader(io.BytesIO(data)),x,HEIGHT-top-PANEL_HEIGHT,PANEL_WIDTH,PANEL_HEIGHT)
        text(x+PANEL_WIDTH/2,top+PANEL_HEIGHT+10,context,7.4,MUTED,anchor='middle')
        images.append({'task':task,'path':panel['image'],'source_px':source_px,'embedded_px':[embedded_width,embedded_height],'effective_ppi':embedded_width/(PANEL_WIDTH/72)})
    pdf.showPage()
    pdf.save()
    svg.append('</svg>')
    output.with_suffix('.svg').write_text('\n'.join(svg),encoding='utf-8',newline='\n')
    with pymupdf.open(output.with_suffix('.pdf')) as document:
        for dpi,suffix in [(600,''),(144,'_screen'),(96,'_96ppi')]:
            pix = document[0].get_pixmap(dpi=dpi,alpha=False)
            image = Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
            image.save(output.with_name(output.name+suffix).with_suffix('.png'),dpi=(dpi,dpi))
        fonts = document[0].get_fonts()
    report = {'width_in':WIDTH/72,'height_in':HEIGHT/72,'panels':len(images),
              'panel_size_pt':[PANEL_WIDTH,PANEL_HEIGHT],'aspect':16/9,
              'min_font_pt':min(font_sizes),'font':'Arial','pdf_fonts':fonts,
              'raster_dpi':600,'images':images,'text_bounds':text_bounds,
              'status':manifest['status']}
    output.with_suffix('.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ['width_in','height_in','panels','min_font_pt','status']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest',type=Path,default=ROOT/'manifest.json')
    parser.add_argument('--output',type=Path,default=ROOT/'outputs/polished/fig6')
    args = parser.parse_args()
    draw(args.manifest,args.output)
