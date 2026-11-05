# Fig2 输入、监督示例与紧凑主干

这些素材由当前 `../build_fig2.py` 读取；RGB 为实录状态的 Blender 渲染，Depth 与几何标签来自原录制，动作图标与 pose glyph 大小为示意。

- [rgb.png](rgb.png)：第 29 帧实录状态的已采用 Blender 渲染，640×640；作为 RGB 输入示意。
- [depth.png](depth.png)：原录制第 29 帧 metric depth 的线性蓝色显示，范围见来源记录；与 Blender RGB 分别表示两种模态，不是逐像素配准的渲染对。
- [geometry_labels.npz](geometry_labels.npz)：当前彩色工作区点云、196 点稀疏位移及有效性、目标位姿与历史，用于真实几何示例。
- [source.json](source.json)：原始轨迹与帧、相机、显示裁切、时域和箭头缩放的来源记录；核验素材时读取。
- [原创机器人 SVG](robot_arm.svg)：从零绘制的透明背景机械臂；输入与动作输出直接读取原生矢量，不再使用论文裁图。
- [来源记录](source.json)的 `history_glyphs`：三枚缩小 SE(3) 字形的历史索引、共同浅色参考与累计运动显示方式；核对输入历史时读取。
- [原紧凑主干 SVG](backbone_v2.svg)、[布局](backbone_v2_layout.json)、[PDF](backbone_v2.pdf)：用户选定的竖向局部原稿；主图脚本读取原生对象后逆时针旋转。
