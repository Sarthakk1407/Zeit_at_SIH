# Download links — every dataset, every URL

Target drive: **`/Volumes/ZEIT V.1.0/zeit-data/`** — folders are named `Dataset_Source` (e.g. `MUSAN_OpenSLR`), so the origin is visible from the folder name.

**Status: 11 of 16 datasets downloaded, ~229,000 audio files, ~100 GB.** The one still worth doing is **FSD50K**.

Original target drive note (APFS — quotes needed, the name has a space)

```bash
cd /Users/dushyant/ANC/V_1
python3 synthetic_generator/download.py "/Volumes/ZEIT V.1.0"
```

---

## AUTO — ✅ ALL 8 ARCHIVES COMPLETE (11 Sep 2026)

The script finished every automatic download. Nothing left to do here.



| Folder | Dataset | Direct URL | Size | Licence |
|---|---|---|---|---|
| `LibriSpeech_OpenSLR/` | train-clean-100 | `https://www.openslr.org/resources/12/train-clean-100.tar.gz` | 6.3 GB | CC BY 4.0 |
| `LibriSpeech_OpenSLR/` | train-clean-360 | `https://www.openslr.org/resources/12/train-clean-360.tar.gz` | 23 GB | CC BY 4.0 |
| `LibriSpeech_OpenSLR/` | dev-clean | `https://www.openslr.org/resources/12/dev-clean.tar.gz` | 337 MB | CC BY 4.0 |
| `LibriSpeech_OpenSLR/` | test-clean | `https://www.openslr.org/resources/12/test-clean.tar.gz` | 346 MB | CC BY 4.0 |
| `MUSAN_OpenSLR/` | MUSAN | `https://www.openslr.org/resources/17/musan.tar.gz` | 11 GB | CC BY 4.0 |
| `ESC50_GitHub/` | ESC-50 | `https://github.com/karolpiczak/ESC-50/archive/master.zip` | 600 MB | CC BY-NC 3.0 |
| `OpenSLR28_RIRs/` | RIRs and Noises | `https://www.openslr.org/resources/28/rirs_noises.zip` | 4 GB | Apache 2.0 |
| `ZenodoGuns_Zenodo/` | Gunshot/Gunfire | `https://zenodo.org/records/7004819/files/edge-collected-gunshot-audio.zip?download=1` | 1.5 GB | CC BY 4.0 |

If ZenodoGuns shows **HTTP 504**, that is Zenodo's server timing out, not a fault on our side.
Just rerun the script later; everything already complete is skipped.

---

## MANUAL — browser needed. Do them in this order.

Each folder already exists with a `SOURCE.txt` inside. Download the file, drop it in that folder.

### ✅ 1. NOISEX-92 → `NOISEX92_SPIB/` — **DONE**, 14 files

**https://spib.linse.ufsc.br/noise.html**

Only ~50 MB and it is the **only** source of real tank and military aircraft audio anywhere on this list.

Grab these files: `leopard` (tank), `m109` (tank), `f16` (jet cockpit), `machinegun`,
`babble`, `factory1`, `factory2`, `hfchannel` (radio), `pink`, `white`, `volvo` (vehicle).

Licence: research use. 19.98 kHz, 235 s each.

### ✅ 2. MAD — Military Audio Dataset → `MAD_Kaggle/` — **DONE**, 7,466 files

**Get the audio from Kaggle** (the authors' own README says so, and says the YouTube
downloader is no longer needed):

**https://www.kaggle.com/datasets/junewookim/mad-dataset-military-audio-dataset**

```bash
pip install kaggle
# Kaggle -> Settings -> API -> Create New Token  (downloads kaggle.json)
mkdir -p ~/.kaggle && mv ~/Downloads/kaggle.json ~/.kaggle/ && chmod 600 ~/.kaggle/kaggle.json
kaggle datasets download -d junewookim/mad-dataset-military-audio-dataset \
  -p "/Volumes/ZEIT V.1.0/zeit-data/MAD" --unzip
```

8,075 clips, 12 h, 16 kHz, CC BY 4.0. Almost exactly the PS's noise list:
gunshot 1714 · shelling 1173 · communication 1150 · vehicle 1123 · helicopter 1009 · fighter 985 · footsteps 921

Paper: https://www.nature.com/articles/s41597-024-03511-w

**Do NOT clone the GitHub repo for the audio** — `github.com/kaen2891/military_audio_dataset`
holds only training code (ResNet18 / AST baselines, and `method/`, `models/`, `scripts/` are
deleted). The one file worth taking from it is `mad_dataset_annotation.csv` (8,085 rows:
title, video number, file id, start/end time, label, YouTube URL).

