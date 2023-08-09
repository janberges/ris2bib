#!/usr/bin/env python3

import re
import sys

bbl, html = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

citekeys = '--citekeys' in sys.argv[1:]

with open(bbl) as infile:
    s = infile.read()

arg = r' *(<#\d+>|\d| \S)'
noarg = ' *({})?'

outfile = open(html, 'w')
outfile.write('''<!DOCTYPE html>
<html>
<body>
<ul%s>
''' % (" id='bibliography'" * citekeys))

for key, s in re.findall(r'\{([^{}]*?)\}[^{}]*?'
    r'\\BibitemOpen(.+?)\\BibitemShut', s, re.DOTALL)[1:]:

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
        groups[n] = re.sub(r'\\natexlab' + arg, '', groups[n])
        groups[n] = re.sub(r'\\textbf' + arg, r'<b>\1</b>', groups[n])
        groups[n] = re.sub(r'\\textsubscript(\d)', r'&#x208\1;', groups[n])
        groups[n] = re.sub(r'\\textsubscript' + arg, r'<sub>\1</sub>', groups[n])

    s = groups[-1]

    for n, group in reversed(list(enumerate(groups, 1))):
        s = s.replace('<#%d>' % n, group)

    s = re.sub(r'--', r'&ndash;', s)
    s = re.sub(r'~', r'&nbsp;', s)
    s = re.sub(r'\\ ', r' ', s)
    s = re.sub(r"\\'([aeiou])", r'&\1acute;', s, flags=re.I)
    s = re.sub(r'\\"([aeiou])', r'&\1uml;', s, flags=re.I)
    s = re.sub(r'\\allowbreak' + noarg, r'&#x200B;', s)

    if citekeys:
        outfile.write("<li id='%s'> %s\n" % (key, s.strip()))
    else:
        outfile.write('<li> %s\n' % s.strip())

outfile.write('</ul>')

if citekeys:
    outfile.write('''
<script>
    const links = document.getElementsByTagName('a')
    const bib = document.getElementById('bibliography')
    const refs = Array.from(bib.children)
    for (let i = 0; i < links.length; i++) {
        let href = links[i].getAttribute('href')
        if (href && href.startsWith('#')) {
            let ref = document.getElementById(href.substring(1))
            if (ref && bib.contains(ref)) {
                links[i].innerText = refs.indexOf(ref) + 1
            }
        }
    }
</script>''')

outfile.write('''
</body>
</html>
''')

outfile.close()
