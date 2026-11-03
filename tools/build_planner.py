"""Builds C:\\Users\\praty\\youtube\\bean-planner.xlsx: 2 Shorts a day + 1 long-form a week."""
import datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule, CellIsRule
from openpyxl.utils import get_column_letter as L

OUT = r"C:\Users\praty\youtube\bean-planner.xlsx"
RED, BLUE, YEL, INK, PAPER = "FF595E", "1982C4", "FFCA3A", "1C1C1C", "FFFAF0"
fill = lambda c: PatternFill("solid", start_color=c, end_color=c)
thin = Side(style="thin", color="D9D2C3")
box = Border(left=thin, right=thin, top=thin, bottom=thin)
HDR = Font(bold=True, color="FFFFFF")
GREY = Font(italic=True, color="6B6B6B")
WRAP = Alignment(wrap_text=True, vertical="top")
MID = Alignment(horizontal="center", vertical="top", wrap_text=True)

# slot -> (IST time, US time label, days to shift for the US date)
SLOTS = {"A": ("12:00 PM", "1:30 AM ET", 0), "B": ("6:30 AM", "8:00 PM ET", -1), "Long": ("9:30 PM", "11:00 AM ET", 0)}
LONG_DAY = 5  # Saturday

wb = Workbook()

def sheet(name, title, sub, headers, widths, idx=None):
    ws = wb.create_sheet(name, idx) if idx is not None else wb.create_sheet(name)
    ws["A1"] = title; ws["A1"].font = Font(bold=True, size=16, color=INK)
    ws["A2"] = sub; ws["A2"].font = GREY
    for i, (h, w) in enumerate(zip(headers, widths), 1):
        c = ws.cell(row=3, column=i, value=h)
        c.font = HDR; c.fill = fill(BLUE); c.border = box
        c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.column_dimensions[L(i)].width = w
    ws.row_dimensions[3].height = 32
    ws.freeze_panes = "A4"
    ws.sheet_view.showGridLines = False
    return ws

def body(ws, r0, r1, ncol, centre=()):
    for r in range(r0, r1 + 1):
        for c in range(1, ncol + 1):
            cell = ws.cell(row=r, column=c)
            cell.border = box
            cell.alignment = MID if c in centre else WRAP
            if r % 2 == 0: cell.fill = fill(PAPER)

# ---------------- content ----------------
# Video types, learned from 876 Shorts + 482 long videos on 17 channels (research/channel-study-2026-11-03).
TYPES = ["What if", "Myth test", "Why", "True story", "Versus", "Ranking", "Levels", "Paradox", "Puzzle",
         "How it works", "Superlative", "How many", "Map/scale"]
