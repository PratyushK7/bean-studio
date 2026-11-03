// Does swallowed gum stay in you for 7 years? Cast and topic props.

// You: a blue bean in a yellow beanie (the viewer's stand-in)
const YOU = makeChar({ shape: 'bean', color: BLUE, size: 1.4, seed: 21, hat: { kind: 'beanie', color: YEL, pom: RED } });
// Gum: a small red lump with legs and white cheeks
const GUM = makeChar({ shape: 'tiny', color: RED, size: 1.5, seed: 22, cheeks: PAPER, eye: 1.1 });
// the Gut: a floating yellow wide blob with red cheeks
const GUT = makeChar({ shape: 'wide', color: YEL, legs: false, size: 1.1, seed: 23, cheeks: RED, belly: PAPER });
// the Doctor: a tall paper-white character with glasses
const DOC = makeChar({ shape: 'tall', color: PAPER, size: 1.3, seed: 24, glasses: true, hair: 'tuft', hairColor: INK });

const GY = 800;   // ground line

// the winding gut: a vertical S-curve. gutPt(u) is the centre of the tube at u in 0..1
const gutPt = u => [270 + 170 * Math.sin(u * TAU * 1.25), 170 + 600 * u];
const gutPts = () => Array.from({ length: 41 }, (_, i) => gutPt(i / 40));
function drawGut() {
  tube(gutPts(), 78, YEL, 701);
  tube(gutPts(), 8, PAPER, 702, 0.6);
}
// a squeeze ring across the gut at u: two short blue strokes either side of the tube
function squeeze(u) {
  const a = gutPt(u), b = gutPt(Math.min(1, u + 0.01)), dx = b[0] - a[0], dy = b[1] - a[1], l = Math.hypot(dx, dy) || 1;
  const nx = -dy / l, ny = dx / l;
  line([[a[0] + nx * 52, a[1] + ny * 52], [a[0] + nx * 22, a[1] + ny * 22]], 5, 710, BLUE);
  line([[a[0] - nx * 52, a[1] - ny * 52], [a[0] - nx * 22, a[1] - ny * 22]], 5, 711, BLUE);
}
// a calendar page with n dots
function calendar(x, y, n, seed) {
  shape(boxPts(x, y, 200, 170, seed), PAPER, 4, seed);
  shape(boxPts(x, y, 200, 46, seed + 1), RED, 4, seed + 1);
  for (let i = 0; i < n; i++) fillOnly(blobPts(x + 48 + i * 52, y + 112, 15, 15, seed + 10 + i, 7), INK, seed + 10 + i);
}
