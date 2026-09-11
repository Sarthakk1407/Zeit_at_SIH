# Har important term — Hinglish mein, example ke saath

Koi pooche toh yahin se jawab. Har entry: **kya hai → example → hamare project mein kyun**.

---

## 1. α-stable distribution (alpha-stable)

**Kya hai:** Ek probability distribution jisme "bahut bade" values normal se kahin zyada aate hain. Gaussian (bell curve) mein 6-sigma ka event kabhi nahi aata. α-stable mein aata hai, aur aata rehta hai.

**Example:** Class ke 50 bachon ki height Gaussian hai — sabse lamba 6 feet, sabse chhota 5 feet, koi 20 feet ka nahi hoga. Par **income** α-stable hai — 49 log ₹50,000 kamate hain aur ek banda ₹500 crore. Wo ek banda poora average tod deta hai.

**Gunshot exactly aisa hai:** 15 second mein 14.9 second silence (−49 dBFS), aur 0.1 second mein −5 dBFS ka dhamaka.

**Kyun important:** Gaussian assume karne wale saare purane methods (spectral subtraction, Wiener filter, RMS) gunshot pe toot jaate hain.

---

## 2. α (alpha) — the parameter

**Kya hai:** α-stable distribution ka "kitna heavy-tailed hai" wala knob. **0 se 2 tak.**

| α | Matlab |
|---|---|
| **α = 2** | Gaussian — normal, koi outlier nahi |
| **α = 1** | Cauchy — bahut heavy tails |
| **α < 0.5** | Itna extreme ki variance aur mean dono infinite |

**Example:** α ek "kitne bade surprise aayenge" ka dial hai. α = 2 pe surprise nahi. α = 1 pe roz. α = 0.3 pe har doosra sample surprise.

**Hamare project mein:** Training augmentation α ≈ 1 pe karte hain. Aur **α < 0.5 wale zone mein bhi jaate hain jise Yuan et al. ne deliberately chhod diya tha** — kyunki wahan signal clip ho jaata hai. Hamari physics wahi hai (mic sach mein clip hota hai), toh unka "problem" hamara "feature" hai. Ye project ka sabse original idea hai.

---

## 3. γ (gamma)

**Kya hai:** Do jagah use hota hai, confuse mat hona.

**(a) α-stable ka scale parameter** — noise kitna strong hai. Gaussian ke σ (standard deviation) jaisa.

**(b) BMRI ka interpolation threshold** — kitna bada error ho toh sample ko "kharab" maan ke replace kar do.

**Example (b):** γ ek chowkidar ki sakhti hai. γ zyada = sirf bahut bade dhamake pakdega. γ kam = har khatke ko dhamaka samajh lega, aur asli awaaz bhi kaat dega.

**Hamare project mein:** γ **fixed nahi** hai — kurtosis classifier live decide karta hai. Frame impulsive lage toh γ tight, normal speech ho toh γ loose. **Yahi "adaptive" wala hissa hai.**

---

## 4. β (beta)

**Kya hai:** α-stable ka skewness — distribution ek taraf jhuki hai ya symmetric.

**Example:** Blast wave symmetric nahi hoti. Pehle tez positive pressure spike, phir dheemi negative dip. β wahi tedhapan capture karta hai.

---

## 5. Kurtosis

**Kya hai:** "Tails kitni bhaari hain" ka ek number. **Gaussian ka kurtosis = 3.**

**Example:** Kurtosis 3 = normal din. Kurtosis 18 = zyadatar shanti, par kabhi-kabhi vispHot.

**Hamare data mein: median kurtosis 18.5** (`stats_impulse.json`). Ye 3 se 6 guna zyada hai — proof ki hamare events sach mein impulsive hain.

**Kyun important:** Yahi wo ek number hai jisse classifier decide karta hai "ye frame impulsive hai, transient path chalu karo".

---

## 6. Crest factor

**Kya hai:** `peak ÷ RMS`, dB mein. Signal kitna "spiky" hai.

**Example:** Sitar ki lagatar dhun ka crest factor ~6 dB. Tabla ki thap ~15 dB. **Hamara gunshot 17.9 dB.**

---

## 7. A-duration aur B-duration

