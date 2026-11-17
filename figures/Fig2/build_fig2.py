"""Export the adopted Fig2 PowerPoint as PDF, SVG, and manuscript previews."""

import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import fitz


ROOT = Path(__file__).resolve().parent
PAPER_WIDTH_PT = 495.0
PRESENTATION_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
SVG_NS = "http://www.w3.org/2000/svg"
DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
POWERPOINT_EXPORT = r"""
$ErrorActionPreference = 'Stop'
$application = $null
$presentation = $null
$initialCount = 0
try {
    $application = New-Object -ComObject PowerPoint.Application
    $initialCount = $application.Presentations.Count
    $presentation = $application.Presentations.Open($env:FOVEAWAM_FIG2_SOURCE, -1, 0, 0)
    if ($presentation.Slides.Count -ne 1) { throw 'Fig2 requires one slide.' }
    $presentation.SaveAs($env:FOVEAWAM_FIG2_NATIVE_PDF, 32)
} finally {
    if ($null -ne $presentation) {
        $presentation.Close()
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($presentation)
    }
    if ($null -ne $application) {
        if ($initialCount -eq 0) { $application.Quit() }
        [void][Runtime.InteropServices.Marshal]::ReleaseComObject($application)
    }
}
"""


def preserve_noise_pixels(deck_path, page):
    """Restore source PNG pixels after Office's unavoidable PDF downsampling.

    Only the two existing image XObjects change; their placement matrices and
    the native borders stay intact. PDF interpolation is explicitly disabled.
    """
    ns = {"p": PRESENTATION_NS, "a": DRAWING_NS}
    with ZipFile(deck_path) as deck:
        slide = ET.fromstring(deck.read("ppt/slides/slide1.xml"))
        presentation = ET.fromstring(deck.read("ppt/presentation.xml"))
    unit = PAPER_WIDTH_PT / int(presentation.find("p:sldSz", ns).get("cx"))
    groups = {g.find("p:nvGrpSpPr/p:cNvPr", ns).get("name"): g
              for g in slide.findall(".//p:grpSp", ns)}
    images = page.get_image_info(xrefs=True)
    for group_name, label in (("action-noise", "noisy_actions_A"), ("inference-noise", "inference_noise")):
        transform = groups[group_name].find("p:grpSpPr/a:xfrm", ns)
        off, ext = transform.find("a:off", ns), transform.find("a:ext", ns)
        x, y = int(off.get("x")), int(off.get("y"))
        w, h = int(ext.get("cx")), int(ext.get("cy"))
        expected = fitz.Rect(x * unit, y * unit, (x + w) * unit, (y + h) * unit)
        matches = [image for image in images if max(abs(a - b) for a, b in zip(image["bbox"], expected)) < .05]
        if len(matches) != 1:
            raise ValueError(f"Expected one exported image for {label}")
        xref = matches[0]["xref"]
        page.replace_image(xref, stream=(ROOT / "assets/icons_v28" / f"{label}.png").read_bytes())
        page.parent.xref_set_key(xref, "Interpolate", "false")