REBUILD = "Rebuild with current engine: captions + .srt"
# (type, title, promise, status, ticks, note)
shorts = [
    ("How many", "How Many Balloons Would It Take to Lift You?", "About 7,000 — and a man in 1982 actually tried it.", "Ready", "✓✓✓ ✓✓ ", "Needs thumbnail"),
    ("What if", "What If You Pooped Out a Watermelon?", "", "Rendered", "✓✓✓", REBUILD + " + outro"),
    ("How many", "How Many Mosquitoes Would It Take to Drain You?", "", "Rendered", "✓✓✓", REBUILD + " + outro"),
    ("What if", "What If You Never Cut Your Nails?", "", "Rendered", "✓✓✓", REBUILD),
    ("What if", "What If Your Skin Went Clear?", "", "Rendered", "✓✓✓", REBUILD),
    ("Myth test", "Does Swallowed Gum Really Stay in You for 7 Years?", "No — here's where it actually goes.", "Idea", "", ""),
    ("True story", "The Great Molasses Flood of 1919", "A wave of syrup really did flood the streets of Boston.", "Idea", "", "Like Zack D. Films 'Ohio's 1986 Balloon Disaster' (3.8×)"),
    ("What if", "What If You Jumped Into a Hole Through the Earth?", "You'd fall to the other side in about 42 minutes — then fall back.", "Idea", "", ""),
    ("What if", "What If You Never Stopped Growing?", "Tall is fine — growing forever is the bad idea.", "Idea", "", "'Growing' won on What If (72.5×) + MinuteEarth (6.1×)"),
    ("Versus", "Cockroach vs Human: Who Lasts Longer Without a Head?", "The cockroach wins — by weeks.", "Idea", "", "Like TierZoo '1 Gorilla VS 100 Men' (6.1×). Fact-check"),
    ("Paradox", "The Birthday Paradox", "Just 23 people gives a 50/50 chance two share a birthday.", "Idea", "", "Like MinuteEarth 'The Coyote Paradox' (11.5×)"),
    ("Why", "Why Can't You Drink Seawater?", "The salt makes you thirstier until your kidneys give up.", "Idea", "", ""),
    ("Map/scale", "Africa Is WAY Bigger Than Your Map Says", "Flat maps shrink Africa and stretch Greenland.", "Idea", "", "Like RealLifeLore 'Canada is WAY further south' (13.3×)"),
    ("Myth test", "Can Astronauts Burp?", "Not easily — without gravity, gas and lunch don't separate.", "Idea", "", "Like MinuteEarth 'can't BURP in Space' (4.0×). Fact-check"),
    ("Superlative", "The Most Painful Sting on Earth", "", "Idea", "", "Bullet ant / Schmidt index. Fact-check"),
    ("Myth test", "Can Carrots Turn You Orange?", "Yes — eat enough and your skin really changes colour.", "Idea", "", "Carotenemia. Fact-check"),
    ("Levels", "3 Levels of Spicy", "What chilli actually does to your mouth, from tingle to tears.", "Idea", "", "Like Mark Rober '3 Levels of…' (19.1×)"),
    ("What if", "What If You Shrank to the Size of an Ant?", "", "Idea", "", ""),
    ("True story", "The Man Struck by Lightning 7 Times", "", "Idea", "", "Roy Sullivan. Fact-check"),
    ("Puzzle", "Which Glass Fills First?", "Most people guess wrong — pause and pick.", "Idea", "", "Like Veritasium 'cut the green rope?' (14.1×). Comment bait"),
    ("Myth test", "Does Cracking Your Knuckles Ruin Them?", "One doctor cracked one hand for 60 years to find out.", "Idea", "", "Like Mark Rober 'Are Bananas Actually Slippery?' (10.6×). Fact-check"),
    ("How many", "How Many Bananas Would It Take to Hurt You?", "", "Idea", "", "Check banana radiation figures"),
    ("Why", "Why Can't You Tickle Yourself?", "", "Idea", "", ""),
    ("Ranking", "Ranking the Worst Planets to Get Lost On", "", "Idea", "", "Like SciShow 'Ranking Ridiculous Exoplanets' (13.3×)"),
    ("What if", "What If the Moon Disappeared?", "", "Idea", "", ""),
    ("Myth test", "Can Your Eyes Pop Out If You Sneeze?", "Your eyeballs stay put — here's why we blink anyway.", "Idea", "", ""),
    ("True story", "The Dancing Plague of 1518", "", "Idea", "", "Hedge the causes. Fact-check"),
    ("How it works", "How Does a Gecko Walk Up Walls?", "", "Idea", "", "Like Mark Rober 'How Record Players Actually Work' (7.5×)"),
    ("Versus", "Tardigrade vs Everything", "Boil it, freeze it, launch it into space — it shrugs.", "Idea", "", ""),
    ("What if", "What If You Never Cut Your Hair?", "", "Idea", "", ""),
    ("Why", "Why Do We Get Brain Freeze?", "", "Idea", "", ""),
    ("Paradox", "The Potato Paradox", "Dry a potato from 99% to 98% water and it loses half its weight.", "Idea", "", "Math — check the numbers on screen"),
    ("Superlative", "The Loudest Animal on Earth", "", "Idea", "", "Fact-check"),
    ("What if", "What If Earth Stopped Spinning?", "", "Idea", "", ""),
    ("Why", "Why Do We Get Goosebumps?", "", "Idea", "", ""),
    ("Levels", "3 Levels of Cold", "Shiver, numb, then the bad idea.", "Idea", "", ""),
    ("What if", "What If You Hiccuped Forever?", "", "Idea", "", ""),
    ("Myth test", "Do You Really Swallow Spiders in Your Sleep?", "", "Idea", "", ""),
]
longs = {
    dt.date(2026, 11, 7): ("Prep", "Long-form engine week: extend line-boil to 6–8 min episodes", "", "Idea", "", "No long video this week — build the format"),
    dt.date(2026, 11, 14): ("Ranking", "7 Bad Ideas About Your Own Body", "Gum, nails, carrots, knuckles, sneezing, growing — upgraded and linked.", "Idea", "", "Built from Shorts"),
    dt.date(2026, 11, 21): ("True story", "History's Worst Bad Ideas, Ranked", "The lawn-chair balloon flight, the molasses flood, the dancing plague and more.", "Idea", "", "Brand-perfect; built from the True story Shorts"),
    dt.date(2026, 11, 28): ("Why", "Why Mosquitoes Love You (and Not Your Friend)", "", "Idea", "", "Like MinuteEarth 'Mosquito Magnets' (8.1× long). Built from the mosquito Short"),
}

