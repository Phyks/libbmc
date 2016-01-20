"""
This file contains all the DOI-related functions.
"""
import re
import requests

from requests.exceptions import RequestException

from libbmc import tools

# Taken from
# https://stackoverflow.com/questions/27910/finding-a-doi-in-a-document-or-page/10324802#10324802
REGEX = re.compile(r"\b(10[.][0-9]{4,}(?:[.][0-9]+)*/(?:(?![\"&\'])\S)+)\b",
                   re.IGNORECASE)
# Base dx.doi.org URL for redirections
DX_URL = "http://dx.doi.org/{doi}"


def is_valid(doi):
    """
    Check that a given DOI is a valid canonical DOI.

    :param doi: The DOI to be checked.
    :returns: Boolean indicating whether the DOI is valid or not.

    >>> is_valid('10.1209/0295-5075/111/40005')
    True

    >>> is_valid('10.1016.12.31/nature.S0735-1097(98)2000/12/31/34:7-7')
    True

    >>> is_valid('10.1002/(SICI)1522-2594(199911)42:5<952::AID-MRM16>3.0.CO;2-S')
    True

    >>> is_valid('10.1007/978-3-642-28108-2_19')
    True

    >>> is_valid('10.1007.10/978-3-642-28108-2_19')
    True

    >>> is_valid('10.1016/S0735-1097(98)00347-7')
    True

    >>> is_valid('10.1579/0044-7447(2006)35\[89:RDUICP\]2.0.CO;2')
    True

    >>> is_valid('<geo coords="10.4515260,51.1656910"></geo>')
    False
    """
    match = REGEX.match(doi)
    return ((match is not None) and (match.group(0) == doi))


def extract_from_text(text):
    """
    Extract canonical DOIs from a text.

    :param text: The text to extract DOIs from.
    :returns: A list of found DOIs.

    >>> sorted(extract_from_text('10.1209/0295-5075/111/40005 10.1016.12.31/nature.S0735-1097(98)2000/12/31/34:7-7 10.1002/(SICI)1522-2594(199911)42:5<952::AID-MRM16>3.0.CO;2-S 10.1007/978-3-642-28108-2_19 10.1007.10/978-3-642-28108-2_19 10.1016/S0735-1097(98)00347-7 10.1579/0044-7447(2006)35\[89:RDUICP\]2.0.CO;2 <geo coords="10.4515260,51.1656910"></geo>'))
    ['10.1002/(SICI)1522-2594(199911)42:5<952::AID-MRM16>3.0.CO;2-S', '10.1007.10/978-3-642-28108-2_19', '10.1007/978-3-642-28108-2_19', '10.1016.12.31/nature.S0735-1097(98)2000/12/31/34:7-7', '10.1016/S0735-1097(98)00347-7', '10.1209/0295-5075/111/40005', '10.1579/0044-7447(2006)35\\\\[89:RDUICP\\\\]2.0.CO;2']
    """
    return tools.remove_duplicates(REGEX.findall(text))


def to_URL(dois):
    """
    Convert a list of canonical DOIs to a list of DOIs URLs.

    :param dois: List of canonical DOIs. Can also be a single canonical DOI.
    :returns: A list of DOIs URLs (resp. a single value).

    >>> to_URL(['10.1209/0295-5075/111/40005'])
    ['http://dx.doi.org/10.1209/0295-5075/111/40005']

    >>> to_URL('10.1209/0295-5075/111/40005')
    'http://dx.doi.org/10.1209/0295-5075/111/40005'
    """
    if isinstance(dois, list):
        return [DX_URL.format(doi=doi) for doi in dois]
    else:
        return DX_URL.format(doi=dois)


def to_canonical(urls):
    """
    Convert a list of DOIs URLs to a list of canonical DOIs.

    :param dois: A list of DOIs URLs. Can also be a single DOI URL.
    :returns: List of canonical DOIs (resp. a single value). ``None`` if an \
            error occurred.

    >>> to_canonical(['http://dx.doi.org/10.1209/0295-5075/111/40005'])
    ['10.1209/0295-5075/111/40005']

    >>> to_canonical('http://dx.doi.org/10.1209/0295-5075/111/40005')
    '10.1209/0295-5075/111/40005'

    >>> to_canonical('aaaa') is None
    True

    >>> to_canonical(['aaaa']) is None
    True
    """
    try:
        if isinstance(urls, list):
            return [next(iter(extract_from_text(url))) for url in urls]
        else:
            return next(iter(extract_from_text(urls)))
    except StopIteration:
        return None


def get_oa_version(doi):
    """
    Get an OA version for a given DOI.

    .. note::

        Uses beta.dissem.in API.

    :param doi: A canonical DOI.
    :returns: The URL of the OA version of the given DOI, or ``None``.

    >>> get_oa_version('10.1209/0295-5075/111/40005')
    'http://arxiv.org/abs/1506.06690'
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

    >>> get_linked_version('10.1209/0295-5075/111/40005')
    'http://stacks.iop.org/0295-5075/111/i=4/a=40005?key=crossref.9ad851948a976ecdf216d4929b0b6f01'
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

    >>> get_bibtex('10.1209/0295-5075/111/40005')
    '@article{Verney_2015,\\n\\tdoi = {10.1209/0295-5075/111/40005},\\n\\turl = {http://dx.doi.org/10.1209/0295-5075/111/40005},\\n\\tyear = 2015,\\n\\tmonth = {aug},\\n\\tpublisher = {{IOP} Publishing},\\n\\tvolume = {111},\\n\\tnumber = {4},\\n\\tpages = {40005},\\n\\tauthor = {Lucas Verney and Lev Pitaevskii and Sandro Stringari},\\n\\ttitle = {Hybridization of first and second sound in a weakly interacting Bose gas},\\n\\tjournal = {{EPL}}\\n}'
    """
    try:
        r = requests.get(to_URL(doi),
                         headers={"accept": "application/x-bibtex"})
        r.raise_for_status()
        assert(r.headers.get("content-type") == "application/x-bibtex")
        return r.text
    except (RequestException, AssertionError):
        return None
