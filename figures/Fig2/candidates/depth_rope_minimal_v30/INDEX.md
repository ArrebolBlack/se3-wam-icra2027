# RGB-D 与 3D 锚点无底部标题预览 v30

状态：输入区已获用户认可，Q/K 处的 RoPE 标注待审；尚未替换正式母版。RGB-D 缩略图向左排列，保留 Depth → 右侧三维锚点的小箭头，去掉下方三个小标题及 i / x_i 点位标注、高亮和引线。

- [当前输入区](input_detail.png)：直接检查本轮无下方小标题的排布。
- [Q/K 与 RoPE 局部](qk_rope_detail.png)：审阅 3D RoPE 标注、代表 token 和共享注意力之间的视觉关系。
- [整图：无 RoPE 标注 / 深灰标注](fig3_rope_presence_compare.png)、[两页矢量 PDF](fig3_rope_presence_compare.pdf)：两版均保留已认可的输入区，只比较是否显示 RoPE 标注及小箭头，不表示模型消融；[生成脚本](compare_rope_presence.py)不改当前候选或母版。
- [RoPE 蓝色与深灰对比](qk_rope_color_compare.png)、[矢量 PDF](qk_rope_color_compare.pdf)：同裁切、同比例比较标注和小箭头的颜色；[生成脚本](compare_rope_colors.py)只在临时副本恢复蓝色，不改当前候选。
- [与上一版对比](local_before_after.png)、[与原 v27 对比](v27_before_after.png)：比较本轮变化或相对正式图的全部局部变化。
- [完整纸面预览](fig2_paper_width.png)、[整图对比 PDF](before_after.pdf)：原 v27 与候选的完整布局。
- [可编辑 PPTX](fig2_se3wam.pptx)、[PDF](fig2_se3wam.pdf)、[SVG](fig2_se3wam.svg)：本轮候选和导出。
- [构建脚本](make_preview.py)、[核对结果](preview_check.json)：从 v29 副本重建，复用原 PowerPoint 导出入口。

RGB 与 Depth 缩略图由 18 pt 调整到 20 pt，在原输入框中垂直居中；右侧保留实录点云与稀疏 patch 锚点。
Depth → 点云短箭头按用户确认改为深灰 `#6E6E6E`，箭杆与箭头头部的尺寸、位置和线宽均不变。
点云只显示普通锚点，不突出单个对应点。Q/K 处只保留 `3D RoPE`，删除参数和 Q,K 后缀；文字及指向蓝色 token 的短箭头按用户确认改为深灰 `#6E6E6E`，token 保持蓝色。原标注框、字号、旋转和箭头几何不变，文字靠箭头一端对齐。
主干、其他面板、图页尺寸及正式母版不动。
数据来源与反投影核对沿用[第一版记录](../depth_rope_v28/INDEX.md#科学关系与素材)。
144 dpi 逐像素检查确认输入区与 RoPE 提示之外没有变化；正式中英文图注未修改。
