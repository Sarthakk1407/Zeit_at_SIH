# ROBUSTNESS ENHANCEMENT IN NEURAL NETWORKS WITH ALPHA-STABLE TRAINING NOISE 

**Xueqiong Yuan**<sup>_∗_</sup> **, Jipeng Li**<sup>_∗_</sup> **, Ercan Engin Kuruo˘glu**<sup>_†_</sup> Tsinghua-Berkeley Shenzhen Institute Tsinghua University 

_{_ `xq-yuan22, lijipeng22` _}_ `@mails.tsinghua.edu.cn, kuruoglu@sz.tsinghua.edu.cn` 

## **ABSTRACT** 

With the increasing use of deep learning on data collected by non-perfect sensors and in non-perfect environments, the robustness of deep learning systems has become an important issue. A common approach for obtaining robustness to noise has been to train deep learning systems with data augmented with Gaussian noise. In this work, we challenge the common choice of Gaussian noise and explore the possibility of stronger robustness for non-Gaussian impulsive noise, specifically _α_ -stable noise. Justified by the Generalized Central Limit Theorem and evidenced by observations in various application areas, _α_ -stable noise is widely present in nature. By comparing the testing accuracy of models trained with Gaussian noise and _α_ -stable noise on data corrupted by different noise, we find that training with _α_ -stable noise is more effective than Gaussian noise, especially when the dataset is corrupted by impulsive noise, thus improving the robustness of the model. The generality of this conclusion is validated through experiments conducted on various deep learning models with image and time series datasets, and other benchmark corrupted datasets. Consequently, we propose a novel data augmentation method that replaces Gaussian noise, which is typically added to the training data, with _α_ -stable noise. 

## **1 INTRODUCTION** 

Deep learning models have become an effective tool for solving various tasks, including pattern recognition, semantic segmentation, natural language processing, etc. The performance of deep learning models is related to the quality of the input data. It is common for real-life data to be corrupted, both naturally (e.g., noise) and maliciously (e.g., attacks). Therefore, robustness is an important criterion for evaluating machine learning models, which refers to the ability of a model to maintain stable and accurate performance even in the presence of corrupted data. It goes beyond achieving reliable performance on clean datasets and encompasses the resilience of models against noise, distortions, variation, and adversarial attacks. Robustness not only ensures the generalization and reliability of the model, but also makes the model more interpretable. 

One of the frequently occurring perturbations is additive random noise, which is the focus of our work. Gaussian noise is a commonly observed type of noise and is often present in various systems, including electronic components. The Central Limit Theorem (CLT) suggests that under certain conditions, the sum or average of a large number of independent and identically distributed (i.i.d.) random variables will approximately follow a Gaussian distribution, regardless of the original distribution of the variables. Furthermore, the Gaussian distribution is defined with only two parameters, mean and variance, given which it is the maximum entropy distribution. Due to these excellent mathematical properties, the noise is generally assumed to be Gaussian. In order to enhance robustness in the presence of noise, data augmentation methods have been proposed that involve adding Gaussian noise to the training data. This technique is commonly referred to as noise injection and has been theoretically demonstrated to be equivalent to adding penalty terms to the cost function (Reed et al., 1992; Matsuoka, 1992; Bishop, 1995; An, 1996; Grandvalet et al., 1997), thus improving the model generalization ability. 

*These authors contributed equally. 



