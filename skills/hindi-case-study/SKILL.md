---
name: hindi-case-study
description: >-
  Script architect for Decoding Vyapaar, the Hindi/Hinglish business-documentary and explainer channel. It writes a 10 to
  18 minute YouTube script that sounds like a sharp storyteller talking to a friend: one central question with a surprising
  and exact answer, one clear storyline, one takeaway worth remembering, one idea explained at a time, and reveals that
  earn the next minute. It never invents a fact and never passes an illustration off as real. It learned from 45 transcripts
  of the top Hindi business channels (Shivanshu Agrawal, HiddenOps, Money Code, HinExp, ABFinDoc, Paisa Decode) and from
  our own drafts. Formats: the economics of owning a business (as an owner's story or told to "you"), a company's rise or
  fall, a person's story as a thriller, a mystery, a list, a comparison. Output: a sourced, fact-linked script.json (its
  central question, answer, takeaway and shot plan), a readable script.md checked by casecheck.py and by a short editorial
  check, and a free local listen. Use it whenever the user asks for a Hindi or Hinglish script, a Hindi
  case study, a "business case study" or "economics of owning X" video, a Hindi documentary about a company or a
  businessman, or a script for Decoding Vyapaar or the Hindi channel, including from the Bean Studio Agent tab or Topics
  tab. Also use it whenever a Hindi script needs fixing because it "feels off", is boring or sounds robotic.
---

# Decoding Vyapaar: the script architect

**Core principle: one video is one central question, one clear storyline and one useful takeaway, told as a story.** Every
fact arrives as something that happens to someone. Each chapter teaches one thing and leaves the viewer wanting the next.
Clarity beats completeness: a research finding that does not help answer the central question stays in the research file.

**The test of every script:** a first-time viewer easily follows the story, wants to keep watching, and learns something worth
remembering. The editorial check (section 10) asks exactly that.

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

## Three failures to learn from

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

3. **The crowded script** (jewellery, as voiced). A good story carrying too many lessons: the bill's six shares, the year's
   profit, the FD comparison, the gold bet in the safe, the duty cut, the showroom's gold loan, Titan's margin, the carat meter,
   hallmarking and HUID, in 14 minutes. The takeaway split in two (where the money goes, and how to check a bill), and the
   characters spoke in quotable one-liners. A first-time viewer keeps one or two of those ideas (craft.md section 12).

The lesson of all three: **devices are seasoning; the story is the meal, and one meal is enough.** Tell one story first. Add a
device only where a listener would really drift, and never let it show as a device. A script written to pass a checker sounds
like one.

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
- **One idea at a time.** Name a new idea in plain words the first time ("गोल्ड मेटल लोन, यानी सोना किराए पर"), let it happen
  once in a scene, and only then bring in the next. A line never carries two new ideas, and a chapter teaches one thing.

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
   - People talk plainly: short, a little rough, half-finished. A character gets at most one quotable line in the whole video;
     a cast that speaks in epigrams ("सोना बिका नहीं, बस जगह बदली है") sounds written.
   - Real people say only their documented words.
   - **Mark every quote with `say`** (who speaks, and where their words start) so each person is read in their own voice. The
     narrator reads the tag ("रमेश जी हंसकर कहते हैं,") and the person reads the words; the line stays one line, so the shots, the
     graphics and the timings keep their numbers. Full form in section 12.
5. **Time runs in a straight line.**
   - The story has one "now" and at most one flashback.
   - Stamp every jump ("दो साल पहले", "उसी रात", "अगली सुबह").
   - Never put "इस साल" and another year in the same minute. Give the year, or say how it relates to the story's now.
6. **One name per person.** The narrator always calls each person the same thing. Other characters may address them
   differently, but only inside dialogue.
7. **Eyes closed, it still works.** The narration never depends on the picture ("जैसा आप स्क्रीन पर देख रहे हैं"). The screen
   adds to the narration and never replaces it.
8. **Say it once.** The same information twice is padding, unless it is a deliberate callback that now means something new.
9. **The surprising word lands last.** A sentence pulls when its reveal sits at the end: "उस बिल में सबसे महंगी चीज़ सोना नहीं था।
   वो था एक परसेंट — मेकिंग चार्ज।" beats "मेकिंग चार्ज उस बिल की सबसे महंगी चीज़ थी।" Delay the key noun where it costs nothing;
   never pad a sentence just to delay it.

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

## Keeping the viewer: progression, not quotas

