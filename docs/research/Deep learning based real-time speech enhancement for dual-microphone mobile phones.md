

<!-- Start of picture text -->
. SERVICES. ‘<br>a 4 % €<br>“Lavage<br><!-- End of picture text -->

Tan et al. 

Page 2 

configuration is a common choice. In a typical dual-microphone setup, a primary microphone is placed on the bottom of a mobile phone and a secondary microphone on the top, as illustrated in Fig. 1. 

In the past decade, a variety of algorithms have been developed for dual-channel speech enhancement. Yousefian et al. [43] developed a Wiener filter that exploits the power level difference (PLD) between the signals received by two microphones. The experimental results show that their approach improves speech quality. Jeub et al. [16] designed a PLDbased noise estimator, which uses the normalized inter-channel PLD as speech presence probability (SPP). The estimated noise spectrum is used to compute a spectral gain, which is subsequently applied to the noisy spectrum to derive the enhanced spectrum. The results show that their approach outperforms the approach in [43], in terms of objective intelligibility. A similar method was proposed in [44], in which the power level ratio of the dual-channel signals is used to calculate a spectral gain. This method produces comparable results to the PLD-based method in [16], while more efficient computationally. More recently, Fu et al. [8] developed a SPP-based noise correlation matrix estimator, where the inter-channel posteriori signal-to-noise ratio difference (PSNRD) is utilized to estimate SPP. The estimated noise correlation matrix is subsequently used to derive a minimum variance distortionless response (MVDR) spatial filter for noise reduction. Their results show that the PSNRD method is more robust than the PLD method in [16] against different sensitivities of two microphones. Other related studies include [22], [19] and [3]. 

Speech enhancement has been recently formulated as supervised learning, inspired by the concept of time-frequency (T-F) masking in computational auditory scene analysis (CASA) [36]. Thanks to the use of deep learning, the performance of supervised speech enhancement has been dramatically improved in the past decade [37]. Compared to the dual-channel setup, speech enhancement for mobile phones needs to consider short speaker-microphone distances and head shadow effects. To our knowledge, the first deep learning based enhancement method for dual-microphone mobile phones was designed by López-Espejo et al. [18], where a deep neural network (DNN) is trained to produce a binary mask from the log-mel features of the noisy array signals. A truncated-Gaussian based imputation algorithm is used to produce the enhanced spectrum from the estimated mask. In a subsequent study [20], they trained a DNN to estimate the noise spectrum from the log-mel features of dual-channel noisy speech. The noise estimate, along with the primary-channel noisy signal, is used to produce the primary-channel enhanced spectrum by a vector Taylor series feature compensation method. The enhanced spectrum is subsequently passed into a speech recognizer for evaluation. Their results show that the DNN-based approach yields significantly higher word accuracy than several conventional approaches. 

Real-time speech enhancement is needed for mobile communication, and it poses several requirements on model design. First, the model should use no or few future time frames. For example, causal DNNs for speech enhancement have been recently developed [23], [31]. Second, the model should not have a high computational cost for the sake of processing latency and power consumption. Third, memory consumption should fit the given capacity of mobile phones. It should be noted that memory consumption has two main aspects, i.e. to 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 3 

store trainable parameters and intermediate results (e.g. the activations from lower DNN layers). 

In a preliminary study [33], we recently proposed a convolutional recurrent network (CRN) for real-time dual-microphone speech enhancement, motivated by an earlier study on CRN [31]. The proposed method produces a phase-sensitive mask (PSM) [6], [39] from magnitude-domain intra- and inter-channel features. The present study extends the CRNbased method to improve its robustness. The present work differs from the preliminary study in the following main aspects. First, we extend the CRN architecture into a denselyconnected CRN (DC-CRN). Specifically, each convolutional or deconvolutional layer is replaced by a densely-connected block. In addition, each skip connection between the encoder and the decoder is replaced by a densely-connected block. Second, we train the DCCRN to learn a mapping from the real and imaginary spectrograms of the dual-channel noisy mixture to those of the primary-channel clean speech signal, inspired by recent advances in complex-domain speech enhancement [42], [7], [32]. Third, we propose a structured pruning technique to compress the DC-CRN, which significantly reduces the model size without significantly affecting the enhancement performance. Fourth, we simulate array signals by spatializing speech and noise signals by covering a reasonable range of source-array distances and including the head shadow effect. Such a data simulation method accounts for various ways of holding a mobile phone, more robust than using close-talk inter-channel relative transfer functions [33]. 

The rest of this paper is organized as follows. In Section II, we formulate dual-channel speech enhancement for mobile phones. In Section III, we describe our proposed approach in detail. Experimental setup is provided in Section IV. In Section V, we present experimental and comparison results. Section VI concludes this paper. 

# **II. Dual-channel Speech Enhancement for Mobile Phone Communication** 

Given a dual-channel signal recorded in a noisy and reverberant environment, the signal model can be formulated as 



where s and nj denote the speech source and the j-th noise source, respectively, and hs and h the room impulse responses (RIRs) corresponding to the speech source and the j-th noise nj source, respectively. Symbol * represents the convolution operation, k the time sample index, and q ∈ {1, 2} the microphone index. In the short-time Fourier transform (STFT) domain, the signal model can be written as 



where S1 ∈ℂ is the STFT of the target speech signal captured by the primary microphone (microphone 1 in this case), c(f) = [1, c(f)]<sup>T</sup> ∈ℂ<sup>2 × 1</sup> is the relative transfer function between the two microphones, and **R** and **N** denote the STFTs of speech reverberation and 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 4 

reverberant noise, respectively. Y1 and Y2 are the STFTs of y<sup>(1)</sup> and y<sup>(2)</sup> , respectively. Symbols m and f index the time frame and the frequency bin, respectively. In this study, we aim to extract the target speech signal captured by the primary microphone, i.e. s1 = ℱ<sup>−1</sup> {S1}, where ℱ<sup>−1</sup> represents the inverse STFT (iSTFT). We focus on noise 

reduction and assume that reverberation energy is relatively weak, which is reasonable with relatively short speaker-phone distances in mobile communication. 

There are broadly two kinds of mobile phone use scenarios: hand-held and hands-free. In a hand-held scenario, the primary microphone is typically close to the talker’s mouth and the secondary microphone close to the ear. In a hands-free scenario, the mobile phone can be placed at some distance, e.g. on a desk in front of the talker. Note that the terms hand-held and hands-free in this paper should not be interpreted literally, but are meant to differentiate the locations of the two microphones relative to the head. 

