"""
This file contains all the arXiv-related functions.
"""
import io
import re
import requests
import tarfile
import xml.etree.ElementTree

from libbmc import tools


arxiv_identifier_from_2007 = r"\d{4}\.\d{4,5}(v\d+)?"
arxiv_identifier_before_2007 = r"(" + ("|".join([
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
regex = re.compile(
    "(" + arxiv_identifier_from_2007 + ")|(" +
    arxiv_identifier_before_2007 + ")",
    re.IGNORECASE)

# Base arXiv URL used as id sometimes
arxiv_url = "http://arxiv.org/abs/{arxiv_id}"
# Eprint URL used to download sources
arxiv_eprint_url = "http://arxiv.org/e-print/{arxiv_id}"


def is_valid(arxiv_id):
    """
    Check that a given arXiv ID is a valid one.

    :param arxiv_id: The arXiv ID to be checked.
    :returns: Boolean indicating whether the arXiv ID is valid or not.
    """
    match = regex.match(arxiv_id)
    return ((match is not None) and (match.group(0) == arxiv_id))


def get_bibtex(arxiv_id):
    """
    TODO
    """
    assert(False)


def extract_from_text(text):
    """
    Extract arXiv IDs from a text.

    :param text: The text to extract arXiv IDs from.
    :returns: A list of matching arXiv IDs.
    """
    return tools.remove_duplicates(regex.findall(text))


def to_URL(arxiv_ids):
    """
    Convert a list of canonical DOIs to a list of DOIs URLs.

    :param dois: List of canonical DOIs.
    :returns: A list of DOIs URLs.
    """
    if isinstance(arxiv_ids, list):
        return [arxiv_url.format(arxiv_id=arxiv_id) for arxiv_id in arxiv_ids]
    else:
        return arxiv_url.format(arxiv_id=arxiv_ids)


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


def from_doi(doi):
    """
    Get the arXiv eprint id for a given DOI.

    .. note::

        Uses arXiv API. Will not return anything if arXiv is not aware of the
        associated DOI.

    :param doi: The DOI of the resource to look for.
    :returns: The arXiv eprint id, or ``None`` if not found.
    """
    r = requests.get("http://export.arxiv.org/api/query",
                     params={
                         "search_query": "doi:%s" % (doi,),
                         "max_results": 1
                     })
    e = xml.etree.ElementTree.fromstring(r.content)
    for entry in e.iter("{http://www.w3.org/2005/Atom}entry"):
        id = entry.find("{http://www.w3.org/2005/Atom}id").text
        # id is an arXiv full URL. We only want the id which is the last URL
        # component.
        return id.split("/")[-1]
    return None


def to_doi(arxiv_id):
    """
    Get the associated DOI for a given arXiv eprint.

    .. note::

        Uses arXiv API. Will not return anything if arXiv is not aware of the
        associated DOI.

    :param eprint: The arXiv eprint id.
    :returns: The DOI if any, or ``None``.
    """
    r = requests.get("http://export.arxiv.org/api/query",
                     params={
                         "id_list": arxiv_id,
                         "max_results": 1
                     })
    e = xml.etree.ElementTree.fromstring(r.content)
    for entry in e.iter("{http://www.w3.org/2005/Atom}entry"):
        doi = entry.find("{http://arxiv.org/schemas/atom}doi")
        if doi is not None:
            return doi.text
    return None


def get_sources(arxiv_id):
    """
    Download sources on arXiv for a given preprint.

    :param eprint: The arXiv id (e.g. ``1401.2910`` or ``1401.2910v1``) in a \
            canonical form.
    :returns: A ``TarFile`` object of the sources of the arXiv preprint or \
            ``None``.
    """
    r = requests.get(arxiv_eprint_url.format(arxiv_id=arxiv_id))
    try:
        assert(r.status_code == requests.codes.ok)
        file_object = io.BytesIO(r.content)
        return tarfile.open(fileobj=file_object)
    except (AssertionError, tarfile.TarError):
        return None


def get_bbl(arxiv_id):
    """
    Get the .bbl files (if any) of a given preprint.

    :param eprint: The arXiv id (e.g. ``1401.2910`` or ``1401.2910v1``) in a \
            canonical form.
    :returns: A list of the full text of the ``.bbl`` files (if any) \
            or ``None``.
    """
    tf = get_sources(arxiv_id)
    bbl_files = [i for i in tf.getmembers() if i.name.endswith(".bbl")]
    bbl_files = [tf.extractfile(member).read().decode(tarfile.ENCODING)
                 for member in bbl_files]
    return bbl_files


def get_citations(arxiv_id):
    """
    TODO
    """
    assert(False)
