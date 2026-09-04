# Kya record kar rahe hain, kaise, aur kyun

Ek trip hai. Ye document wo poori list hai jo us trip se nikalni chahiye — har
quantity, uska unit, wo kis tool se aati hai, aur agar wo chhoot gayi toh kya
tootega.

Ek rule sabse upar: **jo cheez range pe measure nahi hui, wo baad mein banayi
nahi ja sakti.** Har missing item ke saamne likha hai ki uske bina kya
impossible ho jaata hai.

---

## 1. Raw signal — kis settings pe record ho raha hai

Ye pehle set karna hai, kyunki galat setting pe recorded file baad mein theek
nahi hoti.

| Setting | Value | Kyun |
|---|---|---|
| Sample rate | 96 kHz | 48 kHz tak ka content milta hai. Gunshot mein 20 kHz ke upar bhi asli energy hoti hai — 44.1/48 kHz pe wo hissa hamesha ke liye chala jaata hai |
| Bit depth | 24-bit | ~144 dB theoretical range. Gunshot ka crest factor bahut bada hai; 16-bit mein quiet detail floor mein doob jaati hai |
| Format | Uncompressed WAV | MP3/AAC transient ko smear karte hain — jo cheez measure kar rahe hain wahi kharab ho jaati hai |
| Limiter / AGC | **OFF** | Peak ko compress karta hai. Peak hi wo ek number hai jiske liye poori trip ho rahi hai |
| Low-cut / HPF | **OFF** | Blast wave ka LF content chahiye. Wind ke liye windshield, filter nahi |
| Channels | 2 (staggered gain) | Ek hi gain pe ~100 dB span capture nahi hota. Section 6 dekh |

---

## 2. Level — decibel wali family

Ye sab `analyze.py` nikalta hai. **Calibration ke bina ye sab dBFS mein aate
hain (relative), dB SPL mein nahi (absolute).**

| # | Quantity | Unit | Kya hai |
|---|---|---|---|
| 1 | **Peak SPL** | dB re 20 µPa | Sabse loud instantaneous pressure. Impulse noise ka primary number. Unweighted (Z), A-weighted nahi |
| 2 | **SEL** (Sound Exposure Level) | dB | Poore event ki energy, 1 second pe normalize ki hui. Isse alag-alag duration ke events fairly compare hote hain |
| 3 | **Leq** | dB | Event window pe average level |
| 4 | **Crest factor** | dB | Peak ÷ RMS. Kitna "spiky" hai. Gunshot ka crest bahut bada hota hai — yahi wo cheez hai jo normal audio processing ko todti hai |
| 5 | **Noise floor** | dBFS / dB SPL | Wo reference jiske against har SNR measure hota hai |

**Peak aur SEL dono kyun?** Peak batata hai kitna loud tha, SEL batata hai kitni
energy thi. Ek chhota tez crack aur ek lamba boom ka peak same ho sakta hai par
SEL bilkul alag. Sirf ek record karega toh aadhi picture milegi.

---

## 3. Frequency — "frequency" ka matlab yahan

Ye wo hissa hai jo tune specifically poocha. Ek number nahi hai, paanch cheezein
hain:

| # | Quantity | Unit | Kya hai |
|---|---|---|---|
| 6 | **1/3-octave spectrum** | dB per band, ~30 bands (25 Hz – 20 kHz) | **Ye asli reference curve hai.** Poori frequency shape. Baad mein comparison isi pe hoga |
| 7 | **Spectral centroid** | Hz | Energy ka "centre of mass". Ek number mein brightness |
| 8 | **95% rolloff** | Hz | Jiske neeche 95% energy hai. Bandwidth ka measure |
| 9 | **Peak frequency** | Hz | Jahan sabse zyada energy hai |
| 10 | **Band energy split** | dB (4 bands) | <100 Hz / 100–1k / 1k–8k / >8k. Coarse par seedha samajh aane wala |

**#6 sabse important hai.** Baaki chaar us curve ke summary hain. Jab baad mein
synthetic banega, judges ko wahi curve dikhega — real ka aur synthetic ka, ek
saath.

---

## 4. Time — event ki shape

Level aur frequency batate hain *kya* aaya. Ye batate hain *kaise* aaya.

| # | Quantity | Unit | Kya hai |
|---|---|---|---|
| 11 | **Rise time** | ms | Peak ke 10% se 90% tak ka time. Kitni tezi se shock aaya. Yahi cheez gunshot ko drum hit se alag karti hai |
| 12 | **A-duration** | ms | Initial positive pressure phase. Classic blast-wave metric, physics se seedha juda hua |
| 13 | **B-duration** | ms | Total time jab envelope peak ke 20 dB ke andar rahi. Impulse noise ka standard duration measure |
| 14 | **Decay tail** | ms | Room kitni der mein sound ko le jaata hai |

