"""
This files contains all the functions to extract DOIs of citations from
PDF files.

# TODO: Unittests
"""
import os
import requests
import subprocess
import xml.etree.ElementTree as ET

from requests.exceptions import RequestException

from libbmc.citations import plaintext


CERMINE_BASE_URL = "http://cermine.ceon.pl/"
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))


def cermine(pdf_file, force_API=False, override_local=None):
    """
    Run `CERMINE <https://github.com/CeON/CERMINE>`_ to extract metadata from \
            the given PDF file, to retrieve citations (and more) from the \
            provided PDF file. This function returns the raw output of \
            CERMINE call.

    .. note::

        Try to use a local CERMINE JAR file, and falls back to using the API. \
                JAR file is expected to be found in \
                ``libbmc/external/cermine.jar``. You can override this using \
                the ``override_local`` parameter.

    .. note::

        CERMINE JAR file can be found at \
                `<http://maven.icm.edu.pl/artifactory/simple/kdd-releases/pl/edu/icm/cermine/cermine-impl/>`_.

    .. note::

        This fallback using the \
                `CERMINE API <http://cermine.ceon.pl/about.html>`_, and \
                hence, uploads the PDF file (so uses network). Check out \
                the CERMINE API terms.

    :param pdf_file: Path to the PDF file to handle.
    :param force_API: Force the use of the Cermine API \
            (and do not try to use a local JAR file). Defaults to ``False``.
    :param override_local: Use this specific JAR file, instead of the one at \
            the default location (``libbmc/external/cermine.jar``).
    :returns: Raw output from CERMINE API or ``None`` if an error occurred. \
            No post-processing is done.
    """
    try:
        # Check if we want to load the local JAR from a specific path
        local = override_local
        # Else, try to stat the JAR file at the expected local path
        if (local is None) and (not force_API):
            if os.path.isfile(os.path.join(SCRIPT_DIR,
                                           "../external/cermine.jar")):
                local = os.path.join(SCRIPT_DIR,
                                     "../external/cermine.jar")

        # If we want to force the API use, or we could not get a local JAR
        if force_API or (local is None):
            print("Using API")
            with open(pdf_file, "rb") as fh:
                    # Query the API
                    r = requests.post(
                        CERMINE_BASE_URL + "extract.do",
                        headers={"Content-Type": "application/binary"},
                        files={"file": fh}
                    )
                    return r.text
        # Else, use the local JAR file
        else:
            return subprocess.check_output([
                "java",
                "-cp", local,
                "pl.edu.icm.cermine.PdfNLMContentExtractor",
                "-path", pdf_file])
    except (RequestException,
            subprocess.CalledProcessError,
            FileNotFoundError):
        # In case of any error, return None
        return None


def cermine_dois(pdf_file, force_API=False, override_local=None):
    """
    Run `CERMINE <https://github.com/CeON/CERMINE>`_ to extract DOIs of cited \
            papers from a PDF file.

    .. note::

        Try to use a local CERMINE JAR file, and falls back to using the API. \
                JAR file is expected to be found in \
                ``libbmc/external/cermine.jar``. You can override this using \
                the ``override_local`` parameter.

    .. note::

        CERMINE JAR file can be found at \
                `<http://maven.icm.edu.pl/artifactory/simple/kdd-releases/pl/edu/icm/cermine/cermine-impl/>`_.

    .. note::

        This fallback using the \
                `CERMINE API <http://cermine.ceon.pl/about.html>`_, and \
                hence, uploads the PDF file (so uses network). Check out \
                the CERMINE API terms.

    .. note::

        This function uses CERMINE to extract references from the paper, and \
                try to match them on Crossref to get DOIs.

    :param pdf_file: Path to the PDF file to handle.
    :param force_API: Force the use of the Cermine API \
            (and do not try to use a local JAR file). Defaults to ``False``.
    :param override_local: Use this specific JAR file, instead of the one at \
            the default location (``libbmc/external/cermine.jar``).
    :returns: A dict of cleaned plaintext citations and their associated DOI.
    """
    # TODO
    pass


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
