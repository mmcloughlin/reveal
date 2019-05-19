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

slides/%-0.png: %.pdf
	mkdir -p slides
	convert -density 150 -antialias $< -resize 512x -quality 90 "slides/$*.png"

%.imgur: %.png
	imgur -a=true $< | tr -d '\n' > $@

%.md: %.md.j2
	j2 $< > $@

README.md: $(foreach slide,0 1 2 3 10 11 12,slides/example-$(slide).imgur)

clean:
	$(RM) *.pdf syntax.tex samples/*.tex

tools:
	go get -u github.com/mattn/imgur
	pip install j2cli

.PHONY: all clean tools
