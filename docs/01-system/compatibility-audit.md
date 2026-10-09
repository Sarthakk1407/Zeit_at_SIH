# Compatibility audit — every link, hardware and software

Audit of the locked architecture ([`architecture.md`](architecture.md)) against the
parts list ([`../../synthetic_generator/HARDWARE.md`](../../synthetic_generator/HARDWARE.md))
and the code ([`../../training/`](../../training/)). Done 21 Sep 2026.

Every connection is listed with its status:

| Status | Meaning |
|---|---|
| **VERIFIED** | Checked against a datasheet, manual or manufacturer page |
| **TESTED** | We ran code and it passed |
| **CALCULATED** | Arithmetic from verified numbers; not yet on the bench |
| **UNKNOWN** | Cannot be settled until the part is in hand or a document is read — a gate |

Nothing here is marked VERIFIED or TESTED unless it actually was.

---

## 1. Problems found, and the fix now in the documents

| # | Problem | Why it would fail | Fix applied |
|---|---|---|---|
| 1 | PTT was driven by a **Jetson GPIO** | The Orin Nano header pins go through TXB0108 level shifters: ≈ 2–3 mA, ≈ 4 kΩ output (VERIFIED, NVIDIA forum). A PC817 LED needs ≈ 5–10 mA. PTT would not key | PTT button and optocoupler moved to the **STM32** (≈ 6 mA through 330 Ω). STM32 tells the Jetson `PTT 1/0` over UART |
| 2 | One **8-channel TXS0108** shifter for I²C and TDM | TXS0108-type auto-direction shifters are unreliable on I²C (TI forum, VERIFIED) and marginal on fast clocks | **H12a PCA9306** for I²C; **H12b TXB0104** (push-pull) for BCLK / FSYNC / SDATA, phase 2 only. Both only if the eval board I/O is 1.8 V |
| 3 | MEMS supply said "within datasheet range" — no number | The shared rail was going to be 3.3 V; **IM73A135 maximum is 3.0 V** (VERIFIED) | Shared **2.8 V LDO** on H6: inside IM73A135 (2.3–3.0 V) and ICS-40180 (1.5–3.6 V) |
| 4 | H3 was "a low-noise MEMS breakout" — no part | Nothing to verify | **SparkFun ICS-40180 (BOB-18011)**: 1.5–3.6 V, SNR 65, on-board op-amp output. Stock UNKNOWN (one retailer lists it discontinued) |
| 5 | TPA6130A2 supply voltage not fixed | Its I²C must share the STM32's 3.3 V bus | TPA6130A2 on **3.3 V** from the Nucleo 3V3 pin (part accepts 2.5–5.5 V, VERIFIED) |
| 6 | Radio mic line driven straight by a transformer | The radio feeds electret bias on the mic line and keys PTT when that line is pulled low (Kenwood-type K-plug, VERIFIED). A transformer winding is a DC short: bias lost, radio may sit in transmit | **Series 1–4.7 µF DC-blocking capacitor** after transformer 1 |
| 7 | Radio speaker transformer primary could be grounded | Many radio speaker amps are bridged (BTL); grounding one side shorts them | Primary floats on both ends (HARDWARE §5.6) |
| 8 | Preamp (5 V op-amps at 2.5 V bias) feeding a **1.8 V** ADAU input directly | DC offset and over-voltage on the ADAU pins | ADAU side **AC-coupled**, 1 kΩ series, gain set below ADAU full scale (value UNKNOWN until the datasheet is read) |
| 9 | UART protocol "to be defined" | Jetson and STM32 code could not be written against each other | Defined in `architecture.md` §8: 115200 8N1, ASCII lines (`MODE`, `RADIO`, `PTT`, `CRACK`, `ACK`, `PING/PONG`) |
| 10 | Model is 3-input, **data loader and runner were 2-input** | Training would have produced a 2-input model; the runner would have fed the wrong channels | `data.py` builds the throat channel (simulated) with 30 % dropout; `base.yaml` `mics: 3`; `realtime.py` defaults `--in-ch 1 2 3`, `--rx-ch 4`. Self-test **13/13 pass** |
| 11 | Radio receive audio had no software path to UMC out 2 | Incoming voice would never reach the speakers | `realtime.py` now copies UMC in 4 → out 2 with a gain and a hard ceiling (0.5 FS) |
| 12 | Docs claimed B3 normalisation runs | Neither training nor the runtime applies it | Documented as "to add, in both at once". Today they match (neither has it), so there is no train/device mismatch |

