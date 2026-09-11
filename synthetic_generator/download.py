#!/usr/bin/env python3
"""download.py -- ZEIT corpus downloader.

    python3 download.py /Volumes/ZEIT

Keys while running:   p = pause    r = resume    q = quit (safe, resumable)

One folder per dataset. Everything resumable -- kill it, rerun it, it picks up
mid-file. Each folder gets a SOURCE.txt saying where the data came from, what is
inside, and under what licence.
"""
import os, sys, time, threading, termios, tty, select, shutil, collections
import urllib.request, urllib.error, tarfile, zipfile

W = 100   # line width to clear

# (n, class, short, full name, [urls] or [], size_mb, licence, description)
D = [
 (1,"speech","LibriSpeech_OpenSLR","LibriSpeech_OpenSLR",[
   "https://www.openslr.org/resources/12/train-clean-100.tar.gz",
   "https://www.openslr.org/resources/12/dev-clean.tar.gz",
   "https://www.openslr.org/resources/12/test-clean.tar.gz",
   "https://www.openslr.org/resources/12/train-clean-360.tar.gz",
  ],30000,"CC BY 4.0",
  "Clean English read speech -- the clean half of every training pair.\n"
  "  train-clean-100  100 h, 251 speakers   (start here)\n"
  "  train-clean-360  360 h                 (optional bulk)\n"
  "  dev-clean          5.4 h validation\n"
  "  test-clean         5.4 h test -- never train on this"),

 (2,"speech","LombardGRID_Sheffield","Audio-Visual Lombard Grid corpus",[],2000,"free for research",
  "54 talkers x 100 utterances = 50 Lombard + 50 plain, PAIRED.\n"
  "People shout differently in noise; a neutral-trained model loses ~5 dB on this.\n"
  "GET IT: https://spandh.dcs.shef.ac.uk/avlombard/"),

 (3,"speech","SPRINGINX_IITM","SPRING-INX (IIT Madras)",[],200000,"open, see paper",
  "~2000 h, 10 Indian languages incl. Hindi, manually transcribed.\n"
  "Funded by MeitY, Govt of India, under the National Language Translation Mission.\n"
  "GET IT: see arXiv 2310.14654 for the access link"),

 (4,"noise","MUSAN_OpenSLR","MUSAN noise + speech + music",[
   "https://www.openslr.org/resources/17/musan.tar.gz"],11000,"CC BY 4.0",
  "109 h. Built for augmentation: technical noise, babble, music."),

 (5,"noise","NOISEX92_SPIB","NOISEX-92",[],50,"research use",
  "15 noises x 235 s. THE military one: leopard tank, m109 tank, F-16 cockpit,\n"
  "machine gun, factory, babble, HF radio channel, pink, white.\n"
  "Smallest and most valuable download on this list -- do it first.\n"
  "GET IT: https://spib.linse.ufsc.br/noise.html"),

 (6,"noise","ESC50_GitHub","ESC-50 environmental sounds",[
   "https://github.com/karolpiczak/ESC-50/archive/master.zip"],600,"CC BY-NC 3.0",
  "2000 clips x 5 s, 50 classes. helicopter, train, wind, rain, siren."),

 (7,"noise","DEMAND_Zenodo","DEMAND multichannel environmental noise",[],6000,"CC BY-SA 3.0",
  "18 real environments x 16 channels. kitchen, office, cafe, town square, car, metro.\n"
  "GET IT: Zenodo, search \"DEMAND noise\""),

 (8,"noise","UrbanSound8K_NYU","UrbanSound8K_NYU",[],6000,"CC BY-NC 3.0",
  "8732 clips. siren, engine idling, jackhammer, drilling.\n"
  "NON-COMMERCIAL licence -- fine for the competition, not for a shipped product.\n"
  "GET IT: https://urbansounddataset.weebly.com"),

 (9,"noise","TAUUrban_Zenodo","TAU Urban Acoustic Scenes",[],30000,"CC BY-NC",
  "metro, metro_station, tram, bus, street_traffic, park, airport.\n"
  "GET IT: Zenodo, search \"TAU Urban Acoustic Scenes\""),

 (10,"noise","FSD50K_Zenodo","FSD50K_Zenodo",[],30000,"CC BY / CC0 mix",
  "51197 clips, 200 classes. gunshot, explosion, siren, engine.\n"
  "GET IT: Zenodo, search FSD50K"),

 (11,"gunshot","ZenodoGuns_Zenodo","Zenodo Gunshot/Gunfire Audio Dataset",[
   "https://zenodo.org/records/7004819/files/edge-collected-gunshot-audio.zip?download=1"],
  1495,"CC BY 4.0",
  "2148 real gunshots, 4 firearms, multi-orientation, edge devices at an outdoor range.\n"
  "Source page: https://zenodo.org/records/7004819"),

 (12,"gunshot","Cadre_GunshotForensics","Cadre Gunshot Audio Forensics Dataset",[],5000,"NIJ / research use",
  "~10,000 recordings. 20 firearms x 20 positions x 4 devices, rural Arizona 2017.\n"
  "The 20 positions are the azimuth/distance grid our own field checklist asks for.\n"
  "GET IT: https://cadreforensics.com/audio/"),

 (13,"military","MAD_Kaggle","Military Audio Dataset",[],1500,"CC BY 4.0",
  "8075 clips, 12 h, 16 kHz. Almost exactly the PS's noise list:\n"
  "  gunshot 1714 | shelling 1173 | communication 1150 | vehicle 1123\n"
  "  helicopter 1009 | fighter 985 | footsteps 921\n"
  "GET IT: figshare c.7001919.v1  --  links at github.com/kaen2891/military_audio_dataset"),

 (14,"drone","DroneAudioSet_HF","DroneAudioSet_HF",[],15000,"MIT",
  "23.5 h of drone audio, systematically collected.\n"
  "GET IT: https://huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/"),

 (15,"drone","DREGON_Inria","DREGON drone ego-noise dataset",[],10000,"research use",
  "8-channel mic array mounted ON a quadrotor, 44.1 kHz, with per-rotor rps.\n"
  "Captures ego-noise the way a headset captures the wearer's own environment.\n"
  "GET IT: https://dregon.inria.fr/datasets/dregon/"),

 (16,"rir","OpenSLR28_RIRs","RIRs and Noises",[
   "https://www.openslr.org/resources/28/rirs_noises.zip"],4000,"Apache 2.0",
  "Real + simulated room impulse responses. Convolve a dry sound to place it in a room."),
]

