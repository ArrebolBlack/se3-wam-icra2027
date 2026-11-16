"""Draw illustrative motion in the camera view of the existing P040 RGB panel."""

from base64 import b64encode
from copy import deepcopy
from itertools import product
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from matplotlib import colormaps
from matplotlib.colors import to_hex
import numpy as np


SVG = 'http://www.w3.org/2000/svg'
TARGET_RED = json.loads(
    (Path(__file__).resolve().parents[1] / 'method_colors.json').read_text(encoding='utf-8')
)['FoveaWAM']
AXIS_COLORS = ('#D62728', '#2CA02C', '#1F77B4')
TURBO_RANGE = (0.12, 0.66)
TIME_FRACTIONS = np.linspace(0, 1, 17)
TIME_COLORS = tuple(to_hex(rgba) for rgba in colormaps['turbo'](
    np.linspace(*TURBO_RANGE, len(TIME_FRACTIONS)),
))

# Contour of the red block and cart in the unscaled 2560 x 1440 photo.
CART_CONTOUR = [
    (668, 971), (678, 887), (685, 864), (698, 850), (723, 843),
    (749, 838), (756, 821), (765, 809), (781, 803), (805, 800),
    (808, 657), (810, 648), (816, 643), (830, 642), (975, 641),
    (1000, 643), (1050, 651), (1146, 660), (1152, 664),
    (1154, 673), (1146, 811), (1163, 810), (1173, 819), (1179, 835),
    (1189, 865), (1202, 875), (1234, 887), (1251, 897), (1260, 912),
    (1265, 934), (1269, 1028), (1246, 1040), (1061, 1100), (1027, 1107),
    (1000, 1106), (970, 1101), (713, 1000), (683, 985),
]


def svg(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{SVG}}}{tag}', {
        key.replace('_', '-'): value if isinstance(value, str) else f'{value:.5g}'
        for key, value in attrs.items()
    })


def points(vertices):
    return ' '.join(f'{x:.3f},{y:.3f}' for x, y in vertices)


def line(parent, vertices, stroke, width, **attrs):
    return svg(parent, 'polyline', points=points(vertices), fill='none',
               stroke=stroke, stroke_width=width, stroke_linecap='round',
               stroke_linejoin='round', **attrs)


def label(parent, xy, value, color, size, anchor='middle', weight=700):
    element = svg(parent, 'text', x=xy[0], y=xy[1], fill=color,
                  font_size=size, text_anchor=anchor, font_weight=weight)
    element.text = value
    return element


def gradient(defs, name, a, b, offsets):
    element = svg(defs, 'linearGradient', id=name, gradientUnits='userSpaceOnUse',
                  x1=a[0], y1=a[1], x2=b[0], y2=b[1])
    for offset, color in zip(offsets, TIME_COLORS, strict=True):
        svg(element, 'stop', offset=offset, stop_color=color)
    return f'url(#{name})'


def flow_arrow(parent, anchors, start, end, fill, border=None):
    vector = end - start
    length = np.linalg.norm(vector)
    direction = vector / length
    normal = np.asarray((-direction[1], direction[0]))
    head_length = min(25, 0.32 * length)
    neck = end - direction * head_length
    stem = normal * 4.4
    head = normal * (0.46 * head_length)
    vertices = (start + stem, neck + stem, neck + head, end,
                neck - head, neck - stem, start - stem)
    stroke = {} if border is None else dict(
        stroke=border, stroke_width=2.8, stroke_linejoin='round', stroke_opacity=0.82,
    )
    svg(parent, 'polygon', points=points(vertices), fill=fill, **stroke)
    svg(anchors, 'circle', cx=start[0], cy=start[1], r=7.5, fill='white',
        stroke=TIME_COLORS[0], stroke_width=2.8)


