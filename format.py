#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if len(sys.argv) != 2:
    print("Usage: format.py <input file> > <output file>")
    quit()

def simplify(name):
    for a, b in zip('áäéíóöøúüñçç’–—ß', list("aaeiooouunc'--") + ['ss']):
        name = name.replace(a, b)

    return name

def protect(name):
    for a, b in zip('áäéíóöøúüñç’–—ß', [
        r"\'a",
        r'\"a',
        r"\'e",
        r"\'i",
        r"\'o",
        r'\"o',
        r'\o',
        r"\'u",
        r'\"u',
        r'\~n',
        r'\c{c}',
        "'",
        '--',
        '---',
        r'\ss',
        ]):

        name = name.replace(a, b)

    return name

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

            if key == 'AU':
                if 'AU' in entry:
                    entry['AU'].append(protect(value))

                else:
                    entry['AU'] = [protect(value)]
                    entry['A1'] = value.split(',', 1)[0]
                    entry['A1'] = simplify(entry['A1'])
                    entry['A1'] = ''.join([c for c in entry['A1']
                        if 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122])

            elif key in [
                'CY',
                'DO',
                'ET',
                'J2',
                'PB',
                'PY',
                'SP',
                'T2',
                'TI',
                'UR',
                'VL',
                'Y2',
                ]:

                entry[key] = protect(value)

        if entry:
            if 'J2' not in entry and 'T2' in entry:
                entry['J2'] = entry.pop('T2')

            if 'J2' in entry and entry['J2'].startswith('arXiv'):
                entry['TY'] = 'unpublished'
                entry['AP'] = 'arXiv'
                entry['AR'] = entry.pop('J2')[6:]

            entry['AU'] = ' and '.join(entry['AU'])
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
        ('author',        'AU'),
        ('title',         'TI'),
        ('year',          'PY'),
        ('archiveprefix', 'AP'),
        ('eprint',        'AR'),
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
    )

entries = sorted(entries, key=lambda entry:
    (int(entry['PY']), entry['ID'], entry['TI']))

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
