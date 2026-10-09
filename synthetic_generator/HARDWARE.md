# Hardware — every part, every port, every wire

Companion to [`../docs/01-system/architecture.md`](../docs/01-system/architecture.md),
which is authoritative for *what the system does*. This document is
authoritative for *what is bought, how it connects and how the headset is
built*. Step IDs (A1–A11 Lane A, R1–R5 radio receive, B1–B11 Lane B, T1–T8
training) come from the architecture; hardware IDs (H1–H24) are defined here.

Final design, locked 19 Sep 2026. Prices are **estimates** (September 2026,
including GST) unless marked; confirm with a quotation before ordering.

---

## 1. Summary

| | |
|---|---|
| Headset | 3M PELTOR Optime III earmuff, modified: 6 microphones, 2 speakers |
| Lane A processor | Analog Devices EVAL-ADAU1787Z (one board, both ears) + STM32 Nucleo-H743ZI2 |
| Lane B processor | NVIDIA Jetson Orin Nano Super Developer Kit |
| Audio interface | Behringer UMC404HD |
| Communication unit | Licence-free PMR446 walkie-talkie pair (demo stand-in for a tactical radio) |
| Must-buy total | **≈ ₹1,11,550 – ₹1,37,250** (ESTIMATE; Jetson and earmuff prices are the swing) |
| Budget requested | ₹1,25,000 |

```
                      ┌────────────── HEADSET (H1 group) ──────────────┐
                      │ Mic 1 boom · Mic 2L · Mic 2R · Mic 3L · Mic 3R │── 8-core cable (GX16-8) ──┐
                      │ Speaker L · Speaker R                          │── 4-core cable (GX16-4) ──┼──┐
                      └────────────────────────────────────────────────┘                           │  │
                      Mic 4 throat ── 3.5 mm ──────────────────────────────────────────────────────┤  │
                      PTT button  ── 3.5 mm ──► STM32 input ───────────────────────┐               │  │
                                                                                    │               ▼  │
                              ┌──────────────── PREAMP BOARD (H6) ────────────────┐ │               │
                              │ bias + gain for 6 mics · Mic 2R/2L split · L/R sw │◄┼───────────────┘  │
                              └───┬─────────────┬───────────────────┬─────────────┘ │                  │
                 Mic 1, ref, Mic 4│             │ Mic 2L,2R,3L,3R    │                │                  │
                                  ▼             ▼                    │                │                  │
                 UMC404HD (H14) in 1–3      ADAU1787 (H9) ADC 1–4   │                │                  │
                 in 4 ◄── radio RX (H19)        │ DAC L/R ──────────┼──► H13 amp ──────────────────────►│ speakers
                    │ USB                       │ I²C / TDM (H12a/b) │     ▲  ▲                           
                    ▼                           ▼                    │     │  └ volume (I²C from STM32)   
                 JETSON (H15) ── UART ──► STM32 (H11)               │     │                               
                    │  out 1 ──► H19 ──► radio mic in               │     └── UMC out 2 (radio voice)    
                    │  (UART: PTT state)     STM32 GPIO ──► H19 opto ──► radio PTT
```

---

## 2. Bill of materials

### 2.1 Headset and sensors

