# The anecdote engine

The reference videos hold attention with **complete stories**, not summaries. RZ's barber story runs 55 seconds; AG's blanket
story runs five minutes; neither is compressed into "it is said he could be in two places". This engine turns a ledger entry
into a told story without inventing a single detail.

## The ten steps

Every important anecdote is built in this order. Steps can share a sentence; none is skipped without a reason written in the plan.

| Step | What it gives the viewer | Typical length | From the references |
|---|---|---|---|
| 1. **Time and setting** | where we are | 1 sentence | "समय द्वितीय विश्व युद्ध" (AG 14:14) |
| 2. **Main character** | whose story it is | 1 to 2 sentences | "एक बूढ़ा दंपति ... उनका इकलौता बेटा बर्मा बॉर्डर पर था" (AG 14:27) |
| 3. **What they wanted or feared** | stakes | 1 to 2 sentences | "4 महीने से कोई चिट्ठी नहीं आई थी" (AG 14:35); "उसका बेटा ... अभी तक नहीं लौटा है" (RZ 02:23) |
| 4. **What happened** | the event | 2 to 4 sentences | the visitor, the meal, the night |
| 5. **What made it unusual** | the first oddity | 1 to 2 sentences | soap on the face (RZ 02:34); the groaning night (AG 15:38) |
| 6. **Escalation** | the oddity grows, or is withheld | 1 to 3 sentences | the heavy blanket; "इसे खोलने की कोशिश मत करना" (AG 16:31) |
| 7. **Turning point** | new information arrives | 1 to 2 sentences | the son returns (RZ 02:46; AG 17:08) |
| 8. **Reveal** | the strangest fact, last in its sentence | 1 sentence | "उसी रात वो हमारे घर सोए थे" (AG 18:41) |
| 9. **Outcome** | what changed | 1 to 2 sentences | "यह सुनकर नाई समझ गया ..." (RZ 03:06) |
| 10. **Why it matters here** | the link to the central question | 1 sentence | "उसी क्षण से गांव वालों ने ... भगवान का दर्जा दे दिया" (RZ 05:42) |

A full anecdote is **8 to 20 sentences (45 s to 2:30)**. A vignette (used in montage or Act 1 origins) is steps 1, 2, 4, 8 in
3 to 5 sentences.

## Rules that keep it true

1. **Only the details the sources give.** If no source names the barber, he is "एक नाई". If no source gives the year, the
   setting is "एक दिन". No invented weather, thoughts, faces or words. Specificity comes from the sources' own details (soap
   on the face, two rotis, a heavy blanket), which is why the ledger keeps the exact excerpt.
2. **No invented dialogue.** Quotation marks only for words a source records, with its ledger id. A dramatized film's
   dialogue (status `dramatized`) is never quoted; tell what happened in narration instead. Reported speech without quote
   marks ("उन्होंने बस इतना कहा कि ...") is allowed only when the source reports that the person said it.
3. **One natural attribution, at the entry.** "भक्त यह कहानी आज भी सुनाते हैं।" / "रामदास अपनी किताब में लिखते हैं ..." Then
   tell the story straight. No "कथित तौर पर" in every sentence. (See `hindi-narration.md`, "Attribution".)
4. **When versions differ**, tell the best-supported version and keep the conflicting detail vague where they disagree (the
   distance, the age, the time). Note it in the ledger, not in the narration, unless the disagreement is itself
   interesting (then one sentence: "कोई सौ किलोमीटर कहता है, कोई सौ मील।").
5. **Keep the reveal last.** The sentence that carries the strangest fact ends on it. The explanation, if any, comes in the
   next sentence.
