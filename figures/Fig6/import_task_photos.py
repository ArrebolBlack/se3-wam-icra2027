"""Import the six reviewed task photographs, including the accepted slope v2 crop."""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parent
SPECS = [
    ('t1', 'P051', '传送带抓取', 'Fig7_final/T1_conveyor_pick_P051.png'),
    ('t2', 'P062', '传送带放置', 'Fig7_final/T2_conveyor_place_P062.png'),
    ('t3', 'P034', '转盘抓取', 'Fig7_final/T3_turntable_pick_P034.png'),
    ('t4', 'P068', '小车抓取', 'Fig7_final/T4_car_pick_P068.png'),
    ('t5', 'P079', '网球抓取', 'Fig7_final/T5_tennis_ball_P079.png'),
    ('t6', 'P043', '斜坡小车载块抓取', 'Fig7_final/slope_v2/T6_inclined_rail_pick_P043_v2.png'),
]


def main(photo_root: Path):
    inventory = {r['id']: r for r in json.loads((photo_root / 'review/inventory.json').read_text(encoding='utf-8'))}
    destination = ROOT / 'assets/real_photos'
    (destination / 'originals').mkdir(parents=True, exist_ok=True)
    manifest = {'status':'task_photographs','label':'fig:real_trials','panels':{}}
    records = {}
    for task, pid, name, crop_file in SPECS:
        r = inventory[pid]
        original = photo_root / r['filename']
        cropped = photo_root / crop_file
        with Image.open(cropped) as im:
            im.load()
            crop = json.loads(im.info['CropXYWH'])
            x, y, width, height = crop
            assert im.mode == 'RGB' and im.size == (width, height)
            assert width*9 == height*16
            with Image.open(original) as source:
                source = ImageOps.exif_transpose(source).convert('RGB')
                assert ImageChops.difference(source.crop((x,y,x+width,y+height)), im).getbbox() is None
        crop_name = f'{task}_{pid}.png'
        shutil.copy2(original, destination / 'originals' / original.name)
        shutil.copy2(cropped, destination / crop_name)
        records[task] = {
            'photo_id':pid,
            'task_name':name,
            'source_camera':r['source'],
            'camera_model':r['model'],
            'original':f'originals/{original.name}',
            'crop_file':crop_name,
            'original_crop_xywh':crop,
            'source_px':[r['width'],r['height']],
            'crop_px':[width,height],
            'source_asset':str(cropped),
            'device_exif_datetime':r['datetime_original'],
            'source_pixel_equality':True,
            'content':'task setup photograph; not a logged policy trial',
        }
        manifest['panels'][task] = {
            'status':'task_photo',
            'image':f'assets/real_photos/{crop_name}',
            'provenance_record':f'assets/real_photos/provenance.json#{task}',
        }
    provenance = {
        'source_root':str(photo_root),
        'processing':'Exact source-pixel rectangular crops; no retouching, synthesis, tone changes or sharpening. Figure embedding is downsampled to at least 600 ppi.',
        'time_note':'Original filenames and device EXIF dates are preserved; device clocks have not been calibrated.',
        'photos':records,
    }
    (destination / 'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    (ROOT / 'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    lines = ['# Fig7 实拍任务素材', '', '六项任务场景总览所用的原片与已审核裁剪。斜坡使用用户接受的 v2 裁剪。', '', '| 面板 | 内容 | 审核编号 | 相机来源 | 裁剪PNG |', '|---|---|---|---|---|']
    for task,pid,name,_ in SPECS:
        r = records[task]
        lines.append(f"| {task.upper()} | {name} | {pid} | {r['source_camera']} | [{r['crop_file']}]({r['crop_file']}) |")
    lines += ['', '- [provenance.json](provenance.json)：源文件、相机、原图坐标、尺寸及像素核验记录。', '- `originals/`：六张原始JPEG，保留设备EXIF。', '- [导入脚本](../../import_task_photos.py)：从本地照片审核目录重新导入，逐张检查裁剪像素。', '- [图项目入口](../../INDEX.md)：排版、图注与论文集成。', '']
    (destination / 'INDEX.md').write_text('\n'.join(lines),encoding='utf-8')
    print('Imported and verified 6 task photos; slope uses v2; task overview only.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--photo-root',type=Path,required=True)
    main(parser.parse_args().photo_root)
