#!/usr/bin/env python3

from ris2bib import __version__

import re
import sys

def bbl2html(s):
    arg = r' *(<#\d+>|\d| \S)'
    noarg = ' *({})?'

    for key, s in re.findall(r'\{([^{}]*?)\}[^{}]*?'
        r'\\BibitemOpen(.+?)\\BibitemShut', s, re.DOTALL)[1:]:

        s = re.sub(r'\n', r' ', s)
        s = re.sub(r'  +', r' ', s)
        s = re.sub(r"(?<=\w)'", r'&rsquo;', s)

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
            groups[n] = re.sub(r'\\(Eprint|href)' + 2 * arg,
                r"<a href='\2'>\3</a>", groups[n])
            groups[n] = re.sub(r'\\emph' + arg, r'<em>\1</em>', groups[n])
            groups[n] = re.sub(r'\\natexlab' + arg, '', groups[n])
            groups[n] = re.sub(r'\\textbf' + arg, r'<b>\1</b>', groups[n])
            groups[n] = re.sub(r'\\textsc' + arg, r"<span style='font-variant: "
                r"small-caps'>\1</span>", groups[n])
            groups[n] = re.sub(r'\\textsubscript(\d)', r'&#x208\1;', groups[n])
            groups[n] = re.sub(r'\\textsubscript' + arg, r'<sub>\1</sub>',
                groups[n])
            groups[n] = re.sub(r'\\allowbreak' + noarg, r'&#x200B;', groups[n])
            groups[n] = re.sub(r'\\@' + noarg, r'', groups[n])

        s = groups[-1]

        for n, group in reversed(list(enumerate(groups, 1))):
            s = s.replace('<#%d>' % n, group)

        s = re.sub(r'--', r'&ndash;', s)
        s = re.sub(r'~', r'&nbsp;', s)
        s = re.sub(r'\\ ', r' ', s)
        s = re.sub(r"\\'([aeiou])", r'&\1acute;', s, flags=re.I)
        s = re.sub(r'\\"([aeiou])', r'&\1uml;', s, flags=re.I)

        yield (key, s)

def main():
    bbl, html = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    citekeys = '--citekeys' in sys.argv[1:]

    with open(bbl) as infile:
        s = infile.read()

    outfile = open(html, 'w')
    outfile.write('''<!DOCTYPE html>
<html>
<body>
<%s>
''' % ("ol id='bibliography'" if citekeys else 'ul'))

    for key, s in bbl2html(s):
        if citekeys:
            outfile.write("<li id='%s'> %s\n" % (key, s.strip()))
        else:
            outfile.write('<li> %s\n' % s.strip())

    if citekeys:
        outfile.write('''</ol>
<script>
    const links = document.getElementsByTagName('a')
    const bib = document.getElementById('bibliography')
    const refs = new Array()
    for (let i = 0; i < links.length; i++) {
        let href = links[i].getAttribute('href')
        if (href && href.startsWith('#')) {
            let ref = document.getElementById(href.substring(1))
            if (ref && bib.contains(ref)) {
                links[i].innerText = refs.indexOf(ref) + 1 || refs.push(ref)
            }
        }
    }
    if (refs.length) bib.replaceChildren(...refs)
</script>''')
    else:
        outfile.write('</ul>')

    outfile.write('''
</body>
</html>
''')

    outfile.close()

if __name__ == '__main__':
    main()
