# pileup2acgt optimization notes

## Summary

This fork optimizes the `sequenza-utils pileup2acgt` command by adding a
Rust-accelerated path for uncompressed mpileup input/output. The original
Python implementation remains available and is used automatically when the Rust
path is not suitable.

## What changed

- Added `sequenza/rust/pileup2acgt.rs`, a small Rust implementation of the
  mpileup parsing and A/C/G/T counting loop.
- Added `sequenza/rust_pileup2acgt.py`, a Python wrapper that compiles and
  invokes the Rust binary when possible.
- Updated `sequenza/programs/pileup2acgt.py` to try the Rust path first and
  fall back to the existing Python implementation if Rust cannot run.
- Updated packaging so the Rust source is included in source distributions and
  the binary is built during `build_py` when `rustc` is available.
- Added benchmark tooling in `benchmarks/` to compare the Rust and Python
  outputs and enforce a minimum speedup threshold.

## How the optimization works

The previous implementation processed every mpileup row in Python and called
the Python `acgt` parser for each pileup base string. That loop is CPU-heavy:
it walks compact mpileup syntax, handles read-start and read-end markers,
skips insertion/deletion payloads, applies base-quality thresholds, normalizes
forward and reverse strand bases, and writes per-position base counts.

The optimized path keeps Python as the CLI entry point, but moves that hot loop
to Rust:

1. `pileup2acgt.py` parses arguments exactly as before.
2. `rust_pileup2acgt.run(...)` checks whether Rust acceleration is allowed.
3. The Rust binary is compiled with `rustc -O` if it is missing or stale.
4. The Rust binary streams the input file, performs the base counting, and
   writes the same tab-separated output format as the Python path.
5. If compilation or execution fails, the command silently uses the Python
   fallback to preserve existing behavior.

The Rust path is intentionally limited to uncompressed data. Gzip inputs and
outputs still use the Python fallback, which keeps compatibility with the
existing `xopen` behavior.

## Benchmark method

Benchmark script:

```bash
./benchmarks/bench_pileup2acgt.sh
```

The benchmark:

- generates a synthetic mpileup file with 500,000 rows;
- runs the command once as a warmup;
- runs the Python fallback with `SEQUENZA_DISABLE_RUST=1`;
- runs the Rust-accelerated path;
- compares the Python and Rust output bytes for exact equality;
- reports the speedup and fails if it is below the configured threshold.

## Measured result

Run date: 2026-05-13

Environment:

- macOS 26.2
- arm64
- Python 3.11.14
- rustc 1.93.1
- benchmark rows: 500,000

Result:

```text
rows: 500000
python: 3.207s
rust: 0.255s
speedup: 12.58x
```

This run shows a 12.58x speedup for the benchmarked `pileup2acgt` workload,
with byte-identical output between the Python fallback and Rust path.

## Compatibility notes

- Disable the Rust path with `SEQUENZA_DISABLE_RUST=1`.
- If `rustc` is not installed, the command uses the Python path.
- If the input or output path ends with `.gz`, the command uses the Python path.
- The command-line interface and output columns are unchanged.
