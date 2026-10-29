# Fig7 单排任务总览与论文集成

## 当前内容

Fig7 只保留一排六项任务实拍：T1 P051、T2 P062、T3 P034、T4 P068、T5 P079、T6 P043。斜坡沿用已接受的 v2 裁剪。照片原片与裁剪保留于 [实拍素材](assets/real_photos/INDEX.md)，来源与原像素坐标由该目录的 `provenance.json` 维护。

旧下排的方法名称、AI 故事板、查询/执行/终止节点、时间轴和占位说明全部移出当前图。当前图用于介绍任务场景，方法性能由论文中的结果表和定量分析呈现。

## 图体与对应文字

- 单排六列，图宽 6.875 in、高 1.111 in；每张照片保持 16:9。最小字号 7.4 pt，嵌入图像分辨率不低于 600 ppi。
- 删除 (a)/(b) 子图标号；正文的 Fig7(a) 引用改为 Fig7。保留标签 `fig:real_trials`，避免破坏正文与补充材料的交叉引用。
- 英文 caption 改为 `Real-robot task setups`，中英文图注逐项介绍六个任务，不再说明方法时序或预留配对图。
- T5 使用网球、T6 使用小车承载的红块；照片、任务标签与任务表保持一致。
- 当前面板清单只有六张实拍；旧合成素材、两排图源和导出已进入 [历史两排版](archive/two-row-layout/INDEX.md)。

## 重建

```powershell
python figures/Fig6/import_task_photos.py --photo-root C:/workspace/SE3-WAM-photo-assets
python figures/Fig6/build_figure.py
./scripts/build.ps1 -Target all
```

导入时逐张核对裁剪 PNG 与原 JPEG 区域的像素。已有素材可直接排版和编译，不依赖外部照片目录。

## 验证与集成

已先在任务工作树验证，再集成到实际主论文目录 `C:/workspace/se3-wam-icra2027` 并重新编译。

- 英文正文 12 页、完整稿 26 页、中文稿 33 页、补充材料 15 页；Fig7 位于英文正文/完整稿第 8 页、中文稿第 10 页。
- 四份最终编译日志均无 LaTeX 错误、未定义引用、缺字或 overfull box；正文已不含 Fig7(a)/(b) 引用。
- 独立图 PDF 为 495×80 pt，仅有六幅图像。六幅嵌入图逐一匹配对应实拍裁剪的 672×378 缩放像素，斜坡仍为 v2；不含方法名称、时间轴或占位图文字。
- 已检查英文、中文论文页面及 caption，未发现照片拉伸、遮盖或文字碰撞。
- 编译日志和预览位于 `build/fig7-six-tasks/`；`fig7-in-paper.png` 和 `fig7-in-paper-zh.png` 包含图体及对应图注。
