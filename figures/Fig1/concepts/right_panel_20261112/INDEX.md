# Fig.1(b) 右图精修设计稿（2026-11-12）

[可编辑 SVG](native_tradeoff_v2.svg) · [独立预览](native_tradeoff_v2.png) · [放回 Fig.1 的印刷尺寸预览](fig1_with_v2_print_300dpi.png) · [首页预览](page1_with_v2_300dpi.png) · [右图前后对比](right_panel_before_after_300dpi.png)

设计稿，未接入论文；`../../fig1.*`、`../../native_tradeoff.*` 与 `../../draw_latency.py` 均未改动。

- [绘图脚本](draw_latency_v2.py)：`render_latency()` 的返回值与 `../../draw_latency.py` 相同，仍从主表读取 Native SR／p95。确认采用后可替换原脚本，再运行 `build_fig1.py` 与 `render_fig1.mjs`。
- 绘图区由 (145, 240, 1040×770) 改为 (150, 130, 1080×1005)；十个点按主表数值在新坐标系中重新定位，线性 0–200 ms、0–100% 不变。
- 预览在没有 Arial 的环境中用字宽相同的 Liberation Sans 渲染；SVG 声明的字体仍是 Arial。首页预览是把新图贴到 2026-11-12 20:00 编译的 `main.pdf` 第 1 页同一位置，没有重新编译。