PAUSED = threading.Event(); QUIT = threading.Event()
LOGPATH = '/tmp/zeit_download.log'
EXTRACT = True
def folder_for(root, cls, short):
    """Exact folder, or an existing one that starts with the same name.

    People rename folders to add a source ("MUSAN" -> "MUSAN- OpenSLR"). Without
    this the script would not find them, would make a fresh empty folder, and
    would download everything a second time. That happened once; it does not
    happen again.
    """
    exact = os.path.join(root, short)
    if os.path.isdir(exact):
        return exact
    if os.path.isdir(root):
        base = short.split('_')[0].lower()
        for e in sorted(os.listdir(root)):
            if not os.path.isdir(os.path.join(root, e)) or e.startswith('.'):
                continue
            if e.lower().replace(' ', '').replace('-', '').replace('_', '').startswith(base):
                return os.path.join(root, e)
    return exact

def keywatch():
    if not sys.stdin.isatty(): return
    fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while not QUIT.is_set():
            if select.select([sys.stdin],[],[],0.2)[0]:
                c = sys.stdin.read(1).lower()
                if c=='p': PAUSED.set()
                elif c=='r': PAUSED.clear()
                elif c=='q': QUIT.set(); PAUSED.clear()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def human(n):
    for u in ('B','KB','MB','GB'):
        if n < 1024: return f"{n:.0f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

def hms(s):
    if s is None or s!=s or s<0 or s>86400*7: return "--:--"
    s=int(s)
    return f"{s//3600}:{(s%3600)//60:02d}:{s%60:02d}" if s>=3600 else f"{s//60}:{s%60:02d}"

def bar(f, w=32):
    f=max(0.0,min(1.0,f)); n=int(f*w)
    return "["+"#"*n+"-"*(w-n)+f"] {f*100:5.1f}%"

def line(txt):
    sys.stdout.write("\r" + txt + "\033[K"); sys.stdout.flush()

