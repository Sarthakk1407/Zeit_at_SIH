IEEE/ACM TRANSACTIONS ON AUDIO, SPEECH, AND LANGUAGE PROCESSING, VOL. 23, NO. 10, OCTOBER 2015 

1680 

# Reduction of Gaussian, Supergaussian, and Impulsive Noise by Interpolation of the Binary Mask Residual 

Marco Ruhland, Joerg Bitzer _, Member, IEEE_ , Matthias Brandt, and Stefan Goetze _, Member, IEEE_ 

**_Abstract—_ In this paper, we present a new approach for noise reduction. A binary time–frequency (T-F) masking threshold criterion is proposed and analyzed with respect to the average spectra of music and noise disturbances. Modified autoregressive (AR) detection and AR interpolation are then applied to the residual signal of the binary masking process. The proposed method is able to reduce supergaussian and impulsive noise while ensuring preservation of the desired signal, which is crucial for professional high-quality audio restoration, and it is also suitable for Gaussian noise to a certain extent. The approach is compared to a state-of-the-art restoration algorithm by means of the objective measures signal-to-noise ratio (SNR) improvement and perceptual quality, and by subjective listening tests. The objective results as well as the listening tests show that the proposed algorithm is especially suited for supergaussian, grainy-sounding noise types, e.g., optical soundtrack noise of celluloid movie footage, or rain noise.** 

**_Index Terms—_ Interpolation, noise reduction, optical soundtrack noise, time–frequency masking.** 

## I. INTRODUCTION 

HE term “noise reduction” is often associated with the re- **T** moval or reduction of Gaussian noise disturbances. The assumption of a Gaussian random process is common for popular denoising algorithms, like the well-known Wiener filter [1] or the Ephraim-Malah method [2] developed in the 1980s. However, at the same time, Porter and Boll [3] showed that speech signals are rather characterized by leptokurtic, respectively supergaussian amplitude distributions, and that the error introduced by the deficient Gaussian assumption may be significant. This finding led to the development of more sophisticated approaches, e.g., [4] by Cohen, featuring two-sided Gamma- and Laplace densities for the speech amplitude distributions, however still assuming a Gaussian distribution for the noise. Only a few months later Martin [5] showed that car noise does rather have a Laplacian distribution instead of a Gaussian distribution, 

Manuscript received October 14, 2014; revised February 18, 2015; accepted May 29, 2015. Date of publication June 11, 2015; date of current version June 19, 2015. This work was supported in part by the German Federal Ministry of Education and Research (BMBF) under Grants 17N3008 and 03FH030PX2 and in part by the EU-FP7 project EcoShopping under Grant 609180. The associate editor coordinating the review of this manuscript and approving it for publication was Prof. DeLiang Wang. 

M. Ruhland and S. Goetze are with the Project Group Hearing, Speech and Audio Technology, Fraunhofer Institute for Digital Media Technology (IDMT), D-26129 Oldenburg, Germany (e-mail: marco.ruhland@idmt.fraunhofer.de). J. Bitzer and M. Brandt are with the Institute for Hearing Technology and Audiology, Jade University of Applied Sciences, 26121 Oldenburg, Germany. Color versions of one or more of the figures in this paper are available online at http://ieeexplore.ieee.org. Digital Object Identifier 10.1109/TASLP.2015.2444664 

and he showed how to employ this prior information within the minimum mean square error (MMSE) estimator for a denoising algorithm. This approach works particularly well at low signal-to-noise ratios (SNR) below 0 dB since the Laplacian noise assumption yields less musical noise in that case. Further refinement of the estimators is presented in [6], [7]. Besides these methods, several techniques exist to reduce the musical noise phenomenon, e.g., spectral peak elimination [8], spectral weighting [9], spectral domain smoothing [10], or smoothing of the spectral gain function [11]. For speech signals, it has been shown that cepstral smoothing is superior to spectral domain smoothing, since speech-relevant information like pitch and formant structure can be protected against smoothing within the cepstral domain [12]–[14]. 

The previously described denoising methods usually work in the frequency-domain. However, for the removal of impulsive disturbances, e.g., clicks caused by dust and scratches on a gramophone disc, time-domain interpolation methods are preferable. Since click disturbances are mostly single, sparse events in time, lasting only a few milliseconds, it is usually sufficient to replace the corrupted samples by interpolated values of the surrounding unaffected samples [15]. While frequency-based methods usually affect all samples of a signal block, better preservation of the desired signal is achieved by time-domain interpolation, since only a few samples are changed. Pioneering work on time-domain interpolation has been done independently by Vaseghi [16] and Veldhuis [17] for different applications. 

However, in some cases, a strict distinction between impulse disturbance and hiss cannot be made easily. Imagine the noise of a heavy rainfall or applause which is the result of a vast number of small impulsive events per time instant, and cannot be regarded as single and sparse any more. Though the audible sensation is stationary, a certain granularity is perceived that allows the listener to identify the impulsive origin of the noise. Similar noise can be observed when listening to the sound of old celluloid movies of the optical soundtrack era. The footage decomposes with time and suffers from dust and mould, badly affecting the audio signal which is encoded in an optical soundtrack next to the picture information. The resulting noise is grainy and of supergaussian amplitude distribution. Broadcast media archives request for new restoration techniques to cope with such kinds of degradation. For an overview of restoration of optical soundtracks please cf. [18]. This kind of noise is problematic for both frequency- as well as time-domain approaches. In this contribution we propose a new hybrid algorithm, performing frequency-domain binary masking and time-domain 

2329-9290 © 2015 IEEE. Personal use is permitted, but republication/redistribution requires IEEE permission. See http://www.ieee.org/publications_standards/publications/rights/index.html for more information. 

RUHLAND _et al._ : REDUCTION OF GAUSSIAN, SUPERGAUSSIAN AND IMPULSIVE NOISE 

