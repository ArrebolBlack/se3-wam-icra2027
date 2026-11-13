# Fig. 6 排版与论文集成

Fig. 6 展示六项真机任务的场景。五项使用已审核的照片裁剪，网球拦截使用夹爪接触网球的演示帧。照片来源及原裁剪坐标见[实拍素材索引](assets/real_photos/INDEX.md)。图内采用 Arial 任务名，正文、结果表和附录使用对应的任务名称。LaTeX 标签为 `fig:real_trials`。

## 版式取舍

- **DROID 式通栏。** 六张等高照片以窄白缝拼成一排，按装置所需宽度横裁，图名用 Arial 常规体居中。斜坡图最宽，以保留小车和斜轨。正文引用此版。
- **DemoGen 式单栏。** 两列三行，保留 16:9 裁剪和窄白缝。任务名用 Arial 粗体放在照片左下角，底缘的浅色过渡提供文字对比度。

[导出索引](outputs/INDEX.md)提供两版的构建命令、PDF、可编辑 SVG 和 PNG。试排单栏时，将英文图源中的 `figure*` 改为 `figure`、图片宽度改为 `\columnwidth`，并指向 `outputs/single-column/fig6.pdf`。

## 会议论文参考

- DROID 的六图横排采用等高变宽照片与上方居中任务名。原图下方横线表示三种评测场所，本图的六项任务共用同一平台。[RSS 2024, Fig. 7](https://www.roboticsproceedings.org/rss20/p120.pdf#page=7)
- DemoGen 的实拍网格使用左下角黑色粗体任务名。其叠加箭头表示轨迹，本图图注介绍场景和演示帧来源。[RSS 2025, Fig. 11](https://www.roboticsproceedings.org/rss21/p157.pdf#page=8)

当前照片用于介绍任务场景。策略成功率和延迟见结果表，运动轨迹需查对应实验日志。旧时序占位与配对设计见[历史两排版](archive/two-row-layout/INDEX.md)。实拍来源记录中的历史目录名对应原始资产路径。
