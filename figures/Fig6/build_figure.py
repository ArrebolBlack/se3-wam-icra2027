"""Build the Fig. 6 task photographs at the paper's two figure widths."""
from __future__ import annotations

import argparse
import base64
import io
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import pymupdf
from PIL import Image
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / 'scripts'))
import motion_arrow as motion
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
# Tail to tip in an 800 x 450 reference view of the 16:9 photos.
# See INTEGRATION.md for the source clips and view correspondence.
MOTION_PATHS = {
    "t1": ((727, 363), (524, 318)),
    "t2": ((752, 344), (594, 286)),
    "t3": ((562, 294), (397, 374), (232, 294)),
    "t4": ((60, 350), (205, 301)),
    "t5": ((714, 322), (532, 329)),
    "t6": ((97, 220), (301, 279)),
}
MOTION_TYPES = {"t4": "Planar motion", "t5": "Rolling"}
LABEL_COLOR = "#FFFFFF"


def motion_centerline(points, x, y, width, height):
    """Map photo coordinates to final print points; sample the quadratic arc."""
    positions = [(x + u * width / 800, y + v * height / 450) for u, v in points]
    if len(positions) == 3:
        start, mid, end = positions
        return [tuple((1 - t) ** 2 * a + 2 * (1 - t) * t * b + t * t * c
                      for a, b, c in zip(start, mid, end)) for t in (i / 64 for i in range(65))]
    return positions


def draw_motion(pdf, svg, points, page_height, *, centerline, double_headed=False):
    path = pdf.beginPath()
    path.moveTo(points[0][0], page_height - points[0][1])
    for px, py in points[1:]:
        path.lineTo(px, page_height - py)
    path.close()
    pdf.setLineJoin(1)
    pdf.setStrokeColor("#FFFFFF")
    pdf.setFillColor("#FFFFFF")
    pdf.setLineWidth(2 * motion.RIM)
    pdf.drawPath(path, stroke=1, fill=1)
    pdf.setFillColor(motion.MOTION_COLOR)
    pdf.drawPath(path, stroke=0, fill=1)
    svg.append(ET.tostring(motion.svg_group(centerline, double_headed=double_headed), encoding="unicode"))