1681 

interpolation to tackle the described problem. Comparing our method with a state-of-the-art restoration algorithm will give new ideas on how to cope with supergaussian noise. 

The remainder of this contribution is organized as follows. Section II introduces our approach, being a combination of timefrequency (T-F) masking and AR detection and interpolation. In Section III, a brief summary of the theoretical analysis of the proposed algorithm is given based on a former contribution of the authors [19]. Then, the proposed algorithm is tested versus a state-of-the-art algorithm by means of objective quality measures and subjective listening tests in Sections IV and V, respectively. Finally, conclusions are drawn in Section VI. 

## II. THEORY 

## _A. Binary Masking_ 

A degraded audio signal at discrete time index is given as a set of sinusoidal basis functions plus a random process (cf. [20], [21]): 



For declicking applications, the task is to estimate the complex coefficients in Eq. (1) and the number of sinusoids, that minimize the energy of the residual , e.g., in a least-squares sense (cf. [21], [20] or [22]). The residual is then treated as an autoregressive (AR) process, and AR detection and interpolation is performed within to eliminate the clicks. Afterwards, the interpolated residual is added back to the split-apart sinusoids, to result in the restored audio signal . 

An easier way to split the sinusoids from the residual can be achieved by T-F masking. The use of T-F masking for separation tasks is quite young, though the idea behind it is quite simple and of low complexity. It has been successfully employed e.g., in computational auditory scene analysis (CASA), independent component analysis (ICA), improvement of automatic speech recognition (ASR), and cochlear implant (CI) signal enhancement, amongst other fields of use. A list of contributions on the use of T-F masking within these fields of research is given in [23], pg. 342. For a two-source separation task, like in our case, the separation of a desired target signal from a noisy residual signal, the T-F masking process is also called _binary masking_ (BM). 

Let be the noisy music signal to be restored, as the sum of the undisturbed signal , and the noise disturbance . The aim of the process is to find a target signal and a residual signal that match the true unknown desired signal and the noise signal as closely as possible. Although and are different from and , Eq. (2) shall be satisfied, 



expressing Eq. (1) in a simpler fashion. In Eq. (2), represents the so-called target signal, as the sum of sinusoids, and the noisy residual signal. Several steps have to be performed to obtain these signals. First, the noisy signal is transformed into the frequency-domain, using a DFT of length 

samples at a sampling frequency Hz, with samples block shift, corresponding to 50% overlap, by 



In Eq. (3), denotes the frequency index and the discrete frame index. The frequency-domain target signal and the residual signal are initialized with zeros. The absolute squared magnitude is compared to the binary masking threshold estimate for each frequency bin . The threshold estimate can be initialized with zeros before processing the first block , or, for faster initial response, with the squared magnitude of the first signal block, . If the squared magnitude for a certain frequency bin is above , the respective frequency bin is copied into the target STFT signal . Otherwise, it is copied into the residual STFT signal block . Finally, the inverse discrete Fourier transform (IDFT) is used to obtain the time-domain signal blocks and of the target signal 



and the residual signal 



_1) Proposed BM threshold estimate:_ The above splitting method has already been used in [24], however, with a single-value threshold for all frequency bins . In order to obtain a frequency dependent threshold for the binary mask, we use 



where the power spectral density (PSD) estimate of the input signal is calculated by a recursively smoothed periodogram 



In Eq. (7), the smoothing vector is defined as 



with 





and 



In Eqs. (9) and (10), we use time constants of s, and s. The relatively short release time ensures that the threshold estimate follows the noise floor quickly, whereas the high attack time helps to preserve the threshold. This ensures that short transients, e.g., drum sounds, and other 