plan = [(dt.date(2026, 11, 3), "A", "Short", ("What if", "What If You Sweated Coca-Cola?",
         "Sweating soda would leave you sticky, swarmed by wasps, and overheating.", "Posted", "✓✓✓✓✓✓✓", ""))]
q, n = list(shorts), 1
d = dt.date(2026, 11, 4)
while d <= dt.date(2026, 11, 30):
    for slot in ("A", "B"):
        if q: item = q.pop(0)
        else:
            item = ("", f"(Short #{n}: the winning type, from Ideas)", "", "Idea", "", "Pick at Monday review"); n += 1
        if d.weekday() == 0 and slot == "A":
            item = item[:5] + ((item[5] + " · " if item[5] else "") + "MONDAY REVIEW: compare types + slot A (India) vs B (US) + Top geographies",)
        plan.append((d, slot, "Short", item))
    if d in longs:
        plan.append((d, "Long", "Long", longs[d]))
    d += dt.timedelta(days=1)

# ---------------- Schedule ----------------
# A date, B day, C slot, D IST, E US, F format, G type, H title, I promise, J make by, K status, L-R checks, S link, T notes, U helper
H = ["Post date (IST)", "Day", "Slot", "Post time (IST)", "US time", "Format", "Video type", "Working title", "The one-sentence promise",
     "Make by", "Status", "Script", "Fact-check", "Render", "Thumbnail", "YT details", "SRT", "Scheduled", "Link", "Notes", "next?"]
Wd = [13, 6, 6, 10, 16, 8, 12, 44, 44, 10, 11, 7, 9, 7, 10, 9, 6, 9, 22, 44, 4]
sch = sheet("Schedule", "The Bean With Bad Ideas — posting schedule",
            "2 Shorts a day (B 6:30 AM IST = 8 PM ET for the US, A 12:00 PM IST = Indian lunch) + 1 long-form every Saturday 9:30 PM IST (11 AM ET). Mix the video types.",
            H, Wd)
