#!/bin/bash

me=$(realpath -e "$0")
dr=$(dirname "$me")
cd "$dr" || { echo "Cannot cd ${dr@Q}."; exit 1; }>&2
[ -f test.rpsl ] || { echo "No test file."; exit 1; }>&2
exec python3 -m rpsl test.rpsl

# EOF #
