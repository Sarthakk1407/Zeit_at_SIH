# Dataset specification — every noise class, every source

The PS asks for "a scalable dataset pipeline for generating realistic
noisy-clean speech pairs". This file is that pipeline's input list.

**The rule from `workflow.md` §5.1:** the real recordings are *not* the training
set. They are the reference. The DNN trains on generated audio, which is
effectively unlimited — the limit is compute, not recordings.

---

## 0. What we already own

| | |
|---|---|
| Real impulsive events | **44** (`REFERENCE_REAL/events_impulse/`) |
| All detected events | 213 |
| Reference statistics | `REFERENCE_REAL/analysis/stats_impulse.json` |
| Calibrated? | **No** — levels are dBFS, not dB SPL |

These 44 events are the ground truth the synthetic generator is validated
against. Nobody else at SIH will have measured, sliced, per-event-analysed
impulsive data with a frozen measurement engine.

---

## 0.5 REAL data that already exists — download this before generating anything

Researched 8 Sep 2026. Real recordings beat synthetic wherever they exist; the
generator is for coverage the real world will not hand you.

### ⭐ MAD — Military Audio Dataset (the single best match to this PS)

Published in *Nature Scientific Data*, 2024. Its class list is almost the PS's
noise list.

| | |
|---|---|
| Clips | **8,075** |
| Duration | ~12 hours, 1–10 s per clip |
| Sample rate | 16 kHz |
| Licence | **CC BY 4.0** |
| Data | `figshare.com/articles/c/A_military_audio_dataset_for_situational_awareness_and_surveillance/c.7001919.v1` |
| Code | `github.com/kaen2891/military_audio_dataset` |

| Class | Clips | % |
|---|---|---|
| Gunshot | 1,714 | 21.2 |
| Shelling *(artillery)* | 1,173 | 14.5 |
| Communication | 1,150 | 14.2 |
| Vehicle | 1,123 | 13.9 |
| Helicopter | 1,009 | 12.5 |
| Fighter *(jet)* | 985 | 12.2 |
| Footsteps | 921 | 11.4 |

**Caveat to state honestly:** sourced from military training and education
videos on YouTube, so it carries YouTube's compression. Fine for training and
for class coverage; **not** a substitute for calibrated measurement, and not
usable for absolute SPL or Friedlander claims. Our own range data stays the
reference.

### Gunshots — calibrated and multi-orientation

| Dataset | Size | Detail | Access |
|---|---|---|---|
| **Cadre Gunshot Audio Forensics** | **~10,000 recordings** | 20 firearms × 20 positions × 4 devices; rural Arizona, Summer 2017, NIJ Grant 2016-DN-BX-0183 | `cadreforensics.com/audio/` |
| **Zenodo Gunshot/Gunfire** | **2,148 files**, 1.6 GB | 4 firearms, multi-orientation, edge devices around an outdoor range | `zenodo.org/records/7004819` — **CC BY 4.0** |
| **C3GD** — Certus Caliber Classification | — | caliber classification set | arXiv 2606.18135 |
| **Free Firearm Sound Library** | — | community sound-effects library | **CC0** |
| Composite (published) | **22,306 recordings** | 21 calibers, 85 unique firearms across five open-access sets | see arXiv 2606.19568 |

Cadre is the one that matters most: **twenty positions per firearm** is exactly
the azimuth/distance grid our own field checklist asks for, already measured.

### Drone / UAV

| Dataset | Detail | Access |
|---|---|---|
| **DREGON** | 8-channel mic array **on** a quadrotor, 44.1 kHz, in-flight + per-rotor rps, static and free flight | `dregon.inria.fr/datasets/dregon/` |
| **DroneAudioSet** | **23.5 hours**, systematically collected | `huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/` — **MIT** |
| **DroneAudioDataset** | drone vs background | `github.com/saraalemadi/DroneAudioDataset` |

DREGON is unusual and useful: the array is *on* the airframe, so it captures
ego-noise the way a headset captures the wearer's own environment.

---

## 0.6 Clean speech — Stage 0d can be unblocked today

| Corpus | Size | Why it matters here |
|---|---|---|
| **SPRING-INX** (IIT Madras) | **~2,000 h**, 10 Indian languages incl. Hindi, manually transcribed | Funded by **MeitY, Government of India**, under the National Language Translation Mission — an Indian-government-funded corpus is the right optics for a DRDO deliverable |
| **IndicVoices-R** | **1,704 h**, 10,496 speakers, 22 Indian languages | largest Indian TTS-grade set |
| **LAHAJA** | multi-accent Hindi benchmark | tests accent robustness |
| **LibriSpeech** | ~1,000 h EN | bulk, CC BY 4.0 |
| **VCTK** | 109 speakers, 48 kHz | speaker variety |
| **EARS** | 100 speakers, anechoic, 48 kHz | high-fidelity targets |

