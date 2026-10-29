# Fig7 实拍替换与论文集成

## 当前内容

上排六张合成任务图已替换为审核后的实拍：T1 P051、T2 P062、T3 P034、T4 P068、T5 P079、T6 P043。T6 使用用户接受的斜坡 v2 裁剪（2304×1296）。原片与裁剪保留于 [real_photos](../../assets/real_photos/INDEX.md)，源文件、相机与原像素坐标由该目录的 `provenance.json` 维护。

下排仍为两组重复的 AI 故事板，只保留配对试验的事件槽位。图中和双语图注均说明其身份；没有加入方法结果、轨迹、实测时间或配对 key。上排静态照片只说明任务场景。

## 图体和文字

- 保持六列两排、6.875×2.375 in 和标签 `fig:real_trials`；项目目录仍为 Fig6，正文编号为 Fig7。
- T5 改为网球抓取，T6 改为斜坡小车载块抓取；同步英文、中文正文与任务表。网球运动机制仍待填，不沿用已弃用的两球撞击设定；T6 不再写滚动球或球/块各十个试验键。
- 双语图注区分任务实拍与下排 AI 占位。
- 原像素裁剪独立保存；SVG/PDF 嵌入图按 600 ppi 缩小并保持 16:9，文字为可编辑矢量。

## 重建

```powershell
python figures/Fig6/import_task_photos.py --photo-root C:/workspace/SE3-WAM-photo-assets
python figures/Fig6/build_figure.py
./scripts/build.ps1 -Target all
```

导入时逐张核对裁剪 PNG 与原始 JPEG 区域的像素。已有素材可直接排版和编译，不依赖外部照片目录。

## 验证与主目录集成

已先在独立工作树验证，再将受影响的图源、素材和双语文字集成到实际主论文目录 `C:/workspace/se3-wam-icra2027`，并从该目录重建全部阅读 PDF。尚未 commit 或 push。

- 英文正文 12 页、完整稿 26 页、中文稿 33 页、补充材料 15 页；总页数与替换前一致。Fig7 位于英文正文/完整稿第 8 页、中文稿第 11 页。
- 四份最终编译日志均无 LaTeX 错误、未定义引用、缺字或 overfull box。
- 上排六幅 PDF 嵌入图逐一匹配对应实拍裁剪的 600 ppi 缩放像素；斜坡来源坐标确认为 v2。全图包含 12 次图像展示，图内最小字为 7.2 pt。
- 已查看最终英文/中文整页、图体和图注，无照片拉伸、遮盖或标签碰撞。
- 构建日志与局部检查保留在 `build/fig7-real-photos/`；`fig7-in-paper.png` 包含英文第 8 页中的图体及图注，`Fig7-paper-page.pdf` 是同一页的独立阅读副本。

上一版合成图的集成记录见 [历史记录](../../archive/synthetic-layout/INDEX.md)。
