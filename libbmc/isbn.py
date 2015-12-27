"""
This file contains all the ISBN-related functions.
"""
import isbnlib

from libbmc import doi


def is_valid(isbn):
    """
    Check that a given string is a valid ISBN.

    :param isbn: the isbn to be checked.
    :returns: boolean indicating whether the isbn is valid or not.

    """
    return not isbnlib.notisbn(isbn)


def extract_from_text(text):
    """
    Extract ISBNs from a text.

    :param text: Some text.
    :returns: A list of canonical ISBNs found in the text.
    """
    return [isbnlib.get_canonical_isbn(isbn)
            for isbn in isbnlib.get_isbnlike(text)]


def get_bibtex(isbn):
    """
    Get a BibTeX string for the given ISBN.

    :param isbn: ISBN to fetch BibTeX entry for.
    :returns: A BibTeX string or ``None`` if could not fetch it.
    """
    # Try to find the BibTeX using associated DOIs
    bibtex = doi.get_bibtex(to_DOI(isbn))
    if bibtex is None:
        # In some cases, there are no DOIs for a given ISBN. In this case, try
        # to fetch bibtex directly from the ISBN, using a combination of
        # Google Books and worldcat.org results.
        bibtex = isbnlib.registry.bibformatters['bibtex'](
            isbnlib.meta(isbn, 'default'))
    return bibtex


def to_DOI(isbn):
    """
    Make a DOI out of the given ISBN.

    .. note::

        See https://github.com/xlcnd/isbnlib#note. The returned DOI may not be
        issued yet.

    :param isbn: A valid ISBN string.
    :returns: A DOI as string.
    """
    return isbnlib.doi(isbn)


def from_DOI(doi):
    """
    Make an ISBN out of the given DOI.

    .. note::

        Taken from
        https://github.com/xlcnd/isbnlib/issues/30#issuecomment-167444777.


    .. note::

        See https://github.com/xlcnd/isbnlib#note. The returned ISBN may not be
        issued yet (it is a valid one, but not necessary corresponding to a
        valid book).

    :param doi: A valid canonical DOI.
    :returns: An ISBN string.
    """
    return "".join(c for c in doi[2:] if c in "0123456789xX")
