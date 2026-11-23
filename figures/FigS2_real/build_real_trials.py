"""Build Figure S2 and its S1/S2 spread from selected full video frames."""

import argparse
from dataclasses import dataclass
from math import hypot, isclose
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

import fitz
from PIL import Image
from reportlab import rl_config
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


HERE = Path(__file__).resolve().parent
SOURCE_DIR = Path('D:/workspace/se3-wam-research/local_private/real-robot-demo')
REFERENCE = HERE.parent / 'FigS6' / 'rollouts.pdf'
ARIAL_BOLD = Path('C:/Windows/Fonts/arialbd.ttf')
ORIGINAL_SIZE = (1920, 1080)
PDF_FRAME_SIZE = (1152, 648)
FONT = 'Arial Bold'
WIDTH = 495.0
CELL_WIDTH = 69.7
CELL_HEIGHT = CELL_WIDTH * 9 / 16
ROW_GAP = 1.9
TASK_GAP = 9.0
TASK_HEIGHT = 2 * CELL_HEIGHT + ROW_GAP
TEXT_SIZE = 5.4
TITLE_SIZE = 9.2
TITLE_RIGHT = 105.0
FACE_SIZE = 6.2
CAP_HEIGHT = 0.7163  # Arial Bold capital height in em units.
ROW_COLORS = (HexColor('#3DDC6A'), HexColor('#FF4D4D'))


@dataclass(frozen=True)
class Row:
    video: str
    indices: tuple[int, int, int, int, int]
    method: tuple[float, float]
    target: tuple[float, float]
    callout: tuple[float, float]
    outcome: tuple[float, float]
    note: str


@dataclass(frozen=True)
class Task:
    name: str
    annotation_column: int
    radius: float
    rows: tuple[Row, Row]


# Frame indices count from zero. Positions are relative to each full frame.
# Method and callout offsets are in pt. Target centres are fractions of width and
# height, and outcome offsets are the margins from the right and bottom edges.
TASKS = (
    Task('Conveyor grasp', 3, 5.0, (
        Row('2026-11-14/T1_传送带抓取/成功/VID_20261114_215131.mp4', (131, 155, 164, 179, 200),
            (2.0, 10.0), (.4199, .8228), (29.5, 21.0), (2.0, 3.1), 'Grasps in time'),
        Row('2026-11-14/T1_传送带抓取/失败/VID_20261114_220033.mp4', (329, 353, 362, 377, 398),
            (2.0, 10.0), (.5007, .7317), (2.2, 10.5), (2.0, 3.1), 'Block slips past'),
    )),
    Task('Moving box placement', 3, 5.0, (
        Row('2026-11-14/T2_移动木盒放置/成功/VID_20261114_222003.mp4', (96, 108, 114, 123, 141),
            (2.0, 10.0), (.4845, .6832), (25.0, 32.55), (2.0, 3.1), 'Releases in time'),
        Row('2026-11-14/T2_移动木盒放置/失败/VID_20261114_221325.mp4', (83, 95, 101, 110, 128),
            (2.0, 10.0), (.4495, .6384), (2.2, 32.55), (2.0, 3.1), 'Misses the opening'),
    )),
    Task('Turntable grasp', 3, 5.0, (
        Row('2026-11-22/T3_转盘抓取/成功/VID_20261122_003723.mp4', (249, 285, 303, 336, 366),
            (2.0, 10.0), (.5026, .7963), (2.2, 12.2), (2.0, 3.2), 'Grasps in time'),
        Row('2026-11-22/T3_转盘抓取/失败/VID_20261122_004025.mp4', (252, 288, 306, 339, 369),
            (2.0, 10.0), (.4750, .8222), (2.2, 12.2), (2.0, 3.2), 'Block slips past'),
    )),
    Task('Toy car grasp', 3, 5.0, (
        Row('2026-11-14/T4_玩具车抓取/成功/VID_20261114_164915.mp4', (173, 191, 215, 269, 290),
            (2.0, 10.0), (.5815, .7177), (2.2, 17.0), (2.0, 2.0), 'Grasps in time'),
        Row('2026-11-14/T4_玩具车抓取/失败/VID_20261114_165010.mp4', (203, 221, 245, 299, 320),
            (2.0, 10.0), (.4920, .7224), (2.2, 17.0), (2.0, 2.0), 'Misses the car'),
    )),
    Task('Ball intercept', 3, 5.0, (
        Row('2026-11-14/T5_网球拦截/成功/VID_20261114_162059.mp4', (160, 166, 172, 181, 193),
            (2.0, 10.0), (.5466, .6771), (2.2, 32.4), (2.0, 1.25), 'Intercepts in time'),
        Row('2026-11-14/T5_网球拦截/失败/.VID_20261114_161424.mp4', (103, 109, 115, 124, 136),
            (2.0, 10.0), (.5371, .6632), (2.2, 32.4), (2.0, 1.25), 'Ball rolls past'),
    )),
    Task('Ramp cart grasp', 3, 5.0, (
        Row('2026-11-22/T6_斜坡小车取块/成功/VID_20261122_005212.mp4', (173, 185, 194, 218, 245),
            (2.0, 10.0), (.4456, .6113), (2.2, 12.0), (2.0, 2.0), 'Grasps in time'),
        Row('2026-11-22/T6_斜坡小车取块/失败/VID_20261122_005031.mp4', (154, 166, 175, 199, 226),
            (2.0, 10.0), (.3697, .6163), (2.2, 12.0), (2.0, 2.0), 'Stays on cart'),
    )),
)
HEIGHT = len(TASKS) * TASK_HEIGHT + (len(TASKS) - 1) * TASK_GAP


