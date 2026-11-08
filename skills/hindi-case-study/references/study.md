# The study: ten Hindi case-study hits, read line by line

Source material: the five most-viewed videos of **HinExp** (@HinExpofficial) and of **ABFinDoc** (@ABFinDoc), the two
Hindi business-documentary channels this channel is modelled on. Views are as listed on 9 Nov 2026 (no upload dates
were available, so a low number on a recent video may only mean it is new). The scripts were read from YouTube's Hindi
auto-captions, so a few numbers in them are garbled; the structure, the timings and the phrasing are reliable.

| # | Channel | Video | Views | Length | Format |
|---|---|---|---|---|---|
| 1 | HinExp | The Economics of Owning a Bus Business | 2.0M | 17:48 | economics |
| 2 | ABFinDoc | The Battle for Reliance: Mukesh vs Anil Ambani | 1.4M | 27:59 | person (rivalry) |
| 3 | HinExp | How Hero Honda Split | 1.3M | 19:11 | story (split) |
| 4 | ABFinDoc | How Maharaja Jai Singh Humiliated Rolls-Royce | 1.2M | 13:30 | person (revenge) |
| 5 | HinExp | The Economics of Owning a Petrol Pump | 1.1M | 14:13 | economics |
| 6 | HinExp | Renting vs Buying a Home: The Math Will Shock You | 1.1M | 19:34 | compare |
| 7 | HinExp | How the TAVERA Died: The Real Reason Chevrolet Left India | 1.0M | 15:53 | story (fall) |
| 8 | ABFinDoc | How 5,000 Turned Into 45,000 Crores (Jhunjhunwala) | 976K | 14:22 | person (rise) |
| 9 | ABFinDoc | How a Waiter Built Rameshwaram Cafe | 897K | 17:30 | person (rags to riches) |
| 10 | ABFinDoc | How Dhirubhai Ambani Defeated Manu Manek | 748K | 16:02 | person (war) |

## Measured across the ten

| | Range | Notes |
|---|---|---|
| Length | 13.5 to 28 min | most 14 to 20 |
| Pace | 145 to 183 Hindi words a minute | HinExp 145 to 156 (explaining), ABFinDoc 164 to 183 (telling) |
| Hook length (to "चलिए शुरू करते हैं") | 60 to 110 s | far longer than an English Short's 15 s; the first 15 s still hold the scene and the stakes |
| Turns (लेकिन, पर, a question, "समझो") | one every 20 to 40 s | लेकिन/पर alone 2.0 to 3.3 a minute in every video |
| Strong re-hooks (a new open loop or a twist) | 0.6 to 2.6 a minute | the longest stretch without one in any hit: 4.3 min |
| Numbers (₹, करोड़, लाख, %, years) | economics 3.9 to 5.3 a minute, compare 8.7, story 3.1 to 3.4, person 1.1 to 6.9 | specificity is their credibility |
| Asks (like, share, subscribe) | only in the last 60 to 90 s | never in the hook, never mid-video |
| Channel intro, greeting | none in any of the ten | the first word is already the story |

`casecheck.py` encodes these numbers. All ten pass its FAIL rules (`--transcript` mode).

## What wins, and what does not, on these two channels

Both channels' top videos share three things: **something the viewer already sees or knows** (the bus they took last
night, the petrol pump, the bike their father rode, a name every Indian knows), **a gap between what everyone assumes
and what is true** ("this pump owner must be rolling in money", "the split was just a fight about money"), and **either
money math or a human conflict** (a rivalry, a revenge, a fall, a rise from nothing).

