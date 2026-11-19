---
name: bhakti-arth-abhang-shorts
description: Make a finished 9:16 Chinese-ink-wash YouTube Short for the Marathi channel "भक्ती अर्थ" from ONE Sant Tukaram abhang - Marathi voiceover script (60-90 s, hook first), SRT sync, storyboard for approval, then render, 5 % sound mix and delivery. Use when the user sends an abhang number and text, a voiceover WAV for an abhang, or says "approved" for an abhang storyboard.
---

# bhakti-arth-abhang-shorts

One Tukaram Gatha abhang becomes one Short: a Marathi voiceover that explains the meaning, drawn as ink-wash pictures, with the abhang recited at the END.
The channel is **भक्ती अर्थ** (religious scripts, mantras, shloka with meanings, meditation). Audience: Marathi. Abhangs are made in order (1, 2, 3 ...).

Everything is produced in code (numpy / OpenCV / PIL / ffmpeg). No stock footage, no downloaded sounds, no network needed except the optional TTS.

## Opuscar material (bundled) and the standalone rule

The Chinese Ink Wash style of the Opuscar library is **bundled** in `references/opuscar/` (`styles/ink-wash/STYLE.md` = the look rules, `DEMO.md` + `demo/` = a reference film in code, `DIRECTOR.md` / `TECHNIQUE.md` = craft guides, licences in `LICENSE` and `LICENSES/`, see `NOTICE.md`). This skill therefore works on its own; the full Opuscar repository is NOT needed. If the full Opuscar skill is also installed, **this skill wins** for the abhang Shorts:
- Do NOT run Opuscar's "Brief / Treatment / Look" workflow, do not ask its language question (language is always Marathi), do not pick another style, no TREATMENT.md.
- The style is fixed: Chinese Ink Wash. Read `references/opuscar/styles/ink-wash/STYLE.md` once for the look rules; open `DIRECTOR.md` / `TECHNIQUE.md` / the demo code only when you need a new drawing, camera or sound idea.
- The storyboard stop is mandatory here (Opuscar's default is "no storyboard").
- The render engine is this skill's `engine/` (pure Python), not Opuscar's Node `core/`.
- Licence: the bundled .md files are CC BY-NC 4.0 (own-film use allowed). Keep the repository private; never publish them.

## Fixed facts

- Output: 1080x1920, 24 fps, H.264 + AAC 48 kHz stereo MP4, length = voiceover + 0.7 s. Over 30 MiB -> also `_share.mp4` (~1900 kb/s) and send that.
- Language on screen: Marathi (Devanagari). Never change the user's words. Fonts: FreeSerif and FreeSerif Bold.
- Look: warm rice-paper ground; black ink #121010; ONE accent vermilion #C41C18 (key word, dot, enso, seal, the "life" element of a drawing); grey wash #786F68 for secondary text; ochre only for cloth/beak when needed. Everything arrives as ink (brush strokes that reveal, wash that bleeds). No emoji, no glow, no hard UI shapes.
- **Safe area (YouTube Shorts) - hard rule:** all text, subtitles and key drawings inside x 40-980, y 120-1540. Bottom 380 px (channel name/description) stays empty. Right 100 px (x>980, y 740-1920) stays empty. Every storyboard still shows the overlay (cyan frame, tinted footer, tinted side strip).
- **Sound - strictly 5 %:** the voiceover is untouched. Music + animation sounds (synthesised guqin plucks, pad, brush, ink, drip, rustle, pop, seal thud, ring) are mixed so their RMS over the speaking frames is **5.00 %** of the voice. Measure and report (target 4.9-5.1 %). Mix peak <= 0.98 by ONE uniform scale; if the voice itself peaks above 1.0, say so and tell the user to record a little quieter.

## The video order (fixed - built so viewers do not swipe)

1. **HOOK card** - short, animated; text is a click-line (3-4 short lines, centred, bold black, ONE big red word with a hand-drawn red underline, ends with a question/gap). Fully visible from frame 1 (first second = thumbnail). Red enso drawn in ~1.3 s, faint Vitthal inks in from the feet.
2. **TODAY'S ABHANG** - the whole abhang as one static card (title "तुकाराम गाथा · अभंग क्र. N" with red underline drawing on). Spoken: "हा आजचा अभंग. आधी याचा अर्थ समजून घेऊ."
3. **EXPLANATION** - the meaning, ONE ink drawing per idea (new drawing every 3-6 s), the original half-lines small (42 px) at the top while a stanza is explained. Not a Vitthal slideshow: Vitthal appears only when the words are about Him directly (face, tilak).
4. **TAKEAWAY** - one sentence, one drawing; subtitles on.
5. **SECOND HOOK** - "आता हा अनोखा अभंग पुन्हा ऐका, आणि आत्ता समजलेला अर्थ मनात ठेवून एकाग्र व्हा." Eyes close, red dot gathers, rings pulse.
6. **RECITATION** (at the END) - all lines grey, each word turns bold with the voice, red dot + red underline follow; no subtitles.
7. **FOLLOW / END card** - red enso, "भक्ती अर्थ", "रोज एक अभंग", "फॉलो करा" (red) on the follow request, vermilion seal "राम कृष्ण हरी" stamped on the sign-off.

Subtitles (from the SRT) sit at y ~1340, only during explanation, takeaway and second hook.

## Workflow per abhang (the user sends the abhang number + text)

Keep a task list. First line to the user: one sentence saying what you are doing. Replies to the user are in **Marathi, short**.

### A. Script (the user has not sent a voiceover yet)
1. Write the Marathi voiceover per `references/script-format.md` (about 140-150 words, 60-90 s; the hook first, then the fixed structure). Save as `abhang<N>_voiceover_mr.txt`.
2. Hook: write a few options, pick by judgement. `hookscore.py` of the yt-script skill is tuned for English and is **not reliable for Marathi** - say so if asked. The hook is also the thumbnail text, so it must be short and clickable.
3. Give the user: the script file, the thumbnail text (3-4 lines, which word is red), the meaning notes (how hard words were read), and the ready TTS code (`engine/tts_generate.py <script> abhang<N>_voice`). Ask them to send the WAV. The user makes the voice themselves (Google AI Studio TTS, voice "Elio"). Do not try to generate it unless a GEMINI_API_KEY exists and the network allows it.
4. A sensitive or harsh word in the abhang (e.g. शिंदळी, व्यभिचार) stays **only** in the original abhang text (static card and recitation). In the meaning use a gentle phrase, and tell the user which word you softened.

### B. Voiceover WAV arrives
1. `bash tools/new_abhang.sh N voice.wav script.txt` (creates `films/tukaram-abhang-N/`, builds `out/assets.npz` from `assets/vitthal_reference.png`). If the user attaches a different Vitthal painting, use it: `python3 -I prep.py <image>` (crop constants at the top of prep.py may need adjusting).
2. **Sync:** `python3 -I align.py voice.wav script.txt x.srt` -> prints a table and writes `cues.json`. It detects pauses (10 ms energy, -33 dB, >=150 ms) and aligns the script phrases by dynamic programming (~10.5 chars/s). Check outliers (rate < 8 or > 20 chars/s) against syllable counts. Where pauses are ambiguous, **merge the neighbouring cues** into one wider cue in `cues.json` and tell the user; never guess a split. Abhang lines are recited slowly (8-11 chars/s is normal).
3. `python3 -I mksrt.py <voice_seconds+0.7> abhang<N>_marathi_synced.srt` then `cp` it to `subs.srt`. Max 2 lines per cue, cue ends 0.15 s after speech, abhang cues are the ones with "।"/"॥". Validate: increasing, no overlaps, inside the audio length.
4. **Beat sheet** from the cue times: hook end (`HOOK_END`), meaning start (`EXPL_START`), each idea's window, takeaway, second hook, recitation (`LINE_T` = the abhang cue times, one per half-line), `REC_IN/REC_OUT`, `END_T`, `FOLLOW_T`, `SEAL_T`. Put them in the PER-ABHANG block of `render.py`.
5. **Pictures - the name test (hard rule).** Every drawing must show an object the words of that beat actually NAME or directly act out. Before choosing, write one line per beat: `words: "<Marathi phrase>" -> object: <concrete thing the words name> -> motion: <what it does>`. If you cannot name the object from the words, the picture is wrong.
   - Do NOT reuse a drawing just because it is in the library. Generic fillers (drifting dots / bubbles = `sc_drift`, `sc_wishes`; the red lamp = `sc_lamp`; rings; the globe; the crowd) are allowed only when the words literally say dots, wishes, a lamp, the world, a crowd.
   - Reuse a ready drawing only when its object is named again in the new abhang (a crown for "मुकुट", a bowl for "वाटी", Garuda for "गरुड"). Otherwise **write a new `sc_*` function for this abhang**; it is normal that most drawings of a new abhang are new. Aim for at most 1-2 reused drawings per video (the second-hook eyes and the end card are always reused).
   - Abstract ideas (decision, fear, secret, honour, greed, madness for God) get a concrete everyday image from Marathi / Warkari life: a cut rope, a bud opening, a turban slipping off, coins bouncing off an open palm, cymbals (टाळ) and a flag (पताका), a lamp only if "दिवा", a tulsi plant, a pilgrim road, a bride's garland, a pot (घडा), a cow, a bullock cart, a river (चंद्रभागा), a temple spire, a brick (वीट).
   - Browse `assets/scene_gallery.jpg` (46 drawings, each shown early/late) or run `python3 tools/scene_gallery.py` to see what exists and to copy the drawing style, then give each new drawing a window in `SC` (`SC['name'] = (start, end)`) and list it in the scene tuple inside `frame()`. Write new drawings per `references/scene-guide.md`; check them with a quick contact sheet (4 moments each) before the storyboard.
   - In the storyboard summary tell the user which drawings are new and which are reused, and why each reused one fits.
6. **Mix:** edit the event list and the score in `mix.py` to follow the picture timings, then `python3 -I mix.py <DUR>`; read `out/levels.txt` (bed must be 5.00 % of the voice).
7. **Stills + storyboard:** `python3 -I render.py still <times...>` (safe-area overlay is drawn), edit the list in `board.py`, `python3 -I board.py` -> `sb/storyboard.jpg` (labelled contact sheet: hook, static card, one still per beat, takeaway, second hook, recitation at 2 moments, end card, seal). LOOK at the sheet and fix text overlaps, clipped text, empty frames before sending.
8. **Send** the storyboard, the SRT and a short Marathi summary (seconds per part, 2-3 assumptions: ambiguous SRT spots, softened word, reused drawings). Then **STOP and wait for "Approved"** (or changes by frame number; apply them and send an updated storyboard).

### C. After "Approved"
1. Render two halves in parallel, **detached** (a render started inside a long blocking call gets killed):
   `setsid nohup python3 -I render.py video 0 <MID> > out/r1.log 2>&1 &` and `setsid nohup python3 -I render.py video <MID> <DUR> > out/r2.log 2>&1 &` (MID = half of DUR, e.g. 41.4). Poll with short sleeps (<= 100 s per call) on `out/r1.log` / `out/r2.log` until both print `done`. About 4 min per half.
2. `bash finish.sh N part_00000.mp4 part_<frame>.mp4` (copy `tools/finish.sh` into the project, or call it by path) -> joins, muxes `out/mix.wav`, checks, makes `_share.mp4` when > 30 MiB.
3. **Check before sending:** (a) stills at key times with the safe overlay: nothing in the footer or side zones; (b) `out/levels.txt` shows 4.9-5.1 %; (c) `ffprobe`: 1080x1920, h264 + aac, duration = voice + 0.7; (d) look at a few mid-video frames of the final MP4. Fix problems before sending.
4. Deliver the MP4 (or `_share.mp4`) and a thumbnail (a still at t = 1.0 **without** the overlay if possible - tell the user the overlay lines must not be published). Short Marathi summary: file, 5 % level, voice peak, one next step (the next abhang; offer title/description/tags with the yt-seo skill).

## Gotchas learned

- Never start a long render inside a blocking call; always detached, then poll.
- If the DP alignment gives rates far outside 8-20 chars/s, read the pause structure by hand; merge cues rather than guess.
- Caption rows (original lines) at y 232/284 with 42 px font; 6-8 abhang rows use 60 px / 128 px step, 10 rows 60 px / 112 px, 12 rows 58 px / 94 px with the first row at y 360 (edit `FN`, `Y0`, `STEP`).
- The hook text must fit x 40-980 (`fit(txt, size, maxw)` shrinks it); the enso circle may touch the red word - acceptable, mention if it hurts.
- No network installs may be possible. `tools/setup.sh` only checks / installs once.
- Big file `out/assets.npz` (~140 MB) is rebuilt by `prep.py` in 12 s; never commit it.

## Files in this skill

- `engine/` render.py (template with `# >>> PER-ABHANG` blocks), mix.py, align.py, mksrt.py, prep.py, board.py, tts_generate.py
- `assets/vitthal_reference.png` (the user's Vitthal ink painting), `assets/scene_gallery.jpg`
- `references/opuscar/` (bundled Opuscar Chinese Ink Wash style, guides, licences),
- `references/master-prompt.md` (the original director prompt), `references/script-format.md`, `references/scene-guide.md`
- `examples/abhang-7`, `examples/abhang-8` (script, cues, SRT, storyboard), `examples/abhang-6-script.txt`
- `tools/` setup.sh, new_abhang.sh, finish.sh, scene_gallery.py
