"""Build the ZEIT idea deck on the official SIH 2026 template.

Constraints taken from the template's own instruction slide:
  * six slides maximum, including the title slide
  * the idea-detail pointers must not be changed — they are kept verbatim and
    reused as section labels rather than deleted
  * points, diagrams and infographics rather than paragraphs

    python build_deck.py
"""
import copy
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

from slides_23 import slide2, slide3
import slide_field
from deckkit import (LABEL, fit_widths, widest, panel, bullets, bigstat, dashed, BLUE, BLUE_F, GREEN_F, ORANGE, ORANGE_F, PURPLE, PURPLE_F, CRIMSON, CRIMSON_F, TEAL, TEAL_F, flow, INK, STEEL, MID, PALE, PALER, RUST, RUSTPL, GREEN, GREENPL,
                     WHITE, FONT, _in, textbox, block, chip, arrow, rule, vrule,
                     elbow, pointer_label, stat, delete_shape, set_ph_text,
                     check_fit, ISSUES, photo_chip)

prs = Presentation('template.pptx')
S = prs.slides

# ---------------------------------------------------------------- structure
# Drop the instruction slide; the template says it may be removed.
# The template's instruction slide is not deleted — it is repurposed as the
# mentor-approval slide, because it already carries the footer bar, the
# auto-numbering slide-number field, the footer and the logo. It is then moved
# to position 2, so every following slide shifts down by one.
sldIdLst = prs.slides._sldIdLst

TEAM = "ZEIT v.1.0"


def shp(slide, name):
    for s in slide.shapes:
        if s.name == name:
            return s
    return None


def pointer_text(slide, box_name):
    """Pull the mandated pointer strings out of a template text box."""
    s = shp(slide, box_name)
    out = [p.text.strip() for p in s.text_frame.paragraphs if p.text.strip()]
    return s, out


def brand(slide):
    """Remove the template's per-slide team badge.

    The team name is stated once, on the title slide. Repeating it in the
    corner of every content slide wastes the space and reads as filler.
    """
    for name in [s.name for s in slide.shapes]:
        if name.startswith("Oval"):
            delete_shape(shp(slide, name))


def title(slide, text, size=28, w=9.5):
    t = shp(slide, "Title 1")
    set_ph_text(t, text, size=size, bold=True, color=INK)
    # the placeholder inherits Times New Roman from the template; the rest of
    # the deck is Arial, so state it rather than letting it drift
    t.text_frame.paragraphs[0].runs[0].font.name = FONT
    t.width = _in(w)
    t.text_frame.paragraphs[0].alignment = PP_ALIGN.LEFT
    check_fit("title", text, w, size, True)
    # a short accent bar under the title — the deck's one consistent "designed"
    # motif, so every content slide is anchored the same way
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, _in(0.36), _in(1.02),
                                 _in(1.10), _in(0.06))
    bar.shadow.inherit = False
    bar.fill.solid(); bar.fill.fore_color.rgb = RUST
    bar.line.fill.background()
    return t


def link_block(slide, x, y, w, caption, urls, align_right=False,
               cs=7, us=8, lead=0.165):
    """A caption plus one or more live URLs, as real PowerPoint hyperlinks.

    Sits above the footer bar rather than on it — dark text on the template's
    blue band is close to unreadable at projector distance.
    """
    al = PP_ALIGN.RIGHT if align_right else PP_ALIGN.LEFT
    tb = textbox(slide, x, y, w, 0.15, [(caption, cs, True, LABEL)], align=al)
    yy = y + 0.15
    for u in urls:
        box = textbox(slide, x, yy, w, lead, [(u, us, False, RUST)], align=al)
        r = box.text_frame.paragraphs[0].runs[0]
        r.hyperlink.address = u
        r.font.underline = True
        check_fit("link", u, w, us, False)
        yy += lead
    return tb


