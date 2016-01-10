"""
This file contains all the HAL-related functions.

TODO:
    * Add functions to homogeneize interface with arXiv one.
"""
import re

from libbmc import tools


REGEX = re.compile(r"(hal-\d{8}), version (\d+)")


def is_valid(hal_id):
    """
    Check that a given HAL id is a valid one.

    :param hal_id: The HAL id to be checked.
    :returns: Boolean indicating whether the HAL id is valid or not.
    """
    match = REGEX.match(hal_id)
    return ((match is not None) and (match.group(0) == hal_id))


def extract_from_text(text):
    """
    Extract HAL ids from a text.

    :param text: The text to extract HAL ids from.
    :returns: A list of matching HAL ids.
    """
    return tools.remove_duplicates(REGEX.findall(text))
