#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r"""
Overview
________

This scripts converts bibliographies from RIS to BibTeX format, preserving only
relevant information. The RIS input file can be generated, for example, using
Zotero's "Quick Copy" feature (Edit > Preferences > Export). It may contain
certain Unicode characters, e.g., subscript numbers. The BibTeX output file
ought to contain ASCII characters only. Uppercase letters in acronyms, chemical
formulas, and common physicist's names are protected by automatic insertion of
curly braces.

Usage
_____

format.py <input file> <output file>
          [--sub=<format string>] [--super=<format string>]

The optional arguments --sub and --super specify the markup used to convert
sub- and superscript Unicode sequences in titles to LaTeX code. The default
values are --sub='\textsubscript{X}' and --super='\textsuperscript{X}', where X
is the placeholder for the replaced sequence. Possible alternative values are
--sub='$_{X}$' and --super='$^{X}$'.
"""

import re
import sys

# Read input (.ris) and output (.bib) file given as command-line arguments:

try:
    ris, bib = [argument for argument in sys.argv[1:]
        if not argument.startswith('-')]
except:
    raise SystemExit("Wrong arguments. Check source code for documentation.")

# Read optional command-line arguments:

sup = r'\textsuperscript{X}'
sub = r'\textsubscript{X}'

for argument in sys.argv[1:]:
    if argument.startswith('-') and '=' in argument:
        key, value = argument.split('=')

        if key == '--sub':
            print('Subscript format: %s' % value)
            sub = value

        elif key == '--super':
            print('Superscript format: %s' % value)
            sup = value

    else:
        print('Unknown argument: %s' % argument)

sup = sup.replace('\\', '\\\\').replace('X', '\\1')
sub = sub.replace('\\', '\\\\').replace('X', '\\1')

# Data for text replacements:

accents = {
    '\u00df': r'{\ss}',
    '\u00e1': r"\'a",
    '\u00e4': r'\"a',
    '\u00e7': r'\c{c}',
    '\u00e9': r"\'e",
    '\u00ed': r"\'i",
    '\u00f1': r'\~n',
    '\u00f3': r"\'o",
    '\u00f6': r'\"o',
    '\u00f8': r'{\o}',
    '\u00fa': r"\'u",
    '\u00fc': r'\"u',
    '\u2009': '\,',
    '\u2013': '--',
    '\u2014': '---',
    '\u2018': "`",
    '\u2019': "'",
    '\u201c': "``",
    '\u201d': "''",
    }

simplifications = {
    key: value.replace('}', '')[-1]
    for key, value in accents.items()
    }

superscripts = {
    '\u00b2': '2',
    '\u00b3': '3',
    '\u00b9': '1',
    '\u2070': '0',
    '\u2071': 'i',
    '\u2074': '4',
    '\u2075': '5',
    '\u2076': '6',
    '\u2077': '7',
    '\u2078': '8',
    '\u2079': '9',
    '\u207a': '+',
    '\u207b': r'\ensuremath-',
    '\u207c': '=',
    '\u207d': '(',
    '\u207e': ')',
    '\u207f': 'n',
    }

superscripts_any = ''.join(superscripts.keys())
superscripts_range = '([{0}]+)'.format(superscripts_any)

subscripts = {
    '\u2080': '0',
    '\u2081': '1',
    '\u2082': '2',
    '\u2083': '3',
    '\u2084': '4',
    '\u2085': '5',
    '\u2086': '6',
    '\u2087': '7',
    '\u2088': '8',
    '\u2089': '9',
    '\u208a': '+',
    '\u208b': r'\ensuremath-',
    '\u208c': '=',
    '\u208d': '(',
    '\u208e': ')',
    '\u2090': 'a',
    '\u2091': 'e',
    '\u2092': 'o',
    '\u2093': 'x',
    '\u2094': '.', # misuse of subscript schwa (see subscripts_point)
    '\u2095': 'h',
    '\u2096': 'k',
    '\u2097': 'l',
    '\u2098': 'm',
    '\u2099': 'n',
    '\u209a': 'p',
    '\u209b': 's',
    '\u209c': 't',
    }

subscripts_any = ''.join(subscripts.keys())
subscripts_range = '([{0}]+)'.format(subscripts_any)
subscripts_point = '([{0}])\.([{0}])'.format(subscripts_any)

greeks = {
    '\u0393': r'\Gamma',
    '\u0394': r'\Delta',
    '\u0398': r'\Theta',
    '\u039b': r'\Lambda',
    '\u039e': r'\Xi',
    '\u03a0': r'\Pi',
    '\u03a3': r'\Sigma',
    '\u03a5': r'\Upsilon',
    '\u03a6': r'\Phi',
    '\u03a8': r'\Psi',
    '\u03a9': r'\Omega',
    '\u03b1': r'\alpha',
    '\u03b2': r'\beta',
    '\u03b3': r'\gamma',
    '\u03b4': r'\delta',
    '\u03b5': r'\varepsilon',
    '\u03b6': r'\zeta',
    '\u03b7': r'\eta',
    '\u03b8': r'\theta',
    '\u03b9': r'\iota',
    '\u03ba': r'\kappa',
    '\u03bb': r'\lambda',
    '\u03bc': r'\mu',
    '\u03bd': r'\nu',
    '\u03be': r'\xi',
    '\u03c0': r'\pi',
    '\u03c1': r'\rho',
    '\u03c2': r'\varsigma',
    '\u03c3': r'\sigma',
    '\u03c4': r'\tau',
    '\u03c5': r'\upsilon',
    '\u03c6': r'\varphi',
    '\u03c7': r'\chi',
    '\u03c8': r'\psi',
    '\u03c9': r'\omega',
    '\u03d1': r'\vartheta',
    '\u03d5': r'\phi',
    '\u03d6': r'\varpi',
    '\u03f1': r'\varrho',
    '\u03f5': r'\epsilon',
    }

greeks_any = ''.join(greeks.keys())
greeks_range = '([{0}]+)'.format(greeks_any)

names = [
    'Born',
    'Coulomb',
    'Dirac',
    'Eliashberg',
    'Fermi',
    'Fröhlich',
    'Gauss',
    'Haeckel',
    'Hubbard',
    'Jahn',
    'Kasuya',
    'Kittel',
    'Kohn',
    'Matsubara',
    'Migdal',
    'Mott',
    'Oppenheimer',
    'Padé',
    'Peierls',
    'Raman',
    'Ruderman',
    'Stark',
    'Teller',
    'Van',
    'Waals',
    'Wannier',
    'Wick',
    'Wigner',
    'Yosida',
    ]

elements = [
    'H',  'He', 'Li', 'Be', 'B',  'C',  'N',  'O',  'F',  'Ne', 'Na', 'Mg',
    'Al', 'Si', 'P',  'S',  'Cl', 'Ar', 'K',  'Ca', 'Sc', 'Ti', 'V',  'Cr',
    'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br', 'Kr',
    'Rb', 'Sr', 'Y',  'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd',
    'In', 'Sn', 'Sb', 'Te', 'I',  'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr', 'Nd',
    'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf',
    'Ta', 'W',  'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi', 'Po',
    'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U',  'Np', 'Pu', 'Am', 'Cm',
    'Bk', 'Cf', 'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 'Bh', 'Hs',
    'Mt', 'Ds', 'Rg', 'Cn', 'Nh', 'Fl', 'Mc', 'Lv', 'Ts', 'Og',
    ]

# Considered entry types:

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

search_keys = set(ris_key
    for value in types.values()
    for bib_key, ris_key in value)

# Long journal name (T2) and link to PDF (L1) are read complementarily:

search_keys |= {'T2', 'L1'}

# Simplify author names for reference identifier:

def simplify(name):
    for a, b in simplifications.items():
        name = name.replace(a, b)

    return name

# Check if case of token/word must be protected using curly braces:

def fragile(token, previous=None):
    upper = re.search('[A-Z]', token)

    if upper:
        # Token contains at least two uppercase characters or one uppercase
        # character and a number, e.g., "NaCl" or "W90":

        if len(re.findall('[A-Z0-9]', token)) > 1:
            return True

        # Token contains an uppercase character following a lowercase character,
        # e.g., "eV":

        lower = re.search('[a-z]', token)

        if lower and lower.start() < upper.start():
            return True

        # Token starts with an uppercase letter that must be protected
        # (unnecessary at the beginning of the entry):

        if previous is None:
            return False

        # Token is a single uppercase letter (except "A"), e.g., "T":

        if len(token) == 1 and token != 'A':
            return True

        # Token stars with/derives from famous name, e.g., "Gaussian":

        for name in names:
            if token.startswith(name):
                return True

        # Literal part of token is symbol for chemical element, e.g., "Li":

        letters = ''.join(re.findall('[a-zA-Z]+', token))

        for element in elements:
            if letters == element:
                return True

        # Token follows on period:

        if re.search('\.', previous):
                return True

    return False

def protect(s):
    s = re.sub(subscripts_point, r'\1ₔ\2', s)

    print('%s...' % s[:50])

    groups = []

    while '{' in s:
        for group in re.findall(r'\{[^{]*?\}', s):
            groups.append(group)

            replacement = '<#%d>' % len(groups)
            s = s.replace(group, replacement)

            print('Group: %s = %s' % (replacement, group))

    for group in re.findall(r'\$.+?\$', s):
        if re.search('[A-Z]', group):
            group = '{%s}' % group

        groups.append(group)

        replacement = '<#%d>' % len(groups)
        s = s.replace(group, replacement)

        print('Math: %s = %s' % (replacement, group))

    separator = ' \u2009\\-\u2013\u2014.:,;()\[\]/'

    tokens = re.findall('[{0}]+|[^{0}]+'.format(separator), s)

    for n, token in enumerate(tokens):
        if fragile(token, tokens[n - 1] if n > 0 else None):
            tokens[n] = '{%s}' % token

            print('Protect: %s' % token)

    s = ''.join(tokens)

    for n, group in reversed(list(enumerate(groups, 1))):
        s = s.replace('<#%d>' % n, group)

    return s

def escape(s):
    s = re.sub(superscripts_range, sup, s)
    s = re.sub(  subscripts_range, sub, s)

    for key, value in superscripts.items():
        s = s.replace(key, value)

    for key, value in subscripts.items():
        s = s.replace(key, value)

    for key, value in accents.items():
        s = s.replace(key, value)

    s = re.sub(greeks_range, r'$\1$', s)

    for key, value in greeks.items():
        s = s.replace(key, value)

    s = re.sub(r'\{(\d)\}', r'\1', s)
    s = re.sub(r'_\{(\w)\}', r'_\1', s)
    s = re.sub(r'(\$.+?\$)', lambda x: x.group().replace(r'\ensuremath', ''), s)

    return s

entries = []

with open(ris) as infile:
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

            if key in {'AU', 'A2'} and key in entry:
                    entry[key] += ' and ' + escape(value)

            elif key == 'TI':
                entry[key] = escape(protect(value))

            elif key in search_keys:
                entry[key] = escape(value)

        if entry:
            entry['ID'] = entry['AU'].split(',', 1)[0]
            entry['ID'] = simplify(entry['ID'])
            entry['ID'] = ''.join([c for c in entry['ID']
                if 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122])

            entry['ID'] += entry['PY']

            if 'J2' not in entry and 'T2' in entry:
                entry['J2'] = entry.pop('T2')

            if 'J2' in entry and entry['J2'].startswith('arXiv'):
                entry['TY'] = 'unpublished'
                entry['AP'] = 'arXiv'
                entry['AR'] = entry.pop('J2').split()[0].split(':')[1]

            elif 'L1' in entry and 'arxiv' in entry['L1'].lower():
                entry['AP'] = 'arXiv'
                entry['AR'] = entry.pop('L1').split('/')[-1].replace('.pdf', '')

            entries.append(entry)

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

            print('Sublabel: %s' % entry['ID'])

with open(bib, 'w') as outfile:
    for entry in entries:
        length = max(len(name) for name, key in types[entry['TY']] if key in entry)
        form = "%%%ds = {%%s},\n" % length

        outfile.write("@%s{%s,\n" % (entry['TY'], entry['ID']))

        for name, key in types[entry['TY']]:
            if key in entry:
                outfile.write(form % (name, entry[key]))

        outfile.write("}\n")
