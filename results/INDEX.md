# Result inputs

- `bindings.json`: maps every paper result ID to one LaTeX macro, unit, precision, formatter, and pending placeholder; read when adding or removing a paper claim.
- `pending.json`: sealed no-claim manifest used by the default draft build; it contains no commits, experiments, evidence, media, or available values.
- Reviewed result manifests are produced and retained by Dynamic Benchmark under its publication contract. Pass one explicitly to `scripts/import_results.py` or `scripts/build.ps1`; do not copy it here as a second source of truth.

`results.tex` is generated output. Scientific values must never be entered there by hand.
