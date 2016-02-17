"""
This file contains all the arXiv-related functions.
"""
import io
import re
import tarfile
import xml.etree.ElementTree

from urllib.error import HTTPError


import arxiv2bib
import bibtexparser
import requests

from requests.exceptions import RequestException


from libbmc import __valid_identifiers__
from libbmc import tools

# Append arXiv to the valid identifiers list
__valid_identifiers__ += ["repositories.arxiv"]


ARXIV_IDENTIFIER_FROM_2007 = r"\d{4}\.\d{4,5}(v\d+)?"
ARXIV_IDENTIFIER_BEFORE_2007 = r"(" + ("|".join([
    "astro-ph.GA",
    "astro-ph.CO",
    "astro-ph.EP",
    "astro-ph.HE",
    "astro-ph.IM",
    "astro-ph.SR",
    "cond-math.dis-nn",
    "cond-math.mtrl-sci",
    "cond-math.mes-hall",
    "cond-math.other",
    "cond-math.quant-gas",
    "cond-math.soft",
    "cond-math.stat-mech",
    "cond-math.str-el",
    "cond-math.supr-con",
    "gr-qc",
    "hep-ex",
    "hep-lat",
    "hep-ph",
    "hep-th",
    "math-ph",
    "nlin.AO",
    "nlin.CG",
    "nlin.CD",
    "nlin.SI",
    "nlin.PS",
    "nucl-ex",
    "nucl-th",
    "physics.acc-ph",
    "physics.ao-ph",
    "physics.atom-ph",
    "physics.atm-clus",
    "physics.bio-ph",
    "physics.chem-ph",
    "physics.class-ph",
    "physics.comp-ph",
    "physics.data-an",
    "physics.flu-dyn",
    "physics.gen-ph",
    "physics.geo-ph",
    "physics.hist-ph",
    "physics.ins-det",
    "physics.med-ph",
    "physics.optics",
    "physics.ed-ph",
    "physics.soc-ph",
    "physics.plasm-ph",
    "physics.pop-ph",
    "physics.space-ph",
    "physics.quant-ph",
    "math.AG",
    "math.AT",
    "math.AP",
    "math.CT",
    "math.CA",
    "math.CO",
    "math.AC",
    "math.CV",
    "math.DG",
    "math.DS",
    "math.FA",
    "math.GM",
    "math.GN",
    "math.GT",
    "math.GR",
    "math.HO",
    "math.IT",
    "math.KT",
    "math.LO",
    "math.MP",
    "math.MG",
    "math.NT",
    "math.NA",
    "math.OA",
    "math.OC",
    "math.PR",
    "math.QA",
    "math.RT",
    "math.RA",
    "math.SP",
    "math.ST",
    "math.SG",
    "cs.AI",
    "cs.CL",
    "cs.CC",
    "cs.CE",
    "cs.CG",
    "cs.GT",
    "cs.CV",
    "cs.CY",
    "cs.CR",
    "cs.DS",
    "cs.DB",
    "cs.DL",
    "cs.DM",
    "cs.DC",
    "cs.ET",
    "cs.FL",
    "cs.GL",
    "cs.GR",
    "cs.AR",
    "cs.HC",
    "cs.IR",
    "cs.IT",
    "cs.LG",
    "cs.LO",
    "cs.MS",
    "cs.MA",
    "cs.MM",
    "cs.NI",
    "cs.NE",
    "cs.NA",
    "cs.OS",
    "cs.OH",
    "cs.PF",
    "cs.PL",
    "cs.RO",
    "cs.SI",
    "cs.SE",
    "cs.SD",
    "cs.SC",
    "cs.SY",
    "q-bio.BM",
    "q-bio.CB",
    "q-bio.GN",
    "q-bio.MN",
    "q-bio.NC",
    "q-bio.OT",
    "q-bio.PE",
    "q-bio.QM",
    "q-bio.SC",
    "q-bio.TO",
    "q-fin.CP",
    "q-fin.EC",
    "q-fin.GN",
    "q-fin.MF",
    "q-fin.PM",
    "q-fin.PR",
    "q-fin.RM",
    "q-fin.ST",
    "q-fin.TR",
    "stat.AP",
    "stat.CO",
    "stat.ML",
    "stat.ME",
    "stat.OT",
    "stat.TH"])) + r")/\d+"