<!-- Start of picture text -->
0.6 i — a=2<br>[: meee Q=15<br>0.4 “| -- a=l1<br>I es = O5<br>0.0 5a SAS<br>-5.0 -2.5 0.0 25 5.0<br><!-- End of picture text -->

_PRIME AI paper_ 

noise is effective for improving neural network robustness, contributing to the development of more robust and reliable deep learning models. 

## **2 RELATED WORK** 

### **2.1 Robustness of Neural Networks** 

There have been many empirical and theoretical analyses about the robustness of neural networks in the face of various types of perturbations, including structured transformation (Larochelle et al., 2007), adversarial perturbations (Szegedy et al., 2013; Fawzi et al., 2016, 2018), random noise (Fawzi et al., 2016, 2018) and universal perturbations (Moosavi-Dezfooli et al., 2017). They test the models on perturbed data, and observe the prediction performance. Neural networks have different robustness to random noise, adversarial perturbations and structural transformations. Universal perturbations are observed to have both cross-image and cross-model universality. 

It is worth clarifying that our work is concerned with random noise, which differs from adversarial perturbation in that random noise is not intentionally designed, but naturally generated during the data generation or collection, whereas adversarial perturbation is carefully designed, usually through optimization methods to find the minimum perturbation that makes the model make wrong predictions. 

### **2.2 Noise Injection** 

A frequently used method to improve the robustness of neural networks is data augmentation, a technique of artificially expanding a dataset by applying various transformations or modifications to the existing data samples. One branch of data augmentation is noise injection, which means introducing random noise in training process. Early experimental studies have found that training with noisy signals can improve generalization performance (Plaut et al., 1986; Sietsma and Dow, 1988). It is proved that the method of introducing additive noise is asymptotically consistent (Holmstrom et al., 1992). Moreover, several mathematical analyses have been performed based on Taylor expansion of the cost function, theoretically showing that under certain assumptions, training with random input noise is equivalent to Lagrangian regularization with a derivative regularizer (Reed et al., 1992), a sensitivity penalty term to the loss function (Matsuoka, 1992), or Tikhonov regularization (Bishop, 1995), thus improving the model generalibility. (An, 1996) challenges the previous three studies and argues that adding noise is not exactly equivalent to the regularization method. This is because noise not only introduces a regularization term to the cost function, but also a term depending on the fitting residues, which is not noticed by the aforementioned studies. (Grandvalet et al., 1997) connect Gaussian noise injection and heat kernel, providing a new insight to explain the effect of noise injection on the cost function. In order to prevent the adverse effect of noise injection on the cost function, a modified cost function is proposed (Seghouane et al., 2002). It is also shown that noise benefits accelerating back propagation (Audhkhasi et al., 2013; Kosko et al., 2020). 

In addition to the above theoretical research, there are also plenty of empirical studies on the effectiveness of training with noise. Noise injection is found to be as effective as or even outperform weight decay and early stopping (Zur et al., 2009). It has been also revealed that by strategically incorporating carefully tuned additive noise patterns during training on clean samples, we can achieve superior performance compared to most existing state-of-the-art defense methods against common corruptions (Rusak et al., 2020a,b). The effectiveness of noise injection in improving generalization performance has been demonstrated experimentally in various scenarios of deep learning, including discrete time backpropagation trained network (Reyes and Duro, 2001), ensemble learning (Zhang, 2007; Ahn, 2020), time series forecasting (Huang, 2008), ECG signal classification (Ochoa-Brust et al., 2019; Venton et al., 2021), speech recognition (Yin et al., 2015), inverse problems (Isaev and Dolenko, 2016; Isaev et al., 2018), and decentralized training (Adilova et al., 2019). It is also discovered that noise level has an effect on generalization improvement (Reyes and Duro, 2001; Huang, 2008), and methods of selecting noise are proposed (Holmstrom et al., 1992; Moreno-Barea et al., 2018; Ning et al., 2021). 

The majority of existing research has focused on Gaussian noise, which is a special case of the _α_ -stable distribution where _α_ is 2. There have also been studies that utilize speckle noise for data augmentation (Rusak et al., 2020b), but in fact, speckle noise is also a form of heavy-tailed noise. To the best of our knowledge, this is the first study to investigate the effectiveness of using _α_ -stable noise for data augmentation. 

3 

_PRIME AI paper_ 

## **3 METHODOLOGY** 

### **3.1 Datasets** 

In the study, different _α_ -stable noises are added to classical datasets, including two image datasets, MNIST (LeCun and Cortes, 2010) and CIFAR10 (Krizhevsky, 2009), and two time series datasets, ECG200 (Olszewski et al., 2001) and LIBRAS (Dua and Graff, 2017). MNIST is a dataset of hand-written digit images with 10 classes (digits 0 to 9) and 70,000 images. CIFAR10 is a dataset of 60,000 color images with 10 different categories. ECG200 is a dataset of electrocardiograms, each series capturing the electrical activity during one heartbeat. The dataset consists of two categories: normal heartbeat and myocardial infarction. LIBRAS, which stands for ”Lingua BRAsileira de Sinais”, is the official Brazilian sign language. It contains 15 different types of hand movements. The hand movements are represented as bi-dimensional curves that trace the path of the hand over time. Different types of datasets are used to demonstrate the generality of our approach. All of these datasets are related to classification tasks. The shape of samples and the size of the training set and testing set of all datasets are shown in Table 1. 

In addition to the above datasets, we also select benchmark datasets on the neural network robustness to common corruptions and perturbations, including MNIST-C(Mu and Gilmer, 2019) and CIFAR10-C(Hendrycks and Dietterich, 2019), to evaluate our proposed data augmentation method. These datasets are the corrupted versions of MNIST and CIFAR10, respectively, and they encompass a wide range of common perturbations, including Gaussian noise, impulse noise, blur, weather conditions, etc. These two datasets are used solely for testing purposes and are not used for training. 

### **3.2 Symmetric** _α_ **-Stable Noise** 

Our noise is generated from symmetric _α_ -stable distribution (Samorodnitsky and Taqqu, 1994), which is defined by the Fourier Transform of its characteristic function, 



where _ϕ_ ( _t_ ) can be expressed as 



Here _δ_ is the location parameter, _γ_ is the dispersion parameter, and _α_ is the characteristic exponent, which controls the thickness of the tails of the distribution and ranges from 0 to 2. Smaller _α_ means heavier tails. When _α_ = 2, it degenerates to Gaussian distribution. When _α_ = 1, it degenerates to Cauchy distribution. When _α <_ 2, the variance is infinite and when _α <_ 1, the finite mean does not exist. We control the _α_ of the noise to explore its influence on the model, as will be described in detail in the next section. 

## **4 EXPERIMENTS** 

### **4.1 Noisy Dataset Generation** 

To generate _α_ -stable noise, we utilize the ”levy ~~s~~ table” module from the scipy.stats package in Python. 

Different levels of _α_ -stable noise are introduced to each image or time series, with the level of noise controlled by varying the value of _α_ . We set the location parameter _δ_ to 0. The tails of the distribution become thicker as the _α_ value decreases, but it is important to note that the severity of noise is also influenced by the value of dispersion parameter _γ_ . Therefore, we select a range of different _γ_ values for each _α_ and conduct several experiments to find the corresponding optimal _γ_ values. The range of _γ_ choices is illustrated in Table 2. 

Table 1: Dataset Information 

|Dataset|Shape of|Training|Testing|# of|
|---|---|---|---|---|
||Samples|Set Size|Set Size|Classes|
|MNIST|(28,28,1)|60000|10000|10|
|CIFAR10|(32,32,3)|50000|10000|10|
|ECG200|(96,1)|100|100|2|
|LIBRAS|(45,2)|90|90|15|



4 



<!-- Start of picture text -->
clean data<br><!-- End of picture text -->



<!-- Start of picture text -->
a=2 a=1.9<br><!-- End of picture text -->

a=1.5 a=1.3 a=1 -i,5=ihb=i **e** ai i as ch Ras e ray re a=0.9 a=0.5 mixture ee pe oe eel . a . ir. . sae = har4 . ry : 



<!-- Start of picture text -->
0.50 0.50 6<br>0.25 — original 0.25 : — original j 0.5 i<br>=-- a=2 . H abi aq -n- w=15 : ool J! hy hat<br>0.00 0.00 n Lil 1 ' .<br>-0.25 t , 1 "4 0.25 I | H ‘. itn1 7 2 ""i -0.5_ MaghI ! 1 i<br>‘<br>0.50 ny 0507 1 Ww — original|| 0 Pm aT 1.0 — original<br>-0.75 ? 0.75 " --- @=19 ; is --- @=13<br>0 20 40 60 80 0 20 40 60 80 0 20 40 60 80 0 20 40 60 80<br>1.0 | — original 8 i— original 0 rr 9 H<br>0.5 i --- a@=1 6 §--- a=0.9 '<br>' t ' -250 H _ H<br>0.0, H ul 0 4 H 500 W<br>-0.5 u i H H -100 H<br>WA H 2 il -750 — H — |<br>1.0 4 ' i] " 5 — original | — original i<br>, 4 | 07 beera 410004] --- a= 05 | ~150) --- a= mixture |<br>0 20 40 60 80 0 20 40 60 80 0 20 40 60 80 0 20 40 60 80<br><!-- End of picture text -->



<!-- Start of picture text -->
1.0<br>I<br>i]<br>I<br>i]<br>I<br>i]<br>i]<br>SSan BEeeee !<br>tei EE ET TY !<br>0.8 fs:<br>as a = ~ aT“Ss ==222 !1 a a<br>~S oo<br>~ Sse Sy !<br>0.6 ~e SSE<br>o ssn . SS s XSOR‘. i]I ;<br>© ~S, ‘$s!<br>o ~<br>5 fo I<br>w)© 0.4 -@- clean data \\ 1H<br>-@--@- trainGaussian a = mixture,noise, y =y =0.177 0.177 N ' H<br>-@ train a = multiple, y = 0.177 1<br>-@ traina=1.9, y= 0.247<br>0.2 -@ train~=1.5, y= 0.141<br>traina =1.3, y= 0.106 H<br>-@ traina=1.0, y=0.071 H<br>® traina =0.9, y=0.071<br>6- traina = 0.5, y= 0.035 '<br>0.0<br>clean 2 1.9 1.5 1.3 1 0.9 0.5 mixture: multiple:<br>test a<br><!-- End of picture text -->



