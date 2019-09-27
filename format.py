#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

if len(sys.argv) != 2:
    print("Usage: format.py <input file> > <output file>")
    quit()

def simplify(name):
    for a, b in zip('áäéíóöúÜ', 'aaeioouu'):
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

            if key == 'AU':
                if 'AU' in entry:
                    entry['AU'].append(value)

                else:
                    entry['AU'] = [value]
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
                'VL',
                ]:

                entry[key] = value

        if entry:
            if 'J2' not in entry and 'T2' in entry:
                entry['J2'] = entry.pop('T2')

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
    book = [
        ('author',    'AU'),
        ('title',     'TI'),
        ('edition',   'ET'),
        ('publisher', 'PB'),
        ('address',   'CY'),
        ('year',      'PY'),
        ('doi',       'DO'),
        ],
    )

entries = sorted(entries, key=lambda entry:
    (int(entry['PY']), entry['AU'], entry['TI']))

for entry in entries:
    length = max(len(name) for name, key in types[entry['TY']] if key in entry)
    form = "%%%ds = {%%s}," % length

    print("@%s{%s," % (entry['TY'], entry['ID']))

    for name, key in types[entry['TY']]:
        if key in entry:
            print(form % (name, entry[key]))

    print("}")