# Regex is fully enclosed in a group for findall to match it all
REGEX = re.compile(
    "((arxiv:)?((" + ARXIV_IDENTIFIER_FROM_2007 + ")|(" +
    ARXIV_IDENTIFIER_BEFORE_2007 + ")))",
    re.IGNORECASE)

# Base arXiv URL used as id sometimes
ARXIV_URL = "http://arxiv.org/abs/{arxiv_id}"
# Eprint URL used to download sources
ARXIV_EPRINT_URL = "http://arxiv.org/e-print/{arxiv_id}"


def get_latest_version(arxiv_id):
    """
    Find the latest version of a given arXiv eprint.

    :param arxiv_id: The (canonical) arXiv ID to query.
    :returns: The latest version on eprint as a string, or ``None``.

    >>> get_latest_version('1401.2910')
    '1401.2910v1'

    >>> get_latest_version('1401.2910v1')
    '1401.2910v1'

    >>> get_latest_version('1506.06690v1')
    '1506.06690v2'

    >>> get_latest_version('1506.06690')
    '1506.06690v2'
    """
    # Get updated bibtex
    # Trick: strip the version from the arXiv id, to query updated BibTeX for
    # the preprint and not the specific version
    arxiv_preprint_id = strip_version(arxiv_id)
    updated_bibtex = bibtexparser.loads(get_bibtex(arxiv_preprint_id))
    updated_bibtex = next(iter(updated_bibtex.entries_dict.values()))

    try:
        return updated_bibtex["eprint"]
    except KeyError:
        return None


def strip_version(arxiv_id):
    """
    Remove the version suffix from an arXiv id.

    :param arxiv_id: The (canonical) arXiv ID to strip.
    :returns: The arXiv ID without the suffix version

    >>> strip_version('1506.06690v1')
    '1506.06690'

    >>> strip_version('1506.06690')
    '1506.06690'
    """
    return re.sub(r"v\d+\Z", '', arxiv_id)


def is_valid(arxiv_id):
    """
    Check that a given arXiv ID is a valid one.

    :param arxiv_id: The arXiv ID to be checked.
    :returns: Boolean indicating whether the arXiv ID is valid or not.

    >>> is_valid('1506.06690')
    True

    >>> is_valid('1506.06690v1')
    True

    >>> is_valid('arXiv:1506.06690')
    True

    >>> is_valid('arXiv:1506.06690v1')
    True

    >>> is_valid('arxiv:1506.06690')
    True

    >>> is_valid('arxiv:1506.06690v1')
    True

    >>> is_valid('math.GT/0309136')
    True

    >>> is_valid('abcdf')
    False

    >>> is_valid('bar1506.06690foo')
    False

    >>> is_valid('mare.GG/0309136')
    False
    """
    match = REGEX.match(arxiv_id)
    return  (match is not None) and (match.group(0) == arxiv_id)


