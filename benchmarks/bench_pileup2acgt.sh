#!/usr/bin/env bash
# This file is part of sequenza-utils.
# SPDX-License-Identifier: GPL-3.0-only
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$ROOT/../.venv/bin/python" "$ROOT/benchmarks/bench_pileup2acgt.py" "$@"
