"""
This files contains all the functions to extract DOIs of citations from
BibTeX files.
"""
import bibtexparser
import os

from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode

from libbmc import tools
from libbmc.citations import plaintext


def bibentry_as_plaintext(bibentry):
    """
    Return a plaintext representation of a bibentry from BibTeX file.

    .. note::

        This plaintext representation can be super ugly, contain URLs and so \
        on.

    :param bibentry: A bibentry as parsed by ``bibtexparser``.
    :returns: A cleaned plaintext citation from the bibentry.
    """
    # Just flatten the bibentry
    return tools.clean_whitespaces(" ".join([bibentry[k] for k in bibentry]))


def get_plaintext_citations(bibtex):
    """
    Parse a BibTeX file to get a clean list of plaintext citations.

    :param bibtex: Either the path to the BibTeX file or the content of a \
            BibTeX file.
    :returns:  A list of cleaned plaintext citations.
    """
    parser = BibTexParser()
    parser.customization = convert_to_unicode
    # Load the BibTeX
    if os.path.isfile(bibtex):
        with open(bibtex) as fh:
            bib_database = bibtexparser.load(fh, parser=parser)
    else:
        bib_database = bibtexparser.loads(bibtex, parser=parser)
    # Convert bibentries to plaintext
    bibentries = [bibentry_as_plaintext(bibentry)
                  for bibentry in bib_database.entries]
    # Return them
    return bibentries


def get_cited_DOIs(bibtex):
    """
    Get the DOIs of the papers cited in a BibTeX file.

    .. note::

        For now, this function is actually flattening the BibTeX file \
                (loosing any structure provided by the BibTeX) and calling \
                the matching method for plaintext citations, relying on \
                CrossRef API. This is the best method I have found so far, \
                although it can be quite frustrating. Let me know if you have \
                anything better!

    :param bibtex: Either the path to a BibTeX file or the content of a \
            BibTeX file.
    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    # Get the plaintext citations from the bibtex file
    plaintext_citations = get_plaintext_citations(bibtex)
    # Use the plaintext citations parser on these citations
    return plaintext.get_cited_DOIs(plaintext_citations)