| ID | Part | Key spec | Qty | Est. ₹ | Used by | Buy |
|---|---|---|---|---|---|---|
| **H1** | 3M PELTOR Optime III H540A earmuff (alt. X5A) | Passive, SNR 35 dB (X5A: 37 dB); double casing; deep cups — VERIFIED ratings; price not found online | 1 | 2,000–5,000 | Protection (§3.4 arch.) | Must |
| H1-P | Basic earmuff for practice | Any cheap passive earmuff | 1 | ~500 | Drilling / fitting practice | Must |
| H1-A | 40 mm headphone drivers, 32 Ω | Loose pair or salvaged; 2 fitted + 2 spare | 4 | 400–1,000 | Speakers L / R (A10–A11, R5) | Must |
| H1-B | Gooseneck electret boom mic | 2-wire electret, bias 2–5 V | 1 | 300–800 | **Mic 1** (B1, B7 input 0) | Must |
| H1-C | Acrylic / stiff plastic sheet | For speaker mounting rings | 1 | 150–300 | Speaker mounts | Must |
| H1-D | Acoustic foam sheet | Replaces the foam removed from the cups | 1 | 200–400 | Cup damping and seal | Must |
| H1-E | Boom clamp / bracket | Holds the gooseneck on the left cup | 1 | 100–300 | Mic 1 | Must |
| H1-F | Acoustic mesh / fine cloth | Covers the inside mics against sweat and fingers | 1 | 50–150 | Mic 3L, 3R | Must |
| H1-G | Push-to-talk button + short cable (3.5 mm) | Momentary switch; wired to the **STM32** | 1 | 100–300 | B11 (PTT) | Must |
| **H2** | Infineon IM73A135 analog MEMS breakout | AOP 135 dB SPL, SNR 73 dB, IP57, **VDD 2.3–3.0 V** — VERIFIED (datasheet) | 2 | 1,600–5,000 | **Mic 2L, Mic 2R** (A1–A6, B1, B2, B7 input 1) | Must (Gate 3) |
| **H3** | SparkFun analog MEMS breakout ICS-40180 (BOB-18011) | 1.5–3.6 V, SNR 65 dBA, on-board op-amp output (½ VDD bias, 600 Ω) — VERIFIED; some retailers list it discontinued, check stock | 3 | 750–1,500 | **Mic 3L, Mic 3R** + spare (A7–A9) | Must |
| **H4** | Throat microphone (laryngophone) with 3.5 mm plug | Electret contact mic; avoid walkie-talkie plug + PTT-box versions | 1 | 1,500–3,000 | **Mic 4** (B1, B7 input 2, B9) | Must |
| **H5** | Foam windshields | Small mic foams | 3 | 300–700 | Mic 2L, Mic 2R, Mic 1 | Must |
| **H6** | Microphone preamp / bias board | See §4 | 1 | 3,000–3,500 | All mics | Must (build) |
| **H7** | Foam earplugs | Rated disposable plugs | 1 box | ~300 | Double protection | Must |
| **H8** | Cables, connectors, sealing | 8-core + 4-core shielded cable (~2 m each), GX16 8-pin and 4-pin pairs, rubber grommets, heat-shrink, neutral-cure silicone sealant, cable ties | 1 set | 1,300–2,200 | All headset connections | Must |
| | **Subtotal** | | | **12,550 – 24,950** | | |

### 2.2 Lane A electronics

| ID | Part | Key spec | Qty | Est. ₹ | Used by | Buy |
|---|---|---|---|---|---|---|
| **H9** | Analog Devices EVAL-ADAU1787Z | 4 ADC, 2 DAC, FastDSP up to 768 kHz, 28-bit SigmaDSP, serial ports, USB or 3.8–5 V power — VERIFIED | 1 | ~32,000 | A1–A11, both ears | Must (Gates 1, 2) |
| H10 | USBi programmer EVAL-ADUSB2EBZ | SigmaStudio interface | 0–1 | 0 / ~9,000 | Programming H9 | Only if UG-1532 says the board lacks USB |
| **H11** | STM32 Nucleo-H743ZI2 | Cortex-M7; UART, I²C, SAI (I²S/TDM), ADC; user button | 1 | ~3,500 | Boot-loads H9; modes; A8; ANC button; **PTT**; H13 volume | Must |
| **H12a** | PCA9306 I²C level shifter | 1.8 V ↔ 3.3 V, purpose-built for I²C (TXS0108-type shifters are unreliable on I²C — TI forum, VERIFIED) | 1 | 100–200 | H11 ↔ H9 control | Must unless UG-1532 shows on-board shifting |
| **H12b** | 4-channel push-pull level shifter (TXB0104-type) | 1.8 V → 3.3 V for BCLK, FSYNC, SDATA | 1 | 100–200 | H9 → H11 mic data (A8) | Phase 2 (adaptive ANC) only |
| **H13** | TPA6130A2 stereo headphone amplifier breakout | 2.5–5.5 V supply (VERIFIED), **run at 3.3 V** so its I²C shares the STM32's 3.3 V bus; drives 32 Ω; I²C volume. Breakout availability in India: check | 1 | 1,000–2,000 | Sums ADAU output + radio voice; drives speakers | Must |
| | **Subtotal** | | | **36,700 – 37,900** | | |

### 2.3 Lane B electronics

