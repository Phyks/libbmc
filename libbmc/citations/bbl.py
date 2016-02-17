"""
This file contains all the functions to extract DOIs of citations from .bbl
files.
"""
import os
import re
import subprocess

from libbmc import tools
from libbmc.citations import plaintext


# Regex to match bibitems
BIBITEMS_REGEX = re.compile(r"\\bibitem\{.+?\}")
# Regex to match end of bibliography
ENDTHEBIBLIOGRAPHY_REGEX = re.compile(r"\\end\{thebibliography}.*")


def bibitem_as_plaintext(bibitem):
    """
    Return a plaintext representation of a bibitem from the ``.bbl`` file.

    .. note::

        This plaintext representation can be super ugly, contain URLs and so \
        on.

    .. note::

        You need to have ``delatex`` installed system-wide, or to build it in \
                this repo, according to the ``README.md`` before using this \
                function.

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


def get_cited_dois(bbl):
    """
    Get the DOIs of the papers cited in a .bbl file.

    :param bbl: Either the path to a .bbl file or the content \
            of a .bbl file.

    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    # Get the plaintext citations from the bbl file
    plaintext_citations = get_plaintext_citations(bbl)
    # Use the plaintext citations parser on these citations
    return plaintext.get_cited_dois(plaintext_citations)
