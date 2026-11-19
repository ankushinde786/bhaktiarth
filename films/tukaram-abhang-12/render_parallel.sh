#!/usr/bin/env bash
set -e
cd /workspaces/bhaktiarth/films/tukaram-abhang-12
python3 -I render.py video 0 38.23 > out/r1.log 2>&1 &
PID1=$!
python3 -I render.py video 38.23 76.46 > out/r2.log 2>&1 &
PID2=$!
echo "Running parallel render: PID1=$PID1, PID2=$PID2"
wait $PID1
echo "Half 1 finished"
wait $PID2
echo "Half 2 finished"
echo "both halves done"