<!-- Start of picture text -->
1.0<br>I<br>i]<br>I<br>i]<br>I<br>I<br>0.8 a I<br>— i]<br>So COLL Litt Cheer Ss !<br>‘ SSH~~ TR<br>> 0.6 ws LLth \Oy<br>UO \ ‘\ NSaN I<br>—_ \ I<br>a)© “th s a \ Ioe<br>OU° ySy SA \%\ |I ¢<br>0.4 -@- clean data te. ‘, H t<br>-$- Gaussian noise, y = 0.071 ‘A , H<br>-@ train a = mixture, y = 0.021 “p-<br>-@ train a = multiple, y = 0.035 oh. ‘<br>-@ traina=1.9, y=0.071 ws<br>0.24 -@ traina =1.5, y = 0.035 %<br>traina = 1.3, y= 0.035 H<br>-@ traina=1.0, y= 0.028 |<br>6 traina =0.9, y= 0.021<br>6- traina =0.5, y= 0.021 H<br>0.0<br>clean 2 1.9 1.5 1.3 1 0.9 0.5 mixture multiple<br>test a@<br><!-- End of picture text -->



<!-- Start of picture text -->
1.0<br>I<br>i]<br>=litss Pred<br>SN ae La Soon -<br>0.84 fo Slee -L SOS SRS 5 .<br>- “Sy, wSy “ Se a !<br>> Sy - x ~ 4. i<br>@ “@ ~~ \Y sy . ae %. I<br>@ ene SON, rd Sy I<br>SSE 7 SN oe SS. -5 1 T<br>| i I I<br>0.6 ~ SOE.Tsay Soea SENNCASO HBt ¢<br>~ ar Sse sO H @<br>6) iets tetera Oe<br>© a a<br>Lu I<br>iw)Oo I<br>Oo I<br>5 :<br>0.4 -@- clean data H<br>-$- Gaussian noise, y = 0.141 H<br>-@- train a = mixture, y = 0.106<br>-@ train a = multiple, y = 0.071 ‘<br>-@ traina=1.9, y=0.141 !<br>0.24 -& traina =1.5, y= 0.071<br>e- traina =1.3, y= 0.028 H<br>-@ traina =1.0, y= 0.035<br>6- train a = 0.9, y = 0.007 !<br>@ traina = 0.5, y= 0.014 ‘<br>0.0<br>clean 2 1.9 1.5 1.3 1 0.9 0.5 mixture multiple<br>test a@<br><!-- End of picture text -->



