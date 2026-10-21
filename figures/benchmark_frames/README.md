# DEV84 benchmark frames

Recorded agentview observations from the accepted P15 DEV84 archive in Research
(`local_private/future0-aux-20261012/`). They illustrate task geometry only; they
are not policy rollouts or predictions.

- `dev84_p15_state000.png`, `006`, `012`, `018`, `030`, `042`, `054`, `078`: the
  eight panels of `benchmark_task_examples`. `figures/plot_benchmark_task_examples.py`
  writes them losslessly from the archive (last observed 224x224 RGB of each state)
  and records the selection in `benchmark_task_examples_source.json`.
- `dev84_p15_state010.png`: the observation shown in `model_design` and
  `study_framework`, taken from the same archive.
