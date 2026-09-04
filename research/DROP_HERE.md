# Research inputs — drop files here

Anything in these folders gets read before the workflow document is written.
PDF, DOCX, PPTX, TXT, MD all work. Filenames do not matter.

| Folder | What goes in it |
|---|---|
| `papers/` | Research papers — speech enhancement, ANC, gunshot acoustics, impulse noise |
| `models/` | Anything on the DNN side — architectures, benchmarks, papers, repo READMEs |
| `hardware/` | Mic specs, board datasheets, your friend's hardware notes, SWaP-C numbers |
| `datasets/` | Corpus documentation — DNS, DEMAND, MUSAN, LibriSpeech, anything you plan to use |

## What is already known (no need to re-supply)

- Problem statement 26052 in full (`docs/.TXT`)
- The real-data collection system — what is recorded, how, all 16 metrics,
  all algorithms (`docs/DETAILS.md`)
- PS targets: SNR > 15 dB, STOI > 0.85, PESQ > 2.5, real-time on edge hardware
- The dataset strategy: real gunshots as reference, synthetic for training,
  compare the two to prove dataset quality

## What is missing and blocks the workflow document

1. **The papers themselves** — nothing has been supplied yet
2. **Model choice evidence** — GTCRN was mentioned once in conversation with
   specific numbers (23.7K params, 39.6 MMACs/s, PESQ 2.87 on VCTK-DEMAND).
   That came from conversation, not from a source I have read. Supply the
   paper or I will mark those numbers as unverified.
3. **Hardware** — which board, which mics, how many, reference-mic geometry.
   Nothing concrete beyond "a friend is building it".
4. **Clean speech corpus** — undecided. PS wants Hindi and English.