def draw(manifest_path: Path, output: Path, layout: str = "wide", *, editable: bool = False):
    if editable and layout != "single-column":
        raise ValueError("The editable PPTX uses the single-column layout.")
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
    description = "Task setup photographs and one tennis ball interception demonstration frame."
    if not wide:
        regular_path = font_path.with_name("arial.ttf")
        pdfmetrics.registerFont(TTFont("Fig6Regular", str(regular_path)))
        regular_data = base64.b64encode(regular_path.read_bytes()).decode("ascii")
        description = "Task photographs with example motion directions and a double-headed arc for turntable rotation."
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width / 72:.8f}in"'
        f' height="{height / 72:.8f}in" viewBox="0 0 {width} {height}">',
        f"<title>{TITLE}</title>",
        f"<desc>{description}</desc>",
        f"<defs><style>@font-face{{font-family:Arial;font-weight:{label_weight};src:url(data:font/ttf;base64,"
        f"{font_data}) format('truetype');}}</style></defs>",
    ]
    if not wide:
        svg.insert(-1, "<defs><style>@font-face{font-family:Arial;font-weight:400;"
                   f"src:url(data:font/ttf;base64,{regular_data}) format('truetype');}}</style></defs>")
    images, text_bounds, arrows, slide_images = [], [], [], []
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
        slide_images.append((data, x, top, panel_width, panel_height))
        if not wide:
            centerline = motion_centerline(MOTION_PATHS[task], x, top, panel_width, panel_height)
            outline = motion.arrow_outline(centerline, double_headed=task == "t3")
            draw_motion(pdf, svg, outline, height, centerline=centerline, double_headed=task == "t3")
            arrows.append({"task": task, "outline": outline, "centerline": centerline,
                           "head_length_pt": motion.head_length(centerline, double_headed=task == "t3")})
            if task == "t5":
                label = "Ball Intercept"
        label_width = pdfmetrics.stringWidth(label, "Fig6", label_size)
        label_x = x + (panel_width - label_width) / 2 if wide else x + 4
        baseline = 7.5 if wide else top + panel_height - 3.7
        color = "#444444" if wide else LABEL_COLOR
        if not wide:
            if task in MOTION_TYPES:
                motion_label = MOTION_TYPES[task]
                motion_size = 7.5
                motion_width = pdfmetrics.stringWidth(motion_label, "Fig6Regular", motion_size)
                motion_x = x + panel_width - 4 - motion_width
                assert label_x + label_width + 4 < motion_x
                pdf.saveState()
                pdf.setFont("Fig6Regular", motion_size)
                pdf.setFillColor(color)
                pdf.drawString(motion_x, height - baseline, motion_label)
                pdf.restoreState()
                svg.append(
                    f'<text x="{motion_x}" y="{baseline}" font-family="Arial" font-weight="400"'
                    f' font-size="{motion_size}" fill="{color}">{escape(motion_label)}</text>'
                )
                text_bounds.append({
                    "text": motion_label, "bbox": [motion_x, baseline - motion_size,
                                              motion_x + motion_width, baseline + motion_size / 4],
                    "size_pt": motion_size, "color": color, "bold": False,
                    "baseline_pt": baseline,
                })
        pdf.setFillColor(color)
        pdf.drawString(label_x, height - baseline, label)
        svg.append(
            f'<text x="{label_x}" y="{baseline}" font-family="Arial" font-weight="{label_weight}"'
            f' font-size="{label_size}" fill="{color}">{escape(label)}</text>'
        )
        text_bounds.append({
            "text": label, "bbox": [label_x, baseline - label_size,
                                    label_x + label_width, baseline + label_size / 4],
            "size_pt": label_size, "color": color, "bold": not wide,
            "baseline_pt": baseline,
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
        "panels": len(images), "min_font_pt": min(item["size_pt"] for item in text_bounds),
        "font": "Arial", "pdf_fonts": fonts,
        "raster_dpi": 600, "images": images, "text_bounds": text_bounds,
        "status": manifest["status"],
    }
    if not wide:
        report["motion_style"] = motion.style_manifest()
        report["motion_arrows"] = [{"task": a["task"], "centerline_pt": a["centerline"],
                                    "head_length_pt": a["head_length_pt"],
                                    "double_headed": a["task"] == "t3"} for a in arrows]
    output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if editable:
        export_pptx(output.with_name("Fig6-editable.pptx"), width, height,
                    slide_images, arrows, text_bounds)
    print(json.dumps({key: report[key] for key in ("layout", "width_in", "height_in", "panels")}))


def export_pptx(output, width, height, images, arrows, labels):
    """Export the same photographs, editable filled arrows and editable labels."""
    from lxml import etree
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import MSO_ANCHOR
    from pptx.util import Pt

    scale = 3  # Preserve the existing editable slide's physical size.
    presentation = Presentation()
    presentation.slide_width = Pt(width * scale)
    presentation.slide_height = Pt(height * scale)
    presentation.core_properties.title = TITLE
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    for data, x, y, w, h in images:
        slide.shapes.add_picture(io.BytesIO(data), Pt(x * scale), Pt(y * scale),
                                 Pt(w * scale), Pt(h * scale))
    for arrow in arrows:
        points = [tuple(round(v * 1000) for v in point) for point in arrow["outline"]]
        layers = []
        for color, outlined in (("FFFFFF", True), (motion.MOTION_COLOR[1:], False)):
            freeform = slide.shapes.build_freeform(*points[0], scale=12700 * scale / 1000)
            freeform.add_line_segments(points[1:], close=True)
            shape = freeform.convert_to_shape()
            for effect in shape._element.xpath("./p:style/a:effectRef"):
                effect.set("idx", "0")
            shape._element.spPr.append(etree.Element(
                "{http://schemas.openxmlformats.org/drawingml/2006/main}effectLst"))
            shape.fill.solid()
            shape.fill.fore_color.rgb = RGBColor.from_string(color)
            if outlined:
                shape.line.color.rgb = RGBColor.from_string("FFFFFF")
                shape.line.width = Pt(2 * motion.RIM * scale)
                shape.line._get_or_add_ln().append(etree.Element(
                    "{http://schemas.openxmlformats.org/drawingml/2006/main}round"))
            else:
                shape.line.fill.background()
            layers.append(shape)
        group = slide.shapes.add_group_shape(layers)
        group.name = "Arrow - " + TASKS[arrow["task"]]
    for label in labels:
        x, _, right, _ = label["bbox"]
        shape = slide.shapes.add_textbox(
            Pt(x * scale), Pt((label["baseline_pt"] - 7.4) * scale),
            Pt((right - x + 1) * scale), Pt(10 * scale))
        shape.name = "Label " + label["text"]
        frame = shape.text_frame
        frame.word_wrap = False
        frame.vertical_anchor = MSO_ANCHOR.MIDDLE
        frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
        paragraph = frame.paragraphs[0]
        paragraph.space_before = paragraph.space_after = Pt(0)
        run = paragraph.add_run()
        run.text = label["text"]
        run.font.name = "Arial"
        run.font.size = Pt(label["size_pt"] * scale)
        run.font.bold = label["bold"]
        run.font.color.rgb = RGBColor.from_string(label["color"][1:])
    presentation.save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout", choices=LAYOUTS, default="wide")
    parser.add_argument("--manifest", type=Path, default=ROOT / "manifest.json")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--editable", action="store_true", help="Also rebuild the single-column PPTX")
    args = parser.parse_args()
    output = args.output or ROOT / "outputs" / LAYOUTS[args.layout] / "fig6"
    draw(args.manifest, output, args.layout, editable=args.editable)
