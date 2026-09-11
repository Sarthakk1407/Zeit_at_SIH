#!/bin/bash
# fetch_all.sh -- download every corpus that has a direct URL, onto an SSD.
#
#   bash fetch_all.sh /Volumes/MySSD              # everything
#   bash fetch_all.sh /Volumes/MySSD --core       # ~40 GB, enough to start training
#   bash fetch_all.sh /Volumes/MySSD --jobs 4     # parallel downloads (default 3)
#
# Resumable: interrupt it, run it again, it picks up where it stopped.
# Skips anything already fully downloaded.

set -uo pipefail

DEST="${1:-}"
shift || true
CORE=0; JOBS=3
while [ $# -gt 0 ]; do
  case "$1" in
    --core) CORE=1 ;;
    --jobs) shift; JOBS="$1" ;;
  esac; shift
done

if [ -z "$DEST" ]; then
  echo "usage: bash fetch_all.sh /Volumes/YourSSD [--core] [--jobs N]"
  echo
  echo "plug the SSD in, then:  ls /Volumes    to find its name"
  exit 1
fi
if [ ! -d "$DEST" ]; then echo "not found: $DEST"; exit 1; fi

ROOT="$DEST/zeit-corpora"
LOG="$ROOT/_download.log"
mkdir -p "$ROOT"/{speech,noise,gunshot,drone,rir,_manual}

free_gb=$(df -g "$DEST" | awk 'NR==2{print $4}')
need=$([ $CORE -eq 1 ] && echo 60 || echo 300)
echo "=============================================================="
echo " destination : $ROOT"
echo " free space  : ${free_gb} GB"
echo " need approx : ${need} GB"
echo " parallel    : $JOBS"
echo "=============================================================="
if [ "$free_gb" -lt "$need" ]; then
  echo " !! not enough free space. Use --core, or a bigger SSD."
  read -p " continue anyway? [y/N] " a; [ "$a" = "y" ] || exit 1
fi
echo

# url | subdir | friendly name | core?
LIST=$(cat <<'EOF'
https://www.openslr.org/resources/12/train-clean-100.tar.gz|speech|LibriSpeech train-clean-100 (6 GB)|1
https://www.openslr.org/resources/12/dev-clean.tar.gz|speech|LibriSpeech dev-clean (337 MB)|1
https://www.openslr.org/resources/12/test-clean.tar.gz|speech|LibriSpeech test-clean (346 MB)|1
https://www.openslr.org/resources/12/train-clean-360.tar.gz|speech|LibriSpeech train-clean-360 (23 GB)|0
https://www.openslr.org/resources/17/musan.tar.gz|noise|MUSAN (11 GB)|1
https://www.openslr.org/resources/28/rirs_noises.zip|rir|RIRs and Noises (4 GB)|1
https://github.com/karolpiczak/ESC-50/archive/master.zip|noise|ESC-50 (600 MB)|1
EOF
)

fetch() {
  IFS='|' read -r url sub name core <<< "$1"
  [ "$CORE" -eq 1 ] && [ "$core" -eq 0 ] && return 0
  local out="$ROOT/$sub/$(basename "$url")"
  local done_marker="$out.complete"
  if [ -e "$done_marker" ]; then echo "  [have] $name"; return 0; fi
  echo "  [get ] $name"
  if curl -L --fail --retry 3 --retry-delay 5 -C - -s -o "$out" "$url"; then
    touch "$done_marker"; echo "  [ ok ] $name"
    echo "$(date +%F\ %T)  OK    $name" >> "$LOG"
  else
    echo "  [FAIL] $name  -- rerun to resume"
    echo "$(date +%F\ %T)  FAIL  $name" >> "$LOG"
  fi
}
export -f fetch; export ROOT LOG CORE

echo "-- automatic downloads --"
echo "$LIST" | xargs -P "$JOBS" -I{} bash -c 'fetch "$@"' _ {}

cat > "$ROOT/_manual/README.txt" <<'MAN'
These need a browser, a form, or a login. Download by hand into this folder.

TIER 1 -- do these first
  NOISEX-92        https://spib.linse.ufsc.br/noise.html
                   50 MB. tank (leopard, m109), F-16, machine gun, babble.
                   Smallest and most valuable download on this list.

  MAD              figshare  c.7001919.v1
                   code/links: github.com/kaen2891/military_audio_dataset
                   8,075 clips, 12 h, 7 classes, CC BY 4.0.

  Zenodo gunshots  https://zenodo.org/records/7004819
                   2,148 real gunshots, 1.6 GB, CC BY 4.0.

  Lombard GRID     https://spandh.dcs.shef.ac.uk/avlombard/
                   54 talkers x (50 Lombard + 50 plain), paired.

TIER 2
  Cadre gunshots   https://cadreforensics.com/audio/
                   ~10,000 recordings, 20 firearms x 20 positions x 4 devices.
  VCTK             Edinburgh DataShare
  DEMAND           Zenodo, search "DEMAND noise"
  UrbanSound8K     https://urbansounddataset.weebly.com   (CC BY-NC)
  TAU Urban        Zenodo, search "TAU Urban Acoustic Scenes"  (CC BY-NC)
  FSD50K           Zenodo
  DREGON           https://dregon.inria.fr/datasets/dregon/
  DroneAudioSet    https://huggingface.co/datasets/ahlab-drone-project/DroneAudioSet/
  SPRING-INX       see arXiv 2310.14654 for the access link (~2000 h Hindi+)
MAN

echo
echo "=============================================================="
echo " automatic downloads finished."
echo " still to do by hand:  $ROOT/_manual/README.txt"
echo " log:                  $LOG"
df -h "$DEST" | awk 'NR==2{print "  free now: "$4}'
echo "=============================================================="
