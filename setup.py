from setuptools import setup, Extension
from setuptools.command.build_py import build_py
from sequenza import __version__
import os
import shutil
import subprocess
import sys

# import os
# os.environ['CC'] = 'g++-7'
# os.environ['CXX'] = 'g++-7'

install_requires = []

if sys.version_info < (2, 7):
    raise Exception("sequenza-utils requires Python 2.7 or higher.")

try:
    import argparse
except ImportError:
    install_requires.append("argparse")


def list_lines(comment):
    for line in comment.strip().split("\n"):
        yield line.strip()


class build_py_with_rust(build_py):
    def run(self):
        build_py.run(self)
        rustc = shutil.which("rustc")
        if rustc is None:
            return
        source = os.path.join("sequenza", "rust", "pileup2acgt.rs")
        target_dir = os.path.join(self.build_lib, "sequenza")
        target = os.path.join(target_dir, "_rust_pileup2acgt")
        if os.name == "nt":
            target += ".exe"
        try:
            subprocess.check_call([rustc, "-O", source, "-o", target])
        except (OSError, subprocess.CalledProcessError):
            pass


classifier_text = """
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    Intended Audience :: Science/Research
    Intended Audience :: Healthcare Industry
    Operating System :: OS Independent
    License :: OSI Approved :: GNU General Public License v3 (GPLv3)
    Programming Language :: C
    Programming Language :: Python
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: 3.5
    Programming Language :: Python :: 3.6
    Programming Language :: Python :: Implementation :: CPython
    Programming Language :: Python :: Implementation :: PyPy
    Topic :: Scientific/Engineering :: Bio-Informatics
    Topic :: Utilities
"""

setup(
    name="sequenza-utils",
    version=__version__.VERSION,
    description=(
        "Analysis of cancer sequencing samples, " "utilities for the sequenza R package"
    ),
    long_description=open("README.txt").read(),
    author=__version__.AUTHOR,
    author_email=__version__.EMAIL,
    url=__version__.WEBSITE,
    license="GPLv3",
    packages=["sequenza", "sequenza.programs"],
    package_data={"sequenza": ["rust/*.rs"]},
    cmdclass={"build_py": build_py_with_rust},
    ext_modules=[
        Extension(
            "sequenza.c_pileup",
            sources=["sequenza/src/parsers.c", "sequenza/src/pileup.c"],
        )
    ],
    test_suite="test",
    entry_points={"console_scripts": ["sequenza-utils = sequenza.commands:main"]},
    install_requires=install_requires,
    classifiers=list(list_lines(classifier_text)),
    keywords="bioinformatics cancer tumor NGS sequencing",
)