The hits hold a viewer because something keeps changing: a new fact changes what we believed, a person's situation gets better
or worse, the central question gets closer to its answer. The devices below are the visible surface of that. Counting them does
not separate hits from flops (`references/craft.md` section 1), so there are no quotas: use a device where the story needs it,
write it so it does not show, and leave it out where the scene holds on its own. Real lines and why they work: craft sections 4
and 5.

| Device | What it is | Use it when |
|---|---|---|
| **Hook** | The first 15 s: a scene you could photograph or a surprising true fact, a contradiction between what is seen and what is true, and something at stake. | always, once |
| **Central question (L1)** | The one question the video answers, opened in the hook and answered exactly near the end. | always, once |
| **Curiosity gap** | Tell enough for the viewer to know an answer exists, not enough to guess it. The specific beats the vague: "पांच रुपये की एक चीज" beats "एक ऐसी चीज". | the answer is coming and worth knowing |
| **Smaller loop** (L2, L3...) | A question the story itself raises and later answers. Most videos need one to three; each must serve L1. | the story really raises it; never to fill a lull |
| **Re-hook** | A line that renews the reason to stay by naming this story's next specific thing or the danger to someone we care about. | a chapter seam or a lull the plain story cannot carry |
| **Change of pace** | Cut from explaining to a scene, a very short line after long ones, a jump in scale or time, a character's unexpected line, the music dropping. | a long explaining stretch; never by schedule |
| **Reveal** | A fact that changes how the viewer sees what came before. Build from small to large; the central one comes last. | it is true, it matters to L1, and it was set up |
| **Reversal** | The story's direction flips, up or down. | it follows from what came before |
| **Payoff** | A plant or promise comes back, ideally in its own words, so the viewer feels the click. Every promise is kept. | every promise and plant |

**Curiosity without artificial suspense.** A pull is honest when the next minute pays it. Teasing an answer the video then
delays for the sake of it, announcing a shock that is not one ("जिसके बाद वो घर ही नहीं गए" when he only sat on the step), or
inventing danger the facts do not support all spend the viewer's trust. The honest pulls are surprise (an expectation you set
up, then break), a person we care about with something at stake (what the money *is*: a daughter's wedding, the family's
house), contrast (two shops, then and now, how it looks against what it is), and the viewer's own life (their family's
jeweller, their bill).

### Where viewers skip, and how to defuse each spot

A viewer's thumb hovers over the 10-second jump the whole video. These are the stretches where it lands. Defuse them in the
beat sheet, not with a stinger pasted on top:

