"""
This file contains all the functions to extract DOIs of citations from arXiv
papers.
"""
from libbmc.citations import bbl
from libbmc.repositories import arxiv


def get_plaintext_citations(arxiv_id):
    """
    Get the citations of a given preprint, in plain text.

    .. note::

        Bulk download of sources from arXiv is not permitted by their API. \
                You should have a look at http://arxiv.org/help/bulk_data_s3.

    :param arxiv_id: The arXiv id (e.g. ``1401.2910`` or ``1401.2910v1``) in \
            a canonical form.
    :returns:  A list of cleaned plaintext citations.
    """
    plaintext_citations = []
    # Get the list of bbl files for this preprint
    bbl_files = arxiv.get_bbl(arxiv_id)
    for bbl_file in bbl_files:
        # Fetch the cited DOIs for each of the bbl files
        plaintext_citations.extend(bbl.get_plaintext_citations(bbl_file))
    return plaintext_citations


def get_cited_dois(arxiv_id):
    """
    Get the DOIs of the papers cited in a .bbl file.

    .. note::

        Bulk download of sources from arXiv is not permitted by their API. \
                You should have a look at http://arxiv.org/help/bulk_data_s3.

    :param arxiv_id: The arXiv id (e.g. ``1401.2910`` or ``1401.2910v1``) in \
            a canonical form.
    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    dois = {}
    # Get the list of bbl files for this preprint
    bbl_files = arxiv.get_bbl(arxiv_id)
    for bbl_file in bbl_files:
        # Fetch the cited DOIs for each of the bbl files
        dois.update(bbl.get_cited_dois(bbl_file))
    return dois
