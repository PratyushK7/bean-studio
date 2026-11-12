---
name: hindi-case-study
description: >-
  Writes the script for a long Hindi business case-study video (10 to 20 minutes) for the Hindi channel Decoding Vyapaar, the way
  the top Hindi business-documentary channels write theirs, learned from 45 transcripts (Shivanshu Agrawal, HiddenOps, Money Code,
  HinExp, ABFinDoc, Paisa Decode, Truth Finance and more, hits against flops). It builds a story engine first (one question with a
  surprising exact answer, a person with a wound and a want, physical stakes, costs as characters, reversals, plants and payoffs),
  then a beat sheet, three hooks, the spoken draft and eight revision passes, so the script has emotion, suspense and real
  re-hooks instead of a fact list. Formats: the economics of owning a business (told as an owner's story or to "you"), a company's
  rise or fall, a person's story as a thriller, a mystery, a list, a comparison. Output: a sourced script.json with a shot plan,
  checked by casecheck.py, and a free local preview. Use whenever the user asks for a Hindi script, a Hindi case study, a
  "business case study" or "economics of owning X" video, a Hindi documentary about a company or a businessman, or a script for
  Decoding Vyapaar or the Hindi channel, including from the Bean Studio Agent tab or Topics tab.
---

# hindi-case-study

A topic in, a script a Hindi viewer stays with to the end out. This skill stops at the script: the voice and the
visuals are a later step (each line already carries a visual note and a shot kind).

The order matters, and it is the lesson of the study: **engine, beats, hooks, lines, revision**. Writing lines straight from
the research produces a lecture with re-hooks sprinkled on (our first jewellery script: it passed every count and was dead).

```bash
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json           # the report: FAIL / WARN / PASS
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json --voice   # plain Devanagari narration
python ~/.claude/skills/hindi-case-study/preview.py <project>                         # free local listen (flat voice)
```

The checker catches broken rules (no engine, category chapters, stock re-hooks, an ask in the hook). Passing it is necessary
and nowhere near enough: the craft is judged by the revision passes in section 9.

## Before you write

1. Read `references/craft.md` in full (how the hits make a viewer feel, wonder and stay: the engine, the shapes, hooks,
   re-hooks, scene texture, closes, and the anti-example), then `~/.claude/youtube/voice-hindi.md` (the channel voice) and
   the section of `references/study.md` for your format plus its **What not to copy**. Do not write from memory of them.
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

## 1a. What decides a topic (measured 2026-11-12 on 10 channels' full catalogs, about 450 long videos, plus their thumbnails)

Packaging is not the filter: the flops have thumbnails as polished as the hits (Money Code's 2.2M dhaba and its 2.4K UPI video use the same
cut-away art). **The topic is.** Read this before picking one.

- **Winners are things the viewer can touch or has eaten, in their own street**: dhaba 2.2M, cement-steel dealer 1.2M, petrol pump 1.0M,
  mall, gym, kirana, tea stall, biryani, clothes shop, turf 1.1M, PS5 café 743K, sleeper bus 3.8M, bus 2.1M; household brands with a
  nostalgia or a fight: Haldiram's 12M, Nirma 9.2M, Hero vs Honda 1.5M, Tavera 1M, Big Bazaar, "Indian chips company destroyed Lay's" 2.8M.
- **Losers are institutions and abstractions**: UPI, bank, IPL, coaching industry, dark patterns, a private island, beauty parlour (all under
  4K at Money Code); personal-finance dilemmas (credit card, health claim, home loan: about 300 views each at Paisa Decode);
  geopolitics and current-news films (HiddenOps' Dhurandhar, Operation Sindoor: 0.1x its median); obscure brands (Pulse Candy,
  Old Monk, Royal Enfield, Groww). Copy-cat chasing kills: Rapido (777K once, then 560 / 5.8K / 11K), Ola, Zepto, Zee.
- **A small channel can still hit 1M**: Money Code (median 13K) and Paisa Decode (median 2.4K) did, on "economics of owning X" and a price in
  the title ("₹1,200/Hour Turf Business: Weekend Full, Phir Bhi Profit Kahan Gaya?" 1.1M). But the format is now swarmed by tiny copies
  (medical store, multiplex, wedding hall, school: 100 to 1K views each), so **the plain "economics of owning X" is no longer enough on its own**.
- **A covered topic repeats well**: DMart-in-trouble 1.9M, 3.3M, 551K, 212K on four channels; sleeper bus 3.8M and 207K; "Indian
  brand beats Lay's" 2.8M and 2.1M. The topic is shared; the channel's angle and execution decide the size.
- **Best new idea shape**: a household brand or product in a fight (Indian vs multinational, small vs big), told through the money in the thing
  the viewer holds (the 5-rupee packet: who gets what), with a ₹ number in the title. Check: can I name the object in the viewer's hand? Is there a
  villain or a rival? Is there a number that surprises?
- **Thumbnail pattern of the hits** (not a rule for what to draw, a pattern to match): one giant business or brand object, 2 to 4 huge
  words, a ₹ number or a rising/falling arrow, one emotional face (worried, hand on chin) for the story videos; a cut-away infographic with
  floating ₹ callouts for the economics videos; "11:30 PM, last flight" style time stamps on scam and downfall stories.

## 2. Research: `<slug>-research.md`

A facts table: claim, number, source (link or document), status: **verified** (official record, annual report, court
filing, regulator, two independent reputable reports), **reported** (one reputable outlet), **estimate** (industry
people, a model calculation; say so in the line) or **legend** (no record; say so or leave it out). At least five sources
for a story or person video, three for economics or compare. Prefer filings, court orders, company reports, RBI/SEBI/
ministry data, and established business press (Economic Times, Mint, Business Standard, BusinessLine, Reuters).

Real people: their documented words only. Dramatise with the scene (place, time, the phone ringing, the silence), not
with invented quotes. A reconstruction is marked ("उस दिन कुछ ऐसा माहौल रहा होगा"). Allegations are attributed and the
other side is given. For format A, a made-up model business with a made-up owner is fine and helps (study: "हाईवे फ्यूल
पॉइंट"). Say a MODEL NUMBER is a model number ("मान लीजिए", "हमारे हिसाब में"): that is about the money, which is the one
thing the viewer acts on. Never say the story or its people are fictional (see the rule below). Best of all is **the owner's story** (HiddenOps' sleeper bus, 3.6M, beat HinExp's 2.0M on the
same topic): invented recurring characters and real numbers, told as a plain story. **Never write a line that says the characters are
fictional, made up, "सिर्फ इस कहानी के किरदार", or that the story is imagined** (the channel rule; the hits that do it, HiddenOps, spend
the seconds on a disclaimer, ours never do). Tell it like it happened and keep every number honest. Invented characters suit this
channel's illustrated stills too.

## 3. Packaging first

Write three titles (English, like both reference channels, at most 70 characters, the known thing in the first three
words: "The Economics of Owning a Jewellery Shop", "How Hero Honda Split"; for format A also try PaisaDecodeHQ's Hinglish shape,
the customer's price first: "₹1,200/Hour Turf Business: Weekend Full, Phir Bhi Profit Kahan Gaya?") and two to four thumbnail words in Hindi or
Hinglish that add the stakes ("असली कमाई?", "भाई vs भाई"). The hook has to confirm whichever title wins. Lint them with
**yt-package** if time allows.

## 4. The engine, before a single line: `<slug>-engine.md`

The study's main finding (`references/craft.md`, read sections 1 to 3 now): a gripping script is not a fact list with re-hooks
sprinkled on. Every hit is built on six parts, and the facts arrive as consequences of what happens to someone. Write these in plain
English notes, short, before any Hindi:

1. **The question.** The one question the hook asks and the last minute answers. Its exact answer (from the research file, with the
   arithmetic shown), two or three wrong guesses the viewer will make, and why the true answer surprises. If it does not surprise,
   the angle is wrong: stop and find a sharper one before writing.
2. **The shape** from craft section 3 (A-story, A-explainer, B rise/fall, C thriller, mystery, list, compare), and one line on why.
   For format A prefer **A-story** (an owner's story: HiddenOps' sleeper bus beat HinExp's explainer 3.8M to 2.1M).
3. **The person we follow.** For A-story, invented characters (one, or two whose interests clash, like the buyer and the seller);
   for B and C, the real person; for A-explainer, *you*. Write: the **want** (one line of their own dialogue), the **wound** (a pain
   from the viewer's own life: a salary gone by the 25th, a boss who mocks, a debt, a humiliation in public), the **naive belief**
   (the viewer's belief, with the naive math), the **mistake** they will make that the viewer sees coming, and one habit or line
   that makes them specific. A real person's wound and want must be documented (research file); never invent them.
4. **The stakes**: two to four physical things put on the table, each with the moment it is put down (years of savings, a
   father's land, a wife's jewellery, house papers in a lender's safe, a friend who signs as guarantor, a daughter's wedding).
5. **The opposition with faces**: every share of the money as a character with a place and one line (the lender, the supplier,
   the tax, the landlord, the karigar, the agent), plus the rival or villain, plus the system (duty, permits, the bank).
6. **The dread**: the cold-open event (a disaster, a deadline, a humiliation, the peak before a fall) and the point where the
   story catches up with it (60 to 75% in A-story and C).
7. **The turns**: five to eight reversals, each marked up or down, each revealing one money fact. The line changes direction at
   least four times; the lowest point falls between 45% and 70%.
8. **The plants**: three to five small things put down early (an object, a line of dialogue, a number, a promise) and where
   each pays off.
9. **The payoff**: how the exact answer is staged (a countdown the viewer can follow), the irony that calls back the wound, the
   last turn, the final image back in the opening scene.
10. **The feeling map**: the six to eight feelings the viewer should feel, in order (curiosity, dread, pity, anger, laughter,
    hope, shock, pride), with the beat that causes each.

If the user is present and asked to see the plan, show these ten lines and wait. Otherwise go on.

## 5. The beat sheet: `<slug>-beats.md`

One row per beat (a beat is 15 to 40 seconds; 25 to 45 beats for 10 to 15 minutes), as a table with: time, **event** (what
happens, to whom, where), **feeling** (one word), **fact** (the number this event reveals, or a dash), **open questions** after this
beat (short names), **plant / payoff**. Rules:

- **Every beat is an event.** "Explain making charges" is not a beat; "the father reads the bill, puts his finger on 'making 12%'
  and asks: ये क्या है?" is. No fact without an event; at most two facts in a beat.
- **The question relay**: after every beat at least one named question is open, and a new one opens before an old one closes.
  The engine's big question stays open until the last 5%.
- **The feeling changes** at least every two beats; never three beats in a row with the same feeling.
- **Chapters (5 to 9) are named for what happens** ("The Night the Duty Fell", "Gurmeet's Dustbin"), never for a category
  ("Investment", "Revenue", "Expenses", "Profit", "Introduction", "Conclusion").
- Each chapter opens with a re-hook from craft section 5 that **promises something specific** or **raises the danger to someone we
  care about**, in fresh words.
- The biggest reveal sits in the middle third.

## 6. The hook (the first 20 to 60 seconds): `<slug>-hooks.md`

Write **three** hooks in different shapes from craft section 4. Every one must have: a concrete scene in sentence one (time,
place, a person, a thing you could photograph); a contradiction between what is seen and what is true; rupees or a life at
stake; the engine's question, as a guess with wrong options where there is money; and the promise of ONE specific reveal ("जवाब
आखिर में", "एक छोटी सी चीज...", "एक नंबर...").

- Format B: the short hook (20 to 40 s): year, place, a humble act or the peak, dramatic irony or "ऐसा क्या हुआ कि...", "यह कहानी
  है X की". Then straight into the origin.
- A-story and C: the cold open at the dread event, then the jump back ("यह कहानी उस रात से 11 महीने पहले शुरू होती है").
- Invented characters: no disclaimer, no line about them being made up. The hook goes straight on with the story.
- No greeting, no channel intro, no ask.

Pick with two tests and write the result under the hooks: the **scroll test** (read sentence one alone, then the first 15 seconds
alone: would a stranger stop scrolling for each?) and the **title test** (the hook confirms the title within 15 seconds).

## 7. Writing the lines

Write from the beat sheet, beat by beat, in the channel voice (craft section 6: HiddenOps' cinema in story beats, Money Code's
warmth in the explaining beats, "आप").

- **Scenes**: present tense; time, place, a sound, a light, one object; sentences of 4 to 12 words. Explaining: up to 25 words,
  one idea a line.
- **Show feelings through a cause**: an action, a silence, a reaction, a line of dialogue ("अड्डे पर सन्नाटा छा गया", "सरला कुछ नहीं
  बोली। पर देर रात तक लोहे की अलमारी के पास बैठी रही"). Never tell them ("उसकी सांस रुक गई", "चेहरे पर मुस्कान आ गई").
- **Dialogue** is short and does work: it humiliates, threatens, teaches or reveals. A mentor speaks in riddles and aphorisms.
  Real people say only their documented words; dramatise them with the scene, not invented quotes.
- **Every cost walks in** as a share-taker in a scene, with a face and one line, and the running count of what is left.
- **Sources stay in the research file and `sources`**, not read aloud. At most two or three authority lines a video, only where a
  number must be believed ("सरकारी रिकॉर्ड कहता है..."). Estimates are said as estimates inside the sentence ("मान लीजिए", "हमारे
  हिसाब में").
- **Talk to the viewer** throughout in A-explainer; in story shapes at the guess, the challenge ("आप भी यही सोच रहे हैं ना?"), the
  predictions ("आपको क्या लगता है?") and the close.
- **Humour once a chapter**, from a character's mistake or a sharp observation. **One image a chapter** that sticks.
- **Everyday spoken Hindi, not textbook Hindi.** Write the way a young Indian talks today: Hindi grammar with the English and
  Hinglish words everyone actually says. Use the word people use at the counter and on the phone: jewellery or ज्वेलर (not सर्राफ),
  ज्वेलरी मार्केट (not सर्राफा बाजार), नेकलेस (not हार), मेकिंग चार्ज (not बनवाई), प्रॉफिट (not मुनाफा), कस्टमर (not ग्राहक), सेल
  (not बिक्री), इंटरेस्ट (not ब्याज), रेट (not भाव), लेबर चार्ज (not मजदूरी), ऑर्गनाइज्ड, प्योरिटी, स्टॉक, EMI, GST, बैंक लिमिट.
  Keep the Hindi words that are still everyday (तिजोरी, दुकान, कमाई, हिसाब, भरोसा, कारीगर, गहना). The test: would a friend say it
  in a voice note? If it sounds like a newspaper or a school book, swap it. Mind the verbs: do not swap "हार" the noun and break
  "हार गया" the verb. Numbers as spoken (डेढ़ लाख, ढाई सौ).
- **Banned, because they promise nothing**: "लेकिन कहानी यहीं खत्म नहीं होती", "आगे जो हुआ वो चौंकाने वाला था", "ये तो बस शुरुआत थी"
  (unless the same sentence names the thing), "आइए जानते हैं", "इस वीडियो में हम जानेंगे", "दोस्तों" as an opener.

## 8. The close (the last 60 to 90 seconds)

In this order (craft section 7): **the answer, staged** as a countdown the viewer can follow; **the irony** that calls back the
wound; **one last turn**; **a last image back in the opening scene**; **the maxim** (one line the viewer could repeat) and **the
observation test** (one thing to go and look at next time); **one specific comment question** (two-sided or personal); the ask
(send it to a friend who believes the naive math, the Hype button while the channel is small); the next video named; the
sign-off from `voice-hindi.md`. No ask anywhere before this.

## 9. Revision passes (all of them; write what each one changed into `<slug>-check.txt`)

1. **Scroll test, every 30 seconds**: name the open question, the feeling and the new picture in that window. A window with no
   open question or no feeling is rewritten.
2. **Lecture test**: three or more lines in a row that only inform become a scene, a line of dialogue, a guess, or are cut.
3. **Puppet test**: does every person want something, lose something and change? Do we learn the person's pain within their
   first 20 seconds on screen?
4. **Specificity test**: every scene has a time, a place and an object; every share-taker a face and a line; every number the
   event behind it.
5. **Payoff ledger**: list every plant and promise with the line that pays it; the hook's question is answered with the exact
   number, and that number matches the research arithmetic.
6. **Sweeps**: the banned lines, told feelings, sources read aloud.
7. **Side by side**: read our first 90 seconds next to the first 90 seconds of the closest hit in craft.md (same shape), then one
   middle stretch next to theirs. If a stranger would pick theirs, rewrite ours and say what changed.
8. **The free listen**: `python ~/.claude/skills/hindi-case-study/preview.py <project>` renders the whole script with a local
   voice (free, flat, no emotion) so the user can hear the flow before the paid voice. It judges the story and the pacing, not
   the delivery.

## 10. `script.json`

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

## 11. Check, then hand back

Run `casecheck.py` and save its output to `<slug>-check.txt`, under the notes from the revision passes. Fix every FAIL. For each
WARN, fix it or write one line saying why it is right for this script. Save `--voice` output to `<slug>-script.txt`.

Files in the project: `<slug>-research.md`, `<slug>-engine.md`, `<slug>-beats.md`, `<slug>-hooks.md`, `script.json`,
`<slug>-check.txt`, `<slug>-script.txt`, and (after section 9.8) `preview-local.mp3`.

Hand back: the winning title and thumbnail words; the engine in five lines (the question and its exact answer, the person and
their wound, the stakes, the lowest point, the payoff); the chosen hook in full plus one line on each alternative; the chapter
list with timings; the runtime; what the revision passes changed; the checker summary; the shot counts and estimated cost; and
any facts marked estimate or legend. Nothing here publishes. The last line of every run is the question: **ship it, or change it?**
