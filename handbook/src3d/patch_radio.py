"""Replace the bench display with a tactical communication unit.

PS 26052 asks for integration with "microphones (primary + reference) and
headphones/communication units". A monitor on the bench depicts a development
setup, not the deployed chain, so it is replaced by a handheld radio and the
headphone return path back to the earcups.

The micro-HDMI cable stays on the bill of materials — it is genuinely needed to
bring the board up — but it is no longer drawn as part of the signal path.

    python src3d/patch_radio.py
"""
import io
import sys

# ---------------------------------------------------------------- geometry
p = 'src3d/04-geometry.html'
s = io.open(p, encoding='utf-8').read()

OLD_MON = """/* ---------------- monitor stand-in for micro-HDMI ---------------- */
var P_MON=new THREE.Vector3(34,0,-6);
(function(){
  var g=new THREE.Group();g.position.copy(P_MON);
  var panel=box(16,9.5,.5,MAT.plasticD);at(panel,0,7.5,0);pick(panel,'mon');g.add(panel);
  var scr=box(15.0,8.6,.12,MAT.screen);at(scr,0,7.5,0.32);g.add(scr);
  var neck=box(1.2,2.6,1.0,MAT.plasticD);at(neck,0,1.4,0);g.add(neck);
  var foot=box(8,.5,5,MAT.plasticD);at(foot,0,.25,0);g.add(foot);
  gPi.add(g);PARTS.monGroup=g;
})();"""

NEW_RADIO = """/* ---------------------------------------------------------------
   COMMUNICATION UNIT — handheld tactical radio, ~200 x 65 x 40 mm
   The deployed sink for Lane B. Replaces the bench display: the
   problem statement asks for integration with headphones and
   communication units, not with a development monitor.
   --------------------------------------------------------------- */
var P_RADIO=new THREE.Vector3(33,0,-4);
var P_RAD_AUD;
(function(){
  var g=new THREE.Group();g.position.copy(P_RADIO);
  var W=6.5,H=18,D=4.0;

  var body=box(W,H,D,MAT.plasticD);at(body,0,H/2,0);pick(body,'radio');g.add(body);
  var face=box(W*0.92,H*0.96,0.14,std(0x35353b,.72,.10));at(face,0,H/2,D/2+0.05);g.add(face);

  /* display strip */
  var disp=box(W*0.72,3.0,.10,MAT.screen);at(disp,0,H-3.6,D/2+0.13);g.add(disp);
  for(var r=0;r<2;r++){
    var lit=box(W*0.52,.22,.06,std(0x6f8f7a,.6,.05));
    at(lit,-0.3,H-3.0-r*0.9,D/2+0.20);g.add(lit);
  }
  /* speaker grille */
  for(var gr=0;gr<5;gr++){
    var slot=box(W*0.56,.20,.06,std(0x1c1c20,.9,.05));
    at(slot,0,H-7.4-gr*0.45,D/2+0.16);g.add(slot);
  }
  /* keypad */
  for(var kr=0;kr<4;kr++){
    for(var kc=0;kc<3;kc++){
      var kb=box(1.05,.62,.16,std(0x2a2a30,.7,.08));
      at(kb,-1.55+kc*1.55,H-11.0-kr*1.15,D/2+0.16);g.add(kb);
    }
  }
  /* channel selector on top */
  var sel=cyl(1.15,1.15,.85,22,MAT.knob);at(sel,-1.5,H+0.42,0);g.add(sel);
  var vol=cyl(.80,.80,.70,20,MAT.knob);at(vol,1.4,H+0.35,0);g.add(vol);

  /* antenna */
  var ant=cyl(.30,.22,9.5,14,std(0x1e1e22,.86,.05));at(ant,2.3,H+4.9,0);g.add(ant);
  var antBase=cyl(.52,.52,.9,16,MAT.metalD);at(antBase,2.3,H+0.45,0);g.add(antBase);

  /* push-to-talk on the side */
  var ptt=box(.55,3.2,1.6,std(0x2a2a30,.75,.08));at(ptt,-W/2-0.22,H*0.62,0);
  pick(ptt,'ptt');g.add(ptt);

  /* audio / headset connector, top edge */
  var aud=cyl(.62,.62,.70,18,MAT.metal);at(aud,-2.6,H+0.36,0);pick(aud,'radioaud');g.add(aud);

  /* battery pack at the base */
  var bat=box(W*1.02,4.2,D*1.05,std(0x33333a,.8,.10));at(bat,0,2.1,0);g.add(bat);

  gPi.add(g);PARTS.radioGroup=g;
  P_RAD_AUD=new THREE.Vector3().copy(P_RADIO).add(new THREE.Vector3(-2.6,H+0.9,0));
})();"""

if OLD_MON not in s:
    sys.exit('monitor block not found — already patched?')
s = s.replace(OLD_MON, NEW_RADIO)

# Cabling: the HDMI run to the display becomes the audio feed to the radio,
# and a return path carries received audio back to the earcups.
OLD_CABLE = """CB.hdmi=cable([P_PI_HDMI,new THREE.Vector3(4,1.0,-10),new THREE.Vector3(24,1.0,-12),
  new THREE.Vector3(P_MON.x-2,2.0,P_MON.z-1)],std(0x2a2a30,.94,.02),.17);"""
