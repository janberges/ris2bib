#!/usr/bin/env python3

from ris2bib import __version__

import re
import sys

def bbl2tex(s):
    arg = r' *(<#\d+>|\d| \S)'

    for s in re.findall(r'\\BibitemOpen(.+?)\\BibitemShut', s, re.DOTALL)[1:]:
        s = re.sub(r'\n', r' ', s)
        s = re.sub(r'  +', r' ', s)

        groups = []

        while '{' in s:
            for group in re.findall(r'\{[^{]*?\}', s):
                groups.append(group[1:-1])

                replacement = '<#%d>' % len(groups)
                s = s.replace(group, replacement)

        groups.append(s)

        for n, group in enumerate(groups):
            groups[n] = re.sub(r'\\bibf?namefont' + arg, r'\1', groups[n])
            groups[n] = re.sub(r'\\bib(info|field)' + 2 * arg, r'\3', groups[n])
            groups[n] = re.sub(r'\\(Eprint|href)' + 2 * arg, r'\\href{\2}{\3}',
                groups[n])
            groups[n] = re.sub(r'\\(emph|textbf|textsc)' + arg, r'\\\1{\2}',
                groups[n])
            groups[n] = re.sub(r'\\natexlab' + arg, '', groups[n])

        s = groups[-1]

        for n, group in reversed(list(enumerate(groups, 1))):
            s = s.replace('<#%d>' % n, group)

        s = re.sub(r'\\ ', r' ', s)

        yield s

def main():
    bbl, tex = sys.argv[1:]

    with open(bbl) as infile:
        s = infile.read()

    outfile = open(tex, 'w')
    outfile.write(r'''\documentclass{article}
\usepackage[colorlinks]{hyperref}
\begin{document}
\begin{itemize}
''')

    for s in bbl2tex(s):
        outfile.write('    \\item %s\n' % s.strip())

    outfile.write(r'''\end{itemize}
\end{document}''')
    outfile.close()

if __name__ == '__main__':
    main()
