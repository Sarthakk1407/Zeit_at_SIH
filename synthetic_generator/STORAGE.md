# How much is downloaded, how much is generated

Sizes are approximate — treat them as planning numbers, not guarantees.

---

## Part 1 — DOWNLOADED (real audio, takes disk)

### Core set — enough to start training

| Corpus | Hours | GB |
|---|---|---|
| LibriSpeech train-clean-100 | 100 | 6.0 |
| LibriSpeech dev+test-clean | 11 | 0.7 |
| MUSAN | 109 | 11.0 |
| RIRs and Noises (SLR28) | — | 4.0 |
| ESC-50 | 2.8 | 0.6 |
| NOISEX-92 | ~1 | 0.05 |
| MAD (military) | 12 | ~1.5 |
| Zenodo gunshots | ~2 | 1.6 |
| Lombard GRID (audio) | ~5 | ~2.0 |
| **CORE TOTAL** | **~243 h** | **~28 GB** |

### Full set — everything worth having

| Corpus | Hours | GB |
|---|---|---|
| *core, above* | 243 | 28 |
| LibriSpeech train-clean-360 | 360 | 23 |
| VCTK | 44 | 11 |
| DEMAND | ~27 | 6 |
| UrbanSound8K | 9 | 6 |
| TAU Urban Acoustic Scenes | ~64 | ~30 |
| FSD50K | ~108 | ~30 |
| Cadre gunshots | ~3 | ~5 |
| DREGON (8-channel) | ~2 | ~10 |
| DroneAudioSet | 23.5 | ~15 |
| **FULL TOTAL** | **~880 h** | **~165 GB** |
| SPRING-INX (Hindi, optional) | 2,000 | ~200 |
| **WITH SPRING-INX** | **~2,900 h** | **~365 GB** |

---

## Part 2 — SYNTHETIC (generated, takes almost no disk)

**This is the part people get wrong. Synthetic training data is mixed on the
fly, in the dataloader, and thrown away after each batch. It is never written
to disk.**

### How many distinct mixtures are reachable

With the core set:

| Factor | Count |
|---|---|
| Speech segments (1,000 h ÷ 4 s) | 900,000 |
| Noise segments (150 h ÷ 4 s) | 135,000 |
| SNR levels (−15…+20 dB, 5 dB steps) | 8 |
| RIRs | 50 |
| α-stable values | 5 |

```
900,000 × 135,000 × 8 × 50 × 5  ≈  2.4 × 10^14 distinct mixtures
```

**243 trillion.** "Millions" is not the ceiling — it is not even close to it.
The limit is training compute, not storage, exactly as `workflow.md` §5.1 says.

### If you did store it (don't)

| Stored | Hours | GB |
|---|---|---|
| 1,000,000 clips × 4 s | 1,111 | ~128 |
| 500 h of mixtures | 500 | ~58 |
| **Fixed val + test only ← do this** | **40** | **~4.6** |

At 16 kHz / 16-bit mono, one hour ≈ 115 MB.

**Store only the fixed validation and test sets** — those must be identical
across every experiment or the comparisons mean nothing. Everything else is
regenerated from a seed.

---

## Part 3 — SSD sizing

| Item | GB |
|---|---|
| Downloaded corpora (full, no SPRING-INX) | 165 |
| Fixed val/test mixtures | 5 |
| Our real reference (`REFERENCE_REAL`, `DATA`) | 1 |
| Model checkpoints (~20 × 100 MB) | 2 |
| Working space, unpacked archives, scratch | 80 |
| **TOTAL** | **~253 GB** |

| SSD | Verdict |
|---|---|
| 256 GB | core set only, tight |
| **500 GB** | **full set minus SPRING-INX — comfortable** |
| 1 TB | everything including SPRING-INX, no thinking required |
| 2 TB | room for a second range trip at 96 kHz |

Archives roughly double while unpacking — keep ~80 GB of headroom.

---

## The one-line answer

**Download ~28 GB to start, ~165 GB for everything.
Generate 10^14 mixtures and store ~5 GB of them.**

---

# Part 4 — Class by class: kya download, kya banana