<!-- Start of picture text -->
1.0<br>i]<br>I<br>i]<br>i]<br>~ i]<br>0.8 ésSe !I<br>SSijpseece H<br>o a TaSES Bee. i<br>N X S< = _ I<br>0.6 _ . ae SSa < ; H 3 :<br>~ Se h > ee ~ASSSS $<br>U are SS *S2>% SD <> ! TI<br>o ~o ‘ ae s rs SL H<br>oO a h a \ St MW H<br>ww)© ‘SS Sz are> ‘a)‘Ss, a"\N !1<br>0.4"" -@- clean data { — rn x ae . aN st c} r<br>| -@- Gaussian noise, y = 0.141 “a SN BL _y Yi ~t<br>-$- train a = mixture, y = 0.021 an Soe sg WY<br>-$ train a = multiple, y = 0.106 *S, 35 A \\g |<br>-@ Ss<br>traina =1.9, y=0.177 TENS ‘ 3 H<br>0.241 ~& traina=1.5,y=0.141 ON<br>. train a = 1.3, y = 0.064 ssSe!\<br>-@ train. a= 1.0, y = 0.064 |<br>@- train a = 0.9, y = 0.049<br>6- traina =0.5, y= 0.014 1<br>0.0<br>clean 2 1.9 1.5 1.3 1 0.9 0.5 mixture: multiple:<br>test a<br><!-- End of picture text -->

