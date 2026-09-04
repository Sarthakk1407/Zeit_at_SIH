#!/usr/bin/env python3
"""
plan.py -- build the one-trip range plan: a printable run sheet plus the
metadata CSV pre-filled to match it.

    python3 plan.py --out rangeplan/ --hours 3.5

There is one visit, so the plan is ordered by what cannot be redone. Anything
irreplaceable happens while there is still time and daylight; anything that can
be shortened sits at the end. The time estimate is checked against the slot you
actually have, and the tool says so when the plan does not fit -- finding that
out here is free, finding it out at the range costs the session.
"""

import argparse
import csv
import os
import sys

META_COLS = ['shot_id', 'session', 'tier', 'timestamp', 'recorder',
             'gain_setting', 'sample_rate_hz', 'bit_depth',
             'weapon_make_model', 'caliber', 'barrel_length_cm', 'ammo_type',
             'suppressed', 'distance_m', 'azimuth_deg', 'mic_height_cm',
             'muzzle_height_cm', 'ground_surface', 'clipped', 'temp_c',
             'humidity_pct', 'wind_kmh', 'wind_direction', 'split', 'notes']


def blocks(sources, distances, repeats, azimuths, sec_per_shot, session):
    """The ordered block list. Order is the whole point -- see module docstring."""
    b = []

    b.append(dict(id='SETUP', tier='T0', mins=25, shots=0, kind='setup',
                  title='Rig, power, windshields, stand sandbagged',
                  detail='Mic at muzzle height, 90 deg off-axis, never downrange. '
                         'Cable strain-relieved to the stand. Bluetooth OFF.'))

    b.append(dict(id='CAL', tier='T0', mins=8, shots=3, kind='cal',
                  title='Calibration tone x3 levels + SPL meter reading',
                  detail='WRITE THE METER READING DOWN. Without this every level '
                         'in the dataset is relative forever and nothing can be '
                         'compared with anything measured elsewhere.'))

    b.append(dict(id='FLOOR', tier='T0', mins=3, shots=1, kind='cal',
                  title='Noise floor, 60 s, mic covered, nobody talking',
                  detail='Sets the reference every SNR figure is measured against.'))

    b.append(dict(id='IR', tier='T0', mins=18, shots=4, kind='ir',
                  title='Range impulse response: sweep x2 + balloon pops x2',
                  detail='IRREPLACEABLE. The acoustics of this range cannot be '
                         'recovered later from anything else. Balloons are the '
                         'backup for when wind or traffic ruins the sweep.'))

    b.append(dict(id='GAIN', tier='T0', mins=10, shots=0, kind='check',
                  title='Set gain with record.py --meter on a proxy pop',
                  detail='Target -18 to -12 dBFS on the proxy, then back off '
                         'further for the louder real source.'))

    # Core conditions. The first is the reference everything else hangs off, so
    # it gets the most repeats: the spread of these shots IS the tolerance any
    # later synthetic set has to land inside.
    src0, dist0 = sources[0], distances[0]
    b.append(dict(id='A', tier='T1', mins=repeats * sec_per_shot / 60,
                  shots=repeats, kind='shots', source=src0, distance=dist0,
                  azimuth=azimuths[0],
                  title=f'CORE reference: {src0} @ {dist0} m, {repeats} shots',
                  detail='The primary reference condition. Do not cut this short '
                         'to save time -- with too few shots the spread cannot '
                         'be estimated and no match can be claimed either way.'))

    n2 = max(int(repeats * 0.8), 8)
    if len(distances) > 1:
        b.append(dict(id='B', tier='T1', mins=n2 * sec_per_shot / 60, shots=n2,
                      kind='shots', source=src0, distance=distances[1],
                      azimuth=azimuths[0],
                      title=f'Distance: {src0} @ {distances[1]} m, {n2} shots',
                      detail='Two distances give the propagation behaviour. '
                             'One distance gives a single point and no model.'))

    if len(sources) > 1:
        b.append(dict(id='C', tier='T1', mins=n2 * sec_per_shot / 60, shots=n2,
                      kind='shots', source=sources[1], distance=dist0,
                      azimuth=azimuths[0],
                      title=f'Source: {sources[1]} @ {dist0} m, {n2} shots',
                      detail='A second source type shows what generalises and '
                             'what was specific to the first.'))

    if len(azimuths) > 1:
        n3 = max(int(repeats * 0.6), 8)
        b.append(dict(id='D', tier='T1', mins=n3 * sec_per_shot / 60, shots=n3,
                      kind='shots', source=src0, distance=dist0,
                      azimuth=azimuths[1],
                      title=f'Off-axis: {src0} @ {dist0} m, {azimuths[1]} deg, '
                            f'{n3} shots',
                      detail='Directivity. The blast is not a point source and '
                             'does not radiate evenly.'))

    b.append(dict(id='MECH', tier='T2', mins=12, shots=6, kind='mech',
                  title='Mechanical: bolt cycling, trigger, brass ejection',
                  detail='DRY, no live fire. Close mic, high gain. These are the '
                         'quiet sounds the blast normally buries.'))

    b.append(dict(id='AMB', tier='T3', mins=6, shots=1, kind='amb',
                  title='Range ambience, 5 min continuous, no shots',
                  detail='The stationary background of this site.'))

    b.append(dict(id='SPCH', tier='T3', mins=14, shots=4, kind='speech',
                  title='Speech during live fire + paired quiet reference',
                  detail='Same sentences twice: once during fire, once in a '
                         'pause. The pair is what makes them usable as a '
                         'clean/noisy reference.'))

    b.append(dict(id='FINAL', tier='T0', mins=12, shots=0, kind='check',
                  title='Final sweep: validate every file, review contact sheet',
                  detail='BEFORE you pack up and before anyone leaves. This is '
                         'the last moment a re-shoot is possible.'))
    return b


