"""Rebuild four PDFs, commit, merge into main, and push; no manuscript checks.

Run from main: python scripts/publish.py [-m "Update paper"]
Also accepts an existing task worktree whose main checkout is available.
All tracked edits and non-ignored new files are included. On failure, the task
branch/worktree is retained; a failed push can be retried with git push origin main.
"""

import argparse
from datetime import datetime
from pathlib import Path
import os
import shutil
import subprocess


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def names(output):
    return [part.decode("utf-8") for part in output.split(b"\0") if part]


def changes(repo):
    paths = set(names(git(repo, "diff", "HEAD", "--name-only", "-z")))
    paths.update(names(git(repo, "ls-files", "--others", "--exclude-standard", "-z")))
    return {p: (repo / p).read_bytes() if (repo / p).exists() else None
            for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-m", "--message", default="Update paper and rebuild PDFs")
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[1]
    branch = git(repo, "branch", "--show-current").decode().strip()
    if not branch:
        raise RuntimeError("Run from main or a named task branch, not detached HEAD.")
    main_root = None
    for block in git(repo, "worktree", "list", "--porcelain").decode().split("\n\n"):
        lines = block.splitlines()
        if "branch refs/heads/main" in lines:
            main_root = Path(lines[0].removeprefix("worktree ")).resolve()
    if main_root is None:
        raise RuntimeError("The main branch must have a local checkout.")

    git(repo, "fetch", "origin")
    base = git(main_root, "rev-parse", "HEAD")
    if base != git(repo, "rev-parse", "origin/main"):
        raise RuntimeError("Local main differs from origin/main; integrate or push it first.")
    git(repo, "merge-base", "--is-ancestor", base.decode().strip(), "HEAD")
    source = changes(main_root)
    status = git(main_root, "status", "--porcelain=v1", "-z")
    original_paths = set(names(git(main_root, "ls-tree", "-r", "--name-only", "-z", "HEAD")))
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    created = branch == "main"
    if created:
        branch = "codex/paper-publish-" + stamp
        work = main_root.parent / (main_root.name + "-publish-" + stamp)
        git(repo, "worktree", "add", "-b", branch, str(work), "HEAD")
        for name, content in source.items():
            target = work / name
            if content is None:
                target.unlink()
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
    else:
        work = repo
        for name, content in source.items():
            target = work / name
            if (target.read_bytes() if target.exists() else None) != content:
                raise RuntimeError(f"Task worktree does not contain the main checkout edit: {name}")

    archive = main_root / "build" / ("publish-" + stamp)
    git(main_root, "check-ignore", str(archive / "build.log"))
    archive.mkdir(parents=True)
    print(f"Building in {work}\nBuild log: {archive / 'build.log'}", flush=True)
    with (archive / "build.log").open("wb") as log:
        result = subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
             str(work / "scripts" / "build.ps1")], cwd=work,
            stdout=log, stderr=subprocess.STDOUT,
        )
    if result.returncode:
        raise RuntimeError(f"Compilation failed; files retained in {work}. See {archive / 'build.log'}")
    git(work, "add", "--all")
    if git(work, "diff", "--cached", "--name-only"):
        print(git(work, "commit", "-m", args.message).decode().strip(), flush=True)

    # Do not replace edits made in the main checkout while compilation was running.
    if (git(main_root, "rev-parse", "HEAD") != base
            or git(main_root, "status", "--porcelain=v1", "-z") != status
            or changes(main_root) != source):
        raise RuntimeError(f"Main checkout changed during compilation; candidate retained in {work}.")
    git(main_root, "fetch", "origin")
    if git(main_root, "rev-parse", "origin/main") != base:
        raise RuntimeError(f"Remote main advanced; candidate retained in {work} for integration.")

    # The originals are now committed in the task branch. Clear only that snapshot.
    existing = sorted(set(source) & original_paths)
    added = sorted(set(source) - original_paths)
    if existing:
        git(main_root, "restore", "--source=HEAD", "--staged", "--worktree", "--", *existing)
    if added:
        git(main_root, "reset", "HEAD", "--", *added)
        for name in added:
            target = (main_root / name).resolve()
            if not target.is_relative_to(main_root):
                raise RuntimeError(f"New file is outside the checkout: {name}")
            target.unlink()
    print(git(main_root, "merge", "--no-ff", branch, "-m", args.message).decode().strip(), flush=True)
    for stem in ("main", "supplementary", "paper_full", "manuscript_zh"):
        for suffix in (".aux", ".log", ".bbl", ".blg", ".brf", ".out"):
            artifact = work / (stem + suffix)
            if artifact.exists():
                shutil.copy2(artifact, main_root / artifact.name)
    git(main_root, "push", "origin", "main")
    print("Pushed main: " + git(main_root, "rev-parse", "HEAD").decode().strip(), flush=True)
    if created:
        os.chdir(main_root)
        git(main_root, "worktree", "remove", str(work))
        git(main_root, "branch", "-d", branch)
    else:
        print(f"Existing task worktree retained: {work}", flush=True)


if __name__ == "__main__":
    main()
