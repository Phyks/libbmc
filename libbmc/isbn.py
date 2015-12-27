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
    :returns: A BibTeX string.
    """
    return doi.get_bibtex(to_doi(isbn))


def to_doi(isbn):
    """
    Try to fetch a DOI from a given ISBN.

    :param isbn: A valid ISBN string.
    :returns: A DOI as string.
    """
    return isbnlib.doi(isbn)


def from_doi(doi):
    """
    TODO
    """
    assert(False)
