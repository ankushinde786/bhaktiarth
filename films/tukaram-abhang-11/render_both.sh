#!/usr/bin/env bash
cd /workspaces/bhaktiarth/films/tukaram-abhang-11
setsid nohup python3 -I render.py video 0 38.07 > /workspaces/bhaktiarth/films/tukaram-abhang-11/out/r1.log 2>&1 &
setsid nohup python3 -I render.py video 38.07 76.14 > /workspaces/bhaktiarth/films/tukaram-abhang-11/out/r2.log 2>&1 &
echo "renders launched"