In the hand-held scenario, the sound level of the speech signal coming from the talker’s mouth is reduced by the head obstruction, prior to reaching the secondary microphone near the ear. This head shadow results in a difference between the received speech levels at the two microphones. An example of the power spectral density (PSD) ratio of the primary channel to the secondary channel is shown in Fig. 2(a), where the dual-channel signals are recorded in a hand-held setup without background noise. It can be observed that the primary signal has a larger PSD than the secondary signal in almost all frequency bands. In the hands-free scenario without the head shadow effect, as illustrated in Fig. 2(c), the speech level at the primary channel is not always higher than that at the secondary channel. In both scenarios, the inter-channel intensity difference (IID) is a useful spatial cue for speech enhancement, corresponding to the magnitude difference between Y1 and Y2 (see Eq. (2)), which is leveraged by most studies for dual-channel speech enhancement. Another useful spatial cue is the inter-channel phase difference (IPD) or inter-channel time difference (ITD), which is highly correlated with the direction of arrival with respect to the dualchannel array. Specifically, the IPD can be calculated as θ y1 – θ y2, where θ y1 and θ y2 are the phases of Y1 and Y2, respectively. Figs. 2(b) and 2(d) show the IPDs, wrapped into [− π , π ], for the corresponding hand-held and hands-free scenarios, respectively. 

Both IID and IPD (or ITD) can be implicitly exploited by learning a multi-channel complex spectral mapping [41], where the IID and the IPD are encoded in the dual-channel complex spectrogram of the noisy mixture. In contrast to conventional beamforming that typically exploits second-order statistics of multiple channels [34], such an approach has the potential to extract all discriminative cues in dual-channel complex-domain inputs through deep learning. In addition, complex spectral mapping simultaneously enhances magnitude and phase responses of target speech [32], which is advantageous over magnitude-domain approaches that ignore phase. 

# **III. Model Description** 

In this section, we first introduce our proposed densely-connected convolutional recurrent network for dual-channel complex spectral mapping, and then elaborate the network configurations for a noncausal enhancement system with a large model size, as well as a 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Page 5 

Tan et al. 

causal and lightweight version for real-time processing. We also propose a structured pruning technique to compress the DC-CRN without significantly sacrificing the enhancement performance. 

## **A. Densely-connected Convolutional Recurrent Network** 

In [32], we have recently developed a gated convolutional recurrent network (GCRN) to perform complex spectral mapping for monaural speech enhancement, which substantially outperforms an earlier convolutional neural network (CNN) that learns complex spectral mapping [7]. The GCRN has an encoder-decoder architecture with skip connections between the encoder and the decoder. A two-layer long short-term memory (LSTM) is inserted between the encoder and decoder to aggregate temporal contexts. The encoder is a stack of gated convolutional layers, and the decoder a stack of gated deconvolutional layers. Such an architecture benefits from both the feature extraction capability of the convolutional autoencoder and the sequential modeling capability of the LSTM, and can effectively capture the local and global spectral structure in a spectrogram. 

This study develops the CRN architecture for dual-channel complex spectral mapping. The diagram of the proposed approach is shown in Fig. 3. The input complex spectrograms are computed by applying STFT to the time-domain waveforms of the dual-channel mixtures. We concatenate the real and imaginary components of the dual-channel spectrograms [42], which amount to a 3-dimensional (3-D) representation with four channels. Subsequently, the 3-D representation is passed into a convolutional encoder, which comprises a stack of five convolutional densely-connected (DC) blocks. The 3-D representation learned by the encoder is reshaped to a sequence of 1-D features, which is then modeled by a recurrent neural network (RNN). We reshape the output of the RNN back to a 3-D representation and subsequently feed it into a decoder, i.e. a stack of five deconvolutional DC blocks. The output of the last block is split into two equal-sized 3-D representations along the channel dimension, one for the real spectrum estimation and the other for the imaginary spectrum estimation. These two 3-D representations are individually reshaped to a sequence of 1-D features, and then passed through a linear projection layer to produce estimates of the real and imaginary components of the clean spectrogram, respectively. We apply the iSTFT to the estimated real and imaginary spectrograms to resynthesize the time-domain waveform of enhanced speech for the primary channel. 

Unlike the skip connections that directly bypass the output of each encoder layer to the corresponding decoder layer in [33] and [32], a convolutional DC block is employed to process the features learned by each DC block in the encoder, prior to concatenating them with the output of the corresponding DC block in the decoder. Such a design is inspired by U-Net++ [47] for image segmentation, which uses DC blocks to bridge the semantic gap between the feature maps of the encoder and the decoder prior to fusion. The introduction of DC block based skip pathways can enrich the feature maps from the encoder, which would help to increase the similarity between the feature maps from the encoder and the decoder and thus improves their fusion. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Page 6 

Tan et al. 

As shown in Fig. 4(a), we propose a dense connectivity pattern in each DC block to improve the information flow between layers, i.e. introducing direct connections from any layer to all subsequent layers. In other words, each layer receives the outputs of all preceding layers: 



where ℋl denotes the mapping function defined by the l-th layer in the DC block, and [·, …,·] the concatenation operation. The output of the l-th layer is represented by **z** l, and **z** 0 is the input to the DC block. By encouraging feature reuse, the dense connections exploit the differences learned by different preceding layers. In this study, we set L to 5. Specifically, each of the first four layers in a DC block consists of a 2-D convolutional layer successively followed by batch normalization [15] and exponential linear activation function [4]. The last layer in the DC block is a gated convolutional or deconvolutional layer as illustrated in Fig. 4(b), which incorporates the gated linear units developed in [5]. Note that “Conv-DC-Block” in Fig. 3 performs gated convolution in the last layer, and “Deconv-DC-Block” gated deconvolution in the last layer. 

It should be noted that using an RNN for sequential modeling is typically more memoryefficient than time-dilated convolutions [30], [24] or temporal attention [17], particularly with strict memory limitation. The use of time-dilated convolutions necessitates storing intermediate activations for many past time steps in the receptive fields of all layers. Similarly, it is necessary to store intermediate activations from many past time steps in order to perform temporal attention. In contrast, an RNN only needs the input at the current time step and the hidden state from the last time step to calculate the output at the current step. Therefore, the RNN would demand far less working memory than a comparably sized DNN based on time-dilated convolutions or temporal attention, even if the RNN may have more trainable parameters than the DNN. 

## **B. Network Configurations** 

**1) Noncausal DC-CRN:** In order to systematically examine the proposed architecture, we first configure the DC-CRN into a noncausal system with a reasonably large model size. In each convolutional or deconvolutional DC block, each of the first four layers has 8 output channels with a kernel size of 1×3 (time×frequency), where a zero-padding of size 1 is applied to each side of the feature maps along the frequency dimension. For the DC blocks in the encoder and the decoder, the last layer in each of them has a kernel size of 1×4, where a stride of 2 and a zero-padding of 1 (for each side) is applied along the frequency dimension. Note that the kernel size is set to 1×4 rather than 1×3 in order to alleviate the checkerboard artifacts [1], which arise when the kernel size of a strided deconvolution is not divisible by the stride. Moreover, the DC blocks in the encoder have 16, 32, 64, 128 and 256 output channels successively, and those in the decoder have 256, 128, 64, 32 and 16 output channels successively. The convolutional DC blocks in the skip pathways have the same hyperparameters as those in the encoder, except that the last layer uses a stride of 1 and a kernel size of 1×3. Similarly, these DC blocks have 16, 32, 64, 128 and 256 output channels successively. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 7 

