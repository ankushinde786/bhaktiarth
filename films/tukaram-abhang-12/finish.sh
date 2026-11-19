#!/usr/bin/env bash
# usage (inside the project folder, after both halves finished): bash finish.sh <N> <first_half_file> <second_half_file>
#   e.g.  bash finish.sh 9 part_00000.mp4 part_00994.mp4
# Joins the two halves, muxes out/mix.wav (AAC 192k, 48 kHz), checks the length, and makes <name>_share.mp4 (~1900 kb/s) if the file is over 30 MiB.
set -e
N=$1; A=$2; B=$3; NAME=tukaram-abhang-$N
printf "file '%s'\nfile '%s'\n" "$A" "$B" > out/list.txt
(cd out && ffmpeg -y -loglevel error -f concat -safe 0 -i list.txt -c copy v.mp4)
ffmpeg -y -loglevel error -i out/v.mp4 -i out/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest $NAME.mp4
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height -of default=nw=1 $NAME.mp4
SZ=$(stat -c %s $NAME.mp4); echo "size: $((SZ/1048576)) MiB"
if [ $SZ -gt 31457280 ]; then ffmpeg -y -loglevel error -i $NAME.mp4 -c:v libx264 -preset veryfast -b:v 1900k -maxrate 2200k -bufsize 4000k -pix_fmt yuv420p -c:a aac -b:a 128k ${NAME}_share.mp4; ls -l ${NAME}_share.mp4; fi
cat out/levels.txt | tail -3
