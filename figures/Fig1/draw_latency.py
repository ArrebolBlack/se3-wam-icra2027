"""Fig.1 Native success rate and native p95, read directly from Table 1."""
from pathlib import Path
from html import escape
import math
import re

ROOT = Path(__file__).resolve().parent
PANEL_WIDTH, PANEL_HEIGHT = 1350, 1280

def table_rows():
    rows = []
    def value(cell):
        if cell.strip() == '--':
            return None
        cell = re.sub(r'\\(?:best|second)cell\{([^}]*)\}', r'\1', cell)
        cell = cell.replace(r'$^{\dagger}$', '')
        return float(cell)
    for line in (ROOT.parents[1] / 'tables/main_results.tex').read_text(encoding='utf-8').splitlines():
        cells = [cell.strip() for cell in line.rstrip().rstrip('\\').split('&')]
        if len(cells) != 9:
            continue
        name = re.sub(r'\s*\\cite\{[^}]*\}', '', cells[0])
        display = name.replace('$', '').replace(r'\pi_{0.5}', 'π0.5').replace(r'\alpha', 'α').replace('+SE(3)', ' + SE(3)')
        ours = name.startswith(r'\ours')
        if not ours and not display.startswith(('ACT', 'DP', 'π0.5', 'DynamicVLA', 'PUMA', 'OpenWAM', 'DynamicWAM')):
            continue
        if any(r'\resultplaceholder' in cells[index] for index in [5, 8]):
            raise ValueError('Fig.1 requires reported Native SR and p95 in Table 1.')
        family = 'ours' if ours else 'Reactive' if display in ('ACT', 'DP') else 'Video WAM' if display.startswith(('OpenWAM', 'DynamicWAM')) else 'VLA'
        rows.append(dict(method=name, display='FoveaWAM' if ours else display,
                         family=family, sr=value(cells[5]),
                         paused_sr=None if r'\resultplaceholder' in cells[7] else value(cells[7]),
                         p95=value(cells[8]), pending=value(cells[5]) is None,
                         prior_sync_reference=r'$^{\dagger}$' in cells[7]))
    assert len(rows) == 11, 'Unexpected Table 1 method set; review Fig.1 labels.'
    return rows

