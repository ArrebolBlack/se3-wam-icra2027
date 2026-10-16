"""Draw eight recorded benchmark observations from the accepted P15 DEV84 archive.

The task subset spans the reference, three T1 conditions, and T2--T5. For each
task, choose its lowest state index in the original generation manifest. Export
the last observed RGB without cropping, recoloring, or synthesizing pixels.
These are observation examples, not outcomes or model predictions.

Requires numpy, Pillow, reportlab, pypdf and pypdfium2. The source is read only.
The PDF is 6.875 inches wide; the smallest text is 8.25 pt at that width.
"""

from pathlib import Path
import argparse
import base64
import io
import json
import tarfile
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image
from pypdf import PdfReader
import pypdfium2 as pdfium
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


ROOT = Path(__file__).resolve().parent
REVIEW = ROOT.parent / "tmp" / "benchmark-task-review"
DEFAULT_ARCHIVE = Path(
    "C:/workspace/se3-wam-research/local_private/future0-aux-20261012/"
    "P15-archive-aux-p15-reports-a36-low-priority-4g-a1-a1/"
    "reports-downloaded-20261013T110014343027Z.tar"
)
ACCEPTANCE = (
    "C:/workspace/se3-wam-research/docs/experiments/FUTURE0/results/"
    "auxiliary_supervision/P15_complete_report_archive_20261013.json"
)
TASKS = (
    ("p0_grasp", "Reference grasp", "Moving cuboid"),
    ("t1_belt", "T1 · Translation", "Moving target"),
    ("t1_occ", "T1 · Occlusion", "Physical occluder"),
    ("t1_so3", "T1 · Rotation", "Orientation-sensitive grasp"),
    ("t2_se3", "T2 · Placement", "Moving receptacle"),
    ("t3_full", "T3 · Passage", "Full passage constraints"),
    ("t4_can", "T4 · Capture", "Moving can"),
    ("t5_replan", "T5 · Replanning", "Post-impact adaptation"),
)
ALL_TASKS = (
    "p0_grasp", "t1_belt", "t1_occ", "t1_so3", "t1_xyz", "t2_se3",
    "t2_trans", "t3_full", "t3_phase", "t4_can", "t4_slider", "t4_sphere",
    "t4_sphere_tabletop", "t5_replan",
)
W, H = 660, 408
IMAGE_SIDE, COLUMN_STEP, ROW_STEP = 154, 168, 210
INK, MUTED, BORDER = "#20262D", "#4D555F", "#C8CDD2"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(archive, member):
    return json.load(archive.extractfile(member))


def load_data(path):
    with tarfile.open(path) as archive:
        accepted = read_json(archive, "evaluation/accepted.json")
        dev = read_json(archive, "evaluation/dev/accepted.json")
        epoch = read_json(archive, "control/epoch4.json")
        manifest = read_json(archive, "evaluation/dev/generation-manifest.json")
        require(accepted["accepted"] and accepted["arm"] == "P15", "expected accepted P15")
        require(accepted["completed_epochs"] == epoch["epoch"] == 4, "expected epoch 4")
        require(accepted["optimizer_step"] == epoch["optimizer_step"] == 40104,
                "expected original accepted endpoint")
        require(dev["accepted"] and (dev["states"], dev["episodes"], dev["tasks"]) == (84, 28, 14),
                "expected accepted DEV84")
        samples = manifest["samples"]
        require(manifest["complete"] and len(samples) == 84, "incomplete generation manifest")
        require(set(s["task"] for s in samples) == set(ALL_TASKS), "unexpected task identities")
        selected = []
        for panel, (task, title, interaction) in enumerate(TASKS):
            index = next(i for i, sample in enumerate(samples) if sample["task"] == task)
            sample = samples[index]
            member = f"evaluation/dev/inputs/state-{index:03}.npz"
            with np.load(io.BytesIO(archive.extractfile(member).read()), allow_pickle=False) as z:
                require(z["rgb"].shape == (1, 8, 1, 3, 224, 224), "unexpected RGB tensor shape")
                require(z["rgb"].dtype == np.uint8, "expected original uint8 RGB")
                require(z["observed_frame_indices"][-1] == sample["frame"],
                        f"state {index}: manifest and last observed frame differ")
                rgb = z["rgb"][0, -1, 0].transpose(1, 2, 0).copy()
                timestamp = float(z["observed_timestamp_s"][-1])
            selected.append(dict(panel=chr(97 + panel), task=task, title=title,
                                 interaction=interaction, state_index=index, sample=sample,
                                 input_member=member, current_time_s=timestamp, rgb=rgb))
    return selected, epoch


