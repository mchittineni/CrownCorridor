# Manuscript figures

Two figures are drawings; the third is set as a listing in the manuscript source.

| Figure              | Source                                 | Rendered                     | Size at 3.5in column |
| ------------------- | -------------------------------------- | ---------------------------- | -------------------- |
| `fig:pipeline`      | `pipeline_architecture.mmd`            | `pipeline_architecture.pdf`  | 3.5 x 4.24in         |
| `fig:normalization` | `normalization_workflow.mmd`           | `normalization_workflow.pdf` | 3.5 x 2.83in         |
| `fig:artifact`      | inline `verbatim` in `iacsecbench.tex` | n/a                          | n/a                  |

Both rendered figures are **single-page vector PDFs with no raster content and no
alpha channel**, set in Times to sit alongside the body text. Re-render after any
re-measurement; `experiments/generate_figures.py --check` fails if the committed
`.mmd` sources no longer match the recorded results, which is suitable for CI.

If a `.pdf` is ever missing, `\paperfigure` prints a visible placeholder box naming
the file rather than letting the build appear complete.

## Rendering

```sh
cd <repo root>
python -m experiments.generate_figures        # refresh .mmd from recorded results
for f in pipeline_architecture normalization_workflow; do
  npx -y @mermaid-js/mermaid-cli \
      -i paper/figures/$f.mmd -o paper/figures/$f.pdf \
      --pdfFit -c paper/figures/mermaid.json -C paper/figures/mermaid.css -b white
done
```

`mermaid.json` sets the serif font stack and the node/rank spacing; `mermaid.css`
adjusts label sizes and stroke weights. Without `-c mermaid.json` the diagrams come
out in Trebuchet, which reads as foreign matter in a serif paper: a CSS override
alone loses to Mermaid's inline styles, so the theme variables are the part that
actually takes effect.

`--pdfFit` is not optional. Without it the page is sized to US Letter and a wide
diagram is paginated across several pages, of which `\includegraphics` embeds only
the first. Verify one page before committing:

```sh
python3 - <<'PY'
import re, zlib, glob
for p in sorted(glob.glob('paper/figures/*.pdf')):
    d = open(p, 'rb').read(); t = d
    for m in re.finditer(rb'stream\r?\n', d):
        s, e = m.end(), d.find(b'endstream', m.end())
        if e > 0:
            try: t += zlib.decompress(d[s:e].strip(b'\r\n'))
            except Exception: pass
    print(p, 'pages:', len(re.findall(rb'/Type\s*/Page(?![sR])', t)))
PY
```

Then the `\paperfigure` calls need their extension dropped so graphicx prefers the
PDF (`figures/pipeline_architecture` rather than `...png`), or changed to `.pdf`
explicitly.

## Why the sources are generated

The figures shipped with an earlier revision were exported images with numbers
typed into them. They asserted:

- a corpus of **345** cases, 176 vulnerable / 169 secure
- **Terrascan v1.18.1** as an evaluated engine
- no Trivy at all
- Checkov 3.2.0, tfsec 1.28.1, OPA 0.62.0
- per-layer latencies of 0.4 s / 21.8 s / 5.9 s

Against a manuscript reporting 48 admissible cases (26/22), excluding Terrascan,
evaluating Trivy, measuring Checkov 3.3.8 / tfsec v1.28.14 / OPA 1.19.0, and
recording layer latencies of 0.2 ms and 18.1 ms.

The 345 was not invented: it is `catalogue_gap.internal_declared` from
`results/corpus_report.json`, the declared internal catalogue count. The paper
argues at length that the _admissible_ count is the corpus size and the declared
count is not. The figure showed the number the paper rejects, unlabelled.

None of this was detectable from the figures, because they had no source in the
repository. `experiments/generate_figures.py` now reads every quantity from
`results/evaluation.json`, `results/run_manifest.json`, and
`results/corpus_report.json`, so a figure cannot disagree with a table unless the
generator is wrong for both. `--check` fails if the committed sources are stale,
which is suitable for CI.

## Print requirements when re-rendering

The manuscript targets Empirical Software Engineering and is set **single
column**. The figures were originally sized for a two-column IEEE measure, so the
constraints below changed when the venue did.

- **Vector PDF** rather than PNG. Vector output has no resolution to be wrong
  about, which removes the whole class of problem the superseded PNGs had: they
  rendered at 231-406 dpi, and `pipeline_architecture.png` fell below the 300 dpi
  that raster images in print generally need.
- **No alpha channel.** All three superseded PNGs were RGBA. pdfTeX handles
  transparency, but publisher preflight tooling sometimes flags it, and `--pdfFit`
  avoids the question entirely.
- **Check legibility at the rendered size, which is now one measure, not two.**
  Springer's `smallextended` text block is a single column, and the manuscript's
  fallback build sets it to 117 mm; `\linewidth` is what `\paperfigure` scales to
  in either. A figure wider than about 1.4:1 loses height at this measure, which
  is why the replication-package layout is a `verbatim` listing rather than a
  drawing: as a 10:1 strip its labels fell to roughly 3 pt.
- **There is no `figure*` any more.** A both-columns float has no meaning in a
  one-column class. If a diagram will not fit, redraw it taller rather than
  reaching for a spanning float.
