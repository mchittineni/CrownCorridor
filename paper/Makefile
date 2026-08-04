# IaCSecBench manuscript build.
#
# `make` rebuilds the result tables from recorded tool output before typesetting,
# so the PDF cannot silently contain stale numbers. Use `make paper` to typeset
# without re-measuring.

SHELL   := /bin/bash
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

DIST    := dist

.PHONY: all paper tables clean distclean check dist

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

## Build a self-contained submission bundle.
##
## The working tree keeps the result tables in ../results/tables/ so that the
## generator owns them and the manuscript cannot drift from the measurements. That
## layout does not survive submission: IEEE and arXiv unpack the source into one
## directory, where `\input{../results/tables/...}` resolves to nothing and the
## build dies with six missing-file errors. So the bundle flattens the tables in
## and redefines \resulttable to read them locally. The manuscript source is not
## edited -- the redefinition is appended to a copy.
dist: $(TEX).pdf
	rm -rf $(DIST)
	mkdir -p $(DIST)/figures $(DIST)/tables
	cp $(TEX).tex refs.bib $(DIST)/
	cp $(TABLES)/*.tex $(DIST)/tables/
	@# Only the rendered figures, and only those that exist: figures/ also holds the
	@# .mmd sources, the mermaid config, and superseded/, none of which belong in a
	@# submission. A missing figure must not fail the bundle either, because
	@# \paperfigure degrades to a visible placeholder box that the check below
	@# reports. `find -exec' rather than a glob, so an empty match is not an error.
	@find figures -maxdepth 1 -type f \( -name '*.pdf' -o -name '*.eps' \) \
	  -exec cp {} $(DIST)/figures/ \;
	@# Redirect \resulttable at the flattened copies. Delegated to a script because
	@# the replacement text is backslashes, braces and a `#' parameter marker, each
	@# of which make or the shell would consume first.
	@python3 flatten_for_submission.py $(DIST)/$(TEX).tex
	@# The bundle must build on its own, with no parent directory present.
	@command -v tectonic >/dev/null 2>&1 || command -v pdflatex >/dev/null 2>&1 || { \
	  echo "warning: no LaTeX engine; bundle assembled but NOT verified."; exit 0; }
	@echo "verifying the bundle builds standalone..."
	@cd $(DIST) && { \
	  if command -v tectonic >/dev/null 2>&1; then \
	    tectonic -X compile --keep-intermediates $(TEX).tex >/dev/null; \
	  else \
	    $(LATEX) $(TEX) >/dev/null && $(BIBTEX) $(TEX) >/dev/null 2>&1; \
	    $(LATEX) $(TEX) >/dev/null && $(LATEX) $(TEX) >/dev/null; \
	  fi; }
	@grep -l 'figure not yet produced' $(DIST)/$(TEX).log >/dev/null 2>&1 && \
	  echo "NOTE: bundle contains figure placeholders; regenerate figures/ first." || true
	tar -czf $(TEX)-submission.tar.gz -C $(DIST) .
	@echo
	@echo "Built $(TEX)-submission.tar.gz from $(DIST)/"
	@echo "Check the PDF in $(DIST)/ before uploading."

clean:
	rm -f $(TEX).aux $(TEX).log $(TEX).bbl $(TEX).blg $(TEX).out $(TEX).toc

distclean: clean
	rm -rf $(TEX).pdf $(DIST) $(TEX)-submission.tar.gz
