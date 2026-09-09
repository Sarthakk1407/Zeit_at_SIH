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
import slide_mentor
from deckkit import (flow, INK, STEEL, MID, PALE, PALER, RUST, RUSTPL, GREEN, GREENPL,
                     WHITE, FONT, _in, textbox, block, chip, arrow, rule, vrule,
                     elbow, pointer_label, stat, delete_shape, set_ph_text,
                     check_fit, ISSUES)

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
    return t


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
    ("Team ID", "(from SIH portal)"),
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
tb.top = _in(2.45); tb.height = _in(3.95); tb.width = _in(5.9)

textbox(s1, 0.36, 6.55, 5.9, 0.38,
        [("Two-lane impulse-adaptive noise cancellation for defence "
          "communications", 10, False, RUST)], tag="s1.tag")

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
ev = [("23.7 K", "model parameters", "GTCRN, ICASSP 2024"),
      ("39.6", "MMAC per second", "runs below Jetson class"),
      ("2.78 ms", "per 20 ms frame", "closest prior work, on CPU"),
      ("~₹12 k", "prototype bill of materials", "excluding microphones")]
x = 0.55
for v, l, s in ev:
    block(s4, x, 1.42, 2.9, 1.02, fill=PALER, radius=0.08)
    stat(s4, x + 0.18, 1.54, 2.6, v, l, vs=24, ls=8.5, sub=s)
    x += 3.10

proof = [("Embedded feasibility is already demonstrated",
          "DeepFilterNet2 runs full-band speech enhancement in real time on a Raspberry Pi 4. "
          "Our model is roughly 75× smaller."),
         ("The architecture is assembled from published, reproducible parts",
          "GTCRN, Aux-IVA and BMRI all have public results. We are not inventing a model — "
          "the contribution is the data, the validation and the measurement."),
         ("The measurement toolkit already exists and passes its own self-test",
          "21 command-line tools, nine automated quality checks, calibration to absolute "
          "pressure, and a checksum-frozen reference.")]
y = 2.58
for h, d in proof:
    block(s4, 0.55, y, 12.2, 0.50, fill=WHITE, line=MID, line_w=0.75, radius=0.06)
    textbox(s4, 0.70, y + 0.07, 4.55, 0.36, [(h, 9, True, INK)], tag="s4.proof.h")
    textbox(s4, 5.35, y + 0.06, 7.25, 0.40, [(d, 8.2, False, STEEL)],
            line_spacing=0.94)
    y += 0.57

pointer_label(s4, 0.55, 4.36, 5.6, PTS4[1])           # Potential challenges/risks
pointer_label(s4, 6.60, 4.36, 6.15, PTS4[2] + " " + PTS4[3]
              if len(PTS4) > 3 else PTS4[2])          # Strategies for overcoming
risks = [("One-shot range access; nothing is repeatable",
          "GO / NO-GO validation after every three shots. Balloons and firecrackers give an "
          "energy-scaling axis with no range at all"),
         ("The microphone clips on the blast — irreversibly",
          "Staggered-gain pair 18–24 dB apart, so one channel always survives. Clipping is "
          "modelled in training rather than wished away"),
         ("Pi 5 throttles; latency drifts across a long run",
          "Official active cooler and 27 W supply, both mandatory. Report 99th-percentile "
          "frame time, never the mean"),
         ("PS targets may be unreachable at very low SNR",
          "Report PESQ, STOI and SNR as curves against input SNR and state the crossing "
          "point, rather than as a single pass/fail number"),
         ("α-stable augmentation may simply not help",
          "A Gaussian-augmented baseline is trained alongside. An honest negative result "
          "with an explanation is still a result")]
y = 4.62
for rk, st in risks:
    textbox(s4, 0.55, y, 5.45, 0.36, [(rk, 8.6, True, INK)], line_spacing=0.94)
    flow(s4, [(6.10, y + 0.11), (6.44, y + 0.11)], RUST, 1.4, size=0.11)
    textbox(s4, 6.60, y, 6.15, 0.36, [(st, 8.4, False, STEEL)], line_spacing=0.94)
    y += 0.40

# ================================================================ SLIDE 5
s5 = S[4]
brand(s5)
title(s5, "IMPACT AND BENEFITS", 27)
src, PTS5 = pointer_text(s5, "TextBox 8")
delete_shape(src)

