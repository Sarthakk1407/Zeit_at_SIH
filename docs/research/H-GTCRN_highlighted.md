

<!-- Start of picture text -->
Noisy 1 Separated noise<br>2 Pa<br>* +<br>z2z= FsSy<br>aa0<br>3 8<br>=Zz &Ez_<br>~12 3 4 1 2 3 4<br>Time (s) Time (s)<br>co Noisy 2 oo Separated speech<br>* 7<br>F Fl<br>a a<br>355aaa)2aazg35<br>c 5 P fiat<br>° ahovrebciehit wan moweratiaie setnn °<br>1 2 3 4 1 2 3 4<br>Time (s) Time (s)<br><!-- End of picture text -->



<!-- Start of picture text -->
Masking 1<br>ee Encoder H<br>' t (3) 3 |!<br>} i| 38 2<br>i — > @ : | g 8 :<br>¥1 H H i |> tla 7 a<br>7 rs fs Ba '‘ETREHHlolile{lo onELHS|} & <)-{isTET}—-%<br>| t H H i |<br>||Po OO SEE. EESH\ DualEncoder / cee: /i x2EE4iDecoderx3 x2 }! Cl!|! © & Element-wise_ couetenntion;  product:<br><!-- End of picture text -->



<!-- Start of picture text -->
ty —. Re) }<br>H<br><!-- End of picture text -->



<!-- Start of picture text -->
H\ al;<br>1|2 5 1<br>i]s}ere\ o“encesI2hi5 J<br><!-- End of picture text -->







## **3.3. Encoder and decoder** 

We explore two types of encoder frameworks: single encoder and dual encoder [20]. As depicted in Figure 2c, every encoder consists of two convolution (Conv) blocks, with each block consisting of a convolution layer, a batch normalization, and a PReLU activation, along with three grouped temporal convolution (GT-Conv) blocks [10]. The GT-Conv blocks enhance long-range temporal dependency modeling by incorporating temporal dilation into depth-wise convolutions. They split the input features into two branches, one of which undergoes a sequence of two 2D point-wise convolutions (P-Conv2D) layers and a 2D dilated depth-wise convolution (DD-Conv2D) layer. The outputs of both branches are then concatenated, and a channel shuffle operation facilitates information exchange between them. The decoder mirrors the encoder’s structure, with the Conv blocks replaced by DeConv blocks, where the convolution layers are substituted with transposed convolution layers. Additionally, the activation of the last DeConv block is replaced by tanh to constrain output values within the range of ( _−_ 1 _,_ 1). 

## **3.4. Grouped DPRNN** 

The combined grouped RNN (GRNN) and DPRNN [21] architecture, referred to as G-DPRNN [10], splits the input features into two disjoint groups. Each group is then processed by a recurrent layer, followed by a representation rearrangement layer to obtain output features. For intra-frame modeling, we utilize grouped bidirectional GRUs to capture the spectral patterns within a single frame. For inter-frame modeling, we employ grouped unidirectional GRUs to exploit the temporal dependencies within a specific frequency bin. 

## **3.5. Loss function** 

Our model is trained on the hybrid loss function, which consists of scale-invariant signal-to-noise ratio (SISNR) loss and complex compressed mean-squared error (ccMSE) loss [22]. The overall loss function is given by 



where _x_ ˆ and _x_ denote the enhanced and target waveform, _X_<sup>ˆ</sup> and _X_ denote the complex spectrogram of the enhanced and target, respectively. _α_ and _β_ are the weighting factors, which are respectively set to 0.01 and 0.3 in this work. 

Each term in the aforementioned formula is calculated as follows: 







# **4. Experiment** 

## **4.1. Dataset** 

We generate the simulated dataset with the image method [23], with dual-channel RIRs based on a linear array with two microphones placed 4 cm apart. The room size ranges from 3 m _×_ 3 m _×_ 2.5 m to 10 m _×_ 10 m _×_ 3 m, and the reverberation time (RT60) ranges from 0.1 s to 0.4 s. The distance from the source to the array is randomly selected from _{_ 0.5 m, 1 m, 2 m, 3 m _}_ , with the direction of arrival (DOA) difference between the target speech and interference noise being greater than 5 °. We convolve the speech dataset from the DNS-3 challenge [24] with these dual-channel RIRs to generate the simulated speech signals. The early reflection (50 ms) of the first channel is preserved as the training target. For the noise signals, we select data from the DNS-3 and DCASE [25] datasets. During training, the SNR ranges from −10 dB to 0 dB. The validation set maintains this range of SNR, with 500 noisy-clean pairs in each case. For the test set, we set three SNR levels: −12.5 dB, −7.5 dB, and −2.5 dB, each with 500 noisy-clean pairs. All utterances are sampled at 16 kHz. 

