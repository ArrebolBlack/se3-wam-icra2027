"""Export S4 from accepted Native scenes and compute conditional paired intervals.

No policy is run. Baseline scene identity was checked by the archived experiment
auditors; their compact CSVs retain the common selection index and task. C's raw
joined records are checked against the full common selection again here.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np

from common import REPO, add_research_argument, require, research_root, write_csv
from paired_uncertainty import CELLS, SEED, paired_interval

METHODS = ("act", "dp", "pi05", "pi05_se3", "dynamicvla", "puma",
           "openwam_official", "openwam", "dynamicwam", "dynamicwam_se3", "se3_wam")
TASKS = ("grasp", "t1_belt", "t1_xyz", "t1_so3", "t1_occ", "t2_trans", "t2_se3",
         "t3_phase", "t3_full", "t4_sphere", "t4_sphere_tabletop", "t4_slider",
         "t4_can", "t5_replan")
BASE = Path("docs/experiments/INFER0/results")
OUTPUT = BASE / "c-bf16-table1-fig4-20261104"
STEM = "native-per-task-20261104"
CELL = {(True, True): 0, (True, False): 1, (False, True): 2, (False, False): 3}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                    encoding="utf-8")


def read_archive(path, summaries_member, scenes_member):
    with ZipFile(path) as archive:
        summaries = json.loads(archive.read(summaries_member))
        scenes = list(csv.DictReader(io.StringIO(archive.read(scenes_member).decode("utf-8-sig"))))
    return summaries, scenes


def native_scenes(rows, selection):
    result = {}
    for row in rows:
        if not row["phase"].endswith("-native"):
            continue
        method = row["phase"].removesuffix("-native")
        index = int(row["index"])
        require(row["success"] in ("True", "False"), "Non-binary baseline result")
        require(row["task"] == selection[index]["task_id"], "Baseline task/index mismatch")
        group = result.setdefault(method, {})
        require(index not in group, f"Duplicate baseline scene {method}/{index}")
        group[index] = row["success"] == "True"
    return result


def c_native(source, selection):
    accepted, summary = load(source / "accepted.json"), load(source / "summary.json")
    require(accepted["accepted"] and accepted["episodes"] == 1400 and not accepted["errors"],
            "C Native has not passed scientific acceptance")
    result, samples = {}, None
    for node in range(2):
        with ZipFile(source / f"node-{node}-joined.zip") as archive:
            for name in archive.namelist():
                record = json.loads(archive.read(name))
                joined, run = record["joined"], record["run"]
                index = joined["selection_index"]
                require(index not in result, f"Duplicate C scene {index}")
                for key in ("index", "task_id", "scenario_id", "source_seed", "inference_seed",
                            "shard_index", "shard_count"):
                    require(run["selection"][key] == selection[index][key], f"C scene identity: {key}")
                for key in ("task_id", "scenario_id", "source_seed"):
                    require(joined[key] == selection[index][key], f"C joined identity: {key}")
                execution = run["execution"]
                require(joined["protocol"] == execution["protocol"] == "realtime" and
                        execution["extra_latency_s"] == 0 and execution["seed"] == 20261023,
                        "S4 must use Native real-time +0 ms")
                require(run["config"]["compute"] == dict(precision="bf16", allow_tf32=False, compile=True),
                        "C must use the accepted compiled BF16 route")
                current_samples = execution["latency_samples_s"]
                if samples is None:
                    samples = current_samples
                require(current_samples == samples and len(samples) == 900, "Inconsistent latency replay")
                require(type(joined["success"]) is bool, "Non-binary C result")
                result[index] = joined["success"]
    require(sorted(result) == list(range(1400)), "Incomplete C Native scenes")
    require(sum(result.values()) == accepted["successes"] == summary["overall"]["successes"],
            "C accepted/summary/raw marginal mismatch")
    timing = dict(samples=900, p50_ms=float(np.percentile(samples, 50) * 1000),
                  p95_ms=float(np.percentile(samples, 95) * 1000), maximum_ms=max(samples) * 1000)
    require(abs(timing["p95_ms"] - 15.113406878663227) < 1e-9, "Unexpected accepted latency array")
    return result, summary, accepted, timing


def highlighted(values, lower=False):
    # Rank the displayed one-decimal values so equal printed values share a rank.
    rounded = [None if value is None else round(value, 1) for value in values]
    levels = sorted({value for value in rounded if value is not None}, reverse=not lower)
    cells = []
    for value in rounded:
        if value is None:
            cells.append("--")
        elif value == levels[0]:
            cells.append(r"\bestcell{" + f"{value:.1f}" + "}")
        elif len(levels) > 1 and value == levels[1]:
            cells.append(r"\secondcell{" + f"{value:.1f}" + "}")
        else:
            cells.append(f"{value:.1f}")
    return cells


def delta_cell(interval):
    delta, low, high = (interval[key] for key in ("delta_pp", "ci95_low_pp", "ci95_high_pp"))
    return rf"\dcell{{{delta:.1f}}}{{{delta:+.1f} [{low:.1f}, {high:.1f}]}}"


def write_table(document):
    path = REPO / "tables/supp_per_task.tex"
    lines = path.read_text(encoding="utf-8").splitlines()
    lines[0] = f"% Generated by scripts/build_realtime_per_task.py from results/realtime_c/{STEM}.json."
    lines[1] = "% Native real-time: measured method-specific inference latency + 0 ms extra; one training seed."
    lines[4:8] = [
        r"\caption{\tablelang{\textbf{Per-task held-out success} (\%) on \bench for every method of Table~\mainref{tab:main}, Native real-time protocol: each method's measured inference latency plus \textbf{+0\,ms extra delay}, with physics continuing during inference; 100 paired scenes per task. \ours uses compiled BF16 C (p95 15.1\,ms). DP: Diffusion Policy. DVLA: DynamicVLA. OWAM: OpenWAM-$\alpha$ with official cache/compile; OW-off: both disabled.",
        r"DWAM: DynamicWAM. +: with our SE(3) history tokens. $\Delta$: \ours minus the strongest other method on that task; ties follow table order. The task-balanced row compares against the strongest overall baseline, PUMA. Brackets give pointwise 95\% paired scene-bootstrap intervals, conditional on the selected comparator and checkpoint (100,000 resamples; no selection adjustment). The last two rows give first-contact position error $e_p$ (mm), averaged over the 13 contact tasks, and the number $n$ of episodes with a contact (Appendix~\ref{app:metrics}); --: no complete 13-task mean. $\Delta$ shading is blue for higher SR and orange for lower, saturating at 15 points. Blue/bold and light blue mark the best and second-best displayed values.}{\textbf{\bench 各任务的留出成功率}（\%），涵盖表~\mainref{tab:main} 的全部方法，采用 Native 实时协议：各方法实测推理延迟加\textbf{额外 +0\,ms}，推理期间物理持续推进；每任务 100 个配对场景。\ours 使用编译 BF16 版 C（p95 为15.1\,ms）。",
        r"DP：Diffusion Policy。DVLA：DynamicVLA。OWAM：官方缓存与编译的 OpenWAM-$\alpha$；OW-off：关闭两者。DWAM：DynamicWAM。+：本文 SE(3) 历史 token。",
        r"$\Delta$ 为 \ours 减去该任务最强其他方法；并列时按表中顺序选择。任务等权行与整体最强基线 PUMA 比较。括号为以所选对照与检查点为条件的逐项 95\% 配对场景 bootstrap 区间（100,000 次重采样，不校正选择偏差）。末两行为首次接触位置误差 $e_p$（mm，13 个接触任务等权平均）与发生接触的回合数 $n$（附录~\ref{app:metrics}）；--：无完整13任务均值。$\Delta$ 底色蓝色表示较高 SR、橙色表示较低，在15个百分点处饱和。粗体蓝底与浅蓝底标出显示值的最佳与次佳。}}",
    ]
    task_index = 0
    for index, line in enumerate(lines):
        if line.startswith(r"\tablelang{") and " & " in line and not line.startswith(r"\tablelang{Task}"):
            label = line.split(" & ")[0]
            if "Task-balanced" in line:
                values = [document["overall"][method]["sr_percent"] for method in METHODS]
                interval = document["comparisons"][-1]
            else:
                task = TASKS[task_index]
                values = [document["per_task"][task][method]["sr_percent"] for method in METHODS]
                interval = document["comparisons"][task_index]
                task_index += 1
            lines[index] = " & ".join([label, *highlighted(values), delta_cell(interval)]) + r" \\"
        elif line.startswith("$e_p$"):
            values = [document["overall"][method]["e_p_mm"] for method in METHODS]
            lines[index] = " & ".join(["$e_p$ (mm)", *highlighted(values, lower=True), "--"]) + r" \\"
        elif line.startswith("$n$"):
            values = [str(document["overall"][method]["contacts"]) for method in METHODS]
            lines[index] = " & ".join(["$n$", *values, "--"]) + r" \\"
    require(task_index == 14, "Unexpected S4 row template")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_research_argument(parser)
    parser.add_argument("--c-native-results", type=Path, required=True)
    parser.add_argument("--research-output", type=Path, required=True,
                        help="INFER0 result directory in the writing Research checkout")
    args = parser.parse_args()
    root = research_root(args.research_root)
    selection_list = load(root / BASE / "realtime-c-heldout/selection.json")
    selection = {row["index"]: row for row in selection_list}
    require(sorted(selection) == list(range(1400)) and len(selection_list) == 1400,
            "Expected unique common 1400-scene selection")
    require(all(sum(row["task_id"] == task for row in selection_list) == 100 for task in TASKS),
            "Expected 14 equal-size tasks")
    baseline_path = root / BASE / "realtime-c-table1-rollout/formal64-accepted-20261101/acceptance-evidence.zip"
    summaries, rows = read_archive(baseline_path, "summaries.json", "table1-scenes.csv")
    with ZipFile(baseline_path) as archive:
        reused = json.loads(archive.read("dynamicwam-se3-reused-join.json"))
    require(not reused["errors"], "Reused DynamicWAM+SE(3) join has errors")
    summaries["dynamicwam_se3-native"] = reused["groups"]["native"]
    puma_path = root / BASE / "realtime-c-puma-20261102/acceptance-evidence.zip"
    puma_summaries, puma_rows = read_archive(puma_path, "acceptance/summaries.json", "acceptance/puma-scenes.csv")
    summaries.update(puma_summaries)
    scenes = native_scenes(rows + puma_rows, selection)
    c_scenes, c_summary, accepted, timing = c_native(args.c_native_results, selection)
    scenes["se3_wam"] = c_scenes
    summaries["se3_wam-native"] = c_summary
    per_task, overall = {task: {} for task in TASKS}, {}
    table1 = load(REPO / "results/realtime_c/table1-20261104.json")
    table1_native = {row["method"]: row for row in table1["rows"] if row["protocol"] == "native"}
    for method in METHODS:
        summary = summaries[f"{method}-native"]
        if method != "dynamicwam_se3":
            execution = summary["instance"]["execution"]
            require(execution["protocol"] == "realtime" and execution["extra_latency_s"] == 0,
                    f"Non-Native source {method}")
        require(summary["overall"]["episodes"] == 1400, f"Incomplete summary {method}")
        if method in scenes:
            require(sorted(scenes[method]) == list(range(1400)), f"Incomplete scenes {method}")
            require(sum(scenes[method].values()) == summary["overall"]["successes"],
                    f"Raw/summary marginal mismatch {method}")
        total = 0
        for task in TASKS:
            metric = summary["per_task"][task]
            require(metric["episodes"] == 100, f"Unequal task denominator {method}/{task}")
            successes = metric["successes"]
            if method in scenes:
                require(sum(value for index, value in scenes[method].items()
                            if selection[index]["task_id"] == task) == successes,
                        f"Raw/task marginal mismatch {method}/{task}")
            per_task[task][method] = dict(episodes=100, successes=successes, sr_percent=float(successes))
            total += successes
        require(total == summary["overall"]["successes"], f"Task/overall mismatch {method}")
        require(total == table1_native[method]["successes"], f"S4/Table 1 Native mismatch: {method}")
        require(abs(100 * total / 1400 - table1_native[method]["sr_percent"]) < 1e-12,
                f"S4/Table 1 Native mean mismatch: {method}")
        contact = summary["contact_task_macro"]["contact_position_error_m"]
        overall[method] = dict(episodes=1400, successes=total, sr_percent=100 * total / 1400,
                              e_p_mm=None if contact["complete_13_task_mean"] is None
                              else 1000 * contact["complete_13_task_mean"],
                              contacts=summary["overall"]["contact_count"])
        mean = sum(per_task[task][method]["sr_percent"] for task in TASKS) / 14
        require(abs(mean - overall[method]["sr_percent"]) < 1e-12, "Task-equal mean mismatch")
    comparisons = []
    for task_index, task in enumerate((*TASKS, "task_balanced")):
        metrics = overall if task == "task_balanced" else per_task[task]
        best = max(metrics[method]["successes"] for method in METHODS[:-1])
        ties = [method for method in METHODS[:-1] if metrics[method]["successes"] == best]
        reference = ties[0]
        require(reference in scenes, f"Missing scene pairs for selected reference {reference}")
        selected_tasks = TASKS if task == "task_balanced" else (task,)
        counts = {name: [0, 0, 0, 0] for name in selected_tasks}
        for index, row in selection.items():
            if row["task_id"] in counts:
                counts[row["task_id"]][CELL[(c_scenes[index], scenes[reference][index])]] += 1
        result = paired_interval(counts, seed=SEED + task_index)
        require(abs(result["delta_pp"] - (metrics["se3_wam"]["sr_percent"] -
                                          metrics[reference]["sr_percent"])) < 1e-12,
                "Paired difference/marginal mismatch")
        comparisons.append(dict(task_id=task, arm="se3_wam", reference=reference,
                                tied_strongest_methods=ties, selection_adjusted=False,
                                cells_by_task=dict(zip(counts, (dict(zip(CELLS, cell)) for cell in counts.values()))),
                                **result))
    document = dict(protocol="Native real-time: measured per-method inference latency + 0 ms extra; physics continues",
                    training_seeds_per_method=1, scene_pairing="common held-out selection index and task; source/inference seeds checked by source auditors; C identities rechecked here",
                    strongest_baseline_selection="highest observed task SR, ties resolved by Table 1 method order; fixed comparator during bootstrap; task-balanced row selects by overall SR",
                    methods=list(METHODS), tasks=list(TASKS), timing_c=timing, c_acceptance=accepted,
                    sources=dict(selection=str(BASE / "realtime-c-heldout/selection.json"),
                                 baselines=str(baseline_path.relative_to(root)), puma=str(puma_path.relative_to(root)),
                                 c="native/accepted.json, summary.json and node-{0,1}-joined.zip in the accepted BF16 evidence"),
                    overall=overall, per_task=per_task, comparisons=comparisons)
    # Compact scene records preserve each actual success bit used by the interval.
    # DynamicWAM+SE(3) is aggregate-only here and is never the selected comparator.
    scene_rows = [dict(index=index, task_id=row["task_id"], scenario_id=row["scenario_id"],
                       source_seed=row["source_seed"], inference_seed=row["inference_seed"],
                       **{method: scenes[method][index] for method in METHODS if method in scenes})
                  for index, row in sorted(selection.items())]
    paper_output = REPO / "results/realtime_c"
    args.research_output.mkdir(parents=True, exist_ok=True)
    for output in (args.research_output, paper_output):
        dump(output / f"{STEM}.json", document)
        write_csv(output / f"{STEM}-scenes.csv", scene_rows)
        write_csv(output / f"{STEM}-intervals.csv", [{key: value for key, value in row.items()
                                                   if key not in ("cells_by_task", "tied_strongest_methods")}
                                                  for row in comparisons])
    write_table(document)
    print(json.dumps(dict(methods=11, tasks=14, matched_scenes=1400, comparisons=len(comparisons),
                          native_successes=overall["se3_wam"]["successes"],
                          native_task_equal_sr=overall["se3_wam"]["sr_percent"],
                          overall_delta=comparisons[-1]["delta_pp"],
                          overall_interval=[comparisons[-1]["ci95_low_pp"], comparisons[-1]["ci95_high_pp"]])))


if __name__ == "__main__":
    main()