The weakest videos on the same channels (10K to 25K views) are the ones without a known thing or without a conflict:
abstract finance ("Market crash explained", "Why rich people buy iPhone"), a concept explainer with no person
(ABFinDoc's "Muhurat trading", "Plastic notes"), and stories about people viewers do not already know. Pick topics
where the viewer can picture the thing in the first sentence.

## The four formats

### A. Economics of owning X (videos 1 and 5; HinExp's biggest)

A business the viewer meets as a customer and could imagine owning: bus, petrol pump, transport, dumper, scrap.

1. **Cold open, second person** (0:00 to 0:28). "एक सीन इमेजिन करो। रात के 10 बजे हैं। आप एक स्लीपर बस में अपनी बर्थ पर
   लेटे हो..." The viewer pays a real price (₹1200 ticket, ₹2000 of petrol), then thinks the naive thought ("यह बस वाला तो
   मालामाल होगा") and does the naive math out loud (36 berths x ₹1200 = 40 to 45 thousand a night).
2. **Burst the belief** (0:28). "भाई आज मैं आपका यह बबल फोड़ने आया हूं।" Then the shock number (what actually reaches the
   owner) and a fast list of everything that cuts into it (diesel, toll, driver, agent's commission, EMI, tyres, tax).
3. **The question** (0:54). "तो सवाल यह है, इस बिजनेस में असली पैसा कहां है? ... या यह सिर्फ बाहर से चमकदार दिखने वाला एक
   कांटों भरा धंधा है?"
4. **The roadmap as open loops** (1:03 to 1:30). Four or five things the video will open, each phrased as a secret:
   "वो ऊपर की कमाई जिसकी चर्चा कोई नहीं करता", "वो लीटर जो हवा में उड़ जाता है", "वो नया झटका जो 2026 में हर पंप मालिक
   की नींद उड़ा रहा है". The roadmap is not a table of contents; it is a list of promises.
5. **A model business** (petrol pump): "आज हम एक काल्पनिक पेट्रोल पंप बनाएंगे। नाम रखते हैं हाईवे फ्यूल पॉइंट" and run every
   number on it. This turns averages into a story with a protagonist.
6. **Chapters**, in this order: the cost of entry ("इस खेल में उतरने की टिकट कितनी महंगी है"), how money comes in (often two
   models compared: own route vs government tender), the hidden system ("अब वो हिस्सा जो लगभग किसी को नहीं पता": booking
   software, 15% platform commission, agents), the costs ("अब सिक्के का दूसरा पहलू", "सबसे बड़ा राक्षस: डीजल"), the
   paperwork (permits), the dark side (tax tricks, cheap wiring, bus fires, with a safety takeaway for the viewer), the
   verdict ("हां भी और ना भी"), the future.
7. **Close**: back to the opening scene ("अगली बार जब आप किसी बस में सफर करो... यह पूरी कहानी याद कर लेना"), a maxim
   ("बिक्री जो दिखती है वो शोर है। मुनाफा जो बचता है वो असली कहानी है।"), the ask ("अपने उन दोस्तों को भेजो जो सोचते हैं कि
   बस का धंधा रातोंरात करोड़पति बना देता है"), the next video with two or three questions, the sign-off line.

### B. A company's rise and fall or split (videos 3 and 7)

1. **Nostalgia or accusation cold open.** Hero Honda: "आपके पापा ने या आपके ताऊ जी ने जिंदगी में एक बाइक जरूर चलाई होगी।"
   with sensory detail (black, sturdy; office in the morning, vegetable market in the evening, the whole family of four on
   it on Sunday) and the slogan everyone remembers ("भरो, बंद करो, भूल जाओ"). Tavera: "everyone's favourite car... but this
   American company was cheating Indians in a way that would mean jail today", then three shock facts.
2. **The belief, then the burst**: "ज्यादातर लोग सोचते हैं कि... बस इतनी सी बात। पर आज मैं आपका यह बबल फोड़ने आया हूं, क्योंकि
   सच्चाई इससे कहीं ज्यादा दिलचस्प और थोड़ी सी डरावनी भी है।"
3. **A paradox** the video will explain: the student who is now behind the teacher. Then "आज हम एक जासूस की तरह शुरू से इस
   पूरी कहानी का हर पेज खोलेंगे।"
4. **Humble origin with tiny exact numbers** (a ₹500 bank loan in 1956, 25 cycles a day, 639 in the first year), then the
   scale jump (world's biggest cycle maker by 1986, in Guinness).
5. **Two halves that complete each other** ("एक के पास इंजन था पर बाजार नहीं। दूसरे के पास बाजार था पर इंजन नहीं।"),
   "कागज पर यह दुनिया की सबसे परफेक्ट शादी थी।"
6. **The peak, in numbers**, then the midpoint turn (7:16 of 19:11): "पर यहीं इस चकाचौंध के बीच कहानी एक खतरनाक मोड़ लेती है।"
7. **The hidden move**: "अब ध्यान से सुनिए, क्योंकि यहीं इस पूरी कहानी का सबसे दिलचस्प हिस्सा है। एक बात जो बहुत कम लोग
   जानते हैं।" "जरा हीरो की जगह खुद को रखकर सोचिए।"
8. **Numbered cracks that escalate**: पहली दरार (royalty), दूसरी (export limits), तीसरी (one-way trust), "चौथी दरार और सबसे
   गहरी". Then "आखिरी वार", the date it ended.
9. **The scoreboard today** with real data ("आइए स्कोरबोर्ड देखते हैं"), closing the paradox from the hook.
10. **The lesson as a maxim** ("अपने बिजनेस की सबसे बुनियादी चीज की चाबी कभी किसी और के हाथ में मत दो"), a personal comment
    question ("आपके घर की पहली गाड़ी कौन सी थी? CD 100, Splendor या Activa?"), share with "उस दोस्त को जो आज भी अपनी पुरानी
    Hero Honda की कसमें खाता है".

### C. A person's story: rivalry, revenge, rise (videos 2, 4, 8, 9, 10; all of ABFinDoc's top five)

1. **Date, time and place stamp, inside the decisive moment.** "साल 2019, फरवरी की एक तपती दोपहर, नई दिल्ली, सुप्रीम कोर्ट के
   बाहर..." / "18 मार्च 1982, गुरुवार, दोपहर के 1:35..." / "साल 1920, लंदन का बॉन्ड स्ट्रीट..." The moment is the lowest
   point, the big bet or the insult. Three of the five use **a phone ringing** ("तभी फोन की घंटी बजती है") and a line of
   reconstructed dialogue.
2. **The reframe**: "यह सिर्फ एक बिजनेस के डूबने की कहानी नहीं है। यह कहानी है दो भाइयों के बीच की उस अनकही जंग की..." /
   "यह सिर्फ एक ट्रेडिंग कॉल नहीं थी। यह उस साम्राज्य की नींव थी..."
3. **A contrast or dramatic irony**: "एक भाई हार कर भी आसमान की बुलंदियों पर पहुंच गया, और दूसरा सब कुछ जीत कर भी अर्श से फर्श
   पर आ गिरा।" / "उसे खुद नहीं पता था कि जिस शाहरुख खान का पोस्टर लिए वो आज मन्नत के बाहर खड़ा है, उसी को एक दिन अपने
   हाथों से डोसा सर्व करेगा।"
4. **Two or three questions**, then "चलिए शुरू करते हैं ... की यह पूरी (अनसुनी) दास्तान।" Rolls-Royce adds an emotional
   promise: "यह जानकर एक भारतीय होने के नाते आपका सीना भी गर्व से चौड़ा हो जाएगा।"
5. **The flashback**: "इस कहानी को समझने के लिए हमें वक्त के पहिए को पीछे घुमाना होगा।" Birth date, family, the first job.
6. **Chronology dense with dates and rupees** (the Ambani video: about 7 numbers a minute, years and rupees). Small
   dramatised scenes with dialogue (the father's slap, the mother's line in the room). The villain gets an introduction of
   his own ("उस दौर के सबसे रहस्यमयी और ताकतवर विलेन").
7. **Dramatic irony as the engine**: "लेकिन किसे पता था कि...", "लेकिन उसे अंदाजा भी नहीं था कि..."; and setbacks in a chain
   ("लेकिन यहां भी निराशा ही हाथ लगी", "यहां से भी बात नहीं बनी"), then "सबको लगा उनकी कहानी यहीं खत्म हो गई। लेकिन असल
   में यहीं से नई शुरुआत होने वाली थी।"
8. **Return to the cold open at 60 to 75%**: "अब आते हैं उस पल पर जिससे हमने यह कहानी शुरू की थी" ... "अब वापस चलते हैं उसी
   दृश्य में। समय बीतता जा रहा है..." Then **one more twist after the loop closes**: "लेकिन इस कहानी में एक ऐसा मोड़ भी है जो
   बहुत कम लोगों तक पहुंचा" (the jail-saving payment was a corporate lease, not a brother's gift).
9. **Balance on contested points**: "कुछ इसे ... मानते हैं, तो कुछ इसे ... कहते हैं। सच्चाई शायद इन दोनों के बीच कहीं है।"
10. **Close**: the moral, an emotional last image (the old men of Alwar still telling the story), the ask, often a patriotic
    sign-off ("कमेंट में जय हिंद लिखकर...", "जय हिंद"), and sometimes letting the audience pick the next video ("क्या आप
    हर्षद मेहता और मनु मानेक की जंग पर भी एक वीडियो देखना चाहते हैं?").

### D. Two people, one decision, twenty years (video 6)

Two named, relatable people with identical money and different temperaments ("रोहन और विवेक दोनों 32 साल के हैं... दोनों ने
₹20 लाख की सेविंग जोड़ ली है... लेकिन टेंपरामेंट से बिल्कुल अलग"), each sketched with one domestic detail (a nail in the
wall without calling the landlord; balcony plants). "अगले 20 साल हम दोनों को फॉलो करेंगे।" Every rupee is computed on
screen, with the caveat said inside the line (floating rates). The running scoreboard is the re-hook. The verdict is a
both-sides truth ("जीतने वाला हमेशा घर का मालिक नहीं होता, और हमेशा किराएदार भी नहीं") and the real lesson is behaviour
(did the renter actually invest the difference?).

## The re-hook toolkit, as the hits use it

- **The twist marker**: "कहानी एक खतरनाक मोड़ लेती है", "यहीं से शुरू होता है असली खेल", "सबसे बड़ा और सबसे चौंकाने वाला ट्विस्ट".
- **The secret**: "एक बात जो बहुत कम लोग जानते हैं", "अब वो हिस्सा जो लगभग किसी को नहीं पता", "यही वो छिपी हुई बात है जो कोई
  खुलकर नहीं बताता", "वो बात जो 90% लोगों को नहीं पता".
- **The other side**: "अब सिक्के का दूसरा पहलू", "और यह सिर्फ शुरुआत है".
- **Put the viewer in it**: "जरा खुद को उसकी जगह रखकर सोचिए", "जरा इस बात का वजन महसूस कीजिए", "समझो...", "मान लो...".
- **A question, answered at once**: "यह पैसा कहां जाता है? जमीन, कंस्ट्रक्शन, टैंक..." (keeps the long explaining stretches moving).
- **Escalating numbered items**: "पहली दरार... चौथी दरार और सबसे गहरी" (the last is always the biggest).
- **Dramatic irony**: "किसे पता था कि...", "उसे अंदाजा भी नहीं था कि...".
- **Setback chain then reversal**: "लेकिन यहां भी निराशा...", "सबको लगा कहानी यहीं खत्म... लेकिन असल में यहीं से...".
- **Reframe up**: "यह सिर्फ X नहीं था। यह Y था।"
- **Callback**: "जिसकी बात हमने शुरुआत में की थी", "अब वापस चलते हैं उसी दृश्य में".
- **Images that stick**: "एक खड़ी बस एक घाव है जो हर दिन गहरा होता जाता है", "सबसे बड़ा राक्षस: डीजल", "दिल कोरियन था,
  माथे पर स्टीकर अमेरिकन", "उस्ताद और शागिर्द", "शादी में दरारें", "दो अधूरे टुकड़े".

## Language

Everyday spoken Hindi, not Sanskritised. Business words stay English (EMI, कमीशन, रॉयल्टी, IPO, मार्केट शेयर, वर्किंग
कैपिटल) and are explained once in plain words ("चेसिस यानी ढांचा", "आरओआई यानी पैसा वापस निकलने में"). The explainer
voice (HinExp) talks to the viewer as "आप" with the friendly imperative ("समझो", "सोचो", "सुनो", "भाई"); the documentary
voice (ABFinDoc) narrates in the third person and adds "जी" to elders' names. Sentences are short: one picture each.

## What not to copy

These channels get some things wrong. This channel should be the version a careful viewer trusts.

- **A legend told as fact.** The Rolls-Royce garbage-car story has no solid historical record (the video itself admits it
  is told with different kings). Tell a legend as a legend ("यह किस्सा मशहूर है, लेकिन इसका कोई पक्का रिकॉर्ड नहीं मिलता")
  or skip it.
- **Invented dialogue for real, living people presented as what happened** (the lawyer's phone call to Anil Ambani, the
  broker's call to Jhunjhunwala). Use their documented public words, or describe the scene without quotes, or mark a
  reconstruction ("उस दिन कुछ ऐसा माहौल रहा होगा").
- **Insinuation with no source** ("कुछ रूट्स पर... कभी वो चीजें जिनका जिक्र खुलकर नहीं होता"). A dark-side claim needs a
  named source or a court record, or it stays out.
- **Community or caste generalisations** as a topic ("why is community X good at business").
- **Copying their lines.** Both channels reuse their own hook wording almost word for word ("भाई आज मैं आपका यह बबल फोड़ने आया
  हूं", the cigar puff, the phone bell). Use the same moves in this channel's own words.