Rise time sabse nazuk hai. 96 kHz pe ek sample 10.4 µs ka hai, aur muzzle blast
ka rise ~10–50 µs hota hai — matlab tu us edge ko sirf kuch samples se resolve
kar raha hai. Isliye sample rate pe compromise nahi.

---

## 5. Room aur environment

| # | Quantity | Unit | Kis se | Chhoot gaya toh |
|---|---|---|---|---|
| 15 | **Impulse response** | waveform | sweep ya balloon | Range ki acoustics kabhi reproduce nahi hogi |
| 16 | **RT60 per octave band** | s | IR se | Reverberation model nahi banega |
| 17 | **Direct-to-noise** | dB | IR se | Pata nahi chalega ki RT60 trustworthy hai ya noise fit kar raha hai |
| 18 | **Calibration scale** | Pa per full scale | cal tone + SPL meter | **Saare levels relative reh jaayenge, permanently** |

---

## 6. Metadata — likhna padta hai, tool nahi nikaal sakta

Ye sabse zyada ignore hone wala hissa hai aur sabse zyada mehnga bhi.

| # | Field | Kyun zaroori |
|---|---|---|
| 19 | distance_m | Spherical spreading loss isi se set hota hai |
| 20 | azimuth_deg | Blast point source nahi hai, har direction mein barabar nahi jaata |
| 21 | mic_height_cm, muzzle_height_cm | Ground reflection inse banti hai — aur wo spectrum mein comb filtering dikhati hai |
| 22 | ground_surface | Reflection ka coefficient. Concrete aur ghaas bilkul alag |
| 23 | temp_c, humidity_pct | HF air absorption. Section 8 dekh |
| 24 | wind_kmh, wind_direction | Wind noise aur propagation dono |
| 25 | recorder, gain_setting, mic model | Gain badla toh calibration void ho gayi |
| 26 | source type, ammo, barrel_length_cm | Kya fire hua |
| 27 | **split (fit / holdout)** | Section 9 dekh — ye tere result ko attack se bachata hai |

---

## 7. Capture kaise karna hai — order matters

Order random nahi hai. **Jo cheez dobara nahi ho sakti wo pehle.**

| # | Block | Time | Tool |
|---|---|---|---|
| 1 | Rig, windshield, stand sandbag, Bluetooth OFF | 25 min | — |
| 2 | Calibration tone ×3 + SPL meter reading | 8 min | `calibrate.py` |
| 3 | Noise floor, 60 s, mic covered | 3 min | `validate.py` |
| 4 | Range IR: sweep ×2 + balloon ×2 | 18 min | `ir_extract.py` |
| 5 | Gain set on a proxy pop | 10 min | `record.py --meter` |
| 6 | **Core reference block** — 15 shots | 15 min | `record.py` → `validate.py` |
| 7 | Second distance — 12 shots | 12 min | ditto |
| 8 | Second source — 12 shots | 12 min | ditto |
| 9 | Off-axis angle — 9 shots | 9 min | ditto |
| 10 | Mechanical (dry, no live fire) | 12 min | ditto |
| 11 | Ambience 5 min | 6 min | ditto |
| 12 | Speech during fire + paired quiet | 14 min | ditto |
| 13 | Final validate sweep + contact sheet | 12 min | `validate.py`, `quicklook.py` |

Total ~156 min. `plan.py` ye sheet aur pre-filled CSV dono generate karta hai:

```bash
python3 plan.py --out rangeplan/ --hours 3.5
lpr rangeplan/RUN_SHEET.txt
```

Agar time kam pad raha ho toh **neeche se kaato** — off-axis, phir second
source, phir speech/mechanical chhota karo. Calibration, IR aur core reference
block kabhi mat kaatna. Unke bina trip se kuch usable nahi nikalta, chahe
kitni bhi rounds chali hon.

**Har block ke pehle 3 shots ke baad `validate.py` chalao.** NO-GO aaya toh
wahin rukna hai. "Baad mein theek kar lenge" is trip pe exist nahi karta.

---

## 8. Wo paanch points, dhang se

### Calibration tone

WAV file mein numbers hain, −1 se +1 ke beech. Un numbers ka koi physical
matlab nahi hai jab tak tu na jaane ki "1.0" ka matlab kitna pressure hai.
Calibration tone + SPL meter reading wahi conversion deta hai.

Iske bina tu keh sakta hai "ye usse 6 dB louder hai". Tu kabhi nahi keh sakta
"ye 152 dB SPL hai". Aur kisi aur ke measurement se, ya physics-based synthetic
model se, compare karna impossible ho jaata hai — kyunki unke paas absolute
units hain aur tere paas nahi.

**Gain badal diya toh calibration void.** Naye gain pe naya tone record karo.

### Geometry likhna

