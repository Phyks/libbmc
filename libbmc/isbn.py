"""
This file contains all the ISBN-related functions.
"""
import isbnlib

from libbmc import doi

from libbmc import __valid_identifiers__

# Append ISBN to the valid identifiers list
__valid_identifiers__ += ["isbn"]


def is_valid(isbn_id):
    """
    Check that a given string is a valid ISBN.

    :param isbn_id: the isbn to be checked.
    :returns: boolean indicating whether the isbn is valid or not.

    >>> is_valid("978-3-16-148410-0")
    True

    >>> is_valid("9783161484100")
    True

    >>> is_valid("9783161484100aa")
    False

    >>> is_valid("abcd")
    False

    >>> is_valid("0136091814")
    True

    >>> is_valid("0136091812")
    False

    >>> is_valid("9780136091817")
    False

    >>> is_valid("123456789X")
    True
    """
    return (
        (not isbnlib.notisbn(isbn_id)) and (
            isbnlib.get_canonical_isbn(isbn_id) == isbn_id or
            isbnlib.mask(isbnlib.get_canonical_isbn(isbn_id)) == isbn_id)
    )


def extract_from_text(text):
    """
    Extract ISBNs from a text.

    :param text: Some text.
    :returns: A list of canonical ISBNs found in the text.

    >>> extract_from_text("978-3-16-148410-0 9783161484100 9783161484100aa abcd 0136091814 0136091812 9780136091817 123456789X")
    ['9783161484100', '9783161484100', '9783161484100', '0136091814', '123456789X']
    """
    isbns = [isbnlib.get_canonical_isbn(isbn)
             for isbn in isbnlib.get_isbnlike(text)]
    return [i for i in isbns if i is not None]


def get_bibtex(isbn_identifier):
    """
    Get a BibTeX string for the given ISBN.

    :param isbn_identifier: ISBN to fetch BibTeX entry for.
    :returns: A BibTeX string or ``None`` if could not fetch it.

    >>> get_bibtex('9783161484100')
    '@book{9783161484100,\\n     title = {Berkeley, Oakland: Albany, Emeryville, Alameda, Kensington},\\n    author = {Peekaboo Maps},\\n      isbn = {9783161484100},\\n      year = {2009},\\n publisher = {Peek A Boo Maps}\\n}'
    """
    # Try to find the BibTeX using associated DOIs
    bibtex = doi.get_bibtex(to_doi(isbn_identifier))
    if bibtex is None:
        # In some cases, there are no DOIs for a given ISBN. In this case, try
        # to fetch bibtex directly from the ISBN, using a combination of
        # Google Books and worldcat.org results.
        bibtex = isbnlib.registry.bibformatters['bibtex'](
            isbnlib.meta(isbn_identifier, 'default'))
    return bibtex


def to_doi(isbn_identifier):
    """
    Make a DOI out of the given ISBN.

    .. note::

        See https://github.com/xlcnd/isbnlib#note. The returned DOI may not be
        issued yet.

    :param isbn_identifier: A valid ISBN string.
    :returns: A DOI as string.

    >>> to_doi('9783161484100')
    '10.978.316/1484100'
    """
    return isbnlib.doi(isbn_identifier)


def from_doi(doi_identifier):
    """
    Make an ISBN out of the given DOI.

    .. note::

        Taken from
        https://github.com/xlcnd/isbnlib/issues/30#issuecomment-167444777.


    .. note::

        See https://github.com/xlcnd/isbnlib#note. The returned ISBN may not be
        issued yet (it is a valid one, but not necessary corresponding to a
        valid book).

    :param doi_identifier: A valid canonical DOI.
    :returns: An ISBN string.

    >>> from_doi('10.978.316/1484100')
    '9783161484100'
    """
    return "".join(c for c in doi_identifier[2:] if c in "0123456789xX")
