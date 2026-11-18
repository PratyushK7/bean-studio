# Research ledger: {title}

`<slug>-ledger.md` in the video's project folder. The narration tells the story; this file holds the evidence. Every
fact-bearing script line points here with its ids. `scripts/scriptcheck.py` reads the **Claims** table, so keep its columns
and the id format (`F` + number, or a reference-video code such as `RZ07`).

## Sources

| Code | Source | Type | Details | Read on |
|---|---|---|---|---|
| S1 | {book title, author, publisher, year} | book (devotee memoir) | pages read: {…}; seen in full / excerpt / quoted in S3 | {date} |
| S2 | {video title}, {channel} ({link}) | YouTube documentary | {duration}, {views}, captions {manual/auto}; timed transcript `research/reference-transcripts/{file}` | {date} |
| S3 | {thesis/article}, {author}, {institution}, {year} | scholarly | {pages} | {date} |

**Source types:** `primary` (a record made at the time, the person's own words, an official document), `scholarly`, `book`
(memoir or biography; name whether devotee or critical), `news`, `youtube` (documentary or interview), `website`
(organisation or devotee site), `interview` (named, recorded).

YouTube documentaries are research inputs: log every claim used, with its timestamp and the exact caption text, like any
other source. They are secondary. Several videos repeating a claim is still `video-reported`, unless they cite a source you
can trace (then trace it and log that).

## Claims

| ID | Claim | Source | Timestamp/page | Source type | Status | Excerpt | Corroboration | Used in |
|---|---|---|---|---|---|---|---|---|
| F1 | {one claim, one sentence} | S2 | 03:24 to 03:35 | youtube | video-reported | "{exact words}" | S3 p.12 agrees on the year; place differs | L18 |

One claim per row. Split a sentence that carries two facts. The excerpt is the exact text (caption, page quote, transcript
line) that supports the claim, in the original language.

### Status

| Status | Meaning | How the narration may use it |
|---|---|---|
| `established` | a primary record, or two independent reliable non-YouTube sources | stated plainly |
| `reported` | one reliable published source (scholarly, a serious book, journalism) | stated plainly; name the source when it helps the viewer |
| `account` | a named witness's or devotee's story, in a book, a talk or an interview (most miracle stories) | told in full as their account, attributed once at the start ("रामदास लिखते हैं ...", "भक्त सुनाते हैं ...") |
| `video-reported` | appears only in YouTube documentaries (one or more), without a traceable source | told with one soft attribution ("यह कहानी बहुत सुनाई जाती है"); never as established; no quotation marks |
| `conflicting` | sources disagree on the detail | use the corroborated version, or keep the detail vague, or say both in one sentence |
| `dramatized` | exists only inside a dramatized scene (invented dialogue, names, numbers) | not as an event; the underlying story only if another source carries it |
| `unsupported` | cannot be traced, or contradicts stronger sources | not used |

**Quotations** in the narration need a row with status `established`, `reported` or `account` and a named speaker or book.

## Contradictions

| Topic | Versions (ids) | Decision |
|---|---|---|
| {e.g. distance} | {F3: 100 km; F9: 100 miles} | {kept vague: "बहुत दूर"} |

## Gaps

What the video needs and the research could not settle: a book not seen, an audio not heard, a date with no record. Each gap
says whether the narration names it (only where it matters to the central question; at most once, near the end).

## Not in this video

Good findings that do not serve the central question, kept for later videos.
