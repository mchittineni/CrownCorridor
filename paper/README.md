# IaCSecBench Academic Manuscript & Publication Materials (`paper/`)

This directory contains the LaTeX source code, bibliography, and build configurations for the **IaCSecBench** empirical research paper.

## 📄 Contents

- **`iacsecbench.tex`**: Main LaTeX document for the research paper detailing the evaluation framework methodology, threat model, benchmark datasets, and comparative empirical findings.
- **`refs.bib`**: BibTeX bibliography containing academic and industry references.
- **`Makefile`**: Build automation script for compiling LaTeX into PDF formats (`pdflatex` / `latexmk`).

## 🛠️ Building the Paper

To compile the manuscript PDF:

```bash
cd paper
make
```

To clean intermediate build artifacts:

```bash
cd paper
make clean
```
