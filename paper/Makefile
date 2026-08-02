# IaCSecBench manuscript build.
#
# `make` rebuilds the result tables from recorded tool output before typesetting,
# so the PDF cannot silently contain stale numbers. Use `make paper` to typeset
# without re-measuring.

TEX     := iacsecbench
LATEX   := pdflatex -interaction=nonstopmode -halt-on-error
BIBTEX  := bibtex
TABLES  := ../results/tables

# Engine selection. tectonic resolves packages and runs BibTeX itself, so it
# needs no explicit multi-pass sequence; a TeX Live installation does. Preferring
# whichever is present keeps the build working on machines with either, rather
# than failing on a hardcoded binary that happens to be absent.
HAVE_TECTONIC := $(shell command -v tectonic 2>/dev/null)
HAVE_PDFLATEX := $(shell command -v pdflatex 2>/dev/null)

.PHONY: all paper tables clean distclean check

all: tables paper

## Regenerate every table from recorded raw tool output.
tables:
	cd .. && bash experiments/run_baselines.sh

## Typeset only. Fails if a result table is missing.
paper: $(TEX).pdf

$(TEX).pdf: $(TEX).tex refs.bib
	@test -f $(TABLES)/performance.tex || { \
	  echo "error: $(TABLES)/performance.tex missing."; \
	  echo "       Run 'make tables' -- do not hand-write result tables."; \
	  exit 1; }
ifneq ($(HAVE_TECTONIC),)
	tectonic -X compile --keep-intermediates $(TEX).tex
else ifneq ($(HAVE_PDFLATEX),)
	$(LATEX) $(TEX)
	$(BIBTEX) $(TEX) || true
	$(LATEX) $(TEX)
	$(LATEX) $(TEX)
else
	@echo "error: no LaTeX engine found. Install tectonic (brew install tectonic)"
	@echo "       or a TeX Live distribution providing pdflatex."
	@exit 1
endif
	@echo
	@echo "Built $(TEX).pdf"
	@grep -c 'TODO(author)' $(TEX).tex | xargs -I{} echo "NOTE: {} unresolved TODO(author) markers remain in $(TEX).tex"

## Report anything that would embarrass the submission.
check:
	@echo "== unresolved author TODOs =="
	@grep -n 'TODO(author)' $(TEX).tex || echo "  none"
	@echo
	@echo "== ampersands to review (tabular rows are fine; prose is not) =="
	@grep -n '[^\\&]&[^&]' $(TEX).tex | grep -v '\\\\' | grep -v '^\s*[0-9]*:\s*%' || echo "  none found"
	@echo
	@echo "== Markdown bold left in source =="
	@grep -n '\*\*' $(TEX).tex || echo "  none"
	@echo
	@echo "== citations in .tex absent from refs.bib =="
	@for k in $$(grep -o '\\cite{[^}]*}' $(TEX).tex | sed 's/\\cite{//;s/}//' | tr ',' '\n' | tr -d ' ' | sort -u); do \
	  grep -q "{$$k," refs.bib || echo "  MISSING: $$k"; done; echo "  (blank means all resolve)"
	@echo
	@echo "== refs.bib entries never cited =="
	@for k in $$(grep -o '^@[a-z]*{[^,]*' refs.bib | sed 's/^@[a-z]*{//'); do \
	  grep -q "$$k" $(TEX).tex || echo "  UNCITED: $$k"; done; echo "  (uncited entries are citation padding; remove them)"

clean:
	rm -f $(TEX).aux $(TEX).log $(TEX).bbl $(TEX).blg $(TEX).out $(TEX).toc

distclean: clean
	rm -f $(TEX).pdf
