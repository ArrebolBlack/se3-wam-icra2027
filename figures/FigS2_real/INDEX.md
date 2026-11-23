# 图 S2 真机试次

[论文图体](real_trials.pdf)供[英文附录](../../appendix/real.tex)和[中文附录](../../zh/appendix/real.tex)共用。[600 dpi 预览](real_trials.png)和[跨页核对图](spread_preview.png)可用于审阅。

## 素材与标注帧

试次和取帧时刻来自各任务的定稿胶卷图，60 张选片均已逐帧对回视频原片。T3 和 T6 使用 `2026-11-22` 的补拍原片，其余任务使用 `2026-11-14` 的原片。上行是 FoveaWAM 的成功试次，下行是 π₀.₅ 的失败试次。

| 任务 | 上行 | 下行 | 源表五列相对时刻（秒） | 0.0 s 列 | 标注列 |
|---|---:|---:|---|---:|---:|
| Conveyor grasp | #64 | #71 | −0.8、0.0、+0.3、+0.8、+1.5 | 2 | 3 |
| Moving box placement | #85 | #78 | −0.6、−0.2、0.0、+0.3、+0.9 | 3 | 3 |
| Turntable grasp | #126 | #128 | −1.8、−0.6、0.0、+1.1、+2.1 | 3 | 3 |
| Toy car grasp | #35 | #36 | −0.6、0.0、+0.8、+2.6、+3.3 | 2 | 3 |
| Ball intercept | #15 | #06 | −0.4、−0.2、0.0、+0.3、+0.7 | 3 | 3 |
| Ramp cart grasp | #138 | #135 | −0.4、0.0、+0.3、+1.1、+2.0 | 2 | 3 |

六项都在第 3 列标注圆圈和短注。Turntable grasp 的成功行取 #126 原片 10.100 秒（f303），失败行取 #128 原片 10.200 秒（f306）。Ball intercept 成功行第 3 列是 #15 原片 5.733 秒的首次可见触球帧。失败行第 3 列是 #06 原片 3.833 秒的指尖线通过时刻。

## 失败短注核对

按各任务选片页链接回看了六段失败原片。T1、T3、T5、T6 已将 `Arrives too late` 改为获确认的动作短注。T2 将 `Releases too late` 改为 `Misses the opening`，T4 沿用 `Misses the car`。

| 任务 | 原片证据 | 图内短注 |
|---|---|---|
| Conveyor grasp #71 | 11.767 秒方块仍与指尖投影重合，随后从左侧滑过并转动。夹爪在目标到来前已处在附近。 | `Block slips past` |
| Moving box placement #78 | 3.368 秒松开方块时，盒口左沿刚到释放位置。方块落在盒前的带面上。 | `Misses the opening` |
| Turntable grasp #128 | 10.200 秒绿块仍紧邻左指尖。11.300 秒夹爪已合空，绿块留在盘上并转向左侧。 | `Block slips past` |
| Toy car grasp #36 | 7.367 秒小车与指尖投影重合，夹爪短暂随车跟进，小车仍贴桌面并从左侧驶出。 | `Misses the car` |
| Ball intercept #06 | 3.833 秒球通过指尖线，此后继续向左滚动。 | `Ball rolls past` |
| Ramp cart grasp #135 | 5.533 秒方块处在指尖旁，随后留在沿斜坡滑走的小车上。 | `Stays on cart` |

## 版面和标记

五列图格左边界取自[图 S1](../FigS6/rollouts.pdf)实际坐标，约为 114.0、185.3、256.6、328.0、399.3 pt。图幅为 495 × 526.875 pt。每格为 69.7 × 39.20625 pt，上下行间距 1.9 pt，任务间距 9.0 pt。

每格展示原视频的完整 16:9 画面。为适配 Overleaf 单文件 50 MB 的同步上限，生成器把 1920 × 1080 原片画面整幅等比缩放为 704 × 396，再以 PNG 预测器无损嵌入 PDF，并逐格校验像素与显示边界。

任务标题使用 Arial Bold 9.2 pt。帧内文字使用 Arial Bold 5.4 pt，π₀.₅ 的下标为 3.78 pt。圆圈按全幅画面中的目标位置对齐，各行使用 5 pt 半径。

```powershell
python figures/FigS2_real/build_real_trials.py
```

脚本依赖 FFmpeg、Pillow、PyMuPDF、ReportLab 和 Arial Bold。`--source-dir` 指定 `real-robot-demo` 目录，`--arial-bold` 指定字体文件。

## 任务名大写检索

附录 D 英文任务表采用与 S2 相同的句首大写，中文表沿用原稿。检索排除了 archive、Claude outputs、tmp 和 materials 目录。

- 正文图 6 使用 `figures/Fig6/outputs/single-column/fig6.pdf`，六个任务名仍为每词首字母大写。对应文字也见同目录的 `fig6.svg` 第 8、11、14、18、22、25 行和 `fig6.json`。中英文图体引用见 `figures/Fig6/figure.tex` 第 3 行和 `figures/Fig6/figure_zh.tex` 第 3 行。
- 图 6 的生成器 `figures/Fig6/build_figure.py` 第 28–33、165 行保留这些显示词。旧版 `figures/Fig6/outputs/polished/fig6.{pdf,svg,json}` 也保留每词首字母大写，其中网球任务为 `Tennis Ball Interception`。
- 图 6 的历史评审记录 `docs/figures_20261116/arrow_unify/REPORT.md` 第 57–62 行和同目录 `measurements.json` 第 4564、4611、4658、5209、5256、5303 行也保留该写法。

## 构建与页次

`./scripts/build.ps1 -Check` 通过，17 项测试通过。独立英文补充材料的[图 S1 第 7 页](review/supplement_s1.png)和[图 S2 第 8 页](review/supplement_s2.png)后接参考文献。合订英文稿的图 S1、S2 位于最后两页（第 18、19 页），中文稿也位于最后两页（第 25、26 页）。
