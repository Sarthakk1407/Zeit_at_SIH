# Data and its source

Scanned `/Volumes/ZEIT V.1.0/zeit-data` on 2026-09-11.

Regenerate with:

```bash
python3 synthetic_generator/make_manifest.py "/Volumes/ZEIT V.1.0/zeit-data"
```

**1 datasets on disk · 33,028 audio files · 35 GB**


---

## On disk and usable

| Dataset | Files | Size | Source | Licence |
|---|---|---|---|---|
| **LibriSpeech_OpenSLR** | 33,028 audio | 35 GB | [LibriSpeech_OpenSLR](https://www.openslr.org/12/) | CC BY 4.0 |

## Not downloaded yet

| Dataset | What it gives | Source |
|---|---|---|
| LombardGRID_Sheffield | 54 talkers x 100 utterances = 50 Lombard + 50 plain, PAIRED. Same speaker, same sentence, with and without the Lombard reflex. | [Audio-Visual Lombard Grid corpus](https://spandh.dcs.shef.ac.uk/avlombard/) |
| SPRINGINX_IITM | ~2000 h, 10 Indian languages incl. Hindi. MeitY / Govt of India funded. | [SPRING-INX (IIT Madras)](https://arxiv.org/abs/2310.14654) |
| MUSAN_OpenSLR | 109 h of noise, speech and music, built for augmentation. | [MUSAN_OpenSLR](https://www.openslr.org/17/) |
| NOISEX92_SPIB | 15 noises x 235 s. The only source of real tank (leopard, m109), F-16 cockpit and machine gun audio on this list. Shipped as .mat, converted here to WAV. | [NOISEX-92](https://spib.linse.ufsc.br/noise.html) |
| ESC50_GitHub | 2000 clips x 5 s, 50 classes. helicopter, train, wind, rain, siren. | [ESC-50](https://github.com/karolpiczak/ESC-50) |
| DEMAND_Zenodo | 18 environments recorded on a 16-CHANNEL array, mic spacing 5 cm to 21.8 cm. The ~20 cm pairs match our own Mic1<->Mic2 spacing, so two channels give realistic correlated two-mic noise. | [DEMAND_Zenodo](https://zenodo.org/records/1227121) |
| UrbanSound8K_NYU | 8732 clips. siren, engine idling, jackhammer, drilling. | [UrbanSound8K_NYU](https://urbansounddataset.weebly.com/urbansound8k.html) |
| TAUUrban_Zenodo | metro, metro_station, tram, bus, street_traffic, park, airport. | [TAU Urban Acoustic Scenes 2020](https://zenodo.org/records/3670167) |
| FSD50K_Zenodo | 51,197 Freesound clips, 200 AudioSet classes. | [FSD50K_Zenodo](https://zenodo.org/records/4060432) |
| ZenodoGuns_Zenodo | 2,148 real gunshots, 4 firearms, multi-orientation, edge devices at an outdoor range. | [Zenodo Gunshot/Gunfire Audio Dataset](https://zenodo.org/records/7004819) |
| Cadre_GunshotForensics | 20 firearms x 20 positions x 4 devices, rural Arizona 2017, NIJ Grant 2016-DN-BX-0183. 44.1 kHz mono -- noise library, not calibrated measurement. | [Cadre Gunshot Audio Forensics Dataset](https://cadreforensics.com/audio/) |
| MAD_Kaggle | gunshot 1714 | shelling 1173 | communication 1150 | vehicle 1123 | helicopter 1009 | fighter 985 | footsteps 921. Sourced from YouTube, so it carries YouTube compression -- good for coverage, not for absolute SPL. | [MAD -- Military Audio Dataset](https://www.kaggle.com/datasets/junewookim/mad-dataset-military-audio-dataset) |
| DroneAudioSet_HF | 23.5 h of drone audio. | [DroneAudioSet_HF](https://huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/) |
| DREGON_Inria | 8-channel array mounted ON a quadrotor, 44.1 kHz, per-rotor rps. | [DREGON_Inria](https://dregon.inria.fr/datasets/dregon/) |
| OpenSLR28_RIRs | Real + simulated room impulse responses. | [RIRs and Noises](https://www.openslr.org/28/) |

---

## What each one is for

### LibriSpeech_OpenSLR — 33,028 audio

**LibriSpeech_OpenSLR** · CC BY 4.0

Clean English read speech. The clean half of every training pair.

Source: https://www.openslr.org/12/

### LombardGRID_Sheffield — not downloaded

**Audio-Visual Lombard Grid corpus** · free for research

54 talkers x 100 utterances = 50 Lombard + 50 plain, PAIRED. Same speaker, same sentence, with and without the Lombard reflex.

Source: https://spandh.dcs.shef.ac.uk/avlombard/

### SPRINGINX_IITM — not downloaded

**SPRING-INX (IIT Madras)** · open, see paper

~2000 h, 10 Indian languages incl. Hindi. MeitY / Govt of India funded.

Source: https://arxiv.org/abs/2310.14654

### MUSAN_OpenSLR — not downloaded

**MUSAN_OpenSLR** · CC BY 4.0

109 h of noise, speech and music, built for augmentation.

Source: https://www.openslr.org/17/

### NOISEX92_SPIB — not downloaded

**NOISEX-92** · research use

15 noises x 235 s. The only source of real tank (leopard, m109), F-16 cockpit and machine gun audio on this list. Shipped as .mat, converted here to WAV.

Source: https://spib.linse.ufsc.br/noise.html

### ESC50_GitHub — not downloaded

**ESC-50** · CC BY-NC 3.0

2000 clips x 5 s, 50 classes. helicopter, train, wind, rain, siren.

Source: https://github.com/karolpiczak/ESC-50

### DEMAND_Zenodo — not downloaded

**DEMAND_Zenodo** · CC BY-SA 3.0

18 environments recorded on a 16-CHANNEL array, mic spacing 5 cm to 21.8 cm. The ~20 cm pairs match our own Mic1<->Mic2 spacing, so two channels give realistic correlated two-mic noise.

Source: https://zenodo.org/records/1227121

### UrbanSound8K_NYU — not downloaded

**UrbanSound8K_NYU** · CC BY-NC 3.0

8732 clips. siren, engine idling, jackhammer, drilling.

Source: https://urbansounddataset.weebly.com/urbansound8k.html

### TAUUrban_Zenodo — not downloaded

**TAU Urban Acoustic Scenes 2020** · CC BY-NC

metro, metro_station, tram, bus, street_traffic, park, airport.

Source: https://zenodo.org/records/3670167

### FSD50K_Zenodo — not downloaded

**FSD50K_Zenodo** · CC BY / CC0

51,197 Freesound clips, 200 AudioSet classes.

Source: https://zenodo.org/records/4060432

### ZenodoGuns_Zenodo — not downloaded

**Zenodo Gunshot/Gunfire Audio Dataset** · CC BY 4.0

2,148 real gunshots, 4 firearms, multi-orientation, edge devices at an outdoor range.

Source: https://zenodo.org/records/7004819

### Cadre_GunshotForensics — not downloaded

**Cadre Gunshot Audio Forensics Dataset** · NIJ / research use

20 firearms x 20 positions x 4 devices, rural Arizona 2017, NIJ Grant 2016-DN-BX-0183. 44.1 kHz mono -- noise library, not calibrated measurement.

Source: https://cadreforensics.com/audio/

### MAD_Kaggle — not downloaded

**MAD -- Military Audio Dataset** · CC BY 4.0

gunshot 1714 | shelling 1173 | communication 1150 | vehicle 1123 | helicopter 1009 | fighter 985 | footsteps 921. Sourced from YouTube, so it carries YouTube compression -- good for coverage, not for absolute SPL.

Source: https://www.kaggle.com/datasets/junewookim/mad-dataset-military-audio-dataset

### DroneAudioSet_HF — not downloaded

**DroneAudioSet_HF** · MIT

23.5 h of drone audio.

Source: https://huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/

### DREGON_Inria — not downloaded

**DREGON_Inria** · research use

8-channel array mounted ON a quadrotor, 44.1 kHz, per-rotor rps.

Source: https://dregon.inria.fr/datasets/dregon/

### OpenSLR28_RIRs — not downloaded

**RIRs and Noises** · Apache 2.0

Real + simulated room impulse responses.

Source: https://www.openslr.org/28/


---

## Our own measured data (not downloaded)

| What | Where | Note |
|---|---|---|
| 44 impulsive events | `data for training/REFERENCE_REAL/events_impulse/` | The reference the synthetic generator is validated against |
| 213 detected events | `data for training/REFERENCE_REAL/events_all/` | all detections |
| 15 raw takes | `DATA/002_shot01` … `016_shot015` | 2 ch, 48 kHz, 24-bit |

Recorded 7 Sep 2026, air gun, target impact as the impulsive source. **Uncalibrated** — levels are dBFS, not dB SPL.


## Licence warning

**CC BY-NC (non-commercial): ESC-50, UrbanSound8K, TAU Urban.** Fine for the competition; a shipped product cannot be trained on them. The safe commercial core is LibriSpeech, MUSAN, MAD, ZenodoGuns, FSD50K, DEMAND, OpenSLR28, DroneAudioSet.