def download(url, path, tag):
    tmp = path + ".part"
    have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    req = urllib.request.Request(url, headers={'User-Agent':'zeit/1.0'})
    if have: req.add_header('Range', f'bytes={have}-')
    try:
        r = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code==416 and have: os.rename(tmp,path); return True
        line(f"   {tag}  HTTP {e.code} -- skipped"); print(); return False
    except Exception as e:
        line(f"   {tag}  {type(e).__name__} -- skipped"); print(); return False

    size = r.headers.get('Content-Length')
    total = (int(size)+have) if size else None
    win = collections.deque(maxlen=40)      # rolling window: (time, bytes)
    done = have; t_first = time.time()
    win.append((time.time(), done))
    with open(tmp,'ab') as f:
        while not QUIT.is_set():
            while PAUSED.is_set() and not QUIT.is_set():
                line("   || PAUSED   --   r = resume    q = quit")
                time.sleep(0.3)
                win.clear(); win.append((time.time(), done))
            chunk = r.read(262144)
            if not chunk: break
            f.write(chunk); done += len(chunk)
            now = time.time(); win.append((now, done))
            if now - win[0][0] > 0.5:
                sp = (done - win[0][1]) / (now - win[0][0])
                eta = (total-done)/sp if (total and sp>1) else None
                line(f"   {tag} {bar(done/total if total else 0)}  "
                     f"{human(done)}{'/'+human(total) if total else ''}  "
                     f"{human(sp)}/s  ETA {hms(eta)}")
    r.close()
    if QUIT.is_set():
        line("   stopped -- rerun to resume"); print(); return False
    os.rename(tmp, path)
    line(f"   {tag} {bar(1.0)}  {human(done)}  in {hms(time.time()-t_first)}"); print()
    return True

ST = {}          # slot -> dict(name, folder, done, total, speed, state)
ST_LOCK = threading.Lock()


def unpack(path, fold, key):
    """Extract, then flatten redundant single-folder nesting, then stash the archive."""
    try:
        with ST_LOCK: ST[key].update(state='unpack')
        tmpdir = os.path.join(fold, "_unpack")
        if os.path.exists(tmpdir): shutil.rmtree(tmpdir)
        os.makedirs(tmpdir)
        if path.endswith((".tar.gz",".tgz",".tar")):
            with tarfile.open(path) as t: t.extractall(tmpdir)
        elif path.endswith(".zip"):
            with zipfile.ZipFile(path) as z: z.extractall(tmpdir)
        else:
            with ST_LOCK: ST[key].update(state='done'); return

        # flatten: if the archive made exactly one top folder, lift its contents up
        top = [e for e in os.listdir(tmpdir) if not e.startswith('.')]
        src = os.path.join(tmpdir, top[0]) if (len(top)==1 and
              os.path.isdir(os.path.join(tmpdir, top[0]))) else tmpdir
        for e in os.listdir(src):
            if e.startswith('.'): continue
            dst = os.path.join(fold, e)
            if os.path.exists(dst):
                shutil.rmtree(dst) if os.path.isdir(dst) else os.remove(dst)
            shutil.move(os.path.join(src, e), dst)
        shutil.rmtree(tmpdir)

        arch = os.path.join(fold, "_archive"); os.makedirs(arch, exist_ok=True)
        shutil.move(path, os.path.join(arch, os.path.basename(path)))
        with ST_LOCK: ST[key].update(state='done')
    except Exception as e:
        with ST_LOCK: ST[key].update(state=f'unpack fail: {type(e).__name__}')

def worker(q, root):
    while not QUIT.is_set():
        try: item = q.pop(0)
        except IndexError: return
        n, cls, short, full, url = item
        fold = folder_for(root, cls, short)
        name = os.path.basename(url.split('?')[0])
        key = f"{short}/{name}"
        path = os.path.join(fold, name)
        arch = os.path.join(fold, "_archive", name)
        if os.path.exists(arch):
            with ST_LOCK: ST[key] = dict(done=1, total=1, speed=0, state='have')
            continue
        if os.path.exists(path):
            with ST_LOCK: ST[key] = dict(done=1, total=1, speed=0, state='unpack')
            if EXTRACT: unpack(path, fold, key)
            else:
                with ST_LOCK: ST[key]['state'] = 'have'
            continue
        with ST_LOCK: ST[key] = dict(done=0, total=None, speed=0, state='start')
        for attempt in range(4):
            try:
                pull(url, path, key); break
            except OSError as e:
                with ST_LOCK: ST[key].update(state=f'disk error, retry {attempt+1}/4')
                time.sleep(3 * (attempt + 1))
            except Exception as e:
                with ST_LOCK: ST[key].update(state=f'{type(e).__name__}'); break
        with ST_LOCK: st = ST[key]['state']
        if st == 'done' and EXTRACT: unpack(path, fold, key)

