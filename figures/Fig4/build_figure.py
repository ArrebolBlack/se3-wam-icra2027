"""Replace Fig. 4's rendered panels while preserving its editable vector layout.

The adjacent SVG owns the approved 2026-11-16 palette, typography, and paths.
Blender owns all raster colors; no pixel recoloring is applied here.
"""
from pathlib import Path
import argparse
import base64
import io
import json
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from common import find_chromium, inline_local_images, normalize_pdf_metadata

TASKS = ['grasp', 't1_belt', 't1_xyz', 't1_so3', 't1_occ', 't2_trans',
         't2_se3', 't3_phase', 't3_full', 't5_replan', 't4_sphere',
         't4_sphere_tabletop', 't4_slider', 't4_can']
SVG = '{http://www.w3.org/2000/svg}'


def cropped_png(path, crop):
    x, y, width, height = crop
    with Image.open(path) as source:
        assert source.size == (1024, 1024), (path, source.size)
        image = source.crop((x, y, x + width, y + height))
        data = io.BytesIO()
        image.save(data, 'PNG')
    return base64.b64encode(data.getvalue()).decode('ascii')


def export(svg):
    """Chrome/Arial export at the existing 495 x 236 pt physical size."""
    payload = base64.b64encode(inline_local_images(svg)).decode('ascii')
    html = ('<!doctype html><meta charset="utf-8"><style>'
            '@page{size:495pt 236pt;margin:0}'
            'html,body{width:495pt;height:236pt;margin:0;overflow:hidden}'
            'img{display:block;width:495pt;height:236pt}</style>'
            f'<img src="data:image/svg+xml;base64,{payload}">')
    with tempfile.TemporaryDirectory(prefix='se3wam-fig4-') as folder:
        folder = Path(folder)
        page, raw_pdf = folder / 'figure.html', folder / 'chrome.pdf'
        page.write_text(html, encoding='utf-8')
        subprocess.run([str(find_chromium()), '--headless=new', '--disable-gpu',
                        '--no-pdf-header-footer', f'--user-data-dir={folder / "profile"}',
                        f'--print-to-pdf={raw_pdf}', page.as_uri()],
                       capture_output=True, check=True)
        with pymupdf.open(raw_pdf) as raw, pymupdf.open() as final:
            assert len(raw) == 1
            # Preserve the previous export's correction for Chrome pixel rounding.
            output = final.new_page(width=495, height=236)
            output.show_pdf_page(output.rect, raw, 0, keep_proportion=False)
            final.save(svg.with_suffix('.pdf'), garbage=4, deflate=True)
    normalize_pdf_metadata(svg.with_suffix('.pdf'))
    with pymupdf.open(svg.with_suffix('.pdf')) as final:
        fonts = final[0].get_fonts()
        assert fonts and all('Arial' in font[3] for font in fonts), fonts
        final[0].get_pixmap(dpi=600).save(svg.with_suffix('.png'))


def main(args):
    source = args.template.read_text(encoding='utf-8')
    tree = ET.fromstring(source)
    assert tree.attrib == {'width': '495pt', 'height': '236pt', 'viewBox': '0 0 495 236'}
    owners = {child: parent for parent in tree.iter() for child in parent}
    image_owners = [owners[node].get('id') for node in tree.iter(SVG + 'image')]
    assert image_owners == ['paused', 'advancing'] + ['panel-' + task for task in TASKS], image_owners
    protocol = json.loads(Path(__file__).with_name('protocol_example.json').read_text())
    panels = [cropped_png(args.output / 'protocol' / name / 'history.png', protocol['crop_xywh'])
              for name in ('paused', 'advancing')]
    for task in TASKS:
        record = json.loads((args.output / 'assets' / task / 'panel.json').read_text())
        panels.append(cropped_png(args.output / 'panels' / task / 'history.png', record['crop_xywh']))
    pattern = r'(?P<prefix>(?:xlink:)?href=")data:image/png;base64,[^"]*(?P<suffix>")'
    assert len(re.findall(pattern, source)) == len(panels) == 16
    payloads = iter(panels)
    result = re.sub(pattern, lambda match: match['prefix'] + 'data:image/png;base64,'
                    + next(payloads) + match['suffix'], source)
    # Everything outside the image payloads must remain byte-for-byte identical.
    assert re.sub(pattern, 'IMAGE', result) == re.sub(pattern, 'IMAGE', source)
    args.figure.write_text(result, encoding='utf-8')
    export(args.figure)
    print('Exported 14 task panels + 2 protocol panels; 495 x 236 pt; Arial; 600 dpi.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True, help='Prepared/rendered project directory')
    parser.add_argument('--template', type=Path, default=Path(__file__).with_name('ontimebench.svg'))
    parser.add_argument('--figure', type=Path, default=Path(__file__).with_name('ontimebench.svg'))
    main(parser.parse_args())