NEW_CABLE = """/* Lane B output: enhanced speech from the board to the radio */
CB.radio=cable([P_PI_USB.clone().add(new THREE.Vector3(0,-0.4,1.6)),
  new THREE.Vector3(24,1.0,-6),new THREE.Vector3(30,1.0,-5),P_RAD_AUD],
  std(0x2a2a30,.94,.02),.17);
/* Return path: received audio from the radio back to the earcups —
   the "headphones / communication unit" integration the PS calls for */
CB.phones=cable([P_RAD_AUD,new THREE.Vector3(20,10,10),new THREE.Vector3(-6,16,14),
  new THREE.Vector3(-24,20,8),P_SPK.clone().add(new THREE.Vector3(1.2,2.0,0))],
  std(0x24242a,.94,.02),.16);"""
if OLD_CABLE not in s:
    sys.exit('hdmi cable not found')
s = s.replace(OLD_CABLE, NEW_CABLE)
io.open(p, 'w', encoding='utf-8').write(s)
print('04-geometry: display replaced by radio; cabling rerouted')

# ---------------------------------------------------------------- labels + info
p = 'src3d/05-sim.html'
s = io.open(p, encoding='utf-8').read()

s = s.replace(
  "  {k:'mon'   ,t:'micro-HDMI out'       ,p:P_MON.clone().add(new THREE.Vector3(0,14.0,0)),c:'--text-3'},",
  "  {k:'radio' ,t:'Communication unit'   ,p:P_RADIO.clone().add(new THREE.Vector3(0,24.0,0)),c:'--text-3'},")

OLD_MON_INFO = """mon:{tag:'Output',h:'micro-HDMI to HDMI',b:[
 'The Pi 5 uses two micro-HDMI ports, not full-size HDMI. A standard cable does not fit.',
 'Worth listing explicitly because it is the kind of detail discovered at the venue rather than at the bench. In the demonstration this carries the live spectrogram and the impulse markers from the auxiliary detection head.'],
 d:[['Port','micro-HDMI, 2 ×'],['Cost','₹300–500'],['Shows','Live spectrogram, impulse markers, latency counter']]},"""
NEW_RADIO_INFO = """radio:{tag:'Lane B · deployed sink',h:'Communication unit',b:[
 'Where the enhanced speech actually goes. The problem statement asks for integration with microphones and headphones or communication units, so the demonstrated chain terminates at a radio rather than at a screen.',
 'This matters for what gets measured. A tactical radio does not transmit our waveform — it transmits MELPe, the NATO STANAG 4591 vocoder, at 2400, 1200 or 600 bits per second, re-synthesising speech at the far end from pitch, voicing and spectral envelope. Every metric should therefore be reported twice: before this stage and after it.'],
 d:[['Role','Deployed output of Lane B'],['Codec','MELPe · STANAG 4591'],['Bitrate','2400 / 1200 / 600 bps'],['From the board','Enhanced speech, 20 ms frames'],['Back to the headset','Received audio to the earcups']],
 w:['No development computer in the chain','A monitor or laptop belongs to bring-up, not to the demonstrated system. The board boots from its own card, runs the engine headlessly and talks to the radio. The micro-HDMI cable stays on the parts list for configuration, but it is not part of the signal path.']},
ptt:{tag:'Control',h:'Push-to-talk',b:[
 'Keys the transmitter. It is also the natural place to switch operator modes, because the classifier already exposes γ as a single dial — a low-γ listening mode that preserves ambient awareness, and a high-γ combat mode that protects voice through gunfire.'],
 d:[['Wiring','GPIO header on the board'],['Also selects','Listening / combat preset']]},
radioaud:{tag:'Integration',h:'Headset connector',b:[
 'Carries enhanced speech into the radio and received audio back out to the earcups. One connector, both directions.',
 'This is the physical point the problem statement means by "headphones / communication units", and it is where a bench demonstration becomes a system demonstration.']},"""
if OLD_MON_INFO not in s:
    sys.exit('monitor info entry not found')
s = s.replace(OLD_MON_INFO, NEW_RADIO_INFO)

s = s.replace(
  "pihdmi:{tag:'Output',h:'micro-HDMI',b:['Two micro-HDMI outputs. The demonstration display connects here.']},",
  "pihdmi:{tag:'Bring-up only',h:'micro-HDMI',b:['Two micro-HDMI outputs, used to configure the board and read logs during bring-up.','Deliberately not drawn as part of the bench: the deployed system runs headless and its output goes to the communication unit. The cable stays on the parts list because the Pi 5 takes micro-HDMI rather than full-size, which is a detail better discovered at the bench than at the venue.']},")
io.open(p, 'w', encoding='utf-8').write(s)
print('05-sim: label and part data updated')

# ---------------------------------------------------------------- loop
p = 'src3d/06-loop.html'
s = io.open(p, encoding='utf-8').read()
if 'CB.hdmi' not in s:
    sys.exit('CB.hdmi not found in loop')
s = s.replace('CB.hdmi.userData.curve', 'CB.radio.userData.curve')
io.open(p, 'w', encoding='utf-8').write(s)
print('06-loop: output flow marker follows the radio cable')
