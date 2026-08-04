#!/usr/bin/env python3
r"""Rewrites a copied manuscript so its result tables resolve inside the bundle.

The working tree keeps generated tables in ``results/tables/`` and reaches them
with ``\input{../results/tables/...}``, so the generator owns them and the
manuscript cannot drift from the measurements. That path does not survive
submission: Springer and arXiv unpack the source into a single directory, where the
parent reference resolves to nothing and the build fails once per table.

This appends a ``\renewcommand`` for ``\resulttable`` immediately before
``\begin{document}``, after the preamble definition it overrides. It edits the
copy inside the bundle, never the tracked source.

Kept as a script rather than inlined into the Makefile because the replacement
text is made of backslashes, braces and a ``#`` parameter marker, each of which is
consumed by make or by the shell before reaching the file.

    python3 flatten_for_submission.py dist/iacsecbench.tex
"""

from __future__ import annotations

import pathlib
import sys

MARKER = "% ---- injected by `make dist`: flattened table paths ----"


def flatten(path: pathlib.Path) -> str:
    source = path.read_text(encoding="utf-8")

    if MARKER in source:
        return f"{path}: already flattened, left alone"

    anchor = "\\begin{document}"
    at = source.find(anchor)
    if at < 0:
        raise SystemExit(f"error: {path} has no {anchor}; not a manuscript source")

    if "\\resulttable" not in source[:at]:
        raise SystemExit(
            f"error: {path} does not define \\resulttable in its preamble.\n"
            "       The table-input mechanism has changed and this script is stale;\n"
            "       fix it rather than shipping a bundle whose tables silently vanish."
        )

    injection = "\n".join(
        [
            "",
            MARKER,
            "\\renewcommand{\\resulttable}[1]{\\input{tables/#1.tex}}",
            "",
        ]
    )
    path.write_text(source[:at] + injection + source[at:], encoding="utf-8")
    return f"{path}: \\resulttable redirected to tables/"


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    target = pathlib.Path(argv[1])
    if not target.is_file():
        raise SystemExit(f"error: {target} not found")
    print(flatten(target))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
