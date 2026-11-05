"""Download original papers on request and extract the inspected reference figures."""
from pathlib import Path
import argparse
import json
import urllib.request

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCES = [
    dict(key='01_efficientnet', title='EfficientNet', venue='ICML 2019', figure=1, page=1,
         url='https://proceedings.mlr.press/v97/tan19a.html',
         pdf='https://proceedings.mlr.press/v97/tan19a/tan19a.pdf', crop=[306, 176, 546, 358]),
    dict(key='02_deit', title='DeiT', venue='ICML 2021', figure=1, page=1,
         url='https://proceedings.mlr.press/v139/touvron21a.html',
         pdf='https://proceedings.mlr.press/v139/touvron21a/touvron21a.pdf', crop=[316, 187, 531, 395]),
    dict(key='03_mobilevit', title='MobileViT', venue='ICLR 2022', figure=2, page=2,
         url='https://openreview.net/forum?id=vh-0sUt8HlG',
         pdf='https://arxiv.org/pdf/2110.02178v2', crop=[126, 374, 247, 465]),
    dict(key='04_efficientformer', title='EfficientFormer', venue='NeurIPS 2022', figure=1, page=2,
         url='https://proceedings.neurips.cc/paper_files/paper/2022/hash/5452ad8ee6ea6e7dc41db1cbd31ba0b8-Abstract-Conference.html',
         pdf='https://proceedings.neurips.cc/paper_files/paper/2022/file/5452ad8ee6ea6e7dc41db1cbd31ba0b8-Paper-Conference.pdf',
         crop=[170, 82, 431, 286]),
    dict(key='05_mobileone', title='MobileOne', venue='CVPR 2023', figure=1, page=2,
         url='https://openaccess.thecvf.com/content/CVPR2023/html/Vasu_MobileOne_An_Improved_One_Millisecond_Mobile_Backbone_CVPR_2023_paper.html',
         pdf='https://openaccess.thecvf.com/content/CVPR2023/papers/Vasu_MobileOne_An_Improved_One_Millisecond_Mobile_Backbone_CVPR_2023_paper.pdf',
         crop=[49, 70, 548, 361]),
    dict(key='06_fastvit', title='FastViT', venue='ICCV 2023', figure=1, page=2,
         url='https://openaccess.thecvf.com/content/ICCV2023/html/Vasu_FastViT_A_Fast_Hybrid_Vision_Transformer_Using_Structural_Reparameterization_ICCV_2023_paper.html',
         pdf='https://openaccess.thecvf.com/content/ICCV2023/papers/Vasu_FastViT_A_Fast_Hybrid_Vision_Transformer_Using_Structural_Reparameterization_ICCV_2023_paper.pdf',
         crop=[48, 70, 548, 261]),
    dict(key='07_repvit', title='RepViT', venue='CVPR 2024', figure=1, page=1,
         url='https://openaccess.thecvf.com/content/CVPR2024/html/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.html',
         pdf='https://openaccess.thecvf.com/content/CVPR2024/papers/Wang_RepViT_Revisiting_Mobile_CNN_From_ViT_Perspective_CVPR_2024_paper.pdf',
         crop=[309, 231, 547, 407]),
    dict(key='08_fastvlm', title='FastVLM', venue='CVPR 2025', figure=1, page=1,
         url='https://openaccess.thecvf.com/content/CVPR2025/html/Vasu_FastVLM_Efficient_Vision_Encoding_for_Vision_Language_Models_CVPR_2025_paper.html',
         pdf='https://openaccess.thecvf.com/content/CVPR2025/papers/Vasu_FastVLM_Efficient_Vision_Encoding_for_Vision_Language_Models_CVPR_2025_paper.pdf',
         crop=[324, 240, 547, 535]),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='Fetch the original PDFs.')
    args = parser.parse_args()
    (ROOT / 'papers').mkdir(exist_ok=True)
    font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 28)
    small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 22)
    sheet = Image.new('RGB', (1560, 2460), 'white')
    draw = ImageDraw.Draw(sheet)
    for index, source in enumerate(SOURCES):
        pdf = ROOT / 'papers' / f'{source["key"]}.pdf'
        if args.download:
            request = urllib.request.Request(source['pdf'], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(request, timeout=45) as response:
                pdf.write_bytes(response.read())
        document = fitz.open(pdf)
        page = document[source['page'] - 1]
        crop = fitz.Rect(source['crop'])
        image_path = ROOT / f'{source["key"]}.png'
        page.get_pixmap(matrix=fitz.Matrix(6.25, 6.25), clip=crop, alpha=False).save(image_path)
        image = Image.open(image_path)
        image.thumbnail((700, 480), Image.Resampling.LANCZOS)
        x, y = 30 + index % 2 * 780, 20 + index // 2 * 610
        draw.text((x, y), f'{index+1:02d}  {source["title"]}', fill='#26343B', font=font)
        draw.text((x, y + 38), f'{source["venue"]} | Fig. {source["figure"]} | PDF p. {source["page"]}', fill='#58656B', font=small)
        sheet.paste(image, (x + (700 - image.width) // 2, y + 92 + (480 - image.height) // 2))
    sheet.save(ROOT / 'reference_overview.png')
    (ROOT / 'sources.json').write_text(json.dumps(SOURCES, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'references': len(SOURCES), 'crop_dpi': 450, 'overview': str(ROOT / 'reference_overview.png')}))


if __name__ == '__main__':
    main()
