# Range Data Collection Toolkit

Field toolkit for a **one-shot** gunshot recording session. You cannot come
back, so the design goal throughout is: *find out at the range whether the data
is usable, while you can still do something about it.*

**All commands below are run from the `data_collection/` directory.**

Runs fully offline, CPU only. `numpy`, `scipy`, `matplotlib` — plus
`sounddevice` if you record through this toolkit rather than a standalone recorder.

---

## Install (do this at home, not at the range)

```bash
python3 -m pip install -r requirements.txt
```

There is deliberately **no `soundfile`/`libsndfile` dependency**. WAV I/O is
handled by `wavio.py`, a plain RIFF parser covering 16/24/32-bit PCM and
32/64-bit float. A broken native library cannot strand you in the field.

## Prove it works BEFORE range day

Non-negotiable. Do it the day before, on the actual laptop you are taking.

```bash
python3 make_test_data.py --out testdata/
python3 selftest.py testdata/
```

You want `ALL CHECKS PASSED`. `make_test_data.py` synthesises deliberately
broken recordings — clipped, wind-blown, truncated, buried, DC-offset,
wrong-sample-rate, knocked-stand — and `selftest.py` asserts that
`validate.py` returns NO-GO for each one *with the right reason*.

---

## Where everything is saved

Organised by **recording**, not by session — a session wrapper buries the thing
you actually go looking for. Every recording is a numbered folder directly
inside `DATA/`. Shared assets are `_`-prefixed so they sort out of the way.

```bash
python3 session.py init --name S1 --out ../DATA --hours 3.5
```

```
DATA/
  001_air-rifle-5m/
      raw.wav          the recording, untouched
      validate.json    the GO / NO-GO verdict
      events/          per-shot slices + manifest
      analysis/        features.json + .csv
      report.html      open this
      quicklook/       waveform + spectrogram
      take.json        what this recording was
  002_air-rifle-10m/
  003_.../
  _index.md            every recording, its verdict, one table
  _calibration/        calibration.json (once per gain setting)
  _ir/                 range impulse responses
  _plan/               RUN_SHEET.txt + metadata_S1.csv
  _playback/           sweep, tones, pink noise, order sheet
```

`_index.md` is regenerated after every capture, so there is always one place
that lists what exists and which recordings came back NO-GO.

## One take, one command

```bash
python3 capture.py --device 3
```

The monitor opens and **everything you see is being recorded**. Close the
window and it asks:

```
  Name this recording [take-002]: air rifle 5m
```

Then it files it under `002_air-rifle-5m/` and runs validate, slice,
measure, plot, report and compressed copy, and prints GO or NO-GO with the
reason. Nothing else to remember between shots.

```bash
python3 capture.py --device 3 --name "air rifle 5m" --expect-events 1
python3 capture.py --device 3 --type cal --spl-db 94.0    # calibration tone
python3 capture.py --device 3 --type ir --inverse playback/inverse_filter.wav
```

`--type cal` writes the session's `calibration.json`, and every later take is
measured in absolute SPL automatically.

**Before you pack up, every time:**

```bash
python3 session.py status ../DATA
```

It compares disk against the plan and names what is still missing while a
re-shoot is still possible: no calibration, no impulse response, takes never
validated, takes that came back NO-GO, missing holdout rows, no backup. Exit
code 1 if anything is wrong.

## Range-day quickstart

Commands in the order you will actually run them. `$W` is whatever the
recorder just wrote.

### 1. Before you leave — generate the playback signals

```bash
python3 gen_signals.py --out playback/
lpr playback/PLAYBACK_ORDER.txt          # print it. Paper, not phone.
```

Copy `playback/` to the device you will play from. Leave
`inverse_filter.wav` on the laptop — it is a processing asset, not something
you play.

### 1a. Watch the signal before you trust it

```bash
python3 monitor.py --device 3                            # live window, saves NOTHING
python3 monitor.py --device 3 --record 00_raw/take.wav   # watch AND keep it
python3 monitor.py --device 3 --test-mode                # laptop mic / earbuds
```

**The monitor is a view, not a recorder.** Without `--record` you can watch a
take go perfectly and be left with no record of it. It says so on exit.

Four panels: waveform, spectrum, level with peak hold against the gain target,
and a sub-50 Hz wind meter. Press `r` to reset the peak hold, close the window
to quit.

Look hardest at the **spectrum**. If the top of the band is flat and dead
rather than showing a noise floor all the way to Nyquist, **the device is
resampling** — the file will say 96 kHz and contain 44.1 kHz. This was found on
real hardware here: a 44.1 kHz laptop mic accepted a 96 kHz request and CoreAudio
upsampled silently, producing a file that passed every other check. `validate.py`
now fails it, and in the monitor you can see it live.

