# The script evaluator

Every finished script passes **two separate evaluations**, done in a changed role: an independent senior editor who did not
write it and wants it to fail. A cautious, boring script fails the storytelling score. An exciting script with an invented
detail fails the research score. **Both must pass.**

Order: run `scripts/scriptcheck.py` first (the mechanical checks), fix every hard fail, then score by hand.

## Pass rule

- Each scorecard: **average ≥ 8.0** and **no dimension below 7**.
- **Zero hard fails** (below).
- If a scorecard fails: fix the two lowest dimensions first, re-run the checker, re-score. At most three rounds; if it still
  fails, say what blocks it in the hand-back.

Score 1 to 10 with one line of evidence each (a line number or timestamp and what it shows). A score without evidence is
not a score.

## Storytelling scorecard

| Dimension | 10 looks like | 7 looks like | Below 7 |
|---|---|---|---|
| **Opening strength** | first sentence is a story or a stamp; a complete anecdote or a promise stack by 0:30; name and question land by the template's deadline | strong first line, slow second half | starts with introduction or context |
| **Curiosity** | every chapter opens a real question; the central question is felt, not only stated | most chapters do | the viewer is told, not made to wonder |
| **Story density** | anecdotes in full at the band's count; something new every 15 to 45 s | count met, some summaries | lists of facts between stories |
| **Anecdote quality** | each full anecdote has 8+ of the 10 steps, a withheld element, a reveal at the end of its sentence | 6 to 7 steps | anecdotes squeezed into two sentences |
| **Pacing** | no stretch longer than the band's "something new" limit; rhythm varies between story, explanation, testimony | one slow patch | repeated slow patches or a sponsor-like digression in the first two minutes |
| **Suspense** | at least one withheld object or delayed reveal per chapter; reveals placed by the plan | some | none, or fake suspense |
| **Re-hooks** | every chapter seam has a handoff line; no gap above the band's re-hook limit | one gap | gaps, or a cliffhanger every minute |
| **Emotional connection** | a person to care about in every act; one emotional low before the resolution | present but thin | facts about people, no people |
| **Spoken-Hindi quality** | sentences 6 to 14 words; everyday words; no academic Hindi; English only where common; reads naturally aloud | a few stiff lines | research-paper Hindi, long sentences, repeated source introductions |
| **Chapter progression** | each chapter answers a question and hands over a new one; escalation by stakes; seeds paid off | mostly | chronology without pull |
| **Final payoff** | honest answer to the central question; a callback that changes the opening's meaning; a line worth repeating | answer without callback | trails off, or overclaims |

## Research scorecard

| Dimension | 10 looks like | 7 looks like | Below 7 |
|---|---|---|---|
| **Claim traceability** | every fact-bearing line has ledger ids; every id resolves to a row with source and timestamp/page | a few minor lines untagged | facts without ids |
| **Source accuracy** | each line says no more than its source; excerpts match | one stretch, corrected | details beyond the source |
| **Chronology** | dates consistent across the script and with the ledger; time jumps signposted | one confusing jump | contradictions in dates |
| **Quote provenance** | every quotation is a recorded line with a named speaker or book and a ledger id; translations marked | one quote's page missing | a quote from a dramatized source or with no source |
| **Reported vs established** | reported accounts and beliefs are attributed once, naturally; established facts stated plainly; the method note appears once | attribution slightly heavy or slightly light in one place | an account told as established fact, or disclaimers in every line |
| **Unsupported specificity** | no invented names, numbers, ages, distances, times or weather; conflicting details kept vague | one vague detail made concrete | invented specifics |
| **Missing evidence** | gaps are known, listed in the ledger and, where they matter, named once in the narration | listed but not named where they matter | gaps hidden |

## Hard fails (any one fails the script)

1. A line of dialogue, a quotation, or a name that exists only in a dramatized source or nowhere.
2. A fact-bearing line with no ledger id, or an id that does not exist.
3. A `dramatized` or `unsupported` claim stated in narration as an event.
4. A quotation whose ledger status is `video-reported`, `dramatized` or `unsupported` (paraphrase it as reported speech
   instead, or drop it).
5. An AI image presented as a real photograph, or a prompt asking for "archival" or "vintage photo" looks for a real event.
6. Any label, disclaimer or Devanagari text in an image prompt.
7. No complete anecdote and no promise by the band's deadline (Short 1:30, Standard 0:05, Long 0:05).
8. An open loop never closed (including a story mentioned and not told).
9. More than 2 attribution phrases in any 30-second window, or more than 2 disclaimer phrases in the whole script.
10. A CTA before the last 10% of the video (except the optional soft comment question in Long videos).

## The evaluation file: `<slug>-eval.md`

```
# Evaluation: <title>
Checker: scripts/scriptcheck.py → 0 hard fails, 3 warnings (listed)

## Storytelling: 8.4 (pass)
| Dimension | Score | Evidence |
| Opening strength | 9 | L1 "1967।" stamp; outsider anecdote complete by 2:40 |
...

## Research: 8.6 (pass)
| Dimension | Score | Evidence |
...

## Fixed in this round
- L37: "100 किलोमीटर" made vague (RZ07 conflicting)
...

## Still thin
- the blanket story's book source not yet seen (AG14 → Miracle of Love)
```