**Kya hai:**
- **A-duration** — pehla pressure spike kitni der ka. Microsecond level.
- **B-duration** — awaaz ko −20 dB tak girne mein kitna time. Ye goonj (reverb) hai.

**Example:** Taali bajao. "TAK" = A-duration. Kamre mein jo goonj rehti hai = B-duration.

**Hamare data:** A = **0.27 ms** (median), B = **342.7 ms**. Matlab dhamaka 0.27 ms ka, par uski goonj 343 ms rehti hai — aur wahi 343 ms mein bolne wale ke shabd doob jaate hain.

---

## 8. RMS — aur ise kyun nahi use karte

**Kya hai:** Root Mean Square — `sqrt(average of x²)`. Signal ki "average loudness".

**Problem:** Ye **second moment** hai. Aur α < 2 wale α-stable ke liye second moment **infinite** hota hai — matlab converge hi nahi karta.

**Example:** Ek gaon mein 100 log, sab ₹20,000 kamate hain. Average = ₹20,000. Ab Ambani gaon mein aa gaya. Average = ₹10 crore. **Average ne gaon ke baare mein kuch nahi bataya, sirf Ambani ke baare mein bataya.**

RMS gunshot pe exactly yahi karta hai — jo sabse loud sample tha, RMS bas wahi batata hai. Window badlo, jawab badal jaayega.

**Iska matlab:** RMS se normalize karna = har training example ko ek **random number** se divide karna.

---

## 9. Percentile normalization (90th)

**Kya hai:** RMS ki jagah, `|x|` ka 90th percentile lo aur usse divide karo.

**Example:** Gaon wali misaal mein — average ki jagah **90th percentile income** lo. Ambani top 10% mein chala jaata hai aur nikal jaata hai. Bacha hua number gaon ko sach mein describe karta hai.

**Kyun chalta hai:** Order statistics (percentile) har distribution pe finite hote hain, chahe moment infinite ho.

---

## 10. FLOM — Fractional Lower-Order Moments

**Kya hai:** `E[|x|^p]^(1/p)` jahan **p < α**. Poora power 2 lene ki jagah, chhota fractional power (jaise 0.8) lo.

**Example:** x² lene se bade values ka asar aur bada ho jaata hai. x^0.8 lene se unka asar dab jaata hai. Bade values ka volume kam kar diya.

**Rule:** p **α se chhota** hona chahiye, tabhi converge karega.

**Hamare project mein:** Shao & Nikias (1993) ka paper. `architecture.md` block [3]. **Paper abhi folder mein nahi hai — C++ mein daalne se pehle lena zaroori hai.**

---

## 11. STFT — Short-Time Fourier Transform

**Kya hai:** Audio ko chhote-chhote tukdon (frames) mein kaato, har tukde ka frequency spectrum nikalo. Result = spectrogram.

**Example:** Gaana sunne ki jagah uska "equalizer bars" dekhna — par har 10 millisecond ka alag.

**Hamare settings:** 20 ms frame, 10 ms hop (engine) — ya GTCRN ka 32/16 ms. **Ye dono abhi tak decide nahi hue, aur ye conflict resolve karna zaroori hai.**

---

## 12. Complex domain aur phase

**Kya hai:** STFT do cheezein deta hai — **magnitude** (kitna loud) aur **phase** (timing/alignment). Purane methods sirf magnitude use karte the aur phase phenk dete the.

**Example:** Magnitude = "1 kHz pe 50 dB energy hai". Phase = "wo wave abhi upar ja rahi hai ya neeche". Do awaazon ko subtract karna ho toh dono ka phase match hona zaroori hai — warna cancel hone ki jagah add ho jaayengi.

**Note:** H-GTCRN ke ablation mein log-power feature complex se **behtar** nikla. `placement.md` ye sahi likhta hai, `architecture.md` ulta likhta hai — ek jagah fix karna hai.

---

## 13. ERB — Equivalent Rectangular Bandwidth

**Kya hai:** Frequency bands ko insaani kaan ki tarah baantna — neeche baarik, upar mota.

**Example:** Kaan 100 Hz aur 200 Hz ka farq aasani se sunta hai. Par 10,000 aur 10,100 Hz ka farq nahi sunta. Toh upar wali frequencies ko alag-alag rakhne ka koi fayda nahi — unhe jod do.