In this noncausal DC-CRN, the RNN used for sequential modeling is a two-layer bidirectional LSTM (BLSTM), of which each layer contains 640 units in each direction. As in [32], we adopt a grouping strategy [9] to reduce the number of trainable parameters in the BLSTM without significantly affecting the performance. The number of groups is empirically set to 2. 

**2) Causal DC-CRN:** A causal and small DC-CRN can be easily derived by simply changing the network configurations. First, we set the number of output channels of all DC blocks to 16, except that the last DC block in the decoder only has 2 output channels. Second, we use a two-layer unidirectional LSTM for sequential modeling, which has 80 units in each layer. All other settings are the same as in the noncausal DC-CRN. 

## **C. Training Objective** 

Following [41], we train the DC-CRN to perform dual-channel complex spectral mapping with a loss function as follows: 



(r) (i) (r) (i) where S1 , S1 , S1 and S1 represent the real (r) and imaginary (i) components of the enhanced spectrogram S1<sup>and the clean spectrogram S</sup> 1<sup>for the primary channel,</sup> respectively. Here ∥ · ∥ 1 denotes the ℓ 1 norm, and M and F the number of time frames and frequency bins respectively. The estimated spectral magnitude is calculated from the (r) 2 (i) 2 estimated real and imaginary spectra, i.e. ∣S1<sup>(m, f) ∣=</sup> S1 (m, f) + S1 (m, f) . 

The inclusion of the magnitude loss term penalizes the magnitude estimation error accompanied with the phase estimation error, given that the magnitude and the phase are coupled in the real and imaginary components. This penalty is beneficial due to the relative importance of the magnitude over the phase [35]. 

## **D. Iterative Structured Pruning** 

To further reduce the number of trainable parameters, we propose a structured pruning method to compress the causal DC-CRN, without significantly sacrificing the enhancement performance. Structured pruning is a class of coarse-grained parameter pruning techniques, and it leads to more regular sparsity patterns than unstructured pruning. For example, structured pruning can remove an entire column of a weight matrix, unlike unstructured pruning that prunes individual weights. The regularity of sparse structure makes it easier to apply hardware acceleration [21]. 

To prune the DC-CRN, we define the pruning granularity as follow. For each of the convolutional and deconvolutional layers, the weights compose a 4-D tensor of shape C1×C2×K1×K2, where C1 and C2 represent the output and input channel dimensions 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 8 

respectively, and K1 and K2 the shapes of convolution kernels. We treat each kernel (i.e. a K1×K2 matrix) as a weight group for pruning. Moreover, each of the LSTM layers is defined by the following equations: 













where **x** t, **g** t, **c** t and **h** t denote the input, forget, cell and output gates at time step t, respectively. Here **W** ’s and **b** ’s represent weight matrices and bias vectors respectively, and σ and ⊙ the sigmoid nonlinearity and the element-wise multiplication respectively. In the implementation of LSTM, the weight matrices for the four gates are typically concatenated, 

i.e. Wi = [Wii, Wif, Wig, Wio] ∈ℝ<sup>4D1 × D2</sup> and Wℎ = [Wℎi, Wℎf, Wℎg, Wℎo] ∈ℝ<sup>4D1 × D1</sup> , where D1 and D2 are the output and input dimensions of the LSTM layer, respectively. We treat each column of **W** i and **W** h as a weight group for pruning. Similarly, we treat each column of the weight matrix of each linear layer as a weight group for pruning. Since the number of biases is small relative to that of weights, we only prune weights. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 9 

#### **Algorithm 1 Per-tensor sensitivity analysis** 

Input **:** (1) Validation setV; (2) set Gl of all nonzero weight groups in the l‐th weight tensor Wl<sup>,∀l;(3) loss function</sup> ℒRI+Mag(V, Θ), where Θ is the set of all nonzero trainable parameters in the model; (4) predefined tolerance value α . Output **:** Pruning ratioβl for weight tensor Wl<sup>,∀l .</sup> 1:for each tensor Wl<sup>do</sup> 2: for β in {0 % , 5 % , 10 % , …, 90 % , 95 % , 100 % } do 3: Let U ⊆Gl be the set of the β( % ) of nonzero weight groups with the smallestℓ1 norms in tensor Wl<sup>;</sup> 4: CalculateℐU = ℒRI+Mag(V, Θ ∣g = 0, ∀g ∈U) − ℒRI+Mag(V, Θ); 5: if ℐU > α then 6: βl β −5 % ; 7: break 8: end if 9: end for 10: if βl is not assigned any valuethen 11: βl 100 % ; 12: end if 13:end for 14:return βl for weight tensor Wl<sup>, ∀l</sup> 

In order to achieve a high compression rate, we adopt a group sparse regularization technique [27] to impose the group-level sparsity of the weight tensors. Specifically, we introduce the following sparse group lasso (SGL) [28] penalty: 



where W and G denote the set of all weights and that of all weight groups, respectively. The function n(·) calculates the cardinality of a set, and ∥ · ∥ 2 the ℓ 2 norm. The number of weights in each weight group **g** is represented by p **g** . Here λ 1 and λ 2 are predefined weighting factors. Hence, the new loss function can be written as 



The importance of a specific set U of weight groups can be quantified by the error induced by removing (or zeroing out) it. This induced error can be measured as the increase in the loss on a validation set V: 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 10 

ℐU = ℒRI+Mag(V, Θ ∣g = 0, ∀g ∈U) −ℒRI+Mag(V, Θ), 

(13) 

where Θ is the set of all trainable parameters in the model, and U can be any subset of G. To determine the pruning ratio for each weight tensor, we perform a per-tensor sensitivity analysis following Algorithm 1. Subsequently, we perform group-level pruning as per tensor-wise pruning ratios, and then fine-tune the pruned model. We evaluate the fine-tuned model on the validation set by two standard metrics, i.e. short-time objective intelligibility (STOI) [29] and perceptual evaluation of speech quality (PESQ) [26]. This procedure is repeated until the number of pruned weights becomes trivial in an iteration or a significant degradation of STOI or PESQ is observed on the validation set. Note that the parameter set Θ becomes smaller after each iteration. 

# **IV. Experimental Setup** 

## **A. Data Preparation** 

