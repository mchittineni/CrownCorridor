#!/usr/bin/env python3
"""Fetches the unlabelled external subset at its pinned commits.

Why this exists
---------------
``benchmark/external/aws_samples/manifest.json`` names 25 third-party repositories
by exact commit. This script materialises them and refuses to proceed on any
mismatch, so a measurement can never quietly run against a moved upstream branch.

The working trees are NOT vendored into this repository. Vendoring 15,226 lines of
third-party Terraform would put the corpus's provenance in a git subtree that is
indistinguishable, after the fact, from code this project wrote. A pinned commit is
both smaller and stronger evidence: anyone can fetch the same bytes and check the
hash. MIT-0 would permit vendoring; provenance is the reason not to.

Usage
-----
    python -m experiments.fetch_external            # clone or verify every repo
    python -m experiments.fetch_external --check    # verify only; exit 1 if absent or moved
    python -m experiments.fetch_external --dest DIR # materialise somewhere else

Requires ``git`` and network access on first use.
"""

from __future__ import annotations

import argparse
import functools
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "benchmark" / "external" / "aws_samples" / "manifest.json"
DEFAULT_DEST = ROOT / ".external-corpus"


def _load() -> dict:
    if not MANIFEST.is_file():
        sys.exit(f"error: {MANIFEST.relative_to(ROOT)} not found.")
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


@functools.cache
def _git_executable() -> str:
    """The absolute path to ``git``, resolved once.

    Invoked as an absolute path rather than the bare name ``git``, and cached so
    every call in one run uses the same executable. A fetcher that re-resolved the
    name per call could be pointed at a different ``git`` midway through, and this
    script's whole purpose is to make the fetched bytes attributable to a pinned
    commit -- provenance that a substitutable fetcher would undercut.

    Resolution is deferred to first use rather than done at import, so the module
    stays importable on a machine without git.
    """
    found = shutil.which("git")
    if found is None:
        sys.exit("error: git not found on PATH; it is required to fetch the pinned corpus.")
    return found


def _git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [_git_executable(), *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )


def head_of(path: Path) -> str | None:
    """The checked-out commit, or None when ``path`` is not a git work tree."""
    if not (path / ".git").exists():
        return None
    proc = _git("rev-parse", "HEAD", cwd=path)
    return proc.stdout.strip() if proc.returncode == 0 else None


def _materialise(repo: str, want: str, path: Path, *, fresh: bool) -> str | None:
    """Fetches ``want`` into ``path``; returns an error detail, or None on success.

    Split out of fetch_one so that each function reports on one thing: this one on
    whether the pinned object arrived, its caller on what the repository's state now
    is. The four git steps each fail differently and each failure has to keep its
    own message, since "fetch failed" and "the commit checked out is not the one the
    manifest pins" call for entirely different responses from a reader.
    """
    if fresh:
        init = _git("init", "--quiet", str(path))
        if init.returncode != 0:
            return (init.stderr or "git init failed").strip()
        _git("remote", "add", "origin", f"https://github.com/{repo}.git", cwd=path)

    # A pinned commit may not be the branch tip, so a depth-1 branch clone is not
    # enough. Fetch the single object by hash into an empty repository instead.
    fetched = _git("fetch", "--quiet", "--depth", "1", "origin", want, cwd=path)
    if fetched.returncode != 0:
        return (fetched.stderr or "fetch failed").strip().splitlines()[-1][:120]

    checked = _git("checkout", "--quiet", "--force", want, cwd=path)
    if checked.returncode != 0:
        return (checked.stderr or "checkout failed").strip().splitlines()[-1][:120]

    got = head_of(path)
    if got != want:
        return f"checked out {got} but manifest pins {want}"
    return None


def fetch_one(entry: dict, dest: Path, *, check_only: bool) -> tuple[str, str]:
    """Returns ``(status, detail)`` for one repository.

    Status is one of ``present`` (correct commit already there), ``fetched``,
    ``moved`` (a different commit is checked out), ``absent`` or ``error``.
    """
    repo, want = entry["repo"], entry["commit"]
    path = dest / repo.replace("/", "_")
    have = head_of(path)

    if have == want:
        return "present", want[:12]
    if check_only:
        return ("moved", f"have {have[:12]}, want {want[:12]}") if have else ("absent", want[:12])

    path.mkdir(parents=True, exist_ok=True)
    failure = _materialise(repo, want, path, fresh=have is None)
    if failure is not None:
        return "error", failure
    return "fetched", want[:12]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", maxsplit=1)[0])
    ap.add_argument("--check", action="store_true", help="verify only; do not fetch")
    ap.add_argument("--dest", type=Path, default=DEFAULT_DEST, help="where to materialise")
    args = ap.parse_args(argv)

    doc = _load()
    repos = doc["repositories"]
    args.dest.mkdir(parents=True, exist_ok=True)

    counts: dict[str, int] = {}
    failures: list[str] = []
    for entry in repos:
        status, detail = fetch_one(entry, args.dest, check_only=args.check)
        counts[status] = counts.get(status, 0) + 1
        if status in ("moved", "absent", "error"):
            failures.append(f"  {entry['repo']}: {status} ({detail})")
        print(f"{status:8s} {entry['repo']}  {detail}")

    print("\n" + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    if failures:
        print(f"\n{len(failures)} repositories are not at their pinned commit:", file=sys.stderr)
        for line in failures:
            print(line, file=sys.stderr)
        if args.check:
            print("run: python -m experiments.fetch_external", file=sys.stderr)
        return 1
    print(f"all {len(repos)} repositories are at their pinned commits in {args.dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
