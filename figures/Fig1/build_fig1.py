"""Compose the selected colored real-scene SVG and current Table 1 Native chart."""
from pathlib import Path
import json
import xml.etree.ElementTree as ET

from draw_latency import render_latency, table_rows

ROOT = Path(__file__).resolve().parent
W, H = 3650, 1280
LEFT_WIDTH, CHART_X = 2260, 2300
SCENE_SCALE, SCENE_DX, SCENE_DY = 1.13, -225, -40
SVG = 'http://www.w3.org/2000/svg'
ET.register_namespace('', SVG)

def main():
    selected = ROOT / 'data/real_scene/scene.svg'
    scene = ET.parse(selected).getroot()
    assert scene.get('viewBox') == '0 0 2400 1180'
    geometry_meta = json.loads((ROOT / 'data/real_scene/source.json').read_text(encoding='utf-8'))
    root = ET.Element(f'{{{SVG}}}svg', {'width': '6.875in', 'height': f'{6.875*H/W:.8f}in', 'viewBox': f'0 0 {W} {H}', 'role': 'img', 'font-family': 'Arial,sans-serif'})
    ET.SubElement(root, f'{{{SVG}}}title').text = 'FoveaWAM: real-scene role-aware geometry and Native success versus latency'
    desc = ET.SubElement(root, f'{{{SVG}}}desc')
    ET.SubElement(root, f'{{{SVG}}}rect', {'width': str(W), 'height': str(H), 'fill': 'white'})
    left = ET.SubElement(root, f'{{{SVG}}}g', {'id': 'A_Real_Scene_Visualization'})
    geometry = ET.SubElement(left, f'{{{SVG}}}g', {
        'id': 'A_Uniform_Scene_Placement',
        'transform': f'translate({SCENE_DX} {SCENE_DY}) scale({SCENE_SCALE})'})
    for element in scene:
        tag = element.tag.rsplit('}', 1)[-1]
        if tag in {'title', 'desc', 'rect'}:
            continue
        if element.get('id') != 'direct-annotations':
            geometry.append(element)
            continue
        scaled_annotations = ET.SubElement(geometry, f'{{{SVG}}}g', {'id': 'direct-annotations'})
        for annotation in element:
            name = annotation.get('id')
            if name == 'title':
                annotation.set('x', '40')
                annotation.set('y', '66')
                left.append(annotation)
            elif name == 'status':
                annotation.set('x', '2220')
                annotation.set('y', '66')
                left.append(annotation)
            elif name == 'flow-label':
                annotation.set('x', '48')
                left.append(annotation)
            elif annotation.get('stroke') == '#6F9C90':
                continue
            else:
                scaled_annotations.append(annotation)
        # Only the label placement changes; the leader still points to the same flow.
        ET.SubElement(left, f'{{{SVG}}}path', {
            'd': f'M 414 286 L 560 286 L {SCENE_DX+SCENE_SCALE*1003.103:.3f} {SCENE_DY+SCENE_SCALE*360.847:.3f}',
            'fill': 'none', 'stroke': '#6F9C90', 'stroke-width': '1.7',
            'stroke-linecap': 'round', 'stroke-linejoin': 'round'})
    chart_svg, chart_meta = render_latency()
    performance_desc = (f'Native SR and native p95 from Table 1. FoveaWAM reports {chart_meta["ours"]["native_sr"]:.1f}% '
        f'and {chart_meta["ours"]["p95_ms"]:g} ms. A single diagonal comparison points from OpenWAM-alpha to '
        'FoveaWAM; its label reports the native p95 latency ratio. Circles denote reactive policies, '
        'triangles VLAs, squares video WAMs, and the star FoveaWAM. OpenWAM-alpha (off) is outside the selected 0-200 ms range.')
    desc.text = ('Left: the selected full-color real photograph reconstructed with MoGe-2; future target SE(3) '
                 'and sparse 3D motion are illustrative. Right: ' + performance_desc)
    right = ET.SubElement(root, f'{{{SVG}}}g', {'id': 'B_Native_Chart', 'transform': f'translate({CHART_X} 0)'})
    right.append(ET.fromstring(f'<svg xmlns="{SVG}">{chart_svg}</svg>')[0])
    ET.ElementTree(root).write(ROOT / 'fig1.svg', encoding='utf-8', xml_declaration=True)
    chart = ET.Element(f'{{{SVG}}}svg', {'width': '3.25in', 'height': f'{3.25*H/(W-CHART_X):.8f}in',
        'viewBox': f'0 0 {W-CHART_X} {H}', 'role': 'img', 'font-family': 'Arial,sans-serif'})
    ET.SubElement(chart, f'{{{SVG}}}title').text = 'Native success rate versus p95 time-to-action'
    ET.SubElement(chart, f'{{{SVG}}}desc').text = performance_desc
    ET.SubElement(chart, f'{{{SVG}}}rect', {'width': str(W-CHART_X), 'height': str(H), 'fill': 'white'})
    chart.append(ET.fromstring(f'<svg xmlns="{SVG}">{chart_svg}</svg>')[0])
    ET.ElementTree(chart).write(ROOT / 'native_tradeoff.svg', encoding='utf-8', xml_declaration=True)
    report = {
        'canvas_wh': [W, H], 'width_in': 6.875, 'height_in': 6.875*H/W,
        'panels': {'left': {'x': 0, 'y': 0, 'width': LEFT_WIDTH, 'height': H, 'source': 'data/real_scene/scene.svg',
                            'source_scale': SCENE_SCALE, 'translation': [SCENE_DX, SCENE_DY],
                            'scene_print_scale_vs_previous': SCENE_SCALE*3740/W},
                   'right': {'x': CHART_X, 'y': 0, 'width': W-CHART_X, 'height': H}},
        'layout': {'divider': False, 'left_changes': 'Uniformly enlarged scene; header and flow label repositioned; no change to RGB, geometry, poses, or flow.'},
        'left': {'photo_id': geometry_meta['photo_id'], 'model': geometry_meta['model'],
                 'geometry_status': geometry_meta['geometry_status'], 'future_status': geometry_meta['future_status'],
                 'color_processing': geometry_meta['color_processing'], 'source_geometry': 'data/real_scene/source.json',
                 'point_layer_preserved': True, 'future_horizon_ms': 400},
        'performance': chart_meta,
    }
    (ROOT / 'layout_report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'canvas_wh': [W, H], 'sr_column': chart_meta['sr_column'], 'ours': chart_meta['ours'], 'speedup': chart_meta['speedup']['ratio']}, ensure_ascii=False))

if __name__ == '__main__':
    main()
