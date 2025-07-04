#!/usr/bin/env python3

r"""
## Overview

This scripts converts bibliographies from RIS to BibTeX format, preserving only
relevant information. The RIS input file can be generated, for example, using
Zotero's "Quick Copy" feature (Edit > Preferences > Export). It may contain
certain Unicode characters, e.g., subscript numbers. The BibTeX output file
ought to contain ASCII characters only. Uppercase letters in acronyms, chemical
formulas, and common physicist's names are protected by automatic insertion of
curly braces.

## Usage

    ris2bib.py <input file> <output file>
        [--sub=<format string>] [--super=<format string>] [--colcap=<0 or 1>]
        [--nodash=<0 or 1>] [--short-year=<0 or 1>] [--skip-a=<0 or 1>]
        [--arxiv=<0 or 1>] [--nature=<0 or 1>] [--scipost=<0 or 1>]
        [--etal=<count>]

The optional arguments `--sub` and `--super` specify the markup used to convert
sub- and superscript Unicode sequences in titles to LaTeX code. The default
values are `--sub='\textsubscript{X}'` and `--super='\textsuperscript{X}'`,
where `X` is the placeholder for the replaced sequence. Possible alternative
values are `--sub='$_{X}$'` and `--super='$^{X}$'`.

If `--colcap=1`, words following a colon, e.g., at the beginning of subtitles,
are capitalized. This is the default.

If `--nodash=1`, en dashes between words (not numbers) are replaced by simple
hyphens. The default is `--nodash=0`.

If `--short-year=1`, only the last two digits of the year are used for the
article identifier. The default is `--short-year=0`.

If `--skip-a=1`, sublabels "a" are omitted. The default is `--skip-a=0`.

If `--arxiv=1`, eprint identifiers are included even if an article has already
been published. This is the default.

If `--nature=1`, DOIs and eprint identifiers are provided via the URL entry. The
default is `--nature=0`.

If `--scipost=1`, eprints are provided with a full URL rather than an archive
prefix and identifier, and the entry type "misc" instead of "unpublished" is
used. The default is `--scipost=0`.

If a nonzero maximum number of authors is specified via `--etal`, author lists
with more authors are reduced to the first author "and others". `--etal=15` is
appropriate for APS journals. The default is `--etal=0`.
"""

__version__ = '0.1'

import re
import sys

def positional_arguments():
    """Read input (.ris) and output (.bib) file given as command arguments."""

    try:
        ris, bib = [argument for argument in sys.argv[1:]
            if not argument.startswith('-')]
    except ValueError:
        raise SystemExit(__doc__)

    return ris, bib

def keyword_arguments():
    """Read optional command-line arguments."""

    kwargs = dict()

    for argument in sys.argv[1:]:
        if argument.startswith('-') and '=' in argument:
            key, value = argument.split('=')
            if key == '--sub':
                kwargs['sub'] = value
                print('Subscript format: %(sub)s' % kwargs)

            elif key == '--super':
                kwargs['sup'] = value
                print('Superscript format: %(sup)s' % kwargs)

            elif key == '--colcap':
                kwargs['colcap'] = bool(int(value))
                print('Capitalize after colon: %(colcap)s' % kwargs)

            elif key == '--nodash':
                kwargs['nodash'] = bool(int(value))
                print('Replace en dashes by hyphens: %(nodash)s' % kwargs)

            elif key == '--short-year':
                kwargs['short_year'] = bool(int(value))
                print('Use short year in identifiers: %(short_year)s' % kwargs)

            elif key == '--skip-a':
                kwargs['skip_a'] = bool(int(value))
                print('Omit sublabel a: %(skip_a)s' % kwargs)

            elif key == '--arxiv':
                kwargs['arxiv'] = bool(int(value))
                print('Include eprint identifiers: %(arxiv)s' % kwargs)

            elif key == '--nature':
                kwargs['nature'] = bool(int(value))
                print('Nature DOI style: %(nature)s' % kwargs)

            elif key == '--scipost':
                kwargs['scipost'] = bool(int(value))
                print('SciPost eprint style: %(scipost)s' % kwargs)

            elif key == '--etal':
                kwargs['etal'] = int(value)
                print('Maximum number of listed authors: %(etal)d' % kwargs)

            else:
                print('Unknown argument: %s' % key)

    return kwargs

