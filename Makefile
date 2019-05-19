samples=$(wildcard samples/*.go)
revealed=$(patsubst %.go,%-default.tex,$(samples))

all: example.pdf logo.pdf

example.pdf: style-paraiso-dark.tex $(revealed)

logo.pdf: style-tango.tex samples/logo-default.tex

%.pdf: %.tex
	xelatex $*

style-%.tex: reveal.py
	./$< --style $* style --output $@

%-default.tex: reveal.py %.go
	./$< generate --input $*.go

%-default.tex: reveal.py %.tex
	./$< generate --input $*.tex --comment-chars '%'

slides/%-0.png: %.pdf
	mkdir -p slides
	convert -density 150 -antialias $< -resize 512x -quality 90 "slides/$*.png"

%.imgur: %.png
	imgur -a=true $< | tr -d '\n' > $@

logo.png: slides/logo-0.png
	convert slides/logo-1.png -trim $@

%.md: %.md.j2
	j2 $< > $@

README.md: $(foreach slide,0 1 2 3 10 11 12,slides/example-$(slide).imgur)

clean:
	$(RM) *.pdf syntax.tex samples/*.tex

tools:
	go get -u github.com/mattn/imgur
	pip install j2cli

.PHONY: all clean tools
