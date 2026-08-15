"""Validate one publication manifest and render the paper's LaTeX result macros."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import struct
import tempfile
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any

PUBLICATION_SCHEMA = "se3wam-publication-result-manifest-v1"
BINDINGS_SCHEMA = "se3wam-paper-result-bindings-v1"
_TOP_KEYS = frozenset(
    {
        "schema_version",
        "release_id",
        "state",
        "project",
        "created_at",
        "sources",
        "results",
        "media",
        "review",
        "payload_sha256",
    }
)
_SOURCE_KEYS = frozenset({"repositories", "experiment_ids", "evidence"})
_REPOSITORY_KEYS = frozenset({"research", "model", "benchmark"})
_EVIDENCE_KEYS = frozenset({"id", "repository", "commit", "path", "sha256"})
_RESULT_KEYS = frozenset({"status", "value", "unit", "precision", "evidence_ids"})
_MEDIA_KEYS = frozenset({"id", "path", "mime_type", "sha256", "evidence_ids"})
_REVIEW_KEYS = frozenset({"decision", "reviewed_at", "reviewer_role", "notes"})
_BINDING_KEYS = frozenset(
    {"macro", "result_id", "unit", "precision", "formatter", "placeholder"}
)
_STATIC_MACRO_KEYS = frozenset({"macro", "latex"})
_ID_RE = re.compile(r"^[a-z][a-z0-9_.-]*$")
_MACRO_RE = re.compile(r"^[A-Za-z][A-Za-z0-9]*$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40,64}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_TIMESTAMP_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_FORMATTERS = frozenset({"fixed", "signed_fixed", "interval", "text"})
_MAX_SAFE_INTEGER = (1 << 53) - 1
_NUMBER_IDENTITY_KEY = "$se3wam_f64"
_LATEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "#": r"\#",
    "$": r"\$",
    "%": r"\%",
    "&": r"\&",
    "_": r"\_",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


class ResultImportError(ValueError):
    """Raised when an input cannot safely become paper text."""


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not all(isinstance(key, str) for key in value):
        raise ResultImportError(f"{label} must be an object with string keys")
    return value


def _sequence(value: object, label: str) -> Sequence[Any]:
    if isinstance(value, (str, bytes, bytearray)) or not isinstance(value, Sequence):
        raise ResultImportError(f"{label} must be an array")
    return value


def _exact_keys(value: Mapping[str, Any], expected: frozenset[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise ResultImportError(
            f"{label} fields mismatch: missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}"
        )


def _identifier(value: object, label: str) -> str:
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        raise ResultImportError(f"{label} must match {_ID_RE.pattern}")
    return value


def _macro(value: object, label: str) -> str:
    if not isinstance(value, str) or _MACRO_RE.fullmatch(value) is None:
        raise ResultImportError(f"{label} must be a plain LaTeX command name")
    return value


def _nonempty_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ResultImportError(f"{label} must be non-empty text")
    return value


def _sha256(value: object, label: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ResultImportError(f"{label} must be a lowercase SHA-256")
    return value


def _commit(value: object, label: str, *, allow_none: bool) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or _COMMIT_RE.fullmatch(value) is None:
        raise ResultImportError(f"{label} must be a 40–64 character lowercase commit")
    return value


def _timestamp(value: object, label: str) -> str:
    if not isinstance(value, str) or _TIMESTAMP_RE.fullmatch(value) is None:
        raise ResultImportError(f"{label} must be UTC YYYY-MM-DDTHH:MM:SSZ")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError as error:
        raise ResultImportError(f"{label} must be a valid UTC timestamp") from error
    if parsed.strftime("%Y-%m-%dT%H:%M:%SZ") != value:
        raise ResultImportError(f"{label} must be a canonical UTC timestamp")
    return value


def _safe_path(value: object, label: str) -> str:
    text = _nonempty_text(value, label)
    path = PurePosixPath(text)
    if (
        "\\" in text
        or path.is_absolute()
        or any(part in {"", ".", ".."} for part in path.parts)
        or path.as_posix() != text
    ):
        raise ResultImportError(f"{label} must be a normalized relative POSIX path")
    return text


def _result_value(value: object, label: str) -> None:
    if isinstance(value, bool):
        raise ResultImportError(f"{label} must not be boolean")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            raise ResultImportError(f"{label} must be finite")
        return
    if isinstance(value, str):
        if not value:
            raise ResultImportError(f"{label} must not be empty")
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if not value:
            raise ResultImportError(f"{label} array must not be empty")
        for index, item in enumerate(value):
            _result_value(item, f"{label}[{index}]")
        return
    raise ResultImportError(f"{label} has an unsupported value type")


def _identity_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, (int, float)):
        number = float(value)
        if not math.isfinite(number):
            raise ResultImportError("publication identity numbers must be finite")
        if number.is_integer() and abs(number) > _MAX_SAFE_INTEGER:
            raise ResultImportError(
                "publication identity integers must be within the JSON safe-integer range"
            )
        return {_NUMBER_IDENTITY_KEY: struct.pack(">d", number).hex()}
    if isinstance(value, Mapping):
        return {key: _identity_value(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_identity_value(item) for item in value]
    raise ResultImportError(
        f"unsupported publication identity value: {type(value).__name__}"
    )


def manifest_sha256(manifest: Mapping[str, Any]) -> str:
    payload = {key: value for key, value in manifest.items() if key != "payload_sha256"}
    canonical = json.dumps(
        _identity_value(payload),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_manifest(
    manifest: Mapping[str, Any],
    *,
    require_reviewed: bool = False,
    required_result_ids: Sequence[str] = (),
) -> None:
    root = _mapping(manifest, "manifest")
    _exact_keys(root, _TOP_KEYS, "manifest")
    if root["schema_version"] != PUBLICATION_SCHEMA:
        raise ResultImportError(
            f"unsupported publication schema: {root['schema_version']!r}"
        )
    _identifier(root["release_id"], "release_id")
    _nonempty_text(root["project"], "project")
    _timestamp(root["created_at"], "created_at")
    state = root["state"]
    if state not in {"pending", "reviewed"}:
        raise ResultImportError("state must be 'pending' or 'reviewed'")
    if require_reviewed and state != "reviewed":
        raise ResultImportError("consumer requires a reviewed publication manifest")

    sources = _mapping(root["sources"], "sources")
    _exact_keys(sources, _SOURCE_KEYS, "sources")
    repositories = _mapping(sources["repositories"], "sources.repositories")
    _exact_keys(repositories, _REPOSITORY_KEYS, "sources.repositories")
    commits = {
        name: _commit(
            repositories[name],
            f"sources.repositories.{name}",
            allow_none=state == "pending",
        )
        for name in sorted(_REPOSITORY_KEYS)
    }
    experiment_ids = [
        _identifier(item, f"sources.experiment_ids[{index}]")
        for index, item in enumerate(
            _sequence(sources["experiment_ids"], "sources.experiment_ids")
        )
    ]
    if len(experiment_ids) != len(set(experiment_ids)):
        raise ResultImportError("sources.experiment_ids contains duplicates")

    evidence_ids: set[str] = set()
    for index, item in enumerate(_sequence(sources["evidence"], "sources.evidence")):
        label = f"sources.evidence[{index}]"
        record = _mapping(item, label)
        _exact_keys(record, _EVIDENCE_KEYS, label)
        evidence_id = _identifier(record["id"], f"{label}.id")
        if evidence_id in evidence_ids:
            raise ResultImportError(f"duplicate evidence id: {evidence_id}")
        evidence_ids.add(evidence_id)
        repository = record["repository"]
        if repository not in _REPOSITORY_KEYS:
            raise ResultImportError(f"{label}.repository is invalid")
        if (
            _commit(record["commit"], f"{label}.commit", allow_none=False)
            != commits[repository]
        ):
            raise ResultImportError(
                f"{label}.commit must match sources.repositories.{repository}"
            )
        _safe_path(record["path"], f"{label}.path")
        _sha256(record["sha256"], f"{label}.sha256")

    results = _mapping(root["results"], "results")
    available_count = 0
    for result_id, item in results.items():
        _identifier(result_id, f"result id {result_id!r}")
        label = f"results.{result_id}"
        result = _mapping(item, label)
        _exact_keys(result, _RESULT_KEYS, label)
        status = result["status"]
        if status not in {"pending", "available"}:
            raise ResultImportError(f"{label}.status is invalid")
        _nonempty_text(result["unit"], f"{label}.unit")
        precision = result["precision"]
        if precision is not None and (
            not isinstance(precision, int)
            or isinstance(precision, bool)
            or not 0 <= precision <= 15
        ):
            raise ResultImportError(
                f"{label}.precision must be null or an int from 0 to 15"
            )
        references = [
            _identifier(value, f"{label}.evidence_ids[{index}]")
            for index, value in enumerate(
                _sequence(result["evidence_ids"], f"{label}.evidence_ids")
            )
        ]
        if len(references) != len(set(references)):
            raise ResultImportError(f"{label}.evidence_ids contains duplicates")
        unknown = sorted(set(references) - evidence_ids)
        if unknown:
            raise ResultImportError(
                f"{label}.evidence_ids references unknown evidence: {unknown}"
            )
        if status == "pending":
            if result["value"] is not None or references:
                raise ResultImportError(
                    f"{label} pending result must have null value and no evidence"
                )
        else:
            if result["value"] is None or not references:
                raise ResultImportError(
                    f"{label} available result requires a value and evidence"
                )
            _result_value(result["value"], f"{label}.value")
            available_count += 1

    required = [_identifier(item, "required result id") for item in required_result_ids]
    if len(required) != len(set(required)):
        raise ResultImportError("required result ids contains duplicates")
    missing = sorted(set(required) - set(results))
    if missing:
        raise ResultImportError(f"required result ids are missing: {missing}")

    media_ids: set[str] = set()
    media = _sequence(root["media"], "media")
    for index, item in enumerate(media):
        label = f"media[{index}]"
        record = _mapping(item, label)
        _exact_keys(record, _MEDIA_KEYS, label)
        media_id = _identifier(record["id"], f"{label}.id")
        if media_id in media_ids:
            raise ResultImportError(f"duplicate media id: {media_id}")
        media_ids.add(media_id)
        _safe_path(record["path"], f"{label}.path")
        _nonempty_text(record["mime_type"], f"{label}.mime_type")
        _sha256(record["sha256"], f"{label}.sha256")
        references = [
            _identifier(value, f"{label}.evidence_ids[{item_index}]")
            for item_index, value in enumerate(
                _sequence(record["evidence_ids"], f"{label}.evidence_ids")
            )
        ]
        if len(references) != len(set(references)):
            raise ResultImportError(f"{label}.evidence_ids contains duplicates")
        if not references or not set(references).issubset(evidence_ids):
            raise ResultImportError(f"{label} must reference known evidence")

    review = _mapping(root["review"], "review")
    _exact_keys(review, _REVIEW_KEYS, "review")
    if state == "pending":
        if review["decision"] != "pending":
            raise ResultImportError(
                "pending manifest review.decision must be 'pending'"
            )
        if review["reviewed_at"] is not None or review["reviewer_role"] is not None:
            raise ResultImportError(
                "pending manifest must not claim a completed review"
            )
        if any(value is not None for value in commits.values()):
            raise ResultImportError("pending manifest repository commits must be null")
        if experiment_ids or evidence_ids or available_count or media:
            raise ResultImportError(
                "pending manifest must not carry publication evidence"
            )
    else:
        if review["decision"] != "approved":
            raise ResultImportError(
                "reviewed manifest review.decision must be 'approved'"
            )
        _timestamp(review["reviewed_at"], "review.reviewed_at")
        _nonempty_text(review["reviewer_role"], "review.reviewer_role")
        if not experiment_ids or not evidence_ids or available_count == 0:
            raise ResultImportError(
                "reviewed manifest requires experiments, evidence, and an available result"
            )
    if review["notes"] is not None:
        _nonempty_text(review["notes"], "review.notes")

    recorded = _sha256(root["payload_sha256"], "payload_sha256")
    actual = manifest_sha256(root)
    if recorded != actual:
        raise ResultImportError(
            f"payload_sha256 mismatch: recorded={recorded}, actual={actual}"
        )


def _load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        decoded = json.loads(
            path.read_bytes(),
            parse_constant=lambda value: (_ for _ in ()).throw(
                ResultImportError(f"invalid JSON constant in {label}: {value}")
            ),
        )
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ResultImportError(f"cannot load {label}: {path}") from error
    return dict(_mapping(decoded, label))


def load_bindings(path: Path) -> dict[str, Any]:
    document = _load_json(path, "bindings")
    _exact_keys(
        document, frozenset({"schema_version", "bindings", "static_macros"}), "bindings"
    )
    if document["schema_version"] != BINDINGS_SCHEMA:
        raise ResultImportError(
            f"unsupported bindings schema: {document['schema_version']!r}"
        )
    macros: set[str] = set()
    result_ids: set[str] = set()
    normalized_bindings: list[dict[str, Any]] = []
    for index, item in enumerate(_sequence(document["bindings"], "bindings.bindings")):
        label = f"bindings.bindings[{index}]"
        binding = dict(_mapping(item, label))
        _exact_keys(binding, _BINDING_KEYS, label)
        macro = _macro(binding["macro"], f"{label}.macro")
        result_id = _identifier(binding["result_id"], f"{label}.result_id")
        if macro in macros or result_id in result_ids:
            raise ResultImportError(f"{label} duplicates a macro or result id")
        macros.add(macro)
        result_ids.add(result_id)
        _nonempty_text(binding["unit"], f"{label}.unit")
        precision = binding["precision"]
        if precision is not None and (
            not isinstance(precision, int)
            or isinstance(precision, bool)
            or not 0 <= precision <= 15
        ):
            raise ResultImportError(f"{label}.precision is invalid")
        if binding["formatter"] not in _FORMATTERS:
            raise ResultImportError(f"{label}.formatter is invalid")
        if binding["formatter"] == "text" and precision is not None:
            raise ResultImportError(f"{label} text formatter requires null precision")
        if binding["formatter"] != "text" and precision is None:
            raise ResultImportError(f"{label} numeric formatter requires a precision")
        _nonempty_text(binding["placeholder"], f"{label}.placeholder")
        normalized_bindings.append(binding)

    static_macros: list[dict[str, Any]] = []
    for index, item in enumerate(
        _sequence(document["static_macros"], "bindings.static_macros")
    ):
        label = f"bindings.static_macros[{index}]"
        record = dict(_mapping(item, label))
        _exact_keys(record, _STATIC_MACRO_KEYS, label)
        macro = _macro(record["macro"], f"{label}.macro")
        if macro in macros:
            raise ResultImportError(f"duplicate macro: {macro}")
        macros.add(macro)
        _nonempty_text(record["latex"], f"{label}.latex")
        static_macros.append(record)
    return {"bindings": normalized_bindings, "static_macros": static_macros}


def load_manifest(
    path: Path,
    *,
    require_reviewed: bool = False,
    required_result_ids: Sequence[str] = (),
) -> dict[str, Any]:
    manifest = _load_json(path, "publication manifest")
    validate_manifest(
        manifest,
        require_reviewed=require_reviewed,
        required_result_ids=required_result_ids,
    )
    return manifest


def _latex_escape(value: str) -> str:
    return "".join(_LATEX_ESCAPES.get(character, character) for character in value)


def _number(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ResultImportError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ResultImportError(f"{label} must be finite")
    return number


def _fixed(value: object, precision: int, *, signed: bool, label: str) -> str:
    number = _number(value, label)
    if round(number, precision) == 0:
        number = 0.0
    rendered = f"{number:.{precision}f}"
    if signed and not rendered.startswith("-"):
        rendered = f"+{rendered}"
    return rendered


def _render_available(binding: Mapping[str, Any], result: Mapping[str, Any]) -> str:
    label = f"results.{binding['result_id']}.value"
    formatter = binding["formatter"]
    precision = binding["precision"]
    value = result["value"]
    if formatter == "text":
        if not isinstance(value, str) or not value:
            raise ResultImportError(f"{label} must be non-empty text")
        return _latex_escape(value)
    if formatter == "interval":
        interval = _sequence(value, label)
        if len(interval) != 2:
            raise ResultImportError(
                f"{label} must contain exactly two interval endpoints"
            )
        return ", ".join(
            _fixed(item, precision, signed=False, label=f"{label}[{index}]")
            for index, item in enumerate(interval)
        )
    return _fixed(
        value,
        precision,
        signed=formatter == "signed_fixed",
        label=label,
    )


def render_results(
    manifest: Mapping[str, Any],
    bindings: Mapping[str, Any],
    *,
    require_complete: bool = False,
) -> str:
    lines = [
        "% Generated by scripts/import_results.py; do not edit by hand.",
        (
            f"% Source release={manifest['release_id']} state={manifest['state']} "
            f"payload_sha256={manifest['payload_sha256']}"
        ),
    ]
    pending: list[str] = []
    for binding in bindings["bindings"]:
        result = _mapping(
            manifest["results"][binding["result_id"]], binding["result_id"]
        )
        if result["unit"] != binding["unit"]:
            raise ResultImportError(
                f"results.{binding['result_id']}.unit must be {binding['unit']!r}"
            )
        if result["precision"] != binding["precision"]:
            raise ResultImportError(
                f"results.{binding['result_id']}.precision must be {binding['precision']!r}"
            )
        if result["status"] == "available":
            latex = _render_available(binding, result)
        else:
            pending.append(binding["result_id"])
            latex = rf"\placeholder{{{_latex_escape(binding['placeholder'])}}}"
        lines.append(rf"\newcommand{{\{binding['macro']}}}{{{latex}}}")
    if require_complete and pending:
        raise ResultImportError(f"paper result bindings are still pending: {pending}")
    for record in bindings["static_macros"]:
        lines.append(rf"\newcommand{{\{record['macro']}}}{{{record['latex']}}}")
    lines.append("")
    return "\n".join(lines)


def _write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(text)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("results/pending.json"))
    parser.add_argument("--bindings", type=Path, default=Path("results/bindings.json"))
    parser.add_argument("--output", type=Path, default=Path("results.tex"))
    parser.add_argument("--require-reviewed", action="store_true")
    parser.add_argument("--require-complete", action="store_true")
    parser.add_argument("--check", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    bindings = load_bindings(args.bindings)
    required_ids = [binding["result_id"] for binding in bindings["bindings"]]
    manifest = load_manifest(
        args.manifest,
        require_reviewed=args.require_reviewed,
        required_result_ids=required_ids,
    )
    rendered = render_results(
        manifest, bindings, require_complete=args.require_complete
    )
    if args.check:
        try:
            current = args.output.read_text(encoding="utf-8")
        except OSError as error:
            raise ResultImportError(
                f"cannot read generated output: {args.output}"
            ) from error
        if current != rendered:
            raise ResultImportError(
                f"generated result registry is stale: {args.output}"
            )
    else:
        _write_atomic(args.output, rendered)
    available = sum(
        result["status"] == "available" for result in manifest["results"].values()
    )
    print(
        json.dumps(
            {
                "release_id": manifest["release_id"],
                "state": manifest["state"],
                "payload_sha256": manifest["payload_sha256"],
                "available": available,
                "pending": len(required_ids) - available,
                "checked": args.check,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ResultImportError as error:
        raise SystemExit(f"result import failed: {error}") from error