<!-- Start of picture text -->
N 4_Clean Signal a Target dB FS0<br>z 3 < z< 3 3 1-30<br>> Xl] =o °<br>2 of ae a Sie .. 2158<br>5.1 a 4 Binary Mask TAM 2 = P<br>0 1 2 YAH] 2 og 12 =e<br>Time<br>/ seconds ) Mi 5 om =p 4 ll ° Time / seeds<br>4 ixture 2.15 SaaS ‘<br>O si besre Ss Residual dB FS<br>4 Noise Signal seiey mo : z s<br>a aeS : 9 | z z 3 -30<br>3 . Time / seconds<br>5 S78 ae Ze Pay -60<br>2 DPI . = ee ; 52<br>- Se = s[A.1] 5 bag<br>=! 0 BM Threshold 2<br>md sail mantel Estimator m0 “150<br>01 3 oe<br>ee Time / seconds 0 1ane arenal2<br>0 1 2 Time / seconds<br>Time / seconds<br>Y[ A, J] TI A, |<br>RD , J]<br>f(A, 1]<br>t[ AM + n}<br>r[ AM + n]<br>E[A, 1]<br>Bll)<br>1/f<br>g(r, 1]<br>E[A, 1]<br>Bl)<br>Bi i] = -lo —} .<br>| Baec g ( OL<br>Baec<br>a + Bec<br>r[ AM + n]<br>Pa et<br>Pa et Pa 10<br>Pa et = 16 e[ AM + n]<br>Paet<br>e[ AM + n] = r[ AM + n] — Ss; a pT[ AM + n — p l,<br>p =1<br><!-- End of picture text -->



<!-- Start of picture text -->
sa nr e n r[ AM  +n] J ar e Ap n (Tostrretrirtrlr te ¢<br>r[ AM + n]<br>r<br>v[ AM + n] w ea l CTelfle s obllrlitr 1 Hille<br>e7[ \M + n]<br>y = 0 Le ry<br>a re s y= erttiee<br>diseard<br>ry,<br>= 0.1 ; , Tretrettire!<br>c ian<br>e7[ AM + n] r,<br>v[ AM + n] ; (Treertrertitizres¢<br>v[ AM  + n] vy : . vs r<br>r h s r i<br>Ti nt<br>“dp, 0 0 0<br>0 -ap, 1 0 0<br>0 000 “ap, +. 1<br>Ax Ay<br>ry = ( A T  Au) A T An rK A Ax Ay<br>A Ti nt: AM + n]<br>Ax Au<br>T A<br>ry = [re[ AM + n] ,...,7% [ AM + n— -—h+I]]] (L — P a w ) x L<br>h = | \(1 —7)L Tk T u<br>ny P r t = 32<br>r = ([r[ AM + nJ ,...,r AM + n — L +1]] "<br>L<br><!-- End of picture text -->





<!-- Start of picture text -->
gis<br>z<br>|<br>0.5<br>3<br>g<br>2 0<br>5 10 15 20 25 30 35 40 45 50<br>(a)<br>3>> 1<br>=|<br>ey&& 0.5<br>3ey&&<br>Ss<br>5 10 15 20 25. 30 35 «404550<br>gil<br>®<br>£05<br>2<br>5 10 15 20 25 30 35 40 45 50<br>frequency bin<br>()<br><!-- End of picture text -->



<!-- Start of picture text -->
gis L=2048<br>z <><br>| :<br>0.5<br>3 Tm (fT? LT.<br>g y[AM+n]<br>2 0 Baec<br>5 10 15 20 25 30 35 40 45 50<br>(a)<br>3>> 1 Threshold<br>=| YA! vector<br>3ey&& 0.5 update47)*<br>Ss<br>5 10 15 20 25. 30 35 «404550 TA Binary mask REA<br>gil<br>®<br>£05 r[AM+n]<br>2<br>5 10 15 20 25 30 35 40 45 50 Detection<br>frequency bin spectral<br>() correction<br>(AM+n] (+) FinlAM+n]<br>Ri , I Vres|AM+n]<br>Rint [A, J Hann<br>window<br>nn<br>i<br>Rint  [A, I] Ba ec Y<br>T in t /AM + n]<br>® *( - )<br>—Y e ut +Yc ut<br>y<br>T in t |AM + n] t] AM + n]<br>Yo ut = —®* (7 2 - 100% ) .<br>Yres| AM + n] = r in t |AM + n] 4+ t/ AM + n]. o<br>Yres [n] ; Yeut ,<br>o = / y (y)dy<br>—V eut<br>(- )<br>I n<br>L y = 10 logy ( 07 ) .<br><!-- End of picture text -->

1 

<mark>v0)</mark> 

Y 

Y 

<mark>W</mark> 

