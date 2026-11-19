# Voiceover script format (Marathi, 60-90 s, about 140-150 words)

Paragraph breaks (blank lines) are the long pauses; the aligner relies on them. Keep punctuation ( , . ! ? ) where a breath happens.
The abhang lines at the end are written with "।" and "॥" (one line per half-line); the aligner and mksrt detect abhang cues by those marks.

```
<HOOK: 1-2 short sentences, a gap/question, ends "...त्याचं उत्तर तुकाराम गाथेच्या <क्रमांक> व्या अभंगात आहे.">

हा आजचा अभंग. आधी याचा अर्थ समजून घेऊ.

<meaning paragraph 1 - stanza 1: "तुकोबा म्हणतात, ...">

<meaning paragraph 2 - stanza 2>

<meaning paragraph 3 - stanza 3 ("तुकोबा म्हणतात, ..." for the signature line)>

तर आजचं सांगणं इतकंच. <one-sentence takeaway, 2-3 short phrases>

आता हा अनोखा अभंग पुन्हा ऐका, आणि आत्ता समजलेला अर्थ मनात ठेवून एकाग्र व्हा.
<abhang line 1 ।  line 2 ॥>      <- one source line per row, "।" after the first half, "॥" after the second
<abhang line 3 ।  line 4 ॥>
...

असेच अभंग रोज समजून घ्यायचे असतील, तर भक्ती अर्थ चॅनेल फॉलो करा. राम कृष्ण हरी!
```

## Hook rules
- It doubles as the thumbnail text: 3-4 short lines, ONE key word big + red + underlined, ends with a question ("कुणाला?", "कुणाशिवाय?", "कुणाच्या मुकुटावर?").
- Spoken hook <= about 8 s. If longer, shorten it and tell the user.
- Pick the line in the abhang that makes a viewer curious without giving the answer. Examples that were made:
  - 4: "सूर्य-चंद्रही फिके पडले! कुणापुढे?"
  - 5: "फक्त एकच मागणं! तुकोबांचं कोणतं?"
  - 7: "लोक मला काहीही म्हणोत, पण मी त्याला विसरणार नाही! कुणाला?"
  - 8: "क्षणभरही त्याच्याशिवाय करमत नाही! कुणाशिवाय?"
- Never invent a number, source or claim. Never change the abhang's words.

## Meaning rules
- One paragraph per stanza, plain spoken Marathi, 2-3 short sentences, each sentence = one picture. Say the word's meaning, not a lecture (e.g. "उदास" = विरक्त; "रातलें" = प्रेमात रंगून गेलो).
- Harsh or sensitive words of the original (शिंदळी, व्यभिचार ...) stay only in the abhang text; use a gentle equivalent in the meaning and tell the user.
- Bhava (devotional bride/lover voice) is explained as devotion, gently.
- End the meaning with the takeaway, then the second hook, then the recitation.

## Hand-off message to the user (Marathi, short)
Hook line, thumbnail text with the red word, 3-4 bullet notes on how hard words were read, the files (`abhang<N>_voiceover_mr.txt`, `tts_generate.py` command), and "WAV बनवून पाठवा". See `examples/` for finished scripts.
