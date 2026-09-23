# Build the CSE 565 Design of Experiments report.

REPORT := Coleman_Chase_CSE 565_Design of Experiments Project

.PHONY: all verify clean

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error "$(REPORT).tex"

verify:
	python3 verify_pairwise_coverage.py pict_pairwise_test_cases.tsv
	python3 verify_pairwise_coverage.py chatgpt_pairwise_test_cases.tsv

clean:
	latexmk -C "$(REPORT).tex"
