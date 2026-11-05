"""Extract original VLA/WAM two-axis figures; TinyVLA is the primary reference."""
from pathlib import Path
import argparse
import json
import urllib.request

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCES = [
    dict(key='01_tinyvla', original_key='tinyvla', title='TinyVLA', kind='VLA', venue='RA-L 2025',
         figure='Fig.1', page=1, version='arXiv v5, 2025-05-13',
         url='https://tiny-vla.github.io/', pdf='https://arxiv.org/pdf/2409.12514v5',
         crop=[312, 174, 560, 339], full_crop=[312, 174, 560, 339]),
    dict(key='03_deervla', original_key='deervla', title='DeeR-VLA', kind='VLA', venue='NeurIPS 2024',
         figure='Fig.3, upper row', page=8, version='Official conference PDF',
         url='https://proceedings.neurips.cc/paper_files/paper/2024/hash/67b0e7c7c2a5780aeefe3b79caac106e-Abstract-Conference.html',
         pdf='https://proceedings.neurips.cc/paper_files/paper/2024/file/67b0e7c7c2a5780aeefe3b79caac106e-Paper-Conference.pdf',
         crop=[108, 319, 505, 436], full_crop=[108, 319, 505, 493]),
    dict(key='04_fasterwam', original_key='fasterwam', title='Faster-WAM', kind='WAM', venue='arXiv 2026',
         figure='Fig.1(b)', page=2, version='arXiv v2, 2026-10-06',
         url='https://arxiv.org/abs/2608.02365v2', pdf='https://arxiv.org/pdf/2608.02365v2',
         crop=[315, 81, 504, 253], full_crop=[117, 80, 505, 269]),
    dict(key='05_turbowam', original_key='turbowam', title='TurboWAM', kind='WAM', venue='arXiv 2026',
         figure='Fig.1(b)', page=1, version='arXiv v2, 2026-11-02',
         url='https://turbowam.github.io/', pdf='https://arxiv.org/pdf/2610.33941v2',
         crop=[337, 234, 561, 426], full_crop=[60, 230, 561, 434]),
    dict(key='06_fastwam', original_key='fastwam', title='Fast-WAM', kind='WAM', venue='arXiv 2026',
         figure='Fig.4, left', page=9, version='arXiv v2, 2026-03-23',
         url='https://arxiv.org/abs/2603.16666v2', pdf='https://arxiv.org/pdf/2603.16666v2',
         crop=[117, 74, 300, 225], full_crop=[117, 74, 492, 225]),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Download the pinned original PDFs.')
    args = parser.parse_args()
    (ROOT / 'papers').mkdir(exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 29)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
    sheet = Image.new('RGB', (1560, 2040), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, source in enumerate(SOURCES):
        pdf = ROOT / 'papers' / f'{source["key"]}.pdf'
        if args.download:
            request = urllib.request.Request(source['pdf'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                data = response.read()
                if not data.startswith(b'%PDF'):
                    raise ValueError(f'{source["title"]}: response is not a PDF')
                pdf.write_bytes(data)
        document = fitz.open(pdf)
        page = document[source['page'] - 1]
        for suffix, crop in [('', source['crop']), ('_full', source['full_crop'])]:
            if suffix and source['crop'] == source['full_crop']:
                continue
            page.get_pixmap(matrix=fitz.Matrix(6.25, 6.25), clip=fitz.Rect(crop), alpha=False).save(ROOT / f'{source["key"]}{suffix}.png')
        image = Image.open(ROOT / f'{source["key"]}.png')
        box_w, box_h = (1480, 640) if index == 0 else (700, 470)
        image.thumbnail((box_w, box_h), Image.Resampling.LANCZOS)
        x, y = (30, 20) if index == 0 else (30+(index-1)%2*780, 780+(index-1)//2*630)
        draw.text((x, y), f'{index+1:02d}  {source["title"]}', fill='#26343B', font=font)
        draw.text((x, y + 39), f'{source["venue"]} | {source["figure"]} | p.{source["page"]}', fill='#58656B', font=small)
        sheet.paste(image, (x + (box_w-image.width)//2, y + 100 + (box_h-image.height)//2))
    sheet.save(ROOT / 'reference_overview.png')
    (ROOT / 'sources.json').write_text(json.dumps(SOURCES, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    comparison = Image.new('RGB', (1560, 850), 'white')
    draw = ImageDraw.Draw(comparison)
    for index, (label, path) in enumerate([
        ('Primary reference: TinyVLA Fig.1', ROOT/'01_tinyvla.png'),
        ('FoveaWAM: single diagonal comparison', ROOT.parent/'native_tradeoff.png')]):
        image = Image.open(path)
        image.thumbnail((730, 735), Image.Resampling.LANCZOS)
        x = 25 + index*780
        draw.text((x, 22), label, fill='#26343B', font=small)
        comparison.paste(image, (x+(730-image.width)//2, 82+(735-image.height)//2))
    comparison.save(ROOT/'reference_vs_fig1.png')
    print(json.dumps({'references': len(SOURCES), 'primary': 'TinyVLA Fig.1', 'crop_dpi': 450}))


if __name__ == '__main__':
    main()
