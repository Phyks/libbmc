# Global list of valid paper identifier types. See README.md.
__valid_identifiers__ = []

# Import order of the modules is important, as they will populate
# `__valid_identifiers__` on load, and the order in this list reflects their
# priority.
from . import bibtex, doi, fetcher, isbn  # noqa
from . import citations, papers, repositories  # noqa

__version__ = "0.1.2"

__all__ = [
    "bibtex", "doi", "fetcher", "isbn",
    "citations", "papers", "repositories",
]
