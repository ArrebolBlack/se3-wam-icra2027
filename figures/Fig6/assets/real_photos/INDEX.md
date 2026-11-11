# Fig6 实拍任务素材

任务总览使用五张场景照片和一帧 T5 演示视频。斜坡使用用户接受的 v2 裁剪。

| 面板 | 内容 | 来源编号 | 来源 | 裁剪PNG |
|---|---|---|---|---|
| T1 | 传送带抓取 | P051 | Pocket4 | [t1_P051.png](t1_P051.png) |
| T2 | 传送带放置 | P062 | Pocket4 | [t2_P062.png](t2_P062.png) |
| T3 | 转盘抓取 | P034 | Pocket4 | [t3_P034.png](t3_P034.png) |
| T4 | 小车抓取 | P068 | phone | [t4_P068.png](t4_P068.png) |
| T5 | 滚动网球拦截 | 06-01 | demo video | [t5_demo_06_01.png](t5_demo_06_01.png) |
| T6 | 斜坡小车载块抓取 | P043 | Pocket4 | [t6_P043.png](t6_P043.png) |

- [provenance.json](provenance.json) 记录来源、视频帧号、裁剪坐标及像素核验。
- `originals/` 保存原始照片及设备 EXIF。
- [导入脚本](../../import_task_photos.py) 刷新场景照片并检查裁剪像素，沿用已记录的 T5 视频帧。
- [图项目入口](../../INDEX.md) 包含排版、图注与论文集成。
