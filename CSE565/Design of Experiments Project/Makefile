# Build the CSE 565 Design of Experiments report.

REPORT := Coleman_Chase_CSE 565_Design of Experiments Project

.PHONY: all clean

all:
	latexmk -pdf -interaction=nonstopmode -halt-on-error "$(REPORT).tex"

clean:
	latexmk -C "$(REPORT).tex"