pointer_label(s5, 0.55, 1.18, 12.2, PTS5[0])          # Potential impact
aud = [("The soldier", "Commands are heard through gunfire, and hearing is protected "
        "at the same time. MIL-STD-1474 sets the limit at the ear at 140 dB peak; "
        "few weapons produce below 150 dB.", RUST),
       ("The unit and its commander", "Fewer repeated transmissions, fewer "
        "misheard orders. The operational cost of a gunshot is measured directly "
        "as words lost per shot.", STEEL),
       ("Indian defence industry", "An indigenous, permissively licensed engine "
        "that runs on a ₹12,000 board and feeds a DRDO software-defined radio. "
        "No foreign cloud in the loop.", INK)]
x = 0.55
for h, d, c in aud:
    block(s5, x, 1.42, 3.94, 1.72, fill=PALER, radius=0.07)
    block(s5, x + 0.22, 1.62, 0.34, 0.34, fill=c, radius=0.5, shape=MSO_SHAPE.OVAL)
    textbox(s5, x + 0.68, 1.66, 3.05, 0.28, [(h, 12, True, INK)], tag="s5.aud.h")
    textbox(s5, x + 0.22, 2.06, 3.55, 1.00, [(d, 8.6, False, STEEL)],
            line_spacing=0.98)
    x += 4.13

pointer_label(s5, 0.55, 3.32, 12.2, PTS5[1])          # Benefits of the solution
ben = [("Operational", "Voice survives the noise class the problem statement names "
        "first, and the system adapts per frame rather than being tuned once"),
       ("Health and social", "Impulse noise is the leading cause of service-related "
        "hearing loss. Lane A protects the ear before any processing happens"),
       ("Economic", "A microcontroller-class model instead of a Jetson. Lower unit "
        "cost, lower power, longer field endurance"),
       ("Strategic", "Indigenous IP, permissive licences, no GPL and no cloud "
        "dependency — deployable under Make in India procurement")]
x = 0.55
for h, d in ben:
    block(s5, x, 3.56, 2.98, 1.28, fill=WHITE, line=MID, line_w=0.75, radius=0.07)
    textbox(s5, x + 0.18, 3.70, 2.62, 0.26, [(h, 10.5, True, RUST)], tag="s5.ben.h")
    textbox(s5, x + 0.18, 3.98, 2.62, 0.78, [(d, 8.2, False, STEEL)],
            line_spacing=0.96)
    x += 3.10

rule(s5, 0.55, 5.02, 12.2, color=MID)
textbox(s5, 0.55, 5.14, 12.2, 0.20,
        [("TARGETS THE SYSTEM IS BUILT AGAINST — reported as curves against input SNR, "
          "with the crossing point stated", 7.5, True, MID)], tag="s5.tgtlab")
tg = [("> 15 dB", "SNR"), ("> 0.85", "STOI"), ("> 2.5", "PESQ"),
      ("< 25.3 ms", "latency"), ("140 dB", "MIL-STD-1474 limit at the ear"),
      ("watts", "power draw, on the board")]
x = 0.55
for v, l in tg:
    stat(s5, x, 5.36, 2.0, v, l, vs=19, ls=7.8)
    x += 2.06

textbox(s5, 0.55, 6.28, 12.2, 0.30,
        [("Wider application — the same engine serves aerospace ground crew, armoured "
          "vehicle intercom, mining and heavy industry: any environment where speech "
          "must survive impulsive noise.", 8.6, False, STEEL)], tag="s5.wider")

# ================================================================ SLIDE 6
s6 = S[5]
brand(s6)
title(s6, "RESEARCH AND REFERENCES", 27)
src, PTS6 = pointer_text(s6, "TextBox 8")
delete_shape(src)