### ⭐ Lombard GRID — the gap, now with a source

| | |
|---|---|
| Talkers | **54** (30 F, 24 M) |
| Utterances | 100 per talker — **50 Lombard + 50 plain**, paired |
| Total | 5,400 utterances (16,200 files with the two video views) |
| Extras | versions with speech-shaped noise added at several SNRs |
| Access | `spandh.dcs.shef.ac.uk/avlombard/` — freely available |

The paired plain/Lombard design is what makes it valuable: the same speaker,
the same sentence, with and without the Lombard reflex. That is a controlled
measurement of exactly the ~5 dB penalty a neutral-trained model pays, and it
costs one download.

**Recommended 0d decision:** SPRING-INX (Hindi bulk) + LibriSpeech (English
bulk) + VCTK/EARS (high-fidelity) + **Lombard GRID at ≥20 %**.

---

## 1. Noise classes the PS names, and where each comes from

The PS names: *gunshots, artillery fire, helicopter rotor noise, armored
vehicle sound, emergency sirens, drones, vehicle engines, wind.*

| # | Class | Type | Primary source | Backup |
|---|---|---|---|---|
| 1 | **Gunshot / muzzle blast** | impulsive | **Ours** — range trip | Cadre Gunshot Forensics, Kabealo multi-orientation |
| 2 | **Artillery / cannon / explosion** | impulsive | AudioSet (`Cannon`, `Explosion`, `Artillery fire`) | FSD50K, freesound |
| 3 | **Machine gun / burst fire** | impulsive | **NOISEX-92** (`machinegun`) | AudioSet |
| 4 | **Tank / tracked vehicle** | stationary | **NOISEX-92** (`leopard`, `m109`) | AudioSet `Military vehicle` |
| 5 | **Armored / wheeled vehicle** | stationary | NOISEX-92 (`volvo`), MUSAN | UrbanSound8K `engine_idling` |
| 6 | **Helicopter rotor** | stationary-periodic | ESC-50 (`helicopter`), AudioSet | FSD50K |
| 7 | **Jet / aircraft cockpit** | stationary | **NOISEX-92** (`f16`, `buccaneer`) | ESC-50 `airplane` |
| 8 | **Drone / UAV** | stationary-periodic | DREGON, DroneAudioDataset | AudioSet `Unmanned aerial vehicle` |
| 9 | **Emergency siren** | non-stationary tonal | UrbanSound8K (`siren`), ESC-50 | AudioSet |
| 10 | **Wind** | stationary | DEMAND, ESC-50 (`wind`) | Our range ambience |
| 11 | **Rain / weather** | stationary | ESC-50, FSD50K | — |
| 12 | **Street traffic** | non-stationary | **TAU Urban Acoustic Scenes**, UrbanSound8K | DEMAND `TCAR`,`SCAFE` |
| 13 | **Metro / subway** | stationary | **TAU Urban** (`metro`, `metro_station`) | DEMAND `TMETRO` |
| 14 | **Train / tram** | stationary | **TAU Urban** (`tram`, `train`) | ESC-50 `train` |
| 15 | **Bus** | stationary | TAU Urban (`bus`) | DEMAND `TBUS` |
| 16 | **Human babble / crowd** | non-stationary | **NOISEX-92** (`babble`), MUSAN speech | DEMAND `SPSQUARE`,`SCAFE` |
| 17 | **HVAC / machinery hum** | stationary | DEMAND (`DKITCHEN`,`OOFFICE`), MUSAN | NOISEX-92 `factory1/2` |
| 18 | **Radio channel noise** | stationary | NOISEX-92 (`hfchannel`), `pink`, `white` | — |
| 19 | **Impact / percussive** | impulsive | FreesoundOneShotPercussive, Nonspeech7k | ESC-50 |
| 20 | **Vocal non-speech** | impulsive | VocalSound | Nonspeech7k |

---

## 2. The corpora — what to download

### Defence / military — the ones that matter most

| Corpus | Size | Contains | Licence |
|---|---|---|---|
| **NOISEX-92** | 15 noises, 235 s each @ 19.98 kHz | **tank (leopard, m109), F-16 cockpit, machine gun, factory, babble, HF radio, pink/white** | research use |
| **AudioSet** | ~2.1 M × 10 s clips, 632 classes | `Machine gun`, `Cannon`, `Explosion`, `Artillery fire`, `Military vehicle`, `Helicopter`, `Fusillade` | CC BY (labels); audio via YouTube |
| **FSD50K** | 51,197 clips, 200 classes | gunshot, explosion, siren, engine | CC BY / CC0 mix |