---

## 2. Hardware links

| # | Link | Signal / level | Power source | Status |
|---|---|---|---|---|
| H-1 | Mic 1 (electret boom) → H6 IN1 | mV-level, bias 2–5 V via resistor from H6 | H6 5 V | CALCULATED |
| H-2 | Mic 2L / 2R (IM73A135) → H6 IN2 / IN3 | Analog, 135 dB AOP | 2.8 V LDO; part range 2.3–3.0 V | Supply VERIFIED; breakout availability UNKNOWN |
| H-3 | Mic 3L / 3R (ICS-40180 board) → H6 IN4 / IN5 | Op-amp output, ½ VDD bias, 600 Ω | 2.8 V LDO; part range 1.5–3.6 V | VERIFIED; stock UNKNOWN |
| H-4 | Mic 4 (throat) → H6 IN6 | Assumed electret, 3.5 mm | H6 bias resistor | UNKNOWN (type fixed only when bought) |
| H-5 | Headset → H6 cable | GX16-8: 1 VDD 2.8 V, 2 GND, 3 Mic 1, 4 2L, 5 2R, 6 3L, 7 3R, 8 shield | — | Design; continuity test at build |
| H-6 | H6 OUT1–3 → UMC in 1–3 | Line level, ≤ ≈ 1.2 Vrms (OPA1678 on 5 V, 0.8 V from rails — VERIFIED) | — | CALCULATED; **phantom OFF** |
| H-7 | H6 OUT5–8 → ADAU ADC 1–4 | AC-coupled, 1 kΩ series | — | ADAU full-scale and eval-board input connectors UNKNOWN (UG-1532) |
| H-8 | ADAU DAC L/R → TPA6130A2 (summing resistors) | Line level | TPA on 3.3 V | CALCULATED |
| H-9 | UMC out 2 → TPA6130A2 (summing resistors) | UMC line out, padded by divider; software ceiling 0.5 FS | — | CALCULATED; level set with the mannequin |
| H-10 | TPA6130A2 → speakers 32 Ω | 82 dB SPL needs far below 1 mW | 3.3 V | CALCULATED |
| H-11 | STM32 ↔ ADAU I²C | 3.3 V ↔ 1.8 V via PCA9306 | — | ADAU chip IOVDD 1.8 V VERIFIED; eval-board levels UNKNOWN |
| H-12 | ADAU TDM → STM32 SAI | 1.8 V → 3.3 V via TXB0104 | — | Phase 2; UNKNOWN which header pins carry TDM |
| H-13 | Jetson UART ↔ STM32 UART | 3.3 V both sides; common ground | — | CALCULATED (Jetson header output is weak but STM32 input is high-impedance) |
| H-14 | PTT button → STM32 GPIO | Internal pull-up, press = ground | — | CALCULATED |
| H-15 | STM32 GPIO → PC817 LED | (3.3 − 1.2) V / 330 Ω ≈ 6.4 mA | — | CALCULATED |
| H-16 | PC817 transistor → radio PTT | Pulls the PTT contact to radio ground | Radio | Radio pinout UNKNOWN (Gate) |
| H-17 | UMC out 1 → divider → transformer 1 → DC-block cap → radio mic | Mic level (tens of mV) | — | CALCULATED; level set by ear on a second radio |
| H-18 | Radio speaker → divider → transformer 2 → UMC in 4 | Primary floating | — | CALCULATED |
| H-19 | UMC404HD → Jetson USB | USB 2.0 class-compliant, bus-powered, phantom off | Jetson USB | Linux VERIFIED; **on Jetson UNKNOWN** |
| H-20 | ADAU eval board power | USB or 3.8–5 V | USB / H20 | VERIFIED |
| H-21 | Jetson power | Kit adapter | Mains / battery pack | VERIFIED |
| H-22 | Grounding | One star ground; radio isolated by transformers + opto | — | Hum UNKNOWN until assembled; H17 is the fallback (high-speed isolator only — **not** ADuM3160) |

---

## 3. Software ↔ hardware links