|n erf—+<br>noise type<br>PDF y(y)<br>ICDF &~!(p)<br>sample kurtosis w _perceived sound<br><br><br><br><br><br>|
|---|
|:<br>1<br>Ly?<br>_<br>“<br>”<br>Gaussian<br>vane?”<br>V2erf~!(2p— 1), p € (0,1)<br>3<br>smooth|
|In(2p)<br>,p < 4<br>Laplace<br>2 exp (-ly<br>,<br>»pe(0,l<br>6<br>“sharp”<br>;<br>gp<br>(4)<br>—in(2(1-p)),p>4 7PS<br>OH<br>?|
|mod. Cauchy<br>CTICLES<br>@-1(p)=tan((m— 2n)(p— 4)), p € (0,1)<br>> 20<br>“impulsive”|
|60<br>—white Cauchy noise, 1=0.02, kurtosisw=27<br>---white Gaussian noise, kurtosis w=3<br>50<br>:<br>mM<br>40<br>t<br>7<br>/<br>[4<br>”<br>4<br>30<br>if<br><i<br>a<br>8<br>20<br>et<br>2<br>cee<br>5<br>10<br>ogee<br>tt<br>eee<br>~~w=s~~<br>fl<br>we 27<br>7109<br>10<br>20<br>30<br>40<br>50<br>60<br>70<br>80<br>90<br>100<br>1 ~~=~~ 0~~.~~02<br>detectionpercentagey/%|
|Y|
|W|
|Y<br>Y<br>(n ~~= ~~0.02)<br>Pet<br>y<br>Pint|
|Y<br>Y|





<!-- Start of picture text -->
60<br>—white Cauchy noise, 1=0.02, kurtosis w = 27<br>---white Gaussian noise, kurtosis w=3<br>50 :<br>mM 40 t<br>7 /<br>[4 ”<br>4 30 if<br><i a<br>8 20 et<br>2 cee<br>5 10 eee ogeett<br>fl<br>7109 10 20 30 40 50 60 70 80 90 100<br>detection percentage y/ %<br>Y<br><!-- End of picture text -->

IEEE/ACM TRANSACTIONS ON AUDIO, SPEECH, AND LANGUAGE PROCESSING, VOL. 23, NO. 10, OCTOBER 2015 

1686 

Dau _et al._ [42]. The SNR measure is a frequently used quality measure that is easy to calculate, but as stated in [43], not always shows high correlation with subjective results. Perceptual measures are better suited to determine the perceived signal quality [44]. Since the commonly used _perceptual evaluation of speech quality scores_ (PESQ) [45] is limited to 16 kHz sampling frequency and speech only, we decided to supplement the evaluation by the PEMO-based perceptual measure PSMt. Overall trends between results for PESQ and PSMt are similar. However, PEMO allows the use of audio material of higher sampling frequencies and is not limited to speech signals. Furthermore, it has been shown that PEMO is well-suited for the evaluation of noise reduction tasks [44]. 

_1) SNR measure:_ The input and output signal-to-noise ratios ( and ) can be determined in case the clean audio signal is available. The can be set by mixing the normalized clean audio signal and the normalized noise disturbance signal with adjusted levels. After processing by the denoising algorithm, the (in dB) can be calculated as the average SNR over all discrete time frames by [40] 





where is the clean audio signal without noise, is the restored audio signal after processing, is the set of frames with speech activity and its cardinality [46]. The SNR improvement is then obtained by 



It is common practice to plot the over the to visualize the input-output behavior of the investigated system. 

_2) Overall Perceptual Similarity Measure (PSMt) using PEMO:_ Since the SNR measures do not incorporate any knowledge about the human auditory system [43] and it has been shown that taking such information into account in objective quality assessment [44] is of importance, we furthermore calculate the Perceptual Similarity Measure (PSM) which was originally developed to predict quality degradations of broadband audio signals and which is based on the linear cross correlation coefficient of “internal representations” of signal pairs in blocks of 10 ms length [47]. The measure PSMt is the 5th percentile of the PSM output, calculating the perceptual distance between a test signal and a reference signal in a range between zero and one. A PSMt value of zero means no similarity, whereas a value of one stands for both test and reference signal being perceptually identical. PSMt showed high correlation with subjective ratings [41], [44]. For the input PSMt measure , the clean signal serves as reference, and a degraded signal at a given SNR is used as test signal. The output PSMt measure is calculated using the clean audio signal as reference again, and the restored audio signal as test signal. As before for the SNR measures, the PSMt improvement is calculated by subtracting from , and finally, plotted over . 

## _B. Measurement Results_ 

The top row of Fig. 7 shows the SNR improvement over the input SNR, , for the LSAR algorithm (left panel), the proposed BMRI algorithm with a _matched setting_ (middle panel), and again the BMRI with a _high setting_ (right panel). The bottom row of the plots shows the perceptual measure over the input SNR. Each panel contains three curves for the genres pop, classical music, and speech in white Cauchy noise (black lines), and three for the genres in Gaussian noise (darkgrey lines), plus the neutral line (dashed, no improvement). Furthermore, two dashed light-grey lines indicate the performance of the IBM (diamond markers) and the proposed BM (triangle markers) on classical music and white Cauchy noise as best performing genre, both _without_ interpolation and recombination of target and residual, i.e. measured on the extracted target signals alone. They define an example for floor and ceiling of performance for standalone binary masking, highlighted as a light-grey corridor in Fig. 7. 

The _matched setting_ (middle panels) means that the SNR improvement of the BMRI is set equal to the measured SNR improvement of the LSAR algorithm at its highest point (speech at 0 dB input SNR, white Cauchy noise). The reason for choosing that point is, that speech, with its inherent pauses, at a low input SNR, comes closest to the condition of a theoretically white BM residual signal with no tonal components. This is the preliminary assumption that has to be satisfied in order to predict the SNR improvement of the BMRI algorithm in dependence of the detection percentage parameter and vice versa (cf. Section III). The LSAR algorithm offers a dB at that point, so according to Fig. 6, the BMRI detection percentage was set to , resulting in a very close match of BMRI and LSAR for speech at 0 dB SNR in white Cauchy noise. For the _high setting_ of the BMRI in the right panel, a detection percentage with a theoretical dB was chosen, to investigate possible degradations of the desired signal by interpolation artefacts at higher values. 

## _C. Discussion_ 

The results for the LSAR algorithm (left panels in Fig. 7) show a good SNR improvement for the white Cauchy noise at low input SNR. Towards higher input SNR, the improvement drops, and even reaches negative values for pop music at 20 dB input SNR, as indicated by the standard deviation bars. Here, the desired signal gets affected by the LSAR algorithm. Since at 20 dB input SNR the white Cauchy noise is quite low compared to the desired signal, it is obvious that transients like e.g. drum sounds cause high AR error signals that trigger the interpolation threshold and thus get degraded. The speech and classical music signals achieve the best SNR improvement, since its inherent transient sounds (like e.g. plosives) are lower in energy than transients in pop music. For the Gaussian noise there is no SNR improvement at all for low SNR, and finally, some negative improvement at 15 and 20 dB input SNR, for the same reasons mentioned above. Compared to the standalone performance of the proposed BM, the LSAR seems to be worse at low input SNR. However, this is an erroneous belief, as the PSMt corridor in the lower panel confirms. The proposed BM’s target signal is practically free of white Cauchy noise, but yet 



<!-- Start of picture text -->
LSAR BMRI (y=5.25 %, matched setting) BMRI (y=12.5 %, high setting)<br>Ss 6 iy |<br>Z 4 I 7 / ke  @e ee Sh<br>< 2 @ —=F+——3.5» — —<br>—— mod. Cauchy, classic :<br>2-4 be vden: vd bees ee |e8 mod. Cauchy,ey  popne jeseeseeed vende: bee: be<br>—O- Gaussian, speech<br>0.5 : : olGaussian, classic<br>Pins ’ ~ 9 ~IBM for deguded casi * - : a<br>0.4 Do! : . > - A= prop. BM for degraded classic Dai. : . :<br>> > sneutral r<br>& ~d : 5 q fF ; :<br>a oi} os yO : — : wo<br>0 q » 3 E a ( — F —-a -<br>| ») »} ] »)<br>-5 0 5 10 15 20 25 -5 0 5 10 15 20 25 -5 0 5 10 15 20 25<br>SNR. / dB SNR. /dB SNR. / dB<br>in in in<br>ASNR AP S Mt S NRin<br>+0 . 5 dB<br>ASNRs<br>ASNRs<br>ASNR AP S Mt<br>ASNR<br>y = 12 . 5%<br>ASN R<br>AP S Mt<br>ASN R<br><!-- End of picture text -->

IEEE/ACM TRANSACTIONS ON AUDIO, SPEECH, AND LANGUAGE PROCESSING, VOL. 23, NO. 10, OCTOBER 2015 

1688 

## V. SUBJECTIVE EVALUATION 

