"""Assemble recorded Blender panels and editable vector annotations at print size."""
from pathlib import Path
import argparse
import importlib.util
import json
import sys

import numpy as np
from PIL import Image, ImageFilter
import pymupdf as fitz
from reportlab.pdfbase import pdfmetrics

INK, BLUE, GOLD, GRAY = '#263441', '#2A647A', '#9A6B24', '#596873'
WORDS = [['Harmonic','grasp'],['Conveyor','grasp'],['Translating','grasp'],
         ['Rotating','grasp'],['Occluded','grasp'],['Moving','receptacle'],
         ['Rotating','receptacle'],['Wire passage'],['Wire passage,','full'],
         ['Ball capture'],['Ball capture,','table'],['Slider capture'],
         ['Can capture'],['Post-impact','grasp']]

# Panel-local points at the final 495 pt figure width. These gray glyphs describe
# direction, not measured displacement. Place them beside the relevant object,
# keeping the navy recorded center paths at their original scene coordinates.
LOCAL_CUES = {
    'grasp': ((34.,31.),6.2),
    't1_so3': ((33.,36.8),7.2),
    't2_se3': ((43.3,28.8),7.2),
    't3_phase': ((45.,36.8),6.2),
    't3_full': ((45.,36.8),6.2),
}


def arrow(fig, points, color=BLUE, width=.48, head=1.7, shaft=True, halo=True):
    points = np.asarray(points, float)
    if len(points) < 2:
        return
    if shaft:
        if halo:
            fig.line(points, '#FFFFFF', width+.28, alpha=.70)
        fig.line(points, color, width)
    back = -2
    while np.linalg.norm(points[-1]-points[back]) < 1 and -back < len(points):
        back -= 1
    direction = points[-1]-points[back]
    norm = np.linalg.norm(direction)
    if norm < .2:
        return
    direction /= norm
    normal = np.array([-direction[1], direction[0]])
    tip = points[-1]
    triangle = [tip, tip-head*direction+.34*head*normal, tip-.78*head*direction,
                tip-head*direction-.34*head*normal]
    fig.line(triangle, color, .08, closed=True, fill=color)


def label(fig, point, text, anchor, leader_color=GRAY):
    x, y = point
    size = 6.5
    width = pdfmetrics.stringWidth(text, 'Arial', size)
    # Place dark text directly on the quiet scene background; no backing patch.
    center = np.array([x,y-size*.34])
    delta = np.asarray(anchor)-center
    half = np.array([width/2+1.3,size*.5+1.3])
    distance = np.min(half[np.abs(delta)>1e-8]/np.abs(delta[np.abs(delta)>1e-8]))
    assert distance < 1, 'A leader anchor must lie outside its text.'
    start = center+distance*delta
    fig.line([start, anchor], '#FFFFFF', .75, alpha=.70)
    fig.line([start, anchor], leader_color, .45)
    fig.text(x, y, text, size, color=INK)


def annotate(fig, record, root, x, y, panel_width):
    task = record['task_id']
    cx, cy, cw, ch = record['crop_xywh']
    scale = panel_width/cw
    transform = lambda points: np.asarray([(x+(a-cx)*scale,y+(b-cy)*scale) for a,b in points])
    fig.clip(x, y, panel_width, ch*scale, 'clip-'+task)
    # A fine measured silhouette keeps pale histories legible on gray surfaces.
    # Wire geometry is already thin; outlining it would inflate its diameter.
    if not task.startswith('t3'):
        count = len(record['history_contours'])
        for j, contours in enumerate(record['history_contours']):
            opacity = .50 if count == 1 else [.30,.50][j]
            for contour in contours:
                fig.line(transform(contour), '#62879B', .25, alpha=opacity, closed=True)
    # Keep traces clear of the present object and the recorded visibility gaps.
    last = len(record['frames'])-1
    target = np.array(Image.open(root/'assets'/task/f'target_mask_{last}.png')
                      .convert('L').filter(ImageFilter.MaxFilter(19))) > 0
    segments, run = [], []
    for point, visible in zip(record['trajectory_pixels'], record['trajectory_visible']):
        px, py = np.rint(point).astype(int)
        if 0 <= px < 1024 and 0 <= py < 1024 and target[py,px]:
            visible = False
        if visible:
            run.append(point)
        elif run:
            segments.append(run)
            run = []
    if run:
        segments.append(run)
    if not task.startswith('t3'):
        for segment in segments:
            if len(segment) > 3:
                arrow(fig, transform(segment), width=.45 if task=='grasp' else .48,
                      head=1.35 if task=='grasp' else 1.7)
    if task.startswith('t3'):
        entry = transform([record['roles']['entry']])[0]
        fig.circle(entry, 1.35, '#FFFFFF', 1.0)
        fig.circle(entry, 1.35, GOLD, .55)
        label(fig, entry+[.5,-6.7], 'entry', entry+[0,-1.4], GOLD)
        wire = transform([record['roles']['wire_path'][11]])[0]
        label(fig, wire+[10,-6], 'avoid', wire)
    cue = record.get('motion_cue')
    if task in LOCAL_CUES:
        center, extent = LOCAL_CUES[task]
        assert cue['type'] in ('rotation','oscillation')
        points = np.asarray(cue['projected_icon'], float)
        points -= .5*(points.max(axis=0)+points.min(axis=0))
        points *= extent/max(np.ptp(points, axis=0))
        points += np.array(center)+[x,y]
        fig.svg.append(f'<g id="{task}-local-motion-cue"><title>Qualitative {cue["type"]} direction beside the moving object; not a recorded path.</title>')
        arrow(fig, points, color=GRAY, width=.46, head=1.65)
        if cue['type'] == 'oscillation':
            arrow(fig, points[::-1], color=GRAY, width=.46, head=1.65, shaft=False)
        fig.svg.append('</g>')
    if task == 't1_xyz':
        # Its recorded trace lies almost entirely inside the current silhouette.
        # A separate local direction glyph avoids relocating a measured path.
        direction = np.diff(np.asarray(record['trajectory_pixels'])[[0,-1]],axis=0)[0]
        direction /= np.linalg.norm(direction)
        center = np.array([x+28.8,y+38.1])
        points = center+np.array([[-4.25],[4.25]])*direction
        fig.svg.append('<g id="t1_xyz-local-motion-cue"><title>Qualitative translation direction beside the target; not a recorded path.</title>')
        arrow(fig,points,color=GRAY,width=.46,head=1.65)
        fig.svg.append('</g>')
    if 'impact' in record['roles']:
        point = transform([record['roles']['impact']['pixel']])[0]
        label(fig,[x+13.5,y+28.5],'impact',point)
        fig.circle(point, .48, '#FFFFFF', .65)
        fig.circle(point, .48, INK, .1, fill=INK)
    if 'tray_anchor' in record['roles']:
        anchor = transform([record['roles']['tray_anchor']])[0]
        label(fig, [x+panel_width-8,y+ch*scale-4], 'tray', anchor)
        fig.circle(anchor, .4, GRAY, .4)
    fig.unclip()


