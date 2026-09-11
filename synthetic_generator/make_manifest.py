#!/usr/bin/env python3
"""make_manifest.py -- scan the data drive and write DATA_SOURCES.md.

    python3 make_manifest.py "/Volumes/ZEIT V.1.0/zeit-data"

Walks every dataset folder, counts what is actually there, and writes a table
of data -> source -> licence. Rerun it whenever more data lands.
"""
import argparse, os, sys, datetime

# short -> (full name, what it is, source URL, licence)
SRC = {
 "LibriSpeech_OpenSLR":  ("LibriSpeech_OpenSLR", "Clean English read speech. The clean half of every training pair.",
                  "https://www.openslr.org/12/", "CC BY 4.0"),
 "LombardGRID_Sheffield":  ("Audio-Visual Lombard Grid corpus",
                  "54 talkers x 100 utterances = 50 Lombard + 50 plain, PAIRED. Same speaker, "
                  "same sentence, with and without the Lombard reflex.",
                  "https://spandh.dcs.shef.ac.uk/avlombard/", "free for research"),
 "SPRINGINX_IITM":    ("SPRING-INX (IIT Madras)",
                  "~2000 h, 10 Indian languages incl. Hindi. MeitY / Govt of India funded.",
                  "https://arxiv.org/abs/2310.14654", "open, see paper"),
 "MUSAN_OpenSLR":        ("MUSAN_OpenSLR", "109 h of noise, speech and music, built for augmentation.",
                  "https://www.openslr.org/17/", "CC BY 4.0"),
 "NOISEX92_SPIB":     ("NOISEX-92",
                  "15 noises x 235 s. The only source of real tank (leopard, m109), F-16 cockpit "
                  "and machine gun audio on this list. Shipped as .mat, converted here to WAV.",
                  "https://spib.linse.ufsc.br/noise.html", "research use"),
 "ESC50_GitHub":        ("ESC-50", "2000 clips x 5 s, 50 classes. helicopter, train, wind, rain, siren.",
                  "https://github.com/karolpiczak/ESC-50", "CC BY-NC 3.0"),
 "DEMAND_Zenodo":       ("DEMAND_Zenodo",
                  "18 environments recorded on a 16-CHANNEL array, mic spacing 5 cm to 21.8 cm. "
                  "The ~20 cm pairs match our own Mic1<->Mic2 spacing, so two channels give "
                  "realistic correlated two-mic noise.",
                  "https://zenodo.org/records/1227121", "CC BY-SA 3.0"),
 "UrbanSound8K_NYU": ("UrbanSound8K_NYU", "8732 clips. siren, engine idling, jackhammer, drilling.",
                  "https://urbansounddataset.weebly.com/urbansound8k.html", "CC BY-NC 3.0"),
 "TAUUrban_Zenodo":     ("TAU Urban Acoustic Scenes 2020",
                  "metro, metro_station, tram, bus, street_traffic, park, airport.",
                  "https://zenodo.org/records/3670167", "CC BY-NC"),
 "FSD50K_Zenodo":       ("FSD50K_Zenodo", "51,197 Freesound clips, 200 AudioSet classes.",
                  "https://zenodo.org/records/4060432", "CC BY / CC0"),
 "ZenodoGuns_Zenodo":   ("Zenodo Gunshot/Gunfire Audio Dataset",
                  "2,148 real gunshots, 4 firearms, multi-orientation, edge devices at an outdoor range.",
                  "https://zenodo.org/records/7004819", "CC BY 4.0"),
 "Cadre_GunshotForensics":        ("Cadre Gunshot Audio Forensics Dataset",
                  "20 firearms x 20 positions x 4 devices, rural Arizona 2017, NIJ Grant "
                  "2016-DN-BX-0183. 44.1 kHz mono -- noise library, not calibrated measurement.",
                  "https://cadreforensics.com/audio/", "NIJ / research use"),
 "MAD_Kaggle":          ("MAD -- Military Audio Dataset",
                  "gunshot 1714 | shelling 1173 | communication 1150 | vehicle 1123 | "
                  "helicopter 1009 | fighter 985 | footsteps 921. Sourced from YouTube, so it "
                  "carries YouTube compression -- good for coverage, not for absolute SPL.",
                  "https://www.kaggle.com/datasets/junewookim/mad-dataset-military-audio-dataset",
                  "CC BY 4.0"),
 "DroneAudioSet_HF":("DroneAudioSet_HF", "23.5 h of drone audio.",
                  "https://huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/", "MIT"),
 "DREGON_Inria":       ("DREGON_Inria", "8-channel array mounted ON a quadrotor, 44.1 kHz, per-rotor rps.",
                  "https://dregon.inria.fr/datasets/dregon/", "research use"),
 "OpenSLR28_RIRs":    ("RIRs and Noises", "Real + simulated room impulse responses.",
                  "https://www.openslr.org/28/", "Apache 2.0"),
}

def human(n):
    for u in ('B','KB','MB','GB'):
        if n < 1024: return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

AUDIO = ('.wav', '.flac', '.ogg', '.mp3', '.m4a', '.aif', '.aiff')