def inspect_v28(deck_path, page, drawings, image_info):
    """Check the native icons and lossless, non-interpolated noise in the PDF."""
    ns = {"p": PRESENTATION_NS, "a": DRAWING_NS}
    with ZipFile(deck_path) as deck:
        slide = ET.fromstring(deck.read("ppt/slides/slide1.xml"))
        presentation = ET.fromstring(deck.read("ppt/presentation.xml"))
        slide_width = int(presentation.find("p:sldSz", ns).get("cx"))
        unit = PAPER_WIDTH_PT / slide_width
        parents = {child: parent for parent in slide.iter() for child in parent}

        def slide_bounds(shape, x, y, w, h):
            parent = parents[shape]
            while parent.tag == f"{{{PRESENTATION_NS}}}grpSp":
                transform = parent.find("p:grpSpPr/a:xfrm", ns)
                off, ext = transform.find("a:off", ns), transform.find("a:ext", ns)
                child_off, child_ext = transform.find("a:chOff", ns), transform.find("a:chExt", ns)
                sx, sy = int(ext.get("cx")) / int(child_ext.get("cx")), int(ext.get("cy")) / int(child_ext.get("cy"))
                x, y = (x - int(child_off.get("x"))) * sx + int(off.get("x")), (y - int(child_off.get("y"))) * sy + int(off.get("y"))
                w, h = w * sx, h * sy
                parent = parents[parent]
            return [x, y, w, h]
        groups = {g.find("p:nvGrpSpPr/p:cNvPr", ns).get("name"): g
                  for g in slide.findall(".//p:grpSp", ns)}
        robots = {}
        for label, pose in (("robot-state", "p2"), ("action-chunk-1", "p1"),
                            ("action-chunk-2", "p2"), ("action-chunk-3", "p3"),
                            ("inference-action-chunk", "p2")):
            group = groups[label]
            shapes = group.findall("p:sp", ns)
            assert len(shapes) == 18 and not group.findall(".//p:pic", ns), label
            assert all(f" v28 {pose} " in s.find("p:nvSpPr/p:cNvPr", ns).get("name") for s in shapes)
            transform = group.find("p:grpSpPr/a:xfrm", ns)
            off, ext = transform.find("a:off", ns), transform.find("a:ext", ns)
            x, y = int(off.get("x")), int(off.get("y"))
            w, h = int(ext.get("cx")), int(ext.get("cy"))
            x, y, w, h = slide_bounds(group, x, y, w, h)
            rect = fitz.Rect(x * unit, y * unit, (x + w) * unit, (y + h) * unit)
            vector_count = sum(rect.contains(drawing["rect"]) for drawing in drawings)
            bitmap_count = sum(rect.intersects(image["bbox"]) for image in image_info)
            assert vector_count >= 18 and bitmap_count == 0, label
            robots[label] = {"asset": f"robot_arm_{pose}.svg", "native_vector_shapes": len(shapes),
                             "pdf_vector_paths_in_bounds": vector_count,
                             "pdf_image_placements_in_bounds": bitmap_count,
                             "bounds_emu": [x, y, w, h]}
        noise = {}
        for label in ("noisy_actions_A", "inference_noise"):
            asset = ROOT / "assets/icons_v28" / f"{label}.png"
            raw = asset.read_bytes()
            assert deck.read(f"ppt/media/{label}_v28.png") == raw
            pic = next(pic for pic in slide.findall(".//p:pic", ns)
                       if pic.find("p:nvPicPr/p:cNvPr", ns).get("name") == label)
            transform = pic.find("p:spPr/a:xfrm", ns)
            off, ext = transform.find("a:off", ns), transform.find("a:ext", ns)
            x, y = int(off.get("x")), int(off.get("y"))
            w, h = int(ext.get("cx")), int(ext.get("cy"))
            x, y, w, h = slide_bounds(pic, x, y, w, h)
            expected = fitz.Rect(x * unit, y * unit, (x + w) * unit, (y + h) * unit)
            matches = [info for info in image_info
                       if max(abs(a - b) for a, b in zip(info["bbox"], expected)) < .05]
            assert len(matches) == 1, label
            info = matches[0]
            original, exported = fitz.Pixmap(raw), fitz.Pixmap(page.parent, info["xref"])
            original = fitz.Pixmap(fitz.csRGB, original)
            exported = fitz.Pixmap(fitz.csRGB, exported)
            assert (exported.width, exported.height) == (640, 640), label
            assert exported.samples == original.samples, f"Noise pixels changed in PDF: {label}"
            interpolation = page.parent.xref_get_key(info["xref"], "Interpolate")
            assert interpolation in (("null", "null"), ("bool", "false")), interpolation
            noise[label] = {"grid": [32, 32], "png_pixels": [640, 640],
                            "bounds_emu": [x, y, w, h], "pdf_pixels_match_source": True,
                            "pdf_interpolate": False, "source_sha256": hashlib.sha256(raw).hexdigest(),
                            "border": "original native border preserved"}
        small_noise = [s for s in slide.findall(".//p:sp", ns)
                       if s.find("p:nvSpPr/p:cNvPr", ns).get("name").startswith("Noise ")
                       and s.find("p:spPr/a:xfrm/a:ext", ns).get("cx") in ("22622", "13097")]
        assert not small_noise
        assert len(image_info) == 7
        return {"pptx_native_shapes": len(slide.findall(".//p:sp", ns)),
                "native_noise_rectangles": len(small_noise), "noise_rectangles_removed_from_v27": 2048,
                "robot_icons": robots, "noise_patches": noise}


