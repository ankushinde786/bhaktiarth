# bhakti-arth-abhang-shorts

Skill pack for making the **भक्ती अर्थ** Tukaram-abhang Shorts (9:16, Chinese Ink Wash, Marathi) with an AI coding agent, for example Antigravity CLI in GitHub Codespaces, next to the Opuscar skill.

## Install
1. Unzip into your repo, for example `.agents/skills/bhakti-arth-abhang-shorts/` (Antigravity: workspace skills live in `.agents/skills/`; `/skills reload` after adding) or `skills/bhakti-arth-abhang-shorts/`. Keep `AGENTS.md` where the agent reads it (copy it to the repo root, or point the agent at this folder).
2. Opuscar's Chinese Ink Wash style is already bundled (`references/opuscar/`); you do not need the Opuscar repository. **Keep this repo private** (CC BY-NC material inside, see `references/opuscar/NOTICE.md`).
3. In the Codespace terminal: `bash <skill>/tools/setup.sh` (installs/checks ffmpeg, FreeSerif font, numpy, scipy, opencv, pillow with RAQM).
4. Optional, only for making the voice: `pip install google-genai` and `export GEMINI_API_KEY=...`.

## Use (talk to the agent in plain words)
1. `Abhang 9` + the abhang text -> script, thumbnail text, TTS command.
2. Run the TTS yourself, upload the WAV -> the agent syncs, builds the storyboard and stops.
3. Write `Approved` (or "frame 7 change ...") -> render, mix, final MP4 (+ `_share.mp4`), thumbnail.

Example prompt for the agent:
> Use the bhakti-arth-abhang-shorts skill. Abhang 9: <paste abhang>

and later:
> Here is the voiceover WAV for abhang 9 (attached). Make the storyboard.

## What is inside
| Path | What |
|---|---|
| `SKILL.md` | the full procedure (read this first) |
| `AGENTS.md` | short rules + routing for the agent runtime |
| `engine/` | `render.py` (template with `# >>> PER-ABHANG` blocks), `mix.py` (5 % sound), `align.py` + `mksrt.py` (sync + SRT), `prep.py` (Vitthal painting -> animation layers), `board.py` (storyboard sheet), `tts_generate.py` |
| `assets/vitthal_reference.png` | the Vitthal ink painting used behind the hook, the face shot and the recitation |
| `assets/scene_gallery.jpg` | all 46 ready drawings, early/late frames, with function names |
| `references/opuscar/` | bundled Opuscar Chinese Ink Wash style (STYLE.md, demo, DIRECTOR.md, TECHNIQUE.md) + licences |
| `references/` | `master-prompt.md` (original director prompt), `script-format.md`, `scene-guide.md` |
| `examples/abhang-7`, `abhang-8` | script, cues, synced SRT, storyboard, thumbnail with overlay (abhang 8) |
| `tools/` | `setup.sh`, `new_abhang.sh`, `finish.sh`, `scene_gallery.py` |

## Example: what an abhang folder looks like
```
films/tukaram-abhang-8/
  voice.wav  script.txt  cues.json  subs.srt  abhang8_marathi_synced.srt
  render.py  mix.py  align.py  mksrt.py  prep.py  board.py   (copied from engine/, edited PER-ABHANG blocks)
  out/assets.npz (140 MB, rebuilt by prep.py)  out/mix.wav  out/levels.txt  out/part_*.mp4
  sb/storyboard.jpg
  tukaram-abhang-8.mp4   (+ _share.mp4 when > 30 MiB)
```

## Example numbers (abhang 8)
Voice 82.0 s -> video 82.74 s; hook 0-7.6 s, static card 7.7-12.3 s, meaning 12.3-40.6 s, takeaway 40.7-49.6 s, second hook 49.4-56.3 s, recitation 57-74 s, end card 74.6 s. Bed 5.00 % of the voice; render about 4 min per half on 2 cores.

## Limits
- Rendering is CPU-only; two halves in parallel (about 8 min per Short on 2 cores).
- `assets.npz` is large; it is git-ignored and rebuilt in about 12 s.
- Pictures come from a code library of drawings; a new idea needs a new `sc_*` function (see `references/scene-guide.md`).
