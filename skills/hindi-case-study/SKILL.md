---
name: hindi-case-study
description: >-
  Writes the script for a long Hindi business case-study video (14 to 20 minutes) for the Hindi channel Decoding Vyapaar, using the hooks,
  re-hooks, chapter shapes and closes of the top Hindi business-documentary channels, studied from the transcripts of 38
  hits across 12 channels (Shivanshu Agrawal, HiddenOps, HinExp, ABFinDoc, Paisa Decode, Think School Hindi and more). Four formats: the economics of owning a business (bus, petrol pump, jewellery
  shop), a company's rise, split or fall, a person's rivalry/revenge/rise story, and two people making one money decision.
  Output is a researched, sourced script.json (Devanagari narration, sparse Hinglish on-screen text, a visual note per
  beat) checked by casecheck.py, plus the research file and three hook options. Use whenever the user asks for a Hindi
  script, a Hindi case study, a "business case study" or "economics of owning X" video, a Hindi documentary about a
  company or a businessman, or a script for Decoding Vyapaar or the Hindi channel, including from the Bean Studio Agent tab.
---

# hindi-case-study

A topic in, a script a Hindi viewer stays with for 15 minutes out. This skill stops at the script: the voice and the
visuals are a later step (each line already carries a visual note so either pipeline can use it).

```bash
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json           # the report: FAIL / WARN / PASS
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json --voice   # plain Devanagari narration
```

## Before you write

1. Read `~/.claude/youtube/voice-hindi.md` (the channel voice) and `references/study.md` (the study: the section for
   the format you pick, the re-hook toolkit, and **What not to copy**). Do not write from memory of the study.
2. Never invent a number, a date, a quote or a source. If a figure would help and you cannot source it, write the line
   without it or say it as an estimate with who estimates it.

Projects live in the Hindi channel's folder: `C:\Users\praty\youtube\channels\hindi\videos\<slug>\` (slug: lowercase
English words and dashes, e.g. `jewellery-shop-economics`). Make the folder if it is missing.

## 1. Topic and format

