libBMC
======

A generic Python library to manage bibliography and play with scientific
papers.


_Note_: This library is written for Python 3 and may not work with Python 2.
This is not a major priority for me, but if anyone needed to make it work with
Python 2 and want to make a PR, I will happily merge it :)


## Dependencies

Python dependencies are listed in the `requirements.txt` file at the root of
this repo, and can be installed with `pip install -r requirements.txt`.


External dependencies are [OpenDeTeX](https://code.google.com/p/opendetex/)
(an improved version of DeTeX) and the `pdftotext` and `djvutxt` programs.


OpenDeTeX is available as a Git submodule in the `libbmc/external` folder. If
you do not have it installed system-wide, you can use the following steps to
build it in this repo and the library will use it:

* `git submodule init; git submodule update` to initialize the Git submodules.
* `cd libbmc/external/opendetex; make` to build OpenDeTeX (see `INSTALL` file
  in the same folder for more info, you will need `make`, `gcc` and `flex` to
  build it).

OpenDeTeX is used to get references from a `.bbl` file (or directly from arXiv
as it uses the same pipeline).


`pdftotext` and `djvutxt` should be available in the packages of your
distribution and should be installed systemwide. Both are used to extract
identifiers from papers PDF files.


If you plan on using the `libbmc.citations.pdf` functions, you should also
install the matching software (`CERMINE`, `Grobid` or `pdf-extract`). See the
docstrings of those functions for more infos on this particular point.