The previously described objective quality measures already reveal valuable quantitative properties of the examined audio algorithms. However, objective methods for predicting the overall quality perceived by the human listeners may not fully correlate to the subjective opinion of test listeners [44], [50]. Therefore, it is often advantageous to measure the perceived quality also by means of subjective listening tests. In this contribution, we assessed the subjective perceived quality of the processed audio samples based by means of subjective ratings of ten normal hearing persons with musical background. A subset of the audio samples from Section IV was used (pop music, classical music, and speech), again degraded by adding white Cauchy noise of density ( ), at 10 dB and 20 dB SNR. LSAR and the proposed BMRI algorithm were applied for restoration. For the LSAR algorithm, the default setting was used, and for BMRI, the _matched_ setting (cf. Section IV for the parameters of the settings). 

The objective quality measures calculated in Section IV-B, as well as informal listening tests, reveal just minor improvement for the standard Gaussian noise. Higher settings beyond 12.5% would be necessary to achieve similar noise reduction performance as in the white Cauchy case. If is raised, more and more samples of the residual get interpolated and the residual signal loses energy, and thus, the musical noise of the target signal would become audible in the restoration result. In contrast to speech enhancement for, e.g., hands-free systems in cars or as pre-processing for automatic speech recognition (ASR), here it is crucial for high quality audio restoration to _not_ introduce any artefacts, be it at the cost of obtaining less noise reduction than possible. Besides that, the objective measures showed that the common LSAR approach hardly improves Gaussian disturbed signals at all. Informal listening to the example signals on the website [26] confirm this. For these reasons, we will focus on the white Cauchy noise only and omit the Gaussian noise type in the following subjective evaluations. 

## _A. Evaluation Procedure_ 

Two different subjective evaluation methods are used to analyze different aspects of the processed signals: 

- 1) Pairwise comparison by a two-alternative forced choice test (2-AFC) [51]: The noisy test signals (classic, pop, speech) have either been processed by BMRI or LSAR or left unprocessed. For both noise conditions (10 and 20 dB SNR) and for each genre, three possible algorithm combinations had to be tested, namely BMRI vs. LSAR, BMRI vs. unprocessed, and LSAR vs. unprocessed, resulting in a total of 18 pairs. These pairs were presented in six runs at 36 random pair trials per run. The subjects were instructed to choose the audio sample with the preferred overall quality in each trial. To determine the rank order of the corresponding algorithms, the Bradley-Terry-Luce (BTL) model [52], [53] has been applied with a minimum required significance of 99% to declare a test valid. 

- 2) A Mean Opinion Score (MOS) test procedure was used to evaluate the effect of the denoising algorithms on the residual noise and the target signal individually. It has been adopted from the ITU-T recommendations P.835 

[54], commonly used to evaluate the performance of noise reduction algorithms in speech communication systems. For this test, the subjects were asked to assess the quality dimensions _degradation of desired signal_ , _annoyance of residual noise_ , and _overall quality_ on a quasi-continuous MOS scale, ranging from one to five [44], [55] (1= _bad_ or _very annoying_ , 2= _poor_ or _annoying_ , 3= _fair_ or _slightly annoying_ , 4= _good_ or _perceptible but not annoying_ , 5= _excellent_ or _imperceptible_ ) while they could switch seamlessly between a restored audio signal and a clean, undisturbed version of the signal. Besides the restored signals from the LSAR and BMRI algorithm, a third set of test signals was generated by mixing the clean signals with noise at a 15 dB better SNR than the SNR of the LSAR and BMRI input signals. This additional signal set serves as the imitation of an imaginary artefact-free denoising algorithm with 15 dB noise reduction, as quality reference (REF). Six runs were performed over all test files and subjects, where runs one and two were discarded (they served as training phase for the subjects). Results from run three to six were averaged, as in [43]. 

## _B. Results of Listening Tests_ 

- 1) _2-AFC test:_ The results of the AFC test evaluation are shown in Table II for an input SNR of 10 dB and in Table III for an input SNR of 20 dB, respectively. The proposed BMRI algorithm is preferred for both SNR conditions and all three musical genres. For all test scenarios, the unprocessed signal is rated worst in terms of overall signal quality. The BTL-model scale differences towards the first rank are given in parenthesis for each algorithm [53]. Mostly, the distances to the third rank (unprocessed signal) are rather large, whereas the distances from the second rank (LSAR) against the BMRI tend to be smaller. This shows that both, BMRI and LSAR achieve major improvement in quality towards the unprocessed signal, but nevertheless, BMRI outperforms the common LSAR approach. For pop music at 10 dB SNR, a large BTL distance of the LSAR algorithm towards the first rank can be observed. This indicates the advantage of the proposed BMRI algorithm over the common approaches, e.g. in terms of being able to preserve desired transients like snare drums etc., as already explained in Section II-A. The significance level for all AFC tests is 99%. The _consistency_ in Tables II and III is a measure for the amount of inconsistent subject ratings [56]. A consistency of zero means that the subjects’ answers are completely contradictory, whereas a value of one means that there are no contradicting statements. All consistency values show that there were no contradictions amongst the subjects’ individual ratings except for classical music at SNR 10 dB (consistency 0.9). This small deviation could arise from the fact that classical music offers a high dynamic range, and therefore, it might be more difficult to distinguish the restoration results of very silent parts in the music at that rather low SNR. 

- 2) _MOS test:_ Fig. 8 to 10 show the results of the conducted MOS rating regarding target signal degradation (cf. Fig. 8), 



<!-- Start of picture text -->
degradation of target signal<br>classic pop speech<br>5 = O +! TI imperceptible<br>i !<br>4 - t+ 4 perceptible but<br>; not annoying<br>iS To41 Q<br>S 3h 4 H + L annoyingslightly<br>2 i !I 1 , annoying<br>LI ; LI<br>1 1 very annoying<br>mw > hoe oD hoe D<br>a s S ms < S Ps < S<br>yt a 4 oO 4 ia]<br><!-- End of picture text -->