def make_rows(blocks_, session, sr, bits, holdout_frac):
    rows = []
    for b in blocks_:
        if b['shots'] == 0:
            continue
        for i in range(1, b['shots'] + 1):
            n = b['shots']
            # Hold out the tail of each condition. Decided here, at planning
            # time, so it cannot be quietly chosen later to flatter a result.
            split = 'holdout' if i > n * (1 - holdout_frac) else 'fit'
            rows.append({
                'shot_id': f"{b['id']}-{i:03d}", 'session': session,
                'tier': b['tier'], 'timestamp': '', 'recorder': 'A',
                'gain_setting': '', 'sample_rate_hz': sr, 'bit_depth': bits,
                'weapon_make_model': '', 'caliber': '', 'barrel_length_cm': '',
                'ammo_type': '', 'suppressed': '',
                'distance_m': b.get('distance', ''),
                'azimuth_deg': b.get('azimuth', ''),
                'mic_height_cm': '', 'muzzle_height_cm': '',
                'ground_surface': '', 'clipped': '', 'temp_c': '',
                'humidity_pct': '', 'wind_kmh': '', 'wind_direction': '',
                'split': split if b['kind'] == 'shots' else 'holdout',
                'notes': b.get('source', b['title'][:40]),
            })
    return rows


def runsheet(blocks_, total_min, budget_min, session, rows):
    L = []
    W = 76
    L.append('=' * W)
    L.append(f" ONE-TRIP RANGE RUN SHEET   session {session}")
    L.append(f" Date ____________  Operator ______________  "
             f"Range ________________")
    L.append('=' * W)
    L.append('')
    L.append(" Ordered by what cannot be redone. Work top to bottom.")
    L.append(" Do NOT reorder to 'get the shooting done first' -- without the")
    L.append(" calibration and the impulse response, the shots are unusable.")
    L.append('')
    L.append(f" Planned: {total_min:.0f} min    Slot: {budget_min:.0f} min"
             + ('   FITS' if total_min <= budget_min else '   *** OVER ***'))
    L.append('')

    clock = 0
    for b in blocks_:
        L.append('-' * W)
        L.append(f" [ ]  {b['id']:<6} T+{clock:>3.0f} min   ({b['mins']:.0f} min)"
                 f"   {b['title']}")
        L.append(f"        {b['detail']}")
        if b['shots']:
            L.append(f"        files: {b['id']}-001 .. {b['id']}-{b['shots']:03d}")
        if b['kind'] == 'shots':
            L.append(f"        -> after the first 3: "
                     f"python3 validate.py <file> --expect-events 1")
        clock += b['mins']

    L.append('-' * W)
    L.append('')
    L.append(" HARD RULES")
    L.append("   * validate.py after the first 3 shots of EVERY block, and after")
    L.append("     any change of gain, distance, mic position or source.")
    L.append("   * NO-GO means stop and fix. Never 'carry on and fix later'.")
    L.append("   * Log temp / humidity / wind at the start and end of each block.")
    L.append("   * Never delete a take. A bad take is data about what went wrong.")
    L.append('')
    L.append(" WEATHER LOG        start            middle           end")
    L.append("   temp C           ______           ______           ______")
    L.append("   humidity %       ______           ______           ______")
    L.append("   wind km/h        ______           ______           ______")
    L.append("   wind direction   ______           ______           ______")
    L.append('')
    fit = sum(1 for r in rows if r['split'] == 'fit')
    hold = len(rows) - fit
    L.append(f" Planned events: {len(rows)}   fit {fit}   holdout {hold}")
    L.append(" The holdout is decided HERE, before any data exists. Do not look")
    L.append(" at it while building anything that will later be tested on it.")
    L.append('=' * W)
    return '\n'.join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', default='rangeplan')
    ap.add_argument('--name', '--session', default='S1', dest='name',
                    help='session label used in shot ids (--session accepted)')
    ap.add_argument('--hours', type=float, default=3.5,
                    help='working time you actually have at the range')
    ap.add_argument('--sources', default='air_rifle,firecracker_medium')
    ap.add_argument('--distances', default='5,10')
    ap.add_argument('--azimuths', default='90,45')
    ap.add_argument('--repeats', type=int, default=15,
                    help='shots in the core reference condition')
    ap.add_argument('--sec-per-shot', type=float, default=60.0,
                    help='realistic seconds per shot including logging')
    ap.add_argument('--holdout', type=float, default=0.3,
                    help='fraction of each condition reserved as holdout')
    ap.add_argument('--sr', type=int, default=96000)
    ap.add_argument('--bits', type=int, default=24)
    args = ap.parse_args()

    sources = [s.strip() for s in args.sources.split(',') if s.strip()]
    distances = [float(d) for d in args.distances.split(',') if d.strip()]
    azimuths = [int(a) for a in args.azimuths.split(',') if a.strip()]
    if not sources or not distances:
        print("ERROR: need at least one source and one distance", file=sys.stderr)
        return 2

    b = blocks(sources, distances, args.repeats, azimuths,
               args.sec_per_shot, args.name)
    total = sum(x['mins'] for x in b)
    budget = args.hours * 60
    rows = make_rows(b, args.name, args.sr, args.bits, args.holdout)

    os.makedirs(args.out, exist_ok=True)
    sheet = runsheet(b, total, budget, args.name, rows)
    sp = os.path.join(args.out, 'RUN_SHEET.txt')
    with open(sp, 'w') as f:
        f.write(sheet + '\n')

    cp = os.path.join(args.out, f'metadata_{args.name}.csv')
    with open(cp, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=META_COLS)
        w.writeheader()
        w.writerows(rows)

    print(f"\n  {'block':<8} {'min':>5}  {'shots':>6}  title")
    print(f"  {'-'*8} {'-'*5}  {'-'*6}  {'-'*44}")
    for x in b:
        print(f"  {x['id']:<8} {x['mins']:>5.0f}  {x['shots']:>6}  {x['title'][:44]}")
    print(f"  {'-'*8} {'-'*5}  {'-'*6}")
    print(f"  {'TOTAL':<8} {total:>5.0f}  {sum(x['shots'] for x in b):>6}")

    print(f"\n  slot {budget:.0f} min", end='  ')
    if total > budget:
        over = total - budget
        print(f"*** PLAN IS {over:.0f} MIN OVER ***")
        print(f"\n  Cut in this order -- last first, because the top of the list\n"
              f"  is what cannot be recovered on another day:\n"
              f"    1. drop the off-axis block (D)\n"
              f"    2. drop the second source (C)\n"
              f"    3. shorten speech and mechanical\n"
              f"  Do NOT cut calibration, the impulse response, or the core\n"
              f"  reference block. Without those the trip produces nothing\n"
              f"  usable, however many rounds were fired.")
    else:
        print(f"fits, {budget - total:.0f} min spare (you will need it)")

    fit = sum(1 for r in rows if r['split'] == 'fit')
    print(f"\n  {len(rows)} planned events   fit {fit}   holdout {len(rows)-fit}")
    print(f"\n  -> {sp}   <- PRINT THIS")
    print(f"  -> {cp}\n")
    return 0


if __name__ == '__main__':
    sys.exit(main())