**Caveat to state in the report:** every row in that CSV is a YouTube URL, so MAD carries
YouTube's compression. Good for class coverage and training, but it is not calibrated
measurement — our own 44 range events stay the reference.

### ✅ 3. Lombard GRID → `LombardGRID_Sheffield/` — **DONE**, 5,390 files

**https://spandh.dcs.shef.ac.uk/avlombard/**

54 talkers × 100 utterances = **50 Lombard + 50 plain, paired**. Audio-only is enough; the
video views can be skipped. Free for research, a short form.

This closes the single biggest gap in the plan — see `DATASET_SPEC.md` §0.6.

### ✅ 4. Cadre Gunshot Audio Forensics → `Cadre_GunshotForensics/` — **DONE**, 2,241 files

**https://cadreforensics.com/audio/**

~10,000 recordings, 20 firearms × 20 positions × 4 devices, rural Arizona 2017, NIJ Grant
2016-DN-BX-0183. Requires accepting the NIJ disclaimer.

The 20 positions per firearm are exactly the azimuth/distance grid our own field checklist asks for.

### ✅ 5. DEMAND → `DEMAND_Zenodo/` — **DONE**, 8 environments

**https://zenodo.org/records/1227121**

18 environments × 16 channels, WAV at both 48 kHz and 16 kHz, one zip per environment.
CC BY-SA 3.0. Kitchen, office, cafe, town square, car, metro, park, station, traffic.

### ✅ 6. UrbanSound8K → `UrbanSound8K_NYU/` — **DONE**, 8,732 files

**https://urbansounddataset.weebly.com/urbansound8k.html**

8,732 clips ≤ 4 s across 10 classes — siren, engine idling, jackhammer, drilling, dog bark.
Short form. **CC BY-NC 3.0 — non-commercial.** Fine for the competition, flag it for a product.

### ⬜ 7. TAU Urban Acoustic Scenes 2020 → `TAUUrban_Zenodo/` — optional

Development set: **https://zenodo.org/records/3670167**
Evaluation set: **https://zenodo.org/records/3685828**
3-class evaluation: **https://zenodo.org/records/3685835**

10 s segments from 10 scenes: airport, shopping mall, metro station, pedestrian street,
public square, street traffic, urban park, bus, tram, metro. CC BY-NC.

### ⭐ 8. FSD50K → `FSD50K_Zenodo/` — **DO THIS ONE NEXT**

**https://zenodo.org/records/4060432**

51,197 Freesound clips, 200 classes from the AudioSet ontology — gunshot, explosion, siren,
engine. Mixed CC BY / CC0. Split across several zip parts; take them all.

### ⬜ 9. DroneAudioSet → `DroneAudioSet_HF/`

**https://huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/**

23.5 h, MIT licence. Fastest route:

```bash
pip install huggingface_hub
huggingface-cli download ahlab-drone-project/DroneAudioSet \
  --repo-type dataset --local-dir "/Volumes/ZEIT V.1.0/zeit-data/DroneAudioSet"
```

### ⬜ 10. DREGON → `DREGON_Inria/` — optional

**https://dregon.inria.fr/datasets/dregon/**

8-channel microphone array mounted **on** a quadrotor, 44.1 kHz, with per-rotor rps logs.
In-flight and static recordings, with and without a source. Research use.

### ⏳ 11. SPRING-INX → `SPRINGINX_IITM/` — access request pending

Paper with the access link: **https://arxiv.org/abs/2310.14654**

~2,000 h across 10 Indian languages including Hindi, manually transcribed. From SPRING Lab,
IIT Madras, funded by **MeitY, Government of India** under the National Language Translation
Mission. Requires an access request.

Smaller Hindi fallback if this is slow: **Mozilla Common Voice Hindi** — https://commonvoice.mozilla.org/en/datasets

---

## Zenodo tip

Every Zenodo file has a direct URL of the form:

```
https://zenodo.org/records/<RECORD_ID>/files/<FILENAME>?download=1
```

Open the record page, right-click a file, copy the link, then:

```bash
curl -L -C - -o "/Volumes/ZEIT V.1.0/zeit-data/<Folder>/<file>" "<url>"
```

`-C -` makes it resumable.

---

## Licence table — keep this, DRDO will ask

| Safe for a shipped product | Non-commercial only |
|---|---|
| LibriSpeech, MUSAN, MAD, ZenodoGuns, FSD50K (CC BY / CC0), DEMAND (CC BY-SA), DroneAudioSet (MIT), OpenSLR28 (Apache 2.0) | **ESC-50, UrbanSound8K, TAU Urban** (CC BY-NC) |
| Research use, check terms | NOISEX-92, Cadre, DREGON, Lombard GRID, SPRING-INX |

A model trained on CC BY-NC data cannot ship commercially. Fine for SIH; say so out loud
rather than being caught by it.
