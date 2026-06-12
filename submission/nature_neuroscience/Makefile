TEX=pdflatex
BIB=bibtex
OUTDIR=../submission/compiled_pdfs

.PHONY: all unblinded blinded target supplement figures clean

figures:
	python render_figure_pdfs.py

define build_one
	$(TEX) -interaction=nonstopmode -halt-on-error $(1)
	$(BIB) $(basename $(1))
	$(TEX) -interaction=nonstopmode -halt-on-error $(1)
	$(TEX) -interaction=nonstopmode -halt-on-error $(1)
endef

all: unblinded blinded target supplement

unblinded:
	$(call build_one,main_unblinded.tex)
	mkdir -p $(OUTDIR)
	cp main_unblinded.pdf $(OUTDIR)/main_unblinded_R7.pdf

blinded:
	$(call build_one,main_blinded.tex)
	mkdir -p $(OUTDIR)
	cp main_blinded.pdf $(OUTDIR)/main_blinded_R7.pdf

target:
	$(call build_one,target_journal.tex)
	mkdir -p $(OUTDIR)
	cp target_journal.pdf $(OUTDIR)/target_journal_R7.pdf

supplement:
	cd supplement && $(TEX) -interaction=nonstopmode -halt-on-error supplement.tex && $(BIB) supplement && $(TEX) -interaction=nonstopmode -halt-on-error supplement.tex && $(TEX) -interaction=nonstopmode -halt-on-error supplement.tex
	mkdir -p $(OUTDIR)
	cp supplement/supplement.pdf $(OUTDIR)/supplement_R7.pdf

clean:
	del /Q *.aux *.bbl *.blg *.log *.out *.toc 2>NUL || true
	cd supplement && del /Q *.aux *.bbl *.blg *.log *.out *.toc 2>NUL || true
