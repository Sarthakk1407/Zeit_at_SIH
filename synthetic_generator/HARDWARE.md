# Hardware — as specified in `handbook/`

Read from `handbook/README.md` and `handbook/src3d/04-geometry.html`. World
scale in the 3D model is **1 unit = 10 mm**, and component dimensions follow
datasheets, so on-screen distances are the specification's distances.

## The prototype bench

| Part | Role | Note |
|---|---|---|
| **Headset** | 3 mics + 1 speaker | boom arm on the left cup |
| **Behringer UMC202HD** | 2-in USB audio interface | 128 × 130 × 47 mm, XLR preamps, switchable 48 V phantom, 24-bit up to **192 kHz** |
| **Raspberry Pi 5** | compute | with cooler, PSU, SD card |

Jetson AGX Orin — which the PS names — is noted in the handbook as *itself the
size of* the thing it is meant to fit inside. The Pi 5 is the bench stand-in.

## Sensor positions

Offsets from head origin, in model units (1 unit = 10 mm):

| Sensor | Offset (x, y, z) | Where |
|---|---|---|
| `P_MIC1` | (−1.6, −5.6, 11.2) | **boom mic at the mouth** — primary |
| `P_MIC2` | (12.0, −0.2, 0.4) | **outer earcup shell** — noise reference |
| `P_MIC3` | (8.7, −0.2, 0.9) | **inside the earcup** — in-ear error sensor |
| `P_SPK` | (10.0, −0.2, −0.5) | earcup speaker — anti-noise output |

Mic 1 and Mic 2 sit on opposite sides of the head, ~20 cm apart → **0.58 ms**
inter-mic delay. That is the real geometric look-ahead on a headset, not 29 ms.

**Widrow's constraint:** Mic 2 must contain zero components of the wearer's
voice, or the adaptive filter — which minimises total output power — will
cancel the voice it exists to protect. The handbook states this as a mechanical
requirement for the hardware team.

## The timing the design is built around

Shooter at 30 m, supersonic round:

| t | Event |
|---|---|
| 0 ms | Trigger; muzzle blast expands at 343 m/s |
| 36.5 ms | Bullet at closest approach (~3 m), generates the shockwave |
| **45.2 ms** | **Crack arrives** |
| **87.5 ms** | **Blast arrives** |
| — | **42.3 ms gap — the only genuine look-ahead a headset has** |
| +0.58 ms | Mic 1 after Mic 2 |
| +1 ms | **Lane A** responded |
| +25.3 ms | **Lane B** completed |

## ⭐ The practical consequence for the next range trip

**The UMC202HD is a 2-input interface.** The 7 Sep trip failed on the two-mic
half precisely because the J13 wireless receiver presented as a **1-channel**
USB device — CoreAudio rejected 2 channels at every sample rate — so both
transmitters were summed into one channel that can never be un-mixed.

With the UMC202HD instead:

- two genuinely separate channels, sample-synchronous on one clock — no
  aggregate device, no drift correction, no clap sync
- **24-bit at up to 192 kHz**, so the documented **96 kHz** requirement is met
  rather than falling back to 48 kHz
- real gain knobs per channel, so the staggered-gain array (hot channel + cold
  channel covering the peak) actually works
- no wireless companding or AGC, which is what squeezed the dynamic range on
  7 Sep — clipping on the impulse *and* events buried near the floor at the
  same time

If the UMC202HD already exists on the bench, it should be the capture front end
for the next trip, not the wireless lav pair.