def get_bibtex(arxiv_id):
    """
    Get a BibTeX entry for a given arXiv ID.

    .. note::

        Using awesome https://pypi.python.org/pypi/arxiv2bib/ module.

    :param arxiv_id: The canonical arXiv id to get BibTeX from.
    :returns: A BibTeX string or ``None``.

    >>> get_bibtex('1506.06690')
    "@article{1506.06690v2,\\nAuthor        = {Lucas Verney and Lev Pitaevskii and Sandro Stringari},\\nTitle         = {Hybridization of first and second sound in a weakly-interacting Bose gas},\\nEprint        = {1506.06690v2},\\nDOI           = {10.1209/0295-5075/111/40005},\\nArchivePrefix = {arXiv},\\nPrimaryClass  = {cond-mat.quant-gas},\\nAbstract      = {Using Landau's theory of two-fluid hydrodynamics we investigate the sound\\nmodes propagating in a uniform weakly-interacting superfluid Bose gas for\\nvalues of temperature, up to the critical point. In order to evaluate the\\nrelevant thermodynamic functions needed to solve the hydrodynamic equations,\\nincluding the temperature dependence of the superfluid density, we use\\nBogoliubov theory at low temperatures and the results of a perturbative\\napproach based on Beliaev diagrammatic technique at higher temperatures.\\nSpecial focus is given on the hybridization phenomenon between first and second\\nsound which occurs at low temperatures of the order of the interaction energy\\nand we discuss explicitly the behavior of the two sound velocities near the\\nhybridization point.},\\nYear          = {2015},\\nMonth         = {Jun},\\nUrl           = {http://arxiv.org/abs/1506.06690v2},\\nFile          = {1506.06690v2.pdf}\\n}"

    >>> get_bibtex('1506.06690v1')
    "@article{1506.06690v1,\\nAuthor        = {Lucas Verney and Lev Pitaevskii and Sandro Stringari},\\nTitle         = {Hybridization of first and second sound in a weakly-interacting Bose gas},\\nEprint        = {1506.06690v1},\\nDOI           = {10.1209/0295-5075/111/40005},\\nArchivePrefix = {arXiv},\\nPrimaryClass  = {cond-mat.quant-gas},\\nAbstract      = {Using Landau's theory of two-fluid hydrodynamics we investigate the sound\\nmodes propagating in a uniform weakly-interacting superfluid Bose gas for\\nvalues of temperature, up to the critical point. In order to evaluate the\\nrelevant thermodynamic functions needed to solve the hydrodynamic equations,\\nincluding the temperature dependence of the superfluid density, we use\\nBogoliubov theory at low temperatures and the results of a perturbative\\napproach based on Beliaev diagrammatic technique at higher temperatures.\\nSpecial focus is given on the hybridization phenomenon between first and second\\nsound which occurs at low temperatures of the order of the interaction energy\\nand we discuss explicitly the behavior of the two sound velocities near the\\nhybridization point.},\\nYear          = {2015},\\nMonth         = {Jun},\\nUrl           = {http://arxiv.org/abs/1506.06690v1},\\nFile          = {1506.06690v1.pdf}\\n}"
    """
    # Fetch bibtex using arxiv2bib module
    try:
        bibtex = arxiv2bib.arxiv2bib([arxiv_id])
    except HTTPError:
        bibtex = []

    for bib in bibtex:
        if isinstance(bib, arxiv2bib.ReferenceErrorInfo):
            continue
        else:
            # Return fetched bibtex
            return bib.bibtex()
    # An error occurred, return None
    return None


def extract_from_text(text):
    """
    Extract arXiv IDs from a text.

    :param text: The text to extract arXiv IDs from.
    :returns: A list of matching arXiv IDs, in canonical form.

    >>> sorted(extract_from_text('1506.06690 1506.06690v1 arXiv:1506.06690 arXiv:1506.06690v1 arxiv:1506.06690 arxiv:1506.06690v1 math.GT/0309136 abcdf bar1506.06690foo mare.GG/0309136'))
    ['1506.06690', '1506.06690v1', 'math.GT/0309136']
    """
    # Remove the leading "arxiv:".
    return tools.remove_duplicates([re.sub("arxiv:", "", i[0],
                                           flags=re.IGNORECASE)
                                    for i in REGEX.findall(text) if i[0] != ''])


def to_url(arxiv_ids):
    """
    Convert a list of canonical DOIs to a list of DOIs URLs.

    :param dois: List of canonical DOIs.
    :returns: A list of DOIs URLs.

    >>> to_url('1506.06690')
    'http://arxiv.org/abs/1506.06690'

    >>> to_url('1506.06690v1')
    'http://arxiv.org/abs/1506.06690v1'
    """
    if isinstance(arxiv_ids, list):
        return [ARXIV_URL.format(arxiv_id=arxiv_id) for arxiv_id in arxiv_ids]
    else:
        return ARXIV_URL.format(arxiv_id=arxiv_ids)


