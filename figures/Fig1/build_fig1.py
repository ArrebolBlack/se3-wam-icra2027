"""Compose the selected colored real-scene SVG and current Table 1 Native chart."""
from copy import deepcopy
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from draw_latency import render_latency

ROOT = Path(__file__).resolve().parent
W, H = 3650, 1280
WIDTH_IN = 6.875
LEFT_WIDTH, CHART_X = 2260, 2300
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)

def main():
    selected = ROOT / 'data/real_scene/scene_rgb.svg'
    scene = ET.parse(selected).getroot()
    assert scene.get('viewBox') == f'0 0 {LEFT_WIDTH} {H}'
    geometry_meta = json.loads((ROOT / 'data/real_scene/source.json').read_text(encoding='utf-8'))
    root = ET.Element(f'{{{SVG}}}svg', {'width': f'{WIDTH_IN}in', 'height': f'{WIDTH_IN*H/W:.8f}in', 'viewBox': f'0 0 {W} {H}', 'role': 'img', 'font-family': 'Arial'})
    ET.SubElement(root, f'{{{SVG}}}title').text = 'FoveaWAM: real-scene role-aware geometry and Native success versus latency'
    desc = ET.SubElement(root, f'{{{SVG}}}desc')
    ET.SubElement(root, f'{{{SVG}}}rect', {'width': str(W), 'height': str(H), 'fill': 'white'})
    root.append(deepcopy(scene.find(f'{{{SVG}}}g[@id="A_Real_RGB"]')))
    scene_desc = scene.find(f'{{{SVG}}}desc').text
    scene.set('width', f'{WIDTH_IN*LEFT_WIDTH/W:.8f}in')
    scene.set('height', f'{WIDTH_IN*H/W:.8f}in')
    ET.ElementTree(scene).write(ROOT / 'real_scene.svg', encoding='utf-8', xml_declaration=True)

    chart_svg, chart_meta = render_latency()
    performance_desc = (f'Native SR and native p95 from Table 1. FoveaWAM reports {chart_meta["ours"]["native_sr"]:.1f}% '
        f'and {chart_meta["ours"]["p95_ms"]:g} ms. A single diagonal comparison points from OpenWAM-alpha to '
        'FoveaWAM; its label reports the native p95 latency ratio. Circles denote reactive policies, '
        'triangles VLAs, squares video WAMs, and the star FoveaWAM. OpenWAM-alpha (off) is outside the selected 0-200 ms range.')
    desc.text = f'Left: {scene_desc} Right: {performance_desc}'
    right = ET.SubElement(root, f'{{{SVG}}}g', {'id': 'B_Native_Chart', 'transform': f'translate({CHART_X} 0)'})
    right.append(ET.fromstring(f'<svg xmlns="{SVG}">{chart_svg}</svg>')[0])
    ET.ElementTree(root).write(ROOT / 'fig1.svg', encoding='utf-8', xml_declaration=True)
    chart = ET.Element(f'{{{SVG}}}svg', {'width': '3.25in', 'height': f'{3.25*H/(W-CHART_X):.8f}in',
        'viewBox': f'0 0 {W-CHART_X} {H}', 'role': 'img', 'font-family': 'Arial'})
    ET.SubElement(chart, f'{{{SVG}}}title').text = 'Native success rate versus p95 time-to-action'
    ET.SubElement(chart, f'{{{SVG}}}desc').text = performance_desc
    ET.SubElement(chart, f'{{{SVG}}}rect', {'width': str(W-CHART_X), 'height': str(H), 'fill': 'white'})
    chart.append(ET.fromstring(f'<svg xmlns="{SVG}">{chart_svg}</svg>')[0])
    ET.ElementTree(chart).write(ROOT / 'native_tradeoff.svg', encoding='utf-8', xml_declaration=True)
    report = {
        'canvas_wh': [W, H], 'width_in': WIDTH_IN, 'height_in': WIDTH_IN*H/W,
        'panels': {'left': {'x': 0, 'y': 0, 'width': LEFT_WIDTH, 'height': H, 'source': 'data/real_scene/scene_rgb.svg'},
                   'right': {'x': CHART_X, 'y': 0, 'width': W-CHART_X, 'height': H}},
        'layout': {'divider': False},
        'left': {'photo_id': geometry_meta['photo_id'], 'model': geometry_meta['model'],
                 'geometry_status': geometry_meta['geometry_status'], 'future_status': geometry_meta['future_status'],
                 'color_processing': 'P040 RGB with depth-weighted background toning',
                 'source_geometry': 'data/real_scene/source.json', 'future_horizon_ms': 400},
        'performance': chart_meta,
    }
    (ROOT / 'layout_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'canvas_wh': [W, H], 'sr_column': chart_meta['sr_column'], 'ours': chart_meta['ours'], 'speedup': chart_meta['speedup']['ratio']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