# Data for text replacements:

accents = {
    '\u00c1': r"\'A",
    '\u00cd': r"\'I",
    '\u00d6': r'\"{O}',
    '\u00dc': r'\"{U}',
    '\u00df': r'{\ss}',
    '\u00e0': r'\`a',
    '\u00e1': r"\'a",
    '\u00e4': r'\"a',
    '\u00e5': r'{\aa}',
    '\u00e7': r'\c{c}',
    '\u00e8': r'\`e',
    '\u00e9': r"\'e",
    '\u00ed': r"\'i",
    '\u00ef': r'\"i',
    '\u00f1': r'\~n',
    '\u00f2': r'\`o',
    '\u00f3': r"\'o",
    '\u00f4': r'\^o',
    '\u00f6': r'\"o',
    '\u00f8': r'{\o}',
    '\u00fa': r"\'u",
    '\u00fc': r'\"u',
    '\u0102': r'\u{A}',
    '\u0103': r'\u{a}',
    '\u0107': r"\'c",
    '\u010c': r'\v{C}',
    '\u010d': r'\v{c}',
    '\u0119': r'\k{e}',
    '\u011b': r'\v{e}',
    '\u011f': r'\u{g}',
    '\u012d': r'{\u\i}',
    '\u0130': r'\.I',
    '\u0131': r'{\i}',
    '\u0142': r'{\l}',
    '\u0144': r"\'n",
    '\u0148': r'\v{n}',
    '\u0150': r'\H{O}',
    '\u0151': r'\H{o}',
    '\u0158': r'\v{R}',
    '\u0159': r'\v{r}',
    '\u0159': r'\v{r}',
    '\u015b': r"\'s",
    '\u015e': r'\c{S}',
    '\u015f': r'\c{s}',
    '\u0160': r'\v{S}',
    '\u0161': r'\v{s}',
    '\u0163': r'\c{t}',
    '\u0170': r'\H{U}',
    '\u0171': r'\H{u}',
    '\u017c': r'\.c',
    '\u017e': r'\v{z}',
    '\u01e7': r'\v{g}',
    '\u2018': '`',
    '\u2019': "'",
    '\u201c': '``',
    '\u201d': "''",
}

dashes = {
    '\u2010': '-', # unbreakable
    '\u2013': '--',
    '\u2014': '---',
}

accents.update(dashes)

simplifications = {
    key: value.replace('}', '')[-1]
    for key, value in accents.items()
}

spaces = {
    '\u00a0': '~',
    '\u2009': r'\,',
}

