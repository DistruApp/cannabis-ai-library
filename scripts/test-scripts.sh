#!/usr/bin/env bash
# Gate 2: script tests. Standard library only. See RELEASING.md.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -t . "$@"
