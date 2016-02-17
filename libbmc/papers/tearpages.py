"""
This file contains the necessary functions to determine whether we should tear
the first page from a PDF file, and actually tear it.

TODO: Unittests
"""
import shutil
import tempfile
from PyPDF2 import PdfFileWriter, PdfFileReader
from PyPDF2.utils import PdfReadError


# Dict of bad journals which adds an extra useless first page, which can be
# teared. Please, submit a PR to include new ones which I may not be aware of!
# This dict associates the journal string to look for and to a list of pages
# to tear.
BAD_JOURNALS = {
    "epl": [0],
    "journal of modern optics": [0],
    "new journal of physics": [0]
}


def fix_pdf(pdf_file, destination):
    """
    Fix malformed pdf files when data are present after '%%EOF'

    ..note ::

        Originally from sciunto, https://github.com/sciunto/tear-pages

    :param pdfFile: PDF filepath
    :param destination: destination
    """
    tmp = tempfile.NamedTemporaryFile()
    with open(tmp.name, 'wb') as output:
        with open(pdf_file, "rb") as fh:
            for line in fh:
                output.write(line)
                if b'%%EOF' in line:
                    break
    shutil.copy(tmp.name, destination)


def tearpage_backend(filename, teared_pages=None):
    """
    Copy filename to a tempfile, write pages to filename except the teared one.

    ..note ::

        Adapted from sciunto's code, https://github.com/sciunto/tear-pages

    :param filename: PDF filepath
    :param teared_pages: Numbers of the pages to tear. Default to first page \
            only.
    """
    # Handle default argument
    if teared_pages is None:
        teared_pages = [0]

    # Copy the pdf to a tmp file
    with tempfile.NamedTemporaryFile() as tmp:
        # Copy the input file to tmp
        shutil.copy(filename, tmp.name)

        # Read the copied pdf
        # TODO: Use with syntax
        try:
            input_file = PdfFileReader(open(tmp.name, 'rb'))
        except PdfReadError:
            fix_pdf(filename, tmp.name)
            input_file = PdfFileReader(open(tmp.name, 'rb'))
        # Seek for the number of pages
        num_pages = input_file.getNumPages()

        # Write pages excepted the first one
        output_file = PdfFileWriter()
        for i in range(num_pages):
            if i in teared_pages:
                continue
            output_file.addPage(input_file.getPage(i))

        tmp.close()
        outputStream = open(filename, "wb")
        output_file.write(outputStream)


def tearpage_needed(bibtex):
    """
    Check whether a given paper needs some pages to be teared or not.

    :params bibtex: The bibtex entry associated to the paper, to guess \
            whether tearing is needed.
    :returns: A list of pages to tear.
    """
    for publisher in BAD_JOURNALS:
        if publisher in bibtex.get("journal", "").lower():
            # Bad journal is found, add pages to tear
            return BAD_JOURNALS[publisher]

    # If no bad journals are found, return an empty list
    return []


def tearpage(filename, bibtex=None, force=None):
    """
    Tear some pages of the file if needed.

    :params filename: Path to the file to handle.
    :params bibtex: BibTeX dict associated to this file, as the one given by \
            ``bibtexparser``. (Mandatory if force is not specified)
    :params force: If a list of integers, force the tearing of the \
            specified pages. (Optional)
    :returns: A boolean indicating whether the file has been teared or not. \
            Side effect is tearing the necessary pages from the file.
    """
    # Fetch pages to tear
    pages_to_tear = []
    if force is not None:
        pages_to_tear = force
    elif bibtex is not None:
        pages_to_tear = tearpage_needed(bibtex)

    if len(pages_to_tear) > 0:
        # If tearing is needed, do it and return True
        tearpage_backend(filename, teared_pages=pages_to_tear)
        return True

    # Else, simply return False
    return False