## **4.2. Implementation details** 

The STFT is performed using a square root Hanning window of a length of 512 (32 ms) and a hop length of 256 (16 ms). In the BM module, 192 high-frequency bands are mapped to 64 ERB bands, while 65 low-frequency bands keep unaltered. For the SFE module, a kernel size of 3 is used. The two Conv blocks share a common output channel number of 16 for the single encoder case and 12 for the dual encoder case, ensuring comparable computational complexity for a fair comparison. The kernel size is set to (1,5) with a stride of (1,2), while the second layer uses a group size of 2 to reduce computational complexity. The DD-Conv2D layers in the three GT-Conv blocks have a common channel number of 16, with a kernel size of (3,3), and time dilation values of 1,2 and 5, respectively. 

The models are trained using the Adam optimizer [26] with a warm-up phase. The linear-warm-up-cosine-annealinglearning-rate scheduler is employed, where the learning rate increases linearly during the initial training phase and decreases following a cosine function. In our training, the batch size is set to 8, and the number of steps for each epoch is 1250. The number of warm-up steps and total steps are set to 25000 (20 epochs) and 250000 (200 epochs), respectively. The minimum and maximum learning rates are set to 10<sup>_−_6</sup> and 10<sup>_−_3</sup> . 

# **5. Results** 

## **5.1. Evaluation metrics** 

The evaluation is conducted using the objective metrics, including perceptual evaluation of speech quality (PESQ) [27] and short-time objective intelligibility (STOI) [28]. Additionally, DNN-based non-intrusive subjective metrics DNSMOS P.808 [29] and DNSMOS P.835 [30] are also employed. 

## **5.2. Ablation study** 

We conduct an ablation study on our modified GTCRN to evaluate the impact of various factors, including the use of speech and noise information from IVA, the type of feature, the type of masking approach, and the adoption of the dual-encoder, as shown in Table 1. We compare the performance of different masking approaches, as seen in IDs 1 and 2, IDs 3 and 5, and 

Table 1: _Results of the ablation study on the simulated validation set._ **_BOLD_** _indicates the best score in each metric._ 

|Metrics||||||||PESQ|STOI(_×_100)|DNSMOS-|P.808|SIG|DNSMOS<br>BAK|-|P.835<br>OVRL|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|IDs||Met|hods|||Para. (k)|MACs (M/|s)||||||||
|-||No|isy|||-|-|1.08|55.48|2.19||1.21|1.16||1.10|
|1|IVA-|S+Complex F|eature+|Maskin|g 1|24.39|43.20|1.46|77.83|3.01||2.37|3.76||2.11|
|2|<br>IVA-|<br>S+Complex F|<br>eature+|<br>Maskin|<br>g 2|24.39|43.20|1.51|79.13|3.17||2.59|3.77||2.28|
|3|<br>IV|<br>A-S+LPS Fea|<br>ture+M|<br>asking 1|<br>|24.15|41.44|1.49|78.64|3.11||2.35|3.76||2.09|
|4|<br>IVA-|<br>S&N+LPS F|<br>eature+|<br>Masking|<br>1|24.39|43.20|1.53|79.63|3.11||2.37|3.76||2.11|
|5|IV|A-S+LPS Fea|ture+M|asking 2||24.15|41.44|1.57|79.11|3.25||**2.61**|3.81||2.31|
|6|IVA-|S&N+LPS F|eature+|Masking|2|24.39|43.20|**1.61**|79.57|**3.29**||2.60|**3.83**||**2.32**|
|7<br>IV<br>Tab|A-S&N+L<br>le 2: _Re_|PS Feature+<br>_sults comp_|Maskin<br>_ariso_|g 2+Dua<br>_n with_|l-Encoder<br>_baselines_|25.57<br>_on the_|45.63<br>_simulated t_|1.60<br>_est set._ **_BO_**|**79.99**<br>**_LD_**_indicate_|3.26<br>_s the best sc_|_ore i_|2.56<br>_n each_|3.78<br>_metric_|_._|2.28|
|Metrics||||PESQ||STOI(_×_100|)<br>DN|SMOS-P.808|DNSMOS-SI|G<br>DNS|MOS-BA|K|DNSMO|S|-OVRL|
|SNR (dB)|Para. (k)|MACs (M/s)|-12.5|-7.5|-2.5<br>-12.5|-7.5|-2.5<br>-12.5|-7.5<br>-2.5|-12.5<br>-7.5|-2.5<br>-12.5|-7.5|-2.5|-12.5<br>-|7.|5<br>-2.5|
|Noisy|-|-|1.05|1.05|1.06<br>42.00|50.46|61.07<br>2.17|2.17<br>2.20|1.17<br>1.19|1.25<br>1.14|1.14|1.18|1.08<br>1|.0|9<br>1.12|
|Aux-IVA|-|-|1.07|1.13|1.20<br>62.52|70.22|73.37<br>2.36|2.53<br>2.66|1.61<br>2.00|2.24<br>1.40|1.67|1.93|1.31<br>1|.5|3<br>1.72|
|GTCRN|23.43|32.07|1.09|1.16|1.31<br>47.46|61.12|72.94<br>2.39|2.60<br>2.90|1.73<br>1.99|2.36<br>3.43|3.65|3.79|1.49<br>1|.7|5<br>2.09|
|DC-GTCRN|23.91|35.59|1.15|1.29|1.50<br>60.21|71.27|79.69<br>2.57|2.81<br>3.09|1.82<br>2.14|2.50<br>3.56|3.71|3.82|1.61<br>1|.9|0<br>2.22|
|DC-GTCRN-L|34.80|49.10|1.17|1.32|1.54<br>61.16|72.13|80.39<br>2.59|2.86<br>3.14|1.88<br>2.21|2.56<br>3.60|3.75|3.85|1.66<br>1|.9|6<br>2.28|
|**Proposed**|24.39|43.20|**1.39**|**1.58**|**1.71**<br>**72.38**|**79.01**|**81.96**<br>**3.03**|**3.26**<br>**3.39**|**2.36**<br>**2.62**|**2.74**<br>**3.76**|**3.85**|**3.87**|**2.09**<br>**2**|**.3**|**4**<br>**2.44**|