| ID | Part | Key spec | Qty | Est. ₹ | Used by | Buy |
|---|---|---|---|---|---|---|
| **H14** | Behringer UMC404HD | 4 combo inputs (TRS line used), 24-bit up to 192 kHz, line outputs, USB class-compliant — Linux support VERIFIED; on Jetson UNVERIFIED | 1 | ~15,000 | B1, B11, R1, R5 | Must |
| **H15** | NVIDIA Jetson Orin Nano Super Developer Kit | 6-core Cortex-A78AE, Ampere GPU 1024 CUDA / 32 tensor cores, 8 GB LPDDR5, 67 TOPS, 7–25 W, 40-pin header, DisplayPort — VERIFIED | 1 | 37,200–45,200 (Indian listings: IndiaMART ₹37,200, CrazyPi ₹45,200) | B1–B11, R1–R5, modes | Must (Gate 6) |
| **H16** | 128 GB microSD, A2 / U3 / V30 (SanDisk Extreme / Samsung PRO Plus class) | Boot + storage; the kit ships without | 1 | ~1,500 | H15 | Must |
| H17 | Hum fix | Grounding first; then ground-loop isolators on analog lines; last, a **high-speed** USB isolator (ADuM3165/4165 class). **Not** ADuM3160 — full-speed only, UMC404HD is high-speed | 0–1 | 0 / check | B1 | Only if hum appears |
| | **Subtotal** | | | **53,700 – 61,700** | | |

### 2.4 Communication unit

| ID | Part | Key spec | Qty | Est. ₹ | Used by | Buy |
|---|---|---|---|---|---|---|
| **H18** | PMR446 walkie-talkie pair | 446–446.2 MHz, ≤ 0.5 W ERP, **WPC Equipment Type Approval**, **K-type (3.5 mm + 2.5 mm) accessory jack** — licence rule VERIFIED | 1 pair | 2,500–6,000 | B11 (transmit), R1 (receive) | Must (Gate 5) |
| **H19** | Radio interface parts | 2 × 1:1 600 Ω audio isolation transformers, PC817 optocoupler, resistors / capacitors, a K-type earpiece to cut for plugs, perfboard + box | 1 set | 600–1,200 | B11, R1 | Must |
| | **Subtotal** | | | **3,100 – 7,200** | | |

### 2.5 Power, test and optional

| ID | Part | Key spec | Qty | Est. ₹ | Used by | Buy |
|---|---|---|---|---|---|---|
| **H20** | Clean 5 V supply / power bank | Separate from the Jetson supply | 1 | ~1,000 | H6, H9, H11, H13 | Must |
| H21 | 100 W USB-PD power bank + 19 V trigger cable | Jetson power in the field | 0–1 | 0 / ~5,000 | H15 | Only for an outdoor demo |
| **H22** | Mannequin head + small in-ear measurement mic | Headset must fit | 1 | ~2,000 | Calibration (arch. §4.5), all Lane A measurements | Must |
| **H23** | Sound level meter (e.g. UNI-T UT353BT) | — | 1 | ~2,500 | Calibration; safe test levels | Must |
| H24 | Sound level calibrator 94 dB / 1 kHz | — | 0–1 | 0 / 6,000–12,000 | Absolute dB SPL | Optional |
| | **Subtotal (must)** | | | **5,500** | | |

### 2.6 Tools (only if the lab does not have them)

Mini drill with a **step bit** (clean holes through the double casing), a
temperature-controlled soldering iron + flux, multimeter, hot-glue gun, craft
knife, wire strippers. ≈ ₹2,600–4,800.

### 2.7 Totals

| Group | Est. ₹ |
|---|---|
| Headset and sensors | 12,550 – 24,950 |
| Lane A electronics | 36,700 – 37,900 |
| Lane B electronics | 53,700 – 61,700 |
| Communication unit | 3,100 – 7,200 |
| Power and test | 5,500 |
| **Must-buy total** | **1,11,550 – 1,37,250** |
| Conditional (H10, H17, H21) | up to ~14,000 + isolator if needed |
| Optional (H24) | 6,000 – 12,000 |

The middle of the range sits near the ₹1,25,000 request. Gates 1, 4 and 6 (§10)
fix the exact figure.

---

## 3. Microphone map

