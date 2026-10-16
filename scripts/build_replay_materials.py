"""Package the original benchmark evaluator and accepted scene pool for local review."""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import zipfile


ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "results/replay_materials"


def encoded(value):
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def build(history_archive: Path, evaluation_archive: Path, destination: Path):
    payload = {}
    copied = []
    def copy(path, data, source, member):
        require(path not in payload and ".." not in PurePosixPath(path).parts, "Duplicate or unsafe package path")
        payload[path] = data
        copied.append({"path": path, "source": source, "member": member, "bytes": len(data)})

    with tarfile.open(history_archive) as history:
        members = [m for m in history.getmembers() if m.name.startswith("benchmark-source/")]
        require(len(members) == 171 and all(m.isfile() for m in members), "Historical benchmark file set differs")
        for member in members:
            copy(member.name, history.extractfile(member).read(), "history_archive", member.name)
        copy("provenance/asset-bundle.json", history.extractfile("asset-bundle.json").read(),
             "history_archive", "asset-bundle.json")
        wheel_member = "wheels/robosuite-1.5.2-py3-none-any.whl"
        with zipfile.ZipFile(io.BytesIO(history.extractfile(wheel_member).read())) as wheel:
            require(payload["benchmark-source/assets/textures/red-wood.png"]
                    == wheel.read("robosuite/models/assets/textures/red-wood.png"),
                    "Archived texture differs from archived Robosuite wheel")
            for name in ("LICENSE", "AUTHORS"):
                member = f"robosuite-1.5.2.dist-info/licenses/{name}"
                copy(f"third_party/robosuite-1.5.2/{name}", wheel.read(member),
                     "history_archive", f"{wheel_member}!/{member}")
    transformations = []
    with zipfile.ZipFile(evaluation_archive) as evaluation:
        history_binding = json.loads(evaluation.read("runtime_reference/runtime-assets.json"))["history_assets"]
        require(PurePosixPath(history_binding["uri"]).name == history_archive.name
                and history_binding["bytes"] == history_archive.stat().st_size,
                "Evaluation archive names a different historical resource")
        for member in ("runtime_reference/runtime-assets.json", "runtime_reference/requirements-pro6000.txt",
                       "evaluation_reference/inputs.json", "assets/independent_rollout.py",
                       "evaluation_reference/native-pro6000/worker.py"):
            copy("provenance/" + member, evaluation.read(member), "evaluation_archive", member)
        member = "evaluation_reference/scenes/validation.jsonl"
        copy("accepted/scenes/validation.jsonl", evaluation.read(member), "evaluation_archive", member)
        suites = sorted(name for name in evaluation.namelist()
                        if name.startswith("evaluation_reference/scenes/suites/") and name.endswith(".yaml"))
        require(len(suites) == 14, "Expected fourteen original task suites")
        for member in suites:
            data = evaluation.read(member)
            copy("provenance/" + member, data, "evaluation_archive", member)
            lines = data.decode("utf-8").splitlines(keepends=True)
            changes = 0
            for i, line in enumerate(lines):
                if line.startswith("- manifest: "):
                    old = line[len("- manifest: "):].strip()
                    ending = "\r\n" if line.endswith("\r\n") else "\n"
                    lines[i] = "- manifest: ../scenes/validation.jsonl" + ending
                    changes += 1
            require(changes == 1, "Original suite does not have one explicit manifest path")
            target = "accepted/suites/" + PurePosixPath(member).name
            payload[target] = "".join(lines).encode("utf-8")
            transformations.append({"path": target, "field": "members[0].manifest", "from": old,
                                    "to": "../scenes/validation.jsonl", "other_bytes_equal": True})
        for name in ("fixed140", "independent1260"):
            member = f"evaluation_reference/{name}-selection.json"
            data = evaluation.read(member)
            copy("provenance/" + member, data, "evaluation_archive", member)
            original = json.loads(data)
            portable = [{**row, "suite": f"accepted/suites/sr_{row['task_id']}.yaml"} for row in original]
            require(all({k:v for k,v in a.items() if k != "suite"}
                        == {k:v for k,v in b.items() if k != "suite"}
                        for a,b in zip(original,portable,strict=True)), "Scientific selection changed")
            target = f"accepted/selections/{name}.json"
            payload[target] = encoded(portable)
            transformations.append({"path": target, "field": "[*].suite", "rows": len(portable),
                                    "to": "accepted/suites/sr_<task_id>.yaml",
                                    "other_fields_equal": True,
                                    "original_values": f"provenance/{member}"})
    for name in ("LICENSE", "AUTHORS"):
        source = DEST / f"third_party/robosuite-1.4.0/{name}"
        copy(f"third_party/robosuite-1.4.0/{name}", source.read_bytes(), "official_robosuite_v1.4.0",
             f"https://raw.githubusercontent.com/ARISE-Initiative/robosuite/v1.4.0/{name}")
    for name in ("INDEX.md", "verify_materials.py"):
        payload[name] = (DEST / name).read_bytes()
    payload["provenance/path_transformations.json"] = encoded(transformations)
    source_description = {
        "kind": "Local historical evaluation material candidate; not a public release",
        "history_archive": {"file": history_archive.name, "bytes": history_archive.stat().st_size,
            "research_relative_path": "local_private/zenith-pro6000-history-20261011/asset-adapt/" + history_archive.name},
        "evaluation_archive": {"file": evaluation_archive.name, "bytes": evaluation_archive.stat().st_size,
            "research_relative_path": "local_private/future0-independent1260-20261015/release-a3/" + evaluation_archive.name},
        "benchmark_files": 171,
        "copied_files": copied,
        "derived_files": ["accepted/suites/*", "accepted/selections/*", "INDEX.md", "verify_materials.py",
                          "provenance/path_transformations.json", "provenance/package_sources.json"],
        "history_archive_binding": "Original evaluation runtime-assets basename and bytes match the supplied local archive; no new remote process audit",
        "original_source_bytes_preserved": True,
        "redwood_matches_archived_robosuite_1_5_2": True,
        "license_status": "Historical benchmark LICENSE is an unapproved legal-text placeholder; public redistribution remains unresolved",
        "model_weights_included": False, "physics_or_policy_executed": False,
    }
    payload["provenance/package_sources.json"] = encoded(source_description)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(payload.items()):
            info = zipfile.ZipInfo(name, date_time=(2026,10,17,0,0,0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, data)
    with zipfile.ZipFile(destination) as archive:
        require(set(archive.namelist()) == set(payload), "Written package member set differs")
        require(all(archive.read(name) == data for name,data in payload.items()), "Written bytes differ")
    return {"archive": str(destination), "bytes": destination.stat().st_size,
            "members": len(payload), "uncompressed_bytes": sum(map(len,payload.values())),
            "source_files_copied_byte_for_byte": len(copied), "benchmark_files": 171,
            "only_portable_execution_paths_changed": True, "all_zip_members_read_back_exact": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history-archive", type=Path, required=True)
    parser.add_argument("--evaluation-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEST / "replay_materials.zip")
    args = parser.parse_args()
    print(json.dumps(build(args.history_archive, args.evaluation_archive, args.output), indent=2))


if __name__ == "__main__":
    main()