_PRIME AI paper_ 

Table 7: Average Accuracy Across the Entire CIFAR10-C Dataset, Accuracy of Various Models on Different Representative Corruption Types and Model Sparsity 

|Model|Average|Impulse noise|Accura<br>Spatter|cy<br>Gaussian<br>Blur|Defocus<br>Blur|Glass<br>Blur|Model Sparsity|
|---|---|---|---|---|---|---|---|
|Clean|60.45%|49.11%|67.40%|60.68%|66.86%|33.44%|47.05%|
|Gaussian noise|65.29%|62.99%|67.38%|60.91%|64.69%|58.31%|51.62%|
|Multiple noise|68.46%|74.23%|70.99%|**67.85%**|**70.25%**|65.45%|54.60%|
|Cauchynoise|**68.91%**|**75.56%**|**71.57%**|66.86%|69.40%|**66.63%**|**59.49%**|



like ECG and MRI, holds promising prospects. Furthermore, while our current research primarily centers around image and time series data, it is imperative to acknowledge that noise exerts a substantial influence on audio, video, text, and various other forms of data in everyday life. Consequently, this work lends itself to future extensions encompassing diverse data types, facilitating an exploration of the impact of _α_ -stable noise on each domain. Additionally, we have only explored the role of _α_ -stable noise in classification tasks so far. In the future, it is worth investigating its impact on other supervised learning tasks such as regression, object detection, and more. 

## **References** 

- Adilova, L., Paul, N., and Schlicht, P. (2019). Introducing noise in decentralized training of neural networks. In _ECML PKDD 2018 Workshops: DMLE 2018 and IoTStream 2018, Dublin, Ireland, September 10-14, 2018, Revised Selected Papers 18_ , pages 37–48. Springer. 

- Ahn, K.-H. (2020). A neural network ensemble approach with jittered basin characteristics for regionalized low flow frequency analysis. _Journal of Hydrology_ , 590:125501. 

- An, G. (1996). The effects of adding noise during backpropagation training on a generalization performance. _Neural computation_ , 8(3):643–674. 