def scan(fold):
    """Count audio, and only flag archives that are NOT already filed in _archive/."""
    wav = mat = other = 0; size = 0; pending = 0; arch = 0
    for r, _, fs in os.walk(fold):
        in_archive = os.sep + '_archive' in r
        for f in fs:
            if f.startswith('.'): continue
            p = os.path.join(r, f)
            try: size += os.path.getsize(p)
            except OSError: continue
            lf = f.lower()
            if lf.endswith(AUDIO): wav += 1
            elif lf.endswith('.mat'): mat += 1
            elif lf.endswith(('.crdownload', '.part')): pending += 1
            elif lf.endswith(('.zip','.tar.gz','.tgz','.tar')):
                if not in_archive: arch += 1     # already unpacked ones don't count
            else: other += 1
    return dict(wav=wav, mat=mat, other=other, size=size, pending=pending, arch=arch)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--out', default='synthetic_generator/DATA_SOURCES.md')
    a = ap.parse_args()
    if not os.path.isdir(a.root): print(f"not found: {a.root}"); return 1

    rows = []
    for short in SRC:
        fold = os.path.join(a.root, short)
        rows.append((short, scan(fold) if os.path.isdir(fold) else None))

    have = [(s, st) for s, st in rows if st and st['wav'] > 0]
    part = [(s, st) for s, st in rows if st and st['wav'] == 0 and (st['pending'] or st['arch'])]
    none = [(s, st) for s, st in rows if not st or (st['wav'] == 0 and not st['pending'] and not st['arch'])]
    tot_wav = sum(st['wav'] for _, st in have)
    tot_size = sum(st['size'] for _, st in rows if st)

    L = []
    L.append("# Data and its source\n")
    L.append(f"Scanned `{a.root}` on {datetime.date.today().isoformat()}.\n")
    L.append(f"Regenerate with:\n\n```bash\npython3 synthetic_generator/make_manifest.py \"{a.root}\"\n```\n")
    L.append(f"**{len(have)} datasets on disk · {tot_wav:,} audio files · {human(tot_size)}**\n")

    L.append("\n---\n\n## On disk and usable\n")
    L.append("| Dataset | Files | Size | Source | Licence |")
    L.append("|---|---|---|---|---|")
    for s, st in sorted(have, key=lambda r: -r[1]['wav']):
        full, _, url, lic = SRC[s]
        L.append(f"| **{s}** | {st['wav']:,} audio | {human(st['size'])} | [{full}]({url}) | {lic} |")

    if part:
        L.append("\n## Downloaded but not yet unpacked\n")
        L.append("| Dataset | State | Size | Source |")
        L.append("|---|---|---|---|")
        for s, st in part:
            full, _, url, _ = SRC[s]
            state = (f"{st['pending']} still downloading" if st['pending']
                     else f"{st['arch']} archive(s) to unpack")
            L.append(f"| {s} | {state} | {human(st['size'])} | [{full}]({url}) |")
        L.append("\nUnpack with:\n\n```bash\npython3 synthetic_generator/unpack_manual.py "
                 f"\"{a.root}\"\n```\n")

    if none:
        L.append("\n## Not downloaded yet\n")
        L.append("| Dataset | What it gives | Source |")
        L.append("|---|---|---|")
        for s, _ in none:
            full, what, url, _ = SRC[s]
            L.append(f"| {s} | {what.splitlines()[0]} | [{full}]({url}) |")

    L.append("\n---\n\n## What each one is for\n")
    for s, st in rows:
        full, what, url, lic = SRC[s]
        n = f"{st['wav']:,} audio" if st and st['wav'] else ("pending" if st and (st['pending'] or st['arch']) else "not downloaded")
        L.append(f"### {s} — {n}\n")
        L.append(f"**{full}** · {lic}\n")
        L.append(f"{what}\n")
        L.append(f"Source: {url}\n")

    L.append("\n---\n\n## Our own measured data (not downloaded)\n")
    L.append("| What | Where | Note |")
    L.append("|---|---|---|")
    L.append("| 44 impulsive events | `data for training/REFERENCE_REAL/events_impulse/` | "
             "The reference the synthetic generator is validated against |")
    L.append("| 213 detected events | `data for training/REFERENCE_REAL/events_all/` | all detections |")
    L.append("| 15 raw takes | `DATA/002_shot01` … `016_shot015` | 2 ch, 48 kHz, 24-bit |")
    L.append("\nRecorded 7 Sep 2026, air gun, target impact as the impulsive source. "
             "**Uncalibrated** — levels are dBFS, not dB SPL.\n")

    L.append("\n## Licence warning\n")
    L.append("**CC BY-NC (non-commercial): ESC-50, UrbanSound8K, TAU Urban.** Fine for the "
             "competition; a shipped product cannot be trained on them. The safe commercial core "
             "is LibriSpeech, MUSAN, MAD, ZenodoGuns, FSD50K, DEMAND, OpenSLR28, DroneAudioSet.\n")

    os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
    open(a.out, 'w').write("\n".join(L) + "\n")
    print(f"\n  {len(have)} datasets · {tot_wav:,} audio files · {human(tot_size)}")
    print(f"  -> {a.out}\n")
    for s, st in sorted(have, key=lambda r: -r[1]['wav']):
        print(f"    {s:<16}{st['wav']:>9,} audio  {human(st['size']):>9}")
    for s, st in part:
        print(f"    {s:<16}{'pending':>9}      {human(st['size']):>9}")
    return 0

if __name__ == '__main__':
    sys.exit(main())
