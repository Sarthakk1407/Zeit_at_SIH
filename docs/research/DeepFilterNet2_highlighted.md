# **DEEPFILTERNET2: TOWARDS REAL-TIME SPEECH ENHANCEMENT ON EMBEDDED DEVICES FOR FULL-BAND AUDIO** 

_H. Schr¨oter, A. Maier_<sup>_∗_</sup> 

# _A.N. Escalante-B., T. Rosenkranz_ 

Pattern Recognition Lab Friedrich-Alexander-Universit¨at Erlangen-N¨urnberg Erlangen, Germany 

# WS Audiology Research and Development Erlangen, Germany 

## **ABSTRACT** 

Deep learning-based speech enhancement has seen huge improvements and recently also expanded to full band audio (48 kHz). However, many approaches have a rather high computational complexity and require big temporal buffers for real time usage e.g. due to temporal convolutions or attention. Both make those approaches not feasible on embedded devices. This work further extends DeepFilterNet, which exploits harmonic structure of speech allowing for efficient speech enhancement (SE). Several optimizations in the training procedure, data augmentation, and network structure result in state-of-the-art SE performance while reducing the real-time factor to 0 _._ 04 on a notebook Core-i5 CPU. This makes the algorithm applicable to run on embedded devices in real-time. The DeepFilterNet framework can be obtained under an open source license. 

**_Index Terms_ —** DeepFilterNet, speech enhancement, full-band, two-stage modeling 

## **1. INTRODUCTION** 

Recently, deep learning-based speech enhancement have been extended to full-band (48 kHz) [1, 2, 3, 4]. Most SOTA methods perform SE in frequency domain by applying a short-time Fourier transform (STFT) to the noisy audio signal and enhance the signal in an U-Net like deep neural network (DNN). However, many approaches have relatively large computational demands in terms of multiply-accumulate operations (MACs) and memory bandwidth. That is, the higher sampling rate usually requires large FFT windows resulting in a high number of frequency bins which directly translates to a higher number of MACs. 

PercepNet [1] tackles this problem by using a triangular ERB (equivalent rectangular bandwidth) filter bank. Here, the frequency bins of the magnitude spectrogram are logarithmically compressed to 32 ERB bands. However, this only allows real-valued processing which is why PercepNet additionally applies a comb-filter for finer enhancement of periodic component of speech. FRCRN [3] instead splits the frequency bins into 3 channels to reduce the size of the frequency 

> _∗_ A. Maier is the last author of this paper. 

axis. This approaches allows complex processing and prediction of a complex ratio mask (CRM). Similarly, DMF-Net [4] uses a multi-band approach, where the frequency axis is split into 3 bands that are separately processed by different networks. Generally, multi-stage networks like DMF-Net have recently demonstrated their potential compared to single stage approaches. GaGNet [5], for instance, uses two so called glance and gaze stages after a feature extraction stage. The glance module works on a coarse magnitude domain, while the gaze module processes the spectrum in complex domain allowing to reconstruct the spectrum at a finer resolution. 

In this work we extend the work from [2] which also operates in two stages. DeepFilterNet takes advantage of the speech model consisting of a periodic and a stochastic component. The first stage operates in ERB domain, only enhancing the speech envelope, while the second stage uses deep filtering [6, 7] to enhance the periodic component. In this paper, we describe several optimizations resulting in SOTA performance on the Voicebank+Demand [8] and deep noise suppression (DNS) 4 blind test challenge dataset [9]. Moreover, these optimizations lead to an increased run-time performance, making it possible to run the model in real-time on a Raspberry Pi 4. 

## **2. METHODS** 

## **2.1. Signal Model and the DeepFilterNet framework** 

We assume noise and speech to be uncorrelated such as: 



where _s_ ( _t_ ) is a clean speech signal, _n_ ( _t_ ) is an additive noise, and _h_ ( _t_ ) a room impulse response modeling the reverberant environment resulting in a noisy mixture _x_ ( _t_ ). This directly translates to frequency domain: 



where _X_ ( _k, f_ ) is the STFT representation of the time domain signal _x_ ( _t_ ) and _k_ , _f_ are the time and frequency indices. 

In this work, we adopt the two-stage denoising process of DeepFilterNet [2]. That is, the first stage operates in magnitude domain and predicts real-valued gains. The whole first 

