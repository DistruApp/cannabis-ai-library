#!/usr/bin/env bash
# Copies this case's fixtures into ./resources in the eval workspace (run with --scaffold).
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p resources
cp "$here"/resources/* resources/
