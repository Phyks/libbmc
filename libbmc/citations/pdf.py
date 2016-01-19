"""
This files contains all the functions to extract DOIs of citations from
PDF files.
"""
import requests
import subprocess
import xml.etree.ElementTree as ET

from requests.exceptions import RequestException

from libbmc.citations import plaintext


CERMINE_BASE_URL = "http://cermine.ceon.pl/"


def cermine(pdf_file):
    """
    Run `CERMINE <https://github.com/CeON/CERMINE>`_ to extract procedure on \
            the given PDF file, to retrieve citations (and more) from the \
            provided PDF file.

    .. note::

        This uses the `CERMINE API <http://cermine.ceon.pl/about.html>`_, and \
                hence, uploads the PDF file (so uses network). Check out \
                the CERMINE API terms.

    :param pdf_file: Path to the PDF file to handle.
    :returns: Raw output from CERMINE API or ``None`` if an error occurred. \
            No post-processing is done.
    """
    try:
        with open(pdf_file, "rb") as fh:
            r = requests.post(
                CERMINE_BASE_URL + "extract.do",
                headers={"Content-Type": "application/binary"},
                files={"file": fh}
            )
        return r.text
    except (RequestException, FileNotFoundError):
        return None


def grobid(pdf_file):
    """
    Run `Grobid <https://github.com/kermitt2/grobid>`_ on a given PDF file to \
            extract references.

    .. note::

        Before using this function, you have to download and build Grobid on \
                your system. See \
                `<https://grobid.readthedocs.org/en/latest/Install-Grobid/>`_ \
                for more infos on this. You need Java and \
                ``grobid-core-`<current version>`.one-jar.jar`` to be in your \
                ``$PATH``.

    :param pdf_file: Path to the PDF file to handle.
    :returns: Raw output from ``Grobid`` or ``None`` if an error occurred.
    """
    # TODO + update docstring
    # TODO: Use https://github.com/kermitt2/grobid-example
    subprocess.check_output(["java",
                             "-jar", "grobid-core-0.3.0.one-jar.jar",
                             "-Xmx1024m",  # Avoid OutOfMemoryException
                             "-gH", "/path/to/Grobid/grobid/grobid-home",
                             "-gP", "/path/to/Grobid/grobid-home/config/grobid.properties",
                             "-dIn", "/path/to/input/directory",
                             "-dOut", "/path/to/output/directory",
                             "-exe", "processReferences"])


def pdfextract(pdf_file):
    """
    Run `pdfextract <https://github.com/CrossRef/pdfextract>`_ on a given PDF \
            file to extract references.

    .. note::

        Before using this function, you have to install pdfextract on \
                your system. See \
                `<https://github.com/CrossRef/pdfextract#quick-start>`_ \
                for more infos on this. You need the ``pdf-extract`` command \
                to be in your ``$PATH``. This can be done easily using \
                ``gem install pdf-extract``, provided that you have a correct \
                Ruby install on your system.

    .. note::

        ``pdfextract`` is full a bugs and as the time of writing this, \
                you had to manually ``gem install pdf-reader -v 1.2.0`` \
                before installing ``pdfextract`` or you would get errors. See \
                `this Github issue <https://github.com/CrossRef/pdfextract/issues/23>`_.

    :param pdf_file: Path to the PDF file to handle.
    :returns: Raw output from ``pdfextract`` or ``None`` if an error \
            occurred. No post-processing is done. See \
            ``libbmc.citations.pdf.pdfextract_dois`` for a similar function \
            with post-processing to return DOIs.
    """
    try:
        # Run pdf-extract
        references = subprocess.check_output(["pdf-extract",
                                              "extract", "--references",
                                              pdf_file])
        return references
    except subprocess.CalledProcessError:
        return None


def pdfextract_dois(pdf_file):
    """
    Extract DOIs of references using \
            `pdfextract <https://github.com/CrossRef/pdfextract>`_.

    .. note::

        See ``libbmc.citations.pdf.pdfextract`` function as this one is just \
                a wrapper around it.
        See ``libbmc.citations.plaintext.get_cited_dois`` as well for the \
                returned value, as it is ultimately called by this function.

    :param pdf_file: Path to the PDF file to handle.
    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    # Call pdf-extract on the PDF file
    references = pdfextract(pdf_file)
    # Parse the resulting XML
    root = ET.fromstring(references)
    plaintext_references = [e.text for e in root.iter("reference")]
    # Call the plaintext methods to fetch DOIs
    return plaintext.get_cited_DOIs(plaintext_references)