In our experiments, we use the training set of the WSJ0 corpus [10] for evaluation, which includes 12776 utterances from 101 speakers. These speakers are split into three groups for training, cross validation and testing, which contain 89, 6 (3 males and 3 females) and 6 (3 males and 3 females), respectively. Specifically, these groups include 11084, 846 and 846 clean utterances for creating the training, validation and test sets, respectively. We simulate a rectangular room with a size of 10×7×3 m<sup>3</sup> using the image method [2]. The target speech source (mouth) is located at the center of the room, while the primary microphone is placed on a sphere centered at the target speech source with a radius randomly sampled between 0.01 m and 0.15 m. Such a distance range covers both hand-held and hands-free scenarios. We fix the geometry of the dual-channel microphone array, where the distance between microphones is 0.1 m. Thus the location of the secondary microphone is randomly chosen on a sphere with a radius of 0.1 m, which is centered at the primary microphone. The reverberation time (T60) is randomly sampled between 0.2 s and 0.5 s. Following this procedure, we simulate a set of 5000 dual-channel RIRs for training and cross validation, and another set of 846 dual-channel RIRs for testing. 

As illustrated in Fig. 5, we simulate a diffuse babble noise in the following way. We first concatenate the utterances spoken by each of the 630 speakers in the TIMIT corpus [11], and then split them into 480 and 150 speakers for training and testing. Following [45], we randomly select 72 speech clips from 72 randomly chosen speakers, and place them on a horizontal circle centered at and with the same height as the primary microphone, where the azimuths range from 0° to 355° with 5° steps. The distance between the primary microphone and each of the interfering sources is 2 m. 

We create a training set including 40000 mixtures, each of which is simulated by mixing a diffuse babble noise and a randomly sampled WSJ0 utterance convolved with a randomly selected RIR. To create the validation set, we convolve each of the 846 validation utterances with a randomly selected RIR, and then mix the reverberant speech signal with a random cut of diffuse babble noise at each channel. In order to mimic the head shadow effect, we downscale the amplitude of the speech signal at the secondary channel prior to mixing, 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 11 

where the downscaling ratio is randomly sampled between −10 and 0 dB. For both training and validation data, the SNR is randomly sampled between −5 and 0 dB, where the SNR is with respect to the reverberant speech signal and the reverberant noise signal at the primary channel. Similarly, we create a test set consisting of 846 mixtures for each of four SNRs, i.e. −5, 0, 5 and 10 dB. 

In our experiments, all signals are sampled at 16 kHz. We rescale each noisy mixture by a factor, such that the root mean square of the mixture waveform is 1. The same factor is used to rescale the corresponding target speech waveform. Such noncausal signal level normalization is applied because we focus on speech enhancement and assume that the root mean square power of all input signals is the same. Thus the causal models can benefit from this noncausal normalization in our experiments. Real applications may need a causal automatic gain control for signal level normalization. Moreover, we use a 20-ms Hamming window to segment time-domain signals into a set of frames, with a 50% overlap between adjacent frames. A 320-point (16 kHz × 20 ms) discrete Fourier transform is applied to each frame, yielding 161-D one-sided spectra. 

## **B. Baselines** 

In our preliminary study [33], the PSM is used as the training target, which is originally defined for the primary channel as follows: 



where ∣ S1(m, f) ∣ and ∣ Y1(m, f) ∣ denote the spectral magnitudes of clean speech and noisy speech within the T-F unit at frame m and frequency f respectively, and θ s1 and θ y1 the phases of clean speech and noisy speech within the unit respectively. Re{·} computes the real component. In [33], however, a modified version is used: 



where θ y1–y2 represents the phase of the noisy signal difference between channels, i.e. y1 – y2. For PSM2, θ y1–y2 is used to resynthesize waveforms, which was shown to improve both STOI and PESQ over using PSM1 and θ y1. An interpretation is that the inter-channel PLD of speech signals is typically larger than that of noise signals due to the head shadow in handheld scenarios. With a possible signal cancellation effect due to the subtraction, y1 – y2 may have a higher SNR and thus cleaner phase than y1. 

In [33], a CRN is employed to estimate PSM2 from both intra-channel features (i.e. ∣ Y1 ∣ and ∣ Y2 ∣ ) and inter-channel features (i.e. ∣ Y1−Y2 ∣ and ∣ Y1+Y2 ∣ ). We refer to the approach in [33] 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 12 

as “C-CRN-PSM2” (“C-CRN” indicates causal CRN), and another version that estimates PSM1 as “C-CRN-PSM1”. In addition, we train a noncausal version of each of these two baselines, where the configuration of the CRN is changed as follows. The numbers of output channels for the layers in the encoder are changed to 16, 32, 64, 128 and 256 successively, and those for each layer in the decoder to 128, 64, 32, 16 and 1 successively. The two-layer LSTM is replaced by a two-layer BLSTM, of which each layer contains 512 units in each direction. These noncausal baselines are denoted as “NC-CRN-PSM1” and “NC-CRNPSM2”. 

## **C. Training Methodology** 

The models are trained on 4-second segments using the AMSGrad optimizer [25] with a minibatch size of 16. The learning rate is initialized to 0.001, which decays by 0.98 every two epochs. We apply gradient clipping with a maximum ℓ 2 norm of 5 during training. The validation set is used for both selecting the best model among different epochs and performing the sensitivity analysis prior to pruning. 

For structured pruning, the initial values of λ 2 and λ 2 (see Eq. (11)) are empirically set to 1 and 0.1, both of which decay by 10% every pruning iteration. We alternately prune and finetune the causal DC-CRN for 6 iterations. The tolerance value α for sensitivity analysis (see Algorithm 1) is set to 0.02. 

# **V. Experimental Results and Comparisons** 

## **A. Model Comparison** 

Comprehensive comparisons among alternative models are shown in Table I, in terms of STOI, PESQ and SNR, where the numbers represent the averages over the test set in each condition. The proposed models with noncausal and causal DC-CRNs are denoted as “NCDC-CRN-RI” and “C-DC-CRN-RI”, respectively. The pruned DC-CRN model for the k-th iteration is represented by “C-DC-CRN-RI-Pk”. 

We can observe that using PSM1 yields similar results to using PSM2, unlike the finding that PSM2 produces significantly better results than PSM1 in [33]. This is likely because θ y1–y2 is not always cleaner than θ y1 due to the variety of inter-channel decay ratios and no head shadow in hands-free scenarios. Moreover, our proposed approach substantially outperforms the approach in [33] in all the metrics. At - 5 dB SNR, for example, “NC-DC-CRN-RI” improves STOI by 7.6%, PESQ by 0.89 and SNR by 4.77 dB, over “NC-CRN-PSM2”. Similar improvements are observed for “C-DC-CRN-RI” over “C-CRN-PSM2”. We additionally compare our approach with two ideal masks, i.e. the PSM (PSM1) and the ideal ratio mask (IRM) [38], defined as 



where H1 and N1 are the STFTs of reverberation and reverberant noise at the primary channel, respectively. As shown in Table I, our noncausal enhancement system (“NC-DC- 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 13 

CRN-RI”) produces better results than the IRM in terms of all the three metrics. In addition, our system yields slightly lower STOI and PESQ but higher SNR than the PSM. 