r = 4
for d, slot, fmt, (vtype, title, promise, status, ticks, note) in plan:
    ist, us, shift = SLOTS[slot]
    sch.cell(row=r, column=1, value=d).number_format = "dd mmm yyyy"
    sch.cell(row=r, column=2, value=f'=TEXT(A{r},"ddd")')
    sch.cell(row=r, column=3, value=slot)
    sch.cell(row=r, column=4, value=ist)
    sch.cell(row=r, column=5, value=f'="{us} "&TEXT(A{r}{shift:+d},"ddd")' if shift else f'="{us} "&TEXT(A{r},"ddd")')
    sch.cell(row=r, column=6, value=fmt)
    sch.cell(row=r, column=7, value=vtype or None)
    sch.cell(row=r, column=8, value=title)
    sch.cell(row=r, column=9, value=promise)
    sch.cell(row=r, column=10, value=f"=A{r}-{5 if fmt == 'Long' else 2}").number_format = "dd mmm"
    sch.cell(row=r, column=11, value=status)
    for k, ch in enumerate(ticks.ljust(7)[:7]):
        if ch == "✓": sch.cell(row=r, column=12 + k, value="✓")
    sch.cell(row=r, column=20, value=note)
    r += 1
last = r - 1
END = last + 20
for rr in range(4, END + 1):  # helper for the Dashboard's next-post dates
    sch.cell(row=rr, column=21, value=f'=IF(AND(A{rr}<>"",A{rr}>=TODAY(),K{rr}<>"Posted"),A{rr},"")').font = Font(color="FFFFFF")
sch.column_dimensions["U"].hidden = True
body(sch, 4, END, 20, centre=(2, 3, 4, 6, 7, 10, 11, 12, 13, 14, 15, 16, 17, 18))

STATUSES = "Idea,Scripted,Approved,Rendered,Ready,Scheduled,Posted,Skipped"
for rng, opts in [(f"K4:K{END}", STATUSES), (f"F4:F{END}", "Short,Long"), (f"C4:C{END}", "A,B,Long"),
                  (f"L4:R{END}", "✓"), (f"G4:G{END}", ",".join(TYPES + ["Prep"]))]:
    v = DataValidation(type="list", formula1=f'"{opts}"', allow_blank=True); sch.add_data_validation(v); v.add(rng)

row_rng = f"A4:T{END}"
sch.conditional_formatting.add(row_rng, FormulaRule(formula=['$F4="Long"'], fill=fill("FFE2E3"), font=Font(bold=True, color=INK)))
for word, color, font in [("Posted", "C9E8C9", INK), ("Scheduled", "CFE6F5", INK), ("Ready", "FFE9A8", INK), ("Skipped", "E6E6E6", "8A8A8A")]:
    sch.conditional_formatting.add(row_rng, FormulaRule(formula=[f'$K4="{word}"'], fill=fill(color), font=Font(color=font)))
sch.conditional_formatting.add(f"J4:J{END}", FormulaRule(
    formula=['AND($J4<TODAY(),OR($K4="Idea",$K4="Scripted",$K4="Approved"),$A4<>"")'], fill=fill(RED), font=Font(bold=True, color="FFFFFF")))
sch.conditional_formatting.add(f"G4:G{END}", FormulaRule(formula=['$G4="What if"'], font=Font(bold=True, color=BLUE)))
sch.cell(row=END + 2, column=1, value="Status: Idea → Scripted → Approved → Rendered → Ready → Scheduled → Posted. "
         "Pink rows = long-form. Red 'Make by' = behind. Make by = 2 days before (Shorts), 5 days before (long-form). "
         "Keep 'What if' to about 1 in 4 Shorts.").font = GREY
sch.auto_filter.ref = f"A3:T{last}"