# ================================================================ SLIDE 1
s1 = S[0]
tb = shp(s1, "TextBox 9")
lines = [
    ("Problem Statement ID", "26052"),
    ("Problem Statement Title", "AI/ML-enabled adaptive noise cancellation for "
                               "stationary, non-stationary and impulsive defence noise"),
    ("Theme", "Miscellaneous"),
    ("PS Category", "Hardware"),
    ("Organisation", "DRDO  ·  Department of Defence Production / IDEX"),
    ("Team ID", "HW2026106"),
    ("Team Name", TEAM),
    ("Mentor", "Dr. Swati Singal — Assistant Professor, CSE / SSCSE, Sharda University, Greater Noida"),
]
tf = tb.text_frame
tf.word_wrap = True
for p in list(tf.paragraphs)[1:]:
    p._p.getparent().remove(p._p)
p0 = tf.paragraphs[0]
for r in list(p0.runs):
    r._r.getparent().remove(r._r)
for i, (k, v) in enumerate(lines):
    p = p0 if i == 0 else tf.add_paragraph()
    p.space_after = Pt(7)
    r1 = p.add_run(); r1.text = k + " — "
    r1.font.size = Pt(11); r1.font.bold = True
    r1.font.color.rgb = STEEL; r1.font.name = FONT
    r2 = p.add_run(); r2.text = v
    r2.font.size = Pt(11.5); r2.font.bold = (k == "Team Name")
    r2.font.color.rgb = INK; r2.font.name = FONT
tb.top = _in(2.62); tb.left = _in(0.55); tb.height = _in(3.80); tb.width = _in(5.5)

# ---- cover title lockup: a real hero instead of the bare "TITLE PAGE"
sub = shp(s1, "Subtitle 3")
if sub is not None:
    tf = sub.text_frame
    tf.word_wrap = True
    for p in list(tf.paragraphs)[1:]:
        p._p.getparent().remove(p._p)
    p0 = tf.paragraphs[0]
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    r1 = p0.add_run(); r1.text = "ZEIT"
    r1.font.size = Pt(38); r1.font.bold = True
    r1.font.color.rgb = INK; r1.font.name = FONT
    p2 = tf.add_paragraph(); p2.space_before = Pt(4)
    r2 = p2.add_run()
    r2.text = "Two-Lane Adaptive Noise Cancellation for Defence Communications"
    r2.font.size = Pt(13); r2.font.bold = True
    r2.font.color.rgb = STEEL; r2.font.name = FONT
    sub.left = _in(0.55); sub.top = _in(0.82); sub.width = _in(5.5); sub.height = _in(1.6)

# vertical accent bar anchoring the title block
vbar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, _in(0.36), _in(0.90),
                           _in(0.07), _in(1.34))
vbar.shadow.inherit = False; vbar.fill.solid()
vbar.fill.fore_color.rgb = RUST; vbar.line.fill.background()

# drop the template's dated 2022 logo image
_p4 = shp(s1, "Picture 4")
if _p4 is not None:
    delete_shape(_p4)

# ================================================================ SLIDE 2
s2 = S[1]
brand(s2)
src, PTS2 = pointer_text(s2, "TextBox 8")
delete_shape(src)
slide2(s2, PTS2, title)

# ================================================================ SLIDE 3
s3 = S[2]
brand(s3)
src, PTS3 = pointer_text(s3, "TextBox 8")
delete_shape(src)
slide3(s3, PTS3, title)

# ================================================================ SLIDE 4
s4 = S[3]
brand(s4)
title(s4, "FEASIBILITY AND VIABILITY", 27)
src, PTS4 = pointer_text(s4, "TextBox 8")
delete_shape(src)

pointer_label(s4, 0.55, 1.18, 12.2, PTS4[0])          # Analysis of feasibility

# ---- what the delivered system costs and what it does, in four numbers
ev = [("23.7 K", "parameters in the neural core", "GTCRN · ICASSP 2024"),
      ("25.3 ms", "Lane B, end to end", "20 ms frame · 10 ms hop"),
      ("< 1 ms", "Lane A loop, closed", "anti-noise beats the wavefront"),
      ("~₹12 k", "prototype bill of materials", "Pi 5 · UMC202HD · cooler · PSU")]
x = 0.55
for v, l, sb in ev:
    block(s4, x, 1.40, 2.9, 0.86, fill=PALER, radius=0.08)
    stat(s4, x + 0.18, 1.48, 2.6, v, l, vs=22, ls=8.5, sub=sb)
    x += 3.10

