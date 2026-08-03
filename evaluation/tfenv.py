"""Concurrency-safe Terraform provider provisioning.

Terraform's shared plugin cache (``TF_PLUGIN_CACHE_DIR``) is explicitly
documented as not safe for concurrent use: two ``terraform init`` runs writing
the same cache entry race on partially-extracted packages. When that race is
lost, terraform reports

    registry.terraform.io/hashicorp/aws: the cached package for ... does not
    match any of the checksums recorded in the dependency lock file
    Unrecognized remote plugin message: ...

Those messages are indistinguishable, at the call site, from a genuinely
malformed case. That matters here: the admissibility pass classifies an ``init``
failure as ``invalid_hcl``, so cache contention silently converts valid corpus
cases into inadmissible ones and shrinks the reported denominator. Observed
directly in this repository: the same 44 generated cases reported 44, then 36,
then 26 admissible depending on what else was running.

This module removes the race rather than papering over it with retries. A
*filesystem mirror* is populated once, under an exclusive lock, and every
subsequent ``terraform init`` reads it through ``-plugin-dir``. Mirrors are
read-only during init, so any number of processes may share one safely.

Callers use::

    mirror = ensure_provider_mirror()
    subprocess.run([tf, *init_args(mirror)], cwd=workdir, env=terraform_env())

``ensure_provider_mirror`` returns None when no mirror could be built (no
terraform, or no network on a cold cache); ``init_args`` then falls back to
ordinary registry resolution so behaviour degrades rather than breaks.
"""

from __future__ import annotations

import fcntl
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR_DIR = ROOT / ".terraform-provider-mirror"
LOCK_FILE = ROOT / ".terraform-provider-mirror.lock"

# The corpus pins a single provider. Kept in one place so the mirror and the
# generated cases cannot drift apart.
MIRROR_CONFIG = """\
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
"""

__all__ = ["ensure_provider_mirror", "init_args", "terraform_env", "mirror_is_populated"]


def terraform_env() -> dict[str, str]:
    """Environment for a hermetic, non-interactive terraform invocation.

    Deliberately omits ``TF_PLUGIN_CACHE_DIR``: the mirror supersedes it, and
    leaving it set would reintroduce the write race this module exists to avoid.
    """
    return {
        "TF_IN_AUTOMATION": "1",
        "TF_INPUT": "0",
        "CHECKPOINT_DISABLE": "1",
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin"),
        "HOME": os.environ.get("HOME", str(Path.home())),
    }


def mirror_is_populated(mirror: Path = MIRROR_DIR) -> bool:
    """True when the mirror holds at least one provider package."""
    if not mirror.is_dir():
        return False
    return any(mirror.rglob("*.zip"))


def init_args(mirror: Path | None) -> list[str]:
    """Arguments for ``terraform init`` against ``mirror``.

    Falls back to registry resolution when no mirror is available, so a machine
    without one still works -- just without the concurrency guarantee.
    """
    args = ["init", "-backend=false", "-no-color", "-input=false"]
    if mirror is not None and mirror_is_populated(mirror):
        args.append(f"-plugin-dir={mirror}")
    return args


def ensure_provider_mirror(mirror: Path = MIRROR_DIR, *, timeout: int = 900) -> Path | None:
    """Populates the provider mirror once; returns its path, or None on failure.

    Safe to call concurrently. The first caller to acquire the lock builds the
    mirror; the others block, then observe the finished result. The download is
    staged into a temporary directory and moved into place only on success, so a
    crashed or interrupted build cannot leave a half-populated mirror that later
    runs would treat as usable.
    """
    if mirror_is_populated(mirror):
        return mirror

    terraform = shutil.which("terraform")
    if terraform is None:
        return None

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOCK_FILE, "w", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        # Re-check under the lock: another process may have finished while we
        # were blocked, in which case there is nothing left to do.
        if mirror_is_populated(mirror):
            return mirror

        with tempfile.TemporaryDirectory(prefix="iacsb-mirror-") as tmp:
            config_dir = Path(tmp) / "config"
            config_dir.mkdir()
            (config_dir / "versions.tf").write_text(MIRROR_CONFIG, encoding="utf-8")
            staging = Path(tmp) / "mirror"

            proc = subprocess.run(
                [terraform, "providers", "mirror", "-no-color", str(staging)],
                cwd=config_dir,
                capture_output=True,
                text=True,
                env=terraform_env(),
                timeout=timeout,
                check=False,
            )
            if proc.returncode != 0 or not any(staging.rglob("*.zip")):
                return None

            # Atomic-enough handoff: build beside the target, then rename.
            mirror.parent.mkdir(parents=True, exist_ok=True)
            if mirror.exists():
                shutil.rmtree(mirror)
            shutil.move(str(staging), str(mirror))

    return mirror if mirror_is_populated(mirror) else None


if __name__ == "__main__":  # pragma: no cover - operational helper
    import sys

    result = ensure_provider_mirror()
    if result is None:
        print("error: could not populate the provider mirror.", file=sys.stderr)
        print(
            "       terraform must be installed and the registry reachable once.", file=sys.stderr
        )
        sys.exit(1)
    packages = sorted(p.name for p in result.rglob("*.zip"))
    print(f"Provider mirror ready: {result}")
    for name in packages:
        print(f"  {name}")
