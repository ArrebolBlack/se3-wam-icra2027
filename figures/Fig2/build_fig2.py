"""Export the adopted Fig2 PowerPoint as PDF, SVG, and manuscript previews."""

import json
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
            output.set_metadata({"title": "FoveaWAM architecture"})
            output.save(pdf_path, garbage=4, deflate=True)

        previews = {"fig2_se3wam.png": 300, "fig2_se3wam_600dpi.png": 600,
                    "fig2_paper_width.png": 144}
        svg_path = staging / "fig2_se3wam.svg"
        with fitz.open(pdf_path) as figure:
            page = figure[0]
            vector_paths = len(page.get_drawings())
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
                "release": "v25",
                "editable_source": source.name,
                "renderer": "Microsoft PowerPoint PDF export",
                "paper_size_pt": [PAPER_WIDTH_PT, paper_height],
                "pdf_vector_paths": vector_paths,
                "pdf_image_placements": len(page.get_image_info()),
                "svg_text_elements": len(svg.findall(f".//{{{SVG_NS}}}text")),
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