# ---------------- Dashboard ----------------
db = wb.active; db.title = "Dashboard"
db.sheet_view.showGridLines = False
for c, w in zip("ABCD", (38, 22, 22, 46)): db.column_dimensions[c].width = w
db["A1"] = "The Bean With Bad Ideas 🫘💡"; db["A1"].font = Font(bold=True, size=20)
db["A2"] = "Target: 2 Shorts a day + 1 long-form a week, in a mix of video types. Only yellow cells are typed in."; db["A2"].font = GREY
K, F, A, J, U, G = (f"Schedule!${c}$4:${c}${END}" for c in "KFAJUG")
stats = [
    ("Shorts posted", f'=COUNTIFS({K},"Posted",{F},"Short")', ""),
    ("Long-form posted", f'=COUNTIFS({K},"Posted",{F},"Long")', ""),
    ("Shorts banked (Ready + Scheduled)", f'=COUNTIFS({K},"Ready",{F},"Short")+COUNTIFS({K},"Scheduled",{F},"Short")', "Aim for 4+ (2 days) at all times"),
    ("Behind schedule", f'=SUMPRODUCT(({J}<TODAY())*({A}<>"")*(({K}="Idea")+({K}="Scripted")+({K}="Approved")))', "Past their make-by date"),
    ("Shorts scheduled this week", f'=COUNTIFS({F},"Short",{A},">="&(TODAY()-WEEKDAY(TODAY(),2)+1),{A},"<"&(TODAY()-WEEKDAY(TODAY(),2)+8))', "Target 14"),
    ("Next Short", f'=IFERROR(SMALL(IF(({U}<>"")*({F}="Short"),{U}),1),"—")', ""),
    ("Next long-form", f'=IFERROR(SMALL(IF(({U}<>"")*({F}="Long"),{U}),1),"—")', "Saturdays 9:30 PM IST"),
    ("Subscribers (type latest)", None, "From YouTube Studio"),
    ("Avg 'viewed' % — slot A", '=IFERROR(AVERAGEIFS(Analytics!G4:G300,Analytics!C4:C300,"A"),"—")', "Viewed vs swiped away"),
    ("Avg 'viewed' % — slot B", '=IFERROR(AVERAGEIFS(Analytics!G4:G300,Analytics!C4:C300,"B"),"—")', ""),
    ("Long-form avg % viewed", '=IFERROR(AVERAGEIFS(Analytics!H4:H300,Analytics!C4:C300,"Long"),"—")', ""),
    ("'What if' share of planned Shorts", f'=IFERROR(COUNTIFS({G},"What if",{F},"Short")/COUNTIFS({F},"Short",{G},"<>"),"—")', "Keep near 25%"),
]
for c in "ABCD": db[f"{c}3"].fill = fill(BLUE)
db["A3"] = "Numbers"; db["A3"].font = HDR
for i, (k, v, note) in enumerate(stats, 4):
    db.cell(row=i, column=1, value=k).border = box
    c = db.cell(row=i, column=2, value=v); c.border = box; c.font = Font(bold=True, size=13); c.alignment = Alignment(horizontal="center")
    if v is None: c.fill = fill(YEL)
    db.cell(row=i, column=4, value=note).font = Font(color="6B6B6B")
for ref in ("B9", "B10"): db[ref].number_format = "ddd dd mmm"
for ref in ("B12", "B13", "B14", "B15"): db[ref].number_format = "0%"
from openpyxl.worksheet.formula import ArrayFormula
db["B9"] = ArrayFormula("B9", stats[5][1]); db["B10"] = ArrayFormula("B10", stats[6][1])
db.conditional_formatting.add("B7", CellIsRule(operator="greaterThan", formula=["0"], fill=fill(RED), font=Font(bold=True, color="FFFFFF")))
db.conditional_formatting.add("B6", CellIsRule(operator="lessThan", formula=["4"], fill=fill("FFE9A8")))
db.conditional_formatting.add("B15", CellIsRule(operator="greaterThan", formula=["0.35"], fill=fill("FFE9A8")))

# which video types work for us (from the Analytics tab)
t0 = 18
for c, h in zip("ABCD", ["Video type", "Shorts planned", "Avg 'viewed' %", "Avg views"]):
    db[f"{c}{t0}"] = h; db[f"{c}{t0}"].font = HDR; db[f"{c}{t0}"].fill = fill(RED); db[f"{c}{t0}"].border = box
