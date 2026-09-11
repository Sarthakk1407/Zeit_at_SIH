#!/usr/bin/env python3
"""unpack_manual.py -- extract whatever you downloaded by hand.

    python3 unpack_manual.py "/Volumes/ZEIT V.1.0/zeit-data"
    python3 unpack_manual.py "/Volumes/ZEIT V.1.0/zeit-data" --only DEMAND
    python3 unpack_manual.py "/Volumes/ZEIT V.1.0/zeit-data" --dry-run

Walks every dataset folder, finds .zip / .tar.gz / .tgz / .tar, extracts them,
flattens the redundant single-folder nesting an archive usually creates, and
moves the archive into that folder's _archive/ so the data sits at the top.

Skips Chrome's .crdownload files -- those are still downloading.
"""
import argparse, os, shutil, sys, tarfile, zipfile

ARCH = ('.zip', '.tar.gz', '.tgz', '.tar')

def human(n):
    for u in ('B','KB','MB','GB'):
        if n < 1024: return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

def unpack(path, fold, dry):
    name = os.path.basename(path)
    if dry:
        print(f"    would extract  {name}  ({human(os.path.getsize(path))})"); return True
    tmp = os.path.join(fold, "_unpack")
    if os.path.exists(tmp): shutil.rmtree(tmp)
    os.makedirs(tmp)
    try:
        if name.endswith('.zip'):
            with zipfile.ZipFile(path) as z: z.extractall(tmp)
        else:
            with tarfile.open(path) as t: t.extractall(tmp)
    except Exception as e:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"    FAILED  {name}  ({type(e).__name__}) -- redownload this one")
        return False

    top = [e for e in os.listdir(tmp) if not e.startswith('.')]
    src = os.path.join(tmp, top[0]) if (len(top) == 1 and
          os.path.isdir(os.path.join(tmp, top[0]))) else tmp
    moved = 0
    for e in os.listdir(src):
        if e.startswith('.'): continue
        dst = os.path.join(fold, e)
        if os.path.exists(dst):
            shutil.rmtree(dst) if os.path.isdir(dst) else os.remove(dst)
        shutil.move(os.path.join(src, e), dst); moved += 1
    shutil.rmtree(tmp, ignore_errors=True)
    arch = os.path.join(fold, "_archive"); os.makedirs(arch, exist_ok=True)
    shutil.move(path, os.path.join(arch, name))
    print(f"    extracted      {name}  -> {moved} item(s)")
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root')
    ap.add_argument('--only', help='just this dataset folder')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if not os.path.isdir(a.root): print(f"not found: {a.root}"); return 1

    folders = sorted(d for d in os.listdir(a.root)
                     if os.path.isdir(os.path.join(a.root, d)) and not d.startswith('.'))
    if a.only: folders = [d for d in folders if d == a.only]

    total_ok = total_wait = 0
    for d in folders:
        fold = os.path.join(a.root, d)
        items = [f for f in sorted(os.listdir(fold)) if not f.startswith('.')]
        archives = [f for f in items if f.lower().endswith(ARCH)]
        pending  = [f for f in items if f.endswith('.crdownload') or f.endswith('.part')]
        wavs = sum(1 for _, _, fs in os.walk(fold) for f in fs if f.lower().endswith('.wav'))

        if not archives and not pending:
            print(f"  {d:<18} {wavs:>7,} wav   nothing to unpack")
            continue
        print(f"  {d}")
        for p in pending:
            print(f"    still downloading  {p}  ({human(os.path.getsize(os.path.join(fold,p)))})")
            total_wait += 1
        for f in archives:
            if unpack(os.path.join(fold, f), fold, a.dry_run): total_ok += 1
        if not a.dry_run:
            n = sum(1 for _, _, fs in os.walk(fold) for x in fs if x.lower().endswith('.wav'))
            print(f"    now holds {n:,} wav files")

    print(f"\n  {total_ok} archive(s) unpacked" +
          (f", {total_wait} still downloading -- rerun when they finish" if total_wait else ""))
    return 0

if __name__ == '__main__':
    sys.exit(main())
