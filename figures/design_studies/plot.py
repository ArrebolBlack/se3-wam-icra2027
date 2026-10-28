"""Render accepted appendix design studies in English and Chinese.

    python figures/design_studies/plot.py

No simulation, smoothing, or invented uncertainty. Source mapping: SOURCE.md.
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
import numpy as np

HERE = Path(__file__).resolve().parent
BLUE, ORANGE, GRAY = "#1674AB", "#C95318", "#4D4D4D"


def records(name):
    with (HERE / "data" / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def save(fig, stem, lang):
    suffix = "_zh" if lang == "zh" else ""
    for ext in ("pdf", "svg", "png"):
        output = HERE / f"{stem}{suffix}.{ext}"
        fig.savefig(output, dpi=300, facecolor="white")
        if ext == "svg":
            output.write_text("\n".join(line.rstrip() for line in output.read_text(encoding="utf-8").splitlines())+"\n", encoding="utf-8")
    plt.close(fig)


def history(lang):
    zh = lang == "zh"
    rows = records("history.csv")
    assert len(rows) == 8
    fig = plt.figure(figsize=(6.875, 3.05))
    ax = fig.add_axes([.285, .19, .285, .61])
    ax.set(xlim=(-12, 10), ylim=(7.7, -.7), xticks=[-10, -5, 0, 5, 10])
    ax.set_yticks(range(8), [r[f"label_{lang}"] for r in rows], fontsize=7.6)
    ax.tick_params(axis="y", length=0, pad=5)
    ax.spines["left"].set_visible(False)
    ax.axvline(0, color=GRAY, lw=.7)
    ax.grid(axis="x", color="#E5E5E5", lw=.5)
    for i, row in enumerate(rows):
        d, lo, hi = (float(row[k]) for k in ("delta", "ci_low", "ci_high"))
        assert lo <= d <= hi
        ax.errorbar(d, i, xerr=[[d-lo], [hi-d]], fmt="o", ms=3.5,
                    color=BLUE if d > 0 else ORANGE, elinewidth=1, capsize=2)
        ax.text(1.045, i, f"{float(row['sr']):.2f}", transform=ax.get_yaxis_transform(),
                va="center", fontsize=7.4)
        ax.text(1.265, i, f"{d:+.2f}", transform=ax.get_yaxis_transform(),
                va="center", fontsize=7.4)
    ax.set_xlabel("成功率差值（百分点）" if zh else "SR difference (percentage points)")
    fig.text(.015, .94, "(a) 分别训练的输入变体" if zh else "(a) Separately trained input variants", weight="bold", fontsize=9)
    fig.text(.015, .875, "当前图像参照：53.43% SR" if zh else "Current-image reference: 53.43% SR", color=GRAY)
    fig.text(.583, .83, "SR (%)", fontsize=7.5, weight="bold")
    fig.text(.646, .83, "ΔSR", fontsize=7.5, weight="bold")
    fig.add_artist(Line2D([.706,.706],[.12,.96],transform=fig.transFigure,color="#CCCCCC",lw=.6))
    bx = fig.add_axes([.75, .38, .23, .37])
    bx.set(xlim=(0, 100), ylim=(-.5, 1.55), yticks=[], xticks=[0,50,100])
    bx.spines["left"].set_visible(False)
    bx.grid(axis="x", color="#EAEAEA", lw=.5)
    bx.set_axisbelow(True)
    labels = ["真实历史" if zh else "True history", "静止历史" if zh else "Stationary history"]
    for y, sr, color, label in zip([1,0], [58.86,.64], [BLUE,ORANGE], labels):
        bx.barh(y, sr, height=.28, color=color)
        bx.text(0,y+.25,label,fontsize=7.5,va="bottom")
        bx.text(sr+3,y,f"{sr:.2f}",fontsize=7.5,va="center")
    bx.set_xlabel("SR (%)")
    fig.text(.745,.94,"(b) 固定检查点" if zh else "(b) Fixed checkpoint",weight="bold",fontsize=9)
    fig.text(.745,.875,"仅在测试时替换历史" if zh else "Test-time replacement",color=GRAY,fontsize=8)
    fig.text(.745,.20,"ΔSR = −58.21 pp\n95% CI [−59.86, −56.50]",fontsize=7.8,linespacing=1.6,va="top")
    fig.text(.015,.035,"单训练种子；区间为给定检查点后的场景配对 95% 区间。" if zh else
             "One training seed; pointwise paired 95% scene intervals, conditional on checkpoints.",fontsize=7.5,color=GRAY)
    save(fig,"history",lang)


def prediction_path(lang):
    zh = lang == "zh"
    rows = records("prediction_path.csv")
    grouped = {}
    for row in rows:
        n, s = int(row["episodes"]), int(row["successes"])
        assert n == 1400 and 0 <= s <= n
        key = row["study"], row["path"], row["representation"]
        grouped.setdefault(key, {})[int(row["seed"])] = s/n*100
    expected = {("cnn","direct","2D"):(63.45,2.94), ("cnn","direct","3D"):(64.19,.60),
                ("cnn","future_stream","2D"):(56.83,5.41), ("cnn","future_stream","3D"):(58.19,3.19),
                ("dino","direct","2D"):(62.71,1.65), ("dino","direct","3D"):(62.21,1.82)}
    assert set(grouped) == set(expected)
    for key, (mean, sd) in expected.items():
        values = grouped[key]
        assert set(values) == {0,1,2}
        assert round(np.mean(list(values.values())),2) == mean
        assert round(np.std(list(values.values()),ddof=1),2) == sd
    fig, axes = plt.subplots(1, 2, figsize=(6.875,2.65), sharey=True,
                             gridspec_kw={"width_ratios":[1.6,1]})
    fig.subplots_adjust(left=.08,right=.985,bottom=.23,top=.74,wspace=.22)
    specs = [(axes[0],"cnn",[("direct","2D"),("direct","3D"),("future_stream","2D"),("future_stream","3D")]),
             (axes[1],"dino",[("direct","2D"),("direct","3D")])]
    markers = ["o","s","^"]
    for ax, study, categories in specs:
        for i,(path, rep) in enumerate(categories):
            vals = np.array([grouped[study,path,rep][s] for s in range(3)])
            color = BLUE if path == "direct" else ORANGE
            for seed, (offset, val) in enumerate(zip([-.12,0,.12],vals)):
                ax.plot(i+offset,val,marker=markers[seed],color=color,ms=4,linestyle="none",alpha=.8)
            ax.errorbar(i+.26, vals.mean(), yerr=vals.std(ddof=1), fmt="D",color="black",
                        ms=3,elinewidth=.9,capsize=2)
            ax.text(i,49.7,f"{vals.mean():.2f} ± {vals.std(ddof=1):.2f}",ha="center",fontsize=7.2)
        ax.set_ylim(48.5,70)
        ax.set_yticks([50,55,60,65,70])
        ax.set_xlim(-.4,len(categories)-.35)
        ax.set_xticks(range(len(categories)), [f"{r}\n"+(("直接" if p=="direct" else "Future 流") if zh else ("Direct" if p=="direct" else "Future stream")) for p,r in categories])
        ax.grid(axis="y",color="#E6E6E6",lw=.5)
        ax.set_axisbelow(True)
    axes[0].set_ylabel("成功率 SR (%)" if zh else "Success rate (%)")
    fig.text(.08,.94,"(a) CNN，无未来外观目标" if zh else "(a) CNN, no future appearance targets",weight="bold",fontsize=9)
    fig.text(.64,.94,"(b) DINOv3-L，三辅助全开" if zh else "(b) DINOv3-L, all appearance targets",weight="bold",fontsize=9)
    handles=[Line2D([],[],marker=m,color=GRAY,linestyle="none",ms=4,label=f"种子 {s}" if zh else f"Seed {s}") for s,m in enumerate(markers)]
    handles += [Line2D([],[],marker="D",color="black",ms=3,label="均值 ± 样本标准差" if zh else "Mean ± sample SD")]
    fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.52,.88),ncol=4,frameon=False,fontsize=7.5)
    fig.text(.08,.025,"每个种子 1,400 场；仅在同一面板内比较。" if zh else "1,400 scenes per seed; compare within a panel.",fontsize=7.5,color=GRAY)
    save(fig,"prediction_path",lang)


def main():
    font_manager.fontManager.addfont(r"C:\Windows\Fonts\msyh.ttc")
    for lang in ("en","zh"):
        with plt.rc_context({"font.family":"Microsoft YaHei" if lang=="zh" else "Arial",
                             "font.size":8,"pdf.fonttype":42,"svg.fonttype":"none",
                             "axes.spines.top":False,"axes.spines.right":False,
                             "axes.linewidth":.6,"xtick.major.size":3,"ytick.major.size":3}):
            history(lang)
            prediction_path(lang)
    print("Rendered EN/ZH history and prediction-path figures; all six seed means/SDs verified.")


if __name__ == "__main__":
    main()