def build() -> None:
    source = ROOT / "fig2_se3wam.pptx"
    with TemporaryDirectory(prefix=".fig2_export_", dir=ROOT) as temporary:
        staging = Path(temporary)
        input_copy = staging / source.name
        shutil.copyfile(source, input_copy)
        with ZipFile(input_copy) as deck:
            presentation = ET.fromstring(deck.read("ppt/presentation.xml"))
        slide_size = presentation.find(f"{{{PRESENTATION_NS}}}sldSz")
        if slide_size is None:
            raise ValueError("Fig2 PowerPoint is missing its slide size.")
        paper_height = PAPER_WIDTH_PT * int(slide_size.attrib["cy"]) / int(slide_size.attrib["cx"])
        native_pdf = staging / "powerpoint.pdf"
        subprocess.run(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", POWERPOINT_EXPORT],
            env={**os.environ, "FOVEAWAM_FIG2_SOURCE": str(input_copy),
                 "FOVEAWAM_FIG2_NATIVE_PDF": str(native_pdf)},
            check=True,
        )

        pdf_path = staging / "fig2_se3wam.pdf"
        with fitz.open(native_pdf) as native, fitz.open() as output:
            page = output.new_page(width=PAPER_WIDTH_PT, height=paper_height)
            page.show_pdf_page(page.rect, native, 0)
            preserve_noise_pixels(input_copy, page)
            output.set_metadata({"title": "FoveaWAM architecture"})
            output.save(pdf_path, garbage=4, deflate=True)

        previews = {"fig2_se3wam.png": 300, "fig2_se3wam_600dpi.png": 600,
                    "fig2_paper_width.png": 144}
        svg_path = staging / "fig2_se3wam.svg"
        with fitz.open(pdf_path) as figure:
            page = figure[0]
            drawings = page.get_drawings()
            vector_paths = len(drawings)
            image_info = page.get_image_info(xrefs=True)
            if not vector_paths or not page.get_text().strip():
                raise ValueError("Fig2 export must contain vector shapes and text.")
            svg = ET.fromstring(page.get_svg_image(text_as_path=False))
            ET.register_namespace("", SVG_NS)
            ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
            svg.set("width", f"{PAPER_WIDTH_PT:g}pt")
            svg.set("height", f"{paper_height:g}pt")
            ET.ElementTree(svg).write(svg_path, encoding="utf-8", xml_declaration=True)
            for name, dpi in previews.items():
                page.get_pixmap(dpi=dpi, alpha=False).save(staging / name)
            report = {
                "release": "v28",
                "editable_source": source.name,
                "renderer": "Microsoft PowerPoint PDF export",
                "paper_size_pt": [PAPER_WIDTH_PT, paper_height],
                "pdf_vector_paths": vector_paths,
                "pdf_image_placements": len(image_info),
                "svg_text_elements": len(svg.findall(f".//{{{SVG_NS}}}text")),
                **inspect_v28(input_copy, page, drawings, image_info),
            }
        if source.read_bytes() != input_copy.read_bytes():
            raise RuntimeError("Fig2 PowerPoint changed during export. Run the build again.")
        report_path = staging / "export_report.json"
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        for path in [pdf_path, svg_path, *(staging / name for name in previews), report_path]:
            path.replace(ROOT / path.name)
        print(json.dumps(report))


if __name__ == "__main__":
    build()