- Aubry, A., Maio, A. D., Carotenuto, V., and Farina, A. (2016). Radar phase noise modeling and effects-part i : Mti filters. _IEEE Transactions on Aerospace and Electronic Systems_ , 52(2):698–711. 

- Audhkhasi, K., Osoba, O., and Kosko, B. (2013). Noise benefits in backpropagation and deep bidirectional pretraining. In _The 2013 International Joint Conference on Neural Networks (IJCNN)_ , pages 1–8. IEEE. 

- Berger, J. M. and Mandelbrot, B. (1963). A new model for error clustering in telephone circuits. _IBM Journal of Research and Development_ , 7(3):224–236. 

- Bishop, C. M. (1995). Training with noise is equivalent to tikhonov regularization. _Neural computation_ , 7(1):108–116. 

- Dua, D. and Graff, C. (2017). UCI machine learning repository. 

- Fawzi, A., Fawzi, O., and Frossard, P. (2018). Analysis of classifiers’ robustness to adversarial perturbations. _Machine learning_ , 107(3):481–508. 

- Fawzi, A., Moosavi-Dezfooli, S.-M., and Frossard, P. (2016). Robustness of classifiers: from adversarial to random noise. _Advances in neural information processing systems_ , 29. 

- Grandvalet, Y., Canu, S., and Boucheron, S. (1997). Noise injection: Theoretical prospects. _Neural Computation_ , 9(5):1093–1108. 

- Hassibi, B. and Stork, D. (1992). Second order derivatives for network pruning: Optimal brain surgeon. _Advances in neural information processing systems_ , 5. 

- Hendrycks, D. and Dietterich, T. (2019). Benchmarking neural network robustness to common corruptions and perturbations. _arXiv preprint arXiv:1903.12261_ . 

- Hoefler, T., Alistarh, D., Ben-Nun, T., Dryden, N., and Peste, A. (2021). Sparsity in deep learning: Pruning and growth for efficient inference and training in neural networks. _The Journal of Machine Learning Research_ , 22(1):10882– 11005. 

- Holmstrom, L., Koistinen, P., et al. (1992). Using additive noise in back-propagation training. _IEEE transactions on neural networks_ , 3(1):24–38. 

- Huang, T. (2008). Prior training with jittered series for time series forecasting. In _2008 IEEE International Conference on Industrial Engineering and Engineering Management_ , pages 2001–2005. 

11 

_PRIME AI paper_ 

- Isaev, I., Burikov, S., Dolenko, T., Laptinskiy, K., Vervald, A., and Dolenko, S. (2018). Joint application of group determination of parameters and of training with noise addition to improve the resilience of the neural network solution of the inverse problem in spectroscopy to noise in data. In _Artificial Neural Networks and Machine Learning– ICANN 2018: 27th International Conference on Artificial Neural Networks, Rhodes, Greece, October 4-7, 2018, Proceedings, Part I 27_ , pages 435–444. Springer. 

- Isaev, I. and Dolenko, S. (2016). Training with noise as a method to increase noise resilience of neural network solution of inverse problems. _Optical Memory and Neural Networks_ , 25:142–148. 

- Kalavathi, P. and Priya, T. (2016). Removal of impulse noise using histogram-based localized wiener filter for mr brain image restoration. In _2016 IEEE International Conference on Advances in Computer Applications (ICACA)_ , pages 4–8. 

- Karakus¸, O., Kuruo˘glu, E. E., and Altınkaya, M. A. (2018). Generalized bayesian model selection for speckle on remote sensing images. _IEEE Transactions on Image Processing_ , 28(4):1748–1758. 

- Karakus¸, O., Kuruo˘glu, E. E., and Altınkaya, M. A. (2020). Modelling impulsive noise in indoor powerline communication systems. _Signal, image and video processing_ , 14(8):1655–1661. 

- Kosko, B., Audhkhasi, K., and Osoba, O. (2020). Noise can speed backpropagation learning and deep bidirectional pretraining. _Neural Networks_ , 129:359–384. 

