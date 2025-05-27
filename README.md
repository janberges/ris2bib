# ris2bib

Convert bibliographies from RIS to BibTeX format.

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
