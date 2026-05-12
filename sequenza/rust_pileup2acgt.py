# This file is part of sequenza-utils.
# SPDX-License-Identifier: GPL-3.0-only

import os
import subprocess
from pathlib import Path


def _binary_path():
    suffix = ".exe" if os.name == "nt" else ""
    return Path(__file__).with_name("_rust_pileup2acgt%s" % suffix)


def _source_path():
    return Path(__file__).with_name("rust") / "pileup2acgt.rs"


def _ensure_binary():
    binary = _binary_path()
    source = _source_path()
    if binary.exists() and binary.stat().st_mtime >= source.stat().st_mtime:
        return str(binary)
    try:
        subprocess.check_call(
            ["rustc", "-O", str(source), "-o", str(binary)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return str(binary)


def can_run(mpileup, output):
    if os.environ.get("SEQUENZA_DISABLE_RUST"):
        return False
    return not (mpileup.endswith(".gz") or output.endswith(".gz"))


def run(mpileup, output, min_depth, qlimit, noend=False, nostart=False):
    if not can_run(mpileup, output):
        return False
    binary = _ensure_binary()
    if binary is None:
        return False
    try:
        subprocess.check_call(
            [
                binary,
                mpileup,
                output,
                str(min_depth),
                str(qlimit),
                "1" if noend else "0",
                "1" if nostart else "0",
            ]
        )
    except subprocess.CalledProcessError:
        return False
    return True
