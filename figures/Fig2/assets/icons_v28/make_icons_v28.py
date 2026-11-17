"""Fig. 3 (figures/Fig2) v28 icon assets: robot-arm line icons in three poses and Gaussian noise grids.

Run from this folder: python make_icons_v28.py
Writes robot_arm_p1.svg, robot_arm_p2.svg, robot_arm_p3.svg (shared viewBox, so the base stays
aligned across poses) and noise_grids_v28.json (two 32 x 32 grids of 8-bit gray levels).
"""
import json
import math
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
INK = '#4A4F55'          # outlines and joint pins
BODY = '#F3F4F6'         # link fill
PART = '#DADDE1'         # base, joints
GRIP = '#E3E6E9'         # gripper fill
SW = 1.8                 # outline width in viewBox units
SHOULDER = (30.0, 60.0)
L_UPPER, L_FORE, L_WRIST = 30.0, 30.0, 7.0
POSES = {'p1': (-65, 15), 'p2': (-55, 32), 'p3': (-45, 50)}  # absolute link angles, deg (0 = right, 90 = down)
VIEWBOX = '10 14 80 82'


def fk(theta1, theta2):
    sx, sy = SHOULDER
    a, b = math.radians(theta1), math.radians(theta2)
    elbow = (sx + L_UPPER * math.cos(a), sy + L_UPPER * math.sin(a))
    wrist = (elbow[0] + L_FORE * math.cos(b), elbow[1] + L_FORE * math.sin(b))
    return elbow, wrist, (wrist[0], wrist[1] + L_WRIST)


def link(p, q, width):
    common = f'x1="{p[0]:.2f}" y1="{p[1]:.2f}" x2="{q[0]:.2f}" y2="{q[1]:.2f}" stroke-linecap="round"'
    return [f'<line {common} stroke="{INK}" stroke-width="{width + 2 * SW:.2f}"/>',
            f'<line {common} stroke="{BODY}" stroke-width="{width:.2f}"/>']


def gripper(flange):
    x, y = flange
    palm_w, palm_h, fin_l, fin_w, gap = 15.0, 4.2, 9.0, 3.0, 4.2
    out = [f'<rect x="{x - palm_w / 2:.2f}" y="{y:.2f}" width="{palm_w}" height="{palm_h}" rx="1.2" '
           f'fill="{GRIP}" stroke="{INK}" stroke-width="{SW}"/>']
    for side in (-1, 1):
        fx = x + side * (gap + fin_w / 2) - fin_w / 2
        out.append(f'<rect x="{fx:.2f}" y="{y + palm_h - 0.3:.2f}" width="{fin_w}" height="{fin_l}" rx="0.9" '
                   f'fill="{GRIP}" stroke="{INK}" stroke-width="{SW}"/>')
    return out


def robot_svg(pose):
    elbow, wrist, flange = fk(*POSES[pose])
    top, bottom = 84.0, 92.0
    g = [f'<polygon points="15,{bottom} 45,{bottom} 41,{top} 19,{top}" fill="{PART}" stroke="{INK}" '
         f'stroke-width="{SW}" stroke-linejoin="round"/>']
    g += link((SHOULDER[0], top), SHOULDER, 10.5)
    g += link(SHOULDER, elbow, 8.5)
    g += link(elbow, wrist, 7.5)
    g += link(wrist, flange, 5.5)
    g += gripper(flange)
    for p, r in ((SHOULDER, 6.2), (elbow, 5.6), (wrist, 4.6)):
        g.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r}" fill="{PART}" stroke="{INK}" stroke-width="{SW}"/>')
        g.append(f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r * 0.32:.2f}" fill="{INK}"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" width="80" height="82">'
            f'<title>Robot arm, pose {pose}</title>' + ''.join(g) + '</svg>\n')


def noise_grid(seed, n=32):
    z = np.clip(np.random.default_rng(seed).standard_normal((n, n)) / 2.2, -1, 1)
    return ((z + 1) / 2 * 225 + 15).round().astype(int).tolist()   # gray 15..240


if __name__ == '__main__':
    for pose in POSES:
        (HERE / f'robot_arm_{pose}.svg').write_text(robot_svg(pose), encoding='utf-8')
    (HERE / 'noise_grids_v28.json').write_text(json.dumps({
        'note': '8-bit gray levels; row-major, 32 x 32; no cell outlines; patch keeps a thin #6E6E6E border',
        'noisy_actions_A': noise_grid(3),
        'inference_noise': noise_grid(4),
    }), encoding='utf-8')
