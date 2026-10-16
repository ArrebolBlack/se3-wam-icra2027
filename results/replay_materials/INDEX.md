# Historical evaluation materials

This local candidate contains the historical benchmark implementation and the exact 1,400 accepted simulation scenarios used by the paper's fixed-140 development set and complementary 1,260-scene evaluation. It makes the evaluator, task definitions, scene parameters, and selection identities available for inspection. The delivered checks parse these materials; they do not reproduce a policy rollout or any reported success rate.

The benchmark's original `LICENSE` is a `LicenseRef-Research-Only` placeholder that says the complete approved legal text has not yet been supplied. Its contents remain unchanged. Public redistribution and an anonymous submission package require the project owner's legal and release decisions. This candidate is for local review and has not been uploaded.

The paper repository contains the following delivery files. The ZIP contains this guide and verifier, but not another nested ZIP or the external validation report.

- `replay_materials.zip`: self-contained source/configuration candidate; extract into a new directory before use.
- `verify_materials.py`: the same parser and consistency checker included at the root of the ZIP.
- `validation.json`: results of the local native parser check, produced after extracting the ZIP.
- `third_party/robosuite-1.4.0/`: original upstream license and author attribution used when rebuilding the ZIP.
- `scripts/build_replay_materials.py` in the paper repository: rebuilds the ZIP from the two original archives; see the explicit command below.

## Inside the archive

| Path | Contents and use |
|---|---|
| `benchmark-source/` | All 171 archived benchmark files, copied byte for byte: evaluator, action queue, success/failure rules, six task families, fourteen task and sampling configurations, XML assets, source documentation, tests, original README/AGENTS and license. |
| `accepted/scenes/validation.jsonl` | The actual accepted 1,400-scene manifest, copied byte for byte. Each task has 100 scenes. Initial object/robot state, motion, physics, camera, lighting and event parameters remain intact. |
| `accepted/suites/` | Fourteen original single-task suites with only the manifest execution path changed to `../scenes/validation.jsonl`. |
| `accepted/selections/` | Exact fixed-140 and complementary-1,260 selection order, source and inference seeds, task/scenario identifiers, and task-local shard indices. Only suite execution paths are changed. They are relative to the extracted archive root. |
| `provenance/` | Original selections and suites; original runtime resource and input bindings; original worker/controller source for inspecting inference seeding and the 0.10 m translation limit; source-file map and explicit path transformations. These original files retain historical machine/object paths and are evidence, not portable launch configurations. |
| `third_party/` | Robosuite 1.4.0 and 1.5.2 license and author files. Historical texture attribution is preserved. |

The twelve manifests under `benchmark-source/manifests/v1/` are empty placeholders in the original archive. Use `accepted/scenes/validation.jsonl` and `accepted/suites/` for this study. Filling the old placeholders or regenerating scenes from a newer benchmark would change the delivered material.

## Verification without simulation

From the extracted archive root, with Python 3.11 or newer:

```console
python verify_materials.py
```

This checks the 140/1,260 partition, 1,400 distinct scenario identities, source and inference seeds, task-local shard bindings, unchanged non-path selection fields, action/clock/delay fields, Python syntax, XML file references, and license/attribution presence. It uses only the Python standard library and does not import a simulator.

For the original manifest/task parsers and strict YAML configuration loader, install NumPy 1.26.4 and PyYAML 6.0.3 in an isolated environment, then run:

```console
python verify_materials.py --native --output validation.json
```

The native check imports the archived source, parses all 1,400 scenarios, checks lossless scientific-field round trips, loads all fourteen task definitions and sampling configurations, validates the fourteen portable suite mappings, and resolves scene assets against the historical catalog. It does not call the suite evaluator's `load_suite`, construct a MuJoCo environment, compile its physics model, step physics, initialize a policy, or execute a rollout. No mocks replace those operations. The supplied result used Python 3.12.14, NumPy 1.26.4, and PyYAML 6.0.3 on Windows.

## Requirements for actual replay

The historical `benchmark-source/pyproject.toml` specifies Python >=3.11, MuJoCo 3.11.0, Robosuite 1.5.2, h5py 3.16.0, NumPy >=1.26.4,<2.0, and PyYAML >=6.0. The original `provenance/runtime_reference/requirements-pro6000.txt` records the separately observed Python 3.12.14 inference environment; it is provenance, not a complete new installation lock. Simulation also requires a working rendering backend and the Robosuite robot/controller assets. Those simulator/runtime dependencies are not vendored here or exercised by the parser check.

The accepted SE(3)-WAM model code and model-specific inference components, exported policy/checkpoint, pretrained perception weights, and normalization are also required to reproduce the paper's success rates. They are not included in this evaluator/scene package. The benchmark-side policy binding and original worker are included for inspection. The worker applies `torch.manual_seed(inference_seed)` before each episode and the accepted controller passes an execution translation limit of 0.10 m. A policy replay must preserve these details rather than using CLI defaults or substituting a current checkout. The scientific scenario pool uses 2 ms physics steps and 20 Hz control/sensing; T5 has one native command-delay tick and other tasks have zero. The measured inference wall time is not injected as a simulation delay.

The package binding checks the original evaluation payload's named history resource and its byte count against the supplied historical archive, and checks every copied member directly. It does not establish a new process-by-process audit of remote evaluations.

## Rebuild from the original local archives

Run from the paper repository root, using the two original archive paths:

```console
python scripts/build_replay_materials.py --history-archive "<research>/local_private/zenith-pro6000-history-20261011/asset-adapt/history-assets-a1.tar.gz" --evaluation-archive "<research>/local_private/future0-independent1260-20261015/release-a3/payload.zip"
```

The builder copies the original benchmark, manifest, selection, and provenance bytes, adds the documented portable path variants, and reads back every ZIP member for direct equality. It uses the legal files stored alongside this index and performs no network calls. The original source archives remain unchanged. Run the parser check on a fresh extraction afterward; the build itself is not a simulation test.

The texture `benchmark-source/assets/textures/red-wood.png` is attributed by the historical source to Robosuite 1.4.0. The upstream [license](https://raw.githubusercontent.com/ARISE-Initiative/robosuite/v1.4.0/LICENSE) and [authors](https://raw.githubusercontent.com/ARISE-Initiative/robosuite/v1.4.0/AUTHORS) were retrieved on 2026-10-17 without alteration. The same texture bytes are also present in the Robosuite 1.5.2 wheel embedded in the historical archive, whose license/authors are copied separately. Their inclusion does not replace or resolve the project's missing approved license text.

The preserved `benchmark-source/assets/README.md` contains an older general statement that its materials do not include copied textures. That statement predates the restored texture documented in `assets/textures/INDEX.md`; the specific attribution and supplied upstream legal files govern this material description. Both historical files are retained unchanged.