978-1-6654-6867-1/22/$31.00 ©2022 European Union 



<!-- Start of picture text -->
x ( t )<br>STFT X  ( k ,f  ) ERB X  erb( k ,b ) Stage 1: Envelope ERB G erb ( k ,b )Apply<br>Features Decoder Gains<br>Encoder Y G ( k ,f  ) y ( t  )<br>Complex DF Deep Y  ( k ,f  ) ISTFT<br>Features Decoder Filter<br>X  df( k ,f df)<br>Stage 2: Periodicity C N ( k + l ,i ,f  df)<br>Fig. 1 . Schematic overview of the DeepFilterNet2 speech enhancement process.<br>stage operates in an compressed ERB domain which serves 0.0010 0.05 128<br>the purpose of reducing computational complexity while 0.0008 0.04 96<br>modeling auditory perception of the human ear. Thus, the<br>0.0006 0.03<br>aim of the first stage is to enhance the speech envelope given 64<br>0.0004 0.02<br>its coarse frequency resolution. The second stage operates in Learning Rate 32<br>0.0002 Weight Decay 0.01 24<br>complex domain utilizing deep filtering [7, 6] and is trying to Batch Size 168<br>reconstruct the periodicity of speech. [2] showed, that deep 0.0000 0 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85 90 95 0.00 0<br>filtering (DF) generally outperforms traditional complex ratio Epochs<br>Batch Size<br>Learning Rate Weight Decay<br><!-- End of picture text -->

stage operates in an compressed ERB domain which serves the purpose of reducing computational complexity while modeling auditory perception of the human ear. Thus, the aim of the first stage is to enhance the speech envelope given its coarse frequency resolution. The second stage operates in complex domain utilizing deep filtering [7, 6] and is trying to reconstruct the periodicity of speech. [2] showed, that deep filtering (DF) generally outperforms traditional complex ratio masks (CRMs) especially in very noisy conditions. 

**Fig. 2** . Learning rate, weight decay and batch size scheduling used for training. 

The combined SE procedure can be formulated as follows. An encoder _F_ enc encodes both ERB and complex features into one embedding _E_ . 

## **2.3. Multi-Target Loss** 



We adopt the spectrogram loss _L_ spec from [2]. Additionally use a multi-resolution (MR) spectrogram loss where the enhancement spectrogram _Y_ ( _k, f_ ) is first transformed into time-domain before computing multiple STFTs with windows from 5 ms to 40 ms [11]. To propagate the gradient for this loss, we use the pytorch STFT/ISTFT, which is numerically sufficiently close to the original DeepFilterNet processing loop implemented in Rust. 

Next, the first stage predicts real-valued gains _G_ and enhances the speech envelope resulting in the short-time spectrum _YG_ . 



Finally in the second stage, _F_ df dec<sup>predictsDFcoefficients</sup> _C_ df<sup>_N_of order</sup><sup>_N_which are then linearly applied to</sup><sup>_YG_.</sup> 





where _Yi_<sup>_′_= STFT</sup><sup>_i_(</sup><sup>_y_) is the i-th STFT with window sizes in</sup> _{_ 5 _,_ 10 _,_ 20 _,_ 40 _}_ ms of the predicted TD signal _y_ , and _c_ = 0 _._ 3 is a compression parameter [1]. Compared to DeepFilterNet [2], we drop the _α_ loss term since the employed heuristic is only a poor approximation of the local speeech periodicity. Also, DF may enhance speech in non-voiced sections and can disable its effect by setting the real part of the coefficient at _t_ 0 to 1 and the remaining coefficients to 0. The combined multi-target loss is given by: 

where _l_ is the DF look-ahead. As stated before, the second stage only operates on the lower part of the spectrogram up to a frequency _f_ df = 5 kHz. The DeepFilterNet2 framework is visualized in Fig. 1. 

## **2.2. Training Procedure** 



In DeepFilterNet [2], we used an exponential learning rate schedule and fixed weight decay. In this work, we additionally use a learning rate warmup of 3 epochs followed by a cosine decay. Most importantly, we update the learning rate at every iteration, instead of after each epoch. Similarly, we schedule the weight decay with an increasing cosine schedule resulting in a larger regularization for the later stages of the training. Finally, to achieve faster convergence especially in the beginning of the training, we use batch scheduling [10] starting with a batch size of 8 and gradually increasing it to 96. The scheduling scheme can be observed in Fig. 2. 

