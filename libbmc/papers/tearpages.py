"""
This file contains the necessary functions to determine whether we should tear
the first page from a PDF file, and actually tear it.
"""
import tearpages


# List of bad publishers which adds an extra useless first page, which can be
# teared. Please, submit a PR to include new ones which I may not be aware of!
BAD_PUBLISHERS = [
    "IOP"
]


def tearpage_needed(bibtex):
    """
    Check whether a given paper needs the first page to be teared or not.

    :params bibtex: The bibtex entry associated to the paper, to guess \
            whether tearing is needed.
    :returns: A boolean indicating whether first page should be teared or not.
    """
    # For each bad publisher, look for it in the publisher bibtex entry
    has_bad_publisher = [p in bibtex.get("publisher", [])
                         for p in BAD_PUBLISHERS]
    # Return True iff there is at least one bad publisher
    return (True in has_bad_publisher)


def tearpage(filename, bibtex=None):
    """
    Tear the first page of the file if needed.

    :params filename: Path to the file to handle.
    :params bibtex: BibTeX dict associated to this file, as the one given by \
            ``bibtexparser``.
    :returns: A boolean indicating whether the file has been teared or not. \
            Side effect is tearing the first page from the file.
    """
    if bibtex is not None and tearpage_needed(bibtex):
        # If tearing is needed, do it and return True
        tearpages.tearpage(filename)
        return True
    # Else, simply return False
    return False