def logline(msg):
    try:
        with open(LOGPATH, 'a') as f:
            f.write(f"{time.strftime('%F %T')}  {msg}\n")
    except Exception:
        pass

def pull(url, path, key):
    tmp = path + ".part"
    have = os.path.getsize(tmp) if os.path.exists(tmp) else 0
    logline(f"START {key}  resuming from {human(have)}")
    req = urllib.request.Request(url, headers={'User-Agent':'zeit/1.0'})
    if have: req.add_header('Range', f'bytes={have}-')
    try:
        r = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code == 416 and have:
            # 416 means the server thinks we already have it all -- verify before trusting
            try:
                h = urllib.request.urlopen(urllib.request.Request(
                    url, method='HEAD', headers={'User-Agent':'zeit/1.0'}), timeout=30)
                exp = int(h.headers.get('Content-Length') or 0)
            except Exception:
                exp = 0
            if exp and have == exp:
                os.rename(tmp, path)
                with ST_LOCK: ST[key].update(state='have', done=exp, total=exp)
            elif exp:
                # we KNOW the expected size and ours does not match -- only now is
                # deleting safe, and even then keep a copy rather than lose bytes
                os.replace(tmp, tmp + '.bad')
                with ST_LOCK: ST[key].update(state='size mismatch, will redo')
            else:
                # HEAD failed, so we do NOT know the size. Never throw away a
                # partial file on a guess -- keep it and try again next run.
                with ST_LOCK: ST[key].update(state='size unknown -- kept, rerun')
            return
        with ST_LOCK: ST[key].update(state=f'HTTP {e.code}'); return
    except Exception as e:
        r = getattr(e, 'reason', e)
        msg = str(r)
        if 'not known' in msg or 'Name or service' in msg or 'nodename' in msg:
            msg = 'DNS FAIL -- try: sudo networksetup -setdnsservers Wi-Fi 8.8.8.8 1.1.1.1'
        with ST_LOCK: ST[key].update(state=msg[:46]); return

    size = r.headers.get('Content-Length')
    if have and r.status == 200:
        # server ignored the Range header -- appending would corrupt the file
        os.replace(tmp, tmp + '.bad'); have = 0
        with ST_LOCK: ST[key].update(state='no range support, restarting')
    total = (int(size) + have) if size else None
    win = collections.deque(maxlen=40); done = have
    win.append((time.time(), done))
    with ST_LOCK: ST[key].update(total=total, done=done, state='dl')
    with open(tmp, 'ab') as f:
        while not QUIT.is_set():
            while PAUSED.is_set() and not QUIT.is_set():
                with ST_LOCK: ST[key]['state'] = 'paused'
                time.sleep(0.3); win.clear(); win.append((time.time(), done))
            chunk = r.read(262144)
            if not chunk: break
            f.write(chunk); done += len(chunk)
            now = time.time(); win.append((now, done))
            dt = now - win[0][0]
            sp = (done - win[0][1]) / dt if dt > 0.25 else 0.0
            with ST_LOCK: ST[key].update(done=done, speed=sp, state='dl')
    r.close()
    if QUIT.is_set():
        with ST_LOCK: ST[key]['state'] = 'stopped'; return
    if total and done != total:
        with ST_LOCK: ST[key].update(state=f'short {human(done)}/{human(total)} -- will resume')
        return
    os.rename(tmp, path)
    logline(f"DONE  {key}  {human(done)}")
    with ST_LOCK: ST[key].update(state='done', done=total or done, total=total or done)

def render(nlines_prev):
    with ST_LOCK: snap = dict(ST)
    cols = max(60, shutil.get_terminal_size((100, 30)).columns - 1)
    rows = []
    tot_done = tot_all = tot_sp = 0
    for key, v in snap.items():
        d, t, sp, st = v['done'], v['total'], v['speed'], v['state']
        if t: tot_done += d; tot_all += t
        if st == 'dl': tot_sp += sp
        short = key if len(key) <= 42 else key[:20] + ".." + key[-20:]
        if st in ('done', 'have'):
            body = f"{bar(1.0,18)}  complete"
        elif st == 'paused':
            body = "|| PAUSED".ljust(28)
        elif st == 'unpack':
            body = f"{bar(1.0,18)}  unpacking..."
        elif st == 'dl':
            eta = (t - d) / sp if (t and sp > 1) else None
            body = (f"{bar(d/t if t else 0,18)} {human(d):>7}/{human(t) if t else '?':<7}"
                    f" {human(sp):>7}/s {hms(eta):>7}")
        else:
            body = f"{'':18}  {st}"
        rows.append(f"  {short:<42} {body}"[:cols])
    if tot_all:
        eta = (tot_all - tot_done) / tot_sp if tot_sp > 1 else None
        rows.append("")
        rows.append((f"  TOTAL {bar(tot_done/tot_all,24)} {human(tot_done)}/{human(tot_all)}"
                     f"  {human(tot_sp)}/s  ETA {hms(eta)}   [p]ause [r]esume [q]uit")[:cols])
    if nlines_prev: sys.stdout.write(f"\033[{nlines_prev}A")
    for r_ in rows: sys.stdout.write("\r" + r_ + "\033[K\n")
    sys.stdout.flush()
    return len(rows)