quotes = {
    '\u00ab': r'{\guillemotleft}',
    '\u00bb': r'{\guillemotright}',
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
    '\u1d62': 'i',
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
subscripts_range = '([{0}]+([{0}.,]+[{0}])?)'.format(subscripts_any)

math = {
    '\u00d7': r'\times',
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
    '\u2032': r"'",
    '\u2033': r"''",
    '\u2202': r'\partial',
    '\u2212': r'-',
    '\u221a': r'\sqrt',
    '\u221e': r'\infty',
    '\u223c': r'\sim',
    '\u2264': r'\leq',
}

math_any = ''.join(math.keys())
math_range = r'(([{0}\d][{0}\d\sx]*)?[{0}]+([{0}\d\sx]*[{0}\d])?)'.format(
    math_any)

others = {
    '&': r'\&',
    '\u00ad': r'\-',
}

names = {
    'Bethe',
    'Born',
    'Bose',
    'Brillouin',
    'Burke',
    'Carlo',
    'Cooper',
    'Coulomb',
    'Dirac',
    'Eliashberg',
    'Ernzerhof',
    'Fermi',
    'Feynman',
    'Fock',
    'Fr\u00f6hlich',
    'Gauss',
    'Goldstone',
    'Green',
    'Haeckel',
    'Hall',
    'Hamilton',
    'Hartree',
    'Heeger',
    'Heisenberg',
    'Hove',
    'Huang',
    'Hubbard',
    'Hund',
    'Ising',
    'Jahn',
    'Kasuya',
    'Kittel',
    'Kohn',
    'Lifshitz',
    'Luttinger',
    'Matsubara',
    'Migdal',
    'Monte',
    'Mott',
    'Oppenheimer',
    'Pad\u00e9',
    'Pariser',
    'Parr',
    'Peierls',
    'Perdew',
    'Pople',
    'Python',
    'Raman',
    'Ruderman',
    'Salpeter',
    'Schrieffer',
    'Schwinger',
    'Stark',
    'Sternheimer',
    'Su',
    'Teller',
    'Tomonaga',
    'Van',
    'Vanderbilt',
    'Waals',
    'Wagner',
    'Wannier',
    'Ward',
    'Weyl',
    'Wick',
    'Wigner',
    'Yosida',
}

elements = set('''
    H                                                  He
    Li Be                               B  C  N  O  F  Ne
    Na Mg                               Al Si P  S  Cl Ar
    K  Ca Sc Ti V  Cr Mn Fe Co Ni Cu Zn Ga Ge As Se Br Kr
    Rb Sr Y  Zr Nb Mo Tc Ru Rh Pd Ag Cd In Sn Sb Te I  Xe
    Cs Ba Lu Hf Ta W  Re Os Ir Pt Au Hg Tl Pb Bi Po At Rn
    Fr Ra Lr Rf Db Sg Bh Hs Mt Ds Rg Cn Nh Fl Mc Lv Ts Og

          La Ce Pr Nd Pm Sm Eu Gd Tb Dy Ho Er Tm Yb
          Ac Th Pa U  Np Pu Am Cm Bk Cf Es Fm Md No
    '''.split())

elements -= {'Bi', 'In'}

# Considered entry types:

types = dict(
    article=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('journal', 'J2'),
        ('volume', 'VL'),
        ('pages', 'SP'),
        ('year', 'PY'),
    ],
    unpublished=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('year', 'PY'),
    ],
    book=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('edition', 'ET'),
        ('publisher', 'PB'),
        ('address', 'CY'),
        ('year', 'PY'),
    ],
    electronic=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('urldate', 'Y2'),
    ],
    incollection=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('editor', 'A2'),
        ('booktitle', 'J2'),
        ('volume', 'VL'),
        ('edition', 'ET'),
        ('publisher', 'PB'),
        ('address', 'CY'),
        ('year', 'PY'),
    ],
    phdthesis=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('type', 'M3'),
        ('school', 'PB'),
        ('year', 'PY'),
    ],
    misc=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('howpublished', 'HP'),
        ('year', 'PY'),
    ],
    techreport=[
        ('author', 'AU'),
        ('title', 'TI'),
        ('institution', 'PB'),
        ('year', 'PY'),
    ],
)

for key, value in types.items():
    value.extend([
        ('url', 'UR'),
        ('doi', 'DO'),
        ('archiveprefix', 'AP'),
        ('eprint', 'AR'),
    ])

search_keys = set(ris_key
    for value in types.values()
    for bib_key, ris_key in value)

# Date (DA) and long journal names (T2) are read complementarily:

search_keys |= {'DA', 'T2'}

def simplify(name):
    """Simplify author names for reference identifier."""

    # Remove LaTeX commands:

    name = re.sub(r'\\\w+', '', name)

    # Remove accents etc.:

    for a, b in simplifications.items():
        name = name.replace(a, b)

    # Keep only ASCII alphanumericals:

    name = ''.join([c for c in name
        if 65 <= ord(c) <= 90 or 97 <= ord(c) <= 122])

    return name

