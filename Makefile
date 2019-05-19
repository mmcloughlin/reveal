style=paraiso-dark
samples=$(wildcard samples/*.go)
revealed=$(patsubst %.go,%-default.tex,$(samples))

all: example.pdf

example.pdf: syntax.tex $(revealed)

%.pdf: %.tex
	xelatex $*

syntax.tex: reveal.py
	./$< --style $(style) style --output $@

%-default.tex: reveal.py %.go
	./$< --style $(style) generate --input $*.go

clean:
	$(RM) *.pdf syntax.tex samples/*.tex

.PHONY: all clean
