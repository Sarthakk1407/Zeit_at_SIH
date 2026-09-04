# Shooting range recording — field checklist

**One visit only. Work top to bottom. Do not skip Tier 0.**

---

## Before you leave home

- [ ] Recorder charged + spare batteries
- [ ] Spare SD card (formatted)
- [ ] Phone charged (second recorder + logging)
- [ ] Windscreen / foam on mic — **mandatory**
- [ ] Mic stand (never hand-hold — handling noise)
- [ ] Tape measure or laser distance meter (pace count as backup)
- [ ] SPL meter app installed + note the app name/model
- [ ] Portable Bluetooth speaker (for sine sweep) OR 5+ balloons
- [ ] Sine sweep file loaded on phone: 20 Hz–20 kHz log sweep, 10 s
- [ ] Hearing protection for yourself
- [ ] Printed metadata sheet + pen (phone may die)
- [ ] Ask range officer permission for balloon pops / speaker sweep in advance

**Recorder settings — set before arriving:**

| Setting | Value |
|---|---|
| Sample rate | 96 kHz (48 kHz absolute minimum) |
| Bit depth | 24-bit (32-bit float if your recorder supports it) |
| Format | WAV / PCM — never MP3 |
| Auto gain | **OFF** |
| Limiter | **OFF** |
| Low-cut filter | **OFF** |

If you can borrow a 32-bit float recorder, do it — clipping becomes impossible and the whole gain problem disappears.

---

## TIER 0 — Do this before any shooting (20 min)

If you skip these, every measurement afterwards is relative-only and your synthetic-vs-real comparison collapses.

### 0.1 Calibration tone
- [ ] Set gain to the level you'll use for shots. **Write it down.**
- [ ] Place SPL meter next to the mic capsule
- [ ] Play a steady 1 kHz tone from the speaker
- [ ] Record 30 s. Log the SPL meter reading in dB
- [ ] Repeat at 2–3 different levels (e.g. 70, 80, 90 dB)

**Why:** This is the only way to convert digital samples to Pascals. Without it you cannot extract peak overpressure, which means no Friedlander parameter fitting.

### 0.2 Noise floor
- [ ] Cover the mic, same gain setting
- [ ] Record 60 s of silence

### 0.3 Mic frequency response reference
- [ ] Speaker at exactly 1 m from mic, on-axis
- [ ] Play the log sine sweep, record it
- [ ] Note the exact speaker model
- [ ] Repeat 3 times

**Why:** Lets you deconvolve your mic's colouration out later.

### 0.4 Range impulse response — **highest value item on this sheet**
- [ ] Speaker at the firing position, mic at each recording position
- [ ] Play the 10 s log sweep, record. 3 repeats per position
- [ ] Do this for **every** mic position you'll use
- [ ] Backup method if no speaker: pop 3–5 balloons at the firing position

Sine sweep is more reliable and accurate than balloon pops, but balloons work with zero equipment and give fairly uniform radiation.

**Why:** With the range IR you can convolve any synthetic gunshot into that exact acoustic space. One visit → unlimited realistic data.

### 0.5 Geometry — measure and photograph everything
- [ ] Mic height above ground (cm) — **ground reflection delay depends on this**
- [ ] Firing point → mic distance (m)
- [ ] Mic height at firing point (muzzle height)
- [ ] Ground surface: concrete / dirt / grass / gravel
- [ ] Distance to nearest wall, berm, or overhead cover
- [ ] Is the range enclosed, semi-enclosed, or open?
- [ ] Photo of every setup **with tape measure visible in frame**
- [ ] Wide shot + sketch of the whole layout

### 0.6 Weather
- [ ] Temperature (°C)
- [ ] Humidity (%)
- [ ] Wind speed + direction
- [ ] Time of day

**Why:** Atmospheric absorption is a function of temperature and humidity. Your propagation model needs these numbers.

---

## TIER 1 — Gunshots

### Two-recorder setup

| Recorder | Position | Role |
|---|---|---|
| **A — main mic** | Moves between positions | Your primary data |
| **B — anchor (phone)** | **Fixed, never moves all day** | Common reference to normalise shot-to-shot variation |

The anchor recorder is the trick that makes single-mic data usable. Every shot is captured at one constant position, so you can separate "this shot was louder" from "this position is louder".

### Recording discipline
- [ ] **Record continuously.** One long file per session. Do not stop/start between shots — you will lose shots.
- [ ] Slate every shot out loud before firing: *"Shot 14, 90 degrees, 10 metres, gain 5"*
- [ ] After the first 3 shots: **stop and listen back.** Check for clipping, wind rumble, handling noise. Fix now, not later.