def fragile(token, previous=None):
    """Check if case of token/word must be protected using curly braces."""

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

        # The first letter after ": " is protected by BibTeX by default:

        if previous == ': ':
            return False

        # Token is a single uppercase letter (except "A"), e.g., "T":

        if len(token) == 1 and token != 'A':
            return True

        # Token stars with/derives from famous name, e.g., "Gaussian":

        for name in names:
            if token == name:
                return True
            if len(name) > 3 and token.startswith(name):
                if not re.match('i?ons?$', token[len(name):]):
                    return True

        # Literal part of token is symbol for chemical element, e.g., "Li":

        letters = ''.join(re.findall('[a-zA-Z]+', token))

        for element in elements:
            if letters == element:
                return True

        # Token follows on period:

        if re.search(r'\.', previous):
            return True

    return False

def protect(s):
    """Protect certain uppercase characters using curly braces."""

    print('%s...' % s[:50])

    # Identify groups that are already enclosed in curly braces and substitute
    # them with placeholders:

    groups = []

    while '{' in s:
        for group in re.findall(r'\{[^{]*?\}', s):
            groups.append(group)

            replacement = '<#%d>' % len(groups)
            s = s.replace(group, replacement)

            print('Group: %s = %s' % (replacement, group))

    # Also substitute inline math with placeholders and protect them if they
    # contain an uppercase letter.

    for group in re.findall(r'\$.+?\$', s):
        groups.append(group)

        replacement = '<#%d>' % len(groups)
        s = s.replace(group, replacement)

        if re.search('[A-Z]', group):
            groups[-1] = '{%s}' % group

        print('Math: %s = %s' % (replacement, group))

    # Split string into tokens:

    separator = r' \-.:,;()\[\]/' + ''.join(spaces) + ''.join(dashes)

    tokens = re.findall('[{0}]+|[^{0}]+'.format(separator), s)

    # Protect tokens where necessary:

    for n, token in enumerate(tokens):
        if fragile(token, tokens[n - 1] if n > 0 else None):
            tokens[n] = '{%s}' % token.replace('<#', '<$')

            print('Protect: %s' % token)

    # Join tokens into one string:

    s = ''.join(tokens)

    # Substitute groups and inline math back:

    for n, group in reversed(list(enumerate(groups, 1))):
        s = s.replace('<#%d>' % n, group)
        s = s.replace('<$%d>' % n, group.strip('{}'))

    return s

def escape(s, sup=r'\textsuperscript{X}', sub=r'\textsubscript{X}'):
    """Replace non-ASCII Unicode characters by LaTeX escape sequences."""

    # Add markup to ranges of certain characters:

    sup = sup.replace('\\', '\\\\').replace('X', '\\1')
    sub = sub.replace('\\', '\\\\').replace('X', '\\1')

    s = re.sub(superscripts_range, sup, s)
    s = re.sub(subscripts_range, sub, s)
    s = re.sub(math_range, r'$\1$', s)

    # Replace certain Unicode characters by LaTeX commands:

    for key, value in accents.items():
        s = s.replace(key, value)

    for key, value in spaces.items():
        s = s.replace(key, value)

    for key, value in quotes.items():
        s = s.replace(key, value)

    for key, value in superscripts.items():
        s = s.replace(key, value)

    for key, value in subscripts.items():
        s = s.replace(key, value)

    for key, value in math.items():
        s = s.replace(key, value)

    for key, value in others.items():
        s = s.replace(key, value)

    # Remove unnecessary curly braces and commands:

    s = re.sub(r'\{(\d)\}', r'\1', s)
    s = re.sub(r'_\{(\w)\}', r'_\1', s)
    s = re.sub(r'(\$.+?\$)', lambda x: x.group().replace(r'\ensuremath', ''), s)

    # Avoid line breaks at equals signs:

    s = re.sub(' = ', '~=~', s)

    # Remove redundant spaces:

    s = re.sub('  +', ' ', s)

    return s

def parseInt(string):
    """Parse string as integer, ignoring all non-numbers."""

    number = ''.join(c for c in string if 48 <= ord(c) <= 57)

    if number:
        return int(number)
    else:
        return 0