def draw_flow(parent, defs, project, geometry, horizon_ms):
    trails = svg(parent, 'g', id='time-colored-scene-flow')
    anchors = svg(parent, 'g', id='flow-anchors')
    drawn = []
    # Draw lower starts first so overlapping shafts leave the upstream tips visible.
    for vector in reversed(geometry['flow_vectors']):
        pixel = tuple(vector['pixel_xy'])
        a, b = (np.asarray(vector[key]) for key in ('start', 'end'))
        samples = project(a + TIME_FRACTIONS[:, None] * (b - a))
        start, end = samples[[0, -1]]
        offsets = np.linalg.norm(samples - start, axis=1) / np.linalg.norm(end - start)
        name = f'flow-{pixel[0]}-{pixel[1]}'
        track = svg(trails, 'g', id=f'{name}-track')
        color = gradient(defs, name, start, end, offsets)
        flow_arrow(track, anchors, start, end, color,
                   '#142039' if vector['carrier'] else None)
        drawn.append(pixel)

    legend = svg(parent, 'g', id='flow-time-key')
    start, end = np.asarray((113, 333)), np.asarray((490, 333))
    label(legend, (107, 280), 'Sparse 3D flow', '#263E74', 59, anchor='start')
    line(legend, ((547, 265), (562, 265), (582.4, 326)), '#637BA3', 4.5)
    color = gradient(defs, 'flow-time-scale', start, end, TIME_FRACTIONS)
    flow_arrow(legend, legend, start, end, color, '#24374C')
    label(legend, start + (0, 53), '0', '#31455C', 45, anchor='start', weight=400)
    label(legend, end + (0, 53), f'+{horizon_ms} ms', '#31455C', 45, anchor='end', weight=400)
    return drawn


def draw_past(parent, defs, image_xy, current, past, scale):
    clip = svg(defs, 'clipPath', id='past-cart-contour', clipPathUnits='userSpaceOnUse')
    svg(clip, 'polygon', points=points(image_xy(CART_CONTOUR)))
    offset = past - scale * current
    transform = f'matrix({scale:.8f} 0 0 {scale:.8f} {offset[0]:.5f} {offset[1]:.5f})'
    ghost = svg(parent, 'g', id='past-target-from-p040', transform=transform, opacity=0.43)
    svg(ghost, 'use', href='#p040-photo', clip_path='url(#past-cart-contour)')


def draw_contact_detail(parent, photo: Path):
    detail = svg(parent, 'g', id='staged-contact-detail')
    x, y, width, height = 1148, 169, 396, 283.64
    # The P043 viewport is an unwarped crop of the Fig. 6 photograph.
    inset = svg(detail, 'svg', x=x, y=y, width=width, height=height,
                viewBox='990 295 726 520', overflow='hidden')
    encoded = b64encode(photo.read_bytes()).decode('ascii')
    svg(inset, 'image', width=2304, height=1296, href=f'data:image/png;base64,{encoded}')
    svg(detail, 'rect', x=x, y=y, width=width, height=height, fill='none',
        stroke=TARGET_RED, stroke_width=4.5)
    label(detail, (x + width / 2, y + height + 47), 'Contact detail', TARGET_RED, 43)


def draw_cuboid(parent, project, center, axes, half_extents):
    box = svg(parent, 'g', id='future-se3-volume')
    signs = tuple(product((-1, 1), repeat=3))
    vertices = dict(zip(signs, project(center + (np.asarray(signs) * half_extents) @ axes)))
    visible_faces = set()
    for axis, normal in enumerate(axes):
        for sign in (-1, 1):
            if (center @ normal) * sign + half_extents[axis] >= 0:
                continue
            visible_faces.add((axis, sign))
            corners = [key for key in signs if key[axis] == sign]
            corners = [corners[i] for i in (0, 1, 3, 2)]
            face_opacity = (0.14, 0.20, 0.08)[axis]
            svg(box, 'polygon', points=points(vertices[key] for key in corners),
                fill=TARGET_RED, fill_opacity=face_opacity)
    visible_edges = []
    for a in signs:
        for i, sign in enumerate(a):
            if sign > 0:
                continue
            b = a[:i] + (1,) + a[i+1:]
            edge = (vertices[a], vertices[b])
            if any((j, a[j]) in visible_faces for j in range(3) if i != j):
                visible_edges.append(edge)
            else:
                line(box, edge, TARGET_RED, 4.8, stroke_dasharray='15 11', opacity=0.42)
    for edge in visible_edges:
        line(box, edge, TARGET_RED, 8)


