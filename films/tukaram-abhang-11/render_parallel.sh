#!/usr/bin/env bash
set -e
cd /workspaces/bhaktiarth/films/tukaram-abhang-11
python3 -I render.py video 0 38.07 > out/r1.log 2>&1 &
PID1=$!
python3 -I render.py video 38.07 76.14 > out/r2.log 2>&1 &
PID2=$!
echo "Running parallel render: PID1=$PID1, PID2=$PID2"
wait $PID1
echo "Half 1 finished"
wait $PID2
echo "Half 2 finished"
echo "both halves done"
