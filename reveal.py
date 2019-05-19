#!/usr/bin/env python3

from pygments import highlight
from pygments.lexers import get_lexer_for_filename, get_lexer_by_name
from pygments.lexer import RegexLexer, include, bygroups, using, words, DelegatingLexer
from pygments.token import Text, Name, Number, String, Comment, Punctuation, Other, Keyword, Operator
from pygments.formatters import LatexFormatter

import argparse
import logging
import sys
import collections
import re
import os.path
import shlex

# Line represents an annotated line of source code.
Line = collections.namedtuple('Line', ['n', 'content', 'params'])


def prefixed_params(params, prefix):
    """

    """
    values = {}
    for k, v in params.items():
        if not k.startswith(prefix + ':'):
            continue
        slide = int(k[len(prefix)+1:])
        values[slide] = v
    return values


# Snippet name if not specified.
DEFAULT_SNIPPET = 'DEFAULT'


def parse_params(s):
    """
    Parse parameters from a reveal comment.
    """
    snippet_name = DEFAULT_SNIPPET
    snippet_params = {}
    for part in shlex.split(s):
        if is_snippet_marker(part):
            snippet_name = part
            snippet_params.setdefault(snippet_name, {})
            continue
        kv = part.split('=', 1)
        params = snippet_params.setdefault(snippet_name, {})
        params[kv[0]] = kv[1] if len(kv) == 2 else True
    return snippet_params


def is_snippet_marker(s):
    """
    Returns whether a word is a snippet token.
    """
    return s.upper() == s


class Source:
    """
    Source represents reveal-annoted source code.
    """

    def __init__(self, lines):
        self.lines = lines

    @property
    def code(self):
        """
        The original source code without reveal comments.
        """
        c = ''
        for l in self.lines:
            c += l.content + '\n'
        return c

    def snippet_names(self):
        """
        All snippet names which occur in the source code.
        """
        names = set()
        for line in self.lines:
            names.update(line.params.keys())
        return names

    @classmethod
    def parse(cls, src):
        """
        Parse source code with reveal comments.
        """
        lines = src.splitlines()
        directive_pattern = r'^(.*?)\s*//r\s+(.*)$'
        result = []
        for i, line in enumerate(lines):
            match = re.match(directive_pattern, line)

            if match:
                p = parse_params(match.group(2))
                l = Line(n=i+1, content=match.group(1), params=p)
            else:
                l = Line(n=i+1, content=line, params={})

            result.append(l)

        # apply defaults
        for line in result:
            line.params.setdefault(DEFAULT_SNIPPET, dict())

        snippet_names = set()
        for line in result:
            for snippet_name, snippet_params in line.params.items():
                snippet_names.add(snippet_name)
                snippet_params.setdefault('skip', False)
                snippet_params.setdefault('stage', 1)

        for line in result:
            for snippet_name in snippet_names:
                line.params.setdefault(snippet_name, dict(skip=True))

        return cls(lines=result)


def format_line(line, params):
    """
    Format a line of source code according to parameters.
    """
    slide = params['stage']
    content = line.replace('\t', ' '*4)
    line = '\\uncover<{slide}>{{{content}'.format(
        slide=slide,
        content=content,
    )

    inline_comments = prefixed_params(params, 'inline')
    for slide, content in inline_comments.items():
        line += '\\only<{slide}>{{\\revealinlinecomment{{{content}}}}}'.format(
            slide=slide, content=content)

    line += '}'
    return line


def build_formatter(args):
    """
    Construct the formatter according to provided arguments.
    """
    return LatexFormatter(style=args.style)


def command_generate(args):
    filename = args.input.name
    output_template = args.output_template or filename + "-SNIPPET.tex"
    lexer = get_lexer_by_name(
        args.lexer) if args.lexer else get_lexer_for_filename(filename)
    src = args.input.read()

    s = Source.parse(src)

    formatter = build_formatter(args)
    highlighted = highlight(s.code, lexer, formatter)
    lines = highlighted.splitlines()

    for snippet_name in s.snippet_names():
        texlines = ['\\begin{semiverbatim}']
        for line, orig in zip(lines[1:-1], s.lines):
            params = orig.params.get(snippet_name, {})
            if params.get('skip'):
                continue
            if 'insert' in params:
                texlines.append(
                    '\\uncover<1>{        ' + params['insert'] + '}')
            texlines.append(format_line(line, params))
        texlines.append('\\end{semiverbatim}')

        output = '\n'.join(texlines) + '\n'
        output_filename = output_template.replace(
            "SNIPPET", snippet_name.lower())
        with open(output_filename, 'w') as f:
            f.write(output)


def command_style(args):
    formatter = build_formatter(args)
    defs = formatter.get_style_defs()
    args.output.write(defs)


def main():
    parser = argparse.ArgumentParser(description='Reveal Source Code')
    subparsers = parser.add_subparsers()

    parser.add_argument(
        '--style', default='default', help='style name')

    # Generate slide for a file.
    parser_generate = subparsers.add_parser(
        "generate", help="generate highlighted source code")
    parser_generate.add_argument('--lexer', help='lexer type')
    parser_generate.add_argument(
        '--input', type=argparse.FileType('r'), default=sys.stdin, help='input file')
    parser_generate.add_argument(
        '--output-template', help='output filename template (use SNIPPET for snippet name)')
    parser_generate.set_defaults(action=command_generate)

    # Generate style macros.
    parser_style = subparsers.add_parser(
        "style", help="output style macros")
    parser_style.add_argument(
        '--output', type=argparse.FileType('w'), default=sys.stdout, help='output file')
    parser_style.set_defaults(action=command_style)

    # Execute.
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()
    args.action(args)


if __name__ == '__main__':
    main()
