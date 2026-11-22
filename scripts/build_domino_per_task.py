"""Build the DOMINO per-task table from the archived Franka results."""

import re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from statistics import mean
from typing import NamedTuple

from common import REPO, TABLES, read_csv, read_json, require, tablelang


DATA = REPO / "results/domino_baselines"
METHODS = ("pi05", "dynamicwam", "puma", "foveawam")
GROUP_SIZES = {"Intercept": 8, "Track": 16}
GROUP_LABELS = {"Intercept": "拦截", "Track": "跟踪"}
TASK_LABELS = {
    "place_a2b_left": "Place A2B Left",
    "place_a2b_right": "Place A2B Right",
    "rotate_qrcode": "Rotate QRcode",
    "shake_bottle_horizontally": "Shake Bottle Horiz.",
}


class Scores(NamedTuple):
    sr: Decimal
    ms: Decimal


def rounded(value, digits=1):
    return Decimal(str(value)).quantize(Decimal(1).scaleb(-digits), rounding=ROUND_HALF_UP)


def load_tasks():
    rows = read_csv(DATA / "per-task-20261122.csv")
    require(len(rows) == 96, "Expected 96 task/method rows")
    groups = {name: {} for name in GROUP_SIZES}
    for row in rows:
        task, group, method = row["task"], row["group"], row["method"]
        require(group in groups and method in METHODS, f"Unknown group or method in {row}")
        methods = groups[group].setdefault(task, {})
        require(method not in methods, f"Duplicate row for {task}/{method}")
        sr, ms = Decimal(row["sr_percent"]), Decimal(row["ms"])
        require(0 <= sr <= 100 and sr == rounded(sr, 0), f"Invalid SR for {task}/{method}")
        require(0 <= ms <= 100 and ms == rounded(ms, 2), f"Invalid MS for {task}/{method}")
        methods[method] = Scores(sr, ms)

    for group, tasks in groups.items():
        require(len(tasks) == GROUP_SIZES[group], f"Wrong number of tasks in {group}")
        for task, methods in tasks.items():
            require(set(methods) == set(METHODS), f"Missing methods for {task}")
    require(groups["Intercept"].keys().isdisjoint(groups["Track"]), "Task in both groups")
    return groups


def check_scenes(groups):
    scenes = defaultdict(dict)
    for row in read_csv(DATA / "foveawam-epoch24-scenes.csv"):
        task, group, seed = row["task"], row["group"], row["seed"]
        require(task in groups.get(group, {}), f"Unexpected scene task or group: {task}/{group}")
        require(seed not in scenes[task], f"Duplicate scene for {task}/{seed}")
        require(row["success"] in ("True", "False"), f"Invalid success flag for {task}/{seed}")
        scenes[task][seed] = (row["success"] == "True", Decimal(row["manipulation_score"]))

    for tasks in groups.values():
        for task, methods in tasks.items():
            records = scenes[task].values()
            require(len(records) == 100, f"Expected 100 FoveaWAM scenes for {task}")
            sr = sum(success for success, _ in records)
            ms = rounded(mean(score for _, score in records), 2)
            require((sr, ms) == methods["foveawam"], f"FoveaWAM scene scores disagree for {task}")


def task_means(tasks):
    return {method: Scores(mean(row[method].sr for row in tasks),
                           mean(row[method].ms for row in tasks)) for method in METHODS}