def source_frames(source_dir: Path, row: Row) -> list[Image.Image]:
    source = source_dir / row.video
    select = '+'.join(f'eq(n\\,{index})' for index in row.indices)
    with TemporaryDirectory() as temporary:
        folder = Path(temporary)
        subprocess.run([
            'ffmpeg', '-nostdin', '-loglevel', 'error', '-threads', '3', '-i', str(source),
            '-map', '0:v:0', '-vf', f'select={select}', '-fps_mode', 'passthrough',
            '-frames:v', str(len(row.indices)), '-pix_fmt', 'rgb24', '-c:v', 'png',
            '-compression_level', '2', '-threads:v', '1', str(folder / 'frame-%02d.png'),
        ], check=True)
        paths = sorted(folder.glob('frame-*.png'))
        if len(paths) != len(row.indices):
            raise ValueError(f'{source}: expected {len(row.indices)} frames, got {len(paths)}')
        frames = []
        for path in paths:
            with Image.open(path) as frame:
                if frame.size != ORIGINAL_SIZE or frame.mode != 'RGB':
                    raise ValueError(f'{source}: unexpected source frame {frame.size}, {frame.mode}')
                frames.append(frame.resize(PDF_FRAME_SIZE, Image.Resampling.LANCZOS))
        return frames


def reference_columns() -> tuple[float, ...]:
    with fitz.open(REFERENCE) as reference:
        page, = reference
        if not isclose(page.rect.width, WIDTH, abs_tol=.001):
            raise ValueError('the S1 figure width changed')
        first_row = [image['bbox'][0] for image in page.get_image_info() if abs(image['bbox'][1]) < .005]
    columns = tuple(sorted(first_row))
    if tuple(round(x, 1) for x in columns) != (114.0, 185.3, 256.6, 328.0, 399.3):
        raise ValueError(f'the S1 columns changed: {columns}')
    return columns


def place_frame(page: Canvas, frame: Image.Image, x: float, y: float) -> fitz.Rect:
    page.drawImage(ImageReader(frame), x, HEIGHT - y - CELL_HEIGHT, CELL_WIDTH, CELL_HEIGHT)
    return fitz.Rect(x, y, x + CELL_WIDTH, y + CELL_HEIGHT)


def text(page: Canvas, x: float, y: float, label: str, color) -> None:
    page.setFillColor(color)
    page.setFont(FONT, TEXT_SIZE)
    page.drawString(x, HEIGHT - y, label)