for i, t in enumerate(TYPES, t0 + 1):
    db.cell(row=i, column=1, value=t).border = box
    db.cell(row=i, column=2, value=f'=COUNTIFS({G},A{i},{F},"Short")').border = box
    c = db.cell(row=i, column=3, value=f'=IFERROR(AVERAGEIFS(Analytics!G$4:G$300,Analytics!D$4:D$300,A{i}),"—")'); c.border = box; c.number_format = "0%"
    c = db.cell(row=i, column=4, value=f'=IFERROR(AVERAGEIFS(Analytics!F$4:F$300,Analytics!D$4:D$300,A{i}),"—")'); c.border = box; c.number_format = "#,##0"
    for col in (2, 3, 4): db.cell(row=i, column=col).alignment = Alignment(horizontal="center")
t1 = t0 + len(TYPES) + 1
db.conditional_formatting.add(f"C{t0+1}:C{t1-1}", CellIsRule(operator="greaterThanOrEqual", formula=["0.6"], fill=fill("C9E8C9")))

r1 = t1 + 2
for c in "ABCD": db[f"{c}{r1}"].fill = fill(INK)
db[f"A{r1}"] = "How the week runs"; db[f"A{r1}"].font = HDR
rules = ["Two Shorts every day: slot B 6:30 AM IST (8 PM ET, US evening), slot A 12:00 PM IST (Indian lunch break). Schedule both in Studio.",
         "Mix the types: no two of the same type in a row, and 'What if' about 1 in 4.",
         "One long-form every Saturday 9:30 PM IST (11 AM ET), 6–8 min, built from that week's best Shorts plus new links.",
         "Make sessions Mon / Wed / Fri, 5 Shorts each; the long-form is finished by Monday for Saturday.",
         "Borrow topics and formats from other channels, never their script, footage or title word-for-word.",
         "Monday review: fill Analytics, read the type table above, double the winning type, pick the next long-form.",
         "If a week slips, drop a weekend slot-A Short first. Never drop the fact-check."]
for i, t in enumerate(rules, r1 + 1):
    db.merge_cells(start_row=i, start_column=1, end_row=i, end_column=4)
    db.cell(row=i, column=1, value=f"• {t}").alignment = WRAP
    db.row_dimensions[i].height = 30

# ---------------- Types ----------------
th = ["Video type", "Shape (how the script runs)", "Title pattern", "Proof from other channels", "Fits line-boil because"]
ty = sheet("Types", "Video types", "From 876 Shorts + 482 long videos on 17 channels, ranked by views vs each channel's own median. "
           "Titles tell you the shape, not why a video worked.", th, [14, 46, 34, 52, 40])