def check_summary(means):
    formal = read_json(DATA / "w5-formal-20261111.json")["methods"]
    for method, name in (("pi05", "π₀.₅"), ("dynamicwam", "DynamicWAM"), ("puma", "PUMA")):
        for group, scores in means.items():
            expected = formal[name][group]
            require(abs(scores[method].sr - Decimal(str(expected["SR"]))) < Decimal("1e-9"),
                    f"{name}/{group} SR differs from the formal result")
            require(abs(scores[method].ms - Decimal(str(expected["MS"]))) < Decimal("0.01"),
                    f"{name}/{group} MS differs from the formal result")

    main_rows = {}
    labels = {r"$\pi_{0.5}$": "pi05", "DynamicWAM": "dynamicwam", "PUMA": "puma",
              r"\oursentry": "foveawam"}
    for line in (TABLES / "main_external.tex").read_text(encoding="utf-8").splitlines():
        cells = line.strip().removesuffix(r"\\").split("&")
        label = cells[0].strip()
        if label in labels:
            method = labels[label]
            require(method not in main_rows, f"Duplicate main table row for {method}")
            main_rows[method] = [re.sub(r"\\(?:best|second)cell\{([0-9.]+)\}", r"\1", cell.strip())
                                 for cell in cells[1:]]
    for method in METHODS:
        scores = [means[group][method].sr for group in ("Intercept", "Track", "All")]
        scores.append(means["All"][method].ms)
        require([str(rounded(value)) for value in scores] == main_rows.get(method),
                f"DOMINO means disagree with tables/main_external.tex for {method}")


def table_row(label, scores, sr_digits):
    sr = [rounded(scores[m].sr, sr_digits) for m in METHODS]
    ms = [rounded(scores[m].ms) for m in METHODS]
    best_sr, best_ms = max(sr), max(ms)
    cells = [label]
    for success, score in zip(sr, ms):
        cells.append(rf"\bestcell{{{success}}}" if success == best_sr else str(success))
        cells.append(rf"\bestcell{{{score}}}" if score == best_ms else str(score))
    return " & ".join(cells) + r" \\"


def main():
    groups = load_tasks()
    check_scenes(groups)
    means = {group: task_means(tasks.values()) for group, tasks in groups.items()}
    means["All"] = task_means([row for tasks in groups.values() for row in tasks.values()])
    check_summary(means)

    lines = [
        "% Generated by scripts/build_domino_per_task.py from results/domino_baselines/per-task-20261122.csv.",
        r"\tablelang{\begin{table*}[!t]}{\begin{table}[H]}",
        r"\centering\footnotesize",
        r"\caption{\tablelang{\textbf{Per-task SR} (\%) \textbf{and MS} on DOMINO. Each method is evaluated "
        r"on the same 100 scenes per task. MS: manipulation score. Bold marks the best value.}"
        r"{\textbf{DOMINO 上的逐任务成功率}（\%）\textbf{和操作得分}。每个方法都在相同的 100 个场景上评测每个任务。"
        r"MS：操作得分。粗体标出最佳值。}}",
        r"\label{tab:supp_domino_per_task}",
        r"\setlength{\tabcolsep}{3pt}",
        r"\renewcommand{\arraystretch}{0.95}",
        r"\begin{tabular}{@{}l*{8}{>{\centering\arraybackslash}p{0.44in}}}",
        r"\toprule",
        r" & \multicolumn{2}{c}{$\pi_{0.5}$} & \multicolumn{2}{c}{DynamicWAM} & "
        r"\multicolumn{2}{c}{PUMA} & \multicolumn{2}{c}{\oursname{} \tablelang{(Ours)}{（本文）}} \\",
        r"\cmidrule(lr){2-3}\cmidrule(lr){4-5}\cmidrule(lr){6-7}\cmidrule(lr){8-9}",
        r"\tablelang{Task}{任务} & SR & MS & SR & MS & SR & MS & SR & MS \\",
    ]
    for group, tasks in groups.items():
        lines.append(r"\midrule")
        lines.append(r"\multicolumn{9}{@{}l}{\emph{" + tablelang(group, GROUP_LABELS[group]) + r"}} \\")
        for task in sorted(tasks):
            label = TASK_LABELS.get(task, task.replace("_", " ").title())
            lines.append(table_row(label, tasks[task], sr_digits=0))
    lines.append(r"\midrule")
    summary = []
    for group, label in (("Intercept", "拦截均值"), ("Track", "跟踪均值"), ("All", "全部")):
        english = group if group == "All" else group + " mean"
        summary.append(table_row(tablelang(english, label), means[group], sr_digits=1))
    lines.extend([*summary, r"\bottomrule", r"\end{tabular}", r"\tablelang{\end{table*}}{\end{table}}"])
    (TABLES / "supp_domino_per_task.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
