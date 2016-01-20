"""
This file contains various functions to fetch unique identifiers from papers
(DOIs, arXiv id etc).

Needs pdftotext and/or djvutxt installed on the machine.

TODO: Unittests
"""
import subprocess

from libbmc import doi, isbn
from libbmc.repositories import arxiv, hal


def find_identifiers(src):
    """
    Search for a valid identifier (DOI, ISBN, arXiv, HAL) in a given file.

    .. note::

        This function returns the first matching identifier, that is the most
        likely to be relevant for this file. However, it may fail and return an
        identifier taken from the references or another paper.

    .. note::

        You will need to have ``pdftotext`` and/or ``djvutxt`` installed \
                system-wide before processing files with this function.


    :params src: Path to the file to scan.

    :returns: a tuple (type, identifier) or ``None`` if not found or \
            an error occurred.
    """
    if src.endswith(".pdf"):
        totext = subprocess.Popen(["pdftotext", src, "-"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  bufsize=1)
    elif src.endswith(".djvu"):
        totext = subprocess.Popen(["djvutxt", src],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE,
                                  bufsize=1)
    else:
        return None

    while totext.poll() is None:
        extract_full = ' '.join([i.decode("utf-8").strip()
                                for i in totext.stdout.readlines()])
        found_isbn = isbn.extract_from_text(extract_full)
        if isbn:
            totext.terminate()
            return ("isbn", found_isbn)

        found_doi = doi.extract_from_text(extract_full)
        if doi:
            totext.terminate()
            return ("doi", found_doi)

        found_arxiv = arxiv.extract_from_text(extract_full)
        if arxiv:
            totext.terminate()
            return ("arxiv", found_arxiv)

        found_hal = hal.extract_from_text(extract_full)
        if hal:
            totext.terminate()
            return ("hal", found_hal)

    return None