def draw_method(page: Canvas, image: fitz.Rect, offset: tuple[float, float], row_index: int) -> None:
    x = image.x0 + offset[0]
    y = image.y0 + offset[1] + CAP_HEIGHT * TEXT_SIZE
    if row_index == 0:
        text(page, x, y, 'FoveaWAM', white)
    else:
        text(page, x, y, 'π', white)
        page.setFont(FONT, TEXT_SIZE * .7)
        page.drawString(x + pdfmetrics.stringWidth('π', FONT, TEXT_SIZE), HEIGHT - y - 1.05, '0.5')


def draw_callout(page: Canvas, image: fitz.Rect, row: Row, radius: float, color) -> None:
    cx = image.x0 + row.target[0] * image.width
    cy = image.y0 + row.target[1] * image.height
    circle = fitz.Rect(cx - radius - .5, cy - radius - .5, cx + radius + .5, cy + radius + .5)
    if not image.contains(circle):
        raise ValueError(f'target circle crosses an image edge: {row}')
    page.setStrokeColor(color)
    page.setLineWidth(1.0)
    page.circle(cx, HEIGHT - cy, radius, stroke=1, fill=0)

    left, top = image.x0 + row.callout[0], image.y0 + row.callout[1]
    width = pdfmetrics.stringWidth(row.note, FONT, TEXT_SIZE)
    baseline = top + CAP_HEIGHT * TEXT_SIZE
    bounds = fitz.Rect(left, top, left + width, baseline + .22 * TEXT_SIZE)
    if not image.contains(bounds) or min(left - image.x0, image.x1 - bounds.x1,
                                         top - image.y0, image.y1 - bounds.y1) < 1.47:
        raise ValueError(f'callout does not fit with a 1.5 pt margin: {row.note}')
    dx = cx - min(max(cx, bounds.x0), bounds.x1)
    dy = cy - min(max(cy, bounds.y0), bounds.y1)
    if hypot(dx, dy) <= radius + .65:
        raise ValueError(f'callout overlaps the target circle: {row.note}')
    text(page, left, baseline, row.note, color)


def draw_outcome(page: Canvas, image: fitz.Rect, margins: tuple[float, float], row_index: int) -> None:
    color = ROW_COLORS[row_index]
    label = ('Success', 'Failure')[row_index]
    label_width = pdfmetrics.stringWidth(label, FONT, TEXT_SIZE)
    right, bottom = image.x1 - margins[0], image.y1 - margins[1]
    gap = 1.4
    x = right - label_width - gap - FACE_SIZE
    y = HEIGHT - bottom
    cx, cy = x + FACE_SIZE / 2, y + FACE_SIZE / 2

    page.saveState()
    page.setFillColor(white)
    page.setFillAlpha(.85)
    page.roundRect(x, y, FACE_SIZE, FACE_SIZE, .85, stroke=0, fill=1)
    page.restoreState()
    page.setStrokeColor(color)
    page.setFillColor(color)
    page.setLineWidth(.6)
    page.circle(cx, cy, 2.18, stroke=1, fill=0)
    for offset in (-.76, .76):
        page.circle(cx + offset, cy + .53, .26, stroke=0, fill=1)
    mouth = page.beginPath()
    if row_index == 0:
        mouth.moveTo(cx - .96, cy - .42)
        mouth.curveTo(cx - .58, cy - 1.29, cx + .58, cy - 1.29, cx + .96, cy - .42)
    else:
        mouth.moveTo(cx - .94, cy - 1.02)
        mouth.curveTo(cx - .56, cy - .24, cx + .56, cy - .24, cx + .94, cy - 1.02)
    page.setLineCap(1)
    page.setLineWidth(.6)
    page.drawPath(mouth, stroke=1, fill=0)
    text(page, x + FACE_SIZE + gap, bottom - FACE_SIZE / 2 + CAP_HEIGHT * TEXT_SIZE / 2, label, color)