- Krizhevsky, A. (2009). Learning multiple layers of features from tiny images. Technical report. 

- Larochelle, H., Erhan, D., Courville, A., Bergstra, J., and Bengio, Y. (2007). An empirical evaluation of deep architectures on problems with many factors of variation. In _Proceedings of the 24th international conference on Machine learning_ , pages 473–480. 

- LeCun, Y. and Cortes, C. (2010). MNIST handwritten digit database. 

- LeCun, Y., Denker, J., and Solla, S. (1989). Optimal brain damage. _Advances in neural information processing systems_ , 2. 

- Lee, W., Nam, H. S., Seok, J. Y., Oh, W.-Y., Kim, J. W., and Yoo, H. (2023). Deep learning-based image enhancement in optical coherence tomography by exploiting interference fringe. _Communications Biology_ , 6(1):464. 

- L´evy, P. (1937). _Theorie de l’addition des variables aleatoires [Combination theory of unpredictable variables]_ . Gauthier-Villars, Paris. 

- Matsuoka, K. (1992). Noise injection into inputs in back-propagation learning. _IEEE Transactions on Systems, Man, and Cybernetics_ , 22(3):436–440. 

- Molchanov, D., Ashukha, A., and Vetrov, D. (2017). Variational dropout sparsifies deep neural networks. In _International Conference on Machine Learning_ , pages 2498–2507. PMLR. 

- Moosavi-Dezfooli, S.-M., Fawzi, A., Fawzi, O., and Frossard, P. (2017). Universal adversarial perturbations. In _Proceedings of the IEEE conference on computer vision and pattern recognition_ , pages 1765–1773. 

- Moreno-Barea, F. J., Strazzera, F., Jerez, J. M., Urda, D., and Franco, L. (2018). Forward noise adjustment scheme for data augmentation. In _2018 IEEE symposium series on computational intelligence (SSCI)_ , pages 728–734. IEEE. 

- Mu, N. and Gilmer, J. (2019). Mnist-c: A robustness benchmark for computer vision. _arXiv preprint arXiv:1906.02337_ . 

- Ning, K.-P., Tao, L., Chen, S., and Huang, S.-J. (2021). Improving model robustness by adaptively correcting perturbation levels with active queries. In _Proceedings of the AAAI Conference on Artificial Intelligence_ , volume 35, pages 9161–9169. 

- Ochoa-Brust, A. M., Mena, L. J., Felix, V. G., Gonz´alez, A., Mata-L´opez, W. A., and Maestre, G. (2019). Noisetolerant modular neural network system for classifying ECG signal. _Informatica (Slovenia)_ , 43(1). 

- Olszewski, R. T., Maxion, R., and Siewiorek, D. (2001). _Generalized Feature Extraction for Structural Pattern Recognition in Time-Series Data_ . PhD thesis, USA. AAI3040489. 

- Plaut, D. C. et al. (1986). Experiments on learning by back propagation. 

- Reed, R., Oh, S., Marks, R., et al. (1992). Regularization using jittered training data. In _International joint conference on neural networks_ , volume 3, pages 147–152. 

- Reyes, J. S. and Duro, R. J. (2001). Influence of noise on discrete time backpropagation trained networks. _Neurocomputing_ , 41(1-4):67–89. 

- Rusak, E., Schott, L., Zimmermann, R. S., Bitterwolf, J., Bringmann, O., Bethge, M., and Brendel, W. (2020a). Increasing the robustness of dnns against image corruptions by playing the game of noise. _CoRR_ , abs/2001.06057. 

12 

_PRIME AI paper_ 

- Rusak, E., Schott, L., Zimmermann, R. S., Bitterwolf, J., Bringmann, O., Bethge, M., and Brendel, W. (2020b). _A simple way to make neural networks robust against diverse image corruptions_ , page 53–69. 

- Salas-Gonzalez, D., Kuruoglu, E. E., and Ruiz, D. P. (2009). Finite mixture of _α_ -stable distributions. _Digital Signal Processing_ , 19(2):250–264. 