def main():
    if len(sys.argv)<2:
        print(__doc__); print("  plug the SSD in, then:  ls /Volumes"); return 1
    dest = sys.argv[1]
    if not os.path.isdir(dest): print(f"not found: {dest}"); return 1
    root = os.path.join(dest,"zeit-data"); os.makedirs(root, exist_ok=True)
    global LOGPATH
    LOGPATH = os.path.join(root, "_download.log")
    jobs = 3
    if "--jobs" in sys.argv: jobs = int(sys.argv[sys.argv.index("--jobs")+1])
    global EXTRACT
    if "--no-extract" in sys.argv: EXTRACT = False

    auto = [d for d in D if d[4]]; man = [d for d in D if not d[4]]
    n_files = sum(len(d[4]) for d in auto)
    print("="*W)
    print("  ZEIT corpus downloader")
    print(f"  destination : {root}")
    print(f"  free space  : {human(shutil.disk_usage(dest).free)}")
    print(f"  automatic   : {len(auto)} datasets / {n_files} archives, ~{sum(d[5] for d in auto)/1024:.1f} GB")
    print(f"  manual      : {len(man)} datasets (folders + SOURCE.txt will be made)")
    print(f"  parallel    : {jobs} at a time")
    print(f"  extract     : {'yes -- archives unpacked, nesting flattened, zip moved to _archive/' if EXTRACT else 'no'}")
    print("  keys        : p = pause    r = resume    q = quit (resumable)")
    print("="*W)

    for n,cls,short,full,urls,mb,lic,what in D:
        fold = folder_for(root, cls, short); os.makedirs(fold, exist_ok=True)
        with open(os.path.join(fold,"SOURCE.txt"),"w") as f:
            f.write(f"{full}\n{'='*len(full)}\n\nshort name : {short}\nclass      : {cls}\n"
                    f"licence    : {lic}\nsize       : ~{mb} MB\n"
                    f"files      : {len(urls) if urls else 'MANUAL DOWNLOAD'}\n")
            for u in urls: f.write(f"             {u}\n")
            f.write(f"\nWHAT IS IN HERE\n{what}\n")

    # round-robin across datasets so different folders fill at once
    queue, i = [], 0
    while True:
        added = False
        for n,cls,short,full,urls,mb,lic,what in auto:
            if i < len(urls): queue.append((n,cls,short,full,urls[i])); added = True
        if not added: break
        i += 1

    print(f"\n  starting {len(queue)} archives, {jobs} in parallel...\n")
    n_queued = len(queue)
    ths = [threading.Thread(target=worker, args=(queue, root), daemon=True) for _ in range(jobs)]
    for t in ths: t.start()
    t0 = time.time(); nl = 0
    while any(t.is_alive() for t in ths) and not QUIT.is_set():
        nl = render(nl); time.sleep(0.4)
    render(nl)

    with ST_LOCK: snap = dict(ST)
    ok = sum(1 for v in snap.values() if v['state'] in ('done','have'))
    print("\n"+"="*W)
    print(f"  {ok}/{n_queued} archives complete   elapsed {hms(time.time()-t0)}")
    print(f"\n  BY HAND ({len(man)}) -- open each folder's SOURCE.txt for the link:")
    for n,cls,short,full,urls,mb,lic,what in man:
        star = "   <- do this first, only 50 MB" if short=="NOISEX92_SPIB" else ""
        print(f"    {short:<16} {full}{star}")
    print(f"\n  everything is in: {root}")
    print("="*W)
    QUIT.set(); return 0

if __name__=='__main__':
    threading.Thread(target=keywatch, daemon=True).start()
    try: sys.exit(main())
    except KeyboardInterrupt: QUIT.set(); print("\nstopped -- rerun to resume"); sys.exit(1)