<!-- Start of picture text -->
rank classic pop speech<br>—_ECC_[RFRFREHFHFERrOmrNmNR—T—FRHEH7>FomaaRhaamoporooo0020TTSFTFTFTFTETOEF—THO FEHR HpHpHRFHERHROemPepOano2-2NF<br>1 BMRI (0.00) BMRI (0.00) BMRI (0.00)<br>2 LSAR (0.84) LSAR (24.03) LSAR (0.56)<br>3 unprocessed (36.46) unprocessed (48.06) unprocessed (2.48)<br>consistency 0.90 1.00 1.00<br><!-- End of picture text -->



<!-- Start of picture text -->
rank classic pop speech<br>1 BMRI (0.00) BMRI (0.00) BMRI (0.00)<br>2 LSAR (0.92) LSAR (0.92) LSAR (0.92)<br>3 unprocessed (2.66) unprocessed (36.51) unprocessed (36.51)<br>consistency 1.00 1.00 1.00<br>significance 0.99 0.99 0.99<br><!-- End of picture text -->



<!-- Start of picture text -->
residual noise annoyance<br>classic pop speech<br>5 imperceptible<br>TaT<br>I<br>+ not annoying<br>4 ~- ' ] perceptible but<br>N J<br>fo) 3 L slightly<br>Ss annoying<br>2 I ; tot i<br>i + l annoying<br>!1<br>I<br>1<br>1 very annoying<br>za}Hw a4 nwa 4 za]Hw a4<br>~ AS weRSE MES<br>4 a 4 m4 4 a4<br><!-- End of picture text -->



<!-- Start of picture text -->
overall quality<br>classic pop speech<br>5 oO a excellent<br>T<br>T+<br>4 + ; Igood<br>I<br>5 L<br>=) 3 +. I i fair<br>2 L poor<br>+<br>L<br>1 bad<br>zawawsy24 za]<a.) nowyZ| oe<br>~ AS MAS “As<br>4 ma 4 ma 4 m4<br><!-- End of picture text -->

IEEE/ACM TRANSACTIONS ON AUDIO, SPEECH, AND LANGUAGE PROCESSING, VOL. 23, NO. 10, OCTOBER 2015 

1690 

- [4] I. Cohen, “Speech enhancement using super-Gaussian speech models and noncausal _a priori_ SNR estimation,” _Speech Commun._ , vol. 47, no. 3, pp. 336–350, 2005. 

- [5] R. Martin, “Speech enhancement based on minimum mean-square error estimation and supergaussian priors,” _IEEE Trans. Speech Audio Process._ , vol. 13, no. 5, pp. 845–856, Sep. 2005. 

- [6] J. S. Erkelens, R. C. Hendriks, R. Heusends, and J. Jensen, “Minimum mean-square error estimation of discrete Fourier coefficients with generalized gamma priors,” _IEEE Trans. Audio, Speech, Lang. Process._ , vol. 15, no. 6, pp. 1741–1752, Aug. 2007. 

- [7] I. Andrianakis and P. R. White, “Speech spectral amplitude estimators using optimally shaped gamma and chi priors,” _ELSEVIER Speech Commun._ , vol. 51, no. 1, pp. 1–14, 2009. 

- [8] Z. Goh, K.-C. Tan, and B. Tan, “Postprocessing method for suppressing musical noise generated by spectral subtraction,” _IEEE Trans. Speech Audio Process._ , vol. 6, no. 3, pp. 287–292, May 1998. 

- [9] D. Malah, R. V. Cox, and A. J. Accardi, “Tracking speech-presence uncertainty to improve speech enhancement in non-stationary noise environments,” in _Proc. IEEE Int. Conf. Acoust., Speech, Signal Process._ , 1999, vol. 2, pp. 789–792. 

- [10] M. Brandt and J. Bitzer, “Optimal spectral smoothing in short-time spectral attenuation (STSA) algorithms: Results of objective measures and listening tests,” in _Proc. 17th Eur. Signal Process. Conf. (EUSIPCO’09)_ , Aug. 2009, pp. 199–203. 

- [11] H. Gustafsson, S. E. Nordholm, and I. Claesson, “Spectral subtraction using reduced delay convolution and adaptive averaging,” _IEEE Trans. Speech Audio Process._ , vol. 9, no. 8, pp. 799–807, Nov. 2001. 

- [12] C. Breithaupt, T. Gerkmann, and R. Martin, “Cepstral smoothing of spectral filter gains for speech enhancement without musical noise,” _IEEE Signal Process. Lett._ , vol. 14, no. 12, pp. 1036–1039, 2007. 

- [13] C. Breithaupt, T. Gerkmann, and R. Martin, “A novel a priori SNR estimation approach based on selective cepstro-temporal smoothing,” in _Proc. IEEE Int. Conf. Acoust., Speech, Signal Process._ , 2008, pp. 4897–4900. 

- [14] T. Gerkmann and R. Martin, “On the statistics of spectral amplitudes after variance reduction by temporal cepstrum smoothing and cepstral nulling,” _IEEE Trans. Signal Process._ , vol. 57, no. 11, pp. 4165–4174, 2009. 

- [15] S. V. Vaseghi _, Advanced Digital Signal Processing and Noise Reduction_ , 1st ed. Leipzig, Germany: Teubner, 1996. 

- [16] S. V. Vaseghi, “Algorithms for restoration of archived gramophone recordings,” Ph.D. dissertation, Univ. of Cambridge, Cambridge, U.K., 1988. 

- [17] R. Veldhuis _, Restoration of Lost Samples in Digital Signals_ . Englewood Cliffs, NJ, USA: Prentice-Hall, 1990. 

- [18] D. Richter, I. Kurreck, and D. Poetsch, “Restoration of optical variable density sound tracks on motion picture films by digital image processing,” in _Proc. Int. Conf. Optimiz. Elect. Electron. Equipment_ , 2000, vol. 3, pp. 793–798. 

