# Hindi narration: how Jad Tak sounds

The test: **someone half-listening while cooking follows every sentence without looking at the screen.** The narrator is a
person telling a remarkable story to one listener, calm and sure, never a newsreader and never a lecturer.

The voice file `~/.claude/youtube/voice-jadtak.md` holds the channel's persona; read it first. These rules apply on top.

## Sentences

- **Length:** most sentences 6 to 14 words; hard ceiling 22. One idea per sentence. The full stop is where the narrator
  breathes.
- **Order:** subject, then action, verb at the end, as people speak. Put the surprise at the end of the sentence.
- **No stacked clauses.** Not "वह आदमी, जो उस गाँव में रहता था जिसका नाम ... था, ..." Split into two sentences.
- **Rhythm:** after three short sentences, one longer one; after a long one, a very short one. The references' strongest
  moments are 3 to 6 words ("पूरी रात एक भी नहीं।", AG 18:22).
- **Lists of three**, the last item the heaviest; negation lists end on what remains (D14).
- **Questions to the viewer**: 1 to 2 a minute at most, and only where the next sentences answer them.

## Words: the everyday word first

| Avoid (formal / academic) | Say |
|---|---|
| निर्णय लिया | फ़ैसला किया |
| प्राप्त किया / प्राप्ति | मिला, पाया |
| अवधारणा | बात, विचार |
| सदैव | हमेशा |
| परन्तु / किंतु | लेकिन |
| तत्पश्चात / उपरांत | इसके बाद, बाद में |
| अत्यंत | बहुत |
| आवश्यकता | ज़रूरत |
| एकत्र हो गए | इकट्ठा हो गए |
| उल्लेख | ज़िक्र |
| के माध्यम से | के ज़रिए, से |
| उपयोग किया | इस्तेमाल किया |
| विस्तृत | पूरा, विस्तार से |
| प्रतीत होता है | लगता है |
| इस प्रकार | ऐसे, इस तरह |
| शोध-ग्रंथ (repeatedly) | "एक रिसर्च" once; later "उसी रिसर्च में" |
| कथित तौर पर (in every line) | one attribution at the start of the story |

Sanskrit-origin words that are everyday for a Hindi audience stay: भक्त, आश्रम, साधु, संत, समाधि, भंडारा, प्रसाद, कृपा, आस्था.
Explain a religious or technical term once, in one breath, the first time (D8): "महासमाधि, यानी जब कोई संत अपनी मर्ज़ी से शरीर छोड़ता है।"

## English words

Keep the English that Hindi speakers use every day: डॉक्टर, हॉस्पिटल, रिपोर्ट, ट्रेन, स्टेशन, प्रोफेसर, यूनिवर्सिटी, कंपनी,
फ़ोन, फ़ोटो, गाड़ी. Avoid what they don't: "इन्फ्लुएंशियल", "एग्जीक्यूट", "क्लेरिटी", "काउंटर कल्चर", "स्पिरिचुअल सीकर्स" (SM's
habit). Say "उस दौर का नया युवा आंदोलन", "रास्ता साफ़ दिखने लगा", "अध्यात्म की तलाश में आए लोग". Proper names stay as they are
(Apple, Harvard, WHO), said once with a Hindi gloss where needed ("विश्व स्वास्थ्य संगठन, WHO").

## Numbers, dates, places

- Years as digits ("1967 में"); round big numbers the way people say them ("एक लाख से ज़्यादा", "करीब सौ साल पहले").
- Units always in words ("किलोमीटर", "मील"); never a unit the source doesn't give.
- A date-place stamp is its own sentence: "11 सितंबर 1973। वृंदावन।"
- Distances and ages that sources disagree on are said vaguely ("कुछ किलोमीटर आगे", "बहुत कम उम्र में"); see the ledger.

## Attribution: natural, rare, useful

Attribution answers "who is telling this?" when the answer helps the viewer. It is not a disclaimer.

| Situation | How often | Example lines (rotate; don't repeat one in a video) |
|---|---|---|
| A devotee story or miracle | once, at the start of the anecdote | "भक्त यह कहानी आज भी सुनाते हैं।" / "उनके भक्तों की किताबों में एक कहानी बार-बार आती है।" / "यह क़िस्सा सबसे ज़्यादा सुनाया जाता है।" |
| A named witness or book | once, when the witness enters | "रामदास अपनी किताब में लिखते हैं ..." / "दादा मुखर्जी ने बाद में लिखा कि ..." |
| A belief | once per belief | "उनके भक्त मानते हैं कि ..." |
| A disputed fact | once, at the contested point | "कुछ लोग {X} कहते हैं, कुछ {Y}।" |
| A news figure | once | "ज़िला प्रशासन के मुताबिक़ ..." |
| A thin evidence base | once per video, near the end (D22) | "इनके जीवन के बारे में ज़्यादातर बातें उनके भक्तों ने बाद में लिखीं। इसलिए हमने वही कहानियाँ चुनीं, जो उन किताबों में बार-बार आती हैं।" |

Limits (checked by `scripts/scriptcheck.py`): no more than **2 attribution phrases in any 30 seconds**, and on average no more
than **one a minute**; **disclaimer phrases** ("हमने नहीं देखा", "पुष्टि नहीं", "सत्यापित नहीं", "दावा किया जाता है") **at most
twice in the whole video**. The ledger holds the detail; the narration holds the story.

## Audience address

- "आप" always; "सोचिए", "ध्यान दीजिए", "अब ज़रा रुककर सोचिए" at most 3 or 4 times a video, at real turns.
- No "दोस्तों", no "चलिए शुरू करते हैं", no "वीडियो को अंत तक देखिए".
- **CTA only at the end** (RZ and SM do the same): one question about the viewer's own experience or opinion tied to the
  subject, then one line to subscribe, then stop. Optional in Long videos: one soft comment question at the act seam near
  the middle, only after a payoff, never inside suspense. No "लाइक और शेयर कीजिए" before the last 30 seconds.

## Writing for the voice (TTS and human)

- Write "।" in the script; the scratch voice replaces it with "." because Kokoro reads "।" aloud. Never write
  "पूर्णविराम".
- No brackets, slashes, abbreviations or symbols in narration ("डॉ." → "डॉक्टर"; "%" → "प्रतिशत"; "&" → "और").
- Quotation marks only around recorded words (see `anecdote-engine.md`); the narrator says "उन्होंने कहा" before them.
- Avoid two words that sound alike back to back; read every chapter aloud once (or listen to the scratch narration) before
  the evaluation.

## Smooth paragraphs

Each paragraph starts with a link to the last one: a time word (उसी रात, अगले दिन, कुछ साल बाद), a cause (इसीलिए, इसी वजह से),
a contrast (लेकिन, फिर भी), or the last paragraph's key noun. Avoid "अब बात करते हैं ..." and "आगे बढ़ते हैं".
