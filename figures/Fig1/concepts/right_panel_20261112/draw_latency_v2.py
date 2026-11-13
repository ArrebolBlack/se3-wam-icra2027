"""Fig.1(b) refined design draft: Native SR vs. native p95, read from Table 1.

Drop-in candidate for figures/Fig1/draw_latency.py: `render_latency()` returns the
same (svg_group, metadata) pair, so build_fig1.py can import it unchanged.

Standalone use (writes native_tradeoff_v2.svg next to this file):
    python draw_latency_v2.py [path/to/tables/main_results.tex]
"""
from pathlib import Path
from html import escape
import math
import re
import sys

ROOT = Path(__file__).resolve().parent
PANEL_WIDTH, PANEL_HEIGHT = 1350, 1280
# Table 1 lives at <repo>/tables/main_results.tex; works from figures/Fig1/ or figures/Fig1/concepts/<dir>/.
DEFAULT_TABLE = next((parent / 'tables/main_results.tex' for parent in ROOT.parents
                      if (parent / 'tables/main_results.tex').exists()), ROOT / 'main_results.tex')

# ---- layout constants (canvas px; 1 px = 6.875 in / 3650 = 0.1356 pt in the paper) ----
AX, AY, AW, AH = 150, 130, 1080, 1005          # plot box: was 145, 240, 1040, 770
PALETTE = dict(ink='#253436', gray='#53656B', grid='#E9EEF0', axis='#53656B', leader='#93A1A8',
               base='#7B8C93', dark='#344F58', coral='#E95432')
SIZE = dict(title=52, tick=46, axis=50, method=50, ours=62, ours_value=52,
            ratio=50, ratio_detail=44, legend=44)


def table_rows(table=DEFAULT_TABLE):
    """Same parsing as draw_latency.table_rows(): cell 5 = Native SR, cell 8 = p95."""
    rows = []

    def value(cell):
        if cell.strip() == '--':
            return None
        cell = re.sub(r'\\(?:best|second)cell\{([^}]*)\}', r'\1', cell)
        cell = cell.replace(r'$^{\dagger}$', '')
        return float(cell)

    for line in Path(table).read_text(encoding='utf-8').splitlines():
        cells = [cell.strip() for cell in line.rstrip().rstrip('\\').split('&')]
        if len(cells) != 9:
            continue
        name = re.sub(r'\s*\\cite\{[^}]*\}', '', cells[0])
        display = (name.replace('$', '').replace(r'\pi_{0.5}', 'π0.5').replace(r'\alpha', 'α')
                   .replace('+SE(3)', ' + SE(3)'))
        ours = name.startswith(r'\ours')
        if not ours and not display.startswith(('ACT', 'DP', 'π0.5', 'DynamicVLA', 'PUMA', 'OpenWAM', 'DynamicWAM')):
            continue
        if any(r'\resultplaceholder' in cells[index] for index in [5, 8]):
            raise ValueError('Fig.1 requires reported Native SR and p95 in Table 1.')
        family = ('ours' if ours else 'Reactive' if display in ('ACT', 'DP')
                  else 'Video WAM' if display.startswith(('OpenWAM', 'DynamicWAM')) else 'VLA')
        rows.append(dict(method=name, display='FoveaWAM' if ours else display, family=family,
                         sr=value(cells[5]), p95=value(cells[8]), pending=value(cells[5]) is None))
    assert len(rows) == 11, 'Unexpected Table 1 method set; review Fig.1 labels.'
    return rows