- [19] M. Ruhland, S. Goetze, M. Brandt, S. Doclo, and J. Bitzer, “A new approach for reduction of supergaussian noise using autoregressive interpolation and time-frequency masking,” in _Proc. 13th Int. Workshop Acoust. Echo Noise Control_ , Aachen, Germany, Sep. 2012, pp. 1–4. 

- [20] S. J. Godsill and P. J. W. Rayner _, Digital Audio Restoration_ . London, U.K.: Springer, 1998. 

- [21] J. Nuzman _, Audio Restoration: An Investigation of Digital Methods for Click Removal and Hiss Reduction_ , 2004 [Online]. Available: www. umiacs.umd.edu/jnuzman/audio/audio.pdf, last seen in March 2012 

- [22] M. Kahrs and K. Brandenburg _, Applications of Digital Signal Processing to Audio and Acoustics_ , 1st ed. London, U.K.: Springer, 1998. 

- [23] D. L. Wang, “Time-frequency masking for speech separation and its potential for hearing aid design,” _Trends Ampli fi cat._ , vol. 12, no. 4, pp. 332–353, 2008. 

- [24] A. Czyzewski, “Learning algorithms for audio signal enhancement: Part 1 neural network implementation for the removal of impulse distortions,” _J. Audio Eng. Soc._ , vol. 45, no. 10, pp. 815–831, 1997. 

- [25] D. J. Levitin, P. Chordia, and V. Menon, “Musical rhythm spectra from Bach to Joplin obey a 1/f power law,” in _Proc. Nat. Acad. Sci._ , 2012 [Online]. Available: http://www.pnas.org/content/early/2012/02/ 14/1113828109.abstract, last seen in March 2012 

- [26] M. Ruhland _, Website with Audio Examples to this Paper_ , 2014 [Online]. Available: http://tgm.jade-hs.de/Ruhland_2014_Reduction 

- [27] Y. Hu and P. C. Loizou, “Techniques for estimating the ideal binary mask,” in _Proc. 11th Int. Workshop Acoust. Echo Noise Control_ , 2008. 

- [28] G. Hu and D. L. Wang, “Speech segregation based on pitch tracking and amplitude modulation,” in _Proc. IEEE Workshop Applicat. Signal Process. Audio Acoust._ , 2001, pp. 79–82. 

- [29] D. P. Ellis, “Model-based scene analysis,” in _Computational Auditory Scene Analysis: Principles, Algorithms, and Applications_ . Piscataway, NJ, USA: Wiley/IEEE Press, 2006, pp. 115–147, “,” . 

- [30] I. Kauppinen, “Methods for detecting impulsive noise in speech and audio signals,” in _Proc. Int. Conf. Digital Signal Process._ , 2002, vol. 2, pp. 967–970. 

- [31] S. V. Vaseghi and P. J. W. Rayner, “A new application of adaptive filters for restoration of archived gramophone recordings,” in _Proc. Int. Conf. Acoust., Speech, Signal Process._ , 1988, pp. 2548–2551. 

- [32] S. V. Vaseghi and P. J. W. Rayner, “Detection and suppression of impulsive noise in speech communication systems,” in _Proc. IEEE Commun., Speech, Vis._ , 1990, vol. 137, pp. 38–46. 

- [33] J. G. Proakis and D. K. Manolakis _, Digital Signal Processing_ , 4th ed. Upper Saddle River, NJ, USA: Prentice-Hall, Apr. 2006. 

- [34] N. Jayant, “Average- and median-based smoothing techniques for improving digital speech quality in the presence of transmission errors,” _IEEE Trans. Commun._ , vol. COM-24, no. 9, pp. 1043–1045, Sep. 1976. 

- [35] S. J. Godsill and P. J. W. Rayner, “Frequency-based interpolation of sampled signals with applications in audio restoration,” in _Proc. IEEE Int. Conf. Acoust., Speech, Signal Process._ , 1993, vol. 1, pp. 209–212. 

- [36] A. J. E. M. Janssen, R. Veldhuis, and L. B. Vries, “Adaptive interpolation of discrete-time signals that can be modelled as AR processes,” in _Proc. IEEE Int. Conf. Acoust., Speech, Signal Process._ , 1986, vol. 34, no. 2, pp. 317–330. 

- [37] K.-D. Kammeyer and K. Kroschel _, Digital signal processing– fi ltering and spectral analysis with MATLAB exercises, digitale signalverarbeitung– fi lterung und spektralanalyse mit MATLAB–bungen_ , 8th ed. Wiesbaden, Germany: Vieweg+Teubner-Verlag, 2012. 

- [38] Int. Phonetic Association _, Handbook International Phonetic Association: A Guide to the Use of the International Phonetic Alphabet_ . Cambridge, U.K.: Cambridge Univ. Press, Jun. 1999. 

- [39] J. H. McCulloch _, Alpha-Stable Distributions in MATLAB_ , 1996 [Online]. Available: www.mathworks.com/matlabcentral/fileexchange/ 13619-toolbox-non-local-means/content/toolbox_nlmeans/toolbox/ stabrnd.m, last seen in March 2012 

- [40] P. C. Loizou _, Speech Enhancement: Theory and Practice_ . Boca Raton, FL, USA: CRC Press, 2007. 

- [41] R. Huber and B. Kollmeier, “PEMO-Q - a new method for objective audio quality assessment using a model of auditory perception,” _IEEE Trans. Audio, Speech, Lang. Process._ , vol. 14, no. 6, pp. 1902–1911, Nov. 2006. 

- [42] T. Dau, D. Pueschel, and A. Kohlrausch, “A quantitative model of the “effective” signal processing in the auditory system,” _J. Acoust. Soc._ , vol. 99, no. 6, pp. 3615–3622, 1996. 

