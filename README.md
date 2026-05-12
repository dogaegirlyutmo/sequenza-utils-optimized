[![codecov](https://codecov.io/bb/sequenzatools/sequenza-utils/branch/master/graph/badge.svg)](https://codecov.io/bb/sequenza_tools/sequenza-utils)
[![pypi](https://img.shields.io/pypi/v/sequenza-utils.svg)](https://pypi.python.org/pypi/sequenza-utils)
![pypi](https://img.shields.io/pypi/status/sequenza-utils.svg)
![license](https://img.shields.io/pypi/l/sequenza-utils.svg)
![pyversions](https://img.shields.io/pypi/pyversions/sequenza-utils.svg)
![implement](https://img.shields.io/pypi/implementation/sequenza-utils.svg)

![Sequenza_utils_logo](https://bytebucket.org/sequenzatools/icons/raw/324bd43ac4d10546b64b04c38d8c513e8420346d/png/sequenza-utils/sequenzapython_150.png)

Sequenza-utils
==============

Analysis of cancer sequencing samples, utilities for the R package sequenza

Rust-accelerated pileup2acgt
----------------------------

This fork adds an optional Rust fast path for `sequenza-utils pileup2acgt` when
reading and writing uncompressed mpileup data. The command keeps the original
Python implementation as a fallback for gzip files and systems where `rustc` is
unavailable.

The optimization moves the hot pileup base-counting loop into a small compiled
Rust binary while preserving the existing command-line interface and output
format. A local benchmark over 500,000 synthetic mpileup rows measured:

```
python: 3.207s
rust:   0.255s
speedup: 12.58x
```

See [OPTIMIZATION.md](OPTIMIZATION.md) for the implementation details and
benchmark procedure.

>The package uses external software that needs to be installed separately:
> `samtools` >= 1.3.1 and `tabix`.
>
> In order to run the testing suite `bwa` >= 0.7.12 is required


Install
-------

**From Pypi**

```
pip install sequenza-utils
```

or pulling the latest version from git:

```
pip install git+ssh://git@bitbucket.org/sequenzatools/sequenza-utils.git
```

**From Sources**

Installing from sources using the `setup.py` script it's not recommended, instead you could use `pip`
as described above.

However, while developing and testing new functionalities you could use:


```
git clone https://bitbucket.org/sequenzatools/sequenza-utils
pip install ./sequenza-utils
```

or with `setup.py`


```
git clone https://bitbucket.org/sequenzatools/sequenza-utils
cd sequenza-utils
python setup.py test
python setup.py install
```

Docs
----

Documentation and more details are available at [Read the Docs](http://sequenza-utils.readthedocs.io)
