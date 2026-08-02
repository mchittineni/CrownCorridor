"""Regression tests for concurrency-safe provider provisioning.

The bug these guard against was not a crash. Terraform's shared plugin cache is
not safe for concurrent writes, and a lost race surfaces as an ``init`` failure
that the admissibility pass classifies as ``invalid_hcl``. Valid corpus cases
were therefore being silently reclassified as inadmissible, and the reported
corpus size varied with unrelated background load -- 44, then 36, then 26
admissible for one unchanged corpus.

A test that only checks "the mirror can be built" would not have caught it. What
matters is that the environment handed to terraform contains no shared-write
cache, and that init is directed at the read-only mirror.
"""

from __future__ import annotations

from pathlib import Path

from evaluation.tfenv import (
    ensure_provider_mirror,
    init_args,
    mirror_is_populated,
    terraform_env,
)


def test_env_does_not_set_shared_plugin_cache():
    """The regression itself: TF_PLUGIN_CACHE_DIR must not be reintroduced.

    Setting it re-enables the concurrent-write path even when a mirror is also
    supplied, because terraform still writes cache entries during init.
    """
    assert "TF_PLUGIN_CACHE_DIR" not in terraform_env()


def test_env_is_non_interactive_and_hermetic():
    env = terraform_env()
    assert env["TF_IN_AUTOMATION"] == "1"
    assert env["TF_INPUT"] == "0"
    assert env["CHECKPOINT_DISABLE"] == "1"
    # terraform must still be locatable, or every run reports "not installed".
    assert env["PATH"]


def test_init_args_point_at_the_mirror_when_populated(tmp_path: Path):
    mirror = tmp_path / "mirror"
    (mirror / "registry.terraform.io" / "hashicorp" / "aws").mkdir(parents=True)
    (mirror / "registry.terraform.io" / "hashicorp" / "aws" / "p.zip").write_bytes(b"stub")

    args = init_args(mirror)
    assert f"-plugin-dir={mirror}" in args
    assert "-backend=false" in args
    assert "-input=false" in args


def test_init_args_omit_plugin_dir_when_mirror_absent(tmp_path: Path):
    """Degrade to registry resolution rather than pointing init at an empty dir.

    ``-plugin-dir`` at an empty directory makes every provider unresolvable, so a
    failed mirror build must not be passed through as though it succeeded.
    """
    assert not any(a.startswith("-plugin-dir") for a in init_args(None))
    empty = tmp_path / "empty"
    empty.mkdir()
    assert not any(a.startswith("-plugin-dir") for a in init_args(empty))


def test_mirror_is_populated_requires_an_actual_package(tmp_path: Path):
    """A directory that exists but holds no package is not a usable mirror.

    This is the half-populated case left behind by an interrupted build.
    """
    empty = tmp_path / "mirror"
    empty.mkdir()
    assert mirror_is_populated(empty) is False
    assert mirror_is_populated(tmp_path / "does-not-exist") is False

    nested = empty / "registry.terraform.io" / "hashicorp" / "aws"
    nested.mkdir(parents=True)
    (nested / "terraform-provider-aws_5.0.0_darwin_arm64.zip").write_bytes(b"stub")
    assert mirror_is_populated(empty) is True


def test_ensure_returns_existing_mirror_without_rebuilding(tmp_path: Path):
    """Idempotence: a populated mirror is returned as-is.

    Verified by content rather than by mocking -- the stub package would be
    destroyed if the function rebuilt over it.
    """
    mirror = tmp_path / "mirror"
    package = mirror / "registry.terraform.io" / "hashicorp" / "aws"
    package.mkdir(parents=True)
    stub = package / "terraform-provider-aws_5.0.0_darwin_arm64.zip"
    stub.write_bytes(b"sentinel")

    assert ensure_provider_mirror(mirror) == mirror
    assert stub.read_bytes() == b"sentinel"