## **2.4. Data and Augmentation** 

While DeepFilterNet was trained on the deep noise suppression (DNS) 3 challenge dataset [12], we train DeepFilterNet2 on the english part of DNS4 [9] which contains more fullband noise and speech samples. 

In speech enhancement, usually only background noise and in some cases reverberation is reduced [1, 11, 2]. In this work, we further extended the SE concept to declipping. Therefore, we distinguish between _augmentations_ and _distortions_ in the 

on-the-fly data pre-processing pipeline. Augmentations are applied to speech and noise samples with the aim of further extending the data distributions the network observes during training. Distortions, on the other hand, are only applied to speech samples for noisy mixture creation. The clean speech target is not affected by a distortion transform. Thus, the DNN learns to reconstruct the original, undistorted speech signal. Currently, the DeepFilterNet framework supports the following randomized _augmentations_ : 

   - Random 2nd order filtering [13] 

   - Gain changes 

   - Equalizer via 2nd order filters 

   - Resampling for speed and pitch changes [13] 

- Addition of colored noise (not used for speech samples) 

- Additionally to denoising, DeepFilterNet will try to revert the following _distortions_ : 

   - Reverberation; the target signal will contain a smaller amount of reverberation by decaying the room transfer function. 



<!-- Start of picture text -->
Complex ERB ERB DF<br>Features Features Gains Coefs<br>Conv Conv PConv Conv +<br>Conv Conv PConv TConv GLinear<br>GLinear Conv PConv TConv 2 ⨉ GRU<br>Conv PConv TConv GLinear<br>C GLinear<br>GLinear 1 ⨉ GRU 2 ⨉ GRU<br>Encoder ERB Decoder DF Decoder<br>PConv<br><!-- End of picture text -->

**Fig. 3** . DeepFilterNet2 architecture. 

convolutions, the vast amount of parameters and FLOPs is located at the 1 _×_ 1 convolutions. Thus, adding grouping to pathway convolutions (PConv) results in a great parameter reduction while not losing any significant SE performance. 

- Clipping artifacts with SNRs in [20 _,_ 0]dB. 

## **2.6. Post-Filter** 

## **2.5. DNN** 

We keep the general convolutional U-Net structure of DeepFilterNet [2], but make the following adjustments. The final architecture is shown in Fig. 3. 

1. _Unification of the encoder_ . Convolutions for both ERB and complex features are now processed within the encoder, concatenated, and passed to a grouped linear (GLinear) layer and single GRU. 

2. _Simplify Grouping_ . Previously, grouping of linear and GRU layers was implemented via separate smaller layers which results in a relatively high processing overhead. In DeepFilterNet2, only linear layers are grouped over the frequency axis, implemented via a single matrix multiplication. The GRU hidden dim was instead reduced to 256. We also apply grouping in the output layer of the DF decoder with the incentive that the neighboring frequencies are sufficient for predicting the filter coefficients. This greatly reduces run-time, while only minimaly increasing the number of FLOPs. 

3. _Reduction of temporal kernels_ . While temporal convolutions (TCN) or temporal attention have been successfully applied to SE, they require temporal buffers during realtime inference. This can be efficiently implemented via ring buffers, however, the buffers need to be held in memory. This additional memory access may result in bandwidth being the limiting bottleneck, which could be the case especially for embedded devices. Therefore, we reduce the kernel size of the convolutions and transposed convolutions from 2 _×_ 3 to 1 _×_ 3, that is 1D over frequency axis. Only the input layer now incorporates temporal context via a causal 3 _×_ 3 convolution. This drastically reduces the use of temporal buffers during real-time inference. 

4. _Depthwise pathway convolutions_ . When using separable 

We adopt the post-filter, first proposed by Valin et al. [1], with the aim of slightly over-attenuating noisy TF bins while adding some gain back to less noisy bins. We perform this on the predicted gains in the first stage: 



## **3. EXPERIMENTS** 

## **3.1. Implementation details** 