| Mic | Position | Part | Preamp input | Preamp output(s) | Destination |
|---|---|---|---|---|---|
| Mic 1 | Boom, left | H1-B | IN1 | OUT1 | UMC in 1 → AI input 0 |
| Mic 2L | Outside left cup | H2 | IN2 | OUT5, and OUT2 when switch = L | ADAU ADC 1 (+ UMC in 2 for left-handed use) |
| Mic 2R | Outside right cup | H2 | IN3 | OUT6, and OUT2 when switch = R | ADAU ADC 2 + UMC in 2 → AI input 1 |
| Mic 3L | Inside left cup | H3 | IN4 | OUT7 | ADAU ADC 3 |
| Mic 3R | Inside right cup | H3 | IN5 | OUT8 | ADAU ADC 4 |
| Mic 4 | Throat | H4 | IN6 | OUT3 | UMC in 3 → AI input 2 |

---

## 4. Preamp / bias board (H6)

| Function | Design |
|---|---|
| Inputs | 6: IN1 boom (electret), IN2–IN5 MEMS (3-wire), IN6 throat (electret) |
| Bias | Electret: 2–5 V through a resistor on IN1 and IN6. MEMS: shared **2.8 V LDO** on the 8-core cable — inside both the IM73A135 range (2.3–3.0 V) and the ICS-40180 range (1.5–3.6 V); **never 3.3 V**, which exceeds the IM73A135's maximum |
| Gain | Per channel, OPA1678 (4.5–36 V supply, output within 0.8 V of the rails — VERIFIED), on 5 V with a 2.5 V mid-rail bias: ≈ 1.2 Vrms maximum output. Set so a shout reaches ≈ −12 dBFS. The ICS-40180 boards already have an output op-amp, so IN4 / IN5 only need AC coupling and a buffer |
| Outputs | 7 buffered line outputs: OUT1 Mic 1 · OUT2 reference (switched) · OUT3 Mic 4 → UMC; OUT5 Mic 2L · OUT6 Mic 2R · OUT7 Mic 3L · OUT8 Mic 3R → ADAU (OUT4 unused) |
| ADAU side (OUT5–OUT8) | **AC-coupled** (the op-amps sit at 2.5 V; the ADAU runs from 1.8 V), 1 kΩ series resistor on each, and gain set so the loudest sound stays below the ADAU ADC full scale — that full-scale voltage is read from the ADAU1787 datasheet / UG-1532 before the gain resistors are chosen (UNVERIFIED) |
| UMC side (OUT1–OUT3) | TRS line inputs, **phantom power OFF** (48 V would damage the MEMS and op-amps) |
| Handedness switch | SPDT selecting Mic 2R (right-handed, default) or Mic 2L (left-handed) for OUT2 |
| Supply | Clean 5 V (H20); star ground on this board |
| Why buffered copies | Each board sees its own driver; unplugging one never disturbs the other |

---

## 5. Board port assignments

### 5.1 EVAL-ADAU1787Z (H9)

| Port | Signal | Notes |
|---|---|---|
| ADC 1 | Mic 2L (H6 OUT5) | Left feed-forward ANC + hear-through |
| ADC 2 | Mic 2R (H6 OUT6) | Right feed-forward ANC + hear-through |
| ADC 3 | Mic 3L (H6 OUT7) | Left ANC error |
| ADC 4 | Mic 3R (H6 OUT8) | Right ANC error |
| DAC L / R | → H13 inputs (through summing resistors) | Limited to the 79 dB share (arch. §4.4) |
| I²C | ← H11 via H12a (PCA9306) | Control, program load at power-on |
| Serial port (I²S/TDM) | → H11 SAI via H12b (TXB0104) | Adaptive ANC phase (A8) only |
| USB | Laptop with SigmaStudio | Development; power |

### 5.2 Behringer UMC404HD (H14)

| Port | Signal | Notes |
|---|---|---|
| In 1 (TRS) | Mic 1 (H6 OUT1) | AI input 0 — gain set once and logged |
| In 2 (TRS) | Reference (H6 OUT2) | AI input 1 |
| In 3 (TRS) | Mic 4 (H6 OUT3) | AI input 2 |
| In 4 (TRS) | Radio receive (H19) in the field · mannequin ear mic (H22) in the lab | R1 / measurements — swap the cable |
| Out 1 | → H19 → radio mic input | Outgoing cleaned voice (B11) |
| Out 2 | → H13 inputs (through summing resistors) | Incoming cleaned radio voice (R5) |
| 48 V phantom | **OFF** | Mics are powered by H6 |
| USB | → Jetson | Through H17 only if hum |

### 5.3 Jetson Orin Nano Super (H15)