def render_latency(table=DEFAULT_TABLE):
    reported = table_rows(table)
    selected = next(row for row in reported if row['family'] == 'ours')
    rows = [dict(method=row['display'], family=row['family'], native_sr=row['sr'], p95_ms=row['p95'])
            for row in reported
            if row['family'] != 'ours' and row['display'] != 'OpenWAM-α (off)' and not row['pending']]
    ours = dict(status='reported_table1', native_sr=selected['sr'], p95_ms=selected['p95'],
                source='tables/main_results.tex')
    reference = next(row for row in rows if row['method'] == 'OpenWAM-α')
    ratio = reference['p95_ms'] / ours['p95_ms']

    def X(ms): return AX + ms / 200 * AW
    def Y(sr): return AY + (1 - sr / 100) * AH

    P, S = PALETTE, SIZE
    svg = []

    def text(x, y, content, size, color=None, bold=False, anchor='start', transform=None, ident=None):
        extra = (f' transform="{transform}"' if transform else '') + (f' id="{ident}"' if ident else '')
        body = escape(content)
        if content.startswith('π0.5'):
            # Editable subscript: dy shifts are honoured by Chrome, Inkscape and Illustrator alike.
            sub, rest = round(size * 0.17), escape(content[4:])
            body = f'π<tspan font-size="{round(size*0.7)}" dy="{sub}">0.5</tspan>'
            body += f'<tspan dy="-{sub}">{rest}</tspan>' if rest else ''
        svg.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color or P["gray"]}" '
                   f'font-weight="{700 if bold else 400}" text-anchor="{anchor}"{extra}>{body}</text>')

    def path(points, color=None, width=2.0, fill='none', close=False, cls=None):
        d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in points) + (' Z' if close or fill != 'none' else '')
        extra = f' class="{cls}"' if cls else ''
        svg.append(f'<path d="{d}" fill="{fill}" stroke="{color or P["gray"]}" stroke-width="{width}" '
                   f'stroke-linecap="round" stroke-linejoin="round"{extra}/>')

    # Markers: neutral fill + white keyline so neighbours stay separable at print size.
    HALO = 2.6

    def circle(x, y, r, color, cls='marker'):
        svg.append(f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}" stroke="white" stroke-width="{HALO}"/>')

    def square(x, y, half, color, cls='marker'):
        svg.append(f'<rect class="{cls}" x="{x-half:.1f}" y="{y-half:.1f}" width="{half*2}" height="{half*2}" '
                   f'fill="{color}" stroke="white" stroke-width="{HALO}"/>')

    def triangle(x, y, r, color, cls='marker'):
        pts = [(x, y - r), (x + r * .92, y + r * .62), (x - r * .92, y + r * .62)]
        d = 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pts) + ' Z'
        svg.append(f'<path class="{cls}" d="{d}" fill="{color}" stroke="white" stroke-width="{HALO}" stroke-linejoin="round"/>')

    def star(x, y, outer=31, inner=13.2):
        pts = [(x + (outer if i % 2 == 0 else inner) * math.cos(-math.pi / 2 + i * math.pi / 5),
                y + (outer if i % 2 == 0 else inner) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]
        d = 'M' + ' L'.join(f'{a:.1f},{b:.1f}' for a, b in pts) + ' Z'
        svg.append(f'<path id="ours-star" class="marker" d="{d}" fill="{P["coral"]}" stroke="white" stroke-width="3" stroke-linejoin="round"/>')

    svg.append('<g id="B_Native_Success_Latency">')
    text(0, 66, '(b) Success vs. latency', S['title'], P['ink'], True, ident='panel-title')

    # ---- axes -------------------------------------------------------------------------
    svg.append('<g id="axes">')
    for sr in [0, 25, 50, 75, 100]:
        y = Y(sr)
        if sr:
            path([(AX, y), (AX + AW, y)], P['grid'], 1.8, cls='grid')
        text(AX - 20, y + S['tick'] * 0.36, str(sr), S['tick'], anchor='end')
    path([(AX, AY), (AX, AY + AH), (AX + AW, AY + AH)], P['axis'], 2.6)
    for ms in [0, 50, 100, 150, 200]:
        x = X(ms)
        path([(x, AY + AH), (x, AY + AH + 11)], P['axis'], 2.2)
        text(x, AY + AH + 56, str(ms), S['tick'], anchor='middle')
    ymid = AY + AH / 2
    text(50, ymid, 'Native SR (%)', S['axis'], anchor='middle', transform=f'rotate(-90 50 {ymid:.1f})')
    text(AX + AW / 2, 1258, 'p95 time-to-action (ms)', S['axis'], anchor='middle')
    svg.append('</g>')

    pos = {row['method']: (X(row['p95_ms']), Y(row['native_sr'])) for row in rows}
    fp = (X(ours['p95_ms']), Y(ours['native_sr']))
    op = pos['OpenWAM-α']

    # ---- shape legend, parked in the empty 0-25% band ---------------------------------
    svg.append('<g id="legend">')
    ly = Y(11.5)
    lx = AX + 218
    circle(lx, ly, 13, P['base'], 'legend-marker'); text(lx + 26, ly + 16, 'Reactive', S['legend'])
    triangle(lx + 276, ly + 2, 14, P['base'], 'legend-marker'); text(lx + 302, ly + 16, 'VLA', S['legend'])
    square(lx + 462, ly, 11, P['base'], 'legend-marker'); text(lx + 488, ly + 16, 'Video WAM', S['legend'])
    svg.append('</g>')

    # ---- comparison arrow: OpenWAM-α -> FoveaWAM (native p95 ratio) --------------------
    svg.append('<g id="comparison">')
    dx, dy = fp[0] - op[0], fp[1] - op[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    tail = (op[0] + ux * 26, op[1] + uy * 26)
    tip = (fp[0] - ux * 44, fp[1] - uy * 44)
    head = 25
    base = (tip[0] - ux * head, tip[1] - uy * head)
    path([tail, base], 'white', 11)
    path([tail, base], P['coral'], 4.2)
    path([tip, (base[0] - uy * 10.5, base[1] + ux * 10.5), (base[0] + uy * 10.5, base[1] - ux * 10.5)],
         P['coral'], 1, fill=P['coral'])
    # Horizontal two-line label, above the arrow and right of its midpoint.
    rx, ry = X(105), Y(68.6)
    text(rx, ry, f'≈{ratio:.1f}× faster', S['ratio'], P['coral'], True, ident='ratio')
    text(rx, ry + 55, f'p95: {reference["p95_ms"]:g} → {ours["p95_ms"]:g} ms', S['ratio_detail'], P['coral'], ident='ratio-detail')
    svg.append('</g>')

    # ---- baselines: label anchor, baseline y, text-anchor, lines, leader end ------------
    m = S['method']
    cap = m * 0.358                      # half cap height: baseline = centre + cap
    col60 = X(59.6) - 36                 # right edge of the label column for the 60 ms cluster
    below = Y(41.1) + 34                 # shared centre line for the two DynamicWAM labels
    labels = {
        # method: (x, centre_y, anchor, lines, leader_from or None)
        'ACT': (pos['ACT'][0] + 28, pos['ACT'][1], 'start', ['ACT'], None),
        'DP': (pos['DP'][0] + 28, pos['DP'][1], 'start', ['DP'], None),
        'PUMA': (col60, Y(61.4) - 34, 'end', ['PUMA'], (col60 + 7, Y(61.4) - 32)),
        'π0.5 + SE(3)': (col60, Y(58.7) - 5, 'end', ['π0.5 + SE(3)'], (col60 + 7, Y(58.7) - 5)),
        'π0.5': (col60, Y(54.4) + 8, 'end', ['π0.5'], (col60 + 7, Y(54.4) + 6)),
        'DynamicVLA': (pos['DynamicVLA'][0], pos['DynamicVLA'][1] + 50, 'middle', ['DynamicVLA'], None),
        'OpenWAM-α': (op[0] + 34, op[1], 'start', ['OpenWAM-α'], None),
        'DynamicWAM': (pos['DynamicWAM'][0] - 34, below, 'end', ['DynamicWAM'],
                       (pos['DynamicWAM'][0] - 27, below - 6)),
        'DynamicWAM + SE(3)': (pos['DynamicWAM + SE(3)'][0] + 34, below, 'start', ['DynamicWAM', '+ SE(3)'],
                               (pos['DynamicWAM + SE(3)'][0] + 27, below - 6)),
    }
    svg.append('<g id="leaders">')
    for name, (_, _, _, _, leader) in labels.items():
        if leader:
            path([leader, pos[name]], P['leader'], 2.2, cls='leader')
    svg.append('</g>')

    svg.append('<g id="baselines">')
    plotted = []
    # Draw order: the left DynamicWAM square first so its neighbour's keyline stays intact.
    for row in sorted(rows, key=lambda r: r['p95_ms']):
        x, y = pos[row['method']]
        assert 0 <= row['native_sr'] <= 100 and 0 < row['p95_ms'] <= 200
        plotted.append(dict(**row, x=x, y=y))
        is_ref = row['method'] == 'OpenWAM-α'
        color = P['dark'] if is_ref else P['base']
        if row['family'] == 'Reactive':
            circle(x, y, 13, color)
        elif row['family'] == 'VLA':
            triangle(x, y + 2, 14, color)
        else:
            square(x, y, 12.5 if is_ref else 10, color)
    for name, (tx, cy, anchor, parts, _) in labels.items():
        is_ref = name == 'OpenWAM-α'
        for index, part in enumerate(parts):
            text(tx, cy + cap + index * (m + 4), part, m, P['dark'] if is_ref else P['gray'], is_ref, anchor)
    svg.append('</g>')

    # ---- FoveaWAM: star + name + values as one group ------------------------------------
    svg.append('<g id="ours">')
    star(*fp)
    gx = fp[0] + 31 + 22
    value_base = fp[1] - 26
    text(gx, value_base - S['ours_value'] - 14, 'FoveaWAM', S['ours'], P['coral'], True, ident='ours-name')
    text(gx, value_base, f'{ours["native_sr"]:.1f}% · {ours["p95_ms"]:g} ms', S['ours_value'], P['coral'], True, ident='ours-values')
    svg.append('</g>')
    svg.append('</g>')

    metadata = dict(
        sr_column='Native', sr_table_cell=5, p95_table_cell=8,
        axis=dict(scale='linear', minimum=0, maximum=200, sr_minimum=0, sr_maximum=100),
        plot=dict(x=AX, y=AY, width=AW, height=AH), plotted=plotted, ours=dict(**ours, x=fp[0], y=fp[1]),
        omitted=[dict(method='OpenWAM-α (off)', reason='Outside the selected 0-200 ms view; Table 1 reports 466.3 ms.')],
        speedup=dict(reference='OpenWAM-α', p95_ms=reference['p95_ms'], ratio=ratio,
                     arrow_from=list(op), arrow_to=list(fp)),
        style=dict(comparison='single diagonal arrow, horizontal two-line label', reference='TinyVLA Fig.1',
                   px_to_pt=6.875 * 72 / 3650, sizes_px=S))
    return '\n'.join(svg), metadata


def standalone_svg(chart_svg):
    return (f'<?xml version="1.0" encoding="utf-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="2.54280822in" height="2.41095890in" '
            f'viewBox="0 0 {PANEL_WIDTH} {PANEL_HEIGHT}" role="img" font-family="Arial,sans-serif">'
            f'<title>Native success rate versus p95 time-to-action</title>'
            f'<rect width="{PANEL_WIDTH}" height="{PANEL_HEIGHT}" fill="white"/>\n{chart_svg}\n</svg>\n')


if __name__ == '__main__':
    import json
    table = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_TABLE
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / 'native_tradeoff_v2.svg'
    chart, meta = render_latency(table)
    out.write_text(standalone_svg(chart), encoding='utf-8')
    out.with_suffix('.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'ours': meta['ours'], 'ratio': meta['speedup']['ratio'], 'points': len(meta['plotted'])}, ensure_ascii=False))
