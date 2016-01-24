"""
This file contains various utility functions.
"""
import re
import unicodedata

from itertools import islice, chain


# Huge URL regex taken from https://gist.github.com/gruber/8891611
URL_REGEX = re.compile(r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))")


def replaceAll(text, replace_dict):
    """
    Replace multiple strings in a text.


    .. note::

        Replacements are made successively, without any warranty on the order \
        in which they are made.

    :param text: Text to replace in.
    :param replace_dict: Dictionary mapping strings to replace with their \
            substitution.
    :returns: Text after replacements.

    >>> replaceAll("foo bar foo thing", {"foo": "oof", "bar": "rab"})
    'oof rab oof thing'
    """
    for i, j in replace_dict.items():
        text = text.replace(i, j)
    return text


def clean_whitespaces(text):
    """
    Remove multiple whitespaces from text. Also removes leading and trailing \
    whitespaces.

    :param text: Text to remove multiple whitespaces from.
    :returns: A cleaned text.

    >>> clean_whitespaces("this  is    a text with    spaces")
    'this is a text with spaces'
    """
    return ' '.join(text.strip().split())


def remove_duplicates(some_list):
    """
    Remove the duplicates from a list.

    :param some_list: List to remove duplicates from.
    :returns: A list without duplicates.

    >>> remove_duplicates([1, 2, 3, 1])
    [1, 2, 3]

    >>> remove_duplicates([1, 2, 1, 2])
    [1, 2]
    """
    return list(set(some_list))


def batch(iterable, size):
    """
    Get items from a sequence a batch at a time.

    .. note:

        Adapted from
        https://code.activestate.com/recipes/303279-getting-items-in-batches/.


    .. note:

        All batches must be exhausted immediately.

    :params iterable: An iterable to get batches from.
    :params size: Size of the batches.
    :returns: A new batch of the given size at each time.

    >>> [list(i) for i in batch([1, 2, 3, 4, 5], 2)]
    [[1, 2], [3, 4], [5]]
    """
    it = iter(iterable)
    while True:
        bi = islice(it, size)
        yield chain([next(bi)], bi)


def remove_URLs(text):
    """
    Remove URLs from a given text (only removes http, https and naked domains \
    URLs).

    :param text: The text to remove URLs from.
    :returns: The text without URLs.

    >>> remove_URLs("foobar http://example.com https://example.com foobar")
    'foobar foobar'
    """
    return clean_whitespaces(URL_REGEX.sub("", text))


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[\s]+')


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens to have nice filenames.

    From Django's "django/template/defaultfilters.py".

    >>> slugify("El pingüino Wenceslao hizo kilómetros bajo exhaustiva lluvia y frío, añoraba a su querido cachorro. ortez ce vieux whisky au juge blond qui fume sur son île intérieure, à Γαζέες καὶ μυρτιὲς δὲν θὰ βρῶ πιὰ στὸ χρυσαφὶ ξέφωτο いろはにほへとちりぬるを Pchnąć w tę łódź jeża lub ośm skrzyń fig กว่าบรรดาฝูงสัตว์เดรัจฉาน")
    'El_pinguino_Wenceslao_hizo_kilometros_bajo_exhaustiva_lluvia_y_frio_anoraba_a_su_querido_cachorro_ortez_ce_vieux_whisky_au_juge_blond_qui_fume_sur_son_ile_interieure_a_Pchnac_w_te_odz_jeza_lub_osm_skrzyn_fig'
    """
    try:
        unicode_type = unicode
    except NameError:
        unicode_type = str
    if not isinstance(value, unicode_type):
        value = unicode_type(value)
    value = (unicodedata.normalize('NFKD', value).
             encode('ascii', 'ignore').decode('ascii'))
    value = unicode_type(_slugify_strip_re.sub('', value).strip())
    return _slugify_hyphenate_re.sub('_', value)
