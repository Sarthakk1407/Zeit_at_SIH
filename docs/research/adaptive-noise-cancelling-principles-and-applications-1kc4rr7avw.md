PROCEEDINGS OF THE IEEE, VOL. **63,** NO. **12,** DECEMBER **1975** 

   - tuations in the atmosphere” (in Russian), **_Zzv. Vysch. Ucheb._** paper ThB5-1, July **1974.** **_Zuved., Radiofiz.,-vol._ 17,** pp. **105-112,  1974.** [ **1881** D. Slepian, “Linear least-squares filtering of distorted images,” **_J. Opt. SOC.  Amer.,_** vol. **57,** pp. **918-922,** July **1967.** 

   - [ **1891** H. Yura,  Holography in a random spatially  inhomogeneous medium,”Appl. **_Opt.,_** vol. **12,** pp. **1188-1192,** June **1973.** 

- [ **181** 1 D. Fried, “Differential angle of arrival; theory, evaluation, and measurement feasibility,” **_Radio Sei.,_** vol. **10,** pp. **71-76,** Jan. **1975.** 

- **11821** J. Lowry, J. Wolf, and **J.** Carter,  “Acquisition  and  tracking assembly,” McDonnell Douglas Tech. Rep. for **Air** Force Avionics Lab., Tech. Rep. AFAL-TR-73-380,  Feb. **15,  1974.** 

   - **_Section VIII_** 

   - [ **1901** C. Gardner and **M.** Plonus, “The effects of atmospheric turbulence **on** the propagation of pulsed laser beams,” **_Radio_ Sci.,** vol. **10,** pp. **129-137,** Jan. **1975.** 

- [ **1831** V. Lukin, V. Pokasov, and **S.** Khmelevstov, “Investigation of the time  characteristics of fluctuations of the phases of  optical waves propagating in the bottom layer of the atmosphere,” **_Radiophys. Quantum Electron.,_** vol. **15,** pp. **1426-1430,** Dec. **1972.** 

###### **_Section ZX_** 

   - [ **191** ] L. Apresyan, “The radiative-transfer equation with allowance for longitudinal waves,” **_Radiophys. Quantum Electron.,_** vol. **16,** pp. **348-356,** Mar. **1973.** 

- **[184]** R. Lutomirski  and R. Buser, “Phase difference and angle-ofarrival fluctuations in tracking a moving point source,” **_Appl. Opt.,_** vol. **13,** pp. **2869-2873,** Dec. **1974.** 

   - [ **192)** Y. Barabanenkov, A. Vinogradov, Y. Kravtsov, and V. Tatarski, “Application of the theory of multiple scattering of waves to the derivation of the radiation transfer equation for a statistically inhomogeneous  medium,” **_Radiophya  Quantum  Electron.,_** vol. **15,** pp. **1420-1425,** Dec. **1972.** 

   - [ **1931** C. Martens and N. Jen, “Electromagnetic wave scattering from a turbulent plasma,” **_Radio_ Sci.,** vol. **10,** pp. **221-228,** Feb. **1975.** 

   - [ **1941** I. Besieris, “Long-range electromagnetic random wave propagation using the parabolic equation method,” **_Dig. 1975 URSZ Meet.,_** p. **15,** June **1975.** 

- [ **185 1** R. Lutomirski and R. Warren, “Atmospheric distortions in a retroreflected laser signal,” **_Appl. Opr.,_** vol. **14,** pp. **840-846,** Apr. **1975.** 

- **[186]** R. Lutomirski and H. Yura, “Imaging of extended objects through a turbulent atmosphere,” **_AppL Opt.,_** vol. **13,** pp. **431-437,** Feb. **1974.** 

- [ **1871** J. Pearson **_e? al.,_** “Atmospheric turbulence compensation using coherent  optical  adaptive  techniques,”  presented at OSATopical Meeting on Propagation Through Turbulence, Boulder, Colo., 

# **Adaptive  Noise  Cancelling:  Principles  and  Applications** 

BERNARD WIDROW, SENIOR MEMBER, IEEE, JOHN R.  GLOVER, JR., MEMBER, IEEE, JOHN M. MCCOOL, SENIOR MEMBER, IEEE, JOHN KAUNITZ, MEMBER, IEEE, CHARLES **s.** WILLIAMS, STUDENT MEMBER, IEEE, ROBERT H. H E A N , JAMES R.  ZEIDLER, EUGENE DONG, JR., AND ROBERT **C.** GOODLIN 

**_Abstmct-This_ paper** describes **the** concept **of adaptive noise** cancelling, **an  alternative method of estimating signals corrupted by additive** noise **or interfmm. The method** uses **a “primary” input** containing **the comrpted** **_Signrl_ and a “reference” input** containiug noise _corre-_ lated **in some unknown way with the primary noise. The refaence input is adaptively filtered and subtracted** from **the primary input to obtain the** **_signal_ estimate. Adaptive filtering before subtraction allows the treatment of inputs  that are deterministic or stochastic, stationary or time variable. Wiener sdutions are developed to describe ~symptotic adaptive performance and output signal-to-noise ratio for stptiollpy stochastic  inputs, including  single  and multiple reference  inputs.** These 

Manuscript received March **24,1975;** August **7,  1975.** 

This work was supported in part by  the National Science Foundation under  Grant ENGR **74-21752,** the National Institutes of Health  under Grant lROlHL183074JlCVB, and the Naval Ship Systems Command under Task Assignment **SF 11-121-102.** 

B. Widrow and C. **S.** WiUiams are with the Information Systems 

Laboratory, Department  of Electrical Engineering, Stanford University, Stanford, Calif. **94305.** 

**J.** R. Glover, Jr., was with the Information Systems Laboratory, Department of Electrical Engineering, Stanford University, Stanford, Calif. He is now with the Department of Electrical Engineering, University of Houston,  Houston, Tex. 

**J.** M. McCool, R. H. H e m , and J. R. Zeidler are with  the Fleet Engineering Department, Naval Undersea Center, San Diego, Calif. **92132.** 

**J.** Kaunitz was with the Information Systems Laboratory, Department of Electrical Engineering, Stanford University, Stanford, Calif. He is now with Computer Sciences of  Australia, St. Leonards, N. **S: W.,** Australia, **2065.** 

E. Dong, Jr., and R. C. Goodlin are with the School of Medicine, Stanford University, Stanford, Cailf. **94305.** 

**reference input** **_cer-_ tain other** conditions **are met noise in the  primary input** can **be** essen- **_W I y_ eliminated without sigrul** distortion. **It is further shown that in** treating **pedodic** intederence **the adaptive noise candler acts as a notch filter** with **narrow bandwidth,** inlmite **nun, and  the capability of tracking the  exact  frequency of the** interference; **in** _this case_ **the** can- **der behaves as a** liners, **time-h-t systan,with the adaptive** filter _converging_ **on a dynamic rather thm a static solution. Experimental results are presented that** illusbate **the** usefulness **of the adaptive noise** _candling_ **technique in a variety** **_of_ practical applicalitms. These** **_ap-_ plications  include  the** candling **of various forms  of periodic interfezence in elec-hy, the candling of** periodic **interference in** **_speecfi signals,_ and the candling of  brod-bmd** interference **in the** **_side-_ lobes of an antenna amy. In** further **experiments it is shown that a sine wave and Gaussian** noise **_can_ be sepamted by** using **a reference input that is a delayed vezsion of the primary  input. Suggested a p p h - tions include  the  elimination  of** tape **hum** **_or_ turntable rumble during the playback of liecofded broad-band** **_signals_ and the automatic  detec-** _tion_ **of  very4ow4evel** pewdic **_signals_ masked by b d - b m d noise.** 

##### I. INTRODUCTION 

**HE USUAL** method of estimating a **signal** corrupted by additive noise’ is to pass it  through a fiiter  that  tends to suppress the noise while  leaving the **signal** relatively unchanged. The design  of such  filters is the domain of optimal filtering, which originated with .the pioneering work **of** Wiener 

For simplicity the term **“noise”** is **used** in this paper to **signify all** forms  of interference,  deterministic **as** well **as** stochastic. 

WIDROW **_et al.:_** ADAPTIVE NOISE CANCELLING **1693** and was extended  and enhanced by the work of Kalman, Bucy, and others [ 11 -[ 51. Filters used for  the above purpose can be fixed or adaptive. The design  of fixed filters is  based on  prior knowledge zyxwvutsrq of both the signal and the noise. Adaptive filters, on the other hand, **OUTPUT FILTER** have the ability to adjust  their  own parameters automatically, I and their design requires little or no **_u priori_** knowledge of signal or noise characteristics. **_zyxwvuts_** 

Noise cancelling is a variation of optimal filtering that is highly advantageous in many applications. It makes use of an auxiliary or reference input derived from one  or more sensors located  at  points  in  the noise field where the signal is weak or undetectable. This input is filtered and  subtracted  from a primary input  containing  both signal and noise. As a result the primary noise is attenuated  or eliminated by cancellation. At first glance, subtracting noise from a received  signal would seem to be a dangerous procedure. If done improperly it could result in an increase in  output noise power. If, however, filtering and subtraction are controlled  by  an  appropriate adaptive process, noise reduction can be accomplished with little risk  of distorting  the signal or increasing the  output noise level. In circumstances where adaptive noise cancelling is applicable, levels  of  noise rejection are often  attainable  that would be difficult or impossible to achieve by direct filtering. The purpose of this paper is to describe the concept of adaptive noise cancelling, to provide a theoretical  treatment of its advantages and limitations,  and to describe some of the ap- 

**11.** EARLY WORK IN ADAPTIVE NOISE CANCELLING The earliest work in adaptive noise cancelling known to  the authors was performed by Howells and Applebaum and their colleagues at  the General Electric Company  between 1957 and 1960. They designed and built a system for antenna sidelobe cancelling that used a reference input derived from an auxiliary  antenna and a simple two-weight adaptive filter [6]. 

At the time of this work, only a handful of people were interested in adaptive systems,  and development of the multiweight adaptive filter was just beginning. In 1959, Widrow and Hoff at Stanford University were devising the least-meansquare (LMS) adaptive algorithm and the pattern recognition scheme known as Adaline (for “adaptive linear threshold logic element”) [ 71 , [ 81 . Rosenblatt  had  recently built his Perceptron at the Cornell Aeronautical Laboratory [9]-[ 111 **.2** Aizermann and his colleagues at the Institute of Automatics and Telemechanics in Moscow,  U.S.S.R., were constructing  an automatic gradient searching machine. In Great Britain, D. Gabor  and his associates were developing adaptive filters [ 121 . Each of these  efforts was proceeding independently. 

In the early and middle 1960’s, work on adaptive systems intensified. Hundreds of papers on adaptation, adaptive controls, adaptive filtering, and adaptive signal  processing appeared in the literature. The best known commercial application of adaptive filtering grew from the work during this period of Lucky at the Bell Laboratories [ 13 **1,** [ **141** . **His** high-speed MODEM’S for digital communication are now widely used in connecting remote terminals to computers **as** well as one  computer  to  another, allowing an increase in the rate  and accuracy of data transmission by a reduction of intersymbol  interference. 

The first adaptive noise cancelling system at Stanford University was designed and built in  1965 by two  students. Their work was undertaken **as** part of a term paper project for a course in adaptive systems given by the Electrical Engineering Department. The purpose was to cancel 60-Hz interference  at the  output of an electrocardiographic amplifier and recorder. **A** description of the system, which made use  of a two-weight analog adaptive filter, together with results recently obtained by  computer implementation, is presented in Section VIII. 

Since 1965, adaptive noise cancelling has been successfully applied to a number of additional problems, including other aspects of electrocardiography, also  described in  Section  VIII, to  the elimination of periodic interference  in general [ 151 , and to the elimination of echoes on long-distance telephone transmission  lines [ 161 , [ 171. A recent paper on adaptive antennas by Riegler and Compton [ 181 generalizes the work originally performed by  Howells and Applebaum. Riegler and Compton’s approach is  based on  the LMS algorithm and is  an application of the adaptive antenna concepts of  Widrow **_et ul._** [ 191 , [ 201 . 

##### **111.** THE CONCEPT OF ADAPTIVE NOISE CANCELLING 

Fig. 1 shows the basic problem and the adaptive noise cancelling solution to it. A signal s is  transmitted over a channel to a sensor that also  receives a noise **_no_** uncorrelated  with  the signal. The combined signal and noise **s** **_+ n o_** form the primary input to the canceller. A second sensor receives a noise **_nl_** uncorrelated  with  the signal but correlated in some unknown way with the noise **_no._ This** sensor provides the reference input  to  the canceller. The noise **_nl_** is filtered to produce an output **_y_** that is **as** close a replica **as** possible of **_no._** This output is subtracted  from  the primary input **s** + **_no_** to produce the system output **_z_** = **s** + **_no_** - **_y ._** 

If one knew the characteristics of the channels over which the noise  was transmitted to  the primary and reference sensors, it would theoretically be possible to design a fiied filter capable of changing **_nl_** into **_no._** The  filter  output could then be subtracted from the primary input, and the system output would be signal alone. Since, however, the characteristics of the transmission paths are as a rule unknown  or known only approximately and  are seldom of a fixed nature, the use of a fixed fiiter is not feasible. Moreover, even if a fixed filter were feasible, its characteristics would have to be adjusted with a precision difficult to attain, and the slightest error  could result in an increase in  output noise power. 

In the system shown in Fig. 1 the reference input is processed by **an** adaptive filter. **_An_** adaptive filter differs from a fixed fiiter in that it automatically adjusts its own impulse response. Adjustment is accomplished through an algorithm that responds to an error signal dependent, among other things, on  the filter’s output.  Thus with the proper algorithm, the filter can operate under changing conditions and can readjust itself continuously to minimize the  error signal. 

**‘This pioneering equipment now resides at the Smithsonian Institution in Washington,** D.C. 

**DECEMBER IEEE, PROCEEDINGS OF THE** 

**1694** 

The  error signal  used in an adaptive process depends  on  the nature of the application. In noise cancelling systems  the practical objective is to produce  a system output = **s** + **_no_** - y that is a best fit  in the least squares sense to the signal **s.** This objective is accomplished by feeding the system output back to the  adaptive  filter  and  adjusting  the  filter  through  an LMS adaptive algorithm to minimize total system output power.3 In an adaptive noise cancelling system, in other words, the system output serves **as** the  error signal for  the adaptive process. 

It might seem that some prior  knowledge of the signal **s** or of the noises **_no_** and **_nl_** would be necessary before the filter could be designed, or before it could adapt, to produce the noise cancelling signal y. A simple argument will show,  however, that  little  or  no  prior  knowledge of **s,** **_no,_** or **nl** , or of their interrelationships, either statistical or deterministic, is required. Assume that **s,** **_no, n_ 1,** and y are statistically  stationary  and have zero means. Assume that **s** is uncorrelated with **_no_** and **n l ,** and  suppose  that **n1** is correlated  with **_no._** The  output **_z_** is 



Squaring, one  obtains 



Taking expectations of both sides of **(2),** and realizing that **S** is uncorrelated  with **_no_** and withy, yields 

The signal power **_E [ s 2 ]_** will be unaffected **as** the fiiter is adjusted to minimize **_E[z2_** ]. Accordingly, the minimum output power is 

When the fiiter is adjusted **so** that **_E[z’_ 1 is** minimized, **_E[(no_** - y)’ ] is, therefore, **also** minimized. The  filter output  y is then a best least squares estimate of the primary noise **_no._** Moreover, when **_E[(no_** - y)’] is minimized, **_E [ ( z_** - **s)?** ] is also minimized, since, from **(I),** 

Therefore,  y = **_no,_** and **_z_** = **s.** In this case, minimizing output power causes the  output signal to be perfectly noise free! These arguments can readily be extended to the case where the primary and reference inputs contain, in addition to **_no_** and **nl** , additive  random noises uncorrelated  with each other and  with **s,** **_no,_** and **_n l_** . They  can also readily be extended to the **_case_** where **_no_** and **nl** are deterministic  rather  than stochastic. 

#### **IV. WIENER SOLUTIONS TO STATISTICAL NOISE CANCELLING PROBLEMS** 

In this section, optimal unconstrained Wiener solutions to certain statistical noise cancelling problems are derived. The purpose is to demonstrate analytically the increase in signaltonoise  ratio and other advantages of the  noire cancelling technique. Though the idealized solutions presented do not take into account the issues  of fiite fiiter length or causality, which are important in practical applications, means of approximating optimal unconstrained Wiener performance with physically realizable adaptive transversal filters  are readily available  and are described in  Appendix B. As previously noted,  fixed fiiters are for the  most  part  inapplica,ble in noise cancelling because the correlation and cross correlation functions of the  primary  and  reference  inputs are generally unknown and often variable with time. Adaptive filters are required to “learn” the statistics initially and to track  them if they vary slowly. For  stationary  stochastic inputs, however, the steady-state  performance of adaptive filters closely approximates that of fixed Wiener fiiters, and Wiener filter theory thus provides a convenient method of mathematicalfy analyzing statistical noise cancelling problems. 

Fig. **2** shows a classic single-input single-output Wiener fiiter. The input signal is **xi,** the output signal yi, and the desired response **_di._** The input and output signals are assumed to be discrete in time,  and  the  input signal and desired response are assumed to be statistically  stationary.  The  error signal is **_q_** = **_di_** - yi. The filter is linear, discrete, and designed to be optimal in the minimum mean-squareerror. sense. It is composed  of an infinitely  long, two-sided tapped delay line. 

The  optimal impulse response of this  filter may be described in the following manner. The discrete autocorrelation function of the  input signal **X i** is defined as 



Adjusting or  adapting  the  filter to minimize the  total  output power is thus  tantamount to causing the  output **_z_** to be a best least squares estimate of the signal **s** for the given structure  and adjustability of the  adaptive  fiiter  and  for  the given reference input. 

The  output **z** will contain  the signal **s** plus noise. From **(l),** the  output noise is given by **_(no_** - **_y)._** Since minimizing **_E [ z 2_** 1 minimizes **_E[(no_** - y)’] , **_minimizing the total output power minimizes  the  output  noise  power._** Since the signal in  the  output remains constant, **_minimizing  the  total  output  power_** 

The  crosscorrelation  function  between **xi** and the desired response **_di_** is similarly defiied **as** 

The optimal impulse response **_w*(k)_** _can_ then be obtained from  the discrete Wiener-Hopf equation: 

**CANCELLING** **_er al.:_ ADAPTIVE NOISE** 



<!-- Start of picture text -->
OUTPUT<br>ERROR<br>DESIRED<br>‘“i  RESPONSE<br>Fig. 2.  Singlechannel Wiener filter.<br>/  L------------------j<br>~ ~ ~ ~ ~ADAPTIVE  NOISE  CANCELLER E N C E<br>noise  canceller with correlated and un-<br><!-- End of picture text -->

response of the channel whose transfer  function is **_J € ( z ) . ~_** The noises _ni_ and **_nj_** * **_h ( j )_** have a common origin, are correlated with each other, and are uncorrelated with **_si._** They further are assumed to have a finite power spectrum at all frequencies. The noises **_m o j_** and _m_ **_l j_** are uncorrelated  with each other, with **_si,_** and with _ni_ and **_nj_** * **_h(j)._** For  the purposes of analysis all noise propagation paths are assumed to be equivalent to linear, time-invariant filters. The noise  canceller  of  Fig. **3** includes an adaptive filter whose input **_xi,_** the reference input to the canceller, **is** **_m l j_** + **_nj_** * _h ( j )_ and whose desired response **_dj,_** the primary input  to the canceller, is **_si_** + **_moi_** + **_nj._** The  error signal **_~j_ is** the noise canceller’s output. If one assumes that the adaptive process has converged and the minimum meansquareerror solution has been found, then the adaptive filter is equivalent to a Wiener filter. The optimal unconstrained transfer function of the adaptive filter is thus given  by (1 **3)** and may be written as follows. 

The spectrum of the filter’s input **_S,(z)_** can be expressed in terms of the  spectra of its  two mutually uncorrelated additive components. The spectrum of the noise **m l is** **_S m l m l ( z ) ,_** and that of the noise **_n_** arriving  via **_X ( Z )_** is **_S,,(Z)_** I **_X ( z )_** 1 ’. The filter’s input spectrum is thus 

##### The convolution  can be  more simply written as 

This form of the Wiener solution is unconstrained in  that  the impulse response **_w*(k)_** may be causal or noncausal and of finite  or  infinite  extent to the  left  or right of the  time origin.’ The  transfer  function of the Wiener fiter may  now be derived **as** follows. The powerdensity spectrum of the input 

The cross power spectrum between the filter’s input and the desired response depends  only on  the mutually correlated primary and reference components and is  given by 

The Wiener transfer  function is thus 



The cross power  spectrum  between the  input signal and desired response is 



Transfonning (8) then yields the optimal  unconstrained Wiener transfer  function: 

The application of Wiener fiter theory to adaptive noise cancelling may  now be considered. Fig. **3** shows a singlechannel adaptive noise canceller with a typical set of inputs. The primary input consists of a signal **_Si_** plus a sum of **two** noises _moi_ and **_ni._** The reference input consists of a sum of two  other noises **_m l i_** and **_ni_** * _h(j),_ where _h(j)_ is the impulse 

**The Shannon-Bode realization of the Wiener solution,  by contrast, is conatrained to a causal response. This constraint generally leads to a loss of performance and, as shown in Appendix B,** _can_ **normally be avoided in adaptive noise cancelling applications.** 

Note that **W*(z)** is independent of the primary signal spectrum **_S,(Z)_** and of the primary uncorrelated noise spectrum **_Sm,m,(z)._** An mteresting special case occurs when the additive noise **_ml_** in the reference input is zero. Then&mlml(z) is zero and the optimal  transfer  function  (1  6) becomes 



This result is intuitively appealing. The adaptive filter, **as** in the balancing of a bridge, causes the noise **_ni_** to  be perfectly nulled at  the noise canceller output.  The primary uncorrelated noise **_moj_** remains uncancelled. 

The performance of the singlechannel noise canceller  can be evaluated more generally in terms of the  ratio of the signal-tonoise density ratio  at  the  output, **pout(z)** to  the signal-to-noise density ratio  at  the primary input **_p*(z).’_** Assuming that  the signal spectrum is greater than zero at all frequencies and 

**6To simplify the notation the transfer function of the noise path from** **_nj_ to the primary  input  has been set at unity. This procedure does not restrict the analysis, since by a suitable choice of** **_X @ )_ and of statistics for** **_ni_ any combination of mutually correlated noises can be made to appear at the primary and reference inputs. Though** **_X@)_ may consequently be required to have poles inside and outside the unit circle in the Z-plane, a stable two-sided impulse response** **_hQ_** wi **l always exist.** 

> **‘Signal-to-noise density ratio is here defined as the ratio of signal power density to noise power density and is thus a function of frequency.** 

**DECEMBER IEEE, PROCEEDINGS OF THE** 

**1696** 

**_pout(z)_** - primary noise power  spectrum **_p ~ ( z )_** output noise power spectrum - **_5,(z)_** + **_5m0mO(z)_** (18) **Soutput noise(z)** . The canceller’s output noise power spectrum, **as** may be seen from **Fig.” 3,** is a sum of three components, one due to the propagation  of **_moi_** directly to the  output,  another due to the propagation of **_mli_** to the output via the transfer function - **_a*(z),_** and another  due to the  propagation of **_ni_** to the  output via the  transfer  function  1 - **_x ( z ) w * ( z ) ._** The output 

of unity).’ Classical configurations of Wiener, **Kalman,** and adaptive filters, in contrast, generally introduce some signal distortion in the process of noise reduction. It is apparent  from (24)  that  the ability of a noise cancelling system to reduce noise is limited by the  uncorrelated-tocorrelated noise density ratios at the primary and reference inputs. The smaller are **_A ( z )_** and **_B(z),_** the greater will be **_pout(z)/p*(z)_** and the more effective the action of the canceller. The desirability of low levels of uncorrelated noise in both inputs is made still more evident by considering the following special cases. 



**_2)_ l** **_Small_ ~ ~ ~** **_B(z)._ I** 

If one  lets the ratios of the  spectra of the  uncorrelated to the spectra of the  correlated noises (“noise-to-noise  density ratios”)  at  the  primary  and  reference  inputs now be defiied **as** 

**_3) Small A(z) and B(z):_** 

and 

then  the transfer  function **(17)** can be written **as** 



The  output noise power  spectrum (19) can accordingly be rewritten **as** 



The ratio of the output to the primary input noise power spectra is 

This expression is a general representation of ideal noise canceller performance with single primary and reference inputs and  stationary signals and noises. It allows one to estimate the level of **noise** reduction to be expected with an ideal noise cancelling system. In such a system the signal propagates to the  output in an undistorted **fashion** (with  a  transfer  function 

Infinite  improvement is implied by these  relations when both **_A ( z )_** and **_B(z)_** are zero. In this case there is complete removal of noise at the system output, resulting m perfect signal reproduction. When **_A ( z )_** and **_B(z)_** are small, however, other factors become important in limiting sys€em performance. These factors  include  the  finite  length of the adaptive filter  in  practical  systems, discussed in  Appendix **B,** and “misadjustment” caused by gradient  estimation noise in the adaptive process, discussed in [ 191 and [ 201 . A third  factor, signal components sometimes present in the reference input, is discussed in the  following  section. 

## v. **EFFECT OF SIGNAL COMPONENTS IN THE REFERENCE INPUT** 

In certain  instances  the available reference inpu **t** o **an** adaptive noise canceller may contain low-level signal components in addition to the usual correlated and uncorrelated noise components. There is no doubt that these signal components will cause some cancellation of the primary input signal. The question is whether  they will cause sufficient cancellation to render the application of noise cancelling useless. **_An_** answer is provided in  the  present  section  through  a quantitative analysis based, like that of the previous section, on  unconstrained Wiener filter  theory.  In  this analysis expres- **_zyxw_** sions are derived for signal-to-noise density  ratio, signal distortion, and noise spectrum at  the canceller output. 

**Fig. 4** shows an adaptive noise canceller whose reference input contains signal components  and whose primary  and reference inputs contain additive correlated noises. Additive uncorrelated noises have been  omitted to simplify the analysis. The signal components in the reference input are assumed to be propagated through a channel with the transfer function **$(z).** The  other terminology is the same **as** that of **Fig. 3.** 

**‘Some signal cancellation is possible when adaptation is rapid (that is, when the value of  the adaptation constant** **_p ,_ defined in Appendix A, is large) because of the dynamic response of the weight vector, which approaches but do=  not equal the Wiener solution. In most** **_cases_ this effect is negligible; a particular** **_case_ where it is not negligiile is described in Section VI.** 

**WIDROW er al.: ADAPTIVE NOISE CANCELLING** 

**1697** 

The signal-to-noise density  ratio  at the reference input is thus 

The output signal-to-noise density  ratio **(33)** is, therefore, **Fig. 4. Adaptive noise canceller with signal components in the reference input.** zyxwvutsrqpThis result is exact  and  somewhat surprising. It shows that, The  spectrum of the signal in Fig. **4** is S **,** (Z) and that of the assuming the adaptive solution to be unconstrained and the noise S,(z). The spectrum of the reference input, which is noises in the primary and reference inputs to be mutually identical to the  spectrum of the  input **_xi_** zyxwvuts to the adaptive  filter, correlated, the signal-to-noise density ratio at the noise canis thus celler output is simply the reciprocal  at **all** frequencies of the **_zyxwvuts_** signal-to-noise density  ratio  at the reference input. _zyxwvutsrqpS,(z)=_ S,(z)IJ(z)I' **+Snn(z)IJ€(z)12. (28)** The  next  objective of the analysis is to derive  an expression for signal distortion at the noise canceller output. The most The  cross  spectrum  between the reference  and  primary  inputs, useful  reference input is one  composed  almost entirely of identical to the cross spectrum between the fdter's input **_xi_** noise correlated with the noise in the primary input. When and  desired  response **_di,_** is similarly signal components are present  some signal distortion will S d ( Z ) = S,(Z) **_zyxwvutsrqp_ J(z-')** + S,(z) X(z-'). **(29)** generally  occur.  The  amount will depend  on the  amount of  signal propagated  through the adaptive  filter,  which may  be When the adaptive process has converged, the unconstrained determined **as** follows. The transfer function of the propagaWiener transfer  function of the  adaptive  filter, given by **(13),** tion  path  through  the filter is 

The  cross  spectrum  between the reference  and  primary  inputs, identical to the cross spectrum between the fdter's input **_xi_** and  desired  response **_di,_** is similarly 

When the adaptive process has converged, the unconstrained Wiener transfer  function of the  adaptive  filter, given by **(13), is** thus 

> When I J(z) I is small, this  function can be approximated **as** 

The first objective of the analysis is to find the signal-tonoise density ratio **pout(z)** at  the noise canceller output. The transfer  function of the propagation path from the signal input to  the noise  canceller output is 1 - J(z) W*(z) and that of the path  from  the noise input to  the canceller output is 1 - x(z) . a*(z). The spectrum of the signal component in the output is thus 

**_2_** -j(z)/X(z). **9) (3** 

The  spectrum of the signal component  propagated to the noise canceller outpu **t** hrough  the adaptive filter is thus approximately 



The  combining of this  component  with  the signal component in the primary input involves complex addition and is the process that results in signal distortion.  The  worst case, bounding the distortion to be expected in practice, occurs when the  two signal components are of opposite  phase. 

Let "signal distortion" B(z) be definedg **as** a dimensionless ratio of the spectrum of the output signal component propagated through the adaptive filter to the spectrum of the signal component  at  the  primary  input: 

The output signal-to-noise density ratio is thus 



From **(39)** it can be seen that, when J(z) is small, **(41)** reduces to 



The output signal-to-noise density  ratio  can be conveniently expressed in terms of the signal-to-noise density ratio at the reference input **_p,f(z)_ as** follows.  The  spectrum of the signal component in the  reference input is 



This expression may be rewritten in a more useful form by combining the expressions  for the signal-to-noise density  ratio at  the  primary input: 



**'Note that signal distortion as defmed here is a linear phenomenon related to alteration of the signal waveform as it appears at the noise canceller output and is not to be confused with nonlinear harmonic distortion.** 

##### and the signal-to-noise density  ratio  at  the  reference input **(36):** 

##### %z) **Pref** (Z)hpri(Z). **(44)** 

Equation **(44)** shows that, with an unconstrained adaptive solution and mutually correlated noises at the primary and reference  inputs, low signal distortion  results  from a high signal-to-noise density ratio at the primary input and a low signal-to-noise density ratio at the reference input. This conclusion is intuitively  reasonable. 

The  final  objective of the analysis is to derive an expression for  the spectrum of the  output noise. The noise nj propagates to  the  output with  a  transfer  function 

**1 - 1** 





<!-- Start of picture text -->
PROCEEDINGS OF THE IEEE, DECEMBER  1975  z<br>RECEIVING<br>ELEMENTS<br>PRIMP<br>INPUT  i  1  OUTPUT<br>z<br>" I  +w  z<br>I<br>/I<br>/I<br>INTERFERENCE<br>Fig. 5.  Adaptive noise cancelling applied to a receiving  array.<br><!-- End of picture text -->

twenty  times  greater  than  the signal power density at  the  individual array element, then the signal-to-noise ratio at the reference input **pref** is 1/20. If one further assumes that, because of array **_gain,_** the signal power equals the interference power at  the  array  output,  then  the signal-to-noise ratio  at  the primary input **pfi** is 1. After convergence of the adaptive filter  the signal-to-noise ratio  at  the  system  output will thus be 

##### **Pout** = **1/Pref** = 20. The  maximum signal distortion will similarly be 

The  output noise spectrum is 

**9** = **pref/ppri** = (1/20)/1 = **5** percent. 

In  this case, theiefore,  adaptive noise cancelling improves signal-to-noise ratio twentyfold and introduces only a small amount of  signal distortion. 

##### **VI. THE ADAPTIVE NOISE CANCELLER AS A NOTCH FILTER** 

This equation  can be more  conveniently expressed in  terms of the signal-to-noise density ratios at the reference input **(36)** and primary input **(43):** 

In certain  situations  a  primary input is available consisting of a signal component with  an  additive  undesired  sinusoidal  interference. The conventional method of eliminating such interference is through the **use** of a  notch  filter.  In  this  section an unusual form of notch filter, realized by an adaptive noise **zyxwvu** canceller, is described. The advantages of this form of notch filter  are that  it offers easy control of bandwidth, an i n f i t e null, and the capability of adaptively tracking the exact frequency of the interference. The analysis presented deals with the formation of a notch at a single frequency. Analytical and  experimental  results  show,  however, that if more than one frequency is present in the reference input a notch for each will  be formed **[211.** 

**_2_** 5nn(z)lpdz)II  ~pri(z)I. 

**This** result,  which may appear  strange  at f i t glance, can be understood  intuitively as follows. The first  factor  implies  that the output noise spectrum depends on the input noise spectrum and is readily accepted. The second factor implies that, if the signal-to-noise density  ratio at  the  reference input is low, the  output noise will  be low;  that is,  the  smaller  the signal component  in  the  reference  input,  the  more  perfectly  the noise will be cancelled.  The  third  factor implies that, if the signal-to-noise density  ratio  in the primary input  (the desired response of the adaptive  filter) is low,  the  filter will  be trained  most  effectively to cancel the noise rather than the signal and consequently output noise will be low. 

Fig. **6** shows a single-frequency noise canceller with two adaptive weights. The primary input is assumed to be any kind of signal-stochastic, deterministic, periodic, transient, etc.-or any combination of signals. The reference input is assumed to be a pure cosine wave **_C_** cos **_(wot_** + **9).** The primary and reference inputs are sampled at the frequency $2 = **2n/T** rad/s. The reference  input **_zy_** is sampled directly, giving xlj, and  after  undergoing  a **90'** phase shift, giving X;j. The samplers are synchronous  and  strobe  at **_t_** = 0, **f** **_T,_ f** 2 **_T,_** etc. 

The above analysis shows that signal components of low signal-to-noise ratio  in  the  reference  input,  though  undesirable, do  not render  the  application of adaptive noise cancelling useless." For an illustration of the level of performance attainable in  practical  circumstances  consider the following  example. Fig. **5** shows an adaptive noise cancelling system designed to pass a plane-wave  signal received in the main beam  of **an** antenna array and to discriminate against strong interference in  the  near field or  in  a  minor  lobe of the  array. If one assumes that the signal and interference have overlapping and similar power  spectra  and tha **t** he interference  power  density is 

A transfer  function for  the noise canceller of Fig. **6** may be obtained by analyzing signal propagation from the primary input to the system output." For this purpose the flow diagram  of  Fig. **7,** showing  the  operation of the **LMS** algorithm in detail, is constructed. Note that the procedure for updating 

**"It should be noted that if the reference input contained signal components but no noise components, correlated or uncorrelated, then the signal would be completely cancelled. When the reference input is properly derived, however, this  condition cannot occur.** 

**It is not obvious, from inspection of Fig. 6, that a transfer function for  this propagation path in fact exists. Its existence is shown, however, by  the subsequent analysis.** 

**CANCELLING** **_et 01.:_ ADAPTIVE NOISE** 



<!-- Start of picture text -->
NOISE<br>PRIMARY  CANCELLER<br>INPUT  /  dl<br>SYNCHRONOUS AMPLERS  t 'I 1<br>I I<br>REFERENCE<br>INPUT<br>ADAPTIVE<br>FILTER<br>OUTPUT<br>DELAY<br>LMS<br>ALGORITHM<br>SAMPLING PERIOD  =  T SEC  Xzl  =  CrinIwglT+#l<br>SAMPLING FRER.  CZ  =  9  RADiSEC<br>Fig. 6. Single-frequency adaptive noise canceller.<br><!-- End of picture text -->

##### the discrete  unit  step  function 

forj<O **_u(i)_** =<sup>0,</sup> 1, forj>O. 

Convolving **_2 p ( j_** - 1)  with **_ejxli_** yields the response at  point **_E:_** 



where **_j_** > **_k_** + 1. When the scaled and delayed step  function is multiplied  by **x** **_li,_** the response at point **_F_** is obtained: 

**_y l i_** = **2 w C Z** cos **_(oojT_** + @) cos **_(wokT_** + @) (58) where **_j > k_** + 1. The corresponding response at point **_J ,_** obtained  in  a similar manner,  is 

**_yzi_** = **_2 w C 2_** sin **_(wojT_** + @) sin **_( o o k T_** + @) **_(59)_** 

where **_j_** > **_k_** + 1. Combining (58) and **_(59)_** yields the response at the filter output,  point **_G :_** 





Note  that  (60) **is** a  function  only of **_( j_** - **_k)_** and is thus  a  timeinvariant impulse response,  proportional to  the  input impulse. 

**A** linear transfer  function for  the noise canceller may  now be derived in the following manner. If the  time **_k_** is set  equal to zero, the unit impulse response of the linear timeinvariant signal-flow path  from  point **_C_** to point G is 

**Fi. 7. Flow diagram showing signal propagation in single-frequency** 



This function  can be expressed in  terms of a radian sampling frequency C2 = **_2n/T_ as** 

and 





The first step  in  the analysis is to obtain  the isolated impulse **response** from  the error **_ei,_** point C, to  the  fiter  output, point G, with the feedback loop from point G to point **_B_** broken. Let an impulse of amplitude **_01_** be applied  at  point **_C_** at discrete time **_j_** = **_k;_** that is, 

If the  feedback  loop  from  point **_G_** to point **_B_** is now  closed, the transfer function **_H(z)_** from the primary input, point **_A ,_** to the noise canceller output,  point C, can be obtained from the  feedback  formula: **z2** - **22** cos **_(2nWos2-1)_** + 1 **_H(z)_** = (64) **_z 2_** - **2(1** - **_pCZ)_ z** cos **_( 2 n o o a - ' )_** + 1 - **_2pcZ'_** Equation (64) shows that the singlefrequency noise canceller **has** the properties of a notch filter at the reference frequency **wo.** The zeros of the transfer function are located in the **_2_** plane  at 



where 



The response at point **_D_** is then 



which is the  input impulse scaled in  amplitude  by  the  instantaneous value of **x** **_l j_** at **_j_** = k.  The signal flow path  from  point **_D_** to point **_E_** is that of a digital integrator  with  transfer  func- **tion** **_2p/(z_** - 1)  and  impulse response **_2 p ( j_** - 11, where **_u(j)_** is 

and **are** precisely on the unit circle at angles of **_*2nooS2-'_** rad. The poles are  located  at 



**PROCEEDINGS OF THE IEEE, DECEMBER 1975** 



<!-- Start of picture text -->
4<br>(a)<br>0.707<br>NOTE:  NOTCH  REPEATS<br>ATSAMPLING FREQUENCY<br>(b)<br><!-- End of picture text -->



<!-- Start of picture text -->
FREQUENCY<br>(a)<br>(a)<br>0.707<br>NOTE:  NOTCH  REPEATS<br>ATSAMPLING FREQUENCY  3  0.5<br>0<br>(b)<br>Fig. 8.  Roperties  of transfer function of single-frequency  adaptive<br>noise  canceller. (a) Location  of poles and zeros.  (b)  Magnitude of<br>transfer function.<br>zyxwvut '0 "0  1  i:<br>zyxwvutsrq FREQUENCY  zyx<br>The poles are inside the u@t circle at a radial distance (1  -  (b)<br>2pC2)'IZ, approximately  equal  to  1  -  PC',  from the  origin  Fig. 9. Results of single-frequency  adaptive  noise cancelling  experi-<br>ments. (a)  primary input composed of cosine wave at 512 discrete<br>and at angles  of<br>frequencies.  (b)  primary input composed of  uncmelated samples of<br>white noise.<br><!-- End of picture text -->

**_)-'I2_** cos (2nwo~2-' 11. 

For slow adaptation  (that is, small  values  of **_PC')_** these angles superior to  that of a fixed digital or analog filter because the depend on  the factor adaptive process maintains the null exactly at the reference 1 - /icz = (1 - 2 p ~ 2 + **_p2_ c4** lI2 frequency. Fig. 9 shows the results of two experiments performed to (1 - 2pC2)'12 1 - 2pc2 ) demonstrate the characteristics of the adaptive notch filter. E (1 - **p2c4** + . . . )1/2 In the first the primary input was a cosine  wave  of unit power stepped at 5 12 discrete frequencies. The reference input was - " I - - **_;p2_** c **4** +... (67) a cosine wave with a frequency **_wo_** of n/2T rad/s. The value which differs only slightly from a value of one. The result is of **C** was 1, and the value  of **_p_** was 1.25 X The frethat, in practical instances, the angles of the poles are almost quency  resolution of the fast Fourier  transform was **5** 12 bins. identical to those of of the zeros. The  output power at each frequency is shown in Fig. 9(a). As The location **of** the poles and zeros and the magnitude of the primary frequency approaches the reference frequency, the transfer function in terms,of  frequency are shown in significant cancellation occurs. The weights do not converge Fig. 8. Since the zeros lie on  the  unit circle, the  depth of the of the the to stable values but "tumble" at the difference frequency," notch in the  transfer  function is is infinite at  the frequency **_w_** = and the adaptive filter behaves like a modulator, converting **_wo._** The sharpness of of the  notch is determined by  the closeness is determined by  the closeness determined by  the closeness the reference frequency into the primary frequency. The of the poles to  the zeros. Corresponding poles and zeros are theoretical notch width between half-power points, 1.59 X separated by a distance approximately equal to **_pC2._** The arc **lo-'** **_wo,_** compares closely with the measured notch width of 1.62 X 1 **O-'** **_oo._** 

which differs only slightly from a value of one. The result is that, in practical instances, the angles of the poles are almost identical to those of of the zeros. 

The location **of** the poles and zeros and the magnitude of the primary frequency approaches the reference frequency, the transfer function in terms,of  frequency are shown in significant cancellation occurs. The weights do not converge Fig. 8. Since the zeros lie on  the  unit circle, the  depth of the of the the to stable values but "tumble" at the difference frequency," notch in the  transfer  function is is infinite at  the frequency **_w_** = and the adaptive filter behaves like a modulator, converting **_wo._** The sharpness of of the  notch is determined by  the closeness is determined by  the closeness determined by  the closeness the reference frequency into the primary frequency. The of the poles to  the zeros. Corresponding poles and zeros are theoretical notch width between half-power points, 1.59 X separated by a distance approximately equal to **_pC2._** The arc **lo-'** **_wo,_** compares closely with the measured notch width length along the  unit circle (centered at  the  position of a zero) of 1.62 X 1 **O-'** **_oo._** spanning the distance between half-power points is approxiIn the second experiment, the primary input was composed mately 2pC2. This length  corresponds to a notch bandwidth of of uncorrelated samples of white noise of unit power. The reference input and the processing parameters were the same **BW** = **_pc2 !22/n._** (68) as **_in_** the  first experiment. An ensemble average of 4096 The **_Q_** of the  notch is determined by  the  ratio **_zyxwvuts_** of the  center power spectra at the noise canceller output is shown in Fig. frequency to  the bandwidth: 9(b). An infinite null was not obtained in this experiment because of the  finite  frequency resolution of the  spectral analysis  algorithm. 

The single-frequency noise canceller is, therefore, equivalent to a stable notch fiiter when the reference input is a pure cosine wave. The depth of the null achievable is generally 

**''When the primary and reference frequencies are held at a constant difference, the weights develop a sinusoidal steady state at the difference frequency. In other words, they converge on a dynamic rather than  a  static solution. This is an  unusual  form of adaptive  behavior.** 

In these  experiments the filtering of a reference cosine wave of a given frequency caused cancellation of primary input components at adjacent frequencies. This result indicates that, under some circumstances, primary input components may  be partially cancelled and distorted even though  the reference input is uncorrelated with them.  In practice this kind of cancellation is of concern only when the adaptive process is rapid; that is, when it is effected with large values of **_p ._** When the adaptive process is slow, the weights  converge to values that are nearly stable, and though signal cancellation as described in this section occurs it is generally not significant. 



<!-- Start of picture text -->
ADAPTIVE NOISE CANCELLER<br>____________________--<br>PRIMARY INPUT<br>PREAMPLIFIER<br><!-- End of picture text -->

Additional experiments have recently been conducted with reference inputs  containing more than  one sinusoid. The formation of multiple  notches  has been achieved by using an **Fig. 10. Cancelling 60-Hz interference in electrocardiography.** adaptive filter with multiple weights (typically an adaptive transversal filter). Two weights are required for each sinusoid The single-weight noise canceller acting as a high-pass filter to achieve the necessary filter **_gain_** and phase. Uncorrelated is capable of  removing not only a constant bias but also  slowly broad-band noise superposed **on** the reference input creates varying drift in the primary input. Moreover, though it is not a need for additional weights. A full analysis **_zyxwvuts_** of the multiple demonstrated in this  paper,  experience  has  shown  that bias or **zyxwvuts** notch problem can be found  in [ **_2_** 1 **1 .** drift removal can be accomplished simultaneously with cancellation of periodic or  stochastic interference. **VII. THE ADAPTIVE NOISE** zyxwvutsr **CANCELLER AS A** 

##### **VIII. APPLICATIONS** 

##### **HIGH-PASS FILTER** 

The principles of adaptive noise  cancelling, including a description of the concept and theoretical analyses of performance with various kinds of signal and noise, have been presented in the preceding pages. This section describes a variety of practical applications of the technique. These applications include the cancelling of several kinds of interference in electrocardiography, of noise in speech **signals,** of antenna sidelobe interference, and of periodic or broad-band interference for which there is no external reference source. Experimental results are presented that demonstrate the performance of adaptive noise  cancelling in  these  applications  and that show  its  potential value  whenever suitable inputs are available. 

The use of a bias weight in an  adaptive filter to cancel lowfrequency  drift in  the primary input is a special  case  of notch filtering with the notch at zero frequency. The. method of incorporating  the bias  weight is shown in Appendix **A.** Because there is no need to  match  the phase of the signal, only one weight is needed. The reference input is set to a constant value of one. 

The transfer function from the primary input to the noise canceller output is derived **as** follows. Applying equations (A.3) and  (A. 15) of Appendix A yields 



###### **_A . Cancelling 60-Hz Interference in Electrocardiography_** 

or 

**_Yj+_ 1** = **_Y j_** + **_2c~(dj_** - **_Yj)_** In a recent paper [ **_221,_** the  authors  point  out  that a major problem in the recording of electrocardiograms (ECG‘s) is = ( l - **_2C()Yj+2pdj. (72)_** “the appearance of unwanted 6GHz interference in the output.’’ They analyze the various  causes  of such power-line **_2_** transform of **_(72)_** yields the  steady-state  solution: interference, including magnetic induction, displacement currents in leads or in the body of the patient, and equipment **_Y ( z )_** = **_2 -_** (1 **_*’_** - **_2p) D(z)._** (73) interconnections and imperfections. They also describe a number of techniques that are useful for minimizing it and is then obtained by substituting **_E(z)_** = that can be effected in the recording process itself, such as in (73): proper grounding and ,the use of twisted pairs. Another method capable of reducing 6GHz ECG interference is adap _D ( z )_ - _zyxwvutsrqp_ **_E(z)_** = **_2 p D ( z )_** (74) tive noise cancelling, which _can_ be used separately or in con- **_z -_** (1 - **_2p)_** junction with more  conventional approaches. Fig. 10 shows the application of adaptive noise cancelling in electrocardiography. The primary input is taken from the **_E ( z )_** _z -_ 1 ECG preamplifier; the 6GHz reference input is taken from **_H(z)_** = **_D ( z ) z -_** - = **(1** - **_2p)_** a **wall** outlet.  The adaptive filter contains  two variable  weights, _zyxwvutsrqp_ one applied to the reference input directly and the other to Equation  (75) shows that  the bias-weight filter is a high-pass is a high-pass a high-pass a version of it shifted in phase by **_90’._** The two weighted circle at zero frequency and a versions of the reference are summed to form the filter’s **_2p_** to the  left of the  left of of the zero. output, which is subtracted  from  the primary input. Selected to a single-frequency notch filter, a single-frequency notch filter, combinations of the **values** of the weights allow the  reference **_wo_** = 0 and and **_C_** = 1. The waveform to be changed in magnitude and phase in  any way of the  notch is at the  notch is at is at at **_f l l n_** radls. required for cancellation. The two variable weights, or two 

The  transfer  function is then obtained by substituting **_E(z)_** = 

which reduces to 

Equation  (75) shows that  the bias-weight filter is a high-pass is a high-pass a high-pass filter with a zero on the unit circle at zero frequency and a pole on  the real axis at a distance **_2p_** to the  left of the  left of of the zero. Note that  this corresponds to a single-frequency notch filter, a single-frequency notch filter, described by  (64),  for  the case where **_wo_** = 0 and and **_C_** = 1. The half-power frequency of the  notch is at the  notch is at is at at **_f l l n_** radls. 

**1702** 

ADAPTATION ADAPTATION **SINOATRIAL NODES Fig. 12. Deriving  and  processing ECG signals of a  heart-transplant patient.** because the severed **vagus** nerve cannot be surgically r e **( 4** attached, generates a spontaneous pulse that causes the new **Fe. 1 1 . Result of electrocardiographic zyxwvutnoise cancelling  experiment.** heart to beat  at  a  separate self-pacing rate. **(a)** **_Nary_ input.** (b) **Reference input. (c) Noise canceller output.** It is of interest to cardiac  transplant research, and to cardiac **_zyxwvutsrqponm_** zyxwvutresearch in general, to be able to determine  the firing rate of “degrees of freedom,” are required to cancel the single pure the old heart  and,  indeed, to be able to see the waveforms of sinusoid. its electrical output. These waveforms, which cannot be **A** typical result of a  group of experiments  performed with a obtained by ordinary electrocardiographic means because of real-time computer system is shown in **Fig.** 1 1. Sample size interference from the beating of the new heart, are readily was 10  bits  and sampling rate 1000 Hz.  Fig. ll(a) shows obtained with adaptive noise cancelling. 

“degrees of freedom,” are required to cancel the single pure sinusoid. 

**A** typical result of a  group of experiments  performed with a real-time computer system is shown in **Fig.** 1 1. Sample size was 10  bits  and sampling rate 1000 Hz.  Fig. ll(a) shows the  primary  input, an electrocardiographic waveform with an excessive amount of **60-Hz** interference,  and Fig. 1 l(b) shows the reference input from the wall outlet. **Fig.** 1 l(c) is the noise canceller output. Note the absence of interference and the clarity of detail  once the adaptive process has converged. 

Fig. 12 shows the  method of applying adaptive noise cancelling  in heart-transplant  electrocardiography.  The  reference input is provided by a pair of ordinary chest leads. These leads receive a signal that comes essentially from the new heart, the source of interference. The primary input is prcvided by a catheter consisting of a small coaxial cable threaded  through  the  left  brachial vein and the vena cava to a position in the atrium of the old heart. The tip of the catheter, a few millimeters long, is an exposed portion of the center conductor that acts **as** an antenna and is capable of receiving cardiac electrical signals. When it is in the most favorable position, the .desired signal from the old heart and the interference from the new heart are received in about equal  proportion. 

###### **_B. Cancelling the  Donor ECG  in  Heart-Transplonl Electroaardiography_** 

The  electrical  depolarization of the ventricles of the  human heart is triggered by  a  group of specialized muscle  cells known **as** the atrioventricular **(AV)** node. Though capable of inde pendent, asynchronous operation, this node is normally controlled  by a similar complex,  the sinoatrial **(SA)** node, whose depolarization initiates an electrical impulse transmitted by conduction through the atrial heart muscle to  the **AV** node. The **SA** node **is** connected  through  the vagus and  sympathetic nerves to the central nervous system, which by controlling the rate of depolarization  controls  the  frequency of the heartbeat  [231,  [241. 

Fig. 13 shows typical reference and primary inputs and the corresponding noise canceller output.  The  reference  input contains  the  strong **QRS** waves that, in a  normal  electrocardie gram, indicate the firing of the ventricles. The primary input contains pulses that are synchronous with the **QRS** waves of the  reference  input  and  indicate  the  beating of the new heart. The other waves seen in this input are due to the old heart, which is beating at a separate rate. When the  reference  input is adaptively filtered and subtracted from the primary input, one obtains the waveform shown in Fig. 13(c), which is that of the old hear **t** ogether with very  weak residual pulses originating in the new heart.  Note that  the pulses of the  two hearts are easily separated, even when they  occur  at  the same instant. Note also that the electrical waveform of the new heart is steady  and precise, while that of the old heart varies significantly from  beat to beat. 

The cardiac transplantation technique developed by Shumway of the Stanford University Medical Center involves the suturing of the “new” or donor heart to a portion of the atrium of the patient’s “old” heart [25]. Scar tissue forms at the suture line and electrically isolates the small remnant of the old heart,  containing  only  the **SA** node,  from  the  new heart,  containing  both **SA** and **AV** nodes. The **SA** node of the old heart remains connected to the **vagus** and sympathetic nerves, and the old heart  continues to beat  at  a  rate  controlled by the central nervous system. The **SA** node of the new heart, which is not connected to the central nervous system 

**1703** 



<!-- Start of picture text -->
( 4<br><!-- End of picture text -->

Fig. **13.** ECG waveforms of heart-transplant patient. (a) Reference input **(new** heart). (b) **_Rimary_** input (new and old heart). (c) Noise canceller output (old heart). 

For this experiment the noise canceller was implemented in software with an adaptive transversal filter containing **48** 500 **Hz.** 

##### **_C. Cancelling  the  Maternal  ECG in Fetal  Electrocardiography_** 

Abdominal  electrocardiograms  make it possible to determine fetal heart rate and to detect multiple fetuses and are often used during labor and delivery [26]-[28]. Background noise due to muscle activity and fetal motion, however, often has an  amplitude  equal to or greater than  that of the feta1 heartbeat [ 291 -[ 3  1 ]. A still more  serious  problem is the mother's heartbeat, which has an amplitude two to ten times greater than that of the fetal heartbeat and often interferes with its recording  [321. 

In the spring of 1972, a group of experiments was  performed to demonstrate the usefulness of adaptive noise cancelling  in fetal  electrocardiography.  The  objective was to derive as clear a  fetal ECG as possible, so that  not  only could the heart rate be observed but **also** the actual waveform of the electrical output. The  work was performed  by MarieFrance Ravat, Dominique Biard, Denys Caraux, and Michel Cotton,  at  the time students  at  Stanford  Uni~ersity.'~ Four  ordinary  chest  leads were used to record the mother's heartbeat and provide multiple reference inputs to the _can-_ celler.14 A single abdomina **l** ead was  used to record the combined  maternal  and  fetal  heartbeats that served as the primary input. Fig. 14 shows the cardiac electric field vectors of mother and fetus  and  the positions in which the leads were placed.  Each lead terminated in a pair  of electrodes. The chest and abdominal inputs were prefiltered, digitized, and recorded on tape. A multichannel adaptive noise canceller, 

**13A** similar attempt to cancel the maternal heartbeat had previously been made by Walden and Bimbaum [ **331** without  the use of  an  adap tive processor. Some  reduction **of** the maternal  interference **was** achieved by  the careful  placement of leads  and adjustment  of  amplifer gain. It appears that substantially better results **can** be obtained with adaptive processing. 

"More than  one reference input **was used** to make the interference filtering task easier. The number of reference inputs required essentially to eliminate the maternal ECG is **still** uader investigation. 



<!-- Start of picture text -->
n  n<br>CHEST<br>MOTHER'S<br>LEADS<br>CARDIAC<br>VECTOR<br>NEUTRAL<br>ELECTRODE<br>FETAL<br>CARDIAC<br>VECTOR<br>ABDOMINAL<br>LEAD<br>PLACEMENTS<br>(a)  (b)<br>Fig.  14.  Cancelling maternal  heartbeat  in fetal electrocardiography.<br>(a) Cardiac electric field vectors of mother  and fetus.  (b)  Placement<br>of leads.<br>ABDOMINAL LEAD<br>CHEST  1<br>LEAD<br>REFERENCE<br>INPUTS<br>i*  4 w  I<br>+<br><!-- End of picture text -->

Wg. **15.** Multiple-reference noise canceller used in fetal ECG experiment. 



<!-- Start of picture text -->
(C)<br><!-- End of picture text -->

Fig. **16.** Result of fetal ECG experiment (bandwidth, **3-35 Hz;** sampling rate, **256 Hz). (a)** Reference input (chest lead). (b) **_Primary_** input (abdominal lead). (c) **Noise** canceller output. 

shown in Fig. **15** and described theoretically in Appendix **C,** was used. Each channel had 32 taps with nonuniform (log periodic)  spacing  and  a total delay of 129 ms. 

Fig. 16 shows  typical  reference  and  primary  inputs  together with the corresponding noise canceller output. The prefilter- 

**1704** 

##### **,FETUS** 

NUMBER **OF** ADAPTATIONS  (HUNDREDS) **Fig. 19. Typical  learning  curve  for  speech noise cancelling experiment.** 

**( 4 Fig. 17. Result of wide-band fetal ECG experiment  (bandwidth, 0.3-75 Hz; sampling rate, 512 Hz). (a) Reference input (chest lead). (b) F'ri-** 

ing bandwidth was **3** to 35 Hz and the sampling rate 256 Hz. The  maternal heartbeat, which dominates the primary input, is almost completely absent in  the noise canceller output.  Note that  the voltage  scale of the noise canceller output, Fig. 16(c), is approximately two times greater than  that of the primary input, Fig. 16(b). 

Fig. 17 shows corresponding results for a prefiltering bandwidth of 0.3 to  75 Hz and a sampling rate of 5 12 Hz. Baseline drift and 60-Hz interference are clearly present in the primary input, obtained from the abdominal lead. The interference is so strong  that  it is almost impossible to detect  the fetal  heartbeat.  The  inputs  obtained  from  the  chest leads contained the maternal  heartbeat  and **a** sufficient 60-Hz component to serve as a reference for both of these interferences. In the noise  canceller output  both interferences have been significantly reduced, and the fetal heartbeat is clearly discernible. Additional experiments are currently being conducted with the aim of further improving the fetal ECG by reducing the background noise caused by muscle activity. In these experiments various  averaging techniques are being investigated together with new adaptive processing methods for signals derived from an  array of abdominal leads. **_D. Cancelling Noise in Speech Signals_** Consider the situation of a pilot communicating by radio from the cockpit of an aircraft where a high level of engine noise is present. The noise contains,  among  other things, strong periodic components, rich in harmonics, that occupy the same frequency band as speech. These components are picked up by the microphone into which the pilot  speaks  and severely interfere with the intelhgibility of the radio transmission. It would be impractical to process the transmission with 

a conventional filter because the frequency and intensity of the noise components vary with engine speed and load and position of the pilot's head. By placing a second microphone at a suitable location  in  the  cockpit, however, a sample of the ambient noise field free of the pilot's speech could be o b tained. This sample could be filtered and  subtracted  from  the transmission, significantly reducing the interference. 

To demonstrate the feasibility of cancelling noise in speech signals a group of experiments simulating the cockpit noise problem in simplified form was conducted. In these experiments, as shown in Fig. 18, a person **_( A )_** spoke  into a microphone **_(B)_** in a room where strong acoustic interference (C) was present. A second microphone **_(D)_** was  placed  in the room away from the speaker. The  output of microphones **_(B)_** and **_(0)_** formed the primary and reference inputs, respectively, of a noise canceller **_(E),_** whose output was monitored by a remote listener **_(F)._** The canceller included an adaptive filter with 16 hybrid analog weights  whose  values  were  digitally controlled by a computer. The  rate of adaptation was approximately **5** kHz. A typical learning curve, showing output power as a function of number of adaptation cycles, is shown in Fig. 19.  Convergence  was complete after  about 5000 adaptations  or  one second of real time. 

In a typical experiment the interference was an audiofre quency triangular wave containing  many  harmonics  that, because of multipath  effects, varied in amplitude, phase, and waveform from  point to point in the room. The periodic nature of the wave made it possible to ignore the difference in time delay caused by  the  different transmission paths to the two sensors. The noise canceller was able to reduce the  output power of this interference, which otherwise made the speech unintelligible, by 20 to 25 dB, rendering the  interference barely perceptible to the  remote listener. No noticeable distortion was introduced into the speech signal. Convergence times were on the order of seconds, and the processor **w a s** readily able to readapt when the  position of the microphones was changed or when the frequency of the interference was varied  over the range 100  to 2000 **Hz.** 



<!-- Start of picture text -->
WIDROW  et  al.:  ADAPTIVE NOISE CANCELLING  1705<br>zyxwvutsrq zyxwvutsr zy<br>I N T E R F E R E N C E<br>( P P W E R  = 100, 100,<br>zyxwvutsrqponmlk<br>SIGNAL  Boo  -90  ADAPTATIONS<br>LOOK  .  I  *  (POWER  =  1i  @<br><!-- End of picture text -->



<!-- Start of picture text -->
I N T E R F E R E N C E<br>( P P W E R  = 100, 100,<br>SIGNAL  Boo  -90  ADAPTATIONS<br>LOOK  .  I  *  (POWER  =  1i  @<br>*DIRECTION<br>7<br>12  0<br>bo  :  zyxwvutsrqpon<br>Fig. 20.  Array configuration  for  adaptive  sidelobe cancelling ex-<br>periment.<br>zyxwvutsrqp<br><!-- End of picture text -->

###### **_E. Cancelling  Antenna  Sidelobe  Interference_** 

Strong unwanted signals incident on the sidelobes of an antenna array can severely interfere with the reception of weaker signals in the main  beam. The conventional method of reducing such  interference, adaptive beamforming [ 61, [ 181, [ 191,  [34]-[37], is often complicated and expensive to implement. When the number of spatially discrete interference sources is small, adaptive noise cancelling can provide a simpler and less expensive method of dealing with this problem. 

To demonstrate the level of sidelobe reduction achievable with adaptive noise cancelling, a typical  interference cancelling problem was simulated on  the computer. As shown in Fig 20, an array consisting of a circular pattern of 16 equally spaced omnidirectional  elements was chosen. The  outputs of the elements were delayed and  summed to form a main beam steered **(a)** (b) at a relative  angle  of **0’.** A simulated “white” signal consisting **Fig. 21. Results of adaptive sidelobe cancelling experiment. (a) Single** of uncorrelated samples of unit  power was assumed to be inci- **frequency (0.5 relative to folding frequency). (b) Average of eight** dent on this beam. Simulated interference  with  the same **frequencies** **_(0.25_ to 0.75 relative to folding  frequency).** bandwidth and with a power of 100 was incident on  the main PERIODIC beam at a relative angle of 58’. The array was connected to INTERFERENCE an adaptive noise canceller in the manner shown in Fig. **5.** The output of the beamformer served as the canceller’s primary input, and the output of element 4 was arbitrarily chosen as the reference input.  The canceller included an  adap tive filter with 14 weights; the  adaptation constant in the **LMS** algorithm was set at **_p_** = 7 X 1 **0-6,** I L------------J Fig. 21 shows two series of computed directivity patterns, ADAPTIVE NOISE **_zyxwvutsr_** CANCELLER one representing a single frequency of the sampling frequency  and the  other an average of eight frequencies of from **Fig. 22. Cancelling periodic interference without an external reference source.** to **d** the sampling frequency. These patterns indicate the evolution of the main beam and sidelobes **as** observed by **_F. Cancelling Periodic  Interference  without  an  External_** stopping the adaptive process after the specified number of **_Reference  Source_** iterations.  Note  the deep nulls that develop in the  direction of the interference. At the start of adaptation all weights were There are a number of circumstances where **a** broad-band signal is corrupted by periodic interference and no external set at  zero, providing a conventional 16-element beam pattern. reference input free of the **signal** is available. Examples The signal-to-noise ratio at the system output, averaged include the playback of speech or music in the presence of over the eight frequencies, was found  after convergence to  be tape hum or turntable rumble. It might seem that adaptive +20 dB. The signal-to-noise ratio at the single array element noise cancelling could not be applied to reduce or eliminate was -20 dB. This result bears out  the  expectation arising from **(37)** that  the signal-to-noise ratio  at  the system output would this kind of interference. If, however, a fixed delay **A** is inbe the reciprocal of the ratio at the reference input, which serted in a reference input drawn directly from the primary is  derived from a single element. input, as shown in Fig. 22, the periodic interference can in 

There are a number of circumstances where **a** broad-band signal is corrupted by periodic interference and no external reference input free of the **signal** is available. Examples include the playback of speech or music in the presence of tape hum or turntable rumble. It might seem that adaptive noise cancelling could not be applied to reduce or eliminate this kind of interference. If, however, a fixed delay **A** is inserted in a reference input drawn directly from the primary input, as shown in Fig. 22, the periodic interference can in many cases be readily cancelled.” The delay chosen must be of sufficient length to cause the broad-band signal components in the reference input to become decorrelated from those in 

**A** small amount of  signal cancellation occurred, as evidenced by  the changes in sensitivity of the main beam in  the steering direction. These changes  were not unexpected, since the mainlobe pattern was not constrained by the adaptive process. **A** method of **LMS** adaptation with constraints that could have been used to prevent this loss of sensitivity has been developed 

**I s The  delay A may be inserted  in the primary instead of  the reference input if its total length is greater than the total delay of the adaptive filter. Othenvise, the filter** wi **l converge to match it and cancel both signal  and  interference.** 

**1706** 



<!-- Start of picture text -->
PROCEEDINGS OF THE IEEE, DECEMBER 1975<br>BROADBAND<br>t  I  zyxwvuts<br>PERlbDlC<br>SIGNAL<br>I  I<br>!--_--------<br>ADAPTIVE NOISE<br>CANCELLER<br>c  I<br>Fig. 24. The  adaptive noise canceller as a  self-tuning filter. as a  self-tuning filter. a  self-tuning filter.<br>t<br>-  SELF-TUNING FILTER OUTPUT<br>NOISE  CANCELLER  OUTPUT  .__. -- - . -- - -- -  . _ . .  PERIODIC  INPUT<br>- _ _ _ _ _ _  BROADBAND INPUT<br>9 2<br>t  I<br>zyxwvutsrqponmlk<br>- 0  4 t " ' 1 " ' 1 l 1 ' f t 1 1<br>25  1  50  75  0<br>TIME  INDEX<br>-40  25  TIME  INDEX  50  76  1 0 0  Fig. 25. Result of self-tuning  filter experiment. 25. Result of self-tuning  filter experiment.<br>zyxwvutsrqponmlk<br>(b)  zyxwvutsrqponmlk<br><!-- End of picture text -->



<!-- Start of picture text -->
PERlbDlC<br>SIGNAL<br>I  I<br>!--_--------<br>ADAPTIVE NOISE<br>CANCELLER<br>Fig. 24. The  adaptive noise canceller as a  self-tuning filter. as a  self-tuning filter. a  self-tuning filter.<br>t<br>-  SELF-TUNING FILTER OUTPUT<br>.__. -- - . -- - -- -  . _ . .  PERIODIC  INPUT<br>- 0  4 t " ' 1 " ' 1 l 1 ' f t 1 1<br>25  1  50  75  0<br>TIME  INDEX<br>Fig. 25. Result of self-tuning  filter experiment. 25. Result of self-tuning  filter experiment.<br>$ t I<br>84  256 1 2 8  192<br>O.0  FREOUENCY (REL. SAMPLING TO  FREQUENCY1  L I I , l l I l , / i l l l'<br>(b)<br><!-- End of picture text -->

**Fig. 23. Result of periodic interference cancelling experiment. (a) Input signal (correlated Gaussian noise and sine wave). (b) Noise canceller output (correlated Gaussian noise).** 

the primary input. The interference components, because of their  periodic  nature, will remain  correlated  with  each  other. Fig. 23 presents the results of a computer simulation performed to demonstrate  the cancelling  of periodic  interference without an external reference. **_Fig._** 23(a) shows the prima$ input to the canceller. This input is composed of colored Gaussian noise representing the signal and a sine wave representing the interference. **_Fig._** 23(b) shows the noise canceller's output. Since the problem was simulated, the exact nature of the broad-band input **was known** and is plotted  together  with the  output. Note **ti&'** %lose correspondence in form  and registration. The correspondence is not perfect only because the filter was  of finite  length and  had a  finite  rate of adaptation. 

###### **_G. Adaptive  Self-Tuning  Filter_** 

The previous experiment _can_ also be used to demonstrate another  important application of the adaptive noise canceller. In many instances where **an** input **signal** consisting of mixed periodic  and  broad-band  components is available, the periodic rather  than  the  broad-band  components **are** of interest. If the system output of the noise canceller of **_Fig._** 22 **is** taken  from the adaptive filter, the result is an adaptive self-tuning filter capable  of extracting  a  periodic signal from broad-band  noise. 

**Fig. 26. Adaptive filter characteristics in self-tuning filter experiment. (a) Impulse response of adaptive filter after convergence.** (b) **Magnitude of transfer function of adaptive  filter  after  convergence.** 

**_?ig._** 24 shows the adaptive noise canceller **as** a self-tuning filter. The output of this system was simulated **on** the computer with the input of sine wave and correlated Gaussian noise  used in the previous experiment  and  shown in **_Fig_** 23(a). The resulting approximation of the  input sine wave is shown in Fig. 25 together  with the actual input sine wave. Note once again the close agreement in form and registration. The error is a small-amplitude stochastic process. 

shown in **_Fig._** 26(a), is somewhat different from but bears **a** close  resemblance to a sine wave.  If the broad-band input component had been white noise, the optimal estimator would have been a matched filter, and the impulse response would have been sinusoidal. The transfer function, shown in **_Fig._** 26(b), **is** the digital Fourier transform of the impulse response. Its magnitude at 

Fig. 26 shows the impulse  response and  transfer  function of the adaDtive filter after convergence. The impulse response, 

the frequency of the interference is nearly one, the value required for  perfect cancellation. The phase shift at this frequency is not  zero  but when added to the phase shift caused by  the delay **A** forms an  integral'multiple of **360'.** Similar experiments have been conducted with sums of sinusoidal signals in broad-band stochastic  interference.  In these experiments the adaptive fiiter developed sharp resonance peaks at the frequencies of all the spectral line components of the periodic portion of the primary input. The system thus shows considerable promise **as** an automatic signal  seeker. 

Further experiments have shown the ability of the adaptive self-tuning filter to be employed as a line enhancer for the detection of extremely low-level sine waves in noise.  An introductory treatment of this application, which promises to  be of  great importance, is provided in Appendix D. 



<!-- Start of picture text -->
dj<br>Fig. 27.  The  adaptive  linear  combiner.<br><!-- End of picture text -->

taneously on **all** input lines at discrete times indexed by the subscript **_j ._** The  component **xoi** is a constant, normally set to the value +I, used only in cases where biases exist among the inputs  (A.l)  or  in  the desired response (defined below). The weighting coefficients or multiplying factors **_W O ,_** w1, * * , **_wn_** are  adjustable, as symbolized in Fig. 27  by circles with arrows 

##### **IX. CONCLUSION** 

Adaptive noise cancelling is a method of optimal filtering that can be applied whenever a suitable 'reference input is available. The principal advantages of the  method are its adaptive capability, its low output noise, and its low signal distortion. The adaptive capability allows the processing of inputs whose properties  are  unknown  and  in  some cases nonstationary.  It leads to a stable system that  automatically  turns itself off when no improvement in signal-to-noise ratio can be achieved. Output noise and signal distortion are generally lower than can be achieved with conventional optimal filter configurations. 



<!-- Start of picture text -->
W =  (A.2)<br><!-- End of picture text -->

The experimental data presented in this paper demonstrate the ability of adaptive noise  cancelling greatly to reduce additive periodic or stationary random interference in both periodic and random signals. In each instance cancelling was accomplished with little signal distortion even though  the frequencies of the signal and the interference overlapped. The experiments described indicate  the wide range of applications in which adaptive noise  cancelling has potential usefulness. 

where **_wo_ is** the bias weight. 

The  output **_yi_** is equal to the  inner  product of **_Xi_** and **_W:_** 



The error is defined as the difference between the desired response **_di_** (an externally supplied input sometimes called the "training **signal")** and  the  actual response **_yi:_** = **_dl_** - **_XTW_** = **_dl_** - **_WTXi._** (A.4) In most applications some ingenuity is required to obtain a suitable input for **_di._** After all, if the actual desired response were **known,** why would one need an adaptive processor? In noise cancelling systems, however, **_di_ is** simply the primary input.'' 

##### **APPENDIX A** 

##### **THE** LhiS **ADAFTIVE FILTER** 

This Appendix provides a brief description of the **LMS** adaptive filter, the basic element of the adaptive noise cancelling systems described in this paper. For a full description the reader should consult the extensive literature on  the subject, including the references cited below. 

###### **_B. The LMS Adaptive Algorithm_** 

###### **_A.  Adaptive Linear Combiner_** 

It is the purpose of the adaptive algorithm designated in Fig. 27 to adjust the weights of the adaptive **linear** combiner to minimize mean-square error. A general expression for meansquare  error as a function of the weight  values, assuming that the  input signals ind the desired response are statistically stationary and that the weights are fixed, can be derived in the following manner. Expanding (A.4) one  obtains 

The principal component of most adaptive systems is the adaptive linear combiner, shown in Fig. 27.16 The combiner weights and sums a set of input signals to form an output signal. The  input signal vector **_Xi_** is defined as 



<!-- Start of picture text -->
xi  fi  (A.  1)<br>X n i<br>{f<br><!-- End of picture text -->



##### Taking the expected value of both sides yields 

**_E [ € ; ] = E [ d f ]_** - **_2E[djXT] W_** + **_WTEIXFfl W._** (A.6) 

The input **_signal_** components **are** assumed to appear simul-  Defining 

the vector **_P_ as** the cross correlation between the 

**'*This  component is linear only  when  the weighting coefficients are fixed. Adaptive systems, like all systems whose characterbtics change with  the characteristics of their inputs, are by their very nature nonlinear.** 

**"The actual desired response is the primary noise** **_n o ,_ which is not available apart from the primary input s** + **_no._ The converged weight vector solution is easily shown to be the same when either** **_no_ or s +** **_no_ serves as the desired  response.** 

**PROCEEDINGS OF THE IEEE, DECEMBER** 

ments of correlation functions, nor does it involve matrix inversion. Accuracy is limited by statistical sample size, since the weight values found are based on real-time measurements of input signals. The **LMS** algorithm **is** an implementation of the  method of steepest  descent. According to this method,  the  “next” **zyx** weight vector Wj+, is equal **to** the “present” weight vector Wj plus  a change proportional  to  the negative gradient: 

Wj+l = wj - **pvj.** (A.12) The parameter **_p_** is the  factor  that controls  stability  and  rate of convergence. Each iteration occupies a unit time period. The true gradient  at  the jth iteration  is  represented  by **vi.** The **LMS** algorithm estimates **an** instantaneous gradient in a  crude  but  efficient  manner  by assuming that _€7,_ the square of a single error sample, is an estimate of the mean-square error  and by differentiating **_E;_** with  respect to W. The  relationships between true and estimated gradients are given by the following  expressions: 

[a€; I I **_zyxwvuts_** (A. **zyxwv** [- The estimated gradient components **are** related to  the partial derivatives of the  instantaneous  error  with  respect to  the weight components, which can be obtained  by  differentiating (A.5). Thus the expression for the gradient estimate can be simplified to **A vj** = - (A. 2fjXj. 14) Using this estimate in place of the true gradient in (A.12) yields the Widrow-Hoff **LMS** algorithm: wj+1 = **wj** + 2PEjXj. (A. 15) This algorithm is simple and generally easy to implement. Although it it makes use  of gradients of mean-square error  functions, it does not require  squaring, averaging, or  differentiation. It **has** been **shown** [ 181, [ 191 that the gradient estimate used in the **LMS** algorithm **is** unbiased  and that  the expected value of the weight vector converges to the Wiener weight vector (A.11) when the input vectors **are** uncorrelated over time  (although  they  could,  of  course,  be  correlated  from input component  to component).”  Starting  with an arbitrary initial weight vector, the algorithm will converge in  the mean and will remain stable as long **as** the parameter **_p_** is greater than 0 but less than the reciprocal of the largest eigenvalue **h,,** of the  matrix R: 



<!-- Start of picture text -->
(A.  13)<br><!-- End of picture text -->



<!-- Start of picture text -->
w =  wj<br><!-- End of picture text -->

This matrix is symmetric, positive definite, or in rare cases positive semidefinite. The mean-square error can thus be expressed as 

> E[E;] = E[df] - 2PTW + WTRW. (A.9) 



Note that  the error is a  quadratic  function of the weights that _can_ be pictured **as** a concave hyperparaboloidal  surface,  a function that never goes negative. Adjusting the weights to minimize the  error involves descending along this  surface  with the objective of getting to the “bottom of the bowl.” Gradient  methods  are  commonly used for  this  purpose. The gradient **_0_** of the error function is obtained by differentiating  (A.9): **V i** 1-1 =-2P + 2Rw. (A.lO) aE[E;l awn 



This algorithm is simple and generally easy to implement. Although it it makes use  of gradients of mean-square error  functions, it does not require  squaring, averaging, or  differentiation. 

The optimal weight vector **_W*,_** generally called the Wiener weight vector, is obtained  by  setting the gradient of the meansquare  error  function to zero: 

l/Amm > **_p>_** 0. (A. **16)** Fig. 28 shows a typical individual learning curve resulting from the use of **_Also_** shown is an ensemble 



This equation is a matrix form of the Wiener-Hopf equation i l l , D l . 

**“Adaptation with correlated input vectors has been analyzed by Senne [38 J and Daniell** [ **39 1 . Extremely h@ correlation and fast adaptation** **_can_** _cause_ **the weight vector to converge in the mean to something different than the Wiener solution. Practical experience has shown, however, that this effect is generally insignnificant. See also** Kim **and  Davisson [40 J** . 

The **LMS** adaptive algorithm [71, [81, [191, [201 isapractical  method  for  finding  close  approximate  solutions to (A.11) in  real time. The  .algorithm  does not require  explicit measure 

**1709** 



<!-- Start of picture text -->
'"I  I<br>r,lNDlVlDUAL  LEARNINGCURVE<br>u<br>ENSEMBLE  AVERAGE  OF<br>48  LEARNING  CURVES<br>zyxwvutsrqpon<br>1W  2W<br>NUMBER  OF  ITERATIONS<br><!-- End of picture text -->

average of 48 learning curves. The ensemble average reveals the underlying exponential nature of the individual learning curve. The  number of natural modes is equal  to  the  number of degrees of freedom (number of weights). The time constant of the pth mode is related to the pth eigenvalue **_Ap_** of the input  correlation  matrix **_P_** and to  the parameter **_p_** by (A. **17)** 

Although the learning curve consists of a sum of exponentials, it can in many cases be approximated by a single exponential whose time constant is given by (A.17) using the average of the eigenvalues of R : 

Accordingly, the time  constant of an  exponential roughly approximating the mean-square error learning curve is 

**r,,** =-- **_(n_** + 1) - (number of  weights) . (A. 19) 4p tr R (4p)(total input power) 

The total  input power is the **_sum_** of the powers incident **_to_** all of the weights. 

Proof of these assertions and further discussion of the characteristics and properties of the **LMS** algorithm are presented in 1191, I201,and 1411. 

##### C. **_The LMS_** Adaptive Filter 

The adaptive linear combiner may be implemented in conjunction with a tapped delay line to form the **LMS** adaptive filter shown in  Fig. 29, where the bias  weight has been omitted for simplicity. Fig. 29(a) shows the details of the filter, including the adaptive process incorporating  the **LMS** algorithm. Because of the structure of the delay line, the input signal 



The components of this vector are delayed versions of the input signal **xi.** Fig. 29(b) is the representation adopted to symbolize the adaptive tapped-delay-line filter. 

**This** kind of  filter permits the adjustment of gain and phase at many frequencies simultaneously and is useful in adaptive broad-band **signal** processing. Simplified design rules, giving 

**Fig. 29. The LMS adaptive  filter,  (a) Block diagram.** (b) **Symbolic representation.** 

the tap spacings and number of taps (weights), are the following: The tap spacing time must be at least as short as the reciprocal of twice the signal bandwidth (in accord with the sampling theorem). The total real-time length of the delay line is determined by the reciprocal of the desired filter frequency resolution. Thus, the number of weights required is generally equal to twice the  ratio of the  total signal bandwidth to the frequency resolution of the filter. It may be possible to reduce the number required in some cases by using nonuniform tap spacing, such as log  periodic. Whether this is done or  not,  the means of adaptation remain the same. 

##### **APPENDIX B** 

**FINITE-LENGTH, CAUSAL 'APPROXIMATION OF THE UNCONSTRAINED WIENER NOISE CANCELLER** 

In the analyses  of Sections IV and V questions of the physical realizability of Wiener filters were not considered. The expressions derived were ideal, based on the assumption of an infinitely long, two-sided (noncausal) tapped delay line. Though such a delay line cannot in reality be implemented, fortunately its performance, as shown in the following paragraphs, can be closely approximated. Typical impulse responses of ideal Wiener filters approach amplitudes of zero exponentially over time. Approximate realizations are **thus** possible with finite-length transversal filters. The more weights used in the transversal filter, the closer its impulse response wi **l** be to  that of the ideal Wiener filter. Increasing the number of weights, however, also slows the adaptive process and increases the cost of implementation. Performance requirements should thus  be carefully considered before a filter is designed for a particular application. 

Noncausal filters, of course, are not physically realizable in real-time systems. In many cases, however, they can  be realized approximately in delayed form, providing **an** acceptable delayed real-time  response. In practical circumstances excellent performance  can be obtained with twesided filter impulse responses even  when they  are  truncated  in time to the left and nght. By delaying the truncated response it can be made causal and physically  realizable. 

Fig. 30 shows **an** adaptive noise cancelling system with a delay **A** inserted in the primary input. This delay causes an equal delay to develop in the unconstrained  optimal  filter 

**1710** 

**PROCEEDINGS OF THE IEEE, DECEMBER 1975** 

mini- 



<!-- Start of picture text -->
INPUT  CANCELLER NOISE  the  time delay of the adaptive filter  produces  the least<br>OUTPUT  mum output noise power.<br>Fig. 31  shows  the  results<br>ADAPTIVE  cancelling experiment with an unconstrained optimal filter<br>REFERENCE  response that was noncausal.<br>INPUT  of a triangular wave and  additive colored noise. The  reference<br>zyxwvutsrqponmlk<br>input consisted of colored noise correlated with the primary<br>Fe.  30.  Adaptive noise canceller with delay in primary input path.  noise.lg The unconstrained<br>causal, finite  time  adaptive  impulse response obtained  without<br>zyxwvutsrq a delay in the primary input  are<br>large difference in these impulse responses indicates that the<br>noise canceller output will be a poor approximation<br>signal.  The  corresponding  Wiener  and<br>responses obtained with a delay of eight time  units (half the<br>WIENER  SOLUTION U N C O N S T R A I N E D  length of the adaptive filter) are shown in<br>solutions are similar, indicating that  performance of the  adag<br>I  tive filter  will  be close<br>outputs with and without delay are  shown<br>Fig. 31(d). The  waveform obtained with the delay<br>close to that<br>that obtained with no delay still contains a<br>S O L U T I O N  noise.<br>APPENDIX  C<br>MULTIPLE-REFERENCE NOISE CANCELLING NOISE CANCELLING CANCELLING<br>When there  is  more than one<br>cancelled and a  number of linearly independent  reference in-<br>puts  containing  mixtures of each can be obtained,  it is usually<br>advantageous to  use  a multiple-reference noise cancelling<br>UNCONSTRAINED<br>WIENER  SOLUTION  tem.  Such  a system may be considered a  generalization of the<br>zyxwvutsrqponm<br>single-reference noise cancellers analyzed in  this  paper.  In the<br>model  shown  in  Fig. 32 32  the  $i<br>sources of either input signal or noise. The  transfer  functions<br>gi(z)  represent the propagation paths from these sources<br>the primary input. The  S&)<br>tion  paths  to  the  reference  inputs and  allow for cross-coupling.<br>This  modei  permits  treatment  not<br>sources  but also of signal components in in<br>and uncorrelated noises in the reference and primary inputs.<br>In other words, it  is<br>noise canceller.<br>The  unconstrained Wiener transfer  function  of the  multiple-<br>reference canceller is the  matrix equivalent of is the  matrix equivalent of the  matrix equivalent of  (1<br>rived in the following manner. The source spectral matrix of<br>I J ~ is defined as is defined as defined as<br>4  b 1 d z )  0<br>& Z $ Z<br>( 4<br>Fa.  31.  Results of noise cancelling experiment with delay in  primary<br>input path. (a)  Optimal solution and adaptive solution found without<br>t h e delay. (b) Optimal solution and adaptive solution found with<br>delay of eight time units. (c) Noise canceller output without delay.<br>(d) Noise canceller output  with  delay.  0<br><!-- End of picture text -->

Fig. 31  shows  the  results of a  computer-simulated noise cancelling experiment with an unconstrained optimal filter response that was noncausal. The primary input consisted of a triangular wave and  additive colored noise. The  reference input consisted of colored noise correlated with the primary noise.lg The unconstrained Wiener impulse response and the causal, finite  time  adaptive  impulse response obtained  without a delay in the primary input **are** plotted in Fig. 31(a). The large difference in these impulse responses indicates that the noise canceller output will be a poor approximation of the **signal.** The  corresponding Wiener  and adaptive impulse responses obtained with a delay of eight time  units (half the length of the adaptive filter) are shown in Fig. 31(b). These solutions are similar, indicating that  performance of the  adag tive filter will be close to optimal. Typical noise canceller outputs with and without delay are **shown** in Fig. 31(c) and Fig. 31(d). The waveform obtained with the delay is very close to that of the original triangular-wave signal, whereas that obtained with no delay still contains a great amount of noise. 

###### **MULTIPLE-REFERENCE NOISE CANCELLING NOISE CANCELLING CANCELLING** 

When there is more than one noise or kterference to be cancelled and a  number of linearly independent  reference inputs  containing  mixtures of each can be obtained,  it is usually advantageous to **use** a multiple-reference noise cancelling sye tem.  Such  a system may be considered a  generalization of the single-reference noise cancellers analyzed in  this  paper.  In the model  shown  in **Fig. 32 32** the **_$i_** represent  mutually  uncorrelated sources of either input signal or noise. The  transfer  functions **gi(z)** represent the propagation paths from these sources **_zyx_** to the primary input. The **S&)** similarly represent the propagation  paths  to  the  reference  inputs and  allow for cross-coupling. This  modei  permits  treatment  not only of multiple noise sources  but also of signal components in in the  reference  inputs and uncorrelated noises in the reference and primary inputs. In other words, it is a general representation of an adaptive noise canceller. 

> The  unconstrained Wiener transfer  function of the  multiplereference canceller is the  matrix equivalent of is the  matrix equivalent of the  matrix equivalent of **(1** 3)  and is d e rived in the following manner. The source spectral matrix of I J ~ is defined as is defined as defined as 

impulse response, which remains otherwise unchanged. In practical, finite-length adaptive transversal filters, on  the  other hand, the optimal impulse response generally changes shape with changes in the value of **A,** which is chosen to c a w the peak of  the impulse response to center along the  delay line. Experience **has shown** that the value of **A** is not critical within  a  certain  optimal  range;  that is, the curve showing minimum mean-square error **as** a function of **A** generally has a very broad minimum **A** value typically equal to about **half** 

**_k_** reference  inputs to the  adaptive 

**"Except for the delay in the primary input, the simulated noise cancelling system was identical with  the  system shown above in Fig. 3. The transfei function** **_X(z)_ was a nonminimum phase, lowpass transversa1 fitter with** two **zeros and no poles** **_[J€(z)_** = Zz-'(l - ***.-I)** * **(1** - **$z)]. The optimal unconstrained adaptive fitter solution, in this** **_case_ gwen by (1 a), is the reciprocal of** **_H(z)._ It has one pole inside and one pole outside the unit ci~cle in the** **_Z_ plane. A stable realization of** @ **_(2)_ must, therefore, be** **_two_ sided.** 



<!-- Start of picture text -->
ERROR  F<br>WEIGHT  FAST  FILTER<br>VALUES  FOURIER  TRANSFER<br>TRANSFORM  -  FUNCTION<br><!-- End of picture text -->

**Fig. 33. The adaptive line enhancer.** 

##### **APPENDIX D ADAPTIVE LINE ENHANCER** 

filters is then 



<!-- Start of picture text -->
. . .<br>1  3,’  (z)<br><!-- End of picture text -->

and **ql(z)** is the transfer function from input **source** **_1_** to reference  input **_i._** 

The cross-spectral vector between the reference inputs and the primary input is given by 

where 

A classical detection problem is that of finding a low-level sine wave in noise. The adaptive self-tuning filter, whose capability of separating  the  periodic  and  stochastic  components of a signal was illustrated  above  (where  these  components were of comparable level), is able to serve as an “adaptive line enhancer”  for the  detection of extremely low-level sine waves in noise. The adaptive line enhancer becomes a competitor of the  fast  Fourier  transform  algorithm **as** a sensitive detector and has capabilities  that may exceed  those of conventional  spectral analyzers when the unknown sine wave has finite bandwidth or is frequency  modulated. 

The method is illustrated in Fig. **33.** The input consists of signal plus noise. The  output is the digital Fourier transform of the filter’s impulse response. Detection is accomplished when a spectral peak is evident above the background noise. The same method,  with  minor  differences,  has  been  proposed by  Griffiths for “maximum  entropy  spectral  estimation” 

**_1421,  [431._** 

It should be noted  that  the filter output signal is also available. **This** signal could be used directly or as an input to a spectral analyzer or phase-lock loop. The method of **_Fig. 33_** could further be used for  the simultaneous detection of multiple sine waves. None of these  possibilities  is considered here. Only the detection of single low-level sine waves in noise is treated. 

###### **_A. Optimal Transfer Function_** 

**_i_** to the 

primary input. 

The Wiener optimal weight vector is then 





If **[S(z)] is** square,  at  those  frequencies for which **[3(z)l is** invertible **_( 5 5 )_** simplifies to 

**{W*(z))= [S(zlTI-’ {SCZ))** **_(C.7)_** 

which is the matrix  equivalent of **(1 7).** 

These  expressions  can be used to derive steady-state Wiener solutions to multiple-source, multiple-reference noise cancel- **ling** problems  more  general than **those** of Sections IV and V. An example of a multiple-reference problem is given in Section VIII. 

Fig. **_34_** shows the ideal impulse response and transfer function of the adaptive line enhancer  for  a given input spectrum. It is assumed that  the  input noise is white,  with a total power of **_vz_** , and that the input signal has a power of **_C 2 / 2_** at frequency **oo.** The  ideal impulse response,  equivalent to the matched  filter  response, is a sampled sinusoid whose frequency is **_wo.zo_** The phase shift of this response at frequency **_wo_** when added to that of the delay is an integral multiple of **_360’._** If the peak value of the transfer  function is **_a ,_** the peak value of the weights is to  a close approximation **_2a/n,_** where **_n_ is** the  number of weights. 

The adaptive process minimizes the mean square of the  error. The  error  power is the sum of three  components,  the  primary input noise power,  the noise power at  the  output of the adap tive filter, and the sinusoidal signal power. Accordingly, the error  power may be expressed **as** 

error  power = **_uZ_** + **_(vz/2)  (2a/n)’ n_** + **_( c 2 / 2 )_ (1** - **_alZ._ (D.I)** 

z o T h i r **assertion is proved analytically for arbitrary input signal-tonoise ratio in J. R. Zeidler  and D. M. Chabries,** **_‘‘An_ analysis of the LMS adaptive fiier used as a spectral line enhancer,”  Naval  Undersea Center, Tech. Note 1476, Feb. 1975.** 

**DECEMBER IEEE. PROCEEDINGS OF THE** 



<!-- Start of picture text -->
R<br>-  2a<br>n<br><!-- End of picture text -->

where **Vi** is the **tIuc** gradient and ni is the zero-mean gradient estimation  noise.  A **t** he minimum point of the quadratic mean-squareerror  surface  the  true  gradient is zero.  The gradient estimate  at  this  point is thus  equal to the  gradient  estimation  noise: **A vi** = **ni** = - **zEixi. (D.4)** If one assumes that  the  input signal vector **_Xi_** is uncorrelated over time:’ then **ni is also** uncorrelated over time. In addition, when the weight vector **_Wi_** is equal to  the  optimal weight vector **_W*,_** Wiener filter  theory shows that  the error _~i_ and  the input vector **_Xi_** are uncorrelated. If one now assumes that **_ei zyxw_** and **_Xi_** are Gaussian, then these terms are statistically independent  and the covariance of **ni is** 

COV **[nil** = **~ [ n ~ n 7 1** = **~E[E;X~X?I** = **4 ~ [ e ; 1** 

* **E[XiX7]** = **4E[e;] R** (D.5) 

where **R is** the input correlation matrix. Since at the minimum point of the mean-squareerror surface **E [ E ~ ]** = **[min,** (D.5) _can_ be expressed as 

cov **[nil** = **4tmin R.** (D.6) 

In the vicinity of the minimum point the covariance of the gradient noise is closely approximated  by **(D.6),** and the gradient noise is statistically  stationary  and  uncorrelated over time. For  the  purpose of the following analysis it  is more convenient to work in “primed coordinates.” The correlation matrix **R** may be expressed in  normal  form as 

**R** = **QAQ-’** (D.7) **(C) Fig. 34. Ideal adaptive filter impulse response and transfer function  of** where **Q is** an orthonormal  modal  matrix, **A** is a  diagonal ma- **trum. adaptive line enhancer for a given $put spectrum. (a) Input spec-** @) **Transfer function magnitude. (c) Impulse response.** trix  of eigenvalues, and **_Q-’_ is** equal to **QT.** The gradient noise in the primed coordinates  is  then zyxwvuts **n;** = **Q-’fli** (D.8) We have used the facts that 1) the output noise power of a digital filter with a white input equals the input power muland the covariance of the  gradient noise is tiplied  by the sum of the  squares of the impulse values **of** the impulse response and **2)** the primary and filter output sinuscov **rn;~** = **~[n;n;~l= E[Q-~R~R;QI** = **Q - ~ E [ R ~ ~ ? I** **_Q_** oidal components combine coherently at the summing junc= **_Q-’_** cov **[nil Q** = **4[,inQ-’ RQ** = **4 f ~ , , A .** tion.  The signal gain from input  to error is (1 - **_a)._** The optimal value of **_a_** that minimizes error power **_a*_** is (D.9) obtained  by  setting  the derivative of (D.l)  to zero: **_zyxw_** It should be noted that  the  components of **nj** are  mutually  uncorrelated  and  proportional to  the respective eigenvalues. _zyxwvuts_ The  effect **of** gradient  noise  on  the weight vector can now be _(9)_ (;) determined as follows. The **LMS** algorithm  with  a noisy gradient estimate can be  expressed  in  accordance  with  (A.12) as 1 + **A** _(9)_ (;) 

**A** wi+l = **_wi_ +p(-vi)** = wi + **p(-vi +nil.** (D.IO) Reexpressing (D.lO) in terms of **_Vi,_** where **_Vi_** is defied **as** **_Wj_** - W*, yields Vj+l = **Vj+p(-2RVj+nj).** (D.11) 

At **high** signal-to-noise ratios, **_a* S_** 1. At low signal-to-noise ratios, **_a*_** < 1. Low signal-to-noise conditions can be dealt with by using a large number of adaptive weights, although 

Projecting into  the primed coordinates  by  premultiplying both sides  by **_Q-’_** yields 

**_B. Noise_** in **_the Weight Vector_** 

The ability to detect peaks in the transfer function due to the  presence **of** sinusoidal **signals** is limited **by** the presence of spurious  peaks caused by noise in the weight vector. One thus needs to know  the  nature  of  weight-vector noise and its effects on  the transfer  function. 

**_v;+_ 1** = **_V i -_** 2pAVi)+ **_pR;_** = **_( I -_** 2pA) **_V;+ pn;._** (D.12) Note  once again that, since the  components of )r; are  mutually uncorrelated and since  (D.12) is diagonalized, the  components of noise in **_Vi_** are  mutually  uncorrelated. 

The gradient estimate _gi_ used by  the **LMS** algorithm, given by  (A. **14),** may be expressed as 

**z’ This common assumption is not strictly correct in this case but greatly simplifies the analysis and yields results that work well in practice.** 

**A** 

### **vi=-2elxi=vji+ni** 

(D.3) 

**NOISE CANCELLING** 

where **Z** is the frequency  index. For a single  value of **_I, Hi(Z)_** is a linear combination of all the weights, each weighted by a phasor of unit magnitude. Since **_Hi(Z)_** is complex, the power of this noise is the sum of its “real” and “imaginary” power and equals the sum of the noise power in the weights themselves. Thus at each frequency **_I ,_** the noise power in **_Hi(l)_** is 

Near the minimum  point of the  error surface, in steady  state after adaptive transients have died out,  the mean of **_Vi_** is zero, and the covariance of the weight-vector  noise may be obtained as follows. Postmultiplying both sides  of (D.  12)  by  their transposes and taking expected values yields 

**_E [_ Vi+l ViT1** ] **_= E [ ( I -_ 2pA)** **_V,!V,!‘(I-_** ~ / J A ) ] **_+p2E[nik,!’] nAmin._** (D.22) **_+pE[niVi‘(I-_** 2pA)I **_+ p E [ ( I -_** 2pA) **_V,!R,!’]._** (D.13) In  spectral analysis, “ensemble averaging” techniques are It has been assumed that  the  input vector **_Xi_** is uncorrelated commonly used. The same approach could be used here, avover time; the gradient noise **_R,_** is accordingly uncorrelated eraging the weights over time before transforming. Although with the weight vector **_Wi,_** and therefore and **_zyxwvuts Vi_** are uncorthe gradient noise is essentially. uncorrelated over j, the weightrelated.  Equation  (D.13) can thus be expressed as vector noise is generally highly correlated over time. Averag- _E [_ **Vi+l** **_Vi:,] = ( I_** - 2pA)  E[ViViT] **_( I -_** 2pA) _zyxwvutsr_ ing with  each adaptive iteratiqn could be done  but is not necessary; averaging the weight vector at intervals corresponding zyxwvutsrq+ p2E[fr,!niT]. (D.14) to about four adaptive time constants (47,,) would assure Furthermore, if **_Vi_** is stationary, the covariance of **_Vi+,_** is noise independence  and would be appropriate  in gathering the equal to the covariance of **_Vi,_** which may be expressed as information contained in the time history of the weights. On this basis, averaging **_N_** weight vectors would produce, at  the **_C O V [ V , ! ] ~ ( I - ~ ~ A ) C O V [ ~ ~ ] ( I - ~ ~ A )_** Zth frequency, a noise power in **_+ ~ ~ C O V [ ~ ~ I . H(Z),_** the averaged transfer function,  with  the following value: (D. 15) 

**_(nlN)_ Amin.** (D.23) This expression for weight-vector noise can be put  in more usable form by relating **_tmin_** to the physical line enhancing process shown in Fig. 33. The noise power at the filter output will always be  negligible compared to the input noise power, since the optimized filter transfer function will be small in magnitude except at the peaks whose value is **_u*._** When signal power is low compared to noise power, which is the case of interest in the present context,  the  error power is essentially equal to  the  input noise power. **Thus** 

Since the noise components of **_V,!_** are mutually uncorrelated, (D. 15) is diagonal. It can thus be rewritten as 

cov **_[ V i ] = ( I -_** 2pA)? cov [V,!] +p2(4tminA) 

**01** 

**_( I -_ PA)** C ~ V **_[ V i ]_ = A m i n .** (D.17) 

When the value of the adaptive constant **_p_** is small (as is consistent with a converged solution near the minimum point of the  error  surface), it is implied that 

**_pA<<I._** (D.18) 



Equation  (D.  17)  thus becomes 

> The noise power in **_H(2)_** at  the Zth frequency is accordingly 



The covariance of **_Vi_** can now be expressed as follows: 

a v _[vi]_ = **_E [ V , . V ~ I_** = **_E[Qv;v,!~Q-~_** 1 

(D.20) 

where the  components of the weight-vector noise are all  of the same variance and are mutually uncorrelated. This derivation of the covariance depends on  the assumptions  made above. It has been found by experience, however, that (D.20) closely approximates the  exact covariance of the weight-vector noise under a considerably wider range of conditions  than these **as-** sumptions imply. A derivation of bounds on the covariance based on fewer assumptions  has been made by Kim and Davisson  [401. 

###### **_C. Noise in the Transfer Function_** 

The filter weights, comprising the impulse response, undergo digital Fourier transformation to yield the transfer function. The noise in each of the weights is uncorrelated over time, uncorrelated from weight to weight, and of variance **_pEmin._** At the jth instant the impulse response has **_n_** samples, **_woi,_ wli,** - - , **_ww,_** * - , **wn-li,** and their transform is 



###### **_D.  Detectability of Sine Waves by  Adaptive  Line Enhancing_** 

Detection of a signal is dependent on identification of its adaptive filter  transfer  function peak (of value **_a * )_ as** distinct from other peaks due to weight-vector  noise. For  this **purpose** one could compare  the value of **_a_** * with the standard deviation of the noise in **_H(Z)._** A still better procedure is to work with signal and noise power by comparing the squares of these quantities.  “Detectability”  for  the adaptive lin **e** nhancer (ALE) is accordingly defined as follows: 



This measure must typically be one  or greater to achieve signal detection. Using (D.2)  and  (D.22),  equation  (D.26) _can_ be  reexpressed as 

The power of the adaptive filter  input is essentially that of the noise, equal to **_v z ._** Since the filter input is essentially white,  the  input  correlation matrix _can_ be well represented by 



All  eigenvalues are  equal to **_v2._** The  trace of **_R_ is** equal to **_n g_** . 

PROCEEDINGS OF THE IEEE, DECEMBER **1975** 

Using (A.19) of Appendix A, one may thus  write 

> This is the time constant of the mean-square error learning curve. Note that  the line enhancer  does not have a bias  weight and that the number of weights is thus n rather than n + 1. Equation (D.27) may now be expressed in more useful form **as** follows: 

It is reasonable to compare the average signal power in the selected spectral bin with the  standard deviation of the noise power fluctuations  that occur in each spectral  bin; that is, with the square root of (D.36). We thus  define  “detectability”  for spectral analysis  as 



The motive for  this  definition is derived from the early work of Woodward [441, Skolnick 1451, Swerling [461, Marcum [ 471 , and  others. 

For **high** signal-to-noise ratios-that is, for (SNR) ( 4 2 ) >> 1- equation (D.30) becomes 

**_F._** Comparison of Adaptive Line Enhancing and Spectral Analysis 

> Fig. 35 illustrates the definitions of the detectability of a sine wave  by adaptive line enhancing and spectral analysis given in (D.30)  and  (D.37). It is  useful to compare Fig. 35(a) with Fig. 35(b). Note that in the former case the measure of detectability is based on  the magnitude of the adaptive filter transfer  function, whereas in the  latter  it is  based on  the digital power spectrum. Since the measure of detectability is different  for  the  two  techniques, in a sense one is comparing “apples and oranges.” Yet both DUE and D D are ratios of signal ~ power to noise power. 



For low signal-to-noise ratios-that is, for (SNR) ( 4 2 ) << 1- equation (D.30) shows that 



Intermediate values must be independently calculated. 

Choice of the number of weights has an influence on the value of DALE for a given input signal-to-noise ratio. Differentiating (D.30) with respect to n and setting the derivative to zero yields the following expression for  the optimal value of n: 

Fig. 36 presents experimental results, obtained by  computer simulation, showing the performance of the adaptive line enhancing and spectral analysis techniques for three values of DALE and D D ~ Visual examination indicates that DALE . and D D do provide a reasonable basis for comparing the per- ~ formance of the  two  techniques. 



Substituting (D.33) into (D.30) then yields the  optimal value” of DALE : 

Equation (D.34) describes the  detectability of a sine wave by the adaptive technique when n is optimized. This equation can  be rewritten as 







a* = 1/2. (D.35) Since weight vectors are taken  for ensemble averaging at 47intervals and N vectors are averaged, 4N7,, represents the E. Detectability of of Sine Waves by Spectral Analysis total  number of input  data samples. Note that  the  time constant 7,s is not expressed in seconds but in number of adapLet the power spectrum of a signal in white Gaussian noise tive iterations, which is equivalent to number of input data **K?.** derived from an L-point digital Fourier transform. The samples. Thus (D.38) can be rewritten as frequency of the signal is assumed to be at the center of a spectral bin. Input signal power is assumed to be C2/2 and D ~ L = E (number of data samples) (SNR/8). (D.39) noise power to be **_v2._** Ai  the signal frequency, the  component of the power spectrum due to the signal will have the value The  detectability  of a sine  wave by  spectral analysis is given **_zyxwvutsrqp_** by (D.37). Since N sample spectra are ensemble-averaged, and C2L2/4. Each spectral bin  will  have an  identical average  noise power of **_v2 L_** . since each requires L data  points,  the  number of data samples For  the signal to be detected its spectral peak must be disrequired is the  product of N and L. Equation  (D.37) _can_ thus be rewritten as tinguishable from noise peaks that are deviations about the **_zyxwvutsr_** mean noise power. The variance of the noise power about  the D D = (number ~ of datasamples) (SNR/[8N] **_‘I2)._** (D.40) mean can be reduced by ensemble averaging; that is, by averaging N power spectra, each derived from L data points. With The  ratio of detectabilities is, therefore, Gaussian  noise the variance of the noise power about  its mean in any  spectral bin can be shown **23** to be (2/N) (average  noise (D.41) power)2, which is equivalent to 

E. Detectability of of Sine Waves by Spectral Analysis 

Accordingly, spectral analysis is advantageous **as** long as the (2/N) (VZLl2. (D.36) number of ensemble members is less than eight. Adaptive line enhancing would be advantageous when the  number of ensem“The exact value of **_n_** is not critical; it may be **as** much **as** **_8_** times ble members required for  spectral analysis is greater than eight. larger or smaller than **_n*_** and **_DALE_** wi **l** remain within approximately For the comparative experiment represented by **Fig.** 36, **_50 l 3_** percent The **variance** of **_DALE._** in the estimate of variance from **_N_** samples **of** a zeroinput signal-to-noise ratio in each case  was 0.01562. The nummean process equals (mean fourth - [mean square **1** **_)IN._** ber of data samples used with  spectral analysis was the same as **zyxwvutsrqpon** 

**_al.:_ ADAPTIVE  NOISE  CANCELLING** 



<!-- Start of picture text -->
POWER  SPECTRAL  MEAN SIGNAL POWER<br>TRANSFER FUNCTION  A  PEAK  POWER  GAIN  DENSITY  D~~~  ’  STANDARD DEVIATION  OF NOISE POWER<br>MAGNITUDE SQUARED  D~~~  AVERAGE POWER GAIN<br>t  t  ,7---C2L2/4  =  MEAN SIGNAL POWER<br>“BEST“ (.‘I2  =  114<br>STANDARD  DEVIATION  =  2  L ( z / N I ~ / ~<br>AVERAGE POWER GAIN  zyxwvutsrqpo=  (n/Nl ir  v2  zyxw<br>(a)  (b)<br>Fig. 35. Defmition  of  detectability  D  of  a sine wave  in noise.  (a) With adaptive line enhancing.  (b) With spectral analysis.<br>zyxwvutsr zyxwvutsrqp<br>’1<br>DALE  -  2<br>W . 0 F DATASAMPLES  -  1.024<br>t 4  ENSEMBLE SIZE  -  4<br>2: Kula O  1  .<br>g t  Z Z  zyxwvutsrqponmlk<br>0<br>FREOUENCY IREL. TO  SAMPLING  FREOUENCYI  I”  FREWENCYlREL.TOSAMPLlNG FREWENCYI  ln<br>1 1<br>’I  1<br>a i  5s  1  DALE NO ENSEMBLE  OF  =  DATA SAMPLES 8  SIZE  =  16  -  4.m<br>551  !<br>ODFT  I<br>No. OF DATA SAMPLES  =  16%<br>ENSEMBLE SIZE  -  118<br>0  FREOUENCY IREL.TOSAMPLlNG FREWENCYI  112  0  FREOUENCY IREL.TOSAMPLlNG FREOUENCYI  ln<br>2;<br>DALE  -  f2  I<br>a:  1  NO. OF DATA SAMPLES  -  18%<br>t s  ENSEMBLE SIZE  -  64<br>ii  v)-  I D n - , -~ ,-,,<br>I-=  % j DDFT  f2<br>B j NO. ENSEMBLE SIZE OF DATA SAMPLES  =  2.019  -  Z82.144<br>0  O I<br>FREOUENCY IREL.  TO SAMPLING FREWENCYI  I n  FREOUENCY TO IREL  SAWLING FREOUENCYI  ’Iz<br>(a)  (b)<br>Fig. 36.  Experimental comparison of  adaptive line enhancing and spectral analysis for three values of  detectability  D;  input signal-to-<br>noise ratio, 0.01562;number of weights and  transform points, 128.  (a) Adaptive line enhancing. (b) Spectral analysis<br>zyxwvutsrqpon<br>the  number used with  adaptive  line  enhancing  when  the value  hancement.  Thus  the detectability  D D of the  ~ signal  is<br>of  DUE  and  D D was  ~ 2 but became  16 times  greater  when  proportional to  L.  Since ensemble averaging  is  incoherent<br>the value of  DALE  and  D D was  ~ 32.  (“postdetection averaging”), however, the detectability  D D ~<br>With adaptive line enhancing one could freely trade  N  for  is  proportional  only  to the square root  of  N.  The adaptive<br>T-.  Their product  is  all  that  is  important. Ensemble av-  process, on  the  other  hand, provides coherent signal  averaging,<br>eraging may not even be required, since  T,  can  be made large  making the detectability  DALE  proportional to  7-.  It  is<br>by making  p  small (although this may  cause  one to go to  equally coherent  in  averaging  the weight vector ensemble,<br>zyxwvutsrqp<br>“double  precision”  arithmetic). With spectral analysis, on  the  making  DALE  proportional  also  to  N.<br>other hand,  ensemble averaging cannot be avoided in most  An analytical  comparison of the  computational  requirements<br>cases.  The size of  L  may  be  limited by cost considerations,  of the  two  techniques has not  yet  been  made,  but  it  appears<br>computer  speed,  or  in  the  case  where the  signal  is an  imperfect  that the adaptive process  will  provide a simpler implementa-<br>or modulated  sine wave by signal bandwidth. Large values of  tion when spectral  analysis involves large values of  L.  The<br>N  are required when input  signal-to-noise ratio  is  low, and  adaptive process has the advantage of being a smooth, steadily<br>values in the  thousands  are  not  uncommon.  is<br><!-- End of picture text -->

An analytical  comparison of the  computational  requirements of the **two** techniques has not  yet  been  made,  but  it  appears that the adaptive process will provide a simpler implementation when spectral analysis involves large values of **_L._** The adaptive process has the advantage of being a smooth, steadily flowing process, whereas spectral analysis is performed with consecutive  time segments of data. The  subject of **signal** detection by  adaptive  filtering is rela- _zyxwvut_ tively new,  and  the analysis presented  here  should be regarded **as** preliminary. The formulas derived have been verified by 

_tral_ methods in **certain cases,** especially those of low **signal-** to-noise ratio, can be stated **as** follows. Averaging within  the digital Fourier transform itself provides coherent signal en- 

PROCEEDINGS OF THE IEEE, DECEMBER 1975 

1716 

simulation and experiment, but the concepts they describe have not been in existence long enough to provide an adequate perspective. It is hoped that  this work can be extended in the future. 

   - [19] B. Widrow, P. Mantey, L. Griffiths;and B. Goode, “Adaptive antenna systems,” **_Proc. IEEE,_** vol. 55, pp. 2143-2159, Dec. 1967. 

   - [ 201 - , “Adaptive filters,” in **_Aspects of Network and System  Theory,_** R. Kalman and N. DeClaris, **Eds.** New York: Holt, Rinehart, and  Winston, 1971,pp. 563-587. 

   - 121  ] J. Glover, “Adaptive noise cancelling of sinusoidal  interferences,” Ph.D. dissertation,  Stanford Univ., Stanford, Calif., May 1975. 

- ACKNOWLEDGMENT [22] J. C. Huhta and J. **_G._** Webster, “60-Hz interference in electrocardiography,” **_EEE Trans. Biomed.  Eng.,_ vol.** BME-20, pp. 91- 

- Many people have contributed  support, assistance, and ideas 101, Mar. 1973. the work described in this paper. The,authors especially [23] W. Adams and P. Moulder, “Anatomy of heart,” in **_Encycl. Britannica,vol._** ll,pp.219-229,1971. 

- wish to acknowledge the contributions of Prof. T. Kailath, [24] G. von Anrep and L. k e y , “Circulation of blood,” in **_Encycl._** Prof. M. Hellman, Dr. H. Garland, J. Treichler, and **M.** Lari- **_Britannica,_** vol. **5 ,** pp. 783-797,  1971. more of Stanford University; Prof. L. Griffiths of of the Uni- **zyxwvu** [25] R.  R. transplantation  of Lower, R. C. Stofer, and the heart,” **_J. Thoracic and Cardiovascular_** N. E. Shumway, “Homovital versity of Colorado; Dr. D. Chabries and **M.** Ball of the Naval **_Surgery,_** vol. 41, p. 196,  1961. Undersea Center; Dr. 0. Frost of Frost of of Argo Systems, Inc.; Dr. **M.** [26] T. Buxton, **I. Hsu,** and R. Barter, “Fetal electrocardiography,” Hoff  of the  Intel Corp.; and the  students in two classes in the in two classes in the two classes in the in the the [27] J. Roche and E. Hon, “The fetal electrocardiogram,” **_J.A.M.A.,_** VO~. 185,  pp.441-444,Aug.  10,1963. **_Amer. J._** Department of Electrical Engineering at Stanford University: **_Obst. and Gynecol.,vol._** 92,pp. 1149-1159,Aug.  15,  1965. **280,** Computer Applications Laboratory, and **EE** **_313,_** (281 S. Yeh, L. Betyar, and E. Hon, “Computer diagnosis of fetal heart rate patterns,” **_Amer. J. Obst. and Gynecol.,_** vol. 114, pp. 

- Adaptive Systems. Special thanks are also due to R. Fraser 890-897, DeC. 1,  1972. the Naval  Undersea **zyxwvutsrqp** Center, who assisted in editin **_zyxwvuts_** the [29] E. Hon  and **S.** Lee, “Noise reduction in fetal electrocardio- 

- paper; **his** efforts led to significant improvements in i **i** orgraphy,” **_Amer. J. Obst. and Gynecol.,_** vol. 87, pp. 1087-1096, Dec. 15,  1963. 

- ganization and clarity. [ 30)  J. Van Bemmel, “Detection of weak foetal electrocardiograms by **zyxwvutsr** autocorrelation and crosscorrelation of envelopes,” **_IEEE Trans. Biomed.  Eng.,_** vol. BME-15, pp. 17-23, Jan. 196:; 

- REFERENCES [31] J. **R.** Cox, Jr., and L. N. Medgyesi-Mitschang, An algorithmic approach to signal estimation useful in fetal electrocardiography,’’ 

- [ 11 **N.** **_tionary Time Series, with Engineering Applications._** Wiener, **_Extrapolation, Interpolation and Smoodhing of Sta-_** zyxwvutsrq New York: **_EEE Trans. Biomed. Eng.,_** 1969. vol. BME-16, pp. 21 5-219, July Wiley, 1949. [32] J. Van Bemmel, L. Peeters, and S. Hengeveld, “Influence of the 

- [ 21 H. Bode and C. Shannon,  “A  simplired derivation  of linear least maternal ECG **on** the abdominal fetal ECG complex,” **_Amer.  J._** squares smoothing and prediction theory,” Roc. _IRE,_ vol. 38, **_Obst. and Gynecol.,_** vol. 102, pp.  556-562, Oct.  15,  1968. pp. 417-425, Apr. 1950. [ 331 W. Walden and S. Birnbaum, “Fetal electrocardiography with 

- [ 31  R. Kalman, **_“On_** the general theory of control,” in _zyxwvu_ Proc. **_1st_** cancellation of maternal  complexes,” **_Amer.  J.  Obst. and IFACCongresr._** London: Buttenvorth, 1960. **_Gynecol.,vol,_** 94, pp. 596-598,  Feb. 15,1966. 

- [4] R. Kalman and R. Bucy, “New results in linear filtering and pre- **_zyxwvutsrq_** (341 J. Capon, R. J. Greenfield, and R. J. Kolker, ‘‘Multidimensional diction theory,” **_Trans. ASME, ser. D, J. Basic Eng.,_** vol. 83, **_zyxwv_** maximum likelihood processing of a large aperture seismic arpp.  95-107, DeC. 1961. ray,”Proc. **_IEEE,vol. 5 5 ,_** pp.  192-211,  Feb. 1967. 

- [ **_5_** ] T. Kailath, “A view of three decades of linear filtering theory,” [35] S. P. Applebaum, “Adaptive arrays,” Special Projects Lab., Mar. 1974. Syracuse Univ.  Res. Corp., Rep. SPL 769. 

Many people have contributed  support, assistance, and ideas to the work described in this paper. The,authors especially wish to acknowledge the contributions of Prof. T. Kailath, Prof. M. Hellman, Dr. H. Garland, J. Treichler, and **M.** Larimore of Stanford University; Prof. L. Griffiths of of the University of Colorado; Dr. D. Chabries and **M.** Ball of the Naval Undersea Center; Dr. 0. Frost of Frost of of Argo Systems, Inc.; Dr. **M.** Hoff  of the  Intel Corp.; and the  students in two classes in the in two classes in the two classes in the in the the Department of Electrical Engineering at Stanford University: EE **280,** Computer Applications Laboratory, and **EE** **_313,_** Adaptive Systems. Special thanks are also due to R. Fraser of the Naval  Undersea Center, who assisted in editin the paper; **his** efforts led to significant improvements in i **i** organization and clarity. 

- [ **_5_** ] T. Kailath, “A view of three decades of linear filtering theory,” **_IEEE Trans  Inform.  Theory,vol._** IT-20,pp. 145-181, Mar. 1974. 

   - [ 361 L. J.  Griffiths, **“A** simple adaptive  algorithm  for  real-time processing in antenna arrays,” Roc. **_EEE,_** vol. 57, pp. 1696-1704, Oct. 1969. 

- [6] P. Howells, “Intermediate  frequency side-lobe canceller,” US. Patent 3 202 990, Aug. 24,1965. 

- [7] B. Widrow and **M.** Hoff, Jr., “Adaptive switching circuits,” in **_IRE WESCON Conv. Rec.,_** pt.  4, pp. 96-104,1960. 

   - [37] 0. L. Frost, 111, “An algorithm for linearly constrained adaptive array processing,”Roc. **_ZEEE,_** vol. 60, pp. 926-935, Aug. 1972. 

   - I381 K. Senne, “Adaptive linear discrete-time estimation,” Stanford Electronics Lab., Stanford Univ., Rep. SEL-68-090, June 1968 (Ph.D. dissertation). 

- [a]  J. Koford and G. Groner, “The use of an adaptive threshold element to design a linear optimal pattern classifier,” **_BEE Trans. Inform.  Theory,_** vol. IT-12, pp. 42-50,  Jan. 1966. 

- 191 F. Rosenblatt, “The Perceptron: A perceiving and recognizing automaton, Project PARA,” Cornell Aeronaut. Lab., Rep. **_85-_** 460-1, Jan. 1957. 

- [ 101 -, **_Principles of Neurodynamics: Perceptrons_** _and_ **_the TheoTy of Brain Mechanisms._** Washington, D.C.: Spartan **Books,** 1961. 

- [ 11 ] N. N h n , **_Learning Machines._** New York: McGraw-Hill, 1965. [ 12 **1** D. Gabor, W. P. L. Wdby, and **R.** Woodcock, “A universal **non-** linear fdter predictor and simulator which optimizes itself by a learning process,” **_Proc. Inst. Elec. Eng.,_** vol. 108B, July 1960. 

   - [39] T. Daniell, UAdaptive estimation with mutually correlated training samples,” Stanford Electronics Lab., Stanford Univ., Rep. SEL-68-083, Aug. 1968 (Ph.D. dissertation). 

   - [40] J. K.  Kim and L. D. Davisson, “Adaptive linear estimation for stationary M-dependent processes,” **_IEEE_** _Tmns._ **_Inform.  Theory,_** V O ~ . IT-21, pp. 23-31, Jan.  1975. 

   - [41] B. Widrow, “Adaptive fdters 1: Fundamentals,” Stanford Electronics Lab., Stanford Univ., Rep. SUSEL-66-126, Dec. 1966. 

   - [42] L. J. Griffiths,  “Rapid  measurement of **instantaneousfrequency,”** **_EEE Dans.  Acoustics,  Speech, and Si@ Roceming,_** vol. ASSP-23, pp. 209-222, Apr. 1975. 

   - [43] J. P. Burg, “Maximum entropy spectral analysis,” presented at the  37th **Annual** Meeting, Soc. Exploration Geophysicists, **Okla-** homa  City, Okla., 1967. 

- 131 R. Lucky, “Automatic equalization for digital communication,” **_Bell Syst. Tech.  J.,_** vol. 44, pp. 547-588, Apr. 1965. 

- 141 R. Lucky **_et  al, Principles of Data Communication._** New York: McGraw-Hill, 1968. 

- 151  J.  Kaunitz, “Adaptive filtering  of  broadband signals **as** applied to **noise** cancelling,” Stanford Electronics Lab., Stanford Univ., Stanford, Calif., Rep. SUSEL-72-038, Aug. 1972 (Ph.D. dissertation). 

   - [44] P. **M.** Woodward, **_Probability and Information Theory with APplications to Radar,_** 2nd ed. London: Pergamon Press, 1964. 

   - [45] **M.  I** Skolnik, **_Introduction to Radar  Systems._** New York: McGraw-Hill, 1962. 

- [ 161 M. Sondhi, **_‘“An_** adaptive echo canceller,” **_Ben  Syst. Tech. J.,_** vol. 46,pp.497-511,Mar.1967. 

- [ 171 J. Rosenberger and E. Thomas,  “Performance  of an adaptive echo canceller operating in a  noisy,  linear, timeinvariant environment,” **_BellSyst Tech.  J.,_** vot. 50, pp. 785-813, Mar. 1971. 

   - I461 **P.** Swerling, “Probability of detection for fluctuating targets,” _IRE_ **_Trans. Inform.  Theory,_** vol. IT-6, pp.  269-308, Apr. 1960. 

   - [47] J. I. Marcum, “A statistical theory of target detection by pulsed radar:  Mathematical  appendix,” _IRE_ Trans. **_Inform.  Theory,_** VOl. IT-& pp.  145-267, Apr. 1960. 

- [ 181 R. Riegler and R. Compton, Jr., **_“An_** adaptive array for interference  rejection,”Proc. **_IEEE,vol._** 61, **pp.** 748-758, June  1973. 



<!-- Start of picture text -->
Wain<br>tH AAV MAMMA ' WeNY Ay AWM YAN mv<br>ri 1 i 1<br>(a)<br>WIHT |<br>(b)<br>ADAPTATION ADAPTATION<br>BEGINS COMPLETE<br>{c)<br>Fig. 11. Result of electrocardiographic noise cancelling experiment.<br>(a) Primary input. (b) Reference input. (c) Noise canceller output.<br><!-- End of picture text -->

| 