- Samorodnitsky, G. and Taqqu, M. S. (1994). _Stable non-gaussian random processes: stochastic models with infinite variance_ . New York: Chapman-Hall. 

- Seghouane, A.-K., Moudden, Y., and Fleury, G. (2002). On learning feedforward neural networks with noise injection into inputs. In _Proceedings of the 12th IEEE Workshop on Neural Networks for Signal Processing_ , pages 149–158. IEEE. 

- Shao, M. and Nikias, C. L. (1993). Signal processing with fractional lower order moments: stable processes and their applications. _Proceedings of the IEEE_ , 81(7):986–1010. 

- Shen, X., Zhang, H., Xu, Y., and Meng, S. (2015). Observation of alpha-stable noise in the laser gyroscope data. _IEEE Sensors Journal_ , 16(7):1998–2003. 

- Sietsma and Dow (1988). Neural net pruning-why and how. In _IEEE 1988 international conference on neural networks_ , pages 325–333. IEEE. 

- Simsekli, U., G¨urb¨uzbalaban, M., Nguyen, T. H., Richard, G., and Sagun, L. (2019). On the heavy-tailed theory of stochastic gradient descent for deep neural networks. _CoRR_ , abs/1912.00018. 

- Singh, P., Bhole, K., and Sharma, A. (2017). Adaptive filtration techniques for impulsive noise removal from ecg. In _2017 14th IEEE India Council International Conference (INDICON)_ , pages 1–4. 

- Srinivasan, V., Kuruoglu, E. E., M¨uller, K.-R., Samek, W., and Nakajima, S. (2019). Black-box decision based adversarial attack with symmetric _α_ -stable distribution. In _2019 27th European Signal Processing Conference (EUSIPCO)_ , pages 1–5. 

- Stuck, B. W. and Kleiner, B. (1974). A statistical analysis of telephone noise. _Bell System Technical Journal_ , 53(7):1263–1320. 

- Szegedy, C., Zaremba, W., Sutskever, I., Bruna, J., Erhan, D., Goodfellow, I., and Fergus, R. (2013). Intriguing properties of neural networks. _arXiv preprint arXiv:1312.6199_ . 

- Venton, J., Harris, P. M., Sundar, A., Smith, N. A., and Aston, P. J. (2021). Robustness of convolutional neural networks to physiological electrocardiogram noise. _Philosophical Transactions of the Royal Society A_ , 379(2212):20200262. 

- Windyga, P. S. (2001). Fast impulsive noise removal. _IEEE transactions on image processing_ , 10(1):173–179. 

- Yin, S., Liu, C., Zhang, Z., Lin, Y., Wang, D., Tejedor, J., Zheng, T. F., and Li, Y. (2015). Noisy training for deep neural networks in speech recognition. _EURASIP Journal on Audio, Speech, and Music Processing_ , 2015:1–14. 

- Zantedeschi, V., Nicolae, M., and Rawat, A. (2017). Efficient defenses against adversarial attacks. In Thuraisingham, B., Biggio, B., Freeman, D. M., Miller, B., and Sinha, A., editors, _Proceedings of the 10th ACM Workshop on Artificial Intelligence and Security, AISec@CCS 2017, Dallas, TX, USA, November 3, 2017_ , pages 39–49. ACM. 

- Zhan, C., Yan, M., and Hao, D. (2019). Recovery performance of lplq-admm algorithm under s _α_ s impulse noise. In _2019 IEEE-APS Topical Conference on Antennas and Propagation in Wireless Communications (APWC)_ , pages 079–084. IEEE. 

- Zhang, G. P. (2007). A neural network ensemble method with jittered training data for time series forecasting. _Information Sciences_ , 177(23):5329–5346. 

- Zur, R. M., Jiang, Y., Pesce, L. L., and Drukker, K. (2009). Noise injection for training artificial neural networks: A comparison with weight decay and early stopping. _Medical physics_ , 36(10):4810–4818. 

13 

