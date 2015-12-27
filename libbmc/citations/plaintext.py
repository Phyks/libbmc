"""
This files contains all the functions to extract DOIs of citations from
plaintext files.
"""
import os
import requests

from requests.exception import RequestException

from libbmc import doi
from libbmc import tools
from libbmc.repositories import arxiv


# CrossRef API URL
CROSSREF_LINKS_API_URL = "http://search.crossref.org/links"
CROSSREF_MAX_BATCH_SIZE = 10


def get_plaintext_citations(file):
    """
    Parse a plaintext file to get a clean list of plaintext citations. The \
            file should have one citation per line.

    :param file: Either the path to the plaintext file or the content of a \
            plaintext file.
    :returns:  A list of cleaned plaintext citations.
    """
    # Handle path or content
    if os.path.isfile(file):
        with open(file, 'r') as fh:
            content = fh.readlines()
    else:
        content = file.splitlines()
    # Clean every line to have plaintext
    cleaned_citations = [tools.clean_whitespaces(line) for line in content]
    return cleaned_citations


def get_cited_DOIs(file):
    """
    Get the DOIs of the papers cited in a plaintext file. The file should \
            have one citation per line.

    .. note::

        This function is also used as a backend tool by most of the others \
        citations processors, to factorize the code.

    :param file: Either the path to the plaintext file or the content of a \
            plaintext file. It can also be a parsed list of plaintext \
            citations and, in this case, no preprocessing is done.
    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    # If file is not a pre-processed list of plaintext citations
    if not isinstance(file, list):
        # It is either a path to a plaintext file or the content of a plaintext
        # file, we need some pre-processing to get a list of citations.
        plaintext_citations = get_plaintext_citations(file)
    dois = {}
    crossref_queue = []

    # Try to get the DOI directly from the citation
    for citation in plaintext_citations[:]:
        # Some citations already contain a DOI so try to match it directly
        matched_DOIs = doi.extract_from_text(citation)
        if matched_DOIs is not None:
            # Add the DOI and go on
            dois[citation] = matched_DOIs[0]
            continue
        # Same thing for arXiv id
        matched_arXiv = arxiv.extract_from_text(citation)
        if matched_arXiv is not None:
            # Add the associated DOI and go on
            dois[citation] = arxiv.to_DOI(matched_arXiv[0])
            continue
        # If no match found, stack it for next step
        # Note to remove URLs in the citation as the plaintext citations can
        # contain URLs and they are bad for the CrossRef API.
        crossref_queue.append(tools.remove_URLs(citation))

    # Do batch with remaining papers, to prevent from the timeout of CrossRef
    for batch in tools.batch(crossref_queue, CROSSREF_MAX_BATCH_SIZE):
        try:
            # Fetch results from CrossRef
            r = requests.post(CROSSREF_LINKS_API_URL, json=batch)
            for result in r.json()["results"]:
                # Try to get a DOI
                try:
                    dois[result["text"]] = result["doi"]
                except KeyError:
                    # Or set it to None
                    dois[result["text"]] = None
        except (RequestException, ValueError, KeyError):
            # If an exception occurred, set all the DOIs to None for the
            # current batch
            for i in batch:
                dois[i] = None
    return dois
