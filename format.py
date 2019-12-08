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
        r'{\o}',
        r"\'u",
        r'\"u',
        r'\~n',
        r'\c{c}',
        "'",
        '--',
        '---',
        r'{\ss}',
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

                entry[key] = protect(value)

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