def export_sources(path, selected, epoch):
    frames = ROOT / "benchmark_frames"
    frames.mkdir(exist_ok=True)
    for row in selected:
        out = frames / f"dev84_p15_state{row['state_index']:03}.png"
        Image.fromarray(row["rgb"]).save(out, format="PNG")
        require(np.array_equal(np.asarray(Image.open(out)), row["rgb"]),
                "PNG pixel round-trip changed the source observation")
        row["png"] = out
    source = dict(
        source_archive=str(path.resolve()), research_acceptance=ACCEPTANCE,
        source_members=["evaluation/accepted.json", "evaluation/dev/accepted.json",
                        "control/epoch4.json", "evaluation/dev/generation-manifest.json"],
        archive_run_id=epoch["run_id"], archive_arm="P15", archive_endpoint_epoch=4,
        archive_endpoint_optimizer_step=40104, source_states=84, source_episodes=28,
        source_tasks=14, full_task_list=list(ALL_TASKS),
        task_subset_rule="Reference grasp, T1 translation/occlusion/rotation, and one task from each "
                         "of T2 (t2_se3), T3 (t3_full), T4 (t4_can), T5 (t5_replan).",
        state_selection_rule="Within each listed task, choose the lowest zero-based state index "
                             "in evaluation/dev/generation-manifest.json. No image-quality, "
                             "prediction-error, contact-event, or success-based filtering.",
        image_definition="Last observed agentview RGB: rgb[0, -1, 0].transpose(1, 2, 0) from each "
                         "original NPZ (shape [1,8,1,3,224,224], uint8). PNGs preserve all 224x224 "
                         "source pixels; no crop, enhancement, synthetic pixels, or overlays.",
        scope="Recorded benchmark observation examples. Task labels identify the task condition; "
              "a single frame does not establish motion, contact, task success, model performance, "
              "or closed-loop execution. These inputs are independent of the displayed archive's "
              "model predictions.",
        layout=dict(width_inches=W / 96, height_inches=H / 96, columns=4, rows=2,
                    image_display_inches=IMAGE_SIDE / 96, smallest_font_pt=8.25),
        selected=[dict(panel=r["panel"], task=r["task"], title=r["title"],
                       interaction=r["interaction"], state_index=r["state_index"],
                       sample=r["sample"], current_time_s=r["current_time_s"],
                       input_member=r["input_member"],
                       png=r["png"].relative_to(ROOT).as_posix()) for r in selected],
    )
    (ROOT / "benchmark_task_examples_source.json").write_text(
        json.dumps(source, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def draw(selected):
    pdfmetrics.registerFont(TTFont("TaskArial", "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(TTFont("TaskArialBold", "C:/Windows/Fonts/arialbd.ttf"))
    out = ROOT / "benchmark_task_examples.pdf"
    pdf = canvas.Canvas(str(out), pagesize=(W * .75, H * .75), pageCompression=1)
    pdf.setTitle("Recorded benchmark task observations")
    pdf.setSubject("Eight original DEV84 RGB observations, selected by lowest state index per task")
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="Arial, Helvetica, sans-serif">']

    def label(x, y, value, size, bold=False, color=INK):
        font = "TaskArialBold" if bold else "TaskArial"
        require(pdfmetrics.stringWidth(value, font, size) <= IMAGE_SIDE,
                f"label exceeds panel width: {value}")
        svg.append(f'<text x="{x:g}" y="{y:g}" font-size="{size:g}" '
                   f'font-weight="{"bold" if bold else "normal"}" fill="{color}">'
                   f'{escape(value)}</text>')
        pdf.setFont(font, size * .75)
        pdf.setFillColor(color)
        pdf.drawString(x * .75, (H - y) * .75, value)

    for i, row in enumerate(selected):
        x, y = 1 + COLUMN_STEP * (i % 4), ROW_STEP * (i // 4)
        label(x, y + 12, f"({row['panel']}) {row['title']}", 12, bold=True)
        top = y + 22
        payload = base64.b64encode(row["png"].read_bytes()).decode("ascii")
        svg.append(f'<image x="{x}" y="{top}" width="{IMAGE_SIDE}" height="{IMAGE_SIDE}" '
                   f'href="data:image/png;base64,{payload}"/>')
        svg.append(f'<rect x="{x}" y="{top}" width="{IMAGE_SIDE}" height="{IMAGE_SIDE}" '
                   f'fill="none" stroke="{BORDER}" stroke-width="0.5"/>')
        pdf.drawImage(ImageReader(row["png"].as_posix()), x * .75,
                      (H - top - IMAGE_SIDE) * .75, IMAGE_SIDE * .75, IMAGE_SIDE * .75)
        pdf.setStrokeColor(BORDER)
        pdf.setLineWidth(.375)
        pdf.rect(x * .75, (H - top - IMAGE_SIDE) * .75,
                 IMAGE_SIDE * .75, IMAGE_SIDE * .75, fill=0, stroke=1)
        label(x, y + 192, row["interaction"], 11, color=MUTED)
    svg += ["</g>", "</svg>"]
    (ROOT / "benchmark_task_examples.svg").write_text("\n".join(svg) + "\n", encoding="utf-8")
    pdf.showPage()
    pdf.save()
    return out


def verify_and_render(pdf_path, selected):
    doc = PdfReader(pdf_path)
    require(len(doc.pages) == 1, "expected one PDF page")
    page = doc.pages[0]
    require(abs(float(page.mediabox.width) - W * .75) < .01 and
            abs(float(page.mediabox.height) - H * .75) < .01, "incorrect print dimensions")
    for row in selected:
        require(row["interaction"] in page.extract_text(), "missing PDF text")
    embedded = [np.asarray(item.image.convert("RGB")) for item in page.images]
    require(len(embedded) == 8, "expected eight embedded raster images")
    for row in selected:
        require(any(np.array_equal(item, row["rgb"]) for item in embedded),
                f"state {row['state_index']}: PDF did not preserve original pixels")
    REVIEW.mkdir(parents=True, exist_ok=True)
    render = pdfium.PdfDocument(pdf_path)
    for suffix, dpi in (("_actual_size", 96), ("", 240)):
        render[0].render(scale=dpi / 72).to_pil().save(
            REVIEW / f"benchmark_task_examples{suffix}.png")
    render.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    args = parser.parse_args()
    selected, epoch = load_data(args.archive)
    export_sources(args.archive, selected, epoch)
    out = draw(selected)
    verify_and_render(out, selected)
    print(json.dumps(dict(pdf=str(out), svg=str(out.with_suffix(".svg")),
                         states=[dict(task=r["task"], state=r["state_index"],
                                      episode=r["sample"]["episode"], frame=r["sample"]["frame"])
                                 for r in selected],
                         print_inches=[W / 96, H / 96], smallest_font_pt=8.25,
                         source_pixels_verified_in_png_and_pdf=True), indent=2))


if __name__ == "__main__":
    main()