To demonstrate the generalization capability of the trained models, we create an additional test set by mixing real-recorded speech signals and simulated diffuse noise signals at −5, 0, 5 and 10 dB SNRs. Specifically, the diffuse noise is simulated using the same recipe as described in Section IV-A, where the noise source signals are recorded in eight different environments. The speech signals are recorded by a dual-microphone mobile phone (Meizu 15) that is mounted on a dummy head. The source signals<sup>1</sup> contain 20 utterances from four speakers (two males and two females), where each speaker reads five IEEE sentences [14]. The total duration of these utterances is roughly 80 seconds. They are mixed with the eight types of noises at the four SNRs, which amount to a set of noisy speech signals with a total duration of roughly 43 minutes ( ≈ 80×8×4 s). As shown in Table II, “C-DC-CRN-RI” and “C-DC-CRN-RI-P6” produce significantly higher STOI and PESQ than “C-CRN-PSM1”. Moreover, “C-DC-CRN-RI-P6” produces substantial improvements in STOI and PESQ over unprocessed mixtures, consistent with our finding from Table I. This suggests the robustness of our training data simulation method described in Section IV-A. 

Furthermore, we compare the pruned DC-CRN models of different pruning iterations. As presented in Table I, the causal DC-CRN originally has 290.44 K trainable parameters. After 6 iterations of pruning, the number of trainable parameters in the DC-CRN becomes 103.07 K, which is comparable to that of the CRN in [33], i.e. 73.15 K. The model size reduction over pruning iterations is shown in Fig. 6(a). Compared with the original model, the performance of the pruned model after 6 iterations degrades only slightly. Take, for example, the 0 dB SNR case. Iterative pruning decreases STOI by 0.72%, PESQ by 0.05 and SNR by 0.53 dB. Fig. 6(b) shows the STOI and PESQ scores on the validation set over pruning iterations. 

Moreover, we calculate the number of multiply-accumulate (MAC) operations on a 4-second noisy mixture, which is another common metric for evaluating model complexity. The number of MAC operations decreases from 1.97 G for “C-DC-CRN-RI” to 502.40 M for “C-DC-CRN-RI-P6”. Thus the average number of MAC operations for processing a 1- second input signal is 125.60 M, which is amenable to mobile phones on the market. We additionally measure the computation time for “C-DC-CRN-RI-P6” on a Lenovo ThinkPad X1 laptop with Intel Core i7-10510U@1.80GHz processors, and the average time of processing a 20-ms time frame is 2.78 ms, demonstrating real-time feasibility. 

## **B. Ablation Study of Dense Connectivity** 

To investigate the contribution of dense connectivity in the DC-CRN, we conduct an ablation study at −5 dB SNR, as shown in Table III. Several variants of the causal DC-CRN are compared: (i) replacing the DC block based skip pathways by skip connections as in [33]; (ii) replacing each DC block in the encoder and the decoder by a corresponding gated convolutional or deconvolutional layer, as in [32]; (iii) doing both (i) and (ii). We can see that all these variants underperform the proposed causal DC-CRN, which suggests the 

> 1[Online] Available: https://docbox.etsi.org/stq/Open/TS%20103%20106%20Wave%20files/Annex_C_Dynastat%20Speech%20Data/ 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 14 

effectiveness of dense connectivity. Without dense connectivity in the encoder and the decoder, for example, STOI decreases by 1.31% and PESQ by 0.14. Only removing the dense connectivity in the skip pathways does not significantly degrade the enhancement performance, if the DC blocks in the encoder and the decoder are preserved. However, going from (ii) to (iii) results in a significant performance loss. This is likely because the dense connectivity in the skip pathways compensates for the reduced representation power without DC blocks in the encoder and the decoder. 

## **C. Inter-channel Features** 

The approach in [33] exploits both intra- and inter-channel features in the magnitude domain, while our proposed approach performs dual-channel complex spectral mapping without explicitly using any inter-channel features. We now investigate the inclusion of inter-channel features for both these approaches. As shown in Table IV, the inclusion of inter-channel features significantly improves STOI, PESQ and SNR for the magnitudedomain approaches. For our approach based on complex spectral mapping, we use the real and imaginary components of Y1 − Y2 and Y1 + Y2 as the inter-channel features. With multi-channel complex spectral mapping, the explicit use of these inter-channel features does not produce performance gain, as shown in Table IV. Unlike the magnitude spectrograms, the complex spectrograms encode both magnitude and phase information. Hence inter-channel features can be captured implicitly through DNN training that learns multi-channel complex spectral mapping, consistent with [41] which demonstrates the effectiveness of multi-channel to singlechannel complex spectral mapping for speech dereverberation. 

## **D. Comparison with Beamforming** 

We now compare the proposed approach with DNN-based beamforming (BF) [12], [13], [46]. Following [40], we formulate an MVDR beamformer, where the speech and noise covariance matrices are estimated as 



where (·)<sup>H</sup> denotes the conjugate transpose, and η (m, f) and ξ (m, f) the weighting factors representing the importance of each T-F unit for the covariance matrix computation. These weighting factors are calculated as the product of estimated T-F masks for different channels: 



IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Page 15 

Tan et al. 



where D=2 is the number of channels, and Mi<sup>(m, f) the ratio mask for the i-th microphone.</sup> These ratio masks are individually estimated by a noncausal DC-CRN that is monaurally trained to estimate the IRM for each channel. We treat the primary channel as the reference channel, and estimate the inter-channel relative transfer function (i.e. steering vector) as 





where P{ ⋅} computes the principal eigenvector. The MVDR filter is then calculated as 



and the enhanced spectrogram is obtained by S(m, f) = w(f)<sup>H</sup> Y(m, f). To improve the enhancement performance, the monaural DC-CRN trained for IRM estimation is used as a post-filter (PF). As shown in Table V, this masking-based beamforming algorithm outperforms a noncausal DC-CRN that estimates the IRM from the magnitude spectrograms of the two channels, in terms of both STOI and PESQ. 

In addition, we formulate a variant of the aforementioned MVDR beamformer following [41], where the speech and noise covariance matrices are estimated as 





where M is the number of time frames. The complex spectrogram S is estimated by performing a monaural complex spectral mapping using a noncausal DC-CRN. Then the estimated noise spectrogram is calculated as V = Y −S. Akin to masking-based beamforming, we obtain the spatial filter using Eqs. (21)-(23). The DC-CRN for monaural complex spectral mapping is used as a post-filter. As shown in Table V, our proposed approach outperforms the beamformer in terms of both STOI and PESQ, which further suggests that dual-channel complex spectral mapping can effectively exploit spatial cues encoded in the dual-channel complex spectrogram. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Page 16 

Tan et al. 

# **VI. Conclusion** 

