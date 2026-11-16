"""Data and statistics for the Paused-vs-Native ranking figure (small_figs/B).

Inputs (read-only, tracked in the paper repo):
  results/realtime_c/table1-20261104.json            SR and marginal scene-bootstrap 95% CIs
  results/realtime_c/native-per-task-20261104-scenes.csv  per-scene Native successes, all 11 methods
  tables/main_results.tex                           Table 1, checked to one decimal

Paired rank intervals exist only for Native (the repo holds Native scene-level outcomes for
all methods; Paused scene-level outcomes only for ACT and DP). Paused ties are therefore judged
by overlap of marginal intervals, which is conservative (paired intervals are narrower).
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
TABLE1_JSON = REPO / "results/realtime_c/table1-20261104.json"
NATIVE_SCENES = REPO / "results/realtime_c/native-per-task-20261104-scenes.csv"
MAIN_TEX = REPO / "tables/main_results.tex"
COLORS = json.loads((REPO / "figures/method_colors.json").read_text(encoding="utf-8"))["methods"]

# JSON key -> (display label, method_colors key, Fig. 5 marker, Fig. 5 linestyle, Table 1 row label)
METHODS = {
    "se3_wam":          (r"FoveaWAM",            "FoveaWAM",         "o", "-",  r"\ours"),
    "pi05_se3":         (r"$\pi_{0.5}$+SE(3)",   "π0.5+SE(3)",       "o", "-",  r"$\pi_{0.5}$+SE(3)"),
    "pi05":             (r"$\pi_{0.5}$",         "π0.5",             "o", "--", r"$\pi_{0.5}$ \cite{pi05}"),
    "dynamicwam_se3":   (r"DynamicWAM+SE(3)",    "DynamicWAM+SE(3)", "s", "-",  r"DynamicWAM+SE(3)"),
    "openwam_official": (r"OpenWAM-$\alpha$",    "OpenWAM-α",        "D", "-",  r"OpenWAM-$\alpha$ \cite{openwam_alpha}"),
    "openwam":          (r"OpenWAM-$\alpha$ (off)", "OpenWAM-α (off)", "D", "--", r"OpenWAM-$\alpha$ (off)"),
    "dynamicvla":       (r"DynamicVLA",          "DynamicVLA",       "^", "-",  r"DynamicVLA \cite{dynamicvla}"),
    "puma":             (r"PUMA",                "PUMA",             "P", "-",  r"PUMA \cite{domino}"),
    "dynamicwam":       (r"DynamicWAM",          "DynamicWAM",       "s", "--", r"DynamicWAM \cite{dynamicwam}"),
    "act":              (r"ACT",                 "ACT",              "o", "-",  r"ACT \cite{act}"),
    "dp":               (r"DP",                  "DP",               "s", "-",  r"DP \cite{diffusionpolicy}"),
}
ORDER = list(METHODS)


def label(m: str) -> str:
    return METHODS[m][0]


def color(m: str) -> str:
    return COLORS[METHODS[m][1]]


def marker(m: str) -> str:
    return METHODS[m][2]


def hollow(m: str) -> bool:
    return METHODS[m][3] == "--"


def _table1_rows() -> dict[str, list[str]]:
    rows = {}
    for line in MAIN_TEX.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.split("&")]
        if len(cells) == 8:
            rows[cells[0]] = [re.sub(r"\\(?:bestcell|secondcell)\{([0-9.]+)\}", r"\1",
                                     c.removesuffix(r"\\").strip()) for c in cells[4:]]
    return rows


def load() -> dict[str, dict]:
    """Return per-method SR, marginal CI and p95 for Native and Paused, checked against Table 1."""
    js = json.loads(TABLE1_JSON.read_text(encoding="utf-8"))["rows"]
    out: dict[str, dict] = {m: {} for m in ORDER}
    for r in js:
        if r["method"] in out and r["protocol"] in ("native", "paused"):
            if r["episodes"] != 1400 or r.get("status") != "accepted":
                raise ValueError(f"Unaccepted row {r['method']}/{r['protocol']}")
            out[r["method"]][r["protocol"]] = (r["sr_percent"], tuple(r["sr_scene_bootstrap95"]))
            out[r["method"]]["p95"] = r["measured_5090_p95_ms"]
    tex = _table1_rows()
    for m in ORDER:
        native, _, paused, p95 = tex[METHODS[m][4]]
        for proto, v in (("native", native), ("paused", paused)):
            if f"{out[m][proto][0]:.1f}" != v:
                raise ValueError(f"Figure/Table 1 mismatch: {m} {proto} {out[m][proto][0]} vs {v}")
        if f"{out[m]['p95']:.1f}" != p95:
            raise ValueError(f"p95 mismatch: {m}")
    return out


def native_paired_bootstrap(draws: int = 20000, seed: int = 20261116):
    """Task-stratified scene bootstrap, jointly across methods (as in the appendix).

    Returns (point SR [11], draws x 11 SR array) in ORDER.
    """
    with NATIVE_SCENES.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tasks = sorted({r["task_id"] for r in rows})
    arr = np.stack([np.array([[r[m] == "True" for m in ORDER] for r in rows if r["task_id"] == t],
                             dtype=float) for t in tasks])            # tasks x scenes x methods
    if arr.shape != (14, 100, 11):
        raise ValueError(f"Unexpected scene array {arr.shape}")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.shape[1], size=(draws, arr.shape[0], arr.shape[1]))
    srs = np.stack([arr[t][idx[:, t, :]].mean(1) for t in range(arr.shape[0])], 1).mean(1) * 100
    point = arr.mean(1).mean(0) * 100
    return point, srs


def native_rank_intervals(srs: np.ndarray) -> dict[str, tuple[int, int]]:
    ranks = (-srs).argsort(1).argsort(1) + 1
    lo, hi = np.percentile(ranks, [2.5, 97.5], axis=0)
    return {m: (int(lo[i]), int(hi[i])) for i, m in enumerate(ORDER)}


def paused_rank_ranges(data) -> dict[str, tuple[int, int]]:
    """Conservative Paused rank ranges: a method can rank anywhere among methods whose
    marginal 95% intervals overlap its own (paired data unavailable)."""
    out = {}
    for m in ORDER:
        lo, hi = data[m]["paused"][1]
        above = sum(1 for n in ORDER if n != m and data[n]["paused"][1][0] > hi)
        overlap = sum(1 for n in ORDER if n != m and not (data[n]["paused"][1][0] > hi
                                                          or data[n]["paused"][1][1] < lo))
        out[m] = (above + 1, above + 1 + overlap)
    return out


if __name__ == "__main__":
    d = load()
    point, srs = native_paired_bootstrap()
    for i, m in enumerate(ORDER):
        if abs(point[i] - d[m]["native"][0]) > 1e-9:
            raise ValueError(f"Scene CSV does not reproduce Native SR for {m}")
    nr, pr = native_rank_intervals(srs), paused_rank_ranges(d)
    for m in ORDER:
        print(f"{m:17s} paused {d[m]['paused'][0]:5.1f} rank {pr[m]}  native {d[m]['native'][0]:5.1f} "
              f"rank95 {nr[m]}  p95 {d[m]['p95']:.1f}")
    pi, pu = ORDER.index("pi05_se3"), ORDER.index("puma")
    print("PUMA - pi05_se3 native paired 95%:", np.percentile(srs[:, pu] - srs[:, pi], [2.5, 97.5]).round(2))
