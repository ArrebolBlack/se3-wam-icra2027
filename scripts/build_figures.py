"""Regenerate paper figures, each with the one script that produces its PDF.

Usage: python scripts/build_figures.py [--only NAME ...] [--extract] [--research-root <Research>]

Concept figures and replots from adjacent data need no Research checkout. The
future-supervision, prediction and benchmark figures always read Research, and
--extract makes the matplotlib figures re-read it as well. Review PNGs are written
to tmp/figure-review/.
"""
import argparse
import os
import subprocess
import sys

from common import REPO, RESEARCH_ENV, add_research_argument, require

# Figure stem -> (producer script, extra arguments, accepts --extract).
PRODUCERS = {
    "interaction_timing": ("figures/Fig3/archive/concepts/generate_figures.py", ["--figure", "interaction_timing"], False),
    "study_framework": ("figures/Fig3/archive/concepts/generate_figures.py", ["--figure", "study_framework"], False),
    "model_design": ("figures/Fig2/archive/model_design/draw_model_design.py", [], False),
    "future_supervision": ("figures/Fig5/archive/future_supervision/plot_future_supervision.py", [], False),
    "benchmark_task_examples": ("figures/Fig4/archive/benchmark/plot_benchmark_task_examples.py", [], False),
    "prediction_examples": ("figures/Fig5/archive/prediction_examples/plot_prediction_examples.py", [], False),
    "history_diagnostics": ("figures/Fig5/archive/history_diagnostics/plot_history_diagnostics.py", [], True),
    "gt_history_intervention": ("figures/Fig5/archive/gt_history_intervention/plot_gt_history_intervention.py", [], True),
    "decoder_failures": ("figures/Fig5/archive/decoder_failures/plot_decoder_failures.py", [], True),
}
USES_RESEARCH = {"future_supervision", "benchmark_task_examples", "prediction_examples"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=sorted(PRODUCERS), metavar="NAME",
                        help="figure stems to rebuild (default: all)")
    parser.add_argument("--extract", action="store_true",
                        help="re-read Research for the matplotlib figures")
    add_research_argument(parser)
    args = parser.parse_args()
    env = dict(os.environ)
    if args.research_root:
        env[RESEARCH_ENV] = str(args.research_root)
    for name in args.only or PRODUCERS:
        script, extra, extractable = PRODUCERS[name]
        command = [sys.executable, str(REPO / script), *extra]
        if args.extract and extractable:
            command.append("--extract")
        needs_research = name in USES_RESEARCH or (args.extract and extractable)
        print(f"[{name}] {' '.join(command[1:])}" + ("  (reads Research)" if needs_research else ""))
        subprocess.run(command, cwd=REPO, env=env, check=True)
        pdf = (REPO / script).with_name(f"{name}.pdf")
        require(pdf.is_file() and pdf.stat().st_size > 0, f"{name}: producer wrote no PDF")


if __name__ == "__main__":
    main()