# ---- the verification chain: how a claim becomes a frozen artefact
textbox(s4, 0.55, 2.34, 12.2, 0.18,
        [("VERIFICATION CHAIN — EVERY NUMBER IN THIS DECK TRACES BACK TO A "
          "CHECKSUMMED ARTEFACT", 7.5, True, LABEL)])
vchain = [("Capture", "96 kHz · 24-bit"),
          ("GO / NO-GO", "after every 3 shots"),
          ("Calibrate", "absolute dB SPL"),
          ("Measure", "54 quantities / shot"),
          ("Freeze", "SHA-256 data + engine"),
          ("Compare", "against the holdout"),
          ("Reproduce", "by config hash")]
GAPV = 0.22
vws = fit_widths(widest(vchain, 8.5, 6.5),
                 12.20 - GAPV * (len(vchain) - 1) + 0.001, 0.0, 8.5, pad=0.40)
x = 0.55
vcx = []
for i, ((t, sb), w) in enumerate(zip(vchain, vws)):
    gate = (t == "GO / NO-GO")
    chip(s4, x, 2.52, w, 0.46, t, sb,
         fill=RUSTPL if gate else WHITE, line=RUST if gate else STEEL,
         ts=8.5, ss=6.5, tag="s4.v")
    if i < len(vchain) - 1:
        flow(s4, [(x + w, 2.75), (x + w + GAPV, 2.75)], STEEL, 1.5, size=0.11)
    vcx.append(x + w / 2.0)
    x += w + GAPV
# the reject path — a range is not repeatable, so a bad take is caught on site
flow(s4, [(vcx[1], 2.98), (vcx[1], 3.10), (vcx[0], 3.10), (vcx[0], 2.98)],
     RUST, 1.25, size=0.10)
textbox(s4, vcx[0] - 0.30, 3.10, 2.60, 0.16,
        [("reject → re-shoot, on site", 6.8, True, RUST)])

# ---- the feasibility proof is shown, not asserted: our own range capture
slide_field.build(s4, y0=3.28, ph=1.12)

pointer_label(s4, 0.55, 5.12, 5.6, PTS4[1])           # Potential challenges/risks
pointer_label(s4, 6.60, 5.12, 6.15, PTS4[2] + " " + PTS4[3]
              if len(PTS4) > 3 else PTS4[2])          # Strategies for overcoming
risks = [("One-shot range access — nothing is repeatable",
          "GO / NO-GO after every three shots catches a bad take on site"),
         ("The microphone clips on the blast, irreversibly",
          "Staggered-gain pair 18–24 dB apart; the cold channel always survives"),
         ("The Pi 5 throttles and latency drifts",
          "Official cooler and 27 W supply are mandatory parts, not accessories"),
         ("Targets move with input SNR",
          "Reported as curves against input SNR, with the crossing point stated"),
         ("A denoiser can be judged in the wrong place",
          "The MELPe vocoder sits inside the evaluation chain — measured twice")]
y = 5.34
for rk, st in risks:
    block(s4, 0.55, y, 5.45, 0.30, fill=PALER, radius=0.06)
    textbox(s4, 0.66, y + 0.045, 5.25, 0.22, [(rk, 8.4, True, INK)])
    flow(s4, [(6.10, y + 0.15), (6.44, y + 0.15)], RUST, 1.4, size=0.11)
    textbox(s4, 6.60, y + 0.045, 6.15, 0.22, [(st, 8.4, False, STEEL)])
    y += 0.32

# ================================================================ SLIDE 5
s5 = S[4]
brand(s5)
title(s5, "IMPACT AND BENEFITS", 27)
src, PTS5 = pointer_text(s5, "TextBox 8")
delete_shape(src)

pointer_label(s5, 0.55, 1.16, 12.2, PTS5[0])          # Potential impact

