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

On a full `chr20` run from the public 1000 Genomes HG03007 CRAM, the Rust path
processed the same mpileup stream 8.53x faster than the Python fallback:

```
python: 456.00s
rust:    53.45s
speedup: 8.53x
```

See [OPTIMIZATION.md](OPTIMIZATION.md) for the implementation details and
benchmark procedure.

Using the Rust path
-------------------

Install Rust first. On macOS with Homebrew:

```
brew install rust
```

Then install this fork in a local virtual environment:

```
git clone https://github.com/dogaegirlyutmo/sequenza-utils-optimized.git
cd sequenza-utils-optimized
python3.11 -m venv .venv
.venv/bin/python -m pip install --no-build-isolation -e .
```

Run `pileup2acgt` normally:

```
.venv/bin/sequenza-utils pileup2acgt --mpileup input.mpileup -o output.acgt
```

The Rust implementation is used automatically when:

- `rustc` is available;
- the input and output are uncompressed, non-`.gz` paths;
- `SEQUENZA_DISABLE_RUST` is not set.

The command falls back to the Python implementation for gzip input/output or
when Rust compilation/execution is unavailable. To force the Python path:

```
SEQUENZA_DISABLE_RUST=1 .venv/bin/sequenza-utils pileup2acgt --mpileup input.mpileup -o output.acgt
```

To run the benchmark:

```
./benchmarks/bench_pileup2acgt.sh
```

>The package uses external software that needs to be installed separately:
> `samtools` >= 1.3.1 and `tabix`.
>
> In order to run the testing suite `bwa` >= 0.7.12 is required


Install
-------

**From PyPI**

```
pip install sequenza-utils
```

The PyPI package is the upstream `sequenza-utils` release and may not include
the Rust-accelerated `pileup2acgt` changes from this fork.

**From this fork**

```
pip install git+https://github.com/dogaegirlyutmo/sequenza-utils-optimized.git
```

**From Sources**

For development and local testing, use an editable install:

```
git clone https://github.com/dogaegirlyutmo/sequenza-utils-optimized.git
cd sequenza-utils-optimized
python3.11 -m venv .venv
.venv/bin/python -m pip install --no-build-isolation -e .
```

Check the CLI:

```
.venv/bin/sequenza-utils --help
```

Build extension artifacts in place:

```
.venv/bin/python setup.py build_ext --inplace
```

Run the benchmark for the Rust-accelerated `pileup2acgt` path:

```
./benchmarks/bench_pileup2acgt.sh
```

The full test suite uses `unittest` and requires external tools such as
`samtools`, `tabix`, and `bwa`:

```
.venv/bin/python -m unittest discover test
```

Docs
----

Documentation and more details are available at [Read the Docs](http://sequenza-utils.readthedocs.io)