def main(args):
    sys.path.insert(0, str(args.source_project/'scripts'))
    spec = importlib.util.spec_from_file_location('original_layout',args.source_project/'scripts/build_figure.py')
    layout = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(layout)
    root = args.output
    layout.ROOT = root
    fig = layout.Figure()
    fig.pdf._filename = str(root/'dynamic14.pdf')
    pw, ih, gap = layout.PW, layout.IH, layout.GAP
    fig.svg[0] = fig.svg[0].replace('Fourteen real benchmark scenes. Blue histories and traces are measured; isolated corner arrows are qualitative motion symbols. A cross marks the target center during actual striker contact.',
        'Fourteen recorded native-expert task examples. One or two sparse translucent blue meshes show earlier poses. Navy paths follow recorded target centers; local gray arrows denote translation, rotation or oscillation qualitatively. The impact label marks the target center at a recorded contact time, not the contact point. No future prediction is shown. Text and all arrows are editable vectors; historical meshes are editable in companion Blender scenes.')
    for row,start,count,name in [(0,0,5,'Grasp'),(0,5,2,'Place'),(1,0,2,'Pass'),(1,2,4,'Capture'),(1,6,1,'Impact')]:
        x, y = start*(pw+gap), row*73
        fig.text(x, 7+y, name, 7.5, True, 'start', color=INK)
        width = pdfmetrics.stringWidth(name,'ArialBold',7.5)
        fig.line([(x+width+5,4.5+y),(x+count*pw+(count-1)*gap,4.5+y)], '#C2C9CE', .35)
    records = []
    for i,(task,name,family,_,_) in enumerate(layout.PANELS):
        record = json.loads((root/'assets'/task/'panel.json').read_text())
        cx,cy,cw,ch = record['crop_xywh']
        crop = Image.open(root/'panels'/task/'history.png').crop((cx,cy,cx+cw,cy+ch))
        x,y = (i%7)*(pw+gap),(i//7)*73+11
        fig.svg.append(f'<g id="panel-{task}">')
        fig.image(x,y,pw,ih,crop)
        annotate(fig,record,root,x,y,pw)
        for j,text in enumerate(WORDS[i]):
            fig.text(x+pw/2,(i//7)*73+61.5+j*7.25,text,7,color=INK)
        fig.svg.append('</g>')
        records.append({k:record[k] for k in ('task_id','name','family','episode_id','seed','camera','frames','crop_xywh')})
    fig.svg.append('</svg>')
    (root/'dynamic14.svg').write_text('\n'.join(fig.svg),encoding='utf-8')
    fig.pdf.showPage()
    fig.pdf.save()
    doc = fitz.open(root/'dynamic14.pdf')
    for name,dpi in [('dynamic14.png',600),('preview.png',240),('printsize.png',96)]:
        pix = doc[0].get_pixmap(dpi=dpi,alpha=False)
        Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(root/name,dpi=(dpi,dpi))
    Image.open(root/'preview.png').convert('L').save(root/'grayscale.png')
    spans = [s for b in doc[0].get_text('dict')['blocks'] if 'lines' in b for line in b['lines'] for s in line['spans']]
    assert all(0<=s['bbox'][0]<s['bbox'][2]<=495 and 0<=s['bbox'][1]<s['bbox'][3]<=144 for s in spans)
    (root/'sources.json').write_text(json.dumps({'scope':'Recorded native-expert task illustrations; same episodes and current timestamps; sparser historical sampling, no simulation or pose editing','panels':records},indent=2))
    print('Exported 14 panels with editable labels/arrows; 495 x 144 pt; 600 dpi PNG.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-project',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    main(parser.parse_args())