# Hardware integration flow
photo_chip(s5, 0.55, 1.40, 2.50, 2.00, "hw/hw-exploded.png", "Acoustic Isolation", "MIL-STD-1474 earcup", hue=GREEN)
flow(s5, [(3.05, 2.40), (3.45, 2.40)], GREEN, 1.5, size=0.11)
photo_chip(s5, 3.45, 1.40, 2.50, 2.00, "hw/hw-headset.png", "Lane A Cancellation", "Zero-latency anti-noise", hue=BLUE)
flow(s5, [(5.95, 2.40), (6.35, 2.40)], BLUE, 1.5, size=0.11)
photo_chip(s5, 6.35, 1.40, 2.50, 2.00, "hw/hw-pi.png", "Lane B Processing", "Pi 5 Inference Core", hue=ORANGE)
flow(s5, [(8.85, 2.40), (9.25, 2.40)], ORANGE, 1.5, size=0.11)
photo_chip(s5, 9.25, 1.40, 2.50, 2.00, "hw/hw-radio.png", "Radio Integration", "Clean speech to SDR", hue=PURPLE)

# Benefits
pointer_label(s5, 0.55, 3.70, 12.2, PTS5[1])          # Benefits of the solution
ben = [(GREEN, GREEN_F, "Health & Safety", "Lane A protects the ear before any processing, preventing impulse-noise hearing loss."),
       (BLUE, BLUE_F, "Operational Continuity", "Commands survive gunfire. Re-tunes per frame for stationary and non-stationary noise."),
       (ORANGE, ORANGE_F, "Economic Scale", "Built on Pi 5 / microcontroller-class hardware. ~₹12k BOM, highly scalable."),
       (PURPLE, PURPLE_F, "Strategic Autonomy", "100% indigenous IP. No external cloud dependencies, deployable under Make in India.")]

x = 0.55
for hue, tint, h, d in ben:
    sh = block(s5, x, 4.00, 2.98, 1.10, fill=tint, radius=0.05)
    dashed(sh, hue, 1.0)
    block(s5, x, 4.00, 0.08, 1.10, fill=hue, shape=MSO_SHAPE.RECTANGLE)
    textbox(s5, x + 0.22, 4.07, 2.62, 0.22, [(h, 10, True, hue)], tag="s5.ben.h")
    textbox(s5, x + 0.22, 4.31, 2.62, 0.70, [(d, 7.6, False, INK)], line_spacing=0.94)
    x += 3.10

# Envelope
rule(s5, 0.55, 5.30, 12.2, color=MID)
textbox(s5, 0.55, 5.40, 4.20, 0.16, [("SYSTEM ENVELOPE", 7.5, True, LABEL)])
tg = [("> 15 dB", "SNR", BLUE), ("> 0.85", "STOI", BLUE), ("> 2.5", "PESQ", BLUE),
      ("< 25.3 ms", "lane B", GREEN), ("< 1 ms", "lane A", GREEN),
      ("< 6 W", "board power", ORANGE)]
x = 0.55
for v, l, hue in tg:
    textbox(s5, x, 5.60, 1.95, 0.28, [(v, 15.5, True, hue)])
    textbox(s5, x, 5.87, 1.95, 0.16, [(l, 7.4, True, INK)])
    x += 2.06

textbox(s5, 0.55, 6.30, 12.2, 0.16,
        [("MATURITY PATH   ·   bench integrated  →  range, calibrated data  →  "
          "field trial with a unit  →  radio integration  →  production, Make in India",
          7.4, True, LABEL)])

# ================================================================ SLIDE 6
s6 = S[5]
brand(s6)
title(s6, "RESEARCH AND REFERENCES", 27)
src, PTS6 = pointer_text(s6, "TextBox 8")
delete_shape(src)

pointer_label(s6, 0.55, 1.16, 12.2, PTS6[0])          # Details / links

# Replace the text blocks with visual proof
photo_chip(s6, 0.55, 1.40, 3.80, 2.70, "hw/pcb-lane-a.png", "Tentative PCB Design", "Lane A analog cancellation loop", hue=ORANGE)
photo_chip(s6, 4.50, 1.40, 3.80, 2.70, "hw/hw-bench.png", "Prototyping Workbench", "Real-time empirical validation", hue=BLUE)
photo_chip(s6, 8.45, 1.40, 3.80, 2.70, "hw/hw-iface.png", "System Interface", "Audio capture & routing", hue=GREEN)