### 1b. Recording on a laptop + USB interface

```bash
python3 record.py --list                       # find the interface
python3 record.py --meter --device 3           # set gain, records nothing
python3 record.py --device 3 --out S1_take001.wav
```

`--meter` is how you set gain without live fire: pop a balloon at the real
distance and angle, read the **hold** value, aim for −18 to −12 dBFS, then back
off further because the real source is louder than the proxy. An averaging
meter under-reads a gunshot peak by 30 dB or more, which is why this one shows
true sample peak with a hold.

`record.py` hard-refuses two traps:

- **Bluetooth headsets** — they record 16 kHz mono through AGC and noise
  suppression. The file looks fine in a browser and is worthless: nothing above
  ~8 kHz survives and the peaks are already gone.
- **Virtual/loopback devices** (BlackHole, Aggregate, screen-share audio) —
  not microphones.

It also refuses to overwrite an existing take.

The real advantage of laptop + interface over a standalone recorder is the tight
loop: record, validate, fix, re-shoot, without ever touching an SD card.

### 2. At the range — calibrate first, before any shooting

Play `cal_1k_-20dBFS.wav`, hold the SPL meter at the mic, write the reading down.

```bash
python3 calibrate.py $W --spl-db 94.0 --out calibration.json
```

Skip this and every level in your dataset is relative forever. It cannot be
recovered afterwards.

### 3. Noise floor and range impulse response

```bash
python3 validate.py $W_floor                                  # mic covered, 60 s
python3 ir_extract.py $W_sweep --inverse playback/inverse_filter.wav --out ir/
python3 ir_extract.py $W_balloon --balloon --out ir/          # fallback
```

Check `direct-to-noise` in the output. Below ~35 dB the RT60 numbers are
fitting noise, so pop a balloon and use the fallback path.

### 4. Shoot. Validate after the first 3 rounds, then after every change.

```bash
python3 validate.py $W --expect-events 5
```

**Always pass `--expect-events`** with the number of rounds you actually
fired. It is the one thing the tool cannot work out for itself: a quiet file
is correct for ambience and a catastrophe for a shot take. With it, a shot
that was too quiet to detect becomes a hard NO-GO instead of a shrug.

Re-run after every change of source, gain, distance, mic position or weather.

- **GO** — carry on.
- **NO-GO** — stop and fix it now. Read the reason line.

### 5. Cut the take into events and bind it to your log sheet

```bash
python3 ingest.py $W --meta range_metadata_log.csv --out events/ --dry-run
python3 ingest.py $W --meta range_metadata_log.csv --out events/
```

Run `--dry-run` first and eyeball the onsets against your log. Events are
matched to CSV rows **in order**, so one miscount corrupts every pairing after
it. `ingest.py` exits non-zero on a count mismatch.

### 6. Measure the signature and look at it

```bash
python3 analyze.py events/ --cal calibration.json --label real \
        --out features_real.json --csv features_real.csv
python3 report.py features_real.json --audio events/ --out report.html
open report.html
```

`analyze.py` is deliberately **one engine**. Whatever is compared against this
data later must be measured by this same code — if two sets are measured by
different code, part of any difference between them is a difference in the
measuring, and the comparison proves nothing.

`report.py` writes a single HTML file with the figures embedded as base64, so
it opens with no internet and no server.

**Calibrate before you rely on any of it.** Uncalibrated levels are relative to
full scale: they cannot be compared with any measurement made anywhere else,
and the report says so in red.

### 7. Eyeball everything before you pack up

```bash
python3 quicklook.py events/ --out looks/ --cal calibration.json
open looks/contact_sheet.png
```

### Keep a holdout

The metadata CSV has a `split` column. Decide `fit` vs `holdout` **at the
range**, not afterwards. Anything later tuned against the real data cannot then
be validated against that same data — that is circular, and it is the first
thing a sharp reviewer will go looking for. Reserve a set of events you will not
look at while building anything.

Clipped events are outlined in red. Look for doubled reports, ricochets, and
anyone talking over a shot.

---

## The tools

In the order you use them.