Synthesize karne ke liye model banana padta hai. Model banane ke liye pata hona
chahiye ki *kis cheez ka* model bana rahe ho.

- **Distance** → spherical spreading loss set karta hai
- **Height + ground surface** → ground reflection, jo spectrum mein comb
  filtering banati hai (ek bahut visible feature)
- **Azimuth** → directivity

Ye nahi likha toh tere paas audio hoga jise tu reproduce nahi kar sakta. File
sunne mein theek lagegi aur scientifically bekaar hogi.

### Range IR

Jo tu record kar raha hai wo gunshot **nahi** hai. Wo gunshot *convolved with
the range* hai. Dono alag karne ke liye IR chahiye.

Aur IR baad mein measure nahi ho sakti, kyunki range ki acoustics sirf range pe
hi exist karti hai. Sweep pehle, balloon backup — dono.

### Temp aur humidity

Hawa high frequencies ko absorb karti hai, aur absorption coefficient humidity
aur temperature pe **strongly** depend karta hai. 10 kHz pe 10 m distance pe,
30% aur 80% humidity ka farq kai dB ka hota hai.

Aur HF wahi hissa hai jahan synthetic gunshot sabse zyada galat hota hai. Agar
temp/humidity log nahi kiya, toh jab synthetic HF mein mismatch dikhega, tu
bata hi nahi paayega ki wo tere generator ki galti hai ya us din ki hawa ki.

### Repeats — "10+ shots" kyun

Ye sabse non-obvious hai. "Synthetic real se match karta hai" claim karne ke
liye ek **tolerance** chahiye. Tolerance kya hai? Real cheez ka apna natural
variation, matlab uska standard deviation.

Problem: std khud ek estimate hai, aur kam samples pe wo estimate bahut
kharab hota hai. Simulate karke check kiya:

| Shots (n) | Tera std kitna galat ho sakta hai |
|---|---|
| 3 | ±46% |
| 5 | ±34% |
| 10 | ±23% |
| 15 | ±19% |
| 20 | ±16% |
| 30 | ±13% |

3 shots pe tera "tolerance" khud ±46% uncertain hai — matlab wo tolerance hai
hi nahi. Us se compare karke "match ho gaya" ya "nahi hua", dono statements
meaningless hain, kyunki dono unfalsifiable hain.

**10 se kam pe mat jaana. 15 core condition ke liye behtar hai.**

Isliye: **kam conditions par har ek pe zyada repeats** — ye zyada conditions par
3-3 shots se hamesha behtar hai. Agar time kam pad raha hai, conditions kaato,
repeats nahi.

---

## 9. Holdout — apne result ko attack-proof banana

Metadata CSV mein `split` column hai: `fit` aur `holdout`.

Agar tu synthetic generator ko saare real data pe tune karega, phir usi real
data se compare karega — wo **circular** hai. Jo bhi thoda tez judge hoga wo
sabse pehle yahi poochega, aur tere paas jawab nahi hoga.

Isliye kuch events aise rakh jinhe tu generator banate waqt **dekhega hi
nahi**. `plan.py` ye split planning time pe assign kar deta hai — data exist
karne se pehle. Baad mein choose karna hi wo problem hai jise ye rok raha hai.

---

## 10. Ek gain pe sab kyun nahi aata

| Component | Approx SPL |
|---|---|
| Muzzle blast peak | 140–155 dB |
| Early reflections | 120–140 dB |
| Reverberation tail | 70–100 dB |
| Brass ejection, bolt, trigger | 55–85 dB |
| Uske neeche noise floor | 30–45 dB |

Ek hi event mein **~100 dB ka span**. Gain blast ke liye set karo toh mechanical
sounds floor mein; mechanical ke liye set karo toh blast rails pe.

Solution: **staggered-gain array** — do channels, 18–24 dB alag, sample-aligned.

```bash
python3 record.py --meter --device N --channels 2   # gain set karo
python3 record.py --device N --channels 2 --out S1_A_001.wav
python3 validate.py S1_A_001.wav --array --expect-events 1
```

`--array` isliye zaroori hai: array mein hot channel ka clip hona **expected**
hai, failure nahi — jab tak cold channel ne peak pakad liya ho. Iske bina
validate har take ko fail karega aur tu warnings ignore karna seekh jaayega.

Mechanical sounds alag se record karna — dry cycling, live fire ke bina, close
mic aur high gain pe. Wo blast ke saath ek hi take mein nahi aayenge.

---

## 11. Real data kahan save hoga

Ek trip = ek folder. `python3 session.py init --name S1 --out ~/ANC_data`

| Folder | Kya |
|---|---|
| `00_raw/` | **Asli gunshot audio, poora take.** Kabhi edit nahi hota |
| `03_events/` | **Har shot alag WAV** — `SHOT-001.wav`, `SHOT-002.wav` … yahi compare hoga |
| `04_analysis/features.json` | **Reference signature** — 54 measured quantities |
| `01_calibration/`, `02_ir/` | Calibration aur range acoustics |
| `logs/` | Har take ka validate JSON — audit trail |