Research ke baad picture badal gayi. Pehle laga tha bahut kuch synthesize karna
padega — par MAD, Cadre aur Zenodo ke baad **zyadatar classes ke liye asli
recordings mil rahi hain.**

| # | Class | Real milta hai? | Source | Synthesize karna hai? |
|---|---|---|---|---|
| 1 | Gunshot / muzzle blast | ✅ ~12,000 recordings | Cadre + Zenodo + MAD | **Haan — variety aur controlled sweeps ke liye** |
| 2 | Artillery / shelling | ✅ 1,173 clips | MAD | nahi |
| 3 | Machine gun | ✅ | NOISEX-92 + AudioSet | nahi |
| 4 | Tank / tracked vehicle | ✅ | NOISEX-92 (leopard, m109) | nahi |
| 5 | Armored / wheeled vehicle | ✅ 1,123 clips | MAD + NOISEX-92 | nahi |
| 6 | Helicopter | ✅ 1,009 clips | MAD + ESC-50 | nahi |
| 7 | Fighter jet | ✅ 985 clips | MAD + NOISEX-92 (f16) | nahi |
| 8 | Drone / UAV | ✅ 23.5 h | DroneAudioSet + DREGON | nahi |
| 9 | Siren | ✅ | UrbanSound8K + ESC-50 | nahi |
| 10 | Wind | ✅ | DEMAND + ESC-50 | nahi |
| 11 | Traffic / metro / train / bus | ✅ | TAU Urban + DEMAND | nahi |
| 12 | Babble / crowd | ✅ | NOISEX-92 + MUSAN | nahi |
| 13 | HVAC / machinery | ✅ | DEMAND + NOISEX-92 | nahi |
| 14 | Radio channel noise | ✅ | NOISEX-92 (hfchannel) | nahi |
| 15 | Footsteps | ✅ 921 clips | MAD | nahi |

**Ek line:** 15 mein se 14 classes ke liye asli data mil raha hai. Sirf gunshot
ke liye synthesis karna hai — aur wo bhi replacement ke liye nahi, **coverage ke
liye**.

---

## Toh synthesize kya karna hai — sirf do cheezein

### (A) Synthetic gunshots — Phase 3

**Kyun, jab 12,000 real gunshots mil rahe hain:**

Downloaded gunshots fixed hain. Jo record hua wahi mila. Hum **parameter sweep**
nahi kar sakte:

- yahi shot 5 m, 10 m, 25 m, 50 m pe kaisa hoga
- yahi shot 0°, 45°, 90°, 180° pe kaisa hoga
- yahi shot anechoic room mein, aur hard-walled room mein
- yahi shot mic clipping ke saath, aur bina clipping ke

Synthetic generator **wahi ek blast leke uske 500 variants** bana deta hai, har
ek ka distance/angle/room/clipping label ke saath. Real data se ye nahi ho sakta.

| | |
|---|---|
| Kaise banega | Friedlander blast model + range IR convolution + distance/propagation + α-stable structured bursts |
| Validate kaise | `analyze.py` — **wahi engine** — aur `stats_impulse.json` ke ±1 sd ke andar aana chahiye |
| Kitne | ~10,000–50,000 variants |
| Disk | ~5–10 GB agar store karo (ya on-the-fly) |

### (B) Training mixtures — Phase 4

```
noisy = clean_speech + g · (noise ⊛ RIR)
```

| | |
|---|---|
| Kitne possible | **2.4 × 10^14** |
| Kahan banenge | dataloader mein, har batch pe fresh |
| Disk | **~0** — sirf fixed val/test store hoga (~5 GB) |

---

## Final numbers

| | Size |
|---|---|
| **DOWNLOAD — core (shuru karne ke liye)** | **~28 GB** |
| **DOWNLOAD — full (sab kuch)** | **~165 GB** |
| SYNTHESIZE — gunshot variants (stored) | ~5–10 GB |
| SYNTHESIZE — training mixtures (stored) | ~0 |
| Fixed val/test (stored) | ~5 GB |
| Hamara real reference | ~1 GB |
| Working space / unpacking | ~80 GB |
| **SSD pe kul** | **~260 GB** |

683 GB partition hai — aaram se aa jaayega, aur doosre range trip ke liye bhi
jagah bachegi.