| Tool | What it does |
|---|---|
| `session.py init` | Creates the `DATA/` folder, the run sheet and the playback signals |
| `gen_signals.py` | Sweep + matched inverse filter, 1 kHz tones, pink noise, printable order sheet |
| `plan.py` | The one-trip run sheet and a pre-filled metadata CSV, checked against your time slot |
| `monitor.py` | **Live scope window** — waveform, spectrogram, spectrum, level, wind, and every measured number, live |
| `record.py` | Terminal-only recorder with a text peak meter, for when there is no display |
| `capture.py` | **One command per recording.** Monitor opens, you close it, it names and processes the take |
| `validate.py` | **GO / NO-GO on one file in under 10 s.** The only tool that matters at the range |
| `ingest.py` | Slices a take into per-event WAVs and binds them to the metadata CSV |
| `calibrate.py` | Turns dBFS into absolute Pascals from an SPL meter reading |
| `ir_extract.py` | Range impulse response + RT60 per octave band, sweep or balloon-pop |
| `analyze.py` | **The measurement engine.** 54 quantities per recording |
| `report.py` | One self-contained HTML page from that measurement |
| `quicklook.py` | Waveform + spectrogram + 1/3-octave levels, plus a contact sheet |
| `session.py status` | What is present, what is missing, run it before packing up |
| `session.py freeze` / `verify` | Locks the reference and the engine so a later comparison cannot move them |
| `session.py backup` / `listen` | Verified copy to a drive; compressed copies for playing |

Supporting modules: `wavio.py` (RIFF I/O), `dsp.py` (filters, onset detection,
Schroeder RT60), `provenance.py` (keeps synthetic audio out of the dataset).
`make_test_data.py` and `selftest.py` are the pre-flight check.

Every tool: never modifies its input, writes only where told, and fails loudly
with a readable message and exit code 2 rather than a traceback.

## What `validate.py` checks

| Check | Fails when |
|---|---|
| Format | Sample rate or bit depth is not what you expected; truncated `data` chunk |
| Clipping | **Any** clipped sample lands on an impulse — the peak is destroyed and the file is unusable for level work |
| DC offset | Offset above 1% of full scale |
| Noise floor | Floor above −35 dBFS |
| Bandwidth | The header's sample rate is a lie — the band ends in a cliff into digital silence, meaning the device resampled |
| Wind / rumble | Sub-50 Hz dominates the background, measured *away* from the impulses |
| Impulse complete | File starts or ends loud, or an event sits within 0.5 s of the end |
| Events found | Count differs from `--expect-events`, or worst-case event SNR under 20 dB |
| Handling noise | More than 3 low-frequency-only thumps (cable tugs, stand knocks) |

Two of these were harder than they look, and the reasoning is written into the
code so it does not get "simplified" away later:

- **Wind** is measured only in the gaps between impulses. Gunshots have huge
  genuine low-frequency content; measuring across the whole file reports the
  shot, not the weather.
- **Bandwidth** is judged by two signatures together, not by where content
  ends. A genuinely dull source also ends early; what a resample leaves is a
  near-vertical cliff into *numerical* silence, because interpolation puts
  exactly zero energy above the original Nyquist while any real recording has
  mic and ADC noise filling the band. Measured here: a real CoreAudio upsample
  gave −135 dB and a 62 dB cliff, a merely low-passed real file gave −81 dB and
  19 dB. An earlier single-signature version failed the low-passed file, which
  is precisely the false positive that teaches an operator to ignore warnings.
- **Handling noise** is separated from gunshots by spectral shape, not by
  loudness or by timing. Low-passing to 100 Hz leaves a narrowband signal whose
  Rayleigh envelope naturally swings >15 dB, so a relative-prominence test
  fires constantly on quiet ambience. Measured on this data a gunshot sits at
  −2 to −16 dB LF/HF and a stand knock at +33 dB, so the discriminator is that
  ratio, with ~20 dB of margin either side.

## Known limits

- Event detection assumes impulsive sources separated by at least `--min-sep`
  (0.30 s default). Full-auto bursts need a smaller value and manual review.
- RT60 is only meaningful when `direct-to-noise` exceeds ~35 dB.
- `calibrate.py` assumes the recorder gain is unchanged between the tone and
  the shots. **Change the gain and the calibration is void** — record a fresh
  tone at the new setting.
- The Friedlander blast model in `make_test_data.py` is for exercising the
  tools, not a substitute for real data or a source of acoustic claims.
- **Microphone max SPL is the binding constraint, and no software here can fix
  it.** A 3.5mm electret tops out around 100–120 dB SPL; a blank pistol at 1 m
  is 140–155 dB. Once the capsule or its internal FET saturates, no pad or gain
  change downstream recovers the waveform — only distance helps. Check your
  mic's "Max SPL" spec against the source before trusting any recording of it.