Comparison **audio pe nahi hota**. Audio source hai; compare `features.json`
pe hota hai. Baad mein synthetic banega, usi `analyze.py` se measure hoga, aur
do JSON files compare hongi.

## 11b. Audio file bhi milegi — do format mein

**`.wav` khud ek asli playable audio file hai.** macOS use "WAVE audio,
Microsoft PCM, 24 bit, mono 96000 Hz" kehta hai. Double-click karo, chal jaati
hai. Wo "data" nahi hai.

| Format | Kahan | Kaam |
|---|---|---|
| **24-bit WAV** | `00_raw/`, `03_events/` | **Dataset.** Har measurement isi se |
| **AAC .m4a** | `06_listening/` | Sunne, bhejne, slide mein daalne ke liye |

```bash
python3 session.py listen ~/ANC_data/SESSION_S1_20260902
```

Originals ko haath nahi lagta — banane ke baad `verify` abhi bhi
*"Reference intact"* kehta hai. 42.9 MB WAV → 4.5 MB AAC.

### Dataset MP3/AAC mein kyun nahi rakh sakte

Ek asli gunshot event pe measure kiya, 256 kbps AAC:

| Kya | Damage |
|---|---|
| Mid-band levels (31 Hz – 8 kHz) | 0.1 dB — **bilkul theek** |
| Peak level, rise time, B-duration | 0.01 dB / 0.00 ms — theek |
| 32 kHz band | **−83 dB — poora gayab** |
| Spectral centroid | **248 Hz khiska** |

Aakhri do maarti hain:

1. **20 kHz ke upar sab kuch gaya.** AAC 96 kHz carry hi nahi karta — usne
   khud 48 kHz pe downsample kar diya. Teri aadhi bandwidth, aur wahi hissa
   jahan gunshot ka shock content hai.
2. **Centroid 248 Hz khiska, jabki tera asli shot-to-shot sd 1.43 Hz hai.**
   Yaani natural variation se **173 guna**. Us data pe comparison codec ko
   measure karega, gunshot ko nahi.

Sabse khatarnak baat: mid-band aur timing bach jaate hain, matlab **file sunne
mein bilkul sahi lagti hai**. Isliye rule simple hai — sunna `06_listening/`
se, measure hamesha `03_events/` se.

## 12. Reference ko freeze karna — ye tera argument bachata hai

Tera claim hoga: "synthetic real se match karta hai." Judge poochega: *"kaise
pata tera real reference beech mein khiska nahi?"*

```bash
python3 session.py freeze ~/ANC_data/SESSION_S1_20260902   # ek baar, range ke turant baad
python3 session.py verify ~/ANC_data/SESSION_S1_20260902   # har comparison se pehle
```

`freeze` do cheezon ka SHA-256 rakhta hai:

1. **Har audio file aur features.json** — data badla toh pata chalega
2. **Measurement engine khud** (`analyze.py`, `dsp.py`, `wavio.py`) — kyunki
   modified engine dobara chalane se numbers badal jaayenge bina ek bhi audio
   file chhue

Dono test kiye:

- Ek shot ko 0.2 dB quieter kiya (kaan se pata hi nahi chalta) →
  `*** 1 REFERENCE FILE(S) CHANGED ***`
- `analyze.py` mein ek blank line add ki, audio ko haath nahi lagaya →
  `*** MEASUREMENT ENGINE CHANGED ***`

Doosra wala zyada important hai. Wahi wo silent failure hai jisme tu imaandari
se kaam karta rehta hai aur reference chupchaap khisak jaata hai.

## Quick reference

```bash
# ghar pe, ek din pehle
python3 -m pip install -r requirements.txt sounddevice
python3 make_test_data.py --out testdata/ && python3 selftest.py testdata/
python3 gen_signals.py --out playback/
python3 plan.py --out rangeplan/ --hours 3.5
lpr rangeplan/RUN_SHEET.txt playback/PLAYBACK_ORDER.txt

# range pe
python3 record.py --list
python3 calibrate.py CAL-001.wav --spl-db <meter reading>
python3 ir_extract.py IR-001.wav --inverse playback/inverse_filter.wav --out ir/
python3 record.py --meter --device N --channels 2
python3 record.py --device N --channels 2 --out A-001.wav
python3 validate.py A-001.wav --array --expect-events 1

# ghar wapas aake
python3 ingest.py <take>.wav --meta rangeplan/metadata_S1.csv --out events/
python3 analyze.py events/ --cal calibration.json --label real --out real.json
python3 report.py real.json --audio events/ --out report.html
open report.html
```