pointer_label(s6, 0.55, 1.18, 12.2, PTS6[0])          # Details / links
cols = [
    ("Foundations", [
        "Widrow et al. — Adaptive Noise Cancelling, Proc. IEEE 63(12), 1975",
        "Varga & Steeneken — NOISEX-92, Speech Communication 12(3), 1993",
        "Shao & Nikias — Fractional lower-order moments, 1993",
        "Wang & Chen — Supervised Speech Separation, IEEE/ACM TASLP, 2018"]),
    ("Learned enhancement", [
        "DCCRN — complex-domain enhancement, arXiv:2008.00264",
        "FullSubNet — full-band + sub-band fusion, arXiv:2010.15508",
        "DeepFilterNet2 — real time on a Raspberry Pi 4, IWAENC 2022",
        "Rong et al. — GTCRN, ICASSP 2024 · 23.7 K params, 39.6 MMAC/s",
        "H-GTCRN — Aux-IVA + GTCRN hybrid, dual channel"]),
    ("Impulsive noise", [
        "Ruhland et al. — Binary Mask Residual Interpolation, TASLP 23(10), 2015",
        "Yuan, Li & Kuruoğlu — α-stable training noise, arXiv, 2023",
        "Berger et al. — IS³ impulsive–stationary separation, WASPAA 2025",
        "Ono — Auxiliary-function IVA, WASPAA 2011"]),
    ("Baselines and metrics", [
        "Zhang & Wang — Deep ANC, Neural Networks, 2021",
        "Tan, Zhang & Wang — dual-microphone DC-CRN, IEEE/ACM TASLP, 2021",
        "Le Roux et al. — SDR: half-baked or well done?, ICASSP 2019",
        "Reddy et al. — DNSMOS P.835, ICASSP 2022",
        "MIL-STD-1474 · ANSI/ASA S3.2 · JSS 55555"]),
]
x = 0.55
for h, items in cols:
    block(s6, x, 1.42, 2.98, 2.62, fill=PALER, radius=0.07)
    textbox(s6, x + 0.16, 1.54, 2.66, 0.24, [(h, 10, True, RUST)], tag="s6.col.h")
    y = 1.82
    for it in items:
        textbox(s6, x + 0.16, y, 2.66, 0.44, [(it, 7.4, False, STEEL)],
                line_spacing=0.94)
        y += 0.44
    x += 3.10

rule(s6, 0.55, 4.22, 12.2, color=MID)
textbox(s6, 0.55, 4.34, 12.2, 0.22,
        [("WHERE THE PUBLISHED WORK STOPS — the gaps this project is built on",
          8, True, MID)], tag="s6.gaplab")
gaps = [("No impulsive noise in deep ANC at all",
         "Every result table uses engine, factory, babble and speech-shaped noise. "
         "The foundational paper does not address the noise class DRDO names first."),
        ("Latency is bought back by prediction",
         "1.5–1.7 dB lost per 10 ms — on periodic noise. On a gunshot, prediction has "
         "nothing to work with. Nobody has measured the collapse."),
        ("RMS normalisation is formally invalid",
         "For heavy-tailed noise the variance is infinite. The closest prior system "
         "normalises by RMS; the fix is cited inside another paper we hold."),
        ("Microphone-side clipping is modelled by nobody",
         "Loudspeaker saturation is modelled carefully. A 140 dB blast destroys the "
         "waveform at the capsule, before any algorithm sees it.")]
x = 0.55
for h, d in gaps:
    block(s6, x, 4.58, 2.98, 1.30, fill=WHITE, line=RUST, line_w=0.75, radius=0.07)
    textbox(s6, x + 0.16, 4.70, 2.66, 0.40, [(h, 8.8, True, INK)],
            line_spacing=0.94)
    textbox(s6, x + 0.16, 5.14, 2.66, 0.66, [(d, 7.4, False, STEEL)],
            line_spacing=0.94)
    x += 3.10

textbox(s6, 0.55, 6.06, 12.2, 0.50,
        [("Full technical account, interactive 3-D prototype model and the design "
          "review are maintained alongside this submission. Sixteen sources read end "
          "to end; five of them put code on the device — Widrow, Shao & Nikias, BMRI, "
          "GTCRN and H-GTCRN. Everything else is method, baseline or evidence.",
          8.4, False, STEEL)], line_spacing=0.98)

# ================================================================ MENTOR SLIDE
slide_mentor.build(S[6], TEAM, delete_shape)
_ids = list(sldIdLst)
sldIdLst.remove(_ids[6])
sldIdLst.insert(1, _ids[6])          # now slide 2; the rest shift down

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