**Hamare project mein:** 257 bins → **129 features** (64 ERB bands upar se + 65 neeche wale jaise ke waise). Compute 2× kam, aur kaan ke hisaab se sahi.

---

## 14. GTCRN

**Kya hai:** **G**rouped **T**emporal **C**onvolutional **R**ecurrent **N**etwork — hamara neural core. Ek chhota speech-enhancement model.

**Numbers:** **23,700 parameters, 39.6 MMAC/s.** Comparison ke liye — ek normal speech model ke 5–50 lakh parameters hote hain. Ye 23.7 hazaar hai. **200 guna chhota.**

**Kyun ye:** Kyunki headset pe chalna hai, GPU pe nahi.

**H-GTCRN** = iska hybrid version, do microphone ke liye, Aux-IVA front-end ke saath. Wahi hamara base hai.

---

## 15. MMAC

**Kya hai:** Million Multiply-ACcumulate operations per second. Model kitna compute maangta hai.

**Example:** Kilometre-per-litre jaisa — par model ke liye. 39.6 MMAC/s matlab har second 3.96 crore multiply-add.

---

## 16. Mask

**Kya hai:** Model direct saaf awaaz nahi banata. Wo ek **mask** banata hai — har frequency bin ke liye 0 se 1 ke beech ka number — aur usse noisy input ko multiply karta hai.

**Example:** Mask ek per-frequency volume knob hai. Jahan awaaz hai wahan 0.9 (rakh lo), jahan gunshot hai wahan 0.05 (kaat do).

**Zaroori detail:** Mask **noisy input** pe lagta hai, IVA ke output pe nahi. Ye H-GTCRN ka ablation finding hai.

---

## 17. Aux-IVA

**Kya hai:** Auxiliary-function Independent Vector Analysis. Multiple mics se aayi mili-huyi awaazon ko alag streams mein todta hai.

**Example:** Do kaan se do log ek saath bol rahe ho toh dimaag alag kar leta hai. IVA wahi maths mein karta hai.

**Catch:** N mic se zyada se zyada N source alag honge. Aur output **order mein nahi aate** — kaun sa stream voice hai, IVA nahi batata. Isiliye hum saare streams network ko de dete hain aur wo khud decide karta hai.

---

## 18. LMS aur FxLMS

**Kya hai:** **L**east **M**ean **S**quares — 1975 ka classic adaptive filter. Reference mic se noise ka anuman lagata hai aur primary se ghata deta hai.

**FxLMS** = Filtered-x LMS, active noise control ke liye — speaker aur kaan ke beech ka rasta (secondary path) bhi model karta hai.

**Widrow ki shart:** Reference mic mein **wearer ki awaaz bilkul nahi** honi chahiye. Filter total output power minimize karta hai — agar voice reference mein hai, toh wo voice ko hi kaat dega.

**Example:** Do log tumhare kaan mein bol rahe hain. Tum ek ko chup karana chahte ho. Agar dono ek hi mic mein hain toh subtract karne pe dono jaayenge.

---

## 19. BMRI

**Kya hai:** Ek classical method — signal ko AR model se predict karta hai, jahan prediction bahut galat ho wahan "click" maan ke us hisse ko aas-paas se bhar deta hai.

**Example:** Purani gramophone record ki "kat-kat" hatana. Wahi kaam.

**Sach jo bolna zaroori hai:** BMRI **white Cauchy noise pe film restoration ke liye** validate hua tha, gunshot pe nahi. Aur uske authors khud likhte hain ki wo **transients ko kharab karta hai** — aur speech ke plosives (`p`, `t`, `k`) transients hi hain. Isiliye hum ise **sirf ballistic crack aur mechanical noise** ke liye use karenge, poore blast ke liye nahi.

---

## 20. RIR — Room Impulse Response

**Kya hai:** Ek kamre ka "acoustic fingerprint". Ek instant ki taali us kamre mein kaisi sunai deti hai.

**Example:** Bathroom mein taali = lambi goonj. Bistar wale kamre mein = sookhi, turant khatam. RIR wahi farq record karta hai.

**Use:** Kisi bhi saaf awaaz ko RIR se **convolve** karo, aur wo us kamre mein record hui lagegi. Isi se ek range trip se anginat acoustic spaces ban jaati hain.