| Port | Use | Notes |
|---|---|---|
| USB | UMC404HD | Audio class device |
| 40-pin UART | STM32 link: modes down, status up | 3.3 V; assign TX/RX pins from NVIDIA's header pinout before wiring |
| 40-pin GPIO | **Not used for PTT.** Header GPIOs go through TXB0108 shifters (≈ 2–3 mA, ≈ 4 kΩ output — VERIFIED); they cannot drive the optocoupler | PTT is on the STM32 |
| DisplayPort | Monitor for setup and the live display | The dev kit has DisplayPort, not HDMI |
| microSD / M.2 | H16 | — |
| DC barrel | 19 V adapter (included); H21 in the field | — |

### 5.4 STM32 Nucleo-H743ZI2 (H11)

| Port | Use |
|---|---|
| UART | Jetson link (protocol in architecture §8) |
| I²C | ADAU1787 (via H12a) and TPA6130A2 volume (3.3 V side) |
| SAI (I²S/TDM) | Mic data from the ADAU for A8 (via H12b) |
| GPIO in | PTT button H1-G (internal pull-up, press = ground) |
| GPIO out | Radio PTT: drives the PC817 LED through ≈ 330 Ω (≈ 6 mA at 3.3 V) |
| 3V3 pin | Supplies the TPA6130A2 (H13) |
| User button | ANC on / PASSIVE toggle |
| USB | Power (H20) and flashing |

### 5.5 TPA6130A2 amplifier (H13)

| Port | Use |
|---|---|
| Input L | ADAU DAC L + UMC out 2 (left), each through its own summing resistor |
| Input R | ADAU DAC R + UMC out 2 (right), each through its own summing resistor |
| Output L / R | Speakers via the 4-core cable |
| I²C | Volume, set once at calibration and locked by the STM32 |

### 5.6 Radio interface (H19)