- [43] I. Kauppinen and K. Roth, “Improved noise reduction in audio signals using spectral resolution enhancement with time-domain signal extrapolation,” _IEEE Trans. Speech Audio Process._ , vol. 13, no. 6, pp. 1210–1216, 2005. 

- [44] T. Rohdenburg, V. Hohmann, and B. Kollmeier, “Objective perceptual quality measures for the evaluation of noise reduction schemes,” in _Proc. 9th Int. Workshop Acoust. Echo Noise Control_ , 2005, pp. 169–172. 

- [45] A. W. Rix, J. G. Beerends, M. P. Hollier, and A. P. Hekstra, “Perceptual evaluation of speech quality (PESQ) - a new method for speech quality assessment of telephone networks and codecs,” _Speech Commun._ , vol. 2, pp. 749–752, 2001. 

- [46] S. Goetze, V. Mildner, and K.-D. Kammeyer, “A psychoacoustic noise reduction approach for stereo hands-free systems,” in _Proc. 120th Conv. Audio Eng. Soc. (AES)_ , 2006. 

- [47] HörTech _, PEMO-Q (AudioQual and SpeechQual) Audio and Speech Quality Prediction Based on the Oldenburg Perception Model (PEMO) - Manual_ . Oldenburg, Germany: HörTech gGmbH, Kompetenzzentrum für Hörgeraete-Systemtechnik, 2010. 

- [48] B. C. J. Moore _, An Introduction to the Psychology of Hearing_ . Leiden, The Netherlands: Brill, 2012. 

- [49] T. Painter and A. Spanias, “Perceptual coding of digital audio,” _Proc. IEEE_ , vol. 88, no. 4, pp. 451–515, Apr. 2000. 

- [50] S. Goetze, E. Albertin, J. Rennies, E. A. P. Habets, and K.-D. Kammeyer, “Speech quality assessment for listening-room compensation,” _J. Audio Eng. Soc._ , vol. 62, no. 6, pp. 386–399, Jun. 2014. 

- [51] L. L. Thurstone, “A law of comparative judgment,” _Psychol. Rev._ , vol. 34, no. 4, pp. 273–286, 1927. 

- [52] R. A. Bradley and M. E. Terry, “Rank analysis of incomplete block designs: I. The method of paired comparisons,” _Biometrika_ , vol. 39, no. 3/4, p. 324, Dec. 1952. 

- [53] K. Tsukida and M. R. Gupta _, How to analyze paired comparison data_ , May 2011. 

RUHLAND _et al._ : REDUCTION OF GAUSSIAN, SUPERGAUSSIAN AND IMPULSIVE NOISE 

1691 

- [54] ITU-T, “Methods for objective and subjective assessment of quality (P.835),” Nov. 2003. 

- [55] S. R. Quackenbush, T. P. Barnwell III, and M. A. Clements _, Objective Measures of Speech Quality_ . Englewood Cliffs, NJ, USA: PrenticeHall, 1988. 

audio technology in Oldenburg as a Scientific Supervisor and has been the Deputy Head of the Transfer Center for User-Oriented Assistance Systems since 2013. His current research interests include all forms of single- and multichannel speech enhancement, audio restoration, audio effects for musical applications, and information retrieval for large media archives. 

- [56] M. G. Kendall and B. B. Smith, “On the method of paired comparisons,” _Biometrika_ , vol. 31, no. 3/4, pp. 324–345, 1940. 

**Marco Ruhland** studied electrical engineering at the Cooperative State University of Mosbach, Germany. He received his Dipl.-Ing. (BA) degree in 2001. After five years in the electrical construction group of the Michael Weinig AG, Tauberbischofsheim, he studied hearing technology and audiology at the Jade University of Applied Sciences of Oldenburg, Germany, graduating with the B.Eng. in 2010 and continuing with the master studies at the Carl-von-Ossietzy University of Oldenburg, Germany. He received his M.Sc. in 2012 and is now with the Fraunhofer Institute for Digital Media Technology (IDMT), project group Audio Technology for Assistive Systems, in Oldenburg, Germany. His main research interests are on speech enhancement, speech recognition, event detection, and audio restoration algorithms. 

**Joerg Bitzer** received his diploma in 1995 and his doctorate in electrical engineering in 2002 from the University of Bremen where he also was a Research Assistant until 1999. From 2000 to 2003 he was Head of the algorithm development team at Houpert Digital Audio, a company specialized in audio signal processing. Since September 2003, he has been a Professor for audio signal processing at the Jade University of Applied Sciences Wilhelmshaven/Oldenburg/Elsfleth. Additionally, in 2010, he joined the Fraunhofer project group for hearing, speech, and 



**Matthias Brandt** was born in Bremen in 1980. He received his diploma in electrical engineering in 2008 from the University of Bremen, Germany. From 2009 to 2012 he was employed at the Jade University of Applied Sciences Oldenburg, Germany. Since 2012, he has been a Ph.D. student at the University of Oldenburg, Germany, in the field of audio restoration. His research focus is on the processing of music signals–from developing methods to extract parameters required for automatic denoising to creating electronic music in his spare time. 



**Stefan Goetze** is Head of Audio System Technology for Assistive Systems at the Fraunhofer Institute for Digital Media Technology (IDMT), Project group Hearing, Speech and Audio (HSA) in Oldenburg, Germany. He received his Dipl.-Ing. in 2004 and Dr.-Ing. in 2013 at the University of Bremen, Germany, where he was a Research Engineer from 2004 to 2008. His research interests are sound pick/up, processing and enhancement, such as noise reduction, acoustic echo cancellation and dereverberation, as well as assistive technologies, 



human–machine-interaction, detection and classification of acoustic events and automatic speech recognition. He is a Lecturer at the University of Bremen and Project Leader of national and international research projects in the field of acoustics for ambient assisted living (AAL) technologies. He is member of IEEE. 