---

## 21. HRTF

**Kya hai:** Head-Related Transfer Function. Tumhara sar, kaan aur kandhe awaaz ko kaise badalte hain, direction ke hisaab se.

**Example:** Peeche se aayi awaaz alag lagti hai kyunki sar beech mein hai aur high frequencies kaat deta hai. HRTF wahi shadow model karta hai.

**Kyun:** Tan et al. ne flat −10..0 dB scalar use kiya tha. Hum asli HRTF (CIPIC/KEMAR) use karenge — ye ek concrete improvement hai.

---

## 22. Lombard effect

**Kya hai:** Shor mein log apne aap alag tarah bolte hain — zor se, ooncha pitch, alag spectral tilt. Ye involuntary hai.

**Example:** Loud party mein baat karo, phir chup kamre mein wahi vaakya bolo. Recording sun ke farq saaf pata chalega. Tumne koshish nahi ki, apne aap hua.

**Kyun critical:** Normal speech pe train kiya model Lombard speech pe **~5 dB kharab** karta hai. Aur gunfire mein har banda Lombard mein hi bolega. **Ye tumhara poora use case hai — aur "Lombard" shabd abhi tak tumhare docs mein ek baar bhi nahi aaya.**

---

## 23. SNR, SI-SNR, SI-SDR

- **SNR** — signal power ÷ noise power, dB mein. Kitna shor bacha.
- **SI-SNR** — Scale-Invariant. Volume badalne se score nahi badalta.
- **SI-SDR** — Scale-Invariant Signal-to-Distortion Ratio.

**Kyun SI- wala:** Purana SDR **jhooth bol deta hai**. Le Roux ke paper mein (tumhare folder mein hai, abhi uncited) — jaise-jaise frequency bins delete karte jao, SDR 10–15 dB pe tika rehta hai aur 40% masking pe **badh** bhi jaata hai. SI-SDR lagatar girta hai.

Aur bins delete karna **exactly wahi hai jo mask-based denoiser karta hai**. Toh SDR over-suppression ko chhupa deta hai, SI-SDR pakad leta hai.

---

## 24. PESQ aur STOI

- **PESQ** — Perceptual Evaluation of Speech Quality. 1 se 4.5. "Kitna acha sunai deta hai."
- **STOI** — Short-Time Objective Intelligibility. 0 se 1. "Shabd samajh aate hain ya nahi."

**Farq:** Awaaz buri lag sakti hai par samajh aa sakti hai (PESQ kam, STOI zyada). Soldier ke liye **STOI zyada matter karta hai**.

**Dono ki kami:** Dono poore utterance pe average karte hain. 10 second mein 200 ms ka gunshot inhe hila hi nahi paata. **Isiliye humne IRT aur WLPS banaye.**

---

## 25. DNSMOS — SIG aur BAK

**Kya hai:** Ek neural network jo insaani rating ka anuman lagata hai, 1–5 pe.

- **SIG** — sirf speech ki quality
- **BAK** — sirf background suppression

**Kyun alag-alag:** Yahi over-suppression pakadta hai. Agar filter gunshot poora kaat de (BAK high) par awaaz bhi kharab kar de (SIG low), toh ek single SNR number ye chhupa lega. SIG/BAK split nahi chhupata.

**Reality check:** Tumhara target SIG 4.1 / BAK 4.2 hai — **ek Notes screenshot se aaya hai**. GTCRN ka apna blind test result **SIG 3.00** hai, aur wo noisy input ke 3.20 se **kam** kar deta hai. 4.1 reachable nahi hai.

---

## 26. IRT aur WLPS (hamare apne metrics)

- **IRT — Impulse Recovery Time:** dhamake ke baad har band ko wapas normal aane mein kitna time.
- **WLPS — Words Lost Per Shot:** har shot ke andar kitne shabd mar gaye.

**Hamara measured IRT:** 1–2 kHz band **464 ms** leta hai — sabse dheema. Aur wahi band speech intelligibility carry karta hai.

**Ye ek line mein poora argument hai:** 10 second pe average karne wala metric 464 ms ka gaddha nahi dekh sakta.

---

## 27. NMSE

**Kya hai:** Normalized Mean Square Error. Active noise control mein error mic pe kitni energy bachi. **Jitna zyada negative, utna acha.**

