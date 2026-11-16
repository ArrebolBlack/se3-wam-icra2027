# 绘图脚本与新机器复现

## 当前候选

[fig_latency_wide.py](fig_latency_wide.py) 和 [fig_timeline_v3.py](fig_timeline_v3.py) 使用脚本位置定位仓库，不依赖当前工作目录或 Claude 云端路径。默认字体 DejaVu Sans 随 Matplotlib 安装，默认输出到 `../fig4_study/`。两个脚本都会生成 PNG 和 PDF。

从仓库根目录执行（Python 3.12；以下为 PowerShell）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe docs/figures_20261116/scripts/fig_latency_wide.py
.\.venv\Scripts\python.exe docs/figures_20261116/scripts/fig_timeline_v3.py
```

Linux/macOS 使用 `.venv/bin/python`。绘图不需要 LaTeX、Blender 或联网取数据。输入全部在本仓库；来源及图的适用边界见[交接文档](../HANDOFF.md#3-数据来源与解释边界)。

默认命令会更新已跟踪的候选文件。试画可加 `--output-dir tmp/figure-study`；复用原稿字体可加 `--font "Liberation Sans"`，需事先安装该字体，缺失时明确报错。换字体后要查看文字宽度与裁切。当前默认字体已完成本机生成和目视检查。

## 历史脚本

以下文件为 Claude 原工作材料，完整保留，不属于当前两个候选的运行依赖；路径和早期协议/版式未统一迁移。

| 脚本 | 现状与依赖 |
|---|---|
| [fig_timeline_v2.py](fig_timeline_v2.py) | 三泳道旧版；输出硬编码 `/home/claude/`，使用 Liberation Sans |
| [fig_rank_disp.py](fig_rank_disp.py)、[fig_rank_latency.py](fig_rank_latency.py) | 旧单栏备选；Table 1 一位小数快照已核对，输出路径/字体需本地化 |
| [fig4_panels.py](fig4_panels.py) | 最早两个小图；保留旧协议画法，仅供历史追溯 |
| [fig4_C.py](fig4_C.py)、[fig4_arch.py](fig4_arch.py) | 已否决的版式；依赖未随材料提供的 `/tmp/otb_hi.png` 裁剪源和固定坐标，输出为云端路径 |
| [tab.py](tab.py)、[variants.py](variants.py) | Fig. 5 配色试验；需在仓库根目录运行并安装原字体，依赖当时的 plot_latency 布局，未重跑 |
| [recolor_svg.py](recolor_svg.py) | 早期 SVG/嵌入图换色函数；保留试验实现，正式渲染仍从各图项目构建 |
| [v8lib.py](v8lib.py) | 旧 Fig. 4 拼图工具；依赖工作目录内的 ontimebench.svg、rsvg-convert 和 Linux 字体路径，未附完整调用脚本 |
| [variant.py](variant.py)、[variant2.py](variant2.py) | Fig. 2 配色预览；依赖旧 build_paradigms、assets_raw 和 `/home/claude/src`，不是现行 Fig. 2 构建入口 |

这些缺失的云端中间文件不影响当前两个候选。需要继续历史版式时，先核对其原始素材和坐标，不能把当前 SVG 的任意渲染当成原裁剪源。现行 Fig. 2/4 的源码入口在各自图项目索引。
