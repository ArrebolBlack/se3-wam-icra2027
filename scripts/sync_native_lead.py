"""Update the manuscript and optional static project page from OnTimeBench's main table."""

import argparse
import json
import re
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-page", type=Path, help="path to the local project-page HTML")
    args = parser.parse_args()
    lead = json.load(sys.stdin)["native_lead"]
    if (lead["method"], lead["baseline"]) != ("se3_wam", "puma"):
        raise ValueError("The baseline in the manuscript differs from the recomputed comparison.")
    value = lead["display"]
    if not re.fullmatch(r"\d+\.\d", value) or value != format(lead["points"], ".1f"):
        raise ValueError("Expected the full-precision lead rounded once to one decimal place.")
    config = Path(__file__).resolve().parents[1] / "paper_config.tex"
    targets = [(config, r"(?<=\\newcommand\{\\nativeLead\}\{)\d+\.\d+(?=\})")]
    if args.project_page:
        targets.append((args.project_page, r"\b\d+\.\d+(?= points above the strongest baseline)"))

    changes = []
    for path, pattern in targets:
        original = path.read_bytes()
        updated, count = re.subn(pattern.encode(), value.encode(), original)
        if count != 1:
            raise ValueError(f"Expected exactly one Native lead in {path}, found {count}.")
        if updated != original:
            changes.append((path, updated))
    for path, updated in changes:
        path.write_bytes(updated)


if __name__ == "__main__":
    main()