types_rows = [
    ("What if", "Absurd premise → what really happens → callback", "What If You ___?", "What If: 'Grew 1cm Every Second' 72.5×, 'Nuked a Hurricane' 11.1×", "Our home turf; keep ~1 in 4"),
    ("Myth test", "Common belief → test it → verdict", "Does / Can / Is ___ Really ___?", "Mark Rober 'Are Bananas Actually Slippery?' 10.6×; Veritasium 'Can you swim in shade balls?' 17.3×", "A big YES/NO payoff the bean can react to"),
    ("Why", "Everyday thing → hidden cause → 'so that's why'", "Why Do We ___?", "MinuteEarth 'Why do humans stop growing?' 6.1×; RealLifeLore 'Why Canada is WAY…' 13.3×", "One mechanism, easy to draw"),
    ("True story", "Hook on the moment → what led to it → what happened", "The ___ of 1919 / The Man Who ___", "What If 'What Happened Immediately After the Dinosaurs…' 21.6×; Zack D. Films 'Ohio's 1986 Balloon Disaster' 3.8× (long)", "'History's worst bad ideas' is the channel name"),
    ("Versus", "Two contenders → rounds → surprise winner", "___ vs ___: Who Wins?", "TierZoo '1 Gorilla VS 100 Men' 6.1×; Mark Rober 'Sumo Wrestlers vs Phone Books' 8.1×", "Two characters, built-in rivalry"),
    ("Ranking", "5→1 countdown, worst saved for last", "Ranking the ___", "SciShow 'Ranking Ridiculous Exoplanets' 13.3×", "Great long-form spine too"),
    ("Levels", "Level 1 → 2 → 3, each bigger", "3 Levels of ___", "Mark Rober '3 Levels of Elephant Toothpaste' 19.1×", "Escalation = acting beats"),
    ("Paradox", "Feels wrong → the trick → 'wait, what?'", "The ___ Paradox", "MinuteEarth 'The Coyote Paradox' 11.5×; Vsauce 'A Cosmic Coincidence' 6.3×", "Rewatch value"),
    ("Puzzle", "Ask the viewer → pause → reveal", "Which ___ First?", "Veritasium 'What happens if you cut the green rope?' 14.1×; TED-Ed 'Would you take the road less traveled?' 4.4×", "Drives comments"),
    ("How it works", "Thing you use → zoom inside → 'clever'", "How Does ___ Work?", "Mark Rober 'How Record Players Actually Work' 7.5×", "Cutaway drawings"),
    ("Superlative", "The most ___ → why it's the most → you vs it", "The Most ___ on Earth", "Mark Rober 'Sharpest Thing In The World' 9.2×", "One hero prop"),
    ("How many", "Ridiculous count → the maths → the twist", "How Many ___ Would It Take to ___?", "Our balloons + mosquito Shorts", "Numbers as props"),
    ("Map/scale", "Your mental picture → the real size → shock", "___ Is WAY Bigger Than You Think", "RealLifeLore 'South America Is WAY Further East…' 11.2×", "Simple shapes, big reveal"),
]
for i, row in enumerate(types_rows, 4):
    for j, v in enumerate(row, 1): ty.cell(row=i, column=j, value=v)
body(ty, 4, 3 + len(types_rows), len(th))
for rr in range(4, 4 + len(types_rows)): ty.row_dimensions[rr].height = 45

# ---------------- Ideas ----------------
idh = ["Idea / working title", "Format", "Video type", "Inspired by (topic/format only)", "Fact-check notes", "Priority", "Used on"]
ide = sheet("Ideas", "Idea bank", "Borrow the topic or the format, never the script or title word-for-word. Move ideas into the Schedule as slots open.",
            idh, [46, 9, 13, 46, 32, 10, 12])
ideas = [
    ("Every Gross Thing Your Body Does, Explained", "Long", "Why", "MinuteEarth 'ALL THE CATS, EXPLAINED' 6.8× (long)", "", "High"),
    ("The Biggest Things in Space, Sized Against a Bean", "Long", "Map/scale", "What If 'Largest Things… Against a School Bus' 3.0× (long)", "", "High"),
    ("Bad Ideas in Space", "Long", "Ranking", "Built from burp / moon / hole-through-Earth Shorts", "", "Med"),
    ("Signs You're Secretly Two People", "Long", "Myth test", "Life Noggin 'Someone Else Inside You' 6.8× (long)", "Chimerism", "Med"),
    ("If Humans Vanished, How Long Until Earth Forgot Us?", "Long", "What if", "What If 'If All Humans Vanished…' 4.9× (long)", "", "Med"),
    ("Why Grass Grows Better Under Trampolines", "Short", "Why", "MinuteEarth 3.5× (long) — tiny everyday mystery", "", "Med"),
    ("What Happens to Your Body When You Get Stung?", "Short", "How it works", "Infographics 'What Happens When…' 11.0×", "", "Med"),
    ("Pistol Shrimp vs Everything", "Short", "Versus", "TierZoo versus format", "", "Med"),
    ("3 Levels of Bad Breath", "Short", "Levels", "Mark Rober '3 Levels' format", "", "Low"),
    ("Your Brain Is Lying About This Picture", "Short", "Puzzle", "AsapSCIENCE illusion Shorts 22.7×", "Pick a real illusion", "Med"),
    ("What If You Drank a Gallon of Coffee?", "Short", "What if", "", "Keep it non-instructional", "Low"),
    ("What If Your Bones Were Made of Glass?", "Short", "What if", "", "", "Low"),
    ("Why Do Onions Make You Cry?", "Short", "Why", "", "", "Med"),
    ("The Most Venomous Animal You've Never Heard Of", "Short", "Superlative", "", "", "Med"),
    ("Greenland Isn't as Big as Your Map Says", "Short", "Map/scale", "RealLifeLore map Shorts", "", "Med"),
]
for i, row in enumerate(ideas, 4):
    for j, v in enumerate(row, 1): ide.cell(row=i, column=j, value=v)