NOISEX-92 is small but it is the only corpus with **actual tank and military
aircraft** recordings. AudioSet is where "millions" comes from — but the audio
must be fetched from YouTube, so budget time and expect gaps.

### General noise

| Corpus | Size | Notes | Licence |
|---|---|---|---|
| **MUSAN** | ~109 h | noise + speech + music, purpose-built for augmentation | CC BY 4.0 |
| **DEMAND** | 18 environments × 16 ch | real multichannel field recordings | CC BY-SA 3.0 |
| **UrbanSound8K** | 8,732 clips ≤ 4 s, 10 classes | siren, engine idling, jackhammer, drilling | CC BY-NC 3.0 |
| **ESC-50** | 2,000 clips × 5 s, 50 classes | helicopter, chainsaw, siren, train, wind, rain | CC BY-NC 3.0 |
| **TAU Urban Acoustic Scenes** | 10 scenes, multi-city | metro, metro_station, tram, bus, street_traffic, park | CC BY-NC |

### Impulsive (the IS³ list, from `workflow.md` §5.3)

ESC-50 · ReaLISED · VocalSound · FreesoundOneShotPercussive · Nonspeech7k

### Stationary (the IS³ list)

DCASE2018 Task 1 · CochlScene · Arte · CAS2023 · LITIS Rouen

---

## 3. Clean speech — `order.md` calls this **the largest open item**

Stage 0d is marked **BLOCKED, undecided** and it blocks Stage 4 entirely.
Recommended decision:

| Corpus | Size | Why |
|---|---|---|
| **LibriSpeech** | ~1000 h EN | bulk volume, CC BY 4.0 |
| **VCTK** | 109 speakers, ~44 h | speaker variety, 48 kHz |
| **EARS** | 100 speakers, anechoic, 48 kHz | high-fidelity targets |
| **Common Voice Hindi** | growing, CC0 | the PS implies Hindi |
| **IndicTTS / SPRING-INX** | multi Indian language | evaluators' own languages |
| **Lombard GRID** | 54 speakers, neutral **+ Lombard** pairs | ⚠️ see below |

### ⚠️ Lombard speech — the gap nobody has closed

People shouting in gunfire do not speak like people reading sentences. Under
noise, speakers raise pitch, raise level, shift spectral tilt. Systems trained
on neutral speech lose roughly **5 dB** on Lombard speech, and the gap survives
level normalisation.

**The word "Lombard" appears zero times in the current `docs/01-system/` files,
and Lombard speech is the entire use case.** Target ≥ 20 % Lombard content.

---

## 4. Room impulse responses

| Source | Contents |
|---|---|
| **Ours** | range IR (balloon / sweep) — the actual acoustic space |
| **OpenSLR SLR28** | large real + simulated RIR set |
| **MIT IR Survey** | 271 real-world IRs |
| **pyroomacoustics** | unlimited simulated, image-source method |

`workflow.md` §5.4 item 6 requires a **wide** spread — near-anechoic through
hard-walled, reported separately. Deep ANC used one room; that is a gap we
exploit.

## 5. HRTF — head shadow

CIPIC HRTF (45 subjects) or MIT KEMAR. Required by §5.4 item 7: HRTF-based head
shadow, **not** Tan et al.'s flat −10…0 dB scalar.

---

## 6. Target dataset size

| Split | Hours | Pairs @ 4 s | Note |
|---|---|---|---|
| Train | 500 – 1000 h | ~450k – 900k | mixed on the fly, not stored |
| Validation | 20 h | ~18k | fixed seed |
| Test | 20 h | ~18k | fixed seed, never touched during training |
| **Real holdout** | 44 events | — | **never used for training or tuning** |

Mixing on the fly (not pre-rendering) is what makes "millions" reachable — with
~1000 h of speech and ~150 h of noise, the number of distinct
speech × noise × SNR × RIR × α combinations is effectively unbounded.

---

## 7. Licence discipline

DRDO is a defence sponsor. **Track the licence of every corpus.** CC BY-NC
(UrbanSound8K, ESC-50, TAU) is non-commercial — fine for research and for the
competition, but flag it, because a deployed product cannot ship a model whose
training data forbids commercial use. LibriSpeech (CC BY 4.0), MUSAN (CC BY
4.0) and FSD50K are the safe core.
