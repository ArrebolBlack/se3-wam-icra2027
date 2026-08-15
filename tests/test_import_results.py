from __future__ import annotations

import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_results.py"
SPEC = importlib.util.spec_from_file_location("paper_import_results", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
IMPORTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = IMPORTER
SPEC.loader.exec_module(IMPORTER)


class ImportResultsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bindings = IMPORTER.load_bindings(ROOT / "results" / "bindings.json")
        self.pending = json.loads(
            (ROOT / "results" / "pending.json").read_text(encoding="utf-8")
        )

    def reviewed_manifest(self, *, complete: bool = True) -> dict[str, object]:
        manifest = copy.deepcopy(self.pending)
        manifest["release_id"] = "paper_reviewed_v1"
        manifest["state"] = "reviewed"
        commits = {"research": "a" * 40, "model": "b" * 40, "benchmark": "c" * 40}
        manifest["sources"] = {
            "repositories": commits,
            "experiment_ids": ["exp_db0_final_v1"],
            "evidence": [
                {
                    "id": "aggregate_metrics",
                    "repository": "research",
                    "commit": commits["research"],
                    "path": "docs/experiments/exp_db0_final_v1/aggregate.json",
                    "sha256": "d" * 64,
                }
            ],
        }
        for index, binding in enumerate(self.bindings["bindings"]):
            result = manifest["results"][binding["result_id"]]
            if not complete and index == len(self.bindings["bindings"]) - 1:
                continue
            if binding["formatter"] == "interval":
                value: object = [-1.2, 2.3]
            elif binding["formatter"] == "text":
                value = "External & reviewed"
            else:
                value = 12.345
            result.update(
                status="available",
                value=value,
                evidence_ids=["aggregate_metrics"],
            )
        manifest["review"] = {
            "decision": "approved",
            "reviewed_at": "2026-08-15T13:00:00Z",
            "reviewer_role": "experiment_owner",
            "notes": "Checked against the experiment record.",
        }
        manifest["payload_sha256"] = IMPORTER.manifest_sha256(manifest)
        return manifest

    def test_cross_runtime_number_identity_vector(self) -> None:
        self.assertEqual(
            IMPORTER.manifest_sha256(
                {
                    "payload_sha256": "0" * 64,
                    "numbers": [1, 83.5, 1e-7, 9007199254740991],
                    "text": "SE(3)-WAM",
                }
            ),
            "107bb0f77a013e1b848a81ad2629f35c4764189f90bde3eae1579dd5378f8568",
        )

    def test_pending_manifest_renders_only_placeholders(self) -> None:
        required = [binding["result_id"] for binding in self.bindings["bindings"]]
        IMPORTER.validate_manifest(self.pending, required_result_ids=required)
        rendered = IMPORTER.render_results(self.pending, self.bindings)
        self.assertIn(r"\newcommand{\ExternalSummary}{\placeholder{TBD}}", rendered)
        self.assertNotIn("confirm transfer", rendered)
        with self.assertRaisesRegex(IMPORTER.ResultImportError, "requires a reviewed"):
            IMPORTER.validate_manifest(self.pending, require_reviewed=True)

    def test_reviewed_manifest_formats_and_escapes_values(self) -> None:
        manifest = self.reviewed_manifest()
        required = [binding["result_id"] for binding in self.bindings["bindings"]]
        IMPORTER.validate_manifest(
            manifest,
            require_reviewed=True,
            required_result_ids=required,
        )
        rendered = IMPORTER.render_results(
            manifest, self.bindings, require_complete=True
        )
        self.assertIn(r"\newcommand{\DBCoreDelta}{+12.3}", rendered)
        self.assertIn(r"\newcommand{\DBCoreCI}{-1.2, 2.3}", rendered)
        self.assertIn(r"\newcommand{\ExternalSummary}{External \& reviewed}", rendered)

    def test_tamper_and_incomplete_release_fail_closed(self) -> None:
        manifest = self.reviewed_manifest()
        manifest["results"]["db_core_ours_sr_pct"]["value"] = 99.9
        with self.assertRaisesRegex(
            IMPORTER.ResultImportError, "payload_sha256 mismatch"
        ):
            IMPORTER.validate_manifest(manifest)
        incomplete = self.reviewed_manifest(complete=False)
        IMPORTER.validate_manifest(incomplete, require_reviewed=True)
        with self.assertRaisesRegex(IMPORTER.ResultImportError, "still pending"):
            IMPORTER.render_results(incomplete, self.bindings, require_complete=True)

    def test_atomic_generation_and_check_mode(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest_path = root / "manifest.json"
            output_path = root / "results.tex"
            manifest_path.write_text(
                json.dumps(self.pending, ensure_ascii=False),
                encoding="utf-8",
            )
            self.assertEqual(
                IMPORTER.main(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--bindings",
                        str(ROOT / "results" / "bindings.json"),
                        "--output",
                        str(output_path),
                    ]
                ),
                0,
            )
            self.assertEqual(
                IMPORTER.main(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--bindings",
                        str(ROOT / "results" / "bindings.json"),
                        "--output",
                        str(output_path),
                        "--check",
                    ]
                ),
                0,
            )
            output_path.write_text("stale\n", encoding="utf-8")
            with self.assertRaisesRegex(IMPORTER.ResultImportError, "is stale"):
                IMPORTER.main(
                    [
                        "--manifest",
                        str(manifest_path),
                        "--bindings",
                        str(ROOT / "results" / "bindings.json"),
                        "--output",
                        str(output_path),
                        "--check",
                    ]
                )


if __name__ == "__main__":
    unittest.main()
