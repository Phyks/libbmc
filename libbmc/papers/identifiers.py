"""
This file contains various functions to fetch unique identifiers from papers
(DOIs, arXiv id etc).

Needs pdftotext and/or djvutxt installed on the machine.

TODO: Unittests
"""
import importlib
import subprocess
import sys

from libbmc import __valid_identifiers__

# Import all the modules associated to __valid_identifiers__
for type in __valid_identifiers__:
    importlib.import_module("libbmc.%s" % (type,))


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

    :returns: a tuple (type, identifier) or ``(None, None)`` if not found or \
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
        return (None, None)

    while totext.poll() is None:
        extract_full = ' '.join([i.decode("utf-8").strip()
                                for i in totext.stdout.readlines()])
        # Loop over all the valid identifier types
        for type in __valid_identifiers__:
            # Dynamically call the ``extract_from_text`` method for the
            # associated module.
            m = sys.modules.get("libbmc.%s" % (type,), None)
            if m is None:
                continue
            found_id = getattr(m, "extract_from_text")(extract_full)
            if found_id:
                totext.terminate()
                return (type, found_id[0])  # found_id is a list of found IDs
    return (None, None)


def get_bibtex(identifier):
    """
    Try to fetch BibTeX from a found identifier.

    .. note::

        Calls the functions in the respective identifiers module.

    :param identifier: a tuple (type, identifier) with a valid type.
    :returns: A BibTeX string or ``None`` if an error occurred.
    # TODO: Should return a BiBTeX object?
    """
    type, id = identifier
    if type not in __valid_identifiers__:
        return None

    # Dynamically call the ``get_bibtex`` method from the associated module.
    m = sys.modules.get("libbmc.%s" % (type,), None)
    if m is None:
        return None
    return getattr(m, "get_bibtex")(id)
