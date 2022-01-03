#!/usr/bin/env python3

import re
import sys

bbl, html = sys.argv[1:]

with open(bbl) as infile:
    s = infile.read()

arg = r' *(<#\d+>|\d| \S)'

outfile = open(html, 'w')
outfile.write('''<!DOCTYPE html>
<html>
<body>
<ul>
''')

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
        groups[n] = re.sub(r'\\(Eprint|href)' + 2 * arg, r'<a href="\2">\3</a>', groups[n])
        groups[n] = re.sub(r'\\emph' + arg, r'<em>\1</em>', groups[n])
        groups[n] = re.sub(r'\\textbf' + arg, r'<b>\1</b>', groups[n])
        groups[n] = re.sub(r'\\textsubscript(\d)', r'&#x208\1;', groups[n])
        groups[n] = re.sub(r'\\textsubscript' + arg, r'<sub>\1</sub>', groups[n])

    s = groups[-1]

    for n, group in reversed(list(enumerate(groups, 1))):
        s = s.replace('<#%d>' % n, group)

    s = re.sub(r'--', r'&ndash;', s)
    s = re.sub(r'~', r'&nbsp;', s)
    s = re.sub(r'\\ ', r' ', s)
    s = re.sub(r'\\"([aeiou])', r'&\1uml;', s)

    outfile.write('<li> %s\n' % s.strip())

outfile.write('''</ul>
</body>
</html>
''')
outfile.close()