# Add back a condensed references section
rule(s6, 0.55, 4.30, 12.2, color=MID)
textbox(s6, 0.55, 4.40, 12.2, 0.16, [("CORE LITERATURE & RESEARCH", 7.5, True, LABEL)])
refs = [
    ("Foundations", "Widrow — Adaptive Noise Cancelling, Proc. IEEE, 1975 · Varga & Steeneken — NOISEX-92, 1993"),
    ("Learned Enhancement", "GTCRN — Rong, ICASSP 2024 · DCCRN · FullSubNet · DeepFilterNet2 (real time on Pi 4)"),
    ("Impulsive Noise", "Ruhland — BMRI, IEEE/ACM TASLP 2015 · Yuan, Li & Kuruoğlu — α-stable noise, 2023"),
    ("Standards", "Zhang & Wang — Deep ANC, 2021 · MIL-STD-1474 · JSS 55555")
]
ry = 4.60
for category, details in refs:
    textbox(s6, 0.55, ry, 2.0, 0.18, [(category, 8.4, True, BLUE)])
    textbox(s6, 2.65, ry, 9.5, 0.18, [(details, 8.0, False, INK)])
    ry += 0.25

# Project links
rule(s6, 0.55, 5.80, 12.2, color=MID)
textbox(s6, 0.55, 5.90, 12.2, 0.16, [("PROJECT DELIVERABLES & SOURCE", 7.5, True, LABEL)])
DELIV = [(BLUE, "System Handbook", "zeit-handbook.netlify.app"),
         (GREEN, "3-D Workbench", "zeit-handbook.netlify.app/zeit-bench-3d"),
         (ORANGE, "Architecture Audit", "in the repository"),
         (PURPLE, "Source Toolkit", "github.com/Sarthakk1407/Zeit_at_SIH")]
x = 0.55
for hue, h, link in DELIV:
    sh = block(s6, x, 6.15, 2.90, 0.65, fill=WHITE, radius=0.05)
    dashed(sh, hue, 1.0)
    textbox(s6, x + 0.16, 6.25, 2.58, 0.20, [(h, 9.5, True, hue)], tag="s6.dl")
    textbox(s6, x + 0.16, 6.50, 2.58, 0.16, [(link, 7.2, True, hue)])
    x += 3.03

# ================================================================ LIVE LINKS
# The team's own deployment and repository links. They are built here rather
# than pasted into PowerPoint afterwards, because anything added by hand is
# lost the next time this script runs.
link_block(S[1], 0.55, 6.44, 5.30,
           "PROJECT HANDBOOK AND 3D WORKBENCH — LIVE DEPLOYMENT",
           ["https://zeit-handbook.netlify.app/",
            "https://zeit-handbook.netlify.app/zeit-bench-3d"])
link_block(S[2], 7.20, 6.62, 5.80,
           "SOURCE CODE — EVERY FIGURE IN THIS DECK IS REPRODUCIBLE FROM IT",
           ["https://github.com/Sarthakk1407/Zeit_at_SIH.git"],
           align_right=True)

# ---------------------------------------------------------------- structure
# Six slides, as the template's own instruction slide requires. That
# instruction slide is the seventh and is removed here.
_ids = list(sldIdLst)
sldIdLst.remove(_ids[6])

# ---------------------------------------------------------------- write
import sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else 'ZEIT_SIH2026_Idea.pptx'
try:
    prs.save(OUT)
except PermissionError:
    base, ext = os.path.splitext(OUT)
    n = 2
    while os.path.exists("%s_v%d%s" % (base, n, ext)):
        n += 1
    OUT = "%s_v%d%s" % (base, n, ext)
    prs.save(OUT)
    print("(original was locked — wrote %s instead)" % OUT)
print("saved", OUT, " ·  slides:", len(prs.slides._sldIdLst))
if ISSUES:
    print("\nTEXT-FIT WARNINGS (%d):" % len(ISSUES))
    for i in ISSUES:
        print("  ", i)
else:
    print("\nno text-fit warnings")