As stated in section 2.4, we train DeepFilterNet2 on DNS4 dataset using overall more than 500 h of full-band clean speech, approx. 150 h of noise as well as 150 real and 60 000 simulated HRTFs. We split the data into train, validation and test sets (70 %, 15 %, 15 %). The Voicebank set was split speaker-exclusive with no overlap with test set. We evaluate our approach on the Voicebank+Demand test set [8] as well as the DNS4 blind test set [9]. We train the model with AdamW for 100 epochs and select the best model based on the validation loss. 

In this work, we use 20 ms windows, an overlap of 50 %, and a look-ahead of two frames resulting in an overall algorithmic delay of 40 ms. We take 32 ERB bands, _f_ DF = 5 kHz, a DF order of _N_ = 5, and a look-ahead _l_ = 2 frames. The loss parameters _λ_ spec = 1 _e_ 3 and _λ_ MR = 5 _e_ 2 are chosen so that both losses result in the same order of magnitude. The source code and a pretrained DeepFilterNet2 can be obtained at https://github.com/Rikorose/ DeepFilterNet. 

**Table 1** . Objective results on Voicebank+Demand test set. Real-time factors (RTFs) are measured on a notebook Core i5-8250U CPU by taking the average over 5 runs. Unreported values of related work are indicated as “-”. 

||Model|Params[M]|MACS[G]|RTF|PESQ|CSIG|CBAK|COVL|STOI|
|---|---|---|---|---|---|---|---|---|---|
||Noisy|-|-|-<br>|1_._97|3_._34|2_._44|2_._63|0_._921|
||RNNoise [13]<sup>_a_</sup>|**0****_._06**|**0****_._04**|0_._03<sup>_b_</sup>|2_._33|3_._40|2_._51|2_._84|0_._922|
||NSNet2 [14]|6_._17|0_._43|**0****_._02**|2_._47|3_._23|2_._99|2_._90|0_._903|
||PercepNet [1]<br>|8_._00|0_._80|-|2_._73|-|-|-|-|
||DCCRN [15] <sup>_c d_</sup>|3_._70|14_._36|2_._19|2_._54|3_._74|3_._13|2_._75|0_._938|
||DCCRN+ [17]|3_._30|-|-|2_._84|-|-|-|-|
||S-DCCRN [16]|2_._34|-|-|2_._84|4_._03|3_._43|2_._97|0_._940|
||FullSubNet+ [18] <sup>_e_</sup><br>|8_._67|30_._06|0_._55|2_._88|3_._86|3_._42|3_._57|0_._940|
||GaGNet [5]<sup>_f_</sup>|5_._95|1_._65|0_._05|2_._94|**4****_._26**|3_._45|3_._59|-|
||DMF-Net [4]|7_._84|-|-|2_._97|**4****_._26**|3_._52|3_._62|**0****_._944**|
||FRCRN [3]|10_._27|12_._30|-|**3****_._21**|4_._23|**3****_._64**|**3****_._73**|-|
||DeepFilterNet [2]|**1****_._78**|**0****_._35**|0_._11|2_._81|4_._14|3_._31|3_._46|0_._942|
|<br>|+ Scheduling scheme|**1****_._78**|**0****_._35**|0_._11|2_._92|4_._22|3_._39|3_._58|0_._941|
|sed<br><br><br><br>|+ MR Spec-Loss|**1****_._78**|**0****_._35**|0_._11|2_._98|4_._20|3_._41|3_._60|0_._942|
|po<br>|+ Improved Data & Augmentation|**1****_._78**|**0****_._35**|0_._11|3_._04|**4****_._30**|3_._38|3_._67|0_._942|
|pro<br><br><br><br>|+ Simplifed DNN|2_._31|0_._36|**0****_._04**|**3****_._08**|**4****_._30**|**3****_._40**|**3****_._70**|**0****_._943**|
||+ Post-Filter|2_._31|0_._36|**0****_._04**|3_._03|3_._72|3_._37|3_._63|0_._941|



> _a_ Metrics and RTF measured with source code and weights provided at https://github.com/xiph/rnnoise/ 

> _b_ Note, that RNNoise runs single-threaded 

> _c_ RTF measured with source code provided at https://github.com/huyanxin/DeepComplexCRN 

