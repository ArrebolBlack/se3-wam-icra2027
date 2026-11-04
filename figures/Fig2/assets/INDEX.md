# Fig2 真实素材

这些素材由当前 `../build_fig2.py` 读取；图中数据是录制观测和几何标签，动作图标与 pose glyph 大小为示意。

- [rgb.png](rgb.png)：同一 query 的原始 RGB 观测，224×224。
- [depth.png](depth.png)：同帧 metric depth 的线性蓝色显示，范围见来源记录。
- [geometry_labels.npz](geometry_labels.npz)：当前彩色工作区点云、196 点稀疏位移及有效性、目标位姿与历史，用于真实几何示例。
- [source.json](source.json)：原始轨迹与帧、相机、显示裁切、时域和箭头缩放的来源记录；核验素材时读取。
