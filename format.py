#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys

if len(sys.argv) != 2:
    print("Usage: format.py <input file> > <output file>")
    quit()

def simplify(name):
    for a, b in zip('áäéíóöøúüñçç’–—ß', list("aaeiooouunc'--") + ['ss']):
        name = name.replace(a, b)

    return name

names = [
    'Born',
    'Coulomb',
    'Eliashberg',
    'Fermi',
    'Fröhlich',
    'Gauss',
    'Haeckel',
    'Hubbard',
    'Jahn',
    'Kohn',
    'Migdal',
    'Mott',
    'Oppenheimer',
    'Peierls',
    'Raman',
    'Stark',
    'Teller',
    'Van',
    'Waals',
    'Wannier',
    'Wick',
    'Wigner',
    ]

def protected(token, previous=None):
    upper = re.search('[A-Z]', token)

    if upper:
        # e.g. "NaCl", "W90":

        if len(re.findall('[A-Z0-9]', token)) > 1:
            return True

        # e.g. "eV":

        lower = re.search('[a-z]')

        if lower and lower.start() < upper.start():
            return True

        # e.g. "Gaussian"

        for name in names:
            if token.beginswith(name):
                return True

        # Start of further title:

        if previous and re.search('.', previous):
                return True

    return False

def protect(s, capitalization=False):
    if capitalization:
        groups = []

        while '{' in s or '$' in s:
            for group in re.findall(r'\{[^{]*?\}|\$.+?\$', s):
                s = s.replace(group, '<#%d>' % len(groups))
                groups.append(group)

        separator = ' \\-\u2013\u2014.:/'

        tokens = re.findall('[{0}]+|[^{0}]+'.format(separator), s)

        for n, token in enumerate(tokens):
            if protected(token, tokens[n - 1] if n > 0 else None):
                tokens[n] = '{%s}' % token

        s = ''.join(tokens)

        for n, group in reversed(list(enumerate(groups))):
            s = s.replace('<#%d>' % n, group)

    s = re.sub('([\u2070-\u207f]+)', r'\\textsuperscript{\1}', s)
    s = re.sub('([\u2080-\u209f]+)', r'\\textsubscript{\1}', s)

    s = re.sub('\u2080', r'', s)

    s = s.replace('²', '2')
    s = s.replace('³', '3')
    s = s.replace('¹', '1')
    s = s.replace('ß', r'{\ss}')
    s = s.replace('á', r"\'a")
    s = s.replace('ä', r'\"a')
    s = s.replace('ç', r'\c{c}')
    s = s.replace('é', r"\'e")
    s = s.replace('í', r"\'i")
    s = s.replace('ñ', r'\~n')
    s = s.replace('ó', r"\'o")
    s = s.replace('ö', r'\"o')
    s = s.replace('ø', r'{\o}')
    s = s.replace('ú', r"\'u")
    s = s.replace('ü', r'\"u')
    s = s.replace('–', '--')
    s = s.replace('—', '---')
    s = s.replace('’', "'")
    s = s.replace('⁰', '0')
    s = s.replace('ⁱ', 'i')
    s = s.replace('⁴', '4')
    s = s.replace('⁵', '5')
    s = s.replace('⁶', '6')
    s = s.replace('⁷', '7')
    s = s.replace('⁸', '8')
    s = s.replace('⁹', '9')
    s = s.replace('⁺', '+')
    s = s.replace('⁻', '$-$')
    s = s.replace('⁼', '=')
    s = s.replace('⁽', '(')
    s = s.replace('⁾', ')')
    s = s.replace('ⁿ', 'n')
    s = s.replace('₀', '0')
    s = s.replace('₁', '1')
    s = s.replace('₂', '2')
    s = s.replace('₃', '3')
    s = s.replace('₄', '4')
    s = s.replace('₅', '5')
    s = s.replace('₆', '6')
    s = s.replace('₇', '7')
    s = s.replace('₈', '8')
    s = s.replace('₉', '9')
    s = s.replace('₊', '+')
    s = s.replace('₋', '$-$')
    s = s.replace('₌', '=')
    s = s.replace('₍', '(')
    s = s.replace('₎', ')')
    s = s.replace('ₐ', 'a')
    s = s.replace('ₑ', 'e')
    s = s.replace('ₒ', 'o')
    s = s.replace('ₓ', 'x')
    s = s.replace('ₔ', 'e')
    s = s.replace('ₕ', 'h')
    s = s.replace('ₖ', 'k')
    s = s.replace('ₗ', 'l')
    s = s.replace('ₘ', 'm')
    s = s.replace('ₙ', 'n')
    s = s.replace('ₚ', 'p')
    s = s.replace('ₛ', 's')
    s = s.replace('ₜ', 't')

    return s

