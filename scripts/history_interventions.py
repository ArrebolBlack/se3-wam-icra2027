"""Summarize accepted HISTORY1 visual-history stress tests without model execution.

The inputs are native per-task reports, not newly recovered prediction arrays.
Run with --verify-archives to compare each report to its original local tar member.
Means are equal-task descriptive means of the original episode means. We do not
average confidence limits or treat correlated windows as independent samples.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
import tarfile

from common import add_research_argument, require, research_root


ARMS = ("cp_e", "cp_window", "cp_flow", "cp_flow12d", "cp_codec_mv",
        "cp_wan", "cp_pact_age", "cp_pact_uniform")
MODES = ("baseline_repeat", "self", "repeat_current", "reverse")
SITES = ("history_input", "fused_condition", "action_readout_tau0")
REPORTS = ("extract/manifest.json", "extract/controls.json",
           "extract/online-boundary.json", "readouts/scores.json",
           "readouts/intervention-scores.json")
IDENTITY = ("case", "task", "episode", "source_release_id", "frame",
            "timestamp_s", "split", "target_entity", "rotation_observable",
            "source_episode_id", "global_index")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def mean(values):
    values = list(values)
    require(bool(values) and all(math.isfinite(v) for v in values), "invalid mean")
    return math.fsum(values) / len(values)


def verify_archive(research, arm, report_root, records):
    archive = research / "local_private/history1-20261016" / ("retrieved-" + arm.replace("_", "-")) / "reports.tar"
    comparisons = {}
    with tarfile.open(archive) as saved:
        members = saved.getmembers()
        for relative in REPORTS:
            member = "probes/" + relative
            raw = saved.extractfile(member).read()
            require(json.loads(raw) == records[relative], f"archive report differs: {arm}/{relative}")
            copied = (report_root / relative).read_bytes()
            comparisons[member] = dict(
                semantic_equal=True, byte_equal=raw == copied,
                line_ending_normalized_equal=raw.replace(b"\r\n", b"\n") == copied.replace(b"\r\n", b"\n"))
        formal_npz = [m.name for m in members if m.isfile() and m.name.startswith("probes/") and m.name.endswith(".npz")]
    return dict(path=str(archive), compared_reports=comparisons,
                formal_probe_npz_members=len(formal_npz))


def validate(arm, records):
    manifest = records["extract/manifest.json"]
    require(manifest["complete"] and not manifest["smoke"] and manifest["arm"] == arm,
            f"incomplete/wrong source: {arm}")
    require(manifest["object_input_mode"] == "current" and manifest["noise_seeds"] == [17],
            f"unexpected condition/noise: {arm}")
    samples = manifest["samples"]
    require(len(samples) == 1050 and len({r["episode"] for r in samples}) == 350,
            f"wrong development denominator: {arm}")
    tasks = sorted({r["task"] for r in samples})
    require(len(tasks) == 14 and len({r["case"] for r in samples}) == 1050, f"bad identity: {arm}")
    for task in tasks:
        episodes = {}
        for split, expected in (("train", 15), ("validation", 5), ("test", 5)):
            selected = [r for r in samples if r["task"] == task and r["split"] == split]
            episodes[split] = {r["episode"] for r in selected}
            require(len(episodes[split]) == expected and len(selected) == expected * 3,
                    f"unexpected split: {arm}/{task}/{split}")
        require(not (episodes["train"] & episodes["validation"] or episodes["train"] & episodes["test"]
                     or episodes["validation"] & episodes["test"]), f"episode leakage: {arm}/{task}")
    controls = records["extract/controls.json"]["results"]
    expected_cases = {r["case"] for r in samples if r["split"] == "test"}
    require(len(controls) == 840, f"missing controls: {arm}")
    for mode in MODES:
        selected = [r for r in controls if r["mode"] == mode]
        require(len(selected) == 210 and {r["case"] for r in selected} == expected_cases,
                f"missing control cases: {arm}/{mode}")
        require(all(r["actual_initial_noise_equal"] and r["conditioned_baseline_equal"] for r in selected),
                f"unmatched noise/conditions: {arm}/{mode}")
        if mode in ("baseline_repeat", "self") or arm == "cp_e":
            require(all(all(v == 0 for v in r["max_abs_difference"].values()) for r in selected),
                    f"nonzero identity/negative control: {arm}/{mode}")
    boundary = records["extract/online-boundary.json"]
    require(boundary["accepted"] and boundary["applicable"] and len(boundary["steps"]) == 3,
            f"missing cache check: {arm}")
    require(all(s["old_gt_effect_exactly_zero"] and s["conditioning_cache_rebuild_exact"]
                for s in boundary["steps"]), f"cache boundary failed: {arm}")
    ordinary = [r for r in records["readouts/scores.json"]["results"] if "metrics" in r]
    report = records["readouts/intervention-scores.json"]
    require(len(ordinary) == 306 and len(report["results"]) == 306 * 4,
            f"missing readouts: {arm}")
    require(len(report["action_changes"]) == 14 * 4, f"missing action scores: {arm}")
    for row in report["action_changes"]:
        require(row["cases"] == 15 and row["episodes"] == 5, f"bad action denominator: {arm}")
        if row["mode"] in ("baseline_repeat", "self") or arm == "cp_e":
            require(all(v["mean"] == 0 for v in row["metrics"].values()), f"nonzero action control: {arm}")
    for row in report["results"]:
        require(row["cases"] == 15 and row["episodes"] == 5, f"bad probe denominator: {arm}")
        if row["mode"] in ("baseline_repeat", "self") or arm == "cp_e":
            require(all(v["physical_error_increase"]["mean"] == 0 and v["max_abs_readout_change"] == 0
                        for v in row["metrics"].values()), f"nonzero fixed-readout control: {arm}")
    return [{k: r[k] for k in IDENTITY} for r in samples]


def summarize(arm, records):
    report = records["readouts/intervention-scores.json"]
    rows = []
    for mode in ("repeat_current", "reverse"):
        changes = [r for r in report["action_changes"] if r["mode"] == mode]
        row = dict(arm=arm, mode=mode, tasks=14, episodes=70, windows=210,
                   noise_seed=17, action_horizon=8,
                   split="15/5/5 episode train/validation/test per task; 3 windows per episode",
                   averaging="Equal task mean of episode means; first_step is action index 0; chunk_mean averages 8 predicted actions",
                   translation_definition="L2 norm of the difference between corresponding action translation vectors; mm",
                   rotation_definition="SO(3) geodesic angle between the corresponding exp(rotvec) action rotations; degrees",
                   original_controls="840 native controls; equal initial Action/Flow noise and protected conditions; self/baseline_repeat exactly zero",
                   source_report=f"docs/experiments/HISTORY1/results/{arm}/probes/readouts/intervention-scores.json",
                   raw_prediction_recomputation=False)
        for stage in ("action_raw", "action_issued"):
            for horizon in ("first_step", "chunk_mean"):
                for original, converted, scale in (("translation_m", "translation_mm", 1000.),
                                                   ("rotation_rad", "rotation_deg", 180. / math.pi),
                                                   ("gripper_abs", "gripper_abs", 1.)):
                    key = f"{stage}__{horizon}__{original}"
                    row[f"{stage}__{horizon}__{converted}"] = mean(r["metrics"][key]["mean"] for r in changes) * scale
        for horizon in ("first_step", "chunk_mean"):
            # Issued E7 gripper commands are -1/+1, so an absolute difference of 2 is a flip.
            row[f"issued__{horizon}__gripper_flip_fraction"] = row[f"action_issued__{horizon}__gripper_abs"] / 2
        for site in SITES:
            for label, unit, scale, expected in (("future_translation_h8_m", "translation_mm", 1000., 14),
                                                 ("future_rotation_h8_rad", "rotation_deg", 180. / math.pi, 3)):
                selected = [r for r in report["results"] if r["mode"] == mode and r["site"] == site and r["label"] == label]
                require(len(selected) == expected and not any(r["oracle_determined"] for r in selected),
                        f"wrong future readout scope: {arm}/{mode}/{site}/{label}")
                for kind in ("retained", "residual_reconstruction"):
                    row[f"ridge__{site}__{kind}__h8_{unit}_error_increase"] = mean(
                        r["metrics"][kind]["physical_error_increase"]["mean"] for r in selected) * scale
        rows.append(row)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_research_argument(parser)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[1] / "figures/Fig5/archive/history_diagnostics/history_interventions.csv")
    parser.add_argument("--audit-output", type=Path)
    parser.add_argument("--verify-archives", action="store_true")
    args = parser.parse_args()
    args.research_root = research_root(args.research_root)
    output, audits, identity = [], {}, None
    for arm in ARMS:
        root = args.research_root / "docs/experiments/HISTORY1/results" / arm / "probes"
        records = {p: read(root / p) for p in REPORTS}
        current = validate(arm, records)
        require(identity is None or current == identity, f"cross-arm source/split mismatch: {arm}")
        identity = current
        output.extend(summarize(arm, records))
        audits[arm] = dict(source=str(root), completed_readouts=306, intervention_controls=840,
                          paired_case_metadata=True, raw_probe_array_pairing_verified=False)
        if args.verify_archives:
            audits[arm]["archive"] = verify_archive(args.research_root, arm, root, records)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    audit = dict(arms=audits, rows=len(output),
        aggregation="Equal-task mean of native per-task episode means; 14 tasks x 5 held-out episodes x 3 windows. Rotation probe means use only the 3 rotation-observable tasks (15 episodes / 45 windows). No aggregate CI is inferred from per-task CIs.",
        intervention="Replace the past seven visual RGB/depth/calibration frames with the current frame, or reverse those seven frames; keep current inputs, robot history, all object pose observations, clocks and masks unchanged. Re-encode each complete snapshot and rebuild conditioning.",
        interpretation="Descriptive dependence under input corruption, not physically matched alternative histories, better actions, online prediction use or closed-loop benefit. Ridge h8 error changes are fixed probe readouts of history/Meta/action-tau0 features, not the model SE3 prediction head.",
        raw_arrays="The accepted native per-task reports and metadata are available. Formal 1050-window probe NPZ arrays are not present in these local archives; this script does not claim cross-arm tensor or per-window metric recomputation.")
    if args.audit_output:
        args.audit_output.parent.mkdir(parents=True, exist_ok=True)
        args.audit_output.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(dict(csv=str(args.output), rows=len(output), arms=len(ARMS),
                          archives_verified=args.verify_archives, raw_probe_array_pairing_verified=False)))


if __name__ == "__main__":
    main()
