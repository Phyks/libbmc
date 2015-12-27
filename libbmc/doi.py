"""
This file contains all the DOI-related functions.
"""
import re
import requests

from requests.exception import RequestException

from libbmc import tools

# Taken from
# https://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page/10324802#10324802
REGEX = re.compile(r"\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'<>])\S)+)\b",
                   re.IGNORECASE)
# Base dx.doi.org URL for redirections
DX_URL = "http://dx.doi.org/{doi}"


def is_valid(doi):
    """
    Check that a given DOI is a valid canonical DOI.

    :param doi: The DOI to be checked.
    :returns: Boolean indicating whether the DOI is valid or not.
    """
    match = REGEX.match(doi)
    return ((match is not None) and (match.group(0) == doi))


def extract_from_text(text):
    """
    Extract canonical DOIs from a text.

    :param text: The text to extract DOIs from.
    :returns: A list of found DOIs.
    """
    return tools.remove_duplicates(REGEX.findall(text))


def to_URL(dois):
    """
    Convert a list of canonical DOIs to a list of DOIs URLs.

    :param dois: List of canonical DOIs.
    :returns: A list of DOIs URLs.
    """
    if isinstance(dois, list):
        return [DX_URL.format(doi=doi) for doi in dois]
    else:
        return DX_URL.format(doi=dois)


def to_canonical(urls):
    """
    Convert a list of DOIs URLs to a list of canonical DOIs.

    :param dois: A list of DOIs URLs.
    :returns: List of canonical DOIs.
    """
    if isinstance(urls, list):
        return [extract_from_text(url) for url in urls]
    else:
        return extract_from_text(urls)


def get_oa_version(doi):
    """
    Get an OA version for a given DOI.

    .. note::

        Uses beta.dissem.in API.

    :param doi: A canonical DOI.
    :returns: The URL of the OA version of the given DOI, or ``None``.
    """
    # If DOI is a link, truncate it
    try:
        r = requests.get("http://beta.dissem.in/api/%s" % (doi,))
        r.raise_for_status()
        result = r.json()
        assert(result["status"] == "ok")
        return result["paper"]["pdf_url"]
    except (AssertionError, ValueError, KeyError, RequestException):
        return None


def get_linked_version(doi):
    """
    Get the original link behind the DOI.

    :param doi: A canonical DOI.
    :returns: The canonical URL behind the DOI, or ``None``.
    """
    try:
        r = requests.head(to_URL(doi))
        return r.headers.get("location")
    except RequestException:
        return None


def get_bibtex(doi):
    """
    Get a BibTeX entry for a given DOI.

    .. note::

        Adapted from https://gist.github.com/jrsmith3/5513926.

    :param doi: The canonical DOI to get BibTeX from.
    :returns: A BibTeX string or ``None``.
    """
    try:
        r = requests.get(to_URL(doi),
                         headers={"accept": "application/x-bibtex"})
        r.raise_for_status()
        assert(r.headers.get("content-type") == "application/x-bibtex")
        return r.text
    except (RequestException, AssertionError):
        return None