A topic works when all three hold (this is what separates both channels' million-view videos from their 10K ones):

- **The viewer can picture it in the first sentence**: a business they use (the bus, the petrol pump, the jeweller), a
  brand they grew up with, a name every Indian knows.
- **There is a gap between what everyone assumes and what is true.** Write the assumption down in one Hindi line.
- **It has money math or a human conflict** (a rivalry, a revenge, a fall, a rise from nothing).

**A topic someone already covered is fine, and often the best bet, if you repeat it cleverly** (the demand is proven; the
viewer clicks the title they already trust). Search YouTube for the topic first and list who has it and with how many
views. Then pick a **different angle**, not a retelling: (1) a different question in the title (the competitor asks "how
did X rise?", you ask "where does the money actually go?" or "what did X's rival do right?"); (2) the mechanism or the
numbers nobody put on screen (unit economics, a ledger, a loan, a contract clause); (3) a human on the other side (the
small shopkeeper, the employee, the customer); (4) a story shape the competitor doesn't use (money math as a story with
two characters, not a lecture). Keep the title formula of the proven hit (e.g. "X BUSINESS | Investment, Expenses,
Revenue & Real Profit") but never its script, its examples or its order. Write the competitor list and your angle in
`<slug>-research.md` under "Covered by".

If a topic misses one of the three, say which and offer a sharper angle before writing. Then pick the format. **B and C are the safest
bet**: the only two channels in the niche whose typical video (not just one hit) beats 300K, Shivanshu Agrawal (3.8M) and
HiddenOps (336K), tell one company's or one person's story from a humble start to its peak or fall.

| Format | `format` | Use for | Study videos |
|---|---|---|---|
| A. Economics of owning X | `economics` | a business the viewer meets as a customer | bus 2.0M, petrol pump 1.1M; told as a story: sleeper bus 3.6M |
| B. A company's rise, split or fall | `story` | a brand with nostalgia or a betrayal; "X is in trouble" | Haldiram's 12M, Byju's 10M, Nirma 9.2M, Hero Honda 1.3M |
| C. A person's story | `person` | rivalry, revenge, rags to riches, a big bet | Ambani 1.4M, Rolls-Royce 1.2M, Jhunjhunwala 976K |
| D. Two people, one decision | `compare` | rent vs buy, SIP vs plot, job vs business | rent vs buy 1.1M |

## 2. Research: `<slug>-research.md`

A facts table: claim, number, source (link or document), status: **verified** (official record, annual report, court
filing, regulator, two independent reputable reports), **reported** (one reputable outlet), **estimate** (industry
people, a model calculation; say so in the line) or **legend** (no record; say so or leave it out). At least five sources
for a story or person video, three for economics or compare. Prefer filings, court orders, company reports, RBI/SEBI/
ministry data, and established business press (Economic Times, Mint, Business Standard, BusinessLine, Reuters).

Real people: their documented words only. Dramatise with the scene (place, time, the phone ringing, the silence), not
with invented quotes. A reconstruction is marked ("उस दिन कुछ ऐसा माहौल रहा होगा"). Allegations are attributed and the
other side is given. For format A, a made-up model business with a made-up owner is fine and helps (study: "हाईवे फ्यूल
पॉइंट"); say it is a model. Best of all is **the owner's story** (HiddenOps' sleeper bus, 3.6M, beat HinExp's 2.0M on the
same topic): invented recurring characters, real numbers, and one plain line saying so ("ये किरदार सिर्फ इस कहानी में हैं; पैसा
असली है, एक-एक रुपया"). Invented characters suit this channel's illustrated stills too.

## 3. Packaging first

Write three titles (English, like both reference channels, at most 70 characters, the known thing in the first three
words: "The Economics of Owning a Jewellery Shop", "How Hero Honda Split"; for format A also try PaisaDecodeHQ's Hinglish shape,
the customer's price first: "₹1,200/Hour Turf Business: Weekend Full, Phir Bhi Profit Kahan Gaya?") and two to four thumbnail words in Hindi or
Hinglish that add the stakes ("असली कमाई?", "भाई vs भाई"). The hook has to confirm whichever title wins. Lint them with
**yt-package** if time allows.

## 4. The hook: short (25 to 40 s) or long (60 to 110 s)

**The short hook** is what the niche's strongest channel uses on every video (Shivanshu Agrawal: Haldiram's, Byju's, Nirma,
Oberoi, Big Bazaar, 6.5M to 12M each). Use it for formats B and C. Three beats, then straight into the origin:

1. **Year, place, a humble act or the peak moment**: "साल 1969, गुजरात। एक 24 साल का लड़का साइकिल पर घर-घर जाकर पीला
   पाउडर बेचना शुरू करता है।" / "26 जनवरी 2001, सुबह 5 बजे, हजारों लोग बिग बाजार की दीवार फांद रहे थे।"
2. **Dramatic irony or the fall**: "उस वक्त किसी ने सपने में भी नहीं सोचा होगा कि..." / "लेकिन अगले 20 सालों में ऐसा क्या हुआ
   कि इसी बिग बाजार के हर स्टोर पर ताला लग गया?"
3. **Name it**: "यह कहानी है ... की।" Then the birth, the family, the first job. No roadmap.

**The long hook** (HinExp, ABFinDoc, HiddenOps) suits format A, D and a mystery ("X is in trouble"). Every second works.
Its parts, in order:

1. **The scene (first 15 s).** One of: *you are there* ("एक सीन इमेजिन कीजिए। आप...", format A); *the stamped moment*
   ("साल 1982, 18 मार्च, दोपहर के डेढ़ बजे...", format C); *nostalgia* ("आपके पापा ने जिंदगी में एक बाइक जरूर चलाई होगी...",
   format B); *the accusation* (a trusted brand did something unforgivable, format B); *two people* (format D); *the
   paradox* ("स्टोर में पैर रखने की जगह नहीं, फिर भी शेयर महीनों से गिर रहा है", a mystery); *you are the owner* ("मान लो यह
   कैफे तुम खोल रहे हो। तुम 26 साल के हो, ₹35,000 की नौकरी है", format A); *the story scene* (invented characters at the
   worst moment, then "यह कहानी उस रात से 11 महीने पहले शुरू होती है", format A told as a story).
2. **The belief** the viewer holds, said in their voice, with the naive math if there is money ("36 बर्थ, हर एक बारह सौ की...").
3. **The break**: the shock number, the reveal ("...वो अलवर के महाराजा थे"), or the reframe ("यह सिर्फ X नहीं था, यह Y था").
4. **One to three questions** the video will answer, ending on the big one. The strongest version **defers one exact
   answer to the end and says so**: "उस टिकट में 10 हिस्सेदार हैं, मालिक की बारी 11वीं। जवाब आखिर में।" / "और आखिर में बताऊंगा
   कि अगर मुझे कल यह कैफे खोलना हो तो मैं सबसे उल्टा क्या करूंगा।" Then pay it off, exactly, at the end.
5. **The roadmap as promises**: three to five things the video will open, each phrased as a secret or a stake ("वो खर्च
   जिसकी बात कोई नहीं करता", "वो फैसला जिसने..."). Then the start line, in this channel's own words.

Write **three complete hooks** (at least one short, one long, with different scene types) into `<slug>-hooks.md`, pick
one, and say in one line why it fits this topic. Never a greeting, a channel intro or an ask in the hook.

## 5. The body

Chapter order comes from the format's section in `references/study.md`. Through every chapter:

- **A turn every 20 to 40 seconds**: लेकिन, a question answered at once ("यह पैसा जाता कहां है? ..."), or talking straight
  to the viewer ("समझो...", "मान लीजिए...").
- **A strong re-hook every 60 to 90 seconds**, never more than about 2.5 minutes without one: a twist marker, a secret, the
  other side of the coin, putting the viewer in someone's place, dramatic irony ("उन्हें अंदाजा भी नहीं था कि..."), a setback
  chain and reversal, an escalating numbered list ("पहली वजह... चौथी और सबसे बड़ी"). Use the moves in the toolkit, in fresh
  words every time.
- **In a company or person story, explain every win as a named strategy with its mechanism and a number** (Shivanshu's
  method): Nirma hired women to ask shopkeepers for Nirma until the shops stocked it; 65% soda ash; three stages to the
  customer instead of Surf's four; a 15% excise rebate. Give the rival's counter-move its own scene (HLL's secret "STING"
  mission, then Wheel). Foreshadow every fall: "सब अच्छा चल रहा था, कि तभी कुछ ऐसा हुआ जिसने...", "लेकिन ये कामयाबी
  ज्यादा देर टिकने वाली नहीं थी", "लेकिन फिर कहानी में एंट्री होती है एक ऐसे खिलाड़ी की जो...". In a fall, say what they should
  have done, then "लेकिन उन्होंने इनमें से कुछ भी नहीं किया".
- **In an owner's story, plant the naive math early and promise it will flip** ("याद रखिए, यह हिसाब आखिर में पलटेगा"), then
  let the real costs arrive as events in the character's life (the bank refuses, a tyre bursts, the agent takes 15%).
- **The biggest twist in the middle third.** In format C, **return to the cold-open scene at 60 to 75%**, then give one
  more twist after the loop closes.
- **Numbers carry the trust** (rupees, percentages, years): format A at least 3.5 a minute, D at least 6, B 2.5, C 1, with the source in the research file. Say an
  estimate as an estimate inside the same sentence.
- **Balance** anything contested: "कुछ लोग इसे... मानते हैं, तो कुछ... सच शायद बीच में कहीं है।"
- **One picture per sentence, at most 25 words a line** (one line is one breath of the voice). Explain each English
  business word once in plain Hindi. One image that sticks per chapter ("एक खड़ी बस, एक घाव जो हर दिन गहरा होता है").

## 6. The close: the last 60 to 90 seconds

1. **The verdict**, a judgment, not a recap of the chapters ("हां भी और ना भी, और फर्क इस बात से पड़ता है कि...").
2. **The maxim**: one line the viewer could repeat ("अपने धंधे की सबसे जरूरी चाबी कभी किसी और के हाथ में मत दो").
3. **The callback as an observation test**: back to the opening scene, with one thing to go and look at (used by four
   channels): "अगली बार संडे शाम टर्फ के ₹75 दो, तो एक बार सुबह 6 बजे भी उस टर्फ के पास से गुजरना। वहां जो दिखेगा, वही
   बता देगा..." / "अगली बार DMart की लाइन में खड़े हों, तो देखिएगा कितने लोग सामान गिन रहे हैं और कितने फोन।"
4. **One ask block**: send it to a specific friend ("उस दोस्त को भेजिए जो सोचता है कि..."), a personal or two-sided comment
   question ("आपके घर की पहली गाड़ी कौन सी थी?", "हक पद का बनता है या हिस्से का?"), while the channel is small the Hype
   button ("नीचे Hype का बटन दिखे तो एक Hype दे दीजिए, छोटे चैनल के लिए वो एक लाइक से कहीं ज्यादा काम करता है"), or let them pick the next topic, subscribe for the next video named with two
   questions about it. No ask anywhere before this.
5. **The sign-off line** from `voice-hindi.md`.

## 7. `script.json`

```json
{
  "title": "The Economics of Owning a Jewellery Shop",
  "format": "economics",
  "sources": ["https://...", "BIS hallmarking notification, 2021", "..."],
  "lines": [
    {"hi": "एक सीन इमेजिन कीजिए।", "visual": "Evening, a busy Indian bazaar, a jewellery shop glowing behind glass", "chapter": "Hook"},
    {"hi": "आप एक ज्वेलरी शोरूम में खड़े हैं, और आपके सामने डेढ़ लाख का एक हार रखा है।", "screen": "₹1,50,000", "visual": "Close-up: a gold necklace on red velvet, a price tag"}
  ]
}
```

- `hi`: the narration in Devanagari, as the narrator says it (numbers in spoken form; brand and people's names may stay
  in Latin letters). One sentence per line.
- `screen` (optional, rare): Hinglish in Latin letters, at most 6 words: a number, a name, the key word. On under a third
  of the lines.
- `visual`: what is on screen, in English, specific enough to draw (place, people, action, the one object that matters).
  A new picture every one to three lines. Recurring characters keep the same description word for word.
- `chapter` on the first line of each chapter: a 3 to 5 word English title that promises the section (it becomes the
  YouTube chapter).

Aim for 2,200 to 2,800 Hindi words (14 to 18 minutes at 155 words a minute); for a 10 to 15 minute video, 1,600 to 2,300.

### The shot plan (every line carries `kind`)

The pictures follow how the reference channels edit, measured on their real clips (HinExp, ABFinDoc, Finance In Minutes
animate 88 to 99% of the time in 1 to 4 s shots; Money Code is the hybrid: 3 to 4 s shots, about half moving; HiddenOps
cuts under 1 s in the hook, then 3 to 6 s). Add to each line `"kind"`:

- `hero`: an AI image-to-video clip of 2 to 4 s (a face turning, a gesture, a walk-in, coins falling). Costs money, so
  it goes where the narration matters.
- `still`: an illustration held 3 to 6 s with a slow code camera move (push-in, parallax, drifting dust, a light flicker).
- `card`: a code graphic (a number, a ledger, a bar, a map, a flow arrow) drawn in clean Hindi/Hinglish; free.

Timing rules (a shot is not the same as a line: one `kind` marks the picture that starts on that line):
1. **Hook (0 to 40 s): a new shot every 1.5 to 3 s, at least 70% `hero`**, with a card for the first number. The hook is
   where the real channels cut fastest and move most.
2. **Body: a new shot every 3 to 5 s; about 35 to 45% `hero`, 35 to 45% `still`, 15 to 25% `card`.** Never hold a `still`
   longer than 6 s. Never two `card`s in a row.
3. **Every money-math line gets a `card`** (the number on screen while it is said). Every emotional beat (a fall, a
   betrayal, relief) gets a `hero` on the face.
4. **Re-hook burst**: at each chapter start and about every 3 minutes, a run of 3 to 4 short `hero` shots.
5. **Close (last 60 s)**: slow down to `still` and one long `hero` on the closing face; the last line holds a still.
6. The same scene may appear again from a new angle or a new moment (an animated repeat of the same still counts as a new
   shot): repeating the location or the character is how the cost stays low without the video feeling repetitive.
Also add `"shot": "<what moves>"` for `hero` lines (the motion prompt: one action, camera almost still). Count the kinds in
the hand-back (shots, `hero` seconds, estimated xAI cost at $0.032 per `hero` second and $0.055 per distinct image).

## 8. Check, then hand back

Run `casecheck.py` and save its output to `<slug>-check.txt`. Fix every FAIL. For each WARN, fix it or write one line in
the check file saying why it is right for this script. Save `--voice` output to `<slug>-script.txt` for reading aloud.

Hand back: the winning title and thumbnail words, the chosen hook in full plus one line on each alternative, the chapter
list with timings, the runtime, the checker summary, and any facts marked estimate or legend. Nothing here publishes.
The last line of every run is the question: **ship it, or change it?**