| # | Link | What must match | Status |
|---|---|---|---|
| S-1 | Channel order | UMC in 1 boom, in 2 reference, in 3 throat = model inputs 0, 1, 2 = `data.py` order | TESTED (self-test + runner with fake 4-channel audio) |
| S-2 | Radio receive | UMC in 4 → `--rx-ch 4` → UMC out 2 | TESTED with fake audio; R1–R5 cleaning **not coded yet** (passthrough + ceiling only) |
| S-3 | Rates | 48 kHz capture ↔ 16 kHz model, 3:1 resampler | TESTED in code; on Jetson UNKNOWN |
| S-4 | Framing | 768 samples at 48 kHz = 256 at 16 kHz = one model hop | TESTED |
| S-5 | ONNX interface | `frame (1, 3, 257, 1, 2)` + caches conv (1,6,16,10,33), tra (6,1,16), inter (4,33,8) | TESTED (parity ≤ 6×10⁻⁸) |
| S-6 | TensorRT | GRU layers run in FP32 / FP16 / BF16, **not INT8** (VERIFIED, NVIDIA docs) → INT8 only for convolutions, GRUs stay FP16 | Engine build UNKNOWN (needs the Jetson) |
| S-7 | Frame time | Must finish in 16 ms at the 99th percentile | UNKNOWN (Gate 6); ≈ 25 k-parameter model makes it very likely |
| S-8 | Throat mic missing | Model trained with 30 % zero throat input; runs if the mic is unplugged | TESTED (self-test dropout check) |
| S-9 | Throat realism | Simulated throat (low-pass 1.5–3 kHz + small noise leak) vs a real throat mic | UNKNOWN — compare with TAPS / Vibravox and with our own mic before the full run |
| S-10 | B3 normalisation | Same in training and runtime | Consistent (both absent); add to both together |
| S-11 | UART protocol | Jetson and STM32 speak the same lines | Defined; not coded |
| S-12 | Python version | JetPack 6 ships Python 3.10; code tested on newer Python | Grep found no 3.11+-only syntax; run the self-test on the Jetson first thing |
| S-13 | Jetson packages | `onnxruntime-gpu` (Jetson build), `sounddevice` + PortAudio, TensorRT from JetPack | UNKNOWN until installed |
| S-14 | 82 dB at the ear | ADAU limiter (79 dB share) + radio path ceiling (79 dB share) | Settings exist; true SPL only by mannequin measurement |
| S-15 | Handedness | Switch picks Mic 2R or 2L for UMC in 2; software unchanged | Design; no code dependency |
| S-16 | FastDSP capacity | Two ANC paths + hear-through + limiters in one ADAU1787 | UNKNOWN (Gate 2); fallback: shorter ANC filters |

---

## 4. Staged buy-and-test plan

Buy in stages so a failed gate costs little.

| Stage | Buy | Test | Pass means |
|---|---|---|---|
| 1 | Jetson, microSD, UMC404HD | JetPack; UMC records 4 channels at 48 kHz; self-test on Python 3.10; TensorRT engine; `realtime.py` loopback, 99th-percentile frame time | Lane B platform works (S-3, S-6, S-7, S-12, S-13, H-19) |
| 2 | ADAU eval board, STM32, PCA9306 | Read UG-1532; SigmaStudio pass-through; I²C from the STM32; FastDSP load with two ANC filters | Lane A platform works (H-11, H-20, S-16) |
| 3 | Mics, earmuffs (practice pair first), preamp parts, TPA6130A2 | Build H6 on perfboard; measure 2.8 V rail, bias, noise floor, clip level; hear-through at the dummy ear | Headset works (H-1 … H-10) |
| 4 | Radios, H19 parts | Radio pinout; DC-block cap; STM32 PTT; voice level on a second radio | Radio link works (H-14 … H-18) |
| 5 | — | Full system: ANC dB at the mannequin, 82 dB cap, SNR / STOI / PESQ on range recordings | Ready to demo |

---

## 5. What this audit cannot promise

- Parts not in hand (ADAU eval board details, radio pinout, throat mic type,
  breakout stock) can still surprise us. They are listed as UNKNOWN above,
  each with the test that settles it.
- Every CALCULATED line is arithmetic, not a measurement. Stage 3 and 4 bench
  tests turn them into MEASURED.
