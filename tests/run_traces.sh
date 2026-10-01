#!/bin/sh
# Rebuild every toy program here and write its trace next to it: ./run_traces.sh [name ...]
cd "$(dirname "$0")"
for c in ${@:-*.c}; do
  p=$(basename "$c" .c)
  gcc -g -O0 -o "$p" "$p.c" && gdb -q -nx -batch -x ../trace.py "./$p" 2>&1 | grep wrote
  rm -f "$p" prog_stdout.txt
done
