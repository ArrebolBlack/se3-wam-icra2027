from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "render_figures.py"
SPEC = importlib.util.spec_from_file_location("paper_render_figures", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
RENDERER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RENDERER
SPEC.loader.exec_module(RENDERER)


class RenderFiguresTest(unittest.TestCase):
    def test_pdf_metadata_timestamps_are_reproducible(self) -> None:
        payload = (
            b"%PDF-1.4\n<</CreationDate (D:20260815184757+00'00')\n"
            b"/ModDate (D:20260815184758+00'00')>>\n"
        )
        expected = (
            b"%PDF-1.4\n<</CreationDate (D:19700101000000+00'00')\n"
            b"/ModDate (D:19700101000000+00'00')>>\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "figure.pdf"
            target.write_bytes(payload)

            RENDERER._normalize_pdf_metadata(target)
            self.assertEqual(target.read_bytes(), expected)

            RENDERER._normalize_pdf_metadata(target)
            self.assertEqual(target.read_bytes(), expected)

    def test_non_metadata_date_text_is_unchanged(self) -> None:
        payload = b"stream D:20260815184757+00'00' endstream"
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "figure.pdf"
            target.write_bytes(payload)

            RENDERER._normalize_pdf_metadata(target)

            self.assertEqual(target.read_bytes(), payload)


if __name__ == "__main__":
    unittest.main()