**Example:** −10 dB NMSE = 90% noise energy khatam.

**Note:** Ye **Lane A (hearing protection)** ka metric hai, Lane B (radio) ka nahi. Deep ANC isi se naapta hai. GTCRN NMSE nahi de sakta kyunki wo anti-noise banata hi nahi.

---

## 28. Lane A / Lane B

**Lane A — kaan bachana:**
reference mic → speaker → kaan. Budget **1 ms se kam**. FxLMS. Metric NMSE.

**Lane B — radio pe awaaz bhejna:**
boom mic → denoiser → radio. Budget **20–40 ms**. Neural network. Metric PESQ/STOI.

**Kyun alag:** Anti-noise ko **sound wave se pehle** kaan tak pahunchna hai — earcup se kaan tak 0.3–0.6 ms lagta hai. 25.3 ms budget usse **40–80 guna** slow hai. Neural network Lane A mein reh hi nahi sakta.

**Example:** Lane A = airbag (millisecond mein khulna hai). Lane B = GPS route recalculation (do second theek hai). Dono zaroori, dono ka time-scale alag.

---

## 29. ONNX

**Kya hai:** Open Neural Network Exchange — ek standard file format. PyTorch mein train karo, ONNX mein export karo, C++ mein chalao.

**Example:** PDF jaisa. Word mein bana lo, PDF banao, kisi bhi device pe khul jaayega.

**Hamare project mein:** ONNX **ekmatra** jagah hai jahan Python aur C++ milte hain. `tech-stack.md` isko "the only boundary" kehta hai.

---

## 30. Quantization aur Pruning

- **Quantization:** 32-bit float ki jagah 8-bit integer. Model 4× chhota, 2–4× tez.
  **Example:** ₹1,247.83 ki jagah "₹1,250" likhna. Thoda accuracy gaya, bahut jagah bachi.
- **Pruning:** Jo weights lagbhag zero hain unhe hata do.
  **Example:** Contact list se wo 500 log delete karna jinhe kabhi call nahi kiya.

**Bonus:** α-stable pe train kiye models **zyada sparse** nikalte hain — matlab pruning aur kaam karegi. **Ye kisi ne abhi tak kiya nahi hai.**

---

## 31. Frame, hop, latency

- **Frame:** ek baar mein kitna audio process. 20 ms.
- **Hop:** har kitni der mein naya frame. 10 ms (50% overlap).
- **Algorithmic latency:** frame + buffer = **25.3 ms**.

**Example:** Frame = ek chammach. Hop = do chammach ke beech ka gap. Awaaz aur nikalne ke beech ka delay = latency.

**Sandarbh:** 25.3 ms radio ke liye theek hai (insaan ~40 ms tak notice nahi karta). Par true ANC ke liye 40–80 guna slow hai.

---

## 32. MELPe / vocoder

**Kya hai:** Tactical radio tumhari waveform nahi bhejta. Wo **MELPe** (NATO STANAG 4591) se awaaz ko **2400 / 1200 / 600 bits per second** mein encode karta hai.

**Example:** WhatsApp voice note jaisa, par 100 guna zyada compressed. Radio actual awaaz nahi bhejta — pitch, voicing, spectral envelope ke parameters bhejta hai, aur doosri taraf wapas se banata hai.

**Kyun important:** Hamara PESQ/STOI **galat jagah** naapa ja raha hai — hum denoiser ka output naapte hain, par sunne wala vocoder ka output sunta hai. **Vocoder chain mein daal ke, dono taraf ke numbers report karne chahiye.**

---

## 33. TRL — Technology Readiness Level

**Kya hai:** 1 se 9 ka scale — technology kitni taiyaar hai. DRDO isi mein sochta hai.

| TRL | Matlab |
|---|---|
| 3–4 | lab mein kaam karta hai ← **hum yahan hain** |
| 5–6 | asli environment mein test hua |
| 7–9 | field mein deployed |

**Kya bolna hai:** *"Hum TRL 4 pe hain. TRL 5 ke liye JSS 55555 environmental qualification aur 40 ghante ka field trial chahiye. Plan ye raha."*

Ye samajhdari dikhata hai. "Ye deployable soldier system hai" bolna naasamjhi dikhata hai.
