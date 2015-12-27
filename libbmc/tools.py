"""
This file contains various utility functions.
"""


def replaceAll(text, replace_dict):
    """
    Replace multiple strings in a text.

    :param text: Text to replace in.
    :param replace_dict: Dictionary mapping strings to replace with their \
            substitution.
    :returns: Text after replacements.
    """
    for i, j in replace_dict.items():
        text = text.replace(i, j)
    return text


def clean_whitespaces(text):
    """
    Remove multiple whitespaces from text.

    :param text: Text to remove multiple whitespaces from.
    :returns: A cleaned text.
    """
    return ' '.join(text.strip().split())


def remove_duplicates(some_list):
    """
    Remove the duplicates from a list.

    :param some_list: List to remove duplicates from.
    :returns: A list without duplicates.
    """
    return list(set(some_list))