In this study, we have proposed a novel framework for dual-channel speech enhancement on mobile phones, which employs a new causal DC-CRN to perform dual-channel complex spectral mapping. By applying an iterative structured pruning technique, we derive a lowlatency and memory-efficient enhancement system that is amenable to real-time processing on mobile phones. Evaluation results demonstrate that the proposed approach significantly outperforms an earlier method for speech enhancement for dual-microphone mobile phones. Moreover, our approach consistently outperforms a DNN-based beamformer, which suggests that multi-channel complex spectral mapping can effectively extract and utilize spatial cues encoded in the multi-channel complex spectrogram. 

# **Acknowledgment** 

This research described here was supported in part by an NIDCD grant (R01 DC012048), and the Ohio Supercomputer Center. It started when the first author was interning with Elevoc Technology. 

# **References** 

- [1]. Aitken A, Ledig C, Theis L, Caballero J, Wang Z, and Shi W. Checkerboard artifact free sub-pixel convolution: A note on sub-pixel convolution, resize convolution and convolution resize. arXiv preprint arXiv:1707.02937, 2017. 

- [2]. Allen JB and Berkley DA. Image method for efficiently simulating small-room acoustics. The Journal of the Acoustical Society of America, 65(4):943–950, 1979. 

- [3]. Chen Y-Y. Speech enhancement of mobile devices based on the integration of a dual microphone array and a background noise elimination algorithm. Sensors, 18(5):1467, 2018. 

- [4]. Clevert D-A, Unterthiner T, and Hochreiter S. Fast and accurate deep network learning by exponential linear units (ELUs). International Conference on Learning Representations, 2016. 

- [5]. Dauphin YN, Fan A, Auli M, and Grangier D. Language modeling with gated convolutional networks. In Proceedings of the 34th International Conference on Machine Learning, volume 70, pages 933–941, 2017. 

- [6]. Erdogan H, Hershey JR, Watanabe S, and Le Roux J. Phase-sensitive and recognition-boosted speech separation using deep recurrent neural networks. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 708–712. IEEE, 2015. 

- [7]. Fu S-W, Hu T.-y., Tsao Y, and Lu X. Complex spectrogram enhancement by convolutional neural network with multi-metrics learning. In IEEE 27th International Workshop on Machine Learning for Signal Processing, pages 1–6. IEEE, 2017. 

- [8]. Fu Z-H, Fan F, and Huang J-D. Dual-microphone noise reduction for mobile phone application. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 7239–7243. IEEE, 2013. 

- [9]. Gao F, Wu L, Zhao L, Qin T, Cheng X, and Liu T-Y. Efficient sequence learning with group recurrent networks. In Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers), pages 799–808, 2018. 

- [10]. Garofolo J, Graff D, Paul D, and Pallett D. CSR-I (WSJ0) complete LDC93S6A. Web Download. Philadelphia: Linguistic Data Consortium, 83, 1993. 

- [11]. Garofolo JS, Lamel LF, Fisher WM, Fiscus JG, and Pallett DS. DARPA TIMIT acoustic-phonetic continous speech corpus CD-ROM. NIST speech disc 1-1.1. STIN, 93:27403, 1993. 

- [12]. Heymann J, Drude L, and Haeb-Umbach R. Neural network based spectral mask estimation for acoustic beamforming. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 196–200. IEEE, 2016. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 17 

- [13]. Higuchi T, Ito N, Yoshioka T, and Nakatani T. Robust MVDR beamforming using time-frequency masks for online/offline ASR in noise. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 5210–5214. IEEE, 2016. 

- [14]. IEEE. IEEE recommended practice for speech quality measurements. IEEE Transactions on Audio and Electroacoustics, 17(3):225–246, 1969. 

- [15]. Ioffe S and Szegedy C. Batch normalization: Accelerating deep network training by reducing internal covariate shift. In International Conference on Machine Learning, pages 448–456, 2015. 

- [16]. Jeub M, Herglotz C, Nelke C, Beaugeant C, and Vary P. Noise reduction for dual-microphone mobile phones exploiting power level differences. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 1693–1696. IEEE, 2012. 

- [17]. Koizumi Y, Yaiabe K, Delcroix M, Maxuxama Y, and Takeuchi D. Speech enhancement using self-adaptation and multi-head self-attention. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 181–185. IEEE, 2020. 

- [18]. López-Espejo I, González JÁ, Gómez AM, and Peinado AM. A deep neural network approach for missing-data mask estimation on dual-microphone smartphones: application to noise-robust speech recognition. In Advances in Speech and Language Technologies for Iberian Languages, pages 119–128. Springer, 2014. 

- [19]. López-Espejo I, Martín-Doñas JM, Gomez AM, and Peinado AM. Unscented transform-based dual-channel noise estimation: Application to speech enhancement on smartphones. In 41st International Conference on Telecommunications and Signal Processing, pages 1–5. IEEE, 2018. 

- [20]. López-Espejo I, Peinado AM, Gomez AM, and Martín-Doñas JM. Deep neural network-based noise estimation for robust ASR in dual-microphone smartphones. In International Conference on Advances in Speech and Language Technologies for Iberian Languages, pages 117–127. Springer, 2016. 

- [21]. Mao H, Han S, Pool J, Li W, Liu X, Wang Y, and Dally WJ. Exploring the granularity of sparsity in convolutional neural networks. In Proceedings of the IEEE Conference on Computer Vision and Pattern Recognition Workshops, pages 13–20, 2017. 

- [22]. Nabi W, Aloui N, and Cherif A. Speech enhancement in dual-microphone mobile phones using Kalman filter. Applied Acoustics, 109:1–4, 2016. 

- [23]. Naithani G, Barker T, Parascandolo G, Bramsl L, Pontoppidan NH, and Virtanen T. Low latency sound source separation using convolutional recurrent neural networks. In IEEE Workshop on Applications of Signal Processing to Audio and Acoustics, pages 71–75. IEEE, 2017. 

- [24]. Pandey A and Wang DL. Densely connected neural network with dilated convolutions for realtime speech enhancement in the time domain. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 6629–6633. IEEE, 2020. 

- [25]. Reddi SJ, Kale S, and Kumar S. On the convergence of Adam and beyond. In International Conference on Learning Representations, 2018. 

- [26]. Rix AW, Beerends JG, Hollier MP, and Hekstra AP. Perceptual evaluation of speech quality (PESQ)-a new method for speech quality assessment of telephone networks and codecs. In IEEE International Conference on Acoustics, Speech, and Signal Processing. Proceedings (Cat. No. 01CH37221), volume 2, pages 749–752. IEEE, 2001. 

- [27]. Scardapane S, Comminiello D, Hussain A, and Uncini A. Group sparse regularization for deep neural networks. Neurocomputing, 241:81–89, 2017. 

- [28]. Simon N, Friedman J, Hastie T, and Tibshirani R. A sparse-group lasso. Journal of Computational and Graphical Statistics, 22(2):231–245, 2013. 

