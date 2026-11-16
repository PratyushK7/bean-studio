# Remotion sandbox (evaluated 2026-11-17)

Remotion (React -> video) installed beside the working graphics pipeline, not replacing it.
License: free for individuals, for-profit organisations up to 3 employees, and non-profits, commercial use included
(LICENSE.md in remotion-dev/remotion). Re-check if the channel becomes a company with 4+ people.

    cd tools/remotion
    npx remotion studio                                   # live preview with a timeline
    npx remotion render src/index.ts NumberCard out/x.mov # ProRes 4444 + alpha (remotion.config.ts)

Tested: Devanagari text (Nirmala UI) shapes correctly, alpha is clean, 120 frames in about 26 s, a 4 s card is about 33 MB.
The existing `tools/video/graphics.html` pipeline (10 templates, cues, traceability checks, QA) stays the production path.
Use this for things it cannot do well: animated captions, new transition styles, Shorts, template experiments.
