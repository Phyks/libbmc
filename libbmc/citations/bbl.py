"""
This files contains all the functions to deal with .bbl files.
"""
import os
import re
import requests
import subprocess

from requests.exception import RequestException

from libbmc import doi
from libbmc import tools
from libbmc.repositories import arxiv


# Regex to match bibitems
BIBITEMS_REGEX = re.compile(r"\\bibitem\{.+?\}")
# Regex to match end of bibliography
ENDTHEBIBLIOGRAPHY_REGEX = re.compile(r"\\end\{thebibliography}.*")


# CrossRef API URL
CROSSREF_LINKS_API_URL = "http://search.crossref.org/links"
CROSSREF_MAX_BATCH_SIZE = 10


def bibitem_as_plaintext(bibitem):
    """
    Return a plaintext representation of the bibitem from the ``.bbl`` file.

    .. note::

        This plaintext representation can be super ugly, contain URLs and so \
        on.

    :param bibitem: The text content of the bibitem.
    :returns: A cleaned plaintext citation from the bibitem.
    """
    try:
        output = subprocess.check_output(["delatex",
                                          "-s"],
                                         input=bibitem.encode("utf-8"))
    except FileNotFoundError:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output = subprocess.check_output(["%s/../external/opendetex/delatex" %
                                          (script_dir,),
                                          "-s"],
                                         input=bibitem.encode("utf-8"))
    output = output.decode("utf-8")
    output = tools.clean_whitespaces(output)
    return output


def get_plaintext_citations(bbl):
    """
    Parse a ``*.bbl`` file to get a clean list of plaintext citations.

    :param bbl: Either the path to the .bbl file or the content of a ``.bbl`` \
            file.
    :returns:  A list of cleaned plaintext citations.
    """
    # Handle path or content
    if os.path.isfile(bbl):
        with open(bbl, 'r') as fh:
            bbl_content = fh.read()
    else:
        bbl_content = bbl
    # Get a list of bibitems, taking the first item out as it is *before* the
    # first \bibitem
    bibitems = BIBITEMS_REGEX.split(bbl_content)[1:]
    # Delete the text after the \end{thebibliography}
    bibitems = [ENDTHEBIBLIOGRAPHY_REGEX.sub("", i).strip() for i in bibitems]
    # Clean every bibitem to have plaintext
    cleaned_bbl = [bibitem_as_plaintext(bibitem) for bibitem in bibitems]
    return cleaned_bbl


def get_cited_DOIs(bbl):
    """
    Get the DOIs of the papers cited in this .bbl file.

    :param bbl: Either the path to a .bbl file or the content of a .bbl file.

    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    dois = {}
    crossref_queue = []
    # Get the plaintext citations from the bbl file
    plaintext_citations = get_plaintext_citations(bbl)
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
    # Do batch of papers, to prevent from the timeout of crossref
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
