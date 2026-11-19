#!/usr/bin/env bash
# usage: tools/new_abhang.sh <N> [path/to/voice.wav] [path/to/script.txt]
# Creates films/tukaram-abhang-N/ with the engine, builds out/assets.npz from the Vitthal reference (about 12 s, 140 MB, git-ignored)
# and, when given, copies in the voice and script. Run from the skill folder or from the repo root; films/ is created next to the skill folder.
set -e
N=$1; [ -z "$N" ] && { echo "usage: new_abhang.sh N [voice.wav] [script.txt]"; exit 1; }
SK="$(cd "$(dirname "$0")/.." && pwd)"; FILMS="${FILMS_DIR:-$SK/../../films}"; P="$FILMS/tukaram-abhang-$N"
mkdir -p "$P/out" "$P/sb"
for f in render.py mix.py align.py mksrt.py prep.py board.py; do [ -f "$P/$f" ] || cp "$SK/engine/$f" "$P/$f"; done
[ -f "$P/out/assets.npz" ] || (cd "$P" && python3 -I prep.py "$SK/assets/vitthal_reference.png")
[ -n "$2" ] && cp "$2" "$P/voice.wav"
[ -n "$3" ] && cp "$3" "$P/script.txt"
grep -qs "assets.npz" "$FILMS/.gitignore" || printf "*/out/\n*.mp4\n" >> "$FILMS/.gitignore"
echo "project: $P"
