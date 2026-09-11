#!/usr/bin/env python3
"""wlps.py -- Words Lost Per Shot.

IRT measures how long the signal takes to come back. WLPS measures what the
listener actually lost: how many words were destroyed inside each impulse
window.

    python3 wlps.py --ref reference.txt --hyp asr_output.json --events events.json

PESQ and STOI average over an utterance, so a 200 ms gunshot in a ten-second
clip barely moves them. WLPS counts only the words whose time span overlaps an
impulse, so the number reports exactly the damage the problem statement is
about, per event, and is directly comparable between systems.

Inputs
  --ref     ground-truth transcript, one utterance per line, or a JSON list of
            {"word": str, "start": s, "end": s}
  --hyp     ASR output as JSON: [{"word": str, "start": s, "end": s}, ...]
            Any word-level ASR works (Whisper with word timestamps, Vosk,
            wav2vec2 + CTC segmentation). The ASR model is deliberately not
            fixed here -- it is a parameter of the experiment, and it must be
            the SAME model for every system compared.
  --events  impulse onsets: JSON list of seconds, or of
            {"onset": s, "duration_ms": ms}

Output
  words_lost_per_shot   mean over events -- the headline number
  wer_in_window         word error rate inside impulse windows
  wer_outside           word error rate outside them (the control)

The comparison that matters is in_window vs outside. A system that lowers
wer_in_window without raising wer_outside has genuinely recovered speech; one
that lowers both equally has only got better at ASR in general.
"""
import argparse, json, sys

DEFAULT_WINDOW_MS = 250.0   # if an event carries no duration, assume this


def load_words(path):
    d = json.load(open(path))
    return [(w['word'].lower().strip('.,!?;:"'), float(w['start']), float(w['end']))
            for w in d if w.get('word')]


def load_events(path):
    d = json.load(open(path))
    out = []
    for e in d:
        if isinstance(e, (int, float)):
            out.append((float(e), DEFAULT_WINDOW_MS))
        else:
            out.append((float(e['onset']),
                        float(e.get('duration_ms', DEFAULT_WINDOW_MS))))
    return out


def in_window(w, events):
    _, s, e = w
    for onset, dur in events:
        if e >= onset and s <= onset + dur / 1000.0:
            return True
    return False


def levenshtein(a, b):
    """Word-level edit distance."""
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ref', required=True, help='ground-truth words JSON')
    ap.add_argument('--hyp', required=True, help='ASR output JSON')
    ap.add_argument('--events', required=True, help='impulse onsets JSON')
    ap.add_argument('--json', help='write results here')
    a = ap.parse_args()

    ref, hyp, ev = load_words(a.ref), load_words(a.hyp), load_events(a.events)
    if not ev:
        print("no events given", file=sys.stderr)
        return 1

    ref_in = [w for w in ref if in_window(w, ev)]
    ref_out = [w for w in ref if not in_window(w, ev)]
    hyp_in = [w for w in hyp if in_window(w, ev)]
    hyp_out = [w for w in hyp if not in_window(w, ev)]

    err_in = levenshtein([w[0] for w in ref_in], [w[0] for w in hyp_in])
    err_out = levenshtein([w[0] for w in ref_out], [w[0] for w in hyp_out])

    res = {
        'n_events': len(ev),
        'words_in_window': len(ref_in),
        'words_outside': len(ref_out),
        'words_lost_per_shot': round(err_in / len(ev), 3),
        'wer_in_window': round(err_in / len(ref_in), 4) if ref_in else None,
        'wer_outside': round(err_out / len(ref_out), 4) if ref_out else None,
    }
    if res['wer_in_window'] is not None and res['wer_outside'] is not None:
        res['wer_penalty'] = round(res['wer_in_window'] - res['wer_outside'], 4)

    print(f"\n  events              {res['n_events']}")
    print(f"  words in window     {res['words_in_window']}")
    print(f"  words outside       {res['words_outside']}")
    print(f"\n  WORDS LOST PER SHOT {res['words_lost_per_shot']:.2f}")
    print(f"  WER in window       {res['wer_in_window']}")
    print(f"  WER outside         {res['wer_outside']}")
    if 'wer_penalty' in res:
        print(f"  WER penalty         {res['wer_penalty']:+.4f}   <- the impulse cost\n")

    if a.json:
        json.dump(res, open(a.json, 'w'), indent=2)
        print(f"  -> {a.json}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