### Priority order of variables

**1. Azimuth (highest value — do this first)**

Muzzle blast is strongly directional. When the muzzle faces away from the mic, peak level drops by 20 dB or more. This is the hardest thing to model and the best thing to validate against.

At a real range you'll be beside or behind the shooter, so realistically you'll get:

- [ ] 90° (directly to the side) — 10 shots
- [ ] 135° (behind and to the side) — 10 shots
- [ ] 180° (directly behind shooter) — 10 shots
- [ ] 45° if the range layout safely allows — 10 shots

Note honestly in your report that 0° (downrange) was not accessible. That is a normal constraint, not a flaw.

**2. Distance (second priority)**

- [ ] 2 m — 5 shots
- [ ] 5 m — 5 shots
- [ ] 10 m — 5 shots
- [ ] 25 m — 5 shots (if range allows)

Keep azimuth constant while varying distance.

**3. Gain / clipping (free — costs no extra shots)**

Set recorder A and B to different gains so every shot is captured both clean and clipped.

- [ ] Low gain set — no clipping, clean waveform
- [ ] Medium gain set
- [ ] High gain set — **deliberately clipped**

Firearms exceed 154 dB SPL at 3 m; consumer mics saturate around 120–130 dB. Your headset mic **will** clip in the field, so clipped data is training data, not spoiled data.

**4. Weapon / ammunition (log whatever you get)**

- [ ] Weapon make, model, barrel length
- [ ] Caliber
- [ ] Ammunition type / load
- [ ] Suppressed or unsuppressed

Do not chase multiple weapons if it costs you azimuth coverage. One weapon, well characterised, beats four weapons badly sampled.

**Minimum viable haul: 50 well-documented shots. Not 500 undocumented ones.**

---

## TIER 2 — Mechanical action sounds

Almost nobody records these, and they are what make synthetic gunshots sound real instead of like a bare pressure pulse. A gunshot event has three parts: muzzle blast and shock wave, mechanical action sounds, and environmental reflections. Close recordings capture the mechanical layer.

Close-mic these as **separate short clips**, low gain, quiet moment:

- [ ] Bolt cycling / slide racking
- [ ] Cocking, hammer fall
- [ ] Trigger click (dry fire, if permitted)
- [ ] Brass ejection
- [ ] Brass hitting the ground (concrete and dirt separately if possible)
- [ ] Magazine insert and removal
- [ ] Safety on/off click
- [ ] General handling, sling, rustle

- [ ] **Rapid succession**: 2–3 shots fast, if permitted. Captures overlapping reverb tails.

---

## TIER 3 — Speech and ambience (your ANC gold)

This is the part that makes it a *noise cancellation* dataset rather than a gunshot dataset.

- [ ] **5 minutes of range ambience**, no shots

- [ ] **Speech during live shots — your single most valuable file.** 10+ minutes.
  - Person reads sentences at normal conversational distance while firing continues
  - Read in **both Hindi and English**
  - Use the same fixed sentence list throughout
  - Vary distance: close-talk (5 cm, boom-mic style) and 30 cm

- [ ] **Same sentences, same person, same distance, in quiet** — recorded at the range during a firing pause. Gives you a near-paired clean reference.

- [ ] **Speech with hearing protection on** — the speaker will unconsciously raise their voice and shift their spectrum. That is the Lombard effect, and it is exactly the vocal style your system will face.

- [ ] Shouted range commands over gunfire
- [ ] Distant shots from other lanes
- [ ] Footsteps on gravel, general range activity

---

## TIER 4 — Before you leave the range

- [ ] Listen back to a sample from each tier
- [ ] Confirm the metadata sheet has a row for every shot
- [ ] **Copy all files to phone / cloud before leaving**
- [ ] Photograph your filled-in paper metadata sheet
- [ ] Take a final wide photo of the range layout
- [ ] Thank the range officer — you may want to come back

---

## Split the data before you leave

Decide this at the range, not afterwards. Write it on the sheet.

| Split | Contents | Rule |
|---|---|---|
| **Fit set (~30%)** | One weapon, azimuth 90°, distance 10 m | Extract Friedlander parameters from these |
| **Holdout (~70%)** | Everything else | **Do not open until the generator is frozen** |

If you tune your synthesiser on the same recordings you later compare against, that is curve fitting, not validation — and any reviewer will spot it immediately.

---

## Safety

- Hearing protection on at all times
- No equipment downrange, ever
- Range officer's instructions override everything on this sheet
- Get explicit permission before balloon pops or playing sweeps
- Mic stands well clear of the firing line