def to_canonical(urls):
    """
    Convert a list of arXiv IDs to a list of canonical IDs.

    :param dois: A list of DOIs URLs.
    :returns: List of canonical DOIs. ``None`` if an error occurred.

    >>> to_canonical('http://arxiv.org/abs/1506.06690')
    '1506.06690'

    >>> to_canonical('http://arxiv.org/abs/1506.06690v1')
    '1506.06690v1'

    >>> to_canonical(['http://arxiv.org/abs/1506.06690'])
    ['1506.06690']

    >>> to_canonical('aaa') is None
    True
    """
    return tools.map_or_apply(extract_from_text, urls)


def from_doi(doi):
    """
    Get the arXiv eprint id for a given DOI.

    .. note::

        Uses arXiv API. Will not return anything if arXiv is not aware of the
        associated DOI.

    :param doi: The DOI of the resource to look for.
    :returns: The arXiv eprint id, or ``None`` if not found.

    >>> from_doi('10.1209/0295-5075/111/40005')
    # Note: Test do not pass due to an arXiv API bug.
    '1506.06690'
    """
    try:
        request = requests.get("http://export.arxiv.org/api/query",
                               params={
                                   "search_query": "doi:%s" % (doi,),
                                   "max_results": 1
                               })
        request.raise_for_status()
    except RequestException:
        return None
    root = xml.etree.ElementTree.fromstring(request.content)
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        arxiv_id = entry.find("{http://www.w3.org/2005/Atom}id").text
        # arxiv_id is an arXiv full URL. We only want the id which is the last
        # URL component.
        return arxiv_id.split("/")[-1]
    return None


def to_doi(arxiv_id):
    """
    Get the associated DOI for a given arXiv eprint.

    .. note::

        Uses arXiv API. Will not return anything if arXiv is not aware of the
        associated DOI.

    :param eprint: The arXiv eprint id.
    :returns: The DOI if any, or ``None``.

    >>> to_doi('1506.06690v1')
    '10.1209/0295-5075/111/40005'

    >>> to_doi('1506.06690')
    '10.1209/0295-5075/111/40005'
    """
    try:
        request = requests.get("http://export.arxiv.org/api/query",
                               params={
                                   "id_list": arxiv_id,
                                   "max_results": 1
                               })
        request.raise_for_status()
    except RequestException:
        return None
    root = xml.etree.ElementTree.fromstring(request.content)
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        doi = entry.find("{http://arxiv.org/schemas/atom}doi")
        if doi is not None:
            return doi.text
    return None


def get_sources(arxiv_id):
    """
    Download sources on arXiv for a given preprint.

    .. note::

        Bulk download of sources from arXiv is not permitted by their API. \
                You should have a look at http://arxiv.org/help/bulk_data_s3.

    :param eprint: The arXiv id (e.g. ``1401.2910`` or ``1401.2910v1``) in a \
            canonical form.
    :returns: A ``TarFile`` object of the sources of the arXiv preprint or \
            ``None``.
    """
    try:
        request = requests.get(ARXIV_EPRINT_URL.format(arxiv_id=arxiv_id))
        request.raise_for_status()
        file_object = io.BytesIO(request.content)
        return tarfile.open(fileobj=file_object)
    except (RequestException, AssertionError, tarfile.TarError):
        return None


def get_bbl(arxiv_id):
    """
    Get the .bbl files (if any) of a given preprint.

    .. note::

        Bulk download of sources from arXiv is not permitted by their API. \
                You should have a look at http://arxiv.org/help/bulk_data_s3.

    :param arxiv_id: The arXiv id (e.g. ``1401.2910`` or ``1401.2910v1``) in \
            a canonical form.
    :returns: A list of the full text of the ``.bbl`` files (if any) \
            or ``None``.
    """
    tar_file = get_sources(arxiv_id)
    bbl_files = [i for i in tar_file.getmembers() if i.name.endswith(".bbl")]
    bbl_files = [tar_file.extractfile(member).read().decode(tarfile.ENCODING)
                 for member in bbl_files]
    return bbl_files
