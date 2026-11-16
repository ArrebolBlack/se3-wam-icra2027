# Fig. 4 / Fig. 6 运动箭头统一

- [联系表](arrow_contact_sheet.pdf)：第一页按印刷尺寸 1:1，后八页为 29 个箭头的修改前后 600 dpi 裁切，显示比例 3 倍。
- [验收报告](REPORT.md)：参数、逐项目检、短箭头调整、编译与同步结果。
- [几何测量](measurements.json)：每个箭头的印刷 pt 中心线、头长、路径长、自适应值与裁切框。
- [联系表重建](build_review.py)：从修改前 main 与当前图生成对照；仓库根目录运行 `python docs/figures_20261116/arrow_unify/build_review.py --base 438c4e4`。
- [核对脚本](verify.py)：验证共享几何、SVG 字节保留、幂等性、三种输出一致性，以及正文页数、分页和字体。