entries = []

with open(sys.argv[1]) as infile:
    text = infile.read()

    for block in text.split('\n\n'):
        entry = dict()

        for line in block.split('\n'):
            parts = line.split('  - ', 1)

            if len(parts) == 2:
                key, value = parts
            else:
                continue

            if key == 'TY':
                if value == 'JOUR':
                    entry['TY'] = 'article'

                elif value == 'BOOK':
                    entry['TY'] = 'book'

                elif value == 'ELEC':
                    entry['TY'] = 'electronic'

                elif value == 'CHAP':
                    entry['TY'] = 'incollection'

            if key in {'AU', 'A2'}:
                if key in entry:
                    entry[key].append(protect(value))

                else:
                    entry[key] = [protect(value)]

                    if key == 'AU':
                        entry['A1'] = value.split(',', 1)[0]
                        entry['A1'] = simplify(entry['A1'])
                        entry['A1'] = ''.join([c for c in entry['A1']
                            if 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122])

            elif key in [
                'CY',
                'DO',
                'ET',
                'J2',
                'L1',
                'PB',
                'PY',
                'SP',
                'T2',
                'TI',
                'UR',
                'VL',
                'Y2',
                ]:

                entry[key] = protect(value, capitalization=key == 'TI')

        if entry:
            if 'J2' not in entry and 'T2' in entry:
                entry['J2'] = entry.pop('T2')

            if 'J2' in entry and entry['J2'].startswith('arXiv'):
                entry['TY'] = 'unpublished'
                entry['AP'] = 'arXiv'
                entry['AR'] = entry.pop('J2').split()[0].split(':')[1]

            elif 'L1' in entry and 'arxiv' in entry['L1'].lower():
                entry['AP'] = 'arXiv'
                entry['AR'] = entry.pop('L1').split('/')[-1].replace('.pdf', '')

            for key in 'AU', 'A2':
                if key in entry:
                    entry[key] = ' and '.join(entry[key])

            entry['ID'] = entry['A1'] + entry['PY']

            entries.append(entry)

types = dict(
    article = [
        ('author',  'AU'),
        ('title',   'TI'),
        ('journal', 'J2'),
        ('volume',  'VL'),
        ('pages',   'SP'),
        ('year',    'PY'),
        ('doi',     'DO'),
        ],
    unpublished = [
        ('author', 'AU'),
        ('title',  'TI'),
        ('year',   'PY'),
        ],
    book = [
        ('author',    'AU'),
        ('title',     'TI'),
        ('edition',   'ET'),
        ('publisher', 'PB'),
        ('address',   'CY'),
        ('year',      'PY'),
        ('doi',       'DO'),
        ],
    electronic = [
        ('author',  'AU'),
        ('title',   'TI'),
        ('url',     'UR'),
        ('urldate', 'Y2'),
        ],
    incollection = [
        ('author',    'AU'),
        ('title',     'TI'),
        ('editor',    'A2'),
        ('booktitle', 'J2'),
        ('edition',   'ET'),
        ('publisher', 'PB'),
        ('address',   'CY'),
        ('year',      'PY'),
        ('doi',       'DO'),
        ]
    )

for value in types.values():
    value.extend([
        ('archiveprefix', 'AP'),
        ('eprint',        'AR'),
        ])

def parseInt(string):
    number = ''.join(c for c in string if 48 <= ord(c) <= 57)

    if number:
        return int(number)
    else:
        return 0

entries = sorted(entries, key=lambda entry: (
    parseInt(entry['PY']),
    entry['ID'],
    entry.get('J2', ''),
    parseInt(entry.get('VL', '')),
    parseInt(entry.get('SP', '')),
    entry.get('TI', ''),
    ))

labels = 'abcdefghijklmnopqrstuvwxyz'

n = 0
while n < len(entries):
    n0 = n
    while n < len(entries) and entries[n]['ID'] == entries[n0]['ID']:
        n += 1

    if len(entries[n0:n]) > 1:
        for label, entry in zip(labels, entries[n0:n]):
            entry['ID'] += label

for entry in entries:
    length = max(len(name) for name, key in types[entry['TY']] if key in entry)
    form = "%%%ds = {%%s}," % length

    print("@%s{%s," % (entry['TY'], entry['ID']))

    for name, key in types[entry['TY']]:
        if key in entry:
            print(form % (name, entry[key]))

    print("}")
