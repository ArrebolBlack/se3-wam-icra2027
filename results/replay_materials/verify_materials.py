"""Check extracted historical materials without creating an environment or policy."""
from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import platform
import sys
import xml.etree.ElementTree as ET


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify(root: Path, native: bool) -> dict:
    root = root.resolve()
    scene_path = root / "accepted/scenes/validation.jsonl"
    raw_scenes = [json.loads(line) for line in scene_path.read_text(encoding="utf-8").splitlines()]
    scenes = {row["scenario_id"]: row for row in raw_scenes}
    counts = Counter(row["task_id"] for row in raw_scenes)
    require(len(raw_scenes) == len(scenes) == 1400 and len(counts) == 14,
            "Expected 1,400 distinct scenes in fourteen tasks")
    require(set(counts.values()) == {100}, "Expected 100 scenes per task")
    all_selected = []
    for group, size, per_task, first_seed in (
        ("fixed140", 140, 10, 20260918),
        ("independent1260", 1260, 90, 20261058),
    ):
        rows = read_json(root / f"accepted/selections/{group}.json")
        original = read_json(root / f"provenance/evaluation_reference/{group}-selection.json")
        require(len(rows) == len(original) == size, f"{group}: count differs")
        require([row["index"] for row in rows] == list(range(size)), f"{group}: index order differs")
        require([row["inference_seed"] for row in rows] == list(range(first_seed, first_seed + size)),
                f"{group}: inference seeds differ")
        require(Counter(row["task_id"] for row in rows) == Counter({task: per_task for task in counts}),
                f"{group}: task counts differ")
        for row, before in zip(rows, original, strict=True):
            require(set(row) == {"index", "task_id", "scenario_id", "source_seed", "inference_seed",
                                 "suite", "shard_index", "shard_count"}, "Selection schema differs")
            require({k: v for k, v in row.items() if k != "suite"}
                    == {k: v for k, v in before.items() if k != "suite"},
                    "A non-path selection field was changed")
            task, ordinal = row["task_id"], row["shard_index"]
            require(type(ordinal) is int and ordinal in range(100) and row["shard_count"] == 100,
                    "Invalid task-local shard")
            require(row["scenario_id"] == f"v1:validation:{task}:{ordinal:06d}",
                    "Scenario/shard identity differs")
            require(row["suite"] == f"accepted/suites/sr_{task}.yaml" and (root / row["suite"]).is_file(),
                    "Portable suite path is missing or incorrect")
            scene = scenes[row["scenario_id"]]
            require(scene["task_id"] == task and scene["source_seed"] == row["source_seed"],
                    "Source seed or task does not match accepted scene")
        all_selected.extend(rows)
    require(len({row["scenario_id"] for row in all_selected}) == 1400,
            "Fixed and complementary selections overlap")
    require({row["scenario_id"] for row in all_selected} == scenes.keys(), "Selection omits a scene")
    for row in raw_scenes:
        require(row["schema_version"] == 1 and row["protocol_version"] == "v1"
                and row["partition"] == "validation" and row["factor"] is None,
                "Scene identity/schema differs")
        spec = row["scenario"]
        require(spec["action_mode"] == "E7" and spec["observation_profile"] == "agentview"
                and spec["physics_timestep_s"] == .002
                and spec["control_frequency_hz"] == spec["sensor_frequency_hz"] == 20,
                "Accepted action/observation/clock fields differ")
        require(spec["action_delay_steps"] == (1 if row["task_id"] == "t5_replan" else 0),
                "Native action delay differs")
    python_files = sorted((root / "benchmark-source").rglob("*.py"))
    for path in python_files:
        ast.parse(path.read_bytes(), filename=str(path.relative_to(root)))
    xml_files = sorted((root / "benchmark-source/assets").rglob("*.xml"))
    references = 0
    for path in xml_files:
        for node in ET.fromstring(path.read_bytes()).iter():
            if "file" in node.attrib:
                target = (path.parent / node.attrib["file"]).resolve()
                require(target.is_relative_to(root) and target.is_file(), "Missing or escaping asset reference")
                references += 1
    empty_manifests = sorted((root / "benchmark-source/manifests/v1").glob("*.jsonl"))
    require(len(empty_manifests) == 12 and all(path.stat().st_size == 0 for path in empty_manifests),
            "Original empty repository manifest placeholders differ")
    require("complete approved legal text" in (root / "benchmark-source/LICENSE").read_text(),
            "Historical license placeholder was replaced")
    for version in ("1.4.0", "1.5.2"):
        for name in ("LICENSE", "AUTHORS"):
            require((root / f"third_party/robosuite-{version}/{name}").is_file(), "Missing legal attribution")
    report = {
        "scope": "Material parsing, identity, and file-reference checks; no physics or policy execution",
        "scenes": 1400, "tasks": dict(counts), "fixed140": 140, "independent1260": 1260,
        "selection_overlap": 0, "source_seed_and_inference_seed_checks": "passed",
        "selection_non_path_fields_preserved": True, "python_syntax_files": len(python_files),
        "xml_files": len(xml_files), "xml_file_references": references,
        "original_empty_manifest_placeholders": 12, "native_parser": {"executed": False},
        "environment_constructed": False, "physics_steps": 0, "policy_calls": 0,
        "closed_loop_reproduction": False,
    }
    if native:
        sys.dont_write_bytecode = True
        require(not any(name.startswith("se3_wam_benchmark") for name in sys.modules),
                "Run the native parser in a fresh Python process")
        sys.path.insert(0, str(root / "benchmark-source/src"))
        import numpy
        import yaml
        from se3_wam_benchmark.scenarios import manifest
        from se3_wam_benchmark.scenarios.spec import scenario_to_dict
        from se3_wam_benchmark.tasks.registry import TASK_IDS, load_task, load_yaml_strict
        require(Path(manifest.__file__).resolve().is_relative_to(root / "benchmark-source/src"),
                "Native loader was imported from another checkout")
        parsed = manifest.load_manifest(scene_path)
        require(len(parsed) == 1400 and set(TASK_IDS) == set(counts), "Native parser/task registry differs")
        for before, after in zip(raw_scenes, parsed, strict=True):
            require(before["scenario"] == scenario_to_dict(after.scenario),
                    "Native parsing changes a scientific scenario field")
            require(before["scenario_id"] == after.scenario_id and before["source_seed"] == after.source_seed,
                    "Native parsing changes an identity")
        catalog = load_yaml_strict(root / "benchmark-source/assets/catalog.yaml")
        assets = {item["asset_id"]: item for item in catalog["assets"]}
        for item in assets.values():
            require((root / "benchmark-source" / item["path"]).is_file(), "Catalog asset missing")
        suite_changes = 0
        for task in TASK_IDS:
            require(load_task(task).task_id == task, "Native task load differs")
            load_yaml_strict(root / f"benchmark-source/configs/scenarios/{task}.yaml")
            portable = load_yaml_strict(root / f"accepted/suites/sr_{task}.yaml")
            original = load_yaml_strict(root / f"provenance/evaluation_reference/scenes/suites/sr_{task}.yaml")
            expected = json.loads(json.dumps(original))
            require(len(expected["members"]) == 1, "Expected one manifest per task suite")
            expected["members"][0]["manifest"] = "../scenes/validation.jsonl"
            require(portable == expected, "A suite field other than the manifest path changed")
            require(portable["suite_id"] == f"sr_{task}" and portable["repeats"] == 1
                    and portable["members"][0]["task_ids"] == [task], "Accepted suite identity differs")
            require((root / "accepted/suites" / portable["members"][0]["manifest"]).resolve() == scene_path,
                    "Suite does not resolve to accepted manifest")
            suite_changes += 1
        for row in raw_scenes:
            for item in row["scenario"]["object_states"] + row["scenario"]["fixture_states"]:
                require(item["asset_id"] in assets, "Scene asset is absent from historical catalog")
        report["native_parser"] = {
            "executed": True, "source": "benchmark-source/src/se3_wam_benchmark/scenarios/manifest.py",
            "python": platform.python_version(), "numpy": numpy.__version__, "pyyaml": yaml.__version__,
            "manifest_rows_parsed_and_roundtrip_equal": len(parsed), "tasks_loaded": len(TASK_IDS),
            "sampling_configurations_strict_yaml_loaded": len(TASK_IDS),
            "suite_configurations_strict_yaml_loaded": suite_changes,
            "suite_non_path_fields_preserved": True, "catalog_assets_resolved": len(assets),
            "suite_evaluator_load_suite_called": False,
            "note": "Native manifest and task loaders plus strict YAML loader only; evaluator import needs simulation dependencies.",
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--native", action="store_true", help="Use archived native schema and task loaders; needs NumPy and PyYAML")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.root, args.native)
    text = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