IDs 4 and 6. It is clear that Masking 2 (IDs 2, 5, 6) outperforms Masking 1 (IDs 1, 3, 4), which can be attributed to the coarse estimation and speech preservation provided by IVA. A comparison between ID-1 and ID-3 highlights the effectiveness of the LPS feature, which improves all metrics, indicating that phase information is not as crucial. Compared to ID-5, the inclusion of the noise information provided by IVA (ID-6) leads to substantial improvements in nearly all metrics, despite a slight degradation in SIG is observed. This is because the two separated signals allow for a more comprehensive capture of the noisy mixture, while the speech channel focuses solely on the speech component. Finally, the results for ID-7 exhibit noticeable declines across most metrics, despite a marginal improvement in STOI over ID-6. We attribute this to the computational limitations of our lightweight network, which restrict the ability to fully leverage the potential benefits of the dual-encoder framework. Consequently, we select the best-performing method in the table (ID-6) for comparison with the baseline models. 

## **5.3. Results comparison with baselines** 

Four methods are selected as baselines: (a) Aux-IVA, (b) GTCRN, (c) DC-GTCRN, a dual-channel version of GTCRN, and (d) DC-GTCRN-L, a larger-scale version of DC-GTCRN. The results of the simulated test set are presented in Table 2. Compared to the noisy mixture, the output of Aux-IVA shows a significant improvement in the STOI metric, demonstrating its effectiveness in preserving speech while suppressing noise. By incorporating the second channel input, DC-GTCRN leverages additional inter-channel information, such as phase differences, leading to significant improvements across all evaluation metrics compared to GTCRN, which shows limited performance in low SNR conditions. Although DC-GTCRN-L achieves improved performance with an increased number of parameters, the performance gap between this baseline and our proposed method remains substantial, even with the additional computational overhead. By integrating Aux-IVA, our proposed method attains the highest scores, further validating the efficacy of auxiliary information and underscoring the superiority of our hybrid approach. The parameters and computational loads reported in the table include the Aux-IVA module, which contributes a negligible increase in parameters and only 0.20 MMACs per second per iteration. 













Figure 3: _Typical spectrograms_ 

A set of typical audio samples is presented in Figure 3, clearly demonstrating that our proposed method excels in both speech preservation and noise suppression. The original noisy spectrogram is predominantly dominated by noise, making it difficult to identify speech components. It is evident that the baseline models fail to effectively enhance speech under such low SNR conditions. In contrast, the Aux-IVA result extracts speech components despite some residual noise, while our method’s enhanced result more effectively suppresses noise, and retains more speech details, including harmonic components, further highlighting its effectiveness. Audio samples are available: https://github.com/Max1Wz/H-GTCRN. 

