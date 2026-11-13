"""Build the Fig. 6 task photographs at the paper's two figure widths."""
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
TITLE = "Fig. 6: Real-robot task setups"
# CVPR's 6.875 in text width and (6.875 - 0.3125)/2 in column width.
LAYOUTS = {"wide": "polished", "single-column": "single-column"}
TASKS = {
    "t1": "Conveyor Grasp",
    "t2": "Moving Box Placement",
    "t3": "Turntable Grasp",
    "t4": "Toy Car Grasp",
    "t5": "Tennis Ball Interception",
    "t6": "Ramp Cart Grasp",
}
GAP = 2.5
# Wide panel widths at a common image height, with horizontal crop centers
# chosen to keep the target and task apparatus in view.
WIDE_CROPS = ((77, .53), (85, .56), (77, .50), (72, .49), (77, .50), (94.5, .53))
LABEL_FADE = 13


def draw(manifest_path: Path, output: Path, layout: str = "wide"):
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["status"] == "task_photographs"
    assert set(manifest["panels"]) == set(TASKS)
    wide = layout == "wide"
    width = 495.0 if wide else 236.25
    grid_panel_width = (width - GAP) / 2
    panel_height = 58.0 if wide else grid_panel_width * 9 / 16
    height = panel_height + 11 if wide else 3 * panel_height + 2 * GAP
    label_size = 7.0 if wide else 8.0
    label_weight = 400 if wide else 700
    output.parent.mkdir(parents=True, exist_ok=True)

    font_file = "arial.ttf" if wide else "arialbd.ttf"
    font_path = Path("C:/Windows/Fonts") / font_file
    pdfmetrics.registerFont(TTFont("Fig6", str(font_path)))
    font_data = base64.b64encode(font_path.read_bytes()).decode("ascii")
    pdf = canvas.Canvas(str(output.with_suffix(".pdf")), pagesize=(width, height), invariant=True)
    pdf.setTitle(TITLE)
    pdf.setFont("Fig6", label_size)
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width / 72:.8f}in"'
        f' height="{height / 72:.8f}in" viewBox="0 0 {width} {height}">',
        f"<title>{TITLE}</title>",
        "<desc>Task setup photographs and one tennis ball interception demonstration frame.</desc>",
        f"<defs><style>@font-face{{font-family:Arial;font-weight:{label_weight};src:url(data:font/ttf;base64,"
        f"{font_data}) format('truetype');}}</style></defs>",
    ]
    if not wide:
        # DemoGen's dark labels sit on a light tabletop. Lift the lower edge
        # here so the labels remain legible against six different backgrounds.
        fade = Image.new("RGBA", (1, 128))
        fade.putdata([(255, 255, 255, round(224 * y / 127)) for y in range(128)])
        fade_reader = ImageReader(fade)
        svg.append(
            '<defs><linearGradient id="label-fade" x1="0" x2="0" y1="0" y2="1">'
            '<stop offset="0" stop-color="white" stop-opacity="0"/>'
            '<stop offset="1" stop-color="white" stop-opacity="0.878"/>'
            '</linearGradient></defs>'
        )
    images, text_bounds = [], []
    x = 0.0
    for i, (task, label) in enumerate(TASKS.items()):
        panel = manifest["panels"][task]
        assert panel["status"] == "task_photo"
        if wide:
            panel_width, center = WIDE_CROPS[i]
            top = 11.0
        else:
            row, column = divmod(i, 2)
            panel_width = grid_panel_width
            x = column * (panel_width + GAP)
            top = row * (panel_height + GAP)
        path = ROOT / panel["image"]
        with Image.open(path) as image:
            assert image.mode == "RGB" and image.width * 9 == image.height * 16, path
            source_px = list(image.size)
            if wide:
                crop_width = round(image.height * panel_width / panel_height)
                left = round(center * image.width - crop_width / 2)
                assert 0 <= left and left + crop_width <= image.width, path
                crop = (left, 0, left + crop_width, image.height)
            else:
                crop = (0, 0, image.width, image.height)
            embedded_height = min(image.height, math.ceil(panel_height / 72 * 600))
            embedded_width = round(embedded_height * panel_width / panel_height)
            embedded = image.resize(
                (embedded_width, embedded_height), Image.Resampling.LANCZOS, box=crop
            )
        stream = io.BytesIO()
        embedded.save(stream, format="PNG")
        data = stream.getvalue()
        svg.append(
            f'<image id="{task}" x="{x}" y="{top}" width="{panel_width}" height="{panel_height}"'
            f' preserveAspectRatio="none" href="data:image/png;base64,{base64.b64encode(data).decode()}"/>'
        )
        pdf.drawImage(
            ImageReader(io.BytesIO(data)), x, height - top - panel_height, panel_width, panel_height
        )
        label_width = pdfmetrics.stringWidth(label, "Fig6", label_size)
        label_x = x + (panel_width - label_width) / 2 if wide else x + 4
        baseline = 7.5 if wide else top + panel_height - 4
        color = "#444444" if wide else "#151515"
        pdf.setFillColor(color)
        if not wide:
            bottom = top + panel_height
            pdf.drawImage(fade_reader, x, height - bottom, panel_width, LABEL_FADE, mask="auto")
            svg.append(
                f'<rect x="{x}" y="{bottom - LABEL_FADE}" width="{panel_width}"'
                f' height="{LABEL_FADE}" fill="url(#label-fade)"/>'
            )
        pdf.drawString(label_x, height - baseline, label)
        svg.append(
            f'<text x="{label_x}" y="{baseline}" font-family="Arial" font-weight="{label_weight}"'
            f' font-size="{label_size}" fill="{color}">{escape(label)}</text>'
        )
        text_bounds.append({
            "text": label, "bbox": [label_x, baseline - label_size,
                                    label_x + label_width, baseline + label_size / 4],
            "size_pt": label_size,
        })
        images.append({
            "task": label, "path": panel["image"], "source_px": source_px, "crop_px": crop,
            "panel_size_pt": [panel_width, panel_height],
            "embedded_px": [embedded_width, embedded_height],
            "effective_ppi": min(embedded_width / panel_width, embedded_height / panel_height) * 72,
        })
        x += panel_width + GAP
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
    report = {
        "layout": layout, "width_in": width / 72, "height_in": height / 72,
        "panels": len(images), "min_font_pt": label_size, "font": "Arial", "pdf_fonts": fonts,
        "raster_dpi": 600, "images": images, "text_bounds": text_bounds,
        "status": manifest["status"],
    }
    output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("layout", "width_in", "height_in", "panels")}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", choices=LAYOUTS, default="wide")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifest.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or ROOT / "outputs" / LAYOUTS[args.layout] / "fig6"
    draw(args.manifest, output, args.layout)
