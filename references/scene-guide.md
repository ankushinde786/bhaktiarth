# Scene guide - drawing one idea per beat

Every idea in the voiceover gets its OWN drawing. For each beat decide: (1) the concrete image the words name or imply, (2) how it is drawn on, (3) the ambient animation, (4) the transition (ink wash, brush wipe, camera pan).

## Where things are in render.py
- `SC = dict(name=(start, end), ...)`: a window per drawing. A drawing function reads its own window: `s0, s1 = SC['name']; a = vis(t, s0, s1); lt = t - s0`, returns if `a <= 0`, and draws everything from the local time `lt`.
- `frame(t)`: the scene tuple `for fn in (sc_a, sc_b, ...)` runs the drawings; add yours there.
- Helpers: `stroke(fr, pts, progress, width, colour, alpha)` (brush stroke that reveals along its length), `wash`, `disc`, `ring`, `leaf`, `petal`, `blob` (red dot), `sparkle`, `person(fr, x, y_base, height, alpha, crown, red, pr)`, `catmull` (smooth path), `backout` (overshoot ease), `ss` (smoothstep), `enso`, `uline`.
- Colours: `BLK`, `RED`, `GREY`, `OCHRE`. Red is the only accent.
- Camera: `K` keys (time, cx, cy, zoom) with a PCHIP curve; `AMAX` is the Vitthal painting's visibility over time (low behind text, 1.0 only when He is the subject).
- Vitthal face shot: set `VIT_A, VIT_B`, the `K` keys (push to x 545, y 520-600, zoom 1.3-1.55) and `AMAX` to 1.0 for the same window; the red tilak is inked in by `vitthal()`.

## Ready drawings (see assets/scene_gallery.jpg) - and WHEN each may be reused
Reuse only when the words name that object. Name test first (SKILL.md step B5).
| Function | Shows | Reuse only if the words say |
|---|---|---|
| sc_sunmoon | sun and moon, then red dot | day and night / सूर्य-चंद्र / रात्रंदिवस |
| sc_tilak | clock dial | time, a moment (क्षण, घडी) |
| sc_mukut, sc_mukut2 | crown with red suns | मुकुट / crown, राणी |
| sc_pour | pot pours red into an overflowing bowl | a pot / pouring / overflowing joy |
| sc_bowl, sc_bowl2 | leaking bowl | never filled, a vessel |
| sc_rain | dark cloud, rain | मेघ, rain, cloud-dark Lord |
| sc_eyes | eyes close, red dot, rings | ALWAYS - the second hook |
| sc_garland, sc_cloth, sc_ear, sc_tulsi, sc_feet, sc_murti, sc_garuda, sc_lotus, sc_gem, sc_rakh, sc_sides, sc_sages, sc_friend, sc_unique | garland, cloth, ear, tulsi beads, feet on brick, idol, Garuda, lotus, gem, consort, attendants, singing sages, Lord and friend, one-of-a-kind dot | exactly that object |
| sc_lamp | red-flame lamp | दिवा / lamp / light |
| sc_wishes, sc_drift | many dots drift, one stays | wishes, desires, many things drifting away |
| sc_wilt, sc_road | wilting flower, road to temple | longing / वाट, a journey |
| sc_crowd, sc_words, sc_world | crowd pushes one away, scribbles toward a figure, globe | people / gossip / the world, literally |
| sc_drop, sc_dye, sc_love, sc_near, sc_firm | rings fall off a figure, red fills a figure, glowing heart, two figures near, firm figure in wind | those exact actions |
| sc_thread | a rope between a lone figure and a crowd is cut (abhang 10: no dealings with the world) | cutting ties |
| sc_bud | a bud opens with a red heart (secret love revealed) | hidden / secret / opening up |
| sc_known | red rings reach the people around (everyone comes to know) | it became known |
| sc_honour | a turban slips off (respect lost) | honour, मान |
| sc_coins | coins roll up, an open palm sends them away (no greed) | greed, लोभ, wealth |
| sc_taal | arms raised, cymbals, red flag (mad with love for God) | भक्तीचं वेड, वारकरी, टाळ |
| sc_joy | joyful figure, fallen turban, whispers pass by | carefree devotion |

## New drawing checklist
- Name test: one line `words -> object -> motion` per beat before drawing.
- Prefer people, objects and animals of Marathi / Warkari life over abstract shapes.
- Reads at phone size: bold simple shapes, one focus, empty paper around.
- Inside x 40-980, y 360-1500 (top 120-340 holds the small original lines; subtitles at y 1340-1500 - keep the drawing above ~1300 or accept overlap only on paper-light areas).
- At least one moving element for the whole window; red "life" element appears late (about lt 1-3 s) on the key word.
- Draw-on with `stroke(... progress ...)`, ease with `ss` / `backout`.
- Test with `python3 -I render.py still <t>` at 2-3 moments inside the window.
