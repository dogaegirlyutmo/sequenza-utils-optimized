# This file is part of sequenza-utils.
# SPDX-License-Identifier: GPL-3.0-only

import argparse
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def write_input(path, rows):
    line = "chr1\t{}\tC\t20\tAAAAAAAAAAAAAAAAAAAA\tIIIIIIIIIIIIIIIIIIII\n"
    with path.open("w") as out:
        for index in range(1, rows + 1):
            out.write(line.format(index))


def timed_run(command, env=None):
    start = time.perf_counter()
    subprocess.check_call(command, env=env)
    return time.perf_counter() - start


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=500000)
    parser.add_argument("--min-speedup", type=float, default=3.0)
    parser.add_argument(
        "--sequenza",
        default=str(Path(__file__).resolve().parents[2] / ".venv/bin/sequenza-utils"),
    )
    args = parser.parse_args(argv)

    tmpdir = Path(tempfile.gettempdir())
    mpileup = tmpdir / "sequenza_bench.mpileup"
    python_out = tmpdir / "sequenza_bench.python.tsv"
    rust_out = tmpdir / "sequenza_bench.rust.tsv"
    warmup = tmpdir / "sequenza_bench.warmup.tsv"
    write_input(mpileup, args.rows)

    subprocess.check_call(
        [args.sequenza, "pileup2acgt", "--mpileup", str(mpileup), "-o", str(warmup)]
    )

    disabled_env = os.environ.copy()
    disabled_env["SEQUENZA_DISABLE_RUST"] = "1"
    python_time = timed_run(
        [args.sequenza, "pileup2acgt", "--mpileup", str(mpileup), "-o", str(python_out)],
        env=disabled_env,
    )
    rust_time = timed_run(
        [args.sequenza, "pileup2acgt", "--mpileup", str(mpileup), "-o", str(rust_out)]
    )

    if python_out.read_bytes() != rust_out.read_bytes():
        raise SystemExit("benchmark outputs differ")

    speedup = python_time / rust_time
    print("rows: %d" % args.rows)
    print("python: %.3fs" % python_time)
    print("rust: %.3fs" % rust_time)
    print("speedup: %.2fx" % speedup)
    if speedup < args.min_speedup:
        raise SystemExit(
            "speedup %.2fx is below required %.2fx" % (speedup, args.min_speedup)
        )


if __name__ == "__main__":
    main(sys.argv[1:])
