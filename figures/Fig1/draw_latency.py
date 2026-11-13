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
    ax, ay, aw, ah = 158, 140, 1142, 990
    def X(ms): return ax + ms / 200 * aw
    def Y(sr): return ay + (1 - sr / 100) * ah
    palette = dict(ink='#253436', gray='#53656B', leader='#84939A', grid='#E6EBED',
                   base='#7B8C93', dark='#344F58', coral='#E95432')
    svg = []
    def text(x, y, content, size=48, color=None, bold=False, anchor='start', transform=None, halo=False):
        extra = f' transform="{transform}"' if transform else ''
        if halo:
            extra += ' paint-order="stroke" stroke="white" stroke-width="7" stroke-linejoin="round"'
        body = escape(content).replace('π0.5', 'π<tspan font-size="72%" baseline-shift="-10">0.5</tspan>')
        svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" fill="{color or palette["gray"]}" font-weight="{700 if bold else 400}" text-anchor="{anchor}"{extra}>{body}</text>')
    def path(points, color=None, width=2, fill='none'):
        d = 'M' + ' L'.join(f'{x:.3f},{y:.3f}' for x, y in points)
        if fill != 'none': d += ' Z'
        svg.append(f'<path d="{d}" fill="{fill}" stroke="{color or palette["gray"]}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"/>')
    def circle(x, y, radius, color):
        svg.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="{radius}" fill="{color}" stroke="white" stroke-width="2.6"/>')
    def square(x, y, radius, color):
        svg.append(f'<rect x="{x-radius:.3f}" y="{y-radius:.3f}" width="{radius*2}" height="{radius*2}" fill="{color}" stroke="white" stroke-width="2.6"/>')
    def triangle(x, y, color):
        half_side = 13.5
        height = half_side * math.sqrt(3)
        path([(x, y-2*height/3), (x+half_side, y+height/3), (x-half_side, y+height/3)],
             'white', 2.6, fill=color)
    def star(x, y):
        vertices = [(x + (31 if i % 2 == 0 else 12.6) * math.cos(-math.pi/2 + i*math.pi/5),
                     y + (31 if i % 2 == 0 else 12.6) * math.sin(-math.pi/2 + i*math.pi/5)) for i in range(10)]
        path(vertices, 'white', 3, fill=palette['coral'])

    svg.append('<g id="B_Native_Success_Latency">')
    text(0, 66, '(b) Success vs. latency', 52, palette['ink'], True)
    for sr in [0, 25, 50, 75, 100]:
        y = Y(sr)
        if sr:
            path([(ax, y), (ax + aw, y)], palette['grid'])
        path([(ax, y), (ax-11, y)], width=2.2)
        text(ax-20, y+15.5, str(sr), 44, anchor='end')
    path([(ax, ay), (ax, ay+ah), (ax+aw, ay+ah)], width=2.6)
    for ms in [0, 50, 100, 150, 200]:
        x = X(ms)
        path([(x, ay+ah), (x, ay+ah+11)], width=2.2)
        text(x, ay+ah+54, str(ms), 44, anchor='middle')
    text(46, 635, 'Native SR (%)', anchor='middle', transform='rotate(-90 46 635)')
    text(ax+aw/2, ay+ah+122, 'p95 time-to-action (ms)', anchor='middle')

    positions = {}
    plotted = []
    for row in rows:
        assert 0 <= row['native_sr'] <= 100 and 0 < row['p95_ms'] <= 200
        x, y = X(row['p95_ms']), Y(row['native_sr'])
        positions[row['method']] = (x, y)
        plotted.append(dict(**row, x=x, y=y))

    # Spread the labels for the clusters near 60 ms and 150 ms while keeping
    # the markers at their table-derived positions.
    labels = {
        'PUMA': (462, 507, 'end'),
        'π0.5 + SE(3)': (462, 569, 'end'),
        'π0.5': (462, 631, 'end'),
        'DynamicWAM': (984, 800, 'end'),
        'DynamicWAM + SE(3)': (1300, 862, 'end'),
    }
    label_offsets = {
        'ACT': (30, 17, 'start'),
        'DP': (28, 17, 'start'),
        'DynamicVLA': (0, 62, 'middle'),
        'OpenWAM-α': (-13.5, -33, 'start'),
    }
    leaders = {
        'PUMA': ((-18.5, -4), (471, 491)),
        'π0.5 + SE(3)': ((-18.5, 2), (471, 553)),
        'π0.5': ((-18.5, 6), (471, 615)),
        'DynamicWAM': ((-13.5, 15.5), (978, 760)),
        'DynamicWAM + SE(3)': ((3, 16.5), (positions['DynamicWAM + SE(3)'][0]+3, 820)),
    }
    for method, (offset, end) in leaders.items():
        x, y = positions[method]
        dx, dy = offset
        path([(x+dx, y+dy), end], palette['leader'], 2.4)

    op = positions[reference['method']]
    fp = (X(ours['p95_ms']), Y(ours['native_sr']))
    dx, dy = fp[0]-op[0], fp[1]-op[1]
    length = math.hypot(dx, dy)
    ux, uy = dx/length, dy/length
    tail, tip = (op[0]+ux*36, op[1]+uy*36), (fp[0]-ux*44, fp[1]-uy*44)
    shaft_end = (tip[0]-ux*32, tip[1]-uy*32)
    path([tail, tip], 'white', 11)
    path([tail, shaft_end], palette['coral'], 4.2)
    left = (tip[0]-ux*36-uy*13.5, tip[1]-uy*36+ux*13.5)
    right = (tip[0]-ux*36+uy*13.5, tip[1]-uy*36-ux*13.5)
    path([tip, left, right], palette['coral'], 0, fill=palette['coral'])
    text(1296, 440, f'≈1/{ratio:.2g} the p95 latency', 50, palette['coral'], True, 'end')
    text(1296, 497, f'of OpenWAM-α ({reference["p95_ms"]:g} ms)', 44, anchor='end')

    for row in rows:
        method = row['method']
        x, y = positions[method]
        is_reference = method == reference['method']
        color = palette['dark'] if is_reference else palette['base']
        if row['family'] == 'Reactive':
            circle(x, y, 13, color)
        elif row['family'] == 'VLA':
            triangle(x, y, color)
        else:
            square(x, y, 13.5 if is_reference else 10.5, color)
        if method in label_offsets:
            dx, dy, anchor = label_offsets[method]
            tx, ty = x+dx, y+dy
        else:
            tx, ty, anchor = labels[method]
        text(tx, ty, method, color=palette['dark'] if is_reference else None,
             bold=is_reference, anchor=anchor, halo=method in {'π0.5', 'OpenWAM-α'})

    star(*fp)
    fx, fy = fp
    text(fx-29, fy-120, 'FoveaWAM', 58, palette['coral'], True)
    text(fx-29, fy-55, f'{ours["native_sr"]:.1f}% · {ours["p95_ms"]:g} ms', 54, palette['coral'], True)
    circle(366, 1037, 13, palette['base'])
    text(401, 1052, 'Reactive', 44)
    triangle(647, 1040, palette['base'])
    text(682, 1052, 'VLA', 44)
    square(840, 1037, 10.5, palette['base'])
    text(875, 1052, 'Video WAM', 44)
    svg.append('</g>')
    metadata = dict(sr_column='Native',sr_table_cell=5,p95_table_cell=8,
        axis=dict(scale='linear',minimum=0,maximum=200,sr_minimum=0,sr_maximum=100),
        plot=dict(x=ax,y=ay,width=aw,height=ah),plotted=plotted,ours=dict(**ours,x=fp[0],y=fp[1]),
        omitted=[dict(method='OpenWAM-α (off)',reason='Preserved user-selected 0-200 ms view; Table 1 reports 466.3 ms.'),
                 *[dict(method=row['display'],reason='T2 v2 not evaluated; complete aggregate SR unavailable.') for row in reported if row['pending']]],
        speedup=dict(reference='OpenWAM-α',p95_ms=reference['p95_ms'],ratio=ratio,arrow_from=list(op),arrow_to=list(fp)),
        style=dict(comparison='single diagonal arrow',reference='TinyVLA Fig.1',references='references/INDEX.md',
                   label_px=48,label_pt_at_full_figure=48*6.875*72/3650),
        timing_note='Native deployment settings in Table 1; camera inputs and model deployment settings differ as described there.')
    return '\n'.join(svg), metadata
