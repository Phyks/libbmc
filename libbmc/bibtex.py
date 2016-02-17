"""
This file contains functions to deal with Bibtex files and edit them.

TODO: Unittests
"""
import re

import bibtexparser

from libbmc import tools


DEFAULT_PAPERS_FILENAME_MASK = "{first}_{last}-{journal}-{year}{arxiv_version}"
DEFAULT_BOOKS_FILENAME_MASK = "{authors} - {title}"


def dict2bibtex(data):
    """
    Convert a single BibTeX entry dict to a BibTeX string.

    :param data: A dict representing BibTeX entry, as the ones from \
            ``bibtexparser.BibDatabase.entries`` output.
    :return: A formatted BibTeX string.
    """
    bibtex = '@' + data['ENTRYTYPE'] + '{' + data['ID'] + ",\n"

    for field in [i for i in sorted(data) if i not in ['ENTRYTYPE', 'ID']]:
        bibtex += "\t" + field + "={" + data[field] + "},\n"
    bibtex += "}\n\n"
    return bibtex


def bibdatabase2bibtex(data):
    """
    Convert a BibDatabase object to a BibTeX string.

    :param data: A ``bibtexparser.BibDatabase`` object.
    :return: A formatted BibTeX string.
    """
    return bibtexparser.dumps(data)


def write(filename, data):
    """
    Create a new BibTeX file.

    :param filename: The name of the BibTeX file to write.
    :param data: A ``bibtexparser.BibDatabase`` object.
    """
    with open(filename, 'w') as fh:
        fh.write(bibdatabase2bibtex(data))


def append(filename, data):
    """
    Append some entries to a bibtex file.

    :param filename: The name of the BibTeX file to edit.
    :param data: A ``bibtexparser.BibDatabase`` object.
    """
    with open(filename, 'a') as fh:
        fh.write(bibdatabase2bibtex(data))


def edit(filename, identifier, data):
    """
    Update an entry in a BibTeX file.

    :param filename: The name of the BibTeX file to edit.
    :param identifier: The id of the entry to update, in the BibTeX file.
    :param data: A dict associating fields and updated values. Fields present \
            in the BibTeX file but not in this dict will be kept as is.
    """
    # Get current bibtex
    with open(filename, 'r') as fh:
        bibtex = bibtexparser.load(fh)

    # Update it
    # TODO: Not working
    bibtex.entries_dict[identifier] = data.entries[0]

    # Write the resulting BibTeX
    write(filename, bibtex)


def replace(filename, identifier, data):
    """
    Replace an entry in a BibTeX file.

    :param filename: The name of the BibTeX file to edit.
    :param identifier: The id of the entry to replace, in the BibTeX file.
    :param data: A ``bibtexparser.BibDatabase`` object containing a single \
            entry.
    """
    # Get current bibtex
    with open(filename, 'r') as fh:
        bibtex = bibtexparser.load(fh)

    # Use entries_dict representation to update easily
    # TODO: Not working
    bibtex.entries_dict[identifier] = data.entries[0]

    # Write the resulting BibTeX
    write(filename, bibtex)


def delete(filename, identifier):
    """
    Delete an entry in a BibTeX file.

    :param filename: The name of the BibTeX file to edit.
    :param identifier: The id of the entry to delete, in the BibTeX file.
    """
    # Get current bibtex
    with open(filename, 'r') as fh:
        bibtex = bibtexparser.load(fh)

    # Delete the bibtex entry
    # TODO: Not working
    try:
        del bibtex.entries_dict[identifier]
    except KeyError:
        pass

    # Write the resulting BibTeX
    write(filename, bibtex)


def get(filename, ignore_fields=None):
    """
    Get all entries from a BibTeX file.

    :param filename: The name of the BibTeX file.
    :param ignore_fields: An optional list of fields to strip from the BibTeX \
            file.

    :returns: A ``bibtexparser.BibDatabase`` object representing the fetched \
            entries.
    """
    # Handle default argument
    if ignore_fields is None:
        ignore_fields = []

    # Open bibtex file
    with open(filename, 'r') as fh:
        bibtex = bibtexparser.load(fh)

    # Clean the entries if necessary
    bibtex.entries = [{k: entry[k]
                       for k in entry if k not in ignore_fields}
                      for entry in bibtex.entries]

    return bibtex