> _d_ Composite and STOI metrics provided by the same authors in [16] 

> _e_ Metrics and RTF measured with source code and weights provided at https://github.com/hit-thusz-RookieCJ/FullSubNet-plus 

> _f_ RTF measured with source code provided at https://github.com/Andong-Li-speech/GaGNet/ 

**Table 2** . DNSMOS results on the DNS4 blind test set. 

|Model|SIGMOS|BAKMOS|OVLMOS|
|---|---|---|---|
|Noisy|4_._14|2_._94|3_._29|
|RNNoise [13]|3_._88|3_._69|3_._38|
|NSNet2 [14]|3_._87|4_._21|3_._59|
|FullSubNet+ [18]|**4****_._22**|4_._12|3_._75|
|DeepFilterNet [2]|4_._14|4_._18|3_._75|
|DeepFilterNet2|4_._20|4_._43|3_._88|
|+ Post-Filter|4_._19|**4****_._47**|**3****_._90**|



is able to obtain best results in most metrics, but has a high computational complexity not feasible for embedded devices. 

Table 2 shows DNSMOS P.835 [22] results on the DNS4 blind test set. While DeepFilterNet [2] was not able to enhance the speech quality mean opinion score (SIGMOS), with DeepFilterNet2 we obtain good results also for background and overall MOS values. Moreover, DeepFilterNet2 comes relatively close to the minimum DNSMOS values that were used to select clean speech samples to train the DNS4 baseline NSNet2 (SIG=4.2, BAK=4.5, OVL=4.0) [9] further emphasizing its good SE performance. 

## **3.2. Results** 

## **4. CONCLUSION** 

We evaluate the speech enhancement performance of DeepFilterNet2 using the Valentini Voicebank+Demand test set [8]. Therefore, we chose WB-PESQ [19], STOI [20] and the composite metrics CSIG, CBAK, COVL [21]. Table 1 shows DeepFilterNet2 results in comparison with other stateof-the-art (SOTA) methods. One can find that DeepFilterNet2 achieves SOTA-level results while requiring a minimal amount of multiply-accumulate operation per second (MACS). The number of parameters has slightly increased over DeepFilterNet (Sec. 2.5), but the network is able to run more than twice as fast and achieves a 0 _._ 27 higher PESQ score. GaGNet [5] achieves a similar RTF while having good SE performance. However, it only runs fast when provided with the whole audio and requires large temporal buffers due to its usage of big temporal convolution kernels. FRCRN [3] 

In this work, we presented DeepFilterNet2, a low-complexity speech enhancement framework. Taking advantage from DeepFilterNet’s perceptual approach, we were able to further apply several optimizations resulting in SOTA SE performance. Due to its lightweight architecture, it can be run on a Raspberry Pi 4 with a real-time factor of 0 _._ 42. In future work, we plan to extend the idea of speech enhancement to other enhancements, like correcting lowpass characteristics due to the current room environment. 

## **5. REFERENCES** 

- [1] Jean-Marc Valin, Umut Isik, Neerad Phansalkar, Ritwik Giri, Karim Helwani, and Arvindh Krishnaswamy, “A 

Perceptually-Motivated Approach for Low-Complexity, Real-Time Enhancement of Fullband Speech,” in _INTERSPEECH 2020_ , 2020. 

- [2] Hendrik Schr¨oter, Alberto N Escalante-B, Tobias Rosenkranz, and Andreas Maier, “DeepFilterNet: A low complexity speech enhancement framework for fullband audio based on deep filtering,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022. 

- [3] Shengkui Zhao, Bin Ma, Karn N Watcharasupat, and Woon-Seng Gan, “FRCRN: Boosting feature representation using frequency recurrence for monaural speech enhancement,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022. 

- [4] Guochen Yu, Yuansheng Guan, Weixin Meng, Chengshi Zheng, and Hui Wang, “DMF-Net: A decoupling-style multi-band fusion model for real-time full-band speech enhancement,” _arXiv preprint arXiv:2203.00472_ , 2022. 

- [5] Andong Li, Chengshi Zheng, Lu Zhang, and Xiaodong Li, “Glance and gaze: A collaborative learning framework for single-channel speech enhancement,” _Applied Acoustics_ , vol. 187, 2022. 