1. **Context before conflict.** Backstory before we care is the most skipped minute on YouTube. Start with the trouble; feed
   the backstory in half-sentences after the viewer already needs it ("राजेश — जिसने ये दुकान अपने ससुर से उधार लेकर खोली थी —
   ...").
2. **A chapter that opens with setup.** Chapter seams are the biggest exit doors: the viewer feels a section end and decides.
   So a chapter never ends settled and never opens slow. Close every chapter mid-motion, on the new question. Open the next
   one inside a scene: by its second sentence, someone is doing something.
3. **The lull after a reveal.** The seconds after a payoff are a natural "I got what I came for" exit. Let the reveal's own
   consequence raise the next question soon after ("अब राजेश को पता था पैसा कहां जाता
   है। दिक्कत ये थी — रोकने का रास्ता गैरकानूनी था।").
4. **A run of numbers.** Three numbers in a row and the ear gives up. One number a sentence; the rest of the math happens as a
   scene (a finger moving down a bill, a character's face at the total).
5. **Explaining past the click.** The moment the viewer gets it, every further sentence is a skip. Stop one beat earlier than
   feels safe. If the explanation needs a second example, the first one was the wrong example.
6. **A recap.** Never re-tell what the viewer just watched. A callback is allowed only when the old line now means something
   new.
7. **The tail after the answer.** Once L1 is paid, the video is on borrowed time: last image, one question, one ask, out.
   Keep everything after the central revelation under 90 seconds.

**Storytelling.** Use a real person, or, in an economics video, invented characters with real numbers (introduced as an
example, see the non-negotiables). Give them a want, a wound, a naive belief and a mistake we see coming. Give the conflict a
face: every cost is a character who walks in and takes a share. **Keep a character or a subplot only if the main story needs
it**: a person who neither changes what happens nor helps the viewer understand L1 is cut, however vivid.

**Pacing.** Cut every explanation the story does not need: if a fact changes neither what a character does nor what the viewer
believes about L1, it goes. Chapters usually run 1.5 to 2.5 minutes. Enter each scene late and leave it early.

## The shape of every script

| Part | Where (share of runtime) | What it must do |
|---|---|---|
| 1. Opening hook | 0 to 15 s | A concrete scene in sentence one (time, place, a person, a thing you could photograph), the contradiction, and the stakes. No greeting. |
| 2. The central question | 15 to 60 s | L1, asked as a guess with wrong options where there is money; the promise of one specific reveal; the takeaway in one plain line; the jump into the story. |
| 3. Context through story | to about 20% | The person, their want and wound, the naive belief (the viewer's own, with the naive math), and the first share-taker. |
| 4. Progressive reveal | 20 to 50% | Each chapter reveals one piece and opens the next question. A false high comes before the fall. |
| 5. Twists and rising stakes | 45 to 75% | The lowest point, the cold open catching up, and the biggest twist in the middle third. |
| 6. The central revelation | 75 to 90% | L1 answered, staged so the viewer can follow it. It must surprise and be exactly right. |
| 7. The ending | last 60 to 90 s | The insight in one line the viewer could repeat, the last image back in the opening scene, then one comment question, one ask, the next video in one line, and the sign-off. |

The shares are where the hits usually put each part, not targets. The format shapes in `references/craft.md` section 3
(A-story, A-explainer, B rise/fall, C thriller, mystery, list, compare) refine them. Do not use "चलिए शुरू करते हैं" as a seam between part 2 and part 3; a time stamp does that job better.

## Non-negotiables

1. **Never fabricate** a fact, statistic, quote, date or event. Every factual line links to a row of the research file
   (`facts`). A model number is said as a model number, and a legend as a legend.
2. **Fact-check** every claim a viewer would repeat or act on: two independent sources or one primary record.
3. **No clickbait the video cannot deliver.** Every promise in the title, the thumbnail and the hook maps to the line that pays
   it (step 3).
4. **Every section gives a reason to keep watching**, and the reason is real: the central question is still open, or the
   story has just raised a question the next minutes answer.
5. **Indian examples and analogies**, from the viewer's daily life.
6. **No predictable transitions** ("अब बात करते हैं...", "चलिए आगे बढ़ते हैं") and **no generic conclusion** ("तो उम्मीद है आपको
   समझ आया होगा...").
7. **Accuracy beats engagement.** If a twist needs a stretched fact, lose the twist.
8. **The viewer always knows what kind of claim they hear**:
   - a **verified fact** is said plainly
   - an **estimate** or model number is said as one, in varied words ("करीब", "मोटा-मोटा", "मान लीजिए")
   - an **illustrative scenario** (invented people, their scenes and their words) is introduced once as an example, early and
     in one natural line, before its first person speaks: "रमेश जी की दुकान एक मिसाल है, पर उसका हर नंबर असली बाजार से है।"
     It is never a legal disclaimer and never repeated; after it, tell the story straight. List the invented people in
     `invented` (section 9).

Channel rules:
- No greeting and no channel intro. No ask before the last 90 seconds.
- Invented people, scenes and dialogue are never presented as real events (rule 8).
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
- Search YouTube first (step 2 opens with the competitor research).
- Then pick a **different angle**, not a retelling:
  - a different question in the title ("where does the money actually go?" instead of "how did X rise?")
  - the mechanism nobody put on screen (unit economics, a ledger, a loan, a contract clause)
  - a human on the other side (the small shopkeeper, the employee, the customer)
  - a story shape the competitor does not use
- Keep the proven hit's title formula, but never its script, its examples or its order.

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

**Research broadly, select carefully, explain simply.** The goal is not another version of an existing video; it is the clearest,
most engaging and most useful video on the topic.

### Competitor research first: the top five videos

```bash
python tools/yt_research.py search "<topic in English>" "<topic in Hinglish>" "<the closest equivalent>"   # candidates, by views
python tools/yt_research.py fetch <project> <id> <id> <id> <id> <id>    # details, chapters, description, transcript, top comments
```

1. **Pick the top five** on the exact topic or its closest equivalent: strong views, relevance, engagement (likes, comments), a
   credible creator. The fetch writes `research/competitors/<id>.md` (one per video) and `competitors.json`. Copy the table into
   the research file under **"Top videos on this topic"**: title, channel, views, upload date, duration, link, and the date the
   numbers were read.
2. **Study each one** from its transcript, chapters, description and comments: how it opens and creates curiosity, how it
   explains the hard idea, its facts, numbers and claims, its story shape and takeaway, and what the comments ask, doubt or
   add (a question many people ask is a gift; a correction in the comments is a lead to check).
3. **Their claims go into the facts table like any other**, checked independently, preferably against a primary source. A
   number that appears only in competitor videos is not verified by being repeated; mark it **disputed** when sources
   disagree, and give both sides or leave it out.
4. **The opportunity**, under **"What they do well, what they miss"**: what is already explained well, and what is missed,
   oversimplified, wrong or left unanswered (the comments often say). The angle comes from there; write it in one line.
5. **Our script is our own.** Our own central question, storyline, examples and explanations. Never copy a transcript, a
   distinctive phrase, a joke, a scene, or a creator's unique story structure, and never stitch other scripts into a
   rewritten one. Their transcripts stay in `research/competitors/` and never next to the draft.

When a transcript, comment list or view count is not available (the fetch says so and why), write the limitation down. Never
fill it in, and never invent a source, a view count or an audience reaction. If YouTube asks for a sign-in or a bot check, stop
and say so.

### The facts table

Build a facts table with these columns: **id** (F1, F2...), claim, number, source (a link or a document) and status. The status
is one of:
- **verified**: an official record, an annual report, a court filing, a regulator, or two independent reputable reports
- **reported**: one reputable outlet
- **estimate**: from industry people or a model calculation; say so inside the line
- **disputed**: reliable sources disagree; give both sides in the line, or leave it out
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

End the research file with **"Not in this video"**: the good findings that do not help answer L1. Writing them down makes them
easy to leave out, and they are the next video's material.

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
3. **The takeaway** (`gain`): the one thing the viewer will remember, and can do or see for themselves, by the end: concrete and
   checkable (read a bill, spot a trick, run a number on their own shop). One, not two. It is promised early and paid in the
   close.
   **The ideas the viewer must learn to get there**, in order: usually three to five, one per chapter at most. Anything else
   goes to "Not in this video".
4. **The shape** (craft section 3) and one line on why. For format A, prefer A-story.
5. **The person.** Their want (one line of their own dialogue), their wound (a pain from the viewer's own life), their naive
   belief (the viewer's belief, with the naive math), the mistake we see coming, and one habit that makes them specific. A real
   person's wound and want must be documented.
6. **The stakes**: the physical things put on the table, each with the moment it is put down.
7. **The opposition, with faces**: every share of the money as a character with a place and one line, plus the rival and the
   system (duty, permits, the bank). Only the ones the story needs.
8. **The time line**: the story's "now", the one flashback if there is one, and every real date the script mentions in
   relation to that now. If a real event falls outside the story's frame, either it enters as a flashback or it is cut.
9. **The turns**: the moments the story changes direction, each marked up or down and each revealing one idea from item 3.
10. **Plants and payoffs**: the small things put down early (an object, a line, a number) and where each pays off.
11. **The feeling map**: the feelings in order, each with the beat that causes it. The feeling should not sit still for long.
12. **Who is real**: each person, real (documented words only) or invented (introduced once as an example).

If the user is present and asked to see the plan, show the throughline, L1 and its answer, and the shape, then wait. Otherwise
go on.

## 5. The beat sheet and the loop ledger: `<slug>-beats.md`

**The beat sheet** has one row per beat. A beat usually lasts 15 to 40 seconds. Columns: time, **event** (what happens, to
whom, where), **feeling**, **idea** (which of the engine's ideas it teaches, or a dash), **fact** (its research id, or a dash),
and **device** (a reveal, reversal or payoff; usually none).

- **Every beat is an event.** "Explain making charges" is not a beat. "The father puts his finger on 'making 12%' and asks
  what it is" is. No fact appears without an event, and a beat holds at most two facts.
- **Beats chain with "लेकिन" or "इसलिए", never "और फिर".** Read the event column top to bottom joining each row to the next
  with one of the three. If only "and then" fits, the second beat is a list item, not a story beat: cut it, or find what in
  the first beat forces it. (A story is causes; a Wikipedia page is "and then".)
- **One new idea at a time.** Read the idea column: a beat teaches at most one new idea, and the next idea waits until the last
  one has happened in a scene.
- **Chapters (usually 5 to 8) are named for what happens** ("The Night the Duty Fell"), never for a category ("Investment",
  "Revenue", "Profit", "Introduction", "Conclusion").
- **A stretch where nothing changes** (no new fact, no turn for the person, no step toward L1) is cut or rebuilt. Do not paper
  over it with a stinger.

**The loop ledger** is a short table: id, the question in the viewer's words, the beat that opens it, the beat that closes it,
and how it closes. L1 is the central question. Add a smaller loop only when the story itself raises the question. A loop that
never closes is a broken promise; one closed within a few seconds is not a loop.

## 6. Three hooks: `<slug>-hooks.md`

Write three hooks in different shapes from craft section 4. Every one needs:
- a concrete scene in sentence one
- a contradiction
- rupees or a life at stake
- L1 as a guess with wrong options where there is money
- the promise of one specific reveal, which the video really delivers
- the takeaway in one plain line within the first minute or so

And three hard rules, because the first 30 seconds decide more than the rest of the script together:
- **The first five words hold something concrete**: a time, a place, a rupee amount, a person doing something or a surprising
  true fact — never a
  generality the voice has to climb out of ("रात के ग्यारह बजे, दुकान का शटर आधा गिरा है" starts; "भारत में सोने का बाज़ार
  बहुत बड़ा है" is a skip).
- **No sentence in the first 30 seconds could open any other video.** Read each one alone: if it would fit a different
  topic, replace it with this video's own detail.
- **The hook spends the video's most arresting image.** Not a teaser of it, the image itself: the strongest single picture
  the research produced goes in the first 15 seconds, and the script earns it back later by explaining what it really meant.
  Saving the best image for the middle is saving it for people who already left.

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
2. **Season it, lightly.** Where the plain version really drags, add what fixes it: a scene in place of an explanation, a
   sharper reveal, a re-hook that names the next specific thing. Where it does not drag, add nothing. Mark L1's opening and
   answer (`open`, `close`) and any real reveal, reversal or payoff (`tag`); the marks are notes for the reader of script.md,
   not targets.

While writing, keep these in hand:
- **Every cost walks in** as a share-taker in a scene, with a face and one line, plus the running count of what is left (said as
  a felt amount, not a ledger).
- **Sources stay in the research file**, not in the narration. Use at most two authority lines a video, only where a number
  must be believed.
- **Talk to the viewer** at the guesses, the predictions, the challenge to their naive math, and the close. A story narrated
  with no "आप" in it for five minutes has lost the friend.
- **Humour where it comes naturally**, from a character's mistake or a sharp observation, and **an image that sticks** in most
  chapters. Never force either.

## 8. Revision passes

Run all of them, and write what each one changed into `<slug>-check.txt`.

1. **Throughline and focus**: say the video in the one-sentence throughline. Name each chapter's contribution to it in five
   words, and the one idea it teaches. A chapter that cannot be named is cut or merged; a character or subplot that serves
   no chapter is cut.
2. **Time line**: list every time anchor in order (the checker prints them as INFO). There is one now, at most one flashback,
   every jump is stamped, and nothing is ambiguous to a listener.
3. **Table read**: read every line aloud as the narrator, at speaking pace, as a friend's voice note. Mark every stumble, every
   quote where you cannot tell who speaks, every number you cannot recall ten seconds later, every word nobody says, and every
   newspaper, textbook, serial or chatbot line. Fix them all.
4. **First-time viewer, every 30 seconds**: in each window, does something change (a fact, the person's situation, a step
   toward L1), and could someone new to the trade follow it? A window that fails either is cut or rewritten. Then name the
   three windows where you would most likely skip, and fix those three first.
5. **Promises**: every loop closes, every promise in the promise list is kept, and L1 is answered with the exact number. That
   number matches the research arithmetic. Cut any suspense line the next minute does not pay.
6. **Number diet**: list every number in order. Cut each number the story does not need. Check the three payoff numbers: are
   they introduced early and repeated?
7. **Repetition and template sweep**: repeated phrases (the checker lists them), repeated information, device lines that could
   sit in any video, the "never write" list, told feelings, sources read aloud.
8. **Fact pass**: every factual line carries its `facts` ids. Each id's status is right and is said honestly (an estimate as an
   estimate, a legend as a legend), and the invented people are introduced as an example before they first speak. Fix
   anything that drifted while writing.
9. **Side by side**: read our first 90 seconds next to the first 90 seconds of the closest hit in craft.md (same shape), then one
   middle stretch next to theirs. If a stranger would pick theirs, rewrite ours and say what changed.
10. **The free listen**: `preview.py` renders the whole script with a free local voice. It is flat and has no emotion, so it
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
  "gain": "Most of a jewellery bill is gold passing through; the jeweller earns on the making charge and gambles on the gold he holds",
  "invented": ["ramesh", "ankit", "nandu"],
  "loops": {"L1": "इस बिल में ज्वेलर का अपना कितना?", "L2": "..."},
  "sources": ["https://...", "BIS hallmarking notification, 2021"],
  "lines": [
    {"hi": "...", "visual": "...", "kind": "still", "chapter": "The Night the Duty Fell", "open": "L1", "facts": ["F16"]},
    {"hi": "...", "visual": "...", "kind": "card", "screen": "₹2,94,580", "tag": "gain"}
  ]
}
```

**Top-level fields:** `question` (L1, one question), `answer` (exact, with its research id), `gain` (the one takeaway), and
`invented`: the `who` names of every invented person who speaks (empty or absent when everyone is real). The checker looks
for the example line before the first of them speaks.

**Line fields:**
- `hi`: the narration in Devanagari, exactly as the narrator says it, one sentence a line.
- `visual`: what is on screen, in English, specific enough to draw (place, people, action, the one object). Use a new picture
  every one to three lines, and describe recurring characters in the same words every time. These notes are the brief for
  the visual plan (`visual-plan.json`, `references/production.md` step 1). The plan, not the note, sets the framing, the
  light and the continuity. Never ask for a diagram or readable text in a picture: that is a graphic.
- `kind`: `still` (a picture with a camera move), `card` (a code graphic for a number, a ledger or a map), or `hero` (a paid
  image-to-video clip; on hold until the channel earns, so use it rarely).
- `chapter`: on the first line of each chapter, a 3 to 5 word English title named for an event. It becomes the YouTube chapter.
- `screen` (rare, on under a third of the lines): Hinglish in Latin letters, at most 6 words (a number, a name, the key word).
- `facts`: research ids (F3, M2) on every line that states a fact or a model number.
- `open` / `close`: loop ids from the ledger (a string or a list). L1's are required.
- `tag` (optional): `reveal`, `reversal`, `payoff`, `rehook`, `interrupt`, `gain` (the line that promises the takeaway) or
  `example` (the line that introduces the invented people). Tag what is there; never add a line to have something to tag.
- `say` (on every line where a person speaks): `{"who": "ramesh", "from": "धनतेरस के एक दिन"}`. `from` is where their words start; the
  narrator reads everything before it. Add `to` where they stop and the narrator resumes, or leave `from` out when the whole line is
  theirs. A list of marks covers a line with two speakers. `who` is a short lowercase name that matches `voice-cast.json`.
- Sound plan (optional): `amb` for a looping bed; `sfx` (`"coin@1.0"`) on money moments and reveals only, never under every line.
  `music` tags are only a fallback: the real music is planned after the script is approved, in `audio/music-plan.json` (section 12).

**Shot plan:** roughly 70 to 80% `still` and 20 to 30% `card`, with a card on every money-math line, never two cards in a row,
and a new picture every one to three lines. The edit rules (shot lengths, camera moves, the render checks) are in
`references/production.md`. The script does not need them, but the visual notes should make them possible.

**Length:** as long as the story needs and no longer: usually 1,600 to 2,500 Hindi words (10 to 16 minutes at 155 words a
minute). When in doubt, cut; never pad to reach a length.

Then run `casecheck.py script.json --md`. It writes **`<slug>-script.md`**, the production-ready script the owner reads: the
title and alternatives, the thumbnail words, the central question, answer and takeaway, who is invented, the loops with open
and close times, then every chapter with timestamps, each line with its marks and its visual.

## 10. The editorial check: `<slug>-score.md`

Before handing back, change roles. You are now an independent senior script editor who did not write this script and owes
its writer nothing. Read it as a **first-time viewer** who knows nothing about the trade: can they follow it, do they want the
next minute, and what will they remember tomorrow? Score, fix only what is weak, then score again.

**Step 1: score.** Six questions, each 0 to 10, each with one line of evidence quoted from the script with its timestamp.

| | The question | What a 9 looks like |
|---|---|---|
| **Clarity** | Could a first-time viewer follow every line on one hearing? | one idea at a time, each named in plain words; numbers the ear can hold; natural spoken Hinglish; always clear who speaks and when |
| **Story focus** | Is it one question, one storyline, one takeaway? | every chapter, character and subplot moves L1 forward; nothing is there only because the research found it |
| **Pacing** | Does something change in every stretch? | no lecture, no recap, no explaining past the click; the tail after the answer is short |
| **Engagement** | Would they choose to keep watching? | a hook from a familiar situation or a surprising fact; a person we care about; reveals that change the picture; no suspense the next minute does not pay |
| **Accuracy** | Is every claim true, and is its kind clear? | every number traces to a row; windows, arithmetic and the law check; estimates said as estimates; invented people introduced as an example |
| **Educational value** | What will they remember and be able to do? | the takeaway can be said in one line, the viewer could explain the mechanism to a friend, and it is clearer or more useful than the top five videos on the topic |

The overall score is the mean. A question scoring 8 or more is good: leave it alone. Below 8 is weak.

**Step 2: the weak areas.** For each weak question, say what is wrong, quoting the line with its timestamp. Mark each fault:
- **critical**: a wrong fact, number or date window, the law, or a logic error a viewer would catch
- **minor**: craft

Never invent a weakness to have something to fix.

**Always run the fact and logic audit, whatever the scores.**
- **Re-verify** every statistic, date and claim that carries the story against a current source.
- **Check every window** against the scene's date.
- **Recompute every financial example** with a short script, from the model rows to each spoken number. Check that the
  shares add up to the total, that percentages match their base (with or without GST, before or after interest), and that
  every comparison holds.
- **Compare like with like.** Name the metric on both sides: operating margin against EBIT margin, not against profit after
  interest. A stock gain against a year's profit is a comparison of sizes, not of income, so the script must not treat it as
  earnings.
- **Give every number a status** in the score file: verified, reported, estimate or model. Model numbers are said as
  approximations ("करीब", "मोटा-मोटा").
- **Flag unsupported claims** (a superlative, a "most", an "everywhere") instead of letting them stand as facts.
- **Check the law**: what the characters do on screen is legal.
- **Check realism against the trade.** A jeweller's books go to a CA. One karigar does not earn ₹21 lakh a year alone. A
  dealer restocks the whole day's sales, not one necklace.
- **Hunt for metaphors** a viewer could take literally. An example: "the machine is in your pocket", when the app checks a
  hallmark record and does not test the gold.

**Always run the skip audit, whatever the scores.** Read the script as the impatient viewer whose thumb is on the 10-second
jump: at every chapter seam, every reveal, every math stretch and the tail after the central revelation, ask "if I jumped
ahead here, would I feel I missed something?" List the three stretches where the honest answer is no, with timestamps, and
fix them using "Where viewers skip" above — by cutting or restructuring, never by pasting a stinger. If pass 4 of the
revision already named three windows, check its fixes held; do not re-litigate windows that now pull.

**Always run the naturalness check, whatever the scores.**
- Characters sound like real Indian people in their own trade and age, not like a serial, a slogan or a chatbot.
- Cut artificial drama: a narrator announcing a feeling ("वो बात जो कोई बेटा नहीं कहना चाहता") instead of showing a gesture.
- Cut repeated hooks and suspense the story does not need.
- Cut dialogue that sounds polished: a cast trading quotable lines, or a character stating the lesson.

**Fix these faults wherever they are**, even in a section that scores 8 or more. They are errors, not style. If the audit
finds a fault an earlier score missed, lower that score and say so.

**Step 3: targeted fixes.**
- Rewrite only the weak lines and paragraphs.
- Keep the strong hooks, characters, transitions and loops, and keep the order.
- Do not add length; keep the runtime within 5% unless a cut makes it shorter.
- Verify a fact before changing it, and add the new research rows.
- Where retention is weak because the narrator explains, play the explanation as a scene with a person.
- Where focus is weak, cut: a whole idea, character or chapter that does not serve L1 moves to "Not in this video". Cutting is
  allowed to shorten the runtime.
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
- the top five videos on the topic (one line each), and what ours explains that they do not
- the throughline sentence, and L1 with its exact answer
- the chosen hook in full, plus one line on each alternative
- the chapter list with timings, and the runtime
- the takeaway in one line, and the ideas taught on the way
- who is invented and the line that introduces them
- what the revision passes changed
- the editorial check table (original against revised) and the remaining issues
- the checker summary
- any facts marked estimate or legend
- the full path of `<slug>-script.md`

Nothing here publishes. The last line of every run is the question: **ship it, or change it?**

## 12. After the script is approved: the voice cast and the music plan

Both are decided once the story is fixed and before the voice is paid for. Neither changes a word of the script.

**The voice cast** (`<project>/voice-cast.json`, the channel's narrator and pool in `channels/hindi/voice-cast.json`):
- One entry per person who speaks (every `who` in the script's `say` marks). Each has a Sarvam voice (speaker and pace) and a free
  Kokoro voice (voice, speed and pitch). The narrator is the locked channel voice and is never reassigned.
- **Separate people by pitch and age, not by name.** The pool lists only Sarvam speakers that were actually generated, with their
  measured median pitch (Varun 87 Hz, Kabir 106, Aditya 119, Amit 128, Rahul 131, Rohan 178, Neha 180, Priya 225, Kavya 229, Ritu 235):
  an old man gets a low voice and a slower pace, a young one the high male voice, a woman one of the four women's voices.
  Two people who never share a scene may share a voice; two in the same scene never do.
- Sarvam bulbul:v3 has no pitch dial and no emotion dial, so a voice is chosen by speaker and pace. Kokoro has two Hindi male voices,
  so its people are told apart by a pitch factor (above 1 higher and younger, below 1 lower and older).
- **Hear before paying.** `preview.py <project> --cast-sample` (free) and `vyapaar_voice.py <project> --cast-sample` (paid, about
  1,500 characters) make one real line per person. A voice nobody has heard is a guess: the owner chooses by ear.
- Bean Studio's Pipeline tab has a Voice cast panel for all of this.

**The music plan** (`<project>/audio/music-plan.json`): the music follows what is said and felt, not the chapter.
- Read the whole script and put a cue `{"line": 33, "mood": "sad", "why": "..."}` on every emotional shift: about one every 20 to
  30 seconds, never one per chapter, always with the reason. A cue holds until the next. Moods: `curious`, `tense`, `dread`, `sad`,
  `bittersweet`, `flashback`, `hopeful`, `warm`, `silence`.
- **Drop the music (`silence`) under the sharpest lines**: the number that answers the central question, the line that lands the
  loss. A bare voice is the loudest thing in the video. Bring it back on the next cue.
- Match the music to the line, not to the topic: a joke in a sad chapter gets a lighter cue; the lowest point is `dread` or `sad`,
  never `curious`. Light follows the feeling map, and so does the music.
- `audio/music-map.json` lists several tracks per mood from the channel library `channels/hindi/music/` (Kevin MacLeod, CC BY 4.0;
  credit them in the description, see `CREDITS.md`). The renderer levels every track to one bed level, rotates the tracks when a mood
  returns, continues a track where it stopped, and crossfades 2.5 s across each change. QA warns when one track plays over 150 s or a
  long video uses fewer than five tracks.
- Add a track to the library only after downloading it, checking it is real audio, and measuring it (`_analysis.json`); say honestly
  that nobody has auditioned it.

## Where this sits in the workflow

```
1 Topic and angle  ->  2 Script (this skill)  ->  GATE A: the owner reads script.md and hears preview-local.mp3 (free)
3 Visual plan (visual-plan.json against channels/hindi/visual-bible.json) -> validate -> structured prompts + reference manifest
4 Pictures (sheets first) -> GATE 1: vyapaar_review.py contact sheets, approve/reject per picture -> upscale approved only
4b Voice cast + music plan (section 12): choose each person's voice, hear them (free, then a paid sample), write audio/music-plan.json
5 Voice: the free voice first (people in their own voices); the paid Sarvam voice after the cut is right (the owner OKs the cost first)
6 Optional clips: select -> make (paid, --approve-cost) -> check -> approve
7 Sample render (vyapaar_render.py sample) -> GATE 2: vyapaar_qa.py + the owner's look -> approve -> full render -> QA
8 Packaging: title, thumbnail, description (music credits), chapters
```
The whole visual pipeline, its rules and its rollback are in `references/production.md`. Bean Studio's **Pipeline** tab runs steps 3 to 8 with one button each (and `python tools/vyapaar_steps.py <project> <step>` does the same from a terminal); use it, and keep it in step with the pipeline when anything is added.

**Each new video gets its own Claude session.** Bean Studio's **＋ New video** button (top of every page) makes the project folder and opens a new Claude window that works on that video only, starting with this skill and stopping at Gate A; the video's card reopens the same conversation (💬 Open its Claude session). Do not make several videos in one session.

Nothing paid starts before Gate A. Build the first full cut on the free voice; the pro voice comes after the cut is right. After the voice, a changed line means re-voicing that line, so the script freezes at Gate A.