def draw_figure(file: Path, tasks: list[list[Image.Image]], columns: tuple[float, ...]) -> None:
    page = Canvas(str(file), pagesize=(WIDTH, HEIGHT), initialFontName=FONT, pageCompression=1)
    page.setTitle('Real-robot trials')
    for index, (task, frames) in enumerate(zip(TASKS, tasks, strict=True)):
        top = index * (TASK_HEIGHT + TASK_GAP)
        page.setFont(FONT, TITLE_SIZE)
        page.setFillColor(black)
        page.drawRightString(TITLE_RIGHT, HEIGHT - top - TASK_HEIGHT / 2 - CAP_HEIGHT * TITLE_SIZE / 2, task.name)
        for row_index, row in enumerate(task.rows):
            y = top + row_index * (CELL_HEIGHT + ROW_GAP)
            for column, x in enumerate(columns):
                box = place_frame(page, frames[5 * row_index + column], x, y)
                if column == 0:
                    draw_method(page, box, row.method, row_index)
                if column == task.annotation_column - 1:
                    draw_callout(page, box, row, task.radius, ROW_COLORS[row_index])
                if column == 4:
                    draw_outcome(page, box, row.outcome, row_index)
    page.save()


def verify_images(page: fitz.Page, tasks: list[list[Image.Image]]) -> None:
    embedded = page.get_image_info(xrefs=True)
    originals = [frame for task in tasks for frame in task]
    if len(embedded) != len(originals):
        raise ValueError('the output image count differs from the source')
    # ReportLab rounds page coordinates when writing PDF drawing commands.
    page_bounds = page.rect + (-.001, -.001, .001, .001)
    for image, frame in zip(embedded, originals, strict=True):
        pixels = fitz.Pixmap(page.parent, image['xref'])
        if (pixels.width, pixels.height) != frame.size or pixels.samples != frame.tobytes():
            raise ValueError('an embedded image differs from the resized full video frame')
        box = fitz.Rect(image['bbox'])
        if not (page_bounds.contains(box) and isclose(box.width, CELL_WIDTH, abs_tol=.001)
                and isclose(box.height, CELL_HEIGHT, abs_tol=.001)):
            raise ValueError(f'a full frame does not fit in its cell: {box}')


def render_spread(s2: fitz.Document, target: Path) -> None:
    letter_width, letter_height = 612, 792
    x_margin, y_margin = (letter_width - WIDTH) / 2, 72
    with fitz.open(REFERENCE) as s1, fitz.open() as spread:
        page = spread.new_page(width=2 * letter_width, height=letter_height)
        for index, figure in enumerate((s1, s2)):
            x = x_margin + index * letter_width
            height = figure[0].rect.height
            page.show_pdf_page(fitz.Rect(x, y_margin, x + WIDTH, y_margin + height), figure, 0)
        page.draw_line(fitz.Point(letter_width, 54), fitz.Point(letter_width, letter_height - 54),
                       color=(.84, .87, .89), width=.55)
        page.get_pixmap(dpi=144, alpha=False).save(target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, default=SOURCE_DIR)
    parser.add_argument('--arial-bold', type=Path, default=ARIAL_BOLD)
    parser.add_argument('--output-dir', type=Path, default=HERE)
    args = parser.parse_args()

    rl_config.useA85 = False
    pdfmetrics.registerFont(TTFont(FONT, args.arial_bold))
    frames = [source_frames(args.source_dir, task.rows[0]) + source_frames(args.source_dir, task.rows[1])
              for task in TASKS]
    columns = reference_columns()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=args.output_dir) as temporary:
        stage = Path(temporary)
        pdf = stage / 'real_trials.pdf'
        draw_figure(pdf, frames, columns)
        with fitz.open(pdf) as figure:
            page, = figure
            verify_images(page, frames)
            page.get_pixmap(dpi=600, alpha=False).save(stage / 'real_trials.png')
            render_spread(figure, stage / 'spread_preview.png')
        for filename in ('real_trials.pdf', 'real_trials.png', 'spread_preview.png'):
            (stage / filename).replace(args.output_dir / filename)


if __name__ == '__main__':
    main()
