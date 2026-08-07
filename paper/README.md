# IaCSecBench Manuscript (`paper/`)

LaTeX source, bibliography, figures, and build automation for the **IaCSecBench**
paper. **Target venue: Empirical Software Engineering (Springer).**

## 📄 Contents

| Path                        | Role                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| `iacsecbench.tex`           | The manuscript.                                                                               |
| `refs.bib`                  | Bibliography, 52 entries. Every DOI resolves in Crossref or DataCite; none was typed by hand. |
| `Makefile`                  | Build automation. Prefers `tectonic`, falls back to `pdflatex` + `bibtex`.                    |
| `figures/`                  | Two generated diagrams plus their sources. See `figures/README.md`.                           |
| `flatten_for_submission.py` | Rewrites `\resulttable` in the bundle copy so tables resolve locally. Invoked by `make dist`. |

**No result table lives here.** All eight are generated into `results/tables/` by
`evaluation/analyze.py` and `evaluation/corpus.py`, and pulled in with
`\resulttable`. `make` refuses to typeset if any is missing, so the manuscript
cannot contain a hand-written number.

## ⚠️ The class file you must fetch before submitting

EMSE requires Springer's **`svjour3`** class. Springer distributes it only in its
own template archive: it is **not on CTAN** and not in any TeX distribution's
package set, so no build can fetch it automatically.

```
# once, before submission
#   1. download the LaTeX template from the EMSE submission-guidelines page
#   2. place svjour3.cls, svglov3.clo and spbasic.bst in this directory
```

The manuscript detects them and switches automatically:

```latex
\newif\ifhassvjour
\IfFileExists{svjour3.cls}{\hassvjourtrue}{\hassvjourfalse}
\ifhassvjour \documentclass[smallextended]{svjour3}
\else        \documentclass[11pt,a4paper]{article} \fi
```

Without them the paper builds under `article` at a text measure of **117 mm**,
deliberately narrower than Springer's `smallextended`. That is the conservative
direction: **anything that fits in the fallback fits in the real class.** Every
table is additionally set with `tabularx` against `\linewidth`, so no table can
overrun whatever measure the class sets. `make` prints a NOTE on every fallback
build so you cannot ship the wrong one by accident, and `make dist` copies the
Springer files into the bundle when they are present.

The bibliography style switches the same way: `spbasic` when present, `plainnat`
otherwise. Both are author–year, so citations render in EMSE's form either way.

## 🛠️ Building

```bash
cd paper
make          # regenerate tables from recorded output, then typeset
make paper    # typeset only, no re-measurement
make check    # report anything that would embarrass a submission
make clean    # remove intermediates
```

`make check` covers unresolved `TODO(author)` markers, bare `\cite` (ambiguous
under natbib author–year), ampersands loose in prose, Markdown bold left in the
source, citations absent from `refs.bib`, and `refs.bib` entries never cited.

**Three `TODO(author)` markers are open and block submission**, all one fact: the
identity of the large language model used as the second rater in the blind
relabelling pass. Springer requires methodological AI use to be disclosed in the
methods, and an unnamed automated rater is not reproducible. The disclosure
paragraph is written and sits in Section 4.3; it draws the two missing values from
`\ratermodel` and `\rateraccess`, defined together in the preamble, which render as
visible placeholders in the PDF until filled. Paste the verbatim prompt into
[`benchmark/labelling/rater_prompt.txt`](../benchmark/labelling/rater_prompt.txt),
which the manuscript cites by path, and record the same two values under `method`
in `independent_relabelling.json`.

## ✅ EMSE format compliance

Checked against Springer's [EMSE submission
guidelines](https://link.springer.com/journal/10664/submission-guidelines):

| Requirement                                            | Status                                        |
| ------------------------------------------------------ | --------------------------------------------- |
| Abstract 150–250 words                                 | 249, structured (Context…Conclusion)          |
| 4–6 keywords                                           | 6                                             |
| Single-blind review                                    | no anonymisation needed; author details stay  |
| Statements and Declarations (Springer's exact heading) | present, all seven sub-statements             |
| Affiliation as institution, city, country              | **open** — currently a job title, no city     |
| ORCID                                                  | **absent** (recommended, not mandatory)       |
| `svjour3` class files                                  | **absent** — fetch before `make dist`         |
| DOIs as full links in references                       | 43 of 52; the other 9 are books and standards |

The abstract is 1 word under the ceiling. **Re-run the count after any edit to
it** — an added clause is a format violation, not a style choice.

## 📦 Submission bundle

```bash
cd paper
make dist     # -> iacsecbench-submission.tar.gz
```

The working tree keeps result tables in `../results/tables/` so the generator owns
them. That path does not survive submission: publishers unpack the source into a
single directory, where `\input{../results/tables/...}` resolves to nothing and the
build fails once per table. `make dist` flattens the tables and figures into
`dist/`, redirects `\resulttable` at the copy, copies Springer's class files if
present, **compiles the bundle standalone to prove it builds**, and only then tars
it. `dist/` and the tarball are gitignored; they are pure derived output.

## 🖼️ Figures

Two diagrams are generated, not hand-drawn: `experiments/generate_figures.py`
writes their Mermaid sources from `results/evaluation.json` and
`results/run_manifest.json`, so a figure cannot assert a corpus size or tool
version that disagrees with a table. The third figure, the replication-package
layout, is a `verbatim` listing inside the manuscript rather than a drawing.

Regenerate and re-render after any re-measurement:

```bash
python -m experiments.generate_figures      # refresh figures/*.mmd
# then the mmdc commands in figures/README.md
```

`generate_figures.py --check` exits non-zero if the committed sources no longer
match the recorded results, and runs in CI for that reason.

## ✍️ Conventions worth knowing before editing

- **Numeric table columns are `r`, never `c`.** Each emitter formats a column to a
  fixed number of decimal places, so right alignment lines the decimal points up.
  Centring does not, once a value crosses from one integer digit to two. `siunitx`
  is deliberately absent: the fixed decimal places make it unnecessary, and its
  option names differ between versions 2 and 3.
- **`\citep` and `\citet`, never bare `\cite`.** natbib gives `\cite` different
  meanings in author–year and numeric modes; the explicit forms are unambiguous in
  both. `make check` now flags bare `\cite`, because when the manuscript moved to
  author–year the old check silently passed on every citation.
- **Long file paths use `\path{...}`, not `\texttt{...}`.** A path in `\texttt` is
  one unbreakable token and overflows a one-column measure. `\path` breaks after
  `/` without inserting a hyphen, and needs no `_` escaping. It is **fragile**:
  inside a `\caption` it fails with "`\url` used in a moving argument", so use
  `\texttt` there.
- **Em-dashes are not used in the prose.** A previous revision deleted 24 of them
  without restructuring the surrounding sentences, leaving 24 ungrammatical
  sentences including one in the abstract. Where a parenthetical is needed, use
  commas, parentheses, or a sentence break.
- **A missing figure prints a visible placeholder box** rather than failing the
  build, so an incomplete figure set cannot pass silently as finished work.
