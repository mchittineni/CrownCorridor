# Manuscript figures

Two figures are drawings; the third is set as a listing in the manuscript source.

| Figure | Source | Rendered | Size at 3.5in column |
|---|---|---|---|
| `fig:pipeline` | `pipeline_architecture.mmd` | `pipeline_architecture.pdf` | 3.5 x 4.24in |
| `fig:normalization` | `normalization_workflow.mmd` | `normalization_workflow.pdf` | 3.5 x 2.83in |
| `fig:artifact` | inline `verbatim` in `iacsecbench.tex` | n/a | n/a |

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
argues at length that the *admissible* count is the corpus size and the declared
count is not. The figure showed the number the paper rejects, unlabelled.

None of this was detectable from the figures, because they had no source in the
repository. `experiments/generate_figures.py` now reads every quantity from
`results/evaluation.json`, `results/run_manifest.json`, and
`results/corpus_report.json`, so a figure cannot disagree with a table unless the
generator is wrong for both. `--check` fails if the committed sources are stale,
which is suitable for CI.

## `superseded/`

The three original PNGs, retained for provenance and **not on `graphicspath`**, so
they cannot be picked up by a build. Delete them once the replacements are
rendered and reviewed.

## Print requirements when re-rendering

- **Vector PDF** rather than PNG. The superseded PNGs rendered at 231–406 dpi;
  `pipeline_architecture.png` in particular was under IEEE's 300 dpi preference for
  raster images (600 for line art).
- **No alpha channel.** All three superseded PNGs were RGBA. pdfTeX handles
  transparency, but IEEE PDF eXpress sometimes flags it. Vector output from
  `--pdfFit` avoids the question.
- Check legibility at the *rendered* size: one column is 3.5 in, both columns
  7.16 in. The superseded `artifact_structure.png` was a 10:1 strip whose labels
  fell to roughly 3 pt even across both columns, which is why it is now a listing.
