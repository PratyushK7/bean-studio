---
name: hindi-case-study
description: >-
  Script architect for Decoding Vyapaar, the Hindi/Hinglish business-documentary and explainer channel. It writes a 10 to
  20 minute YouTube script that sounds like a sharp storyteller talking to a friend and is built so the viewer cannot stop
  watching: one central question with a surprising and exact answer, a person with something to lose, open loops that
  pay off, and re-hooks and pattern interrupts at a planned rhythm. It never invents a fact. It learned from 45 transcripts
  of the top Hindi business channels (Shivanshu Agrawal, HiddenOps, Money Code, HinExp, ABFinDoc, Paisa Decode) and from
  our own two rejected drafts. Formats: the economics of owning a business (as an owner's story or told to "you"), a
  company's rise or fall, a person's story as a thriller, a mystery, a list, a comparison. Output: a sourced, fact-linked
  script.json (with its loop ledger and shot plan), a readable script.md (title, hook, narration, re-hooks and ending)
  checked by casecheck.py, and a free local listen. Use it whenever the user asks for a Hindi or Hinglish script, a Hindi
  case study, a "business case study" or "economics of owning X" video, a Hindi documentary about a company or a
  businessman, or a script for Decoding Vyapaar or the Hindi channel, including from the Bean Studio Agent tab or Topics
  tab. Also use it whenever a Hindi script needs fixing because it "feels off", is boring or sounds robotic.
---

# Decoding Vyapaar: the script architect

**Core principle: don't just explain information. Turn it into a story the viewer cannot resist finishing.** Every fact
arrives as something that happens to someone. Every section leaves a question the viewer needs answered. Every question
gets an answer worth the wait.

This skill stops at the script. The voice, the pictures and the edit start only after the owner approves the script
(see "Where this sits in the workflow" at the end).

```bash
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json          # the report: FAIL / WARN / PASS / INFO
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json --md     # writes <slug>-script.md, the copy the owner reads
python ~/.claude/skills/hindi-case-study/casecheck.py <project>/script.json --voice  # plain Devanagari narration for TTS
python ~/.claude/skills/hindi-case-study/preview.py <project>                        # free local listen (flat voice)
```

Projects live in `C:\Users\praty\youtube\channels\hindi\videos\<slug>\` (slug: lowercase English words and dashes, e.g.
`jewellery-shop-economics`). Make the folder if it is missing.

## Two failures to learn from

1. **The lecture** (jewellery v1). Its chapters were named for cost categories, the hero wanted nothing, and the sources were
   read aloud. It passed every count in the checker and was dead.
2. **The checklist script** (jewellery v2, which the owner said "feels so off"). It was written to satisfy the checker, so every
   device showed:
   - a question bolted onto every scene ("क्या वो अंदर आएंगे?")
   - a mentor who spoke only in riddles, and stingers such as "असली चोट अगले नंबर से लगने वाली थी" and "चौथी वाली आपको सबसे
     ज्यादा चुभेगी"
   - an order to write the math down
   - three time frames in two minutes (Budget 2024, "इस धनतेरस", "इस साल मई"), and two central questions fighting each other
   - the same bill read out three times, and about 40 numbers in five minutes
   - a father and son talking with no speaker tags, which one narrator's voice cannot make clear
   - "हमारे हिसाब में" three times, and six asks in the last six lines

   It scored 0 FAIL and 0 WARN. Each device was right on its own. Together they sounded like a template.

The lesson of both: **devices are seasoning; the story is the meal.** Tell the story first. Add a device only where a listener
would really drift, and never let it show as a device. A script written to pass a checker sounds like one.

## How it should sound

- **A brilliant storyteller explaining something to a friend over chai.** Sure of the facts, enjoying the story, a little
  amused. Never lecturing, never shouting, never selling. The listener is smart and has never read a balance sheet.
- **Natural conversational Hinglish, written in Devanagari.** Hindi grammar with the English words Indians actually say: प्रॉफिट,
  मार्जिन, लोन, EMI, स्टॉक, रेट, ऑफर, डिस्काउंट, ब्रांड, शोरूम, कस्टमर, सेल, कैश, बिल, सेविंग, बैंक लिमिट. Brand and people's
  names may stay in Latin letters (Titan, SBI). Keep the Hindi words that are still everyday (दुकान, कमाई, हिसाब, भरोसा,
  तिजोरी, कारीगर, गहना).
- **Talk to the viewer as "आप", warmly.** Spoken glue makes it sound spoken (अब, तो, देखिए, यानी, मतलब, ना?). Use it the way a
  person does, unevenly, never at the start of every line.
- **Two registers.** Story beats are a camera: present tense, short sentences, a time, a place, a sound, one object. Explaining
  beats are the friend: one idea a line, and an Indian analogy from daily life for anything abstract (a train ticket, the kirana
  shop's credit, an EMI, a wedding budget, cricket). One analogy per idea.
- **Attitude about money, not about politics.** The narrator has a view of how the money really works ("सुनने में बढ़िया लगता है।
  हिसाब कुछ और कहता है।") and some dry wit: an understatement, a character's own mistake, a sharp aside. Once or twice a chapter.
  Never a joke at a community or at a victim.
- **The friend test**, on every line: would you say this to a friend in a voice note? If it sounds like a newspaper, a
  textbook, a TV serial, a motivational reel or a chatbot, rewrite it.

### Write for the ear

The viewer hears each sentence once, at about 155 words a minute, in one narrator's voice. The TTS reads `hi` exactly as written.

1. **Sentences**: 4 to 12 words in scenes and up to 18 in explaining, with one idea each and one sentence per script line (two
   very short ones may share). Nothing over 22 words.
2. **Punctuation is breath**: "।" is a stop, "," a short pause, "?" a lift. Use no brackets, slashes or symbols the voice cannot
   say: write करीब, not ~, and परसेंट, not %. Spell every number the way it is said (डेढ़ लाख, ढाई सौ, साढ़े तीन करोड़).
3. **Numbers the ear can hold.**
   - Round them in the story ("करीब तीन लाख"). Be exact only where the exactness is the point, which is the payoff.
   - One number a sentence; two only to compare. Land the number at the end of the sentence.
   - After a big number, say what it means in human terms ("यानी हर सौ रुपये की सेल पर डेढ़ रुपया").
   - For the payoff the viewer needs to remember **at most three numbers**: introduce them early and repeat them. Every other
     number is felt as a comparison, not memorised.
   - Read a bill or a table aloud line by line **at most once** in a video.
4. **Dialogue in one voice.** The listener cannot see who is speaking.
   - Name the speaker before the quote, in the same line: "गोयल जी कैलकुलेटर उठाते हैं और कहते हैं, ...".
   - Allow at most two turns of back-and-forth, then the narrator speaks again.
   - Anything longer than about 12 words becomes reported speech.
   - Dialogue sounds like that person (age, town, trade), not like the narrator, and never states the theme of the video ("मैं
     सीखने जा रहा हूं कि वो जीतते कैसे हैं" is the writer talking, not a son).
   - Real people say only their documented words.
5. **Time runs in a straight line.**
   - The story has one "now" and at most one flashback.
   - Stamp every jump ("दो साल पहले", "उसी रात", "अगली सुबह").
   - Never put "इस साल" and another year in the same minute. Give the year, or say how it relates to the story's now.
6. **One name per person.** The narrator always calls each person the same thing. Other characters may address them
   differently, but only inside dialogue.
7. **Eyes closed, it still works.** The narration never depends on the picture ("जैसा आप स्क्रीन पर देख रहे हैं"). The screen
   adds to the narration and never replaces it.
8. **Say it once.** The same information twice is padding, unless it is a deliberate callback that now means something new.

### The everyday word, not the textbook word

| Say | Not |
|---|---|
| ज्वेलर, ज्वेलरी मार्केट, नेकलेस | सर्राफ, सर्राफा बाजार, हार (the noun; "हार गया" the verb is fine) |
| मेकिंग चार्ज, लेबर चार्ज | बनवाई, मजदूरी |
| प्रॉफिट, कमाई, कस्टमर, सेल, इंटरेस्ट, रेट | मुनाफा, आमदनी, ग्राहक, बिक्री, ब्याज, भाव |
| और, पर/लेकिन, इसलिए, के लिए, से | तथा/एवं, किंतु/परंतु, अतः, हेतु, द्वारा |
| बहुत, लगता है, बाद में, जरूरी, शायद, आज | अत्यंत/अत्यधिक, प्रतीत होता है, पश्चात/उपरांत, आवश्यक, संभवतः, वर्तमान में |
| ऑर्गनाइज्ड, प्योरिटी, स्टॉक | संगठित, शुद्धता, भंडार |

### Never write these

- **Generic AI and template lines**: "आइए जानते हैं", "इस वीडियो में हम जानेंगे", "क्या आपने कभी सोचा है कि", "आज के इस दौर में",
  "दिलचस्प बात यह है कि", "गौर करने वाली बात", "चलिए गहराई से समझते हैं", "यह सफर", "अनसुनी दास्तान", "चौंकाने वाला सच", "आप
  हैरान रह जाएंगे", "रोंगटे खड़े", "महत्वपूर्ण भूमिका", "न केवल... बल्कि", "अंत में" as a summary, "तो दोस्तों", and "दोस्तों" as
  an opener.
- **Stock re-hooks that promise nothing**: "लेकिन कहानी यहीं खत्म नहीं होती", "आगे जो हुआ वो चौंकाने वाला था", "ये तो बस शुरुआत
  थी".
- **Overworked shapes**:
  - "यह सिर्फ X नहीं था, यह Y था" more than once a video
  - three adjectives in a row
  - a moral at the end of every paragraph
  - a rhetorical question after every scene
- **Told feelings** ("उसकी सांस रुक गई", "चेहरे पर मुस्कान आ गई"). Show the cause: an action, a silence, a reaction.
- **Meta orders to the viewer** ("इसे लिख लीजिए", "ये याद रखिएगा"): at most one a video.
- **A device that could be pasted into any other video unchanged.** A re-hook names this video's specific thing.
- **Example lines from this skill or its references, word for word.** They show the move; the words must be new every time.
  Any one device's wording appears at most once a video.
- **Another channel's catchphrases** (HinExp's "बबल फोड़ने आया हूं", ABFinDoc's "जय हिंद" sign-off).

## The retention toolkit

How the hits hold a viewer. Plan each device in the beat sheet (step 5), place it only where a listener would drift, write it
so it does not show, and mark it in `script.json` (`open`, `close`, `tag`) so the checker can audit the rhythm. Real lines
and why they work: `references/craft.md` sections 4 and 5.

| Device | What it is | How often |
|---|---|---|
| **Hook** | The first 15 s: a scene you could photograph, a contradiction between what is seen and what is true, and something at stake. | once |
| **Curiosity gap** | Tell enough for the viewer to know an answer exists, not enough to guess it. The specific beats the vague: "पांच रुपये की एक चीज" beats "एक ऐसी चीज". | inside every chapter |
| **Open loop** | A question or promise opened now and paid later, numbered L1, L2... in the ledger. L1 is the central question: opened in the hook, closed in the last 10 to 15%. Open the next loop before you close the current one (a relay). | 2 or 3 open at every moment; never zero, never more than four |
| **Re-hook** | A line at a chapter start or a lull that renews the reason to stay, by promising something specific or raising the danger to someone we care about. | every 60 to 120 s; never more than 2.5 min without one |
| **Pattern interrupt** | Change how the viewer is listening. Cut from explaining to a scene; after long sentences, a two-word line; ask the viewer a question; jump scale (one shop to the whole country) or time; give a character an unexpected line; make a joke; drop the music. | every 45 to 90 s; never the same kind twice in a row |
| **Reveal** | A fact that changes how the viewer sees what came before. Build from small to large: the biggest twist in the middle third, the central revelation at 75 to 90%. | 4 to 7 a video |
| **Reversal** | The story's direction flips, up or down. The lowest point falls between 45 and 70%. | 5 to 8 a video |
| **Payoff** | A plant or promise comes back, ideally in the plant's own words, so the viewer feels the click. Every plant pays off and every promise is kept. | every loop and plant |

**Psychological triggers**, and how to pull each one honestly:

- **Curiosity**: the gap above, kept specific.
- **Surprise**: break an expectation you first built on purpose. There is no surprise without a set-up.
- **Emotional connection**: a person with a want and a wound, both shown within their first 20 seconds.
- **Relatability**: the viewer's own life (their family's jeweller, their bill, a salary gone by the 25th).
- **Contrast**: two shops, two prices, then and now, how it looks and what it is.
- **Anticipation**: a countdown, a deadline, the disaster from the cold open that we know is coming.
- **Stakes**: what the money *is*. A daughter's wedding, the family's house, a father's land: physical things put on the table.

The feeling map in the engine (step 4) names the trigger each chapter leans on. Never let three beats in a row carry the same
feeling.

**Storytelling.** Use a real person, or, in an economics video, invented characters with real numbers. Give them a want, a wound,
a naive belief and a mistake we see coming. Give the conflict a face: every cost is a character who walks in and takes a share.
Add twists, and end with a payoff.

**Pacing.** Cut every explanation the story does not need: if a fact changes neither what a character does nor what the viewer
believes, it goes. A chapter runs 1.5 to 2.5 minutes. Enter each scene late and leave it early.

## The shape of every script

| Part | Where (share of runtime) | What it must do |
|---|---|---|
| 1. Opening hook | 0 to 15 s | A concrete scene in sentence one (time, place, a person, a thing you could photograph), the contradiction, and the stakes. No greeting. |
| 2. The central question | 15 to 60 s | L1, asked as a guess with wrong options where there is money; the promise of one specific reveal; the viewer's gain in one plain line; the jump into the story. |
| 3. Context through story | to about 20% | The person, their want and wound, the naive belief (the viewer's own, with the naive math), and the first share-taker. |
| 4. Progressive reveal | 20 to 50% | Each chapter reveals one piece and opens the next question. A false high comes before the fall. |
| 5. Twists and rising stakes | 45 to 75% | The lowest point, the cold open catching up, and the biggest twist in the middle third. |
| 6. The central revelation | 75 to 90% | L1 answered, staged so the viewer can follow it. It must surprise and be exactly right. |
| 7. The ending | last 60 to 90 s | The insight in one line the viewer could repeat, the last image back in the opening scene, then one comment question, one ask, the next video in one line, and the sign-off. |

The format shapes in `references/craft.md` section 3 (A-story, A-explainer, B rise/fall, C thriller, mystery, list, compare)
refine these percentages. Do not use "चलिए शुरू करते हैं" as a seam between part 2 and part 3; a time stamp does that job better.

## Non-negotiables

1. **Never fabricate** a fact, statistic, quote, date or event. Every factual line links to a row of the research file
   (`facts`). A model number is said as a model number, and a legend as a legend.
2. **Fact-check** every claim a viewer would repeat or act on: two independent sources or one primary record.
3. **No clickbait the video cannot deliver.** Every promise in the title, the thumbnail and the hook maps to the line that pays
   it (step 3).
4. **Every section gives a reason to keep watching**: some loop is open at every moment.
5. **Indian examples and analogies**, from the viewer's daily life.
6. **No predictable transitions** ("अब बात करते हैं...", "चलिए आगे बढ़ते हैं") and **no generic conclusion** ("तो उम्मीद है आपको
   समझ आया होगा...").
7. **Accuracy beats engagement.** If a twist needs a stretched fact, lose the twist.

Channel rules:
- No greeting and no channel intro. No ask before the last 90 seconds.
- Invented characters are never called fictional; give no disclaimer and tell it straight.
- Real people say only their documented words. A reconstruction is marked as one ("उस दिन माहौल कुछ ऐसा रहा होगा").
- Allegations are attributed, and the other side is given.
- No politics, religion, caste or community generalisations, and no buy/sell advice.
- The channel voice and sign-off are in `~/.claude/youtube/voice-hindi.md`.

## 1. Topic and format

A topic works when all three hold:

- **The viewer can picture it in the first sentence**: a business they use (the bus, the petrol pump, the jeweller), a brand
  they grew up with, or a name every Indian knows.
- **There is a gap between what everyone assumes and what is true.** Write the assumption down in one Hindi line.
- **It has money math or a human conflict** (a rivalry, a revenge, a fall, a rise from nothing).

**A topic someone has already covered is fine, and often the best bet, if you repeat it cleverly.** The demand is proven, and
the viewer clicks a title they already trust.
- Search YouTube first and list who has covered it and with how many views.
- Then pick a **different angle**, not a retelling:
  - a different question in the title ("where does the money actually go?" instead of "how did X rise?")
  - the mechanism nobody put on screen (unit economics, a ledger, a loan, a contract clause)
  - a human on the other side (the small shopkeeper, the employee, the customer)
  - a story shape the competitor does not use
- Keep the proven hit's title formula, but never its script, its examples or its order.
- Write the competitor list and your angle in `<slug>-research.md` under "Covered by".

If a topic misses one of the three, say which and offer a sharper angle before writing.

**What decides a topic.** Measured 2026-11-12 on 10 channels' full catalogues (about 450 long videos):
- Packaging is not the filter: the flops' thumbnails are as polished as the hits'. **The topic is.**
- Winners are things the viewer can touch or has eaten, in their own street: a dhaba (2.2M), a cement dealer (1.2M), a petrol
  pump (1.0M), a turf (1.1M), a sleeper bus (3.8M). Household brands with nostalgia or a fight also win: Haldiram's 12M, Nirma
  9.2M, Hero vs Honda 1.5M.
- Losers are institutions and abstractions (UPI, banks, the coaching industry), personal-finance dilemmas, geopolitics, obscure
  brands, and copy-cat chasing.
- The plain "economics of owning X" is now swarmed by tiny copies. It needs a sharper angle: a fight, a person, a price in the
  title.
- **The best new idea shape** is a household brand or product in a fight (Indian against multinational, small against big),
  told through the money in the thing the viewer holds. Check three things: can I name the object in the viewer's hand, is there
  a rival, and is there a number that surprises?

Then pick the format. B and C are the safest bet: the only two channels whose typical video beats 300K (Shivanshu Agrawal and
HiddenOps) tell one company's or one person's story from a humble start to its peak or fall.

| Format | `format` | Use for | Study videos |
|---|---|---|---|
| A. Economics of owning X | `economics` | a business the viewer meets as a customer | bus 2.0M, petrol pump 1.1M; told as a story: sleeper bus 3.6M |
| B. A company's rise, split or fall | `story` | a brand with nostalgia or a betrayal; "X is in trouble" | Haldiram's 12M, Byju's 10M, Nirma 9.2M |
| C. A person's story | `person` | rivalry, revenge, rags to riches, a big bet | Ambani 1.4M, Rolls-Royce 1.2M, Jhunjhunwala 976K |
| D. Two people, one decision | `compare` | rent vs buy, SIP vs plot, job vs business | rent vs buy 1.1M |

The full data, thumbnail patterns and channel roster are in `references/study.md`.

## 2. Research: `<slug>-research.md`

Read `references/craft.md` in full and `~/.claude/youtube/voice-hindi.md` before this step. For your format, also read its
section of `references/study.md` and that file's **What not to copy**. Do not work from memory of them.

Build a facts table with these columns: **id** (F1, F2...), claim, number, source (a link or a document) and status. The status
is one of:
- **verified**: an official record, an annual report, a court filing, a regulator, or two independent reputable reports
- **reported**: one reputable outlet
- **estimate**: from industry people or a model calculation; say so inside the line
- **legend**: no record; say so, or leave it out

Find at least five sources for a story or person video, and three for economics or compare. Prefer filings, court orders, company
reports, RBI/SEBI/ministry data and established business press (Economic Times, Mint, Business Standard, BusinessLine,
Reuters).

For format A, a model business with invented people is fine, and it helps. Put its arithmetic in a **model table** with ids M1,
M2... and the working shown, so every model number traces to a fact. Say a model number as an estimate inside the sentence, and
vary the words ("मान लीजिए", "मोटा-मोटा", "करीब"); never repeat one tag. Best of all is the owner's story: invented recurring
characters and real numbers, told as a plain story (HiddenOps' sleeper bus, 3.6M, beat HinExp's explainer, 2.0M, on the same
topic).

Real people: use their documented words only. Dramatise with the scene, not with invented quotes.

Two checks that v3 of the jewellery script failed:
- **The window.** Every percent change has a window. Match it to the scene's date. A quarterly-average year-on-year figure
  is not "since last Dhanteras". In v3, the +45% was a July–September average; Dhanteras to Dhanteras was +6 to 9%.
- **The law.** What a character does on screen is legal, or the script says it is not. For example, cash receipts of ₹2 lakh
  or more are barred (Income-tax Act, section 269ST), so a ₹2.6 lakh restock is paid by bank transfer, not in notes.

## 3. Packaging and the promise list

- **Titles**: write three, in English or the Hinglish price-first shape, at most 70 characters, with the known thing in the first
  three words. Examples: "The Economics of Owning a Jewellery Shop"; "₹1,200/Hour Turf Business: Weekend Full, Phir Bhi Profit
  Kahan Gaya?".
- **Thumbnail words**: two to four, in Hindi or Hinglish, that add the stakes.
- **The promise list**: every promise the title, the thumbnail and the hook make, each with the line that pays it. A promise
  with no paying line is clickbait: fix the title or the script.
- The hook must confirm the winning title within 15 seconds. Lint titles with **yt-package** if time allows.

## 4. The engine: `<slug>-engine.md` (one page, before any Hindi)

Write it in short English notes:

1. **The throughline**, in one sentence: "[person] wants [X], but [obstacle]; the video answers [L1] with [the exact,
   surprising answer]." Every chapter must move this sentence forward. **One central question only.** Every other question
   serves it, and one that does not gets cut.
2. **L1 and its answer.** Show the exact answer with the arithmetic from the research file, two or three wrong guesses the viewer
   will make, and why the truth surprises. If it does not surprise, the angle is wrong: find a sharper one before writing.
3. **The viewer's gain**: the one thing they will be able to do or see for themselves by the end, concrete and checkable (read a
   bill, spot a trick, run a number on their own shop). It is promised in the first 60 seconds and paid in the close.
4. **The shape** (craft section 3) and one line on why. For format A, prefer A-story.
5. **The person.** Their want (one line of their own dialogue), their wound (a pain from the viewer's own life), their naive
   belief (the viewer's belief, with the naive math), the mistake we see coming, and one habit that makes them specific. A real
   person's wound and want must be documented.
6. **The stakes**: two to four physical things put on the table, each with the moment it is put down.
7. **The opposition, with faces**: every share of the money as a character with a place and one line, plus the rival and the
   system (duty, permits, the bank).
8. **The time line**: the story's "now", the one flashback if there is one, and every real date the script mentions in
   relation to that now. If a real event falls outside the story's frame, either it enters as a flashback or it is cut.
9. **The turns**: five to eight reversals, each marked up or down and each revealing one money fact. The lowest point falls
   between 45 and 70%.
10. **Plants and payoffs**: three to five small things put down early (an object, a line, a number) and where each pays off.
11. **The feeling map**: six to eight feelings in order, each with the beat that causes it and the trigger behind it.

If the user is present and asked to see the plan, show the throughline, L1 and its answer, and the shape, then wait. Otherwise
go on.

## 5. The beat sheet and the loop ledger: `<slug>-beats.md`

**The beat sheet** has one row per beat. A beat lasts 15 to 40 seconds, which gives 25 to 45 beats for 10 to 15 minutes.
Columns: time, **event** (what happens, to whom, where), **feeling and trigger**, **fact** (its research id, or a dash),
**loops open** after the beat, and **device** (re-hook, interrupt, reveal, reversal, payoff, or none).

- **Every beat is an event.** "Explain making charges" is not a beat. "The father puts his finger on 'making 12%' and asks
  what it is" is. No fact appears without an event, and a beat holds at most two facts.
- **The relay**: after every beat at least one loop is open, and a new one opens before an old one closes.
- **The feeling changes** at least every two beats.
- **Chapters (5 to 9) are named for what happens** ("The Night the Duty Fell"), never for a category ("Investment", "Revenue",
  "Profit", "Introduction", "Conclusion").
- **The device column follows the cadence of the toolkit.** In any 90-second window with no reversal, write which device carries
  it. If the honest answer is "nothing", the beat is cut or rebuilt; do not paper over it with a stinger.

**The loop ledger** is a table: id, the question in the viewer's words, the beat that opens it, the beat that closes it, and how
it closes (which plant's words come back). L1 is the central question. A loop that never closes is a broken promise. A loop
closed within a few seconds of opening is not a loop.

## 6. Three hooks: `<slug>-hooks.md`

Write three hooks in different shapes from craft section 4. Every one needs:
- a concrete scene in sentence one
- a contradiction
- rupees or a life at stake
- L1 as a guess with wrong options where there is money
- the promise of one specific reveal
- the viewer's gain in one plain line within 60 seconds

Shape by format:
- **Format B**: the short hook (20 to 40 s): year, place, a humble act or the peak, then dramatic irony.
- **A-story and C**: a cold open at the dread event, then the jump back, stamped ("ये सब उस रात से ग्यारह महीने पहले शुरू हुआ").

**One time frame in the hook.** If the cold open sits at a different date from the story's now, the jump back is the only other
time mentioned before the story starts.

Pick with two tests and write the result under the hooks:
- **Scroll test**: read sentence one alone, then the first 15 seconds alone. Would a stranger stop scrolling for each?
- **Title test**: does the hook confirm the title within 15 seconds?

## 7. The draft

Write `script.json` directly from the beat sheet, beat by beat, in two passes:

1. **Tell the story plainly**, as if to a friend, with no devices: the events, the people, the money, in order. Read it back. If
   the plain version is not interesting, no device will save it; go back to the engine.
2. **Season it.** Add a device only at the lulls the beat sheet marks: a re-hook at chapter starts, an interrupt in long
   explaining stretches, the loop openings and closings. Then mark each one on its line (`open`, `close`, `tag`).

While writing, keep these in hand:
- **Every cost walks in** as a share-taker in a scene, with a face and one line, plus the running count of what is left (said as
  a felt amount, not a ledger).
- **Sources stay in the research file**, not in the narration. Use at most two authority lines a video, only where a number
  must be believed.
- **Talk to the viewer** at the guesses, the predictions, the challenge to their naive math, and the close. A story narrated
  with no "आप" in it for five minutes has lost the friend.
- **Humour once a chapter**, from a character's mistake or a sharp observation. **One image a chapter** that sticks.

## 8. Revision passes

Run all of them, and write what each one changed into `<slug>-check.txt`.

1. **Throughline**: say the video in the one-sentence throughline. Name each chapter's contribution to it in five words. A
   chapter that cannot be named is cut or merged.
2. **Time line**: list every time anchor in order (the checker prints them as INFO). There is one now, at most one flashback,
   every jump is stamped, and nothing is ambiguous to a listener.
3. **Table read**: read every line aloud as the narrator, at speaking pace. Mark every place you stumble, every quote where you
   cannot tell who speaks, every number you cannot recall ten seconds later, and every word nobody says. Fix them all.
4. **Friend test**: would you send each line to a friend as a voice note? Rewrite the newspaper, textbook, serial and chatbot
   lines.
5. **Bored viewer, every 30 seconds**: name the open question, the feeling and the new picture in that window. A window with
   none of the three is cut or rewritten. Then name the three windows where you would most likely skip, and fix those three
   first.
6. **Loop ledger**: every loop closes, every promise in the promise list is kept, and L1 is answered with the exact number. That
   number matches the research arithmetic.
7. **Number diet**: list every number in order. Cut each number the story does not need. Check the three payoff numbers: are
   they introduced early and repeated?
8. **Repetition and template sweep**: repeated phrases (the checker lists them), repeated information, device lines that could
   sit in any video, the "never write" list, told feelings, sources read aloud.
9. **Fact pass**: every factual line carries its `facts` ids. Each id's status is right and is said honestly (an estimate as an
   estimate, a legend as a legend). Fix anything that drifted while writing.
10. **Side by side**: read our first 90 seconds next to the first 90 seconds of the closest hit in craft.md (same shape), then one
    middle stretch next to theirs. If a stranger would pick theirs, rewrite ours and say what changed.
11. **The free listen**: `preview.py` renders the whole script with a free local voice. It is flat and has no emotion, so it
    judges the story and the pacing, not the delivery.

## 9. The files: `script.json` and `<slug>-script.md`

```json
{
  "title": "The Economics of Owning a Jewellery Shop",
  "alt_titles": ["...", "..."],
  "thumbnail": "असली कमाई?",
  "format": "economics",
  "question": "Of a ₹3 lakh necklace bill, how much is the jeweller's own?",
  "answer": "About ₹4,600 (M7)",
  "gain": "Read any jewellery bill: making charge percent and the HUID",
  "loops": {"L1": "इस बिल में ज्वेलर का अपना कितना?", "L2": "..."},
  "sources": ["https://...", "BIS hallmarking notification, 2021"],
  "lines": [
    {"hi": "...", "visual": "...", "kind": "still", "chapter": "The Night the Duty Fell", "open": "L1", "facts": ["F16"]},
    {"hi": "...", "visual": "...", "kind": "card", "screen": "₹2,94,580", "tag": "gain"}
  ]
}
```

**Line fields:**
- `hi`: the narration in Devanagari, exactly as the narrator says it, one sentence a line.
- `visual`: what is on screen, in English, specific enough to draw (place, people, action, the one object). Use a new picture
  every one to three lines, and describe recurring characters in the same words every time.
- `kind`: `still` (a picture with a camera move), `card` (a code graphic for a number, a ledger or a map), or `hero` (a paid
  image-to-video clip; on hold until the channel earns, so use it rarely).
- `chapter`: on the first line of each chapter, a 3 to 5 word English title named for an event. It becomes the YouTube chapter.
- `screen` (rare, on under a third of the lines): Hinglish in Latin letters, at most 6 words (a number, a name, the key word).
- `facts`: research ids (F3, M2) on every line that states a fact or a model number.
- `open` / `close`: loop ids from the ledger (a string or a list).
- `tag`: `rehook`, `interrupt`, `reveal`, `reversal`, `payoff` or `gain`.
- Sound plan (optional): `music` (`tense`, `warm`, `curious`, `sad`, `hopeful`) on the line where a mood starts; `amb` for a
  looping bed; `sfx` (`"coin@1.0"`) on money moments and reveals only. Never under every line.

**Shot plan:** roughly 70 to 80% `still` and 20 to 30% `card`, with a card on every money-math line, never two cards in a row,
and a new picture every one to three lines. The edit rules (shot lengths, camera moves, the render checks) are in
`references/production.md`. The script does not need them, but the visual notes should make them possible.

**Length:** aim for 2,200 to 2,800 Hindi words (14 to 18 minutes at 155 words a minute). For a 10 to 15 minute video, 1,600 to
2,300.

Then run `casecheck.py script.json --md`. It writes **`<slug>-script.md`**, the production-ready script the owner reads: the
title and alternatives, the thumbnail words, the central question and answer, the gain, the loop ledger with open and close
times, then every chapter with timestamps, each line with its re-hook, loop and interrupt marks and its visual.

## 10. The editor's score: `<slug>-score.md`

Before handing back, change roles. You are now an independent senior script editor who did not write this script and owes
its writer nothing. Score the script, fix only what is weak, then score it again.

**Step 1: score.** Score ten dimensions, equal weight, each 0 to 10. Give each score one line of evidence quoted from the
script, with its timestamp.

| Dimension | What a 9 looks like |
|---|---|
| Opening hook | a picture, a price and a contradiction in 15 seconds; the title's promise is restated by 0:30 |
| Storytelling | a person who wants something, makes choices and pays for them; concrete details; one time line |
| Curiosity and open loops | 2 to 3 loops open at every moment; each closes with something worth the wait |
| Retention and re-hooks | a reason to stay every 60 to 120 s; no stock re-hooks; no stretch where the narrator lectures |
| Natural Hinglish and dialogue | every line passes the friend test; speakers named; nobody talks like a serial or a slogan |
| Emotional connection | we feel what the person feels, shown in gestures, never told |
| Pacing | no stretch drags; the information is spread out; the back third does not stall before the payoff |
| Educational value and clarity | the viewer can explain the mechanism afterwards; no logic gap a smart viewer would catch |
| Factual accuracy and research | every number traces to a row; windows, dates, arithmetic and the law all check |
| Ending and payoff | L1 answered with the exact number; the promises kept; a last image, not a summary |

The overall score is the mean of the ten. A dimension scoring 8 or more is good: leave it alone. A dimension below 8 is
weak.

**Step 2: the weak areas.** For each weak dimension, say what is wrong, quoting the line with its timestamp. Mark each fault:
- **critical**: a wrong fact, number or date window, the law, or a logic error a viewer would catch
- **minor**: craft

Never invent a weakness to have something to fix.

**Always run the fact audit, whatever the scores.**
- Re-verify every number that carries the story against a current source.
- Check every window against the scene's date.
- Redo every piece of arithmetic.
- Check what the characters do against the law.
- Hunt for metaphors a viewer could take literally. An example: "the machine is in your pocket", when the app checks a
  hallmark record and does not test the gold.

**Step 3: targeted fixes.**
- Rewrite only the weak lines and paragraphs.
- Keep the strong hooks, characters, transitions and loops, and keep the order.
- Keep the runtime within 5%.
- Verify a fact before changing it, and add the new research rows.
- Where retention is weak because the narrator explains, play the explanation as a scene with a person.
- Cut stock re-hooks, artificial drama and AI phrasing.
- Do not tune every sentence for retention. Natural storytelling matters more. Do not change good content just to make it
  different.

Back up the old version (`v3/`, `v4/`...) before editing, and rebuild with the same builder.

**Step 4: score again.** Use the same rubric. Show a table of the original score against the revised score. Say which
weaknesses were fixed, and name the remaining issues honestly. The target is 8.5 or more. If the script falls short, say what
blocks it; never inflate a score. A score reflects the script, not the effort.

Write steps 1 to 4 into `<slug>-score.md`.

## 11. Check, then hand back

Run `casecheck.py` and save its output to `<slug>-check.txt`, under the notes from the revision passes. Fix every FAIL. For each
WARN, either fix it or write one line saying why it is right for this script. **Never add a line only to satisfy a rule.** Save
the `--voice` output to `<slug>-script.txt`, and write `<slug>-script.md` with `--md`.

The project folder ends up holding: `<slug>-research.md`, `<slug>-engine.md`, `<slug>-beats.md`, `<slug>-hooks.md`,
`script.json`, `<slug>-script.md`, `<slug>-check.txt`, `<slug>-score.md`, `<slug>-script.txt` and `preview-local.mp3`.

Hand back:
- the winning title and thumbnail words
- the throughline sentence, and L1 with its exact answer
- the chosen hook in full, plus one line on each alternative
- the chapter list with timings, and the runtime
- the loop ledger in one line each
- what the revision passes changed
- the editor's score table (original against revised) and the remaining issues
- the checker summary
- any facts marked estimate or legend
- the full path of `<slug>-script.md`

Nothing here publishes. The last line of every run is the question: **ship it, or change it?**

## Where this sits in the workflow

```
1 Topic and angle  ->  2 Script (this skill)  ->  GATE A: the owner reads script.md and hears preview-local.mp3 (free)
3 Voice: a 60 s sample of the hook in the chosen voice (cheap), then the full voice (paid: the owner OKs the cost first)
4 Pictures from the final script's visual notes, upscaled locally (WaveSpeed's ESRGAN, free)
5 Edit: a 60 s sample in the chosen style  ->  GATE B: the owner OKs it  ->  full render  ->  QC (freeze, black, motion)
6 Music and mix (real tracks only, credits in the description)  ->  7 Packaging: title, thumbnail, description, chapters
```

Nothing paid starts before Gate A. After the voice, a changed line means re-voicing that line, so the script freezes at Gate A.