- [29]. Taal CH, Hendriks RC, Heusdens R, and Jensen J. An algorithm for intelligibility prediction of time–frequency weighted noisy speech. IEEE Transactions on Audio, Speech, and Language Processing, 19(7):2125–2136, 2011. 

- [30]. Tan K, Chen J, and Wang DL. Gated residual networks with dilated convolutions for monaural speech enhancement. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 27(1):189–198, 2019. 

- [31]. Tan K and Wang DL. A convolutional recurrent neural network for real-time speech enhancement. In Interspeech, pages 3229–3233, 2018. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 18 

- [32]. Tan K and Wang DL. Learning complex spectral mapping with gated convolutional recurrent networks for monaural speech enhancement. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 28:380–390, 2020. 

- [33]. Tan K, Zhang X, and Wang DL. Real-time speech enhancement using an efficient convolutional recurrent network for dual-microphone mobile phones in close-talk scenarios. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 5751–5755. IEEE, 2019. 

- [34]. Van Veen BD and Buckley KM. Beamforming: A versatile approach to spatial filtering. IEEE ASSP Magazine, 5(2):4–24, 1988. 

- [35]. Wang D and Lim J. The unimportance of phase in speech enhancement. IEEE Transactions on Acoustics, Speech, and Signal Processing, 30(4):679–681, 1982. 

- [36]. Wang DL and Brown GJ, editors. Computational auditory scene analysis: Principles, algorithms, and applications. Wiley-IEEE press, 2006. 

- [37]. Wang DL and Chen J. Supervised speech separation based on deep learning: An overview. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 26(10):1702–1726, 2018. 

- [38]. Wang Y, Narayanan A, and Wang DL. On training targets for supervised speech separation. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 22(12):1849–1858, 2014. 

- [39]. Wang Y and Wang DL. A deep neural network for time-domain signal reconstruction. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 4390–4394. IEEE, 2015. 

- [40]. Wang Z-Q and Wang DL. All-neural multi-channel speech enhancement. In Interspeech, pages 3234–3238, 2018. 

- [41]. Wang Z-Q and Wang DL. Multi-microphone complex spectral mapping for speech dereverberation. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 486–490. IEEE, 2020. 

- [42]. Williamson DS, Wang Y, and Wang DL. Complex ratio masking for monaural speech separation. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 24(3):483–492, 2016. 

- [43]. Yousefian N, Akbari A, and Rahmani M. Using power level difference for near field dualmicrophone speech enhancement. Applied Acoustics, 70(11-12):1412–1421, 2009. 

- [44]. Zhang J, Xia R, Fu Z, Li J, and Yan Y. A fast two-microphone noise reduction algorithm based on power level ratio for mobile phone. In 8th International Symposium on Chinese Spoken Language Processing, pages 206–209. IEEE, 2012. 

- [45]. Zhang X and Wang DL. Deep learning based binaural speech separation in reverberant environments. IEEE/ACM Transactions on Audio, Speech, and Language Processing, 25(5):1075–1084, 2017. 

- [46]. Zhang X, Wang Z-Q, and Wang DL. A speech enhancement algorithm by iterating single-and multi-microphone processing and its application to robust ASR. In IEEE International Conference on Acoustics, Speech and Signal Processing, pages 276–280. IEEE, 2017. 

- [47]. Zhou Z, Siddiquee MMR, Tajbakhsh N, and Liang J. UNet++: A nested U-Net architecture for medical image segmentation. In Deep Learning in Medical Image Analysis and Multimodal Learning for Clinical Decision Support, pages 3–11. Springer, 2018. 

IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

@ )Secondary  be **Microphone** 



<!-- Start of picture text -->
— 20<br>a<br>ao)<br>Sacet<br>J<br>©<br>[a<br>-20 . ; ;<br>(0) 2 4 6 8<br>Frequency (kHz)<br>(a) Inter-channel PSD Ratio<br>B85 aa<br>7 : oy 5 2<br>2 4 5 es 0<br>3, :<br>52 mast : ose 2<br>Time (s)<br>(b) Inter-channel Phase Difference<br>— 20<br>a<br>no)<br>—<br>:<br>[=<br>Po) 6  a aeeertens-20  i<br>(0) 2 4 6 8<br>Frequency (kHz)<br>(c) Inter-channel PSD Ratio<br>37 hee TS -2<br>i 1 2 3<br>Time (s)<br>(d) Inter-channel Phase Difference<br><!-- End of picture text -->



<!-- Start of picture text -->
Reshape —————— RNN —_____» Reshape<br>if<br>Conv-DC-Block ne Concat<br>Conv-DC-Block pe<br>- Conv-DC-Block oe Concat<br>_ Conv-DC-Block a<br>| Conv-DC-Block oe Concat<br>|<br>Conv-DC-Block ee<br>~_ Conv-DC-Block oe Concat<br>Conv-DC-Block Scam BIG<br>~ Conv-DC-Block —+ Concat<br>Conv-DC-Block Seam SE BIG<br>Split& Reshape |<br>i Concat - Lin ar e e ClLinear<br>STFT STFT iSTFT<br>ft t ‘<br>‘Waratah yagi AAA edna<br><!-- End of picture text -->



<!-- Start of picture text -->
| Conv, BN, ELU<br>| Conv, BN, ELU<br><!-- End of picture text -->



<!-- Start of picture text -->
-<br>Conv,BN,ELU<br>-<br>Conv,BN,ELU<br><!-- End of picture text -->



<!-- Start of picture text -->
|<br>Conv/Deconv<br>Conv/Deconv |<br>|<br>Sigmoid<br><!-- End of picture text -->



<!-- Start of picture text -->
|<br><!-- End of picture text -->

Gated Conv/Deconv 

(a) Densely-connected Block 

(b) Gated Convolution/Deconvolution 



<!-- Start of picture text -->
."oe fe, *<br>) 5° e<br>fo) e i<br>@ ; Interfering<br>Primary + © ® Sources<br>@ Microphone pouth @<br>° a)<br>.. Pi<br>° ° ° Q<br>eee Reverberant Room<br><!-- End of picture text -->



<!-- Start of picture text -->
100% 100.00%<br>90%<br>80%<br>= 70%<br>“<br>E 60%<br>©<br>& 50%<br>40% 43.02% , 17,<br>30% 39.14% 37.45% 36.57% 36.07% 35.49%<br>20%<br>0 1 2 3 4 5 6<br>Iteration<br>(a)<br>man STO] ——PESQ<br>93.0 3.00<br>92.0 2.90<br>= 91.0 ee eee a 4<br>fe) AU<br>f; 20.0 2.60 ~<br>89.0 2.50<br>88.0 2.40<br>0 1 2 3 4 5 6<br>Iteration<br>(b)<br><!-- End of picture text -->

Page 25 

Tan et al. 