body(ide, 4, 80, len(idh), centre=(2, 3, 6))
for rng, opts in [("F4:F300", "High,Med,Low"), ("B4:B300", "Short,Long"), ("C4:C300", ",".join(TYPES))]:
    v = DataValidation(type="list", formula1=f'"{opts}"', allow_blank=True); ide.add_data_validation(v); v.add(rng)

# ---------------- Analytics ----------------
# A title, B posted, C slot, D type, E checked, F views, G viewed%, H avg%, I AVD, J likes, K comments, L shares, M subs, N like rate, O subs/1k
ah = ["Title", "Posted (IST)", "Slot", "Video type", "Checked on", "Views", "Viewed vs swiped %", "Avg % viewed", "Avg view duration (s)",
      "Likes", "Comments", "Shares", "Subs gained", "Like rate", "Subs per 1k views", "Biggest drop at (s)", "Line / shot at the drop", "Notes"]
an = sheet("Analytics", "Analytics log", "Fill in from Studio at ~48-72 h after posting. 'Viewed vs swiped' is Shorts only. Grey columns calculate themselves.",
           ah, [42, 12, 6, 13, 12, 10, 11, 10, 11, 8, 10, 8, 9, 9, 10, 10, 34, 30])
for i, (t, d, s, ty_) in enumerate([("What If You Sweated Coca-Cola?", dt.date(2026, 11, 3), "A", "What if"),
                                    ("How Many Balloons Would It Take to Lift You?", dt.date(2026, 11, 4), "A", "How many")], 4):
    for j, v in enumerate((t, d, s, ty_), 1): an.cell(row=i, column=j, value=v)
for rr in range(4, 301):
    an.cell(row=rr, column=14, value=f'=IF(OR(F{rr}="",F{rr}=0),"",J{rr}/F{rr})').number_format = "0.0%"
    an.cell(row=rr, column=15, value=f'=IF(OR(F{rr}="",F{rr}=0),"",M{rr}/F{rr}*1000)').number_format = "0.0"
    for c in (2, 5): an.cell(row=rr, column=c).number_format = "dd mmm"
    for c in (7, 8): an.cell(row=rr, column=c).number_format = "0%"
    an.cell(row=rr, column=6).number_format = "#,##0"
body(an, 4, 120, len(ah), centre=(3, 4))
for rr in range(4, 121):
    for c in (14, 15): an.cell(row=rr, column=c).fill = fill("EFEFEF")
for rng, opts in [("C4:C300", "A,B,Long"), ("D4:D300", ",".join(TYPES))]:
    v = DataValidation(type="list", formula1=f'"{opts}"', allow_blank=True); an.add_data_validation(v); v.add(rng)
an.conditional_formatting.add("G4:G300", CellIsRule(operator="greaterThanOrEqual", formula=["0.6"], fill=fill("C9E8C9")))
an.conditional_formatting.add("G4:G300", FormulaRule(formula=['AND(G4<>"",G4<0.5)'], fill=fill("FFD1D2")))
an.cell(row=122, column=1, value="Type percentages as 62% (or 0.62). Green 'viewed' = 60%+, pink = under 50%.").font = GREY

wb.active = 0
wb.save(OUT)
print("saved", OUT, "| rows", last - 3, "| shorts", sum(1 for p in plan if p[2] == "Short"), "| long", sum(1 for p in plan if p[2] == "Long"))