- [6] Hendrik Schr¨oter, Tobias Rosenkranz, Alberto Escalante Banuelos, Marc Aubreville, and Andreas Maier, “CLCNet: Deep learning-based noise reduction for hearing aids using complex linear coding,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ , 2020. 

- [7] Wolfgang Mack and Emanu¨el AP Habets, “Deep Filtering: Signal Extraction and Reconstruction Using Complex Time-Frequency Filters,” _IEEE Signal Processing Letters_ , vol. 27, 2020. 

- [8] Cassia Valentini-Botinhao, Xin Wang, Shinji Takaki, and Junichi Yamagishi, “Investigating RNN-based speech enhancement methods for noise-robust Text-toSpeech,” in _SSW_ , 2016. 

- [9] Harishchandra Dubey, Vishak Gopal, Ross Cutler, Ashkan Aazami, Sergiy Matusevych, Sebastian Braun, Sefik Emre Eskimez, Manthan Thakker, Takuya Yoshioka, Hannes Gamper, et al., “ICASSP 2022 deep noise suppression challenge,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022. 

- [10] Samuel L Smith, Pieter-Jan Kindermans, Chris Ying, and Quoc V Le, “Don’t decay the learning rate, increase the batch size,” _arXiv preprint arXiv:1711.00489_ , 2017. 

- [11] Hyeong-Seok Choi, Sungjin Park, Jie Hwan Lee, Hoon Heo, Dongsuk Jeon, and Kyogu Lee, “Real-time denoising and dereverberation wtih tiny recurrent u-net,” in _International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2021. 

- [12] Chandan KA Reddy, Harishchandra Dubey, Kazuhito Koishida, Arun Nair, Vishak Gopal, Ross Cutler, Sebastian Braun, Hannes Gamper, Robert Aichner, and Sriram Srinivasan, “Interspeech 2021 deep noise suppression challenge,” in _INTERSPEECH_ , 2021. 

- [13] Jean-Marc Valin, “A hybrid dsp/deep learning approach to real-time full-band speech enhancement,” in _2018 IEEE 20th international workshop on multimedia signal processing (MMSP)_ . IEEE, 2018. 

- [14] Sebastian Braun, Hannes Gamper, Chandan KA Reddy, and Ivan Tashev, “Towards efficient models for realtime deep noise suppression,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2021. 

- [15] Yanxin Hu, Yun Liu, Shubo Lv, Mengtao Xing, Shimin Zhang, Yihui Fu, Jian Wu, Bihong Zhang, and Lei Xie, “DCCRN: Deep complex convolution recurrent network for phase-aware speech enhancement,” in _INTERSPEECH_ , 2020. 

- [16] Shubo Lv, Yihui Fu, Mengtao Xing, Jiayao Sun, Lei Xie, Jun Huang, Yannan Wang, and Tao Yu, “SDCCRN: Super wide band dccrn with learnable complex feature for speech enhancement,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022. 

- [17] Shubo Lv, Yanxin Hu, Shimin Zhang, and Lei Xie, “DCCRN+: Channel-wise Subband DCCRN with SNR Estimation for Speech Enhancement,” in _INTERSPEECH_ , 2021. 

- [18] Jun Chen, Zilin Wang, Deyi Tuo, Zhiyong Wu, Shiyin Kang, and Helen Meng, “FullSubNet+: Channel attention fullsubnet with complex spectrograms for speech enhancement,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022. 

- [19] ITU, “Wideband extension to Recommendation P.862 for the assessment of wideband telephone networks and speech codecs,” _ITU-T Recommendation P.862.2_ , 2007. 

- [20] Cees H Taal, Richard C Hendriks, Richard Heusdens, and Jesper Jensen, “An algorithm for intelligibility prediction of time–frequency weighted noisy speech,” _IEEE Transactions on Audio, Speech, and Language Processing_ , 2011. 

- [21] Yi Hu and Philipos C Loizou, “Evaluation of objective quality measures for speech enhancement,” _IEEE Transactions on audio, speech, and language processing_ , 2007. 

- [22] Chandan KA Reddy, Vishak Gopal, and Ross Cutler, “Dnsmos p. 835: A non-intrusive perceptual objective speech quality metric to evaluate noise suppressors,” in _IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022. 