6. **Don't explain the miracle away, don't endorse it.** For faith accounts, step 10 links to the belief ("इसी तरह की
   कहानियों से ...") and the record when the record speaks (D18), once per contested event.
7. **Extraordinary is allowed.** Do not cut a story because it is miraculous. Cut it only if it is `unsupported`, if it
   repeats another story's beat, or if it does not serve the central question.

## Pacing inside an anecdote

- Setup sentences (steps 1 to 3) are short and plain: 6 to 10 words.
- The unusual act and the escalation (5 to 6) slow down: one action per sentence, concrete nouns.
- Put a beat of silence (0.5 to 1 s, marked `[ठहराव]` in the visual note, never in the narration) before the reveal.
- After the reveal: one sentence of outcome, one of meaning, then a bridge. Never more than three sentences of commentary.

## Worked example: the barber (ledger RZ07, AG13)

Material: RZ 02:18 to 03:08 (narrated; "एक प्रसिद्ध कथा के अनुसार"; son went to another village; stuck about 100 km away
with no money; a stranger with soap on his face gave him money) and AG 12:25 to 14:12 (dramatized; "100 मील"; narrator:
"the most told story among devotees"). Status: `video-reported` (×2), distance `conflicting`, no book source yet. No names,
no year in any source.

| Step | Narration | Ledger |
|---|---|---|
| attribution + 1 | भक्तों में यह कहानी सबसे ज़्यादा सुनाई जाती है। एक दिन बाबा एक नाई की दुकान पर दाढ़ी बनवा रहे थे। | AG13 (narrator), RZ07 |
| 2 + 3 | बातों-बातों में नाई ने अपनी परेशानी बताई। उसका बेटा कुछ दिन पहले काम से दूसरे गाँव गया था, और अब तक नहीं लौटा था। | RZ07 |
| 4 + 5 | यह सुनते ही बाबा उठ खड़े हुए। आधी दाढ़ी बनी थी। चेहरे पर साबुन लगा था। वे उसी हालत में दुकान से बाहर चले गए। | RZ07 |
| 6 | एक-दो मिनट में वे लौट आए, और फिर बैठ गए। नाई ने कुछ नहीं पूछा। | RZ07 |
| 7 | अगले दिन उसका बेटा घर लौट आया। उसने बताया कि वह बहुत दूर एक गाँव में फँस गया था। लौटने के पैसे नहीं थे। | RZ07 (distance kept vague: conflicting) |
| 8 | फिर एक आदमी उसके पास आया, उसे पैसे दिए, और कहा कि घर जाओ। उस आदमी के चेहरे पर साबुन लगा था। | RZ07 |
| 9 | नाई को याद आया कि बाबा कल बस एक-दो मिनट के लिए बाहर गए थे। | RZ07 |
| 10 | भक्त ऐसी कहानियों को बाबा की उस शक्ति से जोड़ते हैं, जिसमें एक ही समय में दो जगह होना माना जाता है। और यहीं से हमारा सवाल शुरू होता है। | RZ07, RZ08 (belief); central question |

About 140 words, 55 seconds. One attribution. No invented name, number or line of dialogue ("घर जाओ" is reported speech the
source gives: "कहा कि वह अपने पिता के पास वापस चले जाए"). The reveal is the last clause of step 8.

## Converting a dramatized source

A film like AG often carries a real devotee story inside invented scenes. Extract it this way:

1. Write down only what the **narrator** says and what is **common to two independent tellings** (or to the film and a book).
2. Strip names, ages, numbers and dialogue that appear only in the film (AG14's "17 men", the couple's names) unless a book
   gives them; log them as `dramatized`.
3. Keep the event's skeleton and its sensory core if a non-dramatized source shares it (the heavy blanket, "float it in the
   Ganga unopened" in devotee literature).
4. Tell it with one attribution to the tradition ("भक्तों की किताबों में यह कहानी ... "), never to the film.

## Anecdote inventory (fill in `<slug>-plan.md`)

| # | Anecdote | Ledger ids | Status | Steps available (1 to 10) | Score (see chapter-architecture.md) | Placement | Length |
|---|---|---|---|---|---|---|---|
| A1 | the barber | RZ07, AG13 | video-reported | 1,2,3,4,5,6,7,8,9,10 | 26/30 | Ch 3 opener | 55 s |

A story with fewer than six steps available is a vignette, not a full anecdote: use it in a montage or merge it.
