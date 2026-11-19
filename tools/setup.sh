#!/usr/bin/env bash
# One-time setup + check for GitHub Codespaces / any Debian-Ubuntu box. Safe to re-run.
set -e
need=0
for c in python3 ffmpeg ffprobe; do command -v $c >/dev/null || { echo "missing: $c"; need=1; }; done
if [ $need = 1 ]; then sudo apt-get update -y && sudo apt-get install -y ffmpeg python3 python3-pip; fi
# Devanagari font (FreeSerif). RAQM is needed so Marathi conjuncts shape correctly.
fc-list 2>/dev/null | grep -qi FreeSerif || sudo apt-get install -y fonts-freefont-ttf
python3 - <<'PY' || pip install --break-system-packages numpy scipy opencv-python-headless pillow
import numpy, scipy, cv2, PIL
from PIL import features
assert features.check('raqm'), 'Pillow without RAQM'
PY
python3 - <<'PY'
from PIL import features, ImageFont
import cv2, numpy, scipy
print('numpy', numpy.__version__, '| scipy', scipy.__version__, '| opencv', cv2.__version__, '| raqm', features.check('raqm'))
ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf', 40, layout_engine=ImageFont.Layout.RAQM); print('FreeSerif Bold OK')
PY
ffmpeg -version | head -1

# Check for GEMINI_API_KEY from GitHub Codespaces Secrets
if [ -n "$GEMINI_API_KEY" ]; then
  echo "GEMINI_API_KEY detected in environment."
  python3 -c "import google.genai" 2>/dev/null || pip install --break-system-packages google-genai
else
  echo "WARNING: GEMINI_API_KEY not found. Add it to GitHub Codespaces Secrets and reload your Codespace."
fi

echo "setup ok"