# **6. Conclusion** 

In this paper, we propose a hybrid dual-channel speech enhancement system designed for low-SNR conditions, integrating IVA and a modified GTCRN. Aux-IVA acts as a coarse estimator, providing auxiliary information, while the GTCRN further refines the speech quality. Through various architecture modifications, both the original and auxiliary information are fully leveraged. With only a minimal increase in parameters and computational complexity, the proposed system effectively enhances speech. Experimental results validate its effectiveness. 

# **7. Acknowledgements** 

This work is supported by the National Natural Science Foundation of China (Grant No. 12274221) and the AI & AI for Science Project of Nanjing University. 

# **8. References** 

- [1] K. Tan, X. Zhang, and D. Wang, “Real-time speech enhancement using an efficient convolutional recurrent network for dualmicrophone mobile phones in close-talk scenarios,” in _ICASSP 2019-2019 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2019, pp. 5751–5755. 

- [2] Y. Li, F. Chen, Z. Sun, J. Ji, W. Jia, and Z. Wang, “A smart binaural hearing aid architecture leveraging a smartphone app with deeplearning speech enhancement,” _IEEE Access_ , vol. 8, pp. 56 798– 56 810, 2020. 

- [3] N. Modhave, Y. Karuna, and S. Tonde, “Design of matrix wiener filter for noise reduction and speech enhancement in hearing aids,” in _2016 IEEE International Conference on Recent Trends in Electronics, Information & Communication Technology (RTEICT)_ . IEEE, 2016, pp. 843–847. 

- [4] X. Hao, X. Su, Z. Wang, H. Zhang, and Batushiren, “Unetgan: A robust speech enhancement approach in time domain for extremely low signal-to-noise ratio condition,” in _Interspeech 2019_ , 2019, pp. 1786–1790. 

- [5] X. Hao, X. Su, S. Wen, Z. Wang, Y. Pan, F. Bao, and W. Chen, “Masking and inpainting: A two-stage speech enhancement approach for low snr and non-stationary noise,” in _ICASSP 20202020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2020, pp. 6959–6963. 

- [6] Z. Hou, T. Lei, Q. Hu, Z. Cao, M. Tang, and J. Lu, “Snrprogressive model with harmonic compensation for low-snr speech enhancement,” _IEEE Signal Processing Letters_ , 2024. 

- [7] X. Le, T. Lei, L. Chen, Y. Guo, C. He, C. Chen, X. Xia, H. Gao, Y. Xiao, P. Ding, S. Song, and J. Lu, “Harmonic enhancement using learnable comb filter for light-weight full-band speech enhancement model,” in _Interspeech 2023_ , 2023, pp. 3894–3898. 

- [8] Z. Zhang, Y. Xu, M. Yu, S.-X. Zhang, L. Chen, and D. Yu, “Adlmvdr: All deep learning mvdr beamformer for target speech separation,” in _ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2021, pp. 6089–6093. 

- [9] J.-M. Valin, “A hybrid dsp/deep learning approach to real-time full-band speech enhancement,” in _2018 IEEE 20th international workshop on multimedia signal processing (MMSP)_ . IEEE, 2018, pp. 1–5. 

- [10] X. Rong, T. Sun, X. Zhang, Y. Hu, C. Zhu, and J. Lu, “Gtcrn: A speech enhancement model requiring ultralow computational resources,” in _ICASSP 2024-2024 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2024, pp. 971–975. 

- [11] X. Le, H. Chen, K. Chen, and J. Lu, “DPCRN: Dual-Path Convolution Recurrent Network for Single Channel Speech Enhancement,” in _Interspeech 2021_ , 2021, pp. 2811–2815. 

- [12] N. Ma, X. Zhang, H.-T. Zheng, and J. Sun, “Shufflenet v2: Practical guidelines for efficient cnn architecture design,” in _Proceedings of the European conference on computer vision (ECCV)_ , 2018, pp. 116–131. 

- [13] F. Gao, L. Wu, L. Zhao, T. Qin, X. Cheng, and T.-Y. Liu, “Efficient sequence learning with group recurrent networks,” in _Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)_ , 2018, pp. 799–808. 

- [14] T. Kim, T. Eltoft, and T.-W. Lee, “Independent vector analysis: An extension of ica to multivariate components,” in _International conference on independent component analysis and signal separation_ . Springer, 2006, pp. 165–172. 

