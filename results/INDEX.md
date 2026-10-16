# Draft result inputs

This checkout organizes a complete Q1–Q3 Study draft. Its pending values are
not observations, and its proposed experiments do not authorize new runs. Inherited
SE(3)/flow/one-way settings remain candidates until supported by the study. Current
evidence belongs to the [Research experiment route](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/experiments/40_experiment_mainline_cn.md).

- `bindings.json`: maps every paper result ID to one LaTeX macro, unit, precision, formatter, and pending placeholder; read when adding or removing a paper claim.
- `pending.json`: sealed no-claim manifest used by the default draft build; it contains no commits, experiments, evidence, media, or available values.
- `scripts/import_results.py` still consumes the historical `se3wam-publication-result-manifest-v1` format. The rebuilt Benchmark does not thereby provide its former publication producer; see the boundary recorded in [`EXPERIMENT_PLAN.md`](../EXPERIMENT_PLAN.md). Reconnecting reviewed Research evidence requires an explicit result-production interface, not relabeling the pending input.

`results.tex` is generated output. Scientific values must never be entered there by hand.

Before a submission build, reconcile the method, task definitions, result IDs and
claims with the actual evidence and agreed import interface. A successful draft
build checks file usability; it does not establish scientific acceptance.
