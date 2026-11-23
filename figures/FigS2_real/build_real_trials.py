"""Build Figure S2 and its S1/S2 spread from the source PDF's JPEG streams."""

import argparse
from dataclasses import dataclass
from io import BytesIO
from math import hypot, isclose
from pathlib import Path
import re
from tempfile import TemporaryDirectory

import fitz
from reportlab import rl_config
from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


HERE = Path(__file__).resolve().parent
SOURCE = Path('D:/workspace/se3-wam-research/local_private/real-robot-demo/2026-11-14/六任务胶卷图.pdf')
REFERENCE = HERE.parent / 'FigS6' / 'rollouts.pdf'
ARIAL_BOLD = Path('C:/Windows/Fonts/arialbd.ttf')
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
    method: tuple[float, float]
    target: tuple[float, float]
    callout: tuple[float, float]
    outcome: tuple[float, float]
    note: str


@dataclass(frozen=True)
class Task:
    name: str
    zero_column: int
    annotation_column: int
    radius: float
    rows: tuple[Row, Row]


# Positions are relative to each photograph, measured from its top-left corner.
# Method and callout offsets are in pt. Target centres are fractions of width and
# height, and outcome offsets are the margins from the right and bottom edges.
TASKS = (
    Task('Conveyor grasp', 2, 3, 6.3, (
        Row((25.9, 6.1), (.474, .773), (23.3, 8.7), (2.0, 2.0), 'Grasps in time'),
        Row((2.0, 6.6), (.535, .700), (19.0, 10.5), (2.0, 2.0), 'Block slips past'),
    )),
    Task('Moving box placement', 3, 3, 6.3, (
        Row((2.5, 7.3), (.490, .530), (20.1, 32.35), (2.0, 2.0), 'Releases in time'),
        Row((2.0, 6.8), (.598, .495), (2.3, 7.1), (2.0, 2.0), 'Misses the opening'),
    )),
    Task('Turntable grasp', 3, 3, 6.0, (
        Row((1.85, 1.85), (527 / 944, 405 / 590), (2.2, 2.1), (1.85, 1.65), 'Grasps in time'),
        Row((1.85, 1.85), (474 / 944, 426 / 590), (2.2, 2.1), (1.85, 1.65), 'Block slips past'),
    )),
    Task('Toy car grasp', 2, 3, 6.8, (
        Row((1.9, 2.0), (.548, .592), (27.1, 32.25), (2.0, 2.0), 'Grasps in time'),
        Row((1.9, 2.0), (.502, .589), (27.1, 32.25), (2.0, 2.0), 'Misses the car'),
    )),
    Task('Ball intercept', 3, 3, 6.6, (
        Row((1.9, 2.0), (.533, .554), (18.9, 32.25), (2.0, 2.0), 'Intercepts in time'),
        Row((1.9, 2.0), (.585, .534), (27.6, 32.25), (2.0, 2.0), 'Ball rolls past'),
    )),
    Task('Ramp cart grasp', 2, 3, 6.4, (
        Row((1.9, 2.6), (.699, .675), (1.9, 2.3), (2.15, 8.8), 'Grasps in time'),
        Row((2.0, 3.3), (.580, .686), (1.9, 2.3), (2.15, 9.1), 'Stays on cart'),
    )),
)
HEIGHT = len(TASKS) * TASK_HEIGHT + (len(TASKS) - 1) * TASK_GAP


@dataclass(frozen=True)
class Frame:
    jpeg: bytes
    width: int
    height: int


def source_frames(file: Path) -> list[list[Frame]]:
    tasks = []
    with fitz.open(file) as source:
        if len(source) != len(TASKS):
            raise ValueError(f'expected {len(TASKS)} task pages in {file}')
        for page, task in zip(source, TASKS, strict=True):
            times = re.findall(r'^([−+\-]?\d+\.\d+) s\s*$', page.get_text(), re.MULTILINE)
            if len(times) != 5 or times[task.zero_column - 1] != '0.0':
                raise ValueError(f'check the zero column and five offsets for {task.name}: {times}')
            if not 1 <= task.annotation_column <= len(times):
                raise ValueError(f'check the annotation column for {task.name}: {task.annotation_column}')
            items = sorted(page.get_image_info(xrefs=True), key=lambda image: (round(image['bbox'][1], 2), image['bbox'][0]))
            if len(items) != 10:
                raise ValueError(f'expected ten source images for {task.name}, got {len(items)}')
            frames = []
            for item in items:
                image = source.extract_image(item['xref'])
                if image['ext'] != 'jpeg' or image['smask']:
                    raise ValueError(f'{task.name}: expected a standalone JPEG at xref {item["xref"]}')
                frames.append(Frame(image['image'], image['width'], image['height']))
            tasks.append(frames)
    return tasks


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


def place_frame(page: Canvas, frame: Frame, x: float, y: float) -> fitz.Rect:
    # The source crops have different aspect ratios. Fit each intact into its 16:9 cell.
    scale = min(CELL_WIDTH / frame.width, CELL_HEIGHT / frame.height)
    width, height = frame.width * scale, frame.height * scale
    left = x + (CELL_WIDTH - width) / 2
    top = y + (CELL_HEIGHT - height) / 2
    page.drawImage(ImageReader(BytesIO(frame.jpeg)), left, HEIGHT - top - height, width, height)
    return fitz.Rect(left, top, left + width, top + height)


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


def draw_figure(file: Path, tasks: list[list[Frame]], columns: tuple[float, ...]) -> None:
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


def verify_images(page: fitz.Page, tasks: list[list[Frame]]) -> None:
    embedded = page.get_image_info(xrefs=True)
    originals = [frame for task in tasks for frame in task]
    if len(embedded) != len(originals):
        raise ValueError('the output image count differs from the source')
    for image, frame in zip(embedded, originals, strict=True):
        if page.parent.extract_image(image['xref'])['image'] != frame.jpeg:
            raise ValueError('an embedded JPEG differs from the source stream')
        box = fitz.Rect(image['bbox'])
        if not isclose(box.width / box.height, frame.width / frame.height, rel_tol=.00001):
            raise ValueError('a photograph was stretched')


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
    parser.add_argument('--source', type=Path, default=SOURCE)
    parser.add_argument('--arial-bold', type=Path, default=ARIAL_BOLD)
    parser.add_argument('--output-dir', type=Path, default=HERE)
    args = parser.parse_args()

    rl_config.useA85 = False
    pdfmetrics.registerFont(TTFont(FONT, args.arial_bold))
    frames = source_frames(args.source)
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
