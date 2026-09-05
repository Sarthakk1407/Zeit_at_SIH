#!/usr/bin/env python3
"""Big architecture + tech-stack diagrams. matplotlib only."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyBboxPatch, FancyArrowPatch, Rectangle,
                                Circle, Arc, Wedge, Polygon)
import numpy as np, textwrap

BG='#fcfcfb'; INK='#0b0b0b'; INK2='#52514e'; MUTED='#8a8981'; GRID='#e5e4df'
BLUE='#2a78d6';   BLUE_L='#cde2fb'
ORANGE='#eb6834'; ORANGE_L='#fbe3d8'
AQUA='#1baf7a';   AQUA_L='#d6f2e7'
VIOLET='#4a3aa7'; VIOLET_L='#e0dcf5'
GOLD='#eda100';   GOLD_L='#fbeecd'
RED='#d03b3b';    RED_L='#fbe9e9'
MAG='#e87ba4';    MAG_L='#fbe6ee'

plt.rcParams.update({'figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG,
    'font.family':'sans-serif','font.sans-serif':['DejaVu Sans','Helvetica']})

def box(ax,x,y,w,h,title,sub=None,fc='#fff',ec=BLUE,lw=1.8,ts=11,ss=8.2,
        tc=INK,sc=INK2,r=0.03,wrap=None):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={r}",
                 linewidth=lw,edgecolor=ec,facecolor=fc,zorder=3))
    if sub:
        if wrap: sub='\n'.join(textwrap.wrap(sub,wrap))
        n=sub.count('\n')+1
        ax.text(x+w/2,y+h*(0.60 if n<3 else 0.72),title,ha='center',va='center',
                fontsize=ts,color=tc,weight='bold',zorder=4)
        ax.text(x+w/2,y+h*(0.27 if n<3 else 0.34),sub,ha='center',va='center',
                fontsize=ss,color=sc,zorder=4,linespacing=1.4)
    else:
        ax.text(x+w/2,y+h/2,title,ha='center',va='center',fontsize=ts,
                color=tc,weight='bold',zorder=4)

def arr(ax,p0,p1,c=INK2,lw=2.0,rad=0.0,ls='-',st='-|>'):
    ax.add_patch(FancyArrowPatch(p0,p1,arrowstyle=st,mutation_scale=16,linewidth=lw,
                 color=c,linestyle=ls,zorder=2,connectionstyle=f"arc3,rad={rad}",
                 shrinkA=3,shrinkB=3))

def lab(ax,x,y,s,sz=9,c=MUTED,ha='center',w='normal',st='normal'):
    ax.text(x,y,s,ha=ha,va='center',fontsize=sz,color=c,weight=w,style=st,zorder=5)

def headset(ax, cx, cy, s=1.0):
    """Simple headset: band arc, two earcups, boom arm, three mic dots."""
    ax.add_patch(Arc((cx,cy+1.05*s),2.6*s,2.2*s,theta1=20,theta2=160,
                     lw=5,color=INK2,zorder=3))
    for dx in (-1.28*s,1.28*s):
        ax.add_patch(FancyBboxPatch((cx+dx-0.34*s,cy+0.55*s),0.68*s,0.95*s,
                     boxstyle="round,pad=0,rounding_size=0.14",lw=2.5,
                     edgecolor=INK2,facecolor='#efefec',zorder=3))
    # boom arm
    ax.plot([cx-1.28*s,cx-1.75*s,cx-1.9*s],[cy+0.62*s,cy+0.15*s,cy-0.32*s],
            lw=3.5,color=INK2,zorder=3,solid_capstyle='round')
    # mic 1 voice
    ax.add_patch(Circle((cx-1.9*s,cy-0.40*s),0.17*s,facecolor=GOLD,edgecolor=INK,lw=1.6,zorder=5))
    # mic 2 outside
    ax.add_patch(Circle((cx+1.66*s,cy+1.02*s),0.15*s,facecolor=ORANGE,edgecolor=INK,lw=1.6,zorder=5))
    # mic 3 inside
    ax.add_patch(Circle((cx+1.28*s,cy+1.02*s),0.13*s,facecolor=AQUA,edgecolor=INK,lw=1.6,zorder=5))


# ══════════════════════ 4. FULL ARCHITECTURE (very big) ══════════════════════
fig,ax=plt.subplots(figsize=(24,15))
ax.set_xlim(0,24); ax.set_ylim(0,15); ax.axis('off')

ax.text(0.5,14.5,'ZEIT — FULL SYSTEM ARCHITECTURE',fontsize=26,weight='bold',color=INK)
ax.text(0.5,14.0,'AI/ML adaptive noise cancellation for defence  ·  PS 26052  ·  '
        'keep the voice, remove the gunshot, under 25 ms, on a battery',
        fontsize=12,color=INK2)

# ---------- headset panel ----------
ax.add_patch(FancyBboxPatch((0.4,8.4),6.4,5.1,boxstyle="round,pad=0,rounding_size=0.1",
             lw=2.5,edgecolor=GOLD,facecolor=GOLD_L,alpha=0.30,zorder=1))
ax.text(0.7,13.15,'THE HEADSET  —  3 MICROPHONES',fontsize=14,weight='bold',color=GOLD)
headset(ax,3.0,10.4,s=1.15)
for col,name,where,job,yy in (
    (GOLD,  'Mic 1  VOICE',  'boom arm, at the mouth',  'the signal we keep', 9.75),
    (ORANGE,'Mic 2  OUTSIDE','outer earcup shell',      'the noise reference', 9.20),
    (AQUA,  'Mic 3  INSIDE', 'inside the earcup',       'what still leaks to the ear', 8.65)):
    ax.add_patch(Circle((5.0,yy+0.10),0.11,facecolor=col,edgecolor=INK,lw=1.3,zorder=5))
    ax.text(5.22,yy+0.22,name,fontsize=9.6,weight='bold',color=INK,va='center')
    ax.text(5.22,yy-0.02,where,fontsize=8,color=INK2,va='center')
    ax.text(5.22,yy-0.22,job,fontsize=8,color=MUTED,va='center',style='italic')

ax.add_patch(Rectangle((0.7,8.55),5.8,0.62,facecolor='#fff',edgecolor=RED,lw=1.6,zorder=4))
ax.text(0.9,9.02,'HARDWARE RULE',fontsize=9,weight='bold',color=RED,zorder=5)
ax.text(0.9,8.75,'Mic 2 must NOT hear the voice. If it does, the filter cancels\n'
        'the voice — the maths forces it. Physical barrier, not software.',
        fontsize=8,color=INK2,va='center',zorder=5,linespacing=1.3)

# ---------- on-device chain ----------
ax.add_patch(FancyBboxPatch((7.2,3.3),12.2,10.2,boxstyle="round,pad=0,rounding_size=0.1",
             lw=2.5,edgecolor=BLUE,facecolor=BLUE_L,alpha=0.22,zorder=1))
ax.text(7.5,13.15,'THE ENGINE  —  ON DEVICE, REAL TIME, 10 ms PER HOP',fontsize=14,weight='bold',color=BLUE)

CX=8.0; W=4.6
def stage(y,h,tag,title,sub,ec,fc,src):
    box(ax,CX,y,W,h,f'[{tag}]  {title}',sub,fc=fc,ec=ec,ts=10.5,ss=8,wrap=52)
    lab(ax,CX+W+0.2,y+h/2,src,8.2,INK2,ha='left')

stage(12.25,0.72,'1','Audio input','reads 3 mics · lock-free ring buffer',MUTED,'#fff','never allocates,\nnever locks')
stage(11.25,0.80,'2','Aux-IVA  —  source separation',
      'splits 3 mics into voice / impulsive / background',VIOLET,VIOLET_L,
      'H-GTCRN\nno step size, always converges')
stage(10.25,0.80,'3','Robust normalisation',
      '90th percentile or FLOM  ·  NEVER RMS',RED,RED_L,
      'Shao & Nikias 1993\nRMS is undefined for heavy tails')
stage(9.25,0.80,'4','STFT + ERB','complex spectrum · ~32 perceptual bands',BLUE,BLUE_L,
      'DCCRN · GTCRN\nphase kept, bands cut compute')
stage(8.25,0.80,'5','Classifier  —  THE ADAPTIVE PART',
      'kurtosis → sets γ (how hard) and β (threshold)',GOLD,GOLD_L,
      'BMRI, made live\nalso gives operator modes')

box(ax,7.5,6.75,2.6,1.05,'[6] Impulsive path','BMRI\nAR detect + interpolate\nDOES NOT PREDICT',
    fc=ORANGE_L,ec=ORANGE,ts=10,ss=7.8)
box(ax,10.4,6.75,2.6,1.05,'[7] Neural core','GTCRN\nERB · grouped conv/RNN\nSFE · TRA',
    fc=AQUA_L,ec=AQUA,ts=10,ss=7.8)
lab(ax,13.25,7.28,'the AI/ML the PS demands\n23.7K–48.2K params',8.2,AQUA,ha='left')

stage(5.75,0.72,'8','Deep filtering','rebuilds harmonics a plain mask smears',AQUA,AQUA_L,
      'DeepFilterNet2 · IS³')
stage(4.75,0.72,'9','Voice guard','spectral correction · kills LF rumble',BLUE,BLUE_L,
      'BMRI  ·  the intelligibility clause')
stage(3.75,0.72,'10','LMS clean-up  +  [11] ISTFT','adaptive residual from Mic 3 error',MUTED,'#fff',
      'Widrow 1975')

arr(ax,(CX+W/2,12.25),(CX+W/2,12.05))
for y0,y1 in ((12.25,11.25+0.80),(11.25,10.25+0.80),(10.25,9.25+0.80),(9.25,8.25+0.80)):
    arr(ax,(CX+W/2,y0),(CX+W/2,y1))
arr(ax,(CX+1.2,8.25),(8.8,6.75+1.05),c=ORANGE,rad=0.12)
arr(ax,(CX+W-1.2,8.25),(11.7,6.75+1.05),c=AQUA,rad=-0.12)
arr(ax,(8.8,6.75),(CX+1.4,5.75+0.72),c=ORANGE,rad=-0.12)
arr(ax,(11.7,6.75),(CX+W-1.4,5.75+0.72),c=AQUA,rad=0.12)
arr(ax,(CX+W/2,5.75),(CX+W/2,4.75+0.72))
arr(ax,(CX+W/2,4.75),(CX+W/2,3.75+0.72))

# mics into the chain
for yy,col in ((9.75,GOLD),(9.20,ORANGE),(8.65,AQUA)):
    arr(ax,(6.55,yy),(CX,12.4),c=col,lw=1.6,rad=0.22)
# mic3 error into LMS
arr(ax,(6.55,8.65),(CX,4.05),c=AQUA,lw=1.6,rad=-0.30,ls='--')
lab(ax,6.9,5.6,'Mic 3 error signal\n(what still leaks)',7.6,AQUA,ha='left',st='italic')

box(ax,19.7,3.75,3.9,0.72,'CLEAN VOICE OUT','to the radio',fc=AQUA_L,ec=AQUA,ts=11,ss=8)
arr(ax,(CX+W,4.11),(19.7,4.11),c=AQUA,lw=2.4)

# ---------- offline panel ----------
ax.add_patch(FancyBboxPatch((19.9,5.6),3.7,7.9,boxstyle="round,pad=0,rounding_size=0.1",
             lw=2.5,edgecolor=MAG,facecolor=MAG_L,alpha=0.30,zorder=1))
ax.text(20.1,13.15,'OFF-DEVICE',fontsize=14,weight='bold',color=MAG)
ax.text(20.1,12.85,'none of this ships',fontsize=8.5,color=INK2,style='italic')
oy=12.35
for t,s in (('Real gunshot capture','2-mic range data — OURS'),
            ('Synthetic generator','IS³ pipeline template'),
            ('α-stable augmentation','α≈1, and below 0.5 clipped'),
            ('Input saturation model','the mic-clipping gap'),
            ('RIR spread + HRTF','many rooms, real head shadow'),
            ('Training  ·  PyTorch','mask on the noisy input'),
            ('Pruning + quantization','290K → 103K reference'),
            ('Export  →  model.onnx','the ONLY thing that crosses')):
    box(ax,20.1,oy-0.62,3.3,0.62,t,s,fc='#fff',ec=MAG,ts=8.8,ss=7.2,lw=1.2)
    oy-=0.78
arr(ax,(21.7,5.6),(13.0,6.75),c=MAG,lw=2.2,rad=0.18,ls='--')
lab(ax,17.3,5.95,'trained weights  →  model.onnx',8.6,MAG,w='bold')

# footer
ax.add_patch(Rectangle((0.4,0.35),23.2,2.6,facecolor='#fff',edgecolor=GRID,lw=1.5,zorder=2))
ax.text(0.7,2.72,'WHY THE ARCHITECTURE HAS TWO PATHS  —  the one decision everything else follows from',
        fontsize=12,weight='bold',color=INK,zorder=3)
ax.text(0.7,2.28,
 'Deep ANC (the main published deep-learning ANC paper) reduces its own latency by PREDICTING the noise one or two frames ahead.\n'
 'That works for engine hum, which repeats. It costs 1.5–1.7 dB of cancellation per 10 ms bought back.\n\n'
 'It cannot work for a gunshot. There is nothing in the milliseconds before a gunshot that tells you one is coming.\n'
 'So the impulsive path does not predict — it WAITS, DETECTS and REACTS.  And because Mic 2 sits nearer the gun than Mic 1,\n'
 'it hears the blast ~29 ms early at 10 m: real look-ahead from geometry, not from prediction, with no cancellation penalty.',
 fontsize=9.6,color=INK2,va='top',zorder=3,linespacing=1.55)
fig.savefig('4_architecture_full.png',dpi=130,bbox_inches='tight')
plt.close(fig); print('  4_architecture_full.png')


# ═══════════════ 5. SIGNAL PATH DETAIL — every algorithm named ═══════════════
fig,ax=plt.subplots(figsize=(21,13))
ax.set_xlim(0,21); ax.set_ylim(0,13); ax.axis('off')
ax.text(0.4,12.5,'THE ENGINE  —  every block, every algorithm',fontsize=22,weight='bold',color=INK)
ax.text(0.4,12.05,'left: what it does   ·   middle: the algorithm   ·   right: why it is there',
        fontsize=11,color=INK2)

rows=[
 ('1','Audio input','read 3 mics, hand off','lock-free SPSC ring buffer',
  'must never allocate or lock — one late frame is an audible click',MUTED,'#fff'),
 ('2','Source separation','pull 3 mics apart into 3 streams','Aux-IVA\n(auxiliary-function independent vector analysis)',
  '3 sensors separate 3 sources. No step size to tune, converges every iteration.\nDoes the coarse work so the network can stay tiny',VIOLET,VIOLET_L),
 ('3','Normalisation','scale to a standard loudness','90th-percentile scaling\nor fractional lower-order moments',
  'RMS is built on variance. For heavy-tailed noise the variance is INFINITE.\nThe closest published system uses RMS — that is a real bug',RED,RED_L),
 ('4','Analysis','sound → time-frequency picture','complex STFT, 20 ms frame / 10 ms hop\n+ ~32 ERB bands',
  'complex keeps PHASE, which cancellation needs.\nERB cuts the band count — this is where the compute saving comes from',BLUE,BLUE_L),
 ('5','Classification','which kind of noise is this?','kurtosis → γ (aggressiveness), β (threshold)\nSVM / decision tree / tiny CNN',
  'THIS IS THE "ADAPTIVE" THE PS DEMANDS.\nAlso gives Listening mode (low γ) and Combat mode (high γ) for free',GOLD,GOLD_L),
 ('6','Impulsive path','find the bang, cut it, fill the hole','BMRI — binary mask residual interpolation\nAR order 16/32, 2048-sample blocks',
  'Does NOT predict. Waits, detects, reacts.\nBecause nothing before a gunshot tells you it is coming',ORANGE,ORANGE_L),
 ('7','Neural core','learn a mask, apply to the NOISY input','GTCRN — ERB + grouped conv + grouped RNN\n+ SFE + TRA',
  'The AI/ML the PS requires. 23.7K–48.2K params.\nFeed it BOTH separated speech and separated noise — H-GTCRN\'s biggest gain',AQUA,AQUA_L),
 ('8','Detail repair','rebuild what the mask smeared','deep filtering, complex, below 5 kHz',
  'A per-band gain flattens the harmonic structure of voiced speech.\nThis puts it back',AQUA,AQUA_L),
 ('9','Voice guard','make sure cleaning did not eat the voice','spectral correction, removes regained LF rumble',
  'The intelligibility requirement is a hard PS target.\nThis is the module that guarantees it',BLUE,BLUE_L),
 ('10','Residual clean-up','cancel whatever still leaks','LMS adaptive filter, driven by Mic 3',
  'Mic 3 hears what reaches the ear. If it is not silent, something leaked.\nHandles drift a trained model cannot anticipate',MUTED,'#fff'),
 ('11','Synthesis','picture → sound','inverse STFT, overlap-add',
  'phase was kept all the way through, so the output is not smeared',MUTED,'#fff'),
]
y=11.35; H=0.92
for tag,name,what,algo,why,ec,fc in rows:
    box(ax,0.4,y-H,3.2,H,f'[{tag}]  {name}',what,fc=fc,ec=ec,ts=10.5,ss=8,wrap=30)
    box(ax,3.9,y-H,5.2,H,algo,None,fc='#fff',ec=ec,ts=9.4,lw=1.3)
    ax.text(9.5,y-H/2,why,fontsize=8.8,color=INK2,va='center',linespacing=1.45)
    if y-H>0.9: arr(ax,(2.0,y-H),(2.0,y-H-0.10),lw=1.6)
    y-=1.02
fig.savefig('5_signal_path_detail.png',dpi=130,bbox_inches='tight')
plt.close(fig); print('  5_signal_path_detail.png')


# ══════════════════════════ 6. TECH STACK ════════════════════════════════════
fig,ax=plt.subplots(figsize=(20,13))
ax.set_xlim(0,20); ax.set_ylim(0,13); ax.axis('off')
ax.text(0.4,12.5,'TECH STACK',fontsize=22,weight='bold',color=INK)
ax.text(0.4,12.05,'C++ for anything with a deadline  ·  Python for everything else  ·  '
        'the ONNX file is the only thing that crosses',fontsize=11,color=INK2)

def stack(x,w,title,sub,col,fill,items,y0=11.2,h=10.0):
    ax.add_patch(FancyBboxPatch((x,y0-h),w,h,boxstyle="round,pad=0,rounding_size=0.08",
                 lw=2.5,edgecolor=col,facecolor=fill,alpha=0.28,zorder=1))
    ax.text(x+w/2,y0-0.35,title,ha='center',fontsize=14,weight='bold',color=col)
    ax.text(x+w/2,y0-0.70,sub,ha='center',fontsize=8.6,color=INK2,style='italic')
    yy=y0-1.25
    for n,what,forwhat in items:
        box(ax,x+0.2,yy-0.60,w-0.4,0.60,f'{n}. {what}',forwhat,fc='#fff',ec=col,
            ts=9.2,ss=7.4,lw=1.2,wrap=48)
        yy-=0.72

stack(0.3,6.2,'C++  —  THE ENGINE','on device, hard 10 ms deadline',BLUE,BLUE_L,[
  (1,'C++17','the whole real-time path'),
  (2,'CMake','build + cross-compile to ARM'),
  (3,'PortAudio','audio I/O while developing'),
  (4,'ALSA','audio I/O on the target board'),
  (5,'PFFFT','the FFT — NOT FFTW, that is GPL'),
  (6,'ONNX Runtime','runs the trained model'),
  (7,'Eigen','AR / Levinson-Durbin maths'),
  (8,'doctest','parity + real-time safety tests'),
  (9,'TensorRT','only if the board is Jetson'),
])
stack(6.9,6.2,'HAND-WRITTEN C++','no library does these',ORANGE,ORANGE_L,[
  (10,'Lock-free ring buffer','audio between threads, no mutex'),
  (11,'Robust normalisation','percentile / FLOM, replaces RMS'),
  (12,'BMRI impulsive path','AR detect + interpolate'),
  (13,'Transient classifier','kurtosis → γ, β  (the adaptive bit)'),
  (14,'Aux-IVA','3-mic blind source separation'),
  (15,'LMS residual','~20 lines, driven by Mic 3'),
  (16,'Spectral guard','protects intelligibility'),
])
stack(13.5,6.2,'PYTHON  —  OFFLINE','never runs on the device',MAG,MAG_L,[
  (17,'numpy + scipy','all DSP, already installed'),
  (18,'matplotlib','reports, monitor, diagrams'),
  (19,'sounddevice','capture only'),
  (20,'wavio.py  (ours)','WAV I/O, no libsndfile'),
  (21,'PyTorch','model definition + training'),
  (22,'torch.onnx','export — the ONLY boundary'),
  (23,'pesq / pystoi','PS targets 2.5 / 0.85'),
  (24,'DNSMOS','SIG 4.1 · BAK 4.2, catches over-suppression'),
])

ax.add_patch(Rectangle((0.3,0.35),19.4,1.65,facecolor='#fff',edgecolor=RED,lw=1.8,zorder=3))
ax.text(0.6,1.72,'THE BOUNDARY  —  and the failure nobody plans for',fontsize=12,weight='bold',color=RED,zorder=4)
ax.text(0.6,1.30,'PyTorch  ──torch.onnx.export──►  model.onnx  ──►  ONNX Runtime (C++).  Nothing else crosses.\n'
 'The silent failure: C++ produces slightly different numbers than the Python it was trained as — a different window, a different ERB edge.\n'
 'Nothing crashes; the model just quietly performs worse. Fix: a PARITY TEST comparing EVERY stage, not just the output. Build it early.',
 fontsize=9.4,color=INK2,va='center',zorder=4,linespacing=1.5)
fig.savefig('6_tech_stack.png',dpi=130,bbox_inches='tight')
plt.close(fig); print('  6_tech_stack.png')