- [15] T. Kim, H. T. Attias, S.-Y. Lee, and T.-W. Lee, “Blind source separation exploiting higher-order frequency dependencies,” _IEEE transactions on audio, speech, and language processing_ , vol. 15, no. 1, pp. 70–79, 2006. 

- [16] H. Ruan, L. Liao, K. Chen, and J. Lu, “Speech extraction under extremely low snr conditions,” _Applied Acoustics_ , vol. 224, p. 110149, 2024. 

- [17] D. S. Williamson, Y. Wang, and D. Wang, “Complex ratio masking for monaural speech separation,” _IEEE/ACM transactions on audio, speech, and language processing_ , vol. 24, no. 3, pp. 483– 492, 2015. 

- [18] N. Ono, “Stable and fast update rules for independent vector analysis based on auxiliary function technique,” in _2011 IEEE Workshop on Applications of Signal Processing to Audio and Acoustics (WASPAA)_ . IEEE, 2011, pp. 189–192. 

- [19] T. Taniguchi, N. Ono, A. Kawamura, and S. Sagayama, “An auxiliary-function approach to online independent vector analysis for real-time blind source separation,” in _2014 4th Joint Workshop on Hands-free Speech Communication and Microphone Arrays (HSCMA)_ . IEEE, 2014, pp. 107–111. 

- [20] M. Chidambaram, Y. Yang, D. Cer, S. Yuan, Y. Sung, B. Strope, and R. Kurzweil, “Learning cross-lingual sentence representations via a multi-task dual-encoder model,” in _Proceedings of the 4th Workshop on Representation Learning for NLP (RepL4NLP2019)_ . Association for Computational Linguistics, 2019, pp. 250–259. 

- [21] Y. Luo, Z. Chen, and T. Yoshioka, “Dual-path rnn: efficient long sequence modeling for time-domain single-channel speech separation,” in _ICASSP 2020-2020 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2020, pp. 46–50. 

- [22] S. Braun and I. Tashev, “A consolidated view of loss functions for supervised deep learning-based speech enhancement,” in _2021 44th International Conference on Telecommunications and Signal Processing (TSP)_ . IEEE, 2021, pp. 72–76. 

- [23] J. B. Allen and D. A. Berkley, “Image method for efficiently simulating small-room acoustics,” _The Journal of the Acoustical Society of America_ , vol. 65, no. 4, pp. 943–950, 1979. 

- [24] C. K. Reddy, H. Dubey, V. Gopal, R. Cutler, S. Braun, H. Gamper, R. Aichner, and S. Srinivasan, “Icassp 2021 deep noise suppression challenge,” in _ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2021, pp. 6623–6627. 

- [25] K. Dohi, K. Imoto, N. Harada, D. Niizumi, Y. Koizumi, T. Nishida, H. Purohit, T. Endo, M. Yamamoto, and Y. Kawaguchi, “Description and discussion on dcase 2022 challenge task 2: Unsupervised anomalous sound detection for machine condition monitoring applying domain generalization techniques,” _arXiv preprint arXiv:2206.05876_ , 2022. 

- [26] D. P. Kingma and J. Ba, “Adam: A method for stochastic optimization,” in _ICLR 2015_ , 2015. 

- [27] A. W. Rix, J. G. Beerends, M. P. Hollier, and A. P. Hekstra, “Perceptual evaluation of speech quality (pesq)-a new method for speech quality assessment of telephone networks and codecs,” in _2001 IEEE international conference on acoustics, speech, and signal processing. Proceedings (Cat. No. 01CH37221)_ , vol. 2. IEEE, 2001, pp. 749–752. 

- [28] C. H. Taal, R. C. Hendriks, R. Heusdens, and J. Jensen, “A shorttime objective intelligibility measure for time-frequency weighted noisy speech,” in _2010 IEEE international conference on acoustics, speech and signal processing_ . IEEE, 2010, pp. 4214–4217. 

- [29] C. K. Reddy, V. Gopal, and R. Cutler, “Dnsmos: A non-intrusive perceptual objective speech quality metric to evaluate noise suppressors,” in _ICASSP 2021-2021 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2021, pp. 6493–6497. 

- [30] ——, “Dnsmos p. 835: A non-intrusive perceptual objective speech quality metric to evaluate noise suppressors,” in _ICASSP 2022-2022 IEEE International Conference on Acoustics, Speech and Signal Processing (ICASSP)_ . IEEE, 2022, pp. 886–890. 