def read(ris, sup=r'\textsuperscript{X}', sub=r'\textsubscript{X}',
        colcap=True, nodash=False, short_year=False, skip_a=False, arxiv=True,
        nature=False, scipost=False, etal=0):
    """Read RIS input file."""

    entries = []

    with open(ris) as infile:
        text = infile.read()

        for block in re.split(r'\nER\s*-\s*', text):
            entry = dict()

            for line in re.split(r'\n', block):
                parts = re.split(r'\s*-\s*', line, maxsplit=1)

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

                    if value == 'THES':
                        entry['TY'] = 'phdthesis'

                    elif value == 'COMP':
                        entry['TY'] = 'misc'

                    elif value == 'RPRT':
                        entry['TY'] = 'techreport'

                if key in {'AU', 'A2'} and key in entry:
                    entry[key] += ' and ' + value

                elif key == 'UR' or re.match(r'L\d', key):
                    if key == 'UR':
                        entry[key] = value

                    # Try to extract arXiv identifier or DOI from links:

                    if 'AR' not in entry and 'arxiv' in value.lower():
                        entry['AP'] = 'arXiv'
                        entry['AR'] = re.search(
                            r'(abs|pdf)/(.+?)(v\d+)?(.pdf|$)', value).group(2)

                    if 'DO' not in entry and 'doi.org' in value.lower():
                        entry['DO'] = re.search(r'doi\.org/(.+?)/?$',
                            value).group(1)

                    # Handle Materials Cloud Archive records:

                    if 'archive.materialscloud.org' in value.lower():
                        entry['TY'] = 'article'
                        entry['J2'] = 'Materials Cloud Archive'
                        entry['VL'], entry['SP'] = re.search('record/(.+?)/?$',
                            value).group(1).split('.')

                elif key in search_keys:
                    entry[key] = value

            if entry:
                # Generate entry identifier from first author and year:

                entry['ID'] = entry.get('AU', 'Unknown').split(',', 1)[0]
                entry['ID'] = simplify(entry['ID'])

                if short_year:
                    entry['ID'] += entry.get('PY', 'XX')[-2:]
                else:
                    entry['ID'] += entry.get('PY', 'XXXX')

                # Protect (and change) capitalization of titles:

                entry['TI'] = protect(entry['TI'])

                if colcap:
                    entry['TI'] = re.sub(r'(: [^A-Z0-9\s]*?[a-z])',
                        lambda x: x.group().upper(), entry['TI'])

                # Remove special spaces from authors and editors:

                for key in 'AU', 'A2':
                    if key in entry:
                        for space in spaces:
                            entry[key] = entry[key].replace(space, ' ')

                # Reduce long author lists to first author "and others":

                if etal > 0 and 'AU' in entry:
                    authors = entry['AU'].split(' and ')

                    if len(authors) > etal:
                        entry['AU'] = '%s and others' % authors[0]

                # Distinguish different types of thesis:

                if 'M3' in entry:
                    first = entry.pop('M3')[0].lower()

                    if first == 'b':
                        entry['M3'] = "Bachelor's thesis"

                    elif first == 'm':
                        entry['M3'] = "Master's thesis"

                    elif first == 'd':
                        entry['M3'] = 'Dissertation'

                    elif first == 'p':
                        pass # "Ph.D. thesis" should be the default

                # Replace non-ASCII characters by LaTeX escape sequences:

                for key in entry:
                    if key not in ('AR', 'DO', 'UR'):
                        entry[key] = escape(entry[key], sup, sub)

                        if nodash:
                            entry[key] = re.sub(r'(?<=[\D\S])--(?=[\D\S])', '-',
                                entry[key])

                # Ensure unknown date components are sorted after known ones:

                if 'DA' in entry:
                    entry['DA'] = entry['DA'].replace('/', '\\')

                # Use long journal name (T2) if short one (J2) not given:

                if 'J2' not in entry and 'T2' in entry:
                    entry['J2'] = entry.pop('T2')

                # Use type "unpublished" for arXiv preprints:

                if 'J2' in entry and entry['J2'].startswith('arXiv'):
                    entry['TY'] = 'unpublished'
                    entry['AP'] = 'arXiv'
                    entry['AR'] = entry.pop('J2').split()[0].split(':')[1]

                # Use type "unpublished" for articles with "arXiv" as publisher:

                if 'PB' in entry and entry['PB'] == 'arXiv':
                    entry['TY'] = 'unpublished'

                # Extract "howpublished" from URL (or just strip protocol):

                if entry.get('TY') == 'misc' and 'UR' in entry:
                    if 'zenodo' in entry['UR'].lower():
                        entry['HP'] = 'Zenodo'
                    else:
                        entry['HP'] = re.sub('^.*?//', '', entry['UR'])
                        entry['HP'] = entry['HP'].replace('/', r'/\allowbreak ')

                # Prefer DOI or e-print identifier over URL:

                if 'UR' in entry and ('DO' in entry or 'AR' in entry):
                    entry.pop('UR')

                # Prefer eprint identifier of unpublished works over DOI:

                if 'TY' in entry and entry['TY'] == 'unpublished':
                    if 'AR' in entry and 'DO' in entry:
                        entry.pop('DO')

                # Set default type:

                if 'TY' not in entry:
                    if 'J2' in entry:
                        entry['TY'] = 'article'
                    else:
                        entry['TY'] = 'unpublished'

                    print('Unknown type (set to "%(TY)s"): %(ID)s' % entry)

                # Consider journal-specific bibliography style files:

                if nature:
                    if 'DO' in entry:
                        entry['UR'] = 'https://doi.org/%s' % entry.pop('DO')
                    elif entry.get('AP') == 'arXiv':
                        entry['UR'] = ('https://arxiv.org/abs/%s'
                            % entry.pop('AR'))
                        entry.pop('AP')

                elif scipost:
                    if entry.get('AP') == 'arXiv':
                        entry['AR'] = 'https://arxiv.org/abs/%s' % entry['AR']
                        entry.pop('AP')

                    if all('zenodo' in entry.get(key, '').lower()
                            for key in ['HP', 'DO']):
                        entry.pop('HP')

                    if entry.get('TY') == 'unpublished':
                        entry['TY'] = 'misc'

                # Remove arXiv identifier:

                if not arxiv:
                    if entry.get('TY') not in {'misc', 'unpublished'}:
                        for key in 'AP', 'AR':
                            entry.pop(key, None)

                entries.append(entry)

    # Sort entries:

    entries = sorted(entries, key=lambda entry: (
        parseInt(entry.get('PY', '')),
        entry.get('DA', '///'),
        entry['ID'],
        entry.get('J2', ''),
        parseInt(entry.get('VL', '')),
        parseInt(entry.get('SP', '')),
        entry.get('TI', ''),
    ))

    # Add suffices non-unique identifiers:

    labels = 'abcdefghijklmnopqrstuvwxyz'

    if skip_a:
        labels = [''] + [label for label in labels[1:]]

    n = 0
    while n < len(entries):
        n0 = n
        while n < len(entries) and entries[n]['ID'] == entries[n0]['ID']:
            n += 1

        if len(entries[n0:n]) > 1:
            for label, entry in zip(labels, entries[n0:n]):
                entry['ID'] += label

                print('Sublabel: %s' % entry['ID'])

    return entries

def write(bib, entries):
    """Write BibTeX output file."""

    with open(bib, 'w') as outfile:
        for entry in entries:
            length = max(len(name) for name, key in types[entry['TY']]
                if key in entry)

            form = '%%%ds = {%%s},\n' % length

            outfile.write('@%s{%s,\n' % (entry['TY'], entry['ID']))

            for name, key in types[entry['TY']]:
                if key in entry:
                    outfile.write(form % (name, entry[key]))

            outfile.write('}\n')

def main():
    ris, bib = positional_arguments()

    kwargs = keyword_arguments()

    entries = read(ris, **kwargs)

    write(bib, entries)

if __name__ == '__main__':
    main()