def get_entry_by_filter(filename, filter_function, ignore_fields=None):
    """
    Get an entry from a BibTeX file.

    .. note ::

        Returns the first matching entry.

    :param filename: The name of the BibTeX file.
    :param filter_function: A function returning ``True`` or ``False`` \
            whether the entry should be included or not.
    :param ignore_fields: An optional list of fields to strip from the BibTeX \
            file.

    :returns: A ``bibtexparser.BibDatabase`` object representing the \
            first matching entry. ``None`` if entry was not found.
    """
    # Handle default argument
    if ignore_fields is None:
        ignore_fields = []

    # Open bibtex file
    with open(filename, 'r') as fh:
        bibtex = bibtexparser.load(fh)

    matching_entry = None
    try:
        # Try to fetch the matching entry dict
        for entry in bibtex.entries:
            if filter_function(entry):
                matching_entry = entry
    except KeyError:
        # If none found, return None
        return None

    if matching_entry is None:
        return None

    # Clean the entry dict if necessary
    matching_entry = {k: matching_entry[k]
                      for k in matching_entry if k not in ignore_fields}

    bib_db = bibtexparser.bibdatabase.BibDatabase()
    bib_db.entries = [matching_entry]
    return bib_db


def get_entry(filename, identifier, ignore_fields=None):
    """
    Get an entry from a BibTeX file.

    :param filename: The name of the BibTeX file.
    :param identifier: An id of the entry to fetch, in the BibTeX file.
    :param ignore_fields: An optional list of fields to strip from the BibTeX \
            file.

    :returns: A ``bibtexparser.BibDatabase`` object representing the \
            fetched entry. ``None`` if entry was not found.
    """
    # Handle default argument
    if ignore_fields is None:
        ignore_fields = []

    return get_entry_by_filter(filename,
                               lambda x: x["ID"] == identifier,
                               ignore_fields)


def to_filename(data,
                mask=DEFAULT_PAPERS_FILENAME_MASK,
                extra_formatters=None):
    """
    Convert a bibtex entry to a formatted filename according to a given mask.

    .. note ::

        Available formatters out of the box are:
            - ``journal``
            - ``title``
            - ``year``
            - ``first`` for the first author
            - ``last`` for the last author
            - ``authors`` for the list of authors
            - ``arxiv_version`` (discarded if no arXiv version in the BibTeX)

        Filename is slugified after applying the masks.

    :param data: A ``bibtexparser.BibDatabase`` object representing a \
            BibTeX entry, as the one from ``bibtexparser`` output.
    :param mask: A Python format string.
    :param extra_formatters: A dict of format string (in the mask) and \
            associated lambdas to perform the formatting.

    :returns: A formatted filename.
    """
    # Handle default argument
    if extra_formatters is None:
        extra_formatters = {}

    entry = data.entries[0]
    authors = re.split(' and ', entry['author'])

    formatters = {
        "journal": "",
        "title": "",
        "year": "",
        "first": "",
        "last": "",
        "authors": "",
        "arxiv_version": ""
    }

    formatters["journal"] = entry.get("journal", "")
    formatters["title"] = entry.get("title", "")
    formatters["year"] = entry.get("year", "")

    formatters["first"] = authors[0].split(',')[0].strip()
    formatters["last"] = authors[-1].split(',')[0].strip()
    formatters["authors"] = ", ".join([i.split(',')[0].strip()
                                       for i in authors])

    for extra_formatter in extra_formatters:
        formatters[extra_formatter] = extra_formatters[extra_formatter](entry)

    arxiv_version = ""
    if "eprint" in entry:
        arxiv_version = '-' + entry['eprint'][entry['eprint'].rfind('v'):]
    formatters["arxiv_version"] = arxiv_version

    return tools.slugify(mask.format(**formatters))
