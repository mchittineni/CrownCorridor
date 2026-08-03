"""One opt-in gate shared by every stage that fabricates metrics.

Several legacy stages in this repository do not execute a scanner. They multiply
corpus counts by hardcoded ``detection_rate`` / ``fp_rate`` / ``base_latency_ms``
constants and emit the product in the same file formats, and under the same
names, that the real harness writes. ``results/benchmark_results.json`` is
produced this way; so are ``results/charts/`` and ``results/metrics.csv``.

That collision is the hazard. A reader cannot tell a fabricated
``benchmark_results.json`` from a measured one by looking at it, and neither can
a later stage that consumes it. ``experiments/run_all.sh`` used to set the
override for the whole suite, so an editor-triggered run would silently
overwrite measured output with assumed numbers and then publish the result to an
external vault.

Every such stage now calls :func:`refuse_unless_explicitly_allowed` before it
writes anything. Running one is still possible -- these artefacts have a use as
illustrative placeholders -- but it now takes a deliberate, per-invocation act
that names what it is producing.
"""

from __future__ import annotations

import os
import sys

GUARD_ENV = "IACSECBENCH_ALLOW_SYNTHETIC"


def refuse_unless_explicitly_allowed(
    what: str,
    *,
    writes: str = "",
    measure_instead: str = "experiments/run_baselines.sh",
    override_hint: str = "",
) -> None:
    """Exits unless the caller has explicitly opted into fabricated output.

    Args:
        what: What this stage fabricates, as a noun phrase completing
            "this module fabricates ...".
        writes: Paths this stage would overwrite, if it overwrites anything a
            measured run also produces. Named so the cost of the override is
            visible at the point of decision.
        measure_instead: The command that produces the real equivalent.
        override_hint: The exact command that opts in. Defaults to a generic
            form when the caller does not supply one.
    """
    if os.environ.get(GUARD_ENV) == "1":
        message = (
            f"WARNING: {GUARD_ENV}=1 -- emitting SYNTHETIC {what}. "
            "No scanner is executed. Not a measurement; must not be published."
        )
        if writes:
            message += f"\n         Overwrites: {writes}"
        print(message, file=sys.stderr)
        return

    lines = [
        f"refusing to run: this module fabricates {what}.",
        "  No scanner is executed; numbers are corpus counts multiplied by",
        "  hardcoded rates.",
    ]
    if writes:
        lines.append(f"  It would overwrite: {writes}")
    lines.append("")
    lines.append(f"  Measure instead:  {measure_instead}")
    lines.append(
        f"  Override (not for publication):  {override_hint or f'{GUARD_ENV}=1 <command>'}"
    )
    sys.exit("\n".join(lines))