| Path | Parts | Notes |
|---|---|---|
| UMC out 1 → radio mic input | Resistor divider (line → mic level) → transformer 1 → **series DC-blocking capacitor (1–4.7 µF)** | The radio puts electret bias on its mic line and keys PTT when that line is grounded (Kenwood-type K-plug — VERIFIED). A transformer winding alone would short the bias and could hold PTT on; the capacitor prevents it |
| STM32 GPIO → radio PTT | PC817 optocoupler (+ the resistor the radio's pinout specifies) | Isolated; check which K-plug contact keys PTT on the chosen radio |
| Radio speaker → UMC in 4 | Resistor divider (speaker → line level) → transformer 2 | Isolated. Both primary ends float — never tie either to ground: many radio speaker outputs are bridged (BTL), and grounding one side shorts the amplifier |

---

## 6. Headset cables and connector pinouts

**Microphone cable — 8-core shielded, GX16 8-pin**

| Pin | Signal |
|---|---|
| 1 | MEMS supply (VDD) |
| 2 | Microphone ground |
| 3 | Mic 1 (electret signal + bias) |
| 4 | Mic 2L |
| 5 | Mic 2R |
| 6 | Mic 3L |
| 7 | Mic 3R |
| 8 | Shield (connected at the preamp end only) |

**Speaker cable — 4-core shielded, GX16 4-pin**

| Pin | Signal |
|---|---|
| 1 | Left + |
| 2 | Left − |
| 3 | Right + |
| 4 | Right − |

Microphones and speakers travel in **separate cables** so speaker current
cannot couple into the microphones. Mic 4 (throat) and the PTT button use their
own 3.5 mm leads. Label every wire at both ends.

---

## 7. Power and grounding

| Board | Supply | Why |
|---|---|---|
| Jetson (H15) | Its own 19 V adapter; H21 in the field | Keeps its switching noise away from the microphones |
| UMC404HD (H14) | USB bus power from the Jetson | Phantom off keeps current low |
| H6, H9, H11 | Separate clean 5 V (H20); MEMS on a 2.8 V LDO on H6 | Microphone noise floor depends on a quiet supply |
| H13 | 3.3 V from the STM32 Nucleo's 3V3 pin | Shares the STM32's I²C levels; 32 Ω drive at 82 dB needs far under 1 mW |
| Radio (H18) | Its own batteries | Isolated by H19 |

Star ground at the preamp board, short shielded leads, shields grounded at one
end. If hum appears, fix grounding first (H17).

---

## 8. Building the headset

Practise every drilling step on H1-P first.

1. **Open the cups.** Remove the ear cushions and inner foam; note how they seal.
2. **Speakers (H1-A, H1-C).** Cut a ring per cup to hold a 40 mm driver facing
   the ear. Seal the ring into the cup with silicone. The cup must stay airtight —
   that is the passive protection.
3. **Inside mics (H3, H1-F).** One per cup, between speaker and ear, as close to
   the ear canal as possible, facing the ear, on a small foam pad; mesh over it.
   Do not touch the speaker cone.
4. **Outside mics (H2, H5).** Drill one small hole through both casing layers of
   each cup (step bit, slow, masking tape over the spot). Mount the board facing
   out, slightly recessed; seal both layers with silicone; fit the windshield.
   **Mic 2R on the right cup** (away from the boom), **Mic 2L on the left**.
5. **Boom (H1-B, H1-E, H5).** Clamp the gooseneck to the **left** cup; tip
   2–5 cm from the corner of the mouth; windshield on.
6. **Wiring (H8).** One grommeted exit per cup. Route left-cup wires along the
   headband to the right cup. 8-core for mics, 4-core for speakers, GX16 at the
   ends, pinout per §6. Strain relief at every exit.
7. **Throat mic (H4)** and **PTT button (H1-G)** on their own leads.
8. **Close up.** New foam (H1-D), cushions back on; check the seal on a head.

### Tests after building

| Test | How | Pass |
|---|---|---|
| Wiring | Multimeter, end to end, and between adjacent pins | All continuous, no shorts |
| Every mic alive | Record each channel through the UMC / ADAU while tapping near it | Each mic on its own channel |
| Speakers | Slow sweep into each ear | Clean, no rattle, left / right separate |
| Seal | Loud noise outside; record outside vs inside mic with the system off | Inside clearly quieter, consistent with the rating |
| **Voice leak** | Speak in a quiet room; compare Mic 1 and the reference mic | Reference **≥ 25 dB quieter** than Mic 1 — otherwise move Mic 2R further back |
| Throat mic | Speak with loud noise playing | Voice clear, background low |

Then calibration (architecture §4.5).

---

## 9. Hardware ↔ neural network compatibility

| Link | Hardware | Model / training | Status |
|---|---|---|---|
| Inputs and order | UMC in 1 / 2 / 3 = Mic 1 / reference / Mic 4 | Inputs 0 / 1 / 2 | Locked; label the cables |
| Sample rate | 48 kHz capture | 16 kHz model | Resampler MEASURED |
| Frame / hop | 768 samples at 48 kHz | 256 at 16 kHz | Parity MEASURED |
| Reference overload | IM73A135 clips above 135 dB | Clipping augmentation on input 1 | Built |
| Gains | H6 per-channel gain | Random per-channel gain | Input 1 built; input 2 to add |
| Voice in the reference | Head between boom and Mic 2R | Delayed, shadowed leak −45 … −25 dB | Built; confirm with the voice-leak test |
| Throat channel | H4 | Real pairs + simulated + 30 % dropout | To implement |
| Handedness | Switch on H6 | Model sees "outside mic away from the mouth" either way | No retraining |
| TensorRT | H15 | ONNX GRU nodes must convert | UNVERIFIED; fallback ONNX Runtime CUDA |

---

## 10. Gates and checklists

**Before ordering**

| # | Check | Parts |
|---|---|---|
| 1 | UG-1532: built-in USB? I/O voltage and level shifting? self-boot? serial-port pins? analog input connectors, mic-bias off? | H9, H10, H11, H12 |
| 2 | ADAU1787 FastDSP capacity for two ANC paths | H9 |
| 3 | IM73A135 sold as a ready breakout in India; otherwise another ≥ 130 dB analog MEMS | H2 |
| 4 | Earmuff price; cup depth fits a 40 mm driver + inside mic | H1 |
| 5 | PMR446 model: WPC ETA, K-type accessory jack, jack pinout | H18, H19 |
| 6 | Written Jetson quotation | H15 |

**After arrival, in order**

1. Record 4 channels from the UMC404HD on the Jetson (`arecord`).
2. Build the 3-input model as a TensorRT engine; confirm GRUs convert; frame time < 16 ms.
3. Build the headset; run the §8 tests, especially the voice-leak test.
4. SigmaStudio: hear-through + limiters first, then fixed ANC (both ears), then adaptation.
5. Calibrate on the mannequin (arch. §4.5).
6. Hum check; H17 only if needed.
