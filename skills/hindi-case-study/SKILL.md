---
name: hindi-case-study
description: >-
  Writes the script for a long Hindi business case-study video (14 to 20 minutes) for the Hindi channel, using the hooks,
  re-hooks, chapter shapes and closes of the top Hindi business-documentary channels (HinExp, ABFinDoc), studied line by
  line from their ten most-viewed videos. Four formats: the economics of owning a business (bus, petrol pump, jewellery
  shop), a company's rise, split or fall, a person's rivalry/revenge/rise story, and two people making one money decision.
  Output is a researched, sourced script.json (Devanagari narration, sparse Hinglish on-screen text, a visual note per
  beat) checked by casecheck.py, plus the research file and three hook options. Use whenever the user asks for a Hindi
  script, a Hindi case study, a "business case study" or "economics of owning X" video, a Hindi documentary about a
  company or a businessman, or a script for the Hindi channel, including from the Bean Studio Agent tab.
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

If a topic misses one, say which and offer a sharper angle before writing. Then pick the format:

| Format | `format` | Use for | Study videos |
|---|---|---|---|
| A. Economics of owning X | `economics` | a business the viewer meets as a customer | bus 2.0M, petrol pump 1.1M |
| B. A company's rise, split or fall | `story` | a brand with nostalgia or a betrayal | Hero Honda 1.3M, Tavera 1.0M |
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
पॉइंट"); say it is a model.

## 3. Packaging first

Write three titles (English, like both reference channels, at most 70 characters, the known thing in the first three
words: "The Economics of Owning a Jewellery Shop", "How Hero Honda Split") and two to four thumbnail words in Hindi or
Hinglish that add the stakes ("असली कमाई?", "भाई vs भाई"). The hook has to confirm whichever title wins. Lint them with
**yt-package** if time allows.

## 4. The hook: 60 to 110 seconds, ends on "चलिए शुरू करते हैं"

Longer than an English hook, and every second is working. Its parts, in order:

1. **The scene (first 15 s).** One of: *you are there* ("एक सीन इमेजिन कीजिए। आप...", format A); *the stamped moment*
   ("साल 1982, 18 मार्च, दोपहर के डेढ़ बजे...", format C); *nostalgia* ("आपके पापा ने जिंदगी में एक बाइक जरूर चलाई होगी...",
   format B); *the accusation* (a trusted brand did something unforgivable, format B); *two people* (format D).
2. **The belief** the viewer holds, said in their voice, with the naive math if there is money ("36 बर्थ, हर एक बारह सौ की...").
3. **The break**: the shock number, the reveal ("...वो अलवर के महाराजा थे"), or the reframe ("यह सिर्फ X नहीं था, यह Y था").
4. **One to three questions** the video will answer, ending on the big one.
5. **The roadmap as promises**: three to five things the video will open, each phrased as a secret or a stake ("वो खर्च
   जिसकी बात कोई नहीं करता", "वो फैसला जिसने..."). Then the start line, in this channel's own words.

Write **three complete hooks** with different scene types into `<slug>-hooks.md`, pick one, and say in one line why it
fits this topic. Never a greeting, a channel intro or an ask in the hook.

## 5. The body

Chapter order comes from the format's section in `references/study.md`. Through every chapter:

- **A turn every 20 to 40 seconds**: लेकिन, a question answered at once ("यह पैसा जाता कहां है? ..."), or talking straight
  to the viewer ("समझो...", "मान लीजिए...").
- **A strong re-hook every 60 to 90 seconds**, never more than about 2.5 minutes without one: a twist marker, a secret, the
  other side of the coin, putting the viewer in someone's place, dramatic irony ("उन्हें अंदाजा भी नहीं था कि..."), a setback
  chain and reversal, an escalating numbered list ("पहली वजह... चौथी और सबसे बड़ी"). Use the moves in the toolkit, in fresh
  words every time.
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
3. **The callback**: back to the opening scene, changed by what the viewer now knows ("अगली बार जब आप किसी ज्वेलरी शोरूम
   के शीशे के सामने खड़े हों...").
4. **One ask block**: send it to a specific friend ("उस दोस्त को भेजिए जो सोचता है कि..."), a personal comment question
   ("आपके घर की पहली गाड़ी कौन सी थी?") or let them pick the next topic, subscribe for the next video named with two
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

Aim for 2,200 to 2,800 Hindi words (14 to 18 minutes at 155 words a minute).

## 8. Check, then hand back

Run `casecheck.py` and save its output to `<slug>-check.txt`. Fix every FAIL. For each WARN, fix it or write one line in
the check file saying why it is right for this script. Save `--voice` output to `<slug>-script.txt` for reading aloud.

Hand back: the winning title and thumbnail words, the chosen hook in full plus one line on each alternative, the chapter
list with timings, the runtime, the checker summary, and any facts marked estimate or legend. Nothing here publishes.
The last line of every run is the question: **ship it, or change it?**