def render_latency():
    reported = table_rows()
    selected = next(row for row in reported if row['family'] == 'ours')
    rows = [dict(method=row['display'], family=row['family'], native_sr=row['sr'], p95_ms=row['p95'])
            for row in reported if row['family'] != 'ours' and row['display'] != 'OpenWAM-α (off)' and not row['pending']]
    ours = dict(status='reported_table1', native_sr=selected['sr'], p95_ms=selected['p95'], source='tables/main_results.tex')
    reference = next(row for row in rows if row['method'] == 'OpenWAM-α')
    ratio = reference['p95_ms'] / ours['p95_ms']
    ax, ay, aw, ah = 145, 240, 1040, 770
    def X(ms): return ax + ms / 200 * aw
    def Y(sr): return ay + (1 - sr / 100) * ah
    palette = dict(ink='#253436', gray='#53656B', muted='#829198', grid='#E9EEF0', base='#7B8C93', dark='#344F58', coral='#E95432')
    svg = []
    def text(x, y, content, size=46, color=None, bold=False, anchor='start', transform=None):
        extra = f' transform="{transform}"' if transform else ''
        body = escape(content).replace('π0.5', 'π<tspan font-size="70%" baseline-shift="-6">0.5</tspan>')
        svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" fill="{color or palette["gray"]}" font-weight="{700 if bold else 400}" text-anchor="{anchor}"{extra}>{body}</text>')
    def path(points, color=None, width=2, dash=None, fill='none'):
        d = 'M' + ' L'.join(f'{x:.3f},{y:.3f}' for x, y in points)
        if fill != 'none': d += ' Z'
        extra = f' stroke-dasharray="{dash}"' if dash else ''
        svg.append(f'<path d="{d}" fill="{fill}" stroke="{color or palette["gray"]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{extra}/>')
    def circle(x, y, radius, color):
        svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius}" fill="{color}"/>')
    def square(x, y, radius, color, outlined=False):
        svg.append(f'<rect x="{x-radius:.3f}" y="{y-radius:.3f}" width="{radius*2}" height="{radius*2}" fill="{"white" if outlined else color}" stroke="{color}" stroke-width="{3 if outlined else 1}"/>')
    def triangle(x, y, radius, color, filled=False):
        path([(x, y-radius), (x+radius*.9, y+radius*.65), (x-radius*.9, y+radius*.65)], color, 2.7, fill=color if filled else 'white')
    def star(x, y):
        vertices = [(x + (25 if i % 2 == 0 else 10.7) * math.cos(-math.pi/2 + i*math.pi/5),
                     y + (25 if i % 2 == 0 else 10.7) * math.sin(-math.pi/2 + i*math.pi/5)) for i in range(10)]
        path(vertices, 'white', 2.2, fill=palette['coral'])

    svg.append('<g id="B_Native_Success_Latency">')
    text(0, 66, '(b) Success vs. latency', 52, palette['ink'], True)
    for sr in [0, 25, 50, 75, 100]:
        y = Y(sr)
        path([(ax, y), (ax + aw, y)], palette['grid'], 1.6)
        text(ax - 21, y + 14, str(sr), 44, anchor='end')
    path([(ax, ay), (ax, ay+ah), (ax+aw, ay+ah)], width=2.5)
    for ms in [0, 50, 100, 150, 200]:
        x = X(ms)
        path([(x, ay+ah), (x, ay+ah+10)], width=2)
        text(x, ay+ah+55, str(ms), 44, anchor='middle')
    text(47, 625, 'Native SR (%)', 48, anchor='middle', transform='rotate(-90 47 625)')
    text(ax+aw/2, 1132, 'p95 time-to-action (ms)', 48, anchor='middle')

    labels = {
        'ACT': (204, 728, 'start', ['ACT']), 'DP': (503, 837, 'middle', ['DP']),
        'PUMA': (426, 543, 'end', ['PUMA']), 'π0.5': (421, 603, 'end', ['π0.5']),
        'π0.5 + SE(3)': (430, 658, 'end', ['π0.5 + SE(3)']),
        'DynamicVLA': (654, 674, 'middle', ['DynamicVLA']),
        'OpenWAM-α': (984, 644, 'start', ['OpenWAM-α']),
        'DynamicWAM': (984, 727, 'start', ['DynamicWAM']),
        'DynamicWAM + SE(3)': (984, 812, 'start', ['DynamicWAM', '+ SE(3)']),
    }
    leaders = {
        'PUMA': [(444, 535), (437, 535)], 'π0.5': [(436, 590)],
        'π0.5 + SE(3)': [(479, 622), (479, 642), (445, 642)],
        'DynamicVLA': [(654, 630)],
        'OpenWAM-α': [(965, 632), (973, 632)],
        'DynamicWAM': [(962, 711), (973, 711)],
        'DynamicWAM + SE(3)': [(965, 796), (973, 796)],
    }
    for row in rows:
        assert 0 <= row['native_sr'] <= 100 and 0 < row['p95_ms'] <= 200
        position = (X(row['p95_ms']), Y(row['native_sr']))
        if row['method'] in leaders:
            path([position] + leaders[row['method']], '#A8B4BA', 1.6)

    op = (X(reference['p95_ms']), Y(reference['native_sr']))
    fp = (X(ours['p95_ms']), Y(ours['native_sr']))
    dx, dy = fp[0]-op[0], fp[1]-op[1]
    length = math.hypot(dx, dy)
    ux, uy = dx/length, dy/length
    tail, tip = (op[0]+ux*19, op[1]+uy*19), (fp[0]-ux*25, fp[1]-uy*25)
    path([tail, tip], 'white', 9)
    path([tail, tip], palette['coral'], 3.3)
    left = (tip[0]-ux*15-uy*7, tip[1]-uy*15+ux*7)
    right = (tip[0]-ux*15+uy*7, tip[1]-uy*15-ux*7)
    path([tip, left, right], palette['coral'], 0, fill=palette['coral'])
    lx, ly = (op[0]+fp[0])/2 - uy*33, (op[1]+fp[1])/2 + ux*33
    angle = math.degrees(math.atan2(-dy, -dx))
    text(lx, ly, f'≈{ratio:.1f}× faster', 46, palette['coral'], True, 'middle', f'rotate({angle:.6f} {lx:.6f} {ly:.6f})')

    plotted = []
    for row in rows:
        x, y = X(row['p95_ms']), Y(row['native_sr'])
        plotted.append(dict(**row, x=x, y=y))
        color = palette['dark'] if row['method'] == 'OpenWAM-α' else palette['base']
        if row['family'] == 'Reactive': circle(x, y, 12, color)
        elif row['family'] == 'VLA': triangle(x, y, 11, color, row['method'] == 'π0.5 + SE(3)')
        else: square(x, y, 13 if row['method'] == 'OpenWAM-α' else 11, color, row['method'] == 'OpenWAM-α')
        tx, ty, anchor, parts = labels[row['method']]
        for index, part in enumerate(parts):
            text(tx, ty+index*51, part, 46, palette['dark'] if row['method'] == 'OpenWAM-α' else palette['gray'], row['method'] == 'OpenWAM-α', anchor)
    star(*fp)
    text(206, 310, 'FoveaWAM', 54, palette['coral'], True)
    text(206, 368, f'{ours["native_sr"]:.1f}% · {ours["p95_ms"]:g} ms', 46, palette['coral'])
    circle(175, 1220, 11, palette['base']); text(200, 1234, 'Reactive', 44)
    triangle(506, 1220, 13, palette['base']); text(534, 1234, 'VLA', 44)
    square(739, 1220, 11, palette['base']); text(766, 1234, 'Video WAM', 44)
    svg.append('</g>')
    metadata = dict(sr_column='Native',sr_table_cell=5,p95_table_cell=8,
        axis=dict(scale='linear',minimum=0,maximum=200,sr_minimum=0,sr_maximum=100),
        plot=dict(x=ax,y=ay,width=aw,height=ah),plotted=plotted,ours=dict(**ours,x=fp[0],y=fp[1]),
        omitted=[dict(method='OpenWAM-α (off)',reason='Preserved user-selected 0-200 ms view; Table 1 reports 466.3 ms.'),
                 *[dict(method=row['display'],reason='T2 v2 not evaluated; complete aggregate SR unavailable.') for row in reported if row['pending']]],
        speedup=dict(reference='OpenWAM-α',p95_ms=reference['p95_ms'],ratio=ratio,arrow_from=list(op),arrow_to=list(fp)),
        style=dict(comparison='single diagonal arrow',reference='TinyVLA Fig.1',references='references/INDEX.md',
                   label_px=46,label_pt_at_full_figure=46*6.875*72/3650),
        timing_note='Native deployment settings in Table 1; camera inputs and model deployment settings differ as described there.')
    return '\n'.join(svg), metadata