def draw_axes(parent, project, center, axes, future):
    triad = svg(parent, 'g', id='future-pose-axes' if future else 'current-pose-axes')
    origin = project(center)
    if future:
        lengths = (0.028, 0.033, 0.013)
    else:
        lengths = (0.021, 0.022, 0.015)
    for name, axis, length, color, offset in zip(
        'xyz', axes, lengths, AXIS_COLORS,
        ((15, 14), (8, -14), (15, 13)), strict=True,
    ):
        end = project(center + axis * length)
        direction = (end - origin) / np.linalg.norm(end - origin)
        base = end - direction * (18 if future else 15)
        normal = np.asarray((-direction[1], direction[0])) * (7.8 if future else 6.5)
        line(triad, (origin, base), color, 6)
        svg(triad, 'polygon', points=points((end, base + normal, base - normal)), fill=color)
        if future:
            label(triad, end + offset, name, color, 37, anchor='start')
    svg(triad, 'circle', cx=origin[0], cy=origin[1], r=8.2, fill='white',
        stroke=TARGET_RED, stroke_width=4)


def render_real_scene(source: Path, geometry: dict, contact_photo: Path, *,
                      panel_height: int, y_offset: int):
    original = ET.parse(source).getroot()
    background = original.find('.//{*}image')
    origin = np.array([float(background.get(key)) for key in ('x', 'y')])
    size = np.array([float(background.get(key)) for key in ('width', 'height')])
    K = np.array(geometry['intrinsics_normalized'])

    def image_xy(pixels):
        return origin + size * np.asarray(pixels) / geometry['inference_wh']

    def project(xyz):
        homogeneous = np.asarray(xyz) @ K.T
        return origin + size * homogeneous[..., :2] / homogeneous[..., 2:]

    scene = ET.Element(f'{{{SVG}}}svg', original.attrib)
    scene.set('font-family', 'Arial')
    scene.set('viewBox', f'0 0 {original.get("width")} {panel_height}')
    scene.set('height', str(panel_height))
    svg(scene, 'title').text = 'FoveaWAM role-aware motion on a real-robot photograph'
    svg(scene, 'desc').text = (
        'P040 RGB photograph with a translucent copy of the target and cart to illustrate '
        'the past. Projected, time-colored sparse 3D flow arrows and the target '
        'SE(3) pose trajectory are illustrative. A separate staged P043 photograph '
        'shows the gripper on the target.'
    )
    panel = svg(scene, 'g', id='A_Real_RGB')
    defs = svg(panel, 'defs')
    frame = svg(defs, 'clipPath', id='p040-full-frame')
    svg(frame, 'rect', **{key: background.get(key) for key in ('x', 'y', 'width', 'height')})
    stage = svg(panel, 'g', clip_path='url(#p040-full-frame)', transform=f'translate(0 {y_offset})')
    photo = deepcopy(background)
    photo.set('id', 'p040-photo')
    stage.append(photo)

    current = np.array(geometry['target_center'])
    selected = max(geometry['future_specs'], key=lambda pose: pose['ms'])
    future = np.array(selected['center'])
    # Set a separated past position along the ramp in the illustration.
    past = current - 2.6 * (future - current)
    earlier, now, later = project((past, current, future))
    draw_past(stage, defs, image_xy, now, earlier, current[2] / past[2])
    drawn = draw_flow(stage, defs, project, geometry, selected['ms'])

    pose = svg(stage, 'g', id='target-se3-trajectory')
    future_axes = np.array(selected['axes_rows'])
    draw_cuboid(pose, project, future, future_axes, geometry['target_half_extents'])
    line(pose, (earlier, now), TARGET_RED, 5.6, stroke_dasharray='19 13', opacity=0.63)
    # Leave room for the current pose axes along the projected center path.
    outgoing = now + 0.23 * (later - now)
    line(pose, (outgoing, later), TARGET_RED, 7)
    midpoint = project((current + future) / 2)
    for xy, opacity in ((earlier, 0.63), (midpoint, 1)):
        svg(pose, 'circle', cx=xy[0], cy=xy[1], r=9, fill='white',
            stroke=TARGET_RED, stroke_width=5, stroke_opacity=opacity)

    draw_axes(pose, project, current, np.array(geometry['target_axes_rows']), future=False)
    draw_axes(pose, project, future, future_axes, future=True)
    label(pose, (earlier[0], 595), 'Past', TARGET_RED, 50)
    label(pose, (now[0], 635), 'Now', TARGET_RED, 50)
    label(pose, (1133, 576), 'Target SE(3)', TARGET_RED, 60, anchor='start')
    label(pose, (later[0] + 58, 637), f'+{selected["ms"]} ms', TARGET_RED, 50)
    draw_contact_detail(stage, contact_photo)
    return scene, {'flow_anchor_pixels': drawn, 'future_horizon_ms': selected['ms'],
                   'past_status': 'Illustrative placement of a clipped copy of the P040 photo'}