|**Causal**|-|✗|✗|✗|-|-|✓|✓|✓|✓|✓|✓|✓|✓|✓|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|**# Param.**|-|12.99 M|12.99 M|8.36 M|-|-|73.15 K|73.15 K|290.44 K|124.96 K|113.68 K|108.77 K|106.21 K|104.76 K|103.07 K|
|**SNR (dB)**|9.76|15.49|11.07|**18.49**|14.95|18.43|14.63|10.60|**17.53**|17.15|17.11|17.18|17.11|16.97|16.60|
|**10 dB**<br>**PESQ**|2.38|3.16|3.17|**3.78**|3.68|3.88|2.99|2.88|**3.53**|3.46|3.47|3.47|3.44|3.43|3.51|
|**STOI (%)**|91.41|96.96|95.47|**98.45**|97.74|98.87|95.76|94.05|**97.74**|97.63|97.62|97.61|97.59|97.65|97.47|
|**SNR (dB)**|4.91|12.40|9.78|**16.38**|11.95|15.03|11.53|9.18|**15.01**|14.76|14.72|14.75|14.66|14.54|14.29|
|**5 dB**<br>**PESQ**|2.04|2.89|2.93|**3.63**|3.39|3.66|2.59|2.56|**3.30**|3.26|3.27|3.26|3.22|3.20|3.27|
|**STOI (%)**|83.53|94.87|93.82|**97.66**|96.24|97.87|92.76|91.53|**96.35**|96.16|96.14|96.07|96.03|96.07|95.88|
|**SNR (dB)**|−0.05|9.31|8.11|**13.82**|9.07|11.81|8.29|7.29|**11.95**|11.82|11.75|11.77|11.70|11.62|11.42|
|**0 dB**<br>**PESQ**|1.73|2.53|2.60|**3.41**|3.10|3.40|2.17|2.18|**2.99**|2.97|2.98|2.95|2.91|2.90|2.94|
|**STOI (%)**|72.08|91.13|90.79|**96.09**|94.21|96.26|87.30|86.80|**93.36**|93.08|93.10|92.89|92.85|92.86|92.64|
|**SNR (dB)**|−5.03|6.43|6.21|**10.90**|6.47|9.02|5.25|5.13|**8.61**|8.55|8.46|8.50|8.43|8.36|8.21|
|**−5 dB**<br>**PESQ**|1.49|2.11|2.20|**3.07**|2.83|3.16|1.72|1.76|**2.56**|2.54|2.56|2.52|2.49|2.48|2.51|
|**STOI (%)**|58.71|84.65|85.48|**92.77**|92.02|94.08|78.20|78.77|**87.57**|86.88|87.13|86.64|86.63|86.63|86.45|
|**Test SNR**<br>**Metric**|Unprocessed|NC-CRN-PSM1|NC-CRN-PSM2|NC-DC-CRN-RI|IRM|PSM|C-CRN-PSM1|C-CRN-PSM2|C-DC-CRN-RI|C-DC-CRN-RI-P1|C-DC-CRN-RI-P2|C-DC-CRN-RI-P3|C-DC-CRN-RI-P4|C-DC-CRN-RI-P5|C-DC-CRN-RI-P6|



IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Page 26 

Tan et al. 

##### 

##### 

|**B**<br>**PESQ**|2.62|2.94|3.06|2.97|
|---|---|---|---|---|
|**10 d**<br>**STOI (%)**|93.99|95.41|97.71|97.23|
|<br>**PESQ**|2.28|2.74|2.97|2.87|
|**5 dB**<br>**STOI (%)**|88.27|93.14|96.51|95.80|
|<br>**PESQ**|1.91|2.49|2.83|2.76|
|**0 dB**<br>**STOI (%)**|78.96|88.44|94.21|92.99|
|<br>**PESQ**|1.66|2.13|2.57|2.58|
|**−5 dB**<br>**STOI (%)**|66.78|79.82|89.44|87.51|
|**t SNR**<br>**tric**|rocessed|RN-PSM**1**|C-CRN-RI|C-CRN-RI-P6|
|**Tes**<br>**Me**|Unp|C-C|C-D|C-D|



IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 27 

### **TABLE III** 

Effects of Dense Connectivity at −5 dB SNR. 

|**Test SNR**||**−5 dB**||**# Param**|
|---|---|---|---|---|
|**Metric**|**STOI (%)**|**PESQ**|**SNR (dB)**|**.**|
|Unprocessed|58.71|1.49|−5.03|−|
|C-DC-CRN-RI|**87.57**|**2.56**|**8.61**|290.44 K|
|– DCSkip(i)|87.23|2.53|8.49|253.32 K|
|– DCED(ii)|86.26|2.42|8.02|218.69 K|
|– DCSkip– DCED(iii)|82.77|2.10|6.37|181.57 K|



IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 28 

### **TABLE IV** 

INVESTIGATION OF INTER-CHANNEL FEATURES FOR MAGNITUDE- AND COMPLEX-DOMAIN APPROACHES. “ICFs” REPRESENT THE INTER-CHANNEL FEATURES. 

|**Test SNR**||**−5 dB**||**Domain**|
|---|---|---|---|---|
|**Metric**|**STOI (%)**|**PESQ**|**SNR (dB)**||
|Unprocessed|58.71|1.49|−5.03|-|
|C-CRN-PSM**1**w/ ICFs|78.20|1.72|5.25|Magnitude|
|C-CRN-PSM**1**w/o ICFs|76.41|1.63|4.96|Magnitude|
|C-CRN-PSM**2**w/ ICFs|78.77|1.76|5.13|Magnitude|
|C-CRN-PSM**2**w/o ICFs|76.14|1.67|4.56|Magnitude|
|C-DC-CRN-RI w/ ICFs|87.64|2.56|8.44|Complex|
|C-DC-CRN-RI w/o ICFs|87.44|2.56|8.61|Complex|



IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

Tan et al. 

Page 29 

### **TABLE V** 

Comparisons with Beamforming in Magnitude and Complex Domains at −5 and 0 dB SNRs. 

|**Test SNR**|**−5 d**|**B**|**0 dB**||**Domain**|
|---|---|---|---|---|---|
|**Metric**|**STOI (%)**|**PESQ**|**STOI (%)**|**PESQ**||
|Unprocessed|58.71|1.49|72.08|1.73|−|
|Mask-BF|68.85|1.64|81.37|1.92|Magnitude|
|Mask-BF-PF|**86.32**|**2.49**|**92.60**|**2.91**|Magnitude|
|NC-DC-CRN-IRM|85.21|2.42|90.95|2.79|Magnitude|
|RI-BF|71.93|1.65|82.51|1.93|Complex|
|RI-BF-PF|91.03|2.94|95.03|3.31|Complex|
|NC-DC-CRN-RI|**92.77**|**3.07**|**96.09**|**3.41**|Complex|



IEEE/ACM Trans Audio Speech Lang Process. Author manuscript; available in PMC 2022 January 01. 

