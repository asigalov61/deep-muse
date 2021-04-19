# -*- coding: utf-8 -*-
"""deep-muse.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1-ShLT3EJBp_oFxbOqFVgKMxXzodwm4u8

# deep-muse (ver 0.6) [WIP]

***

# Advanced text-to-music generator

***

## Inspired by https://github.com/lucidrains/deep-daze

## Powered by tegridy-tools TMIDI 2.2 Optimus Processors

***

### Project Los Angeles
### Tegridy Code 2021

***

# Setup environment
"""

#@title Install dependencies
!git clone https://github.com/asigalov61/tegridy-tools
!pip install tqdm
!apt install fluidsynth #Pip does not work for some reason. Only apt works
!pip install midi2audio

# packages below are for plotting pianoroll only
# they are not needed for anything else
!pip install pretty_midi
!pip install librosa
!pip install matplotlib

#@title Load needed modules
print('Loading needed modules. Please wait...')

import sys
import os
import json
import secrets
import copy

os.chdir('/content/tegridy-tools/tegridy-tools/')
import TMIDI
os.chdir('/content/')

from pprint import pprint

import tqdm.auto
from tqdm import auto
from midi2audio import FluidSynth
from IPython.display import display, Javascript, HTML, Audio

# only for plotting pianoroll
import pretty_midi
import librosa.display
import matplotlib.pyplot as plt

from google.colab import output, drive

print('Creating Dataset dir...')
if not os.path.exists('/content/Dataset'):
    os.makedirs('/content/Dataset')

os.chdir('/content/')
print('Loading complete. Enjoy! :)')

"""# Prep statistics dictionary"""

#@title Load English Karaoke Statistics
data = TMIDI.Tegridy_Any_Pickle_File_Loader('/content/tegridy-tools/tegridy-data/Basic-English-Karaoke-Statistics')
karp = data[0]
kard = data[1]
karw = data[2]
pitches_words = data[3]
words_music = data[4]

pitches = []
durations = []
words = []

for p in karp:
  pitches.extend(p)

for d in kard:
  durations.extend(d)

for w in karw:
  words.extend(w)

pitches_durations = []
for i in range(len(words)):
  pitches_durations.append([pitches[i], durations[i]])

words_music = []

for i in range(len(words)):
  words_music.append([words[i], pitches_durations[i][0], pitches_durations[i][1] ])

"""# Generate Music

## NOTE: Karaoke melody only for now
"""

#@title Generate Music from the lyrics below

#@markdown NOTE: No spaces, commas, etc., please.

#@markdown ProTip: Be as ambiguous and general as possible for best results as the current dictionary is too small for anything specific. 
lyric1 = 'I love you very very much' #@param {type:"string"}
lyric2 = 'I can not live without you' #@param {type:"string"}
lyric3 = 'You always present on my mind' #@param {type:"string"}
lyric4 = 'I often think about you' #@param {type:"string"}

lyric5 = 'I am all out of love I am so lost without you' #@param {type:"string"}
lyric6 = 'I know you were right believing for so long' #@param {type:"string"}
lyric7 = 'I am all out of love what am I without you' #@param {type:"string"}
lyric8 = 'I cant be too late to say that I was so wrong' #@param {type:"string"}
minimum_notes_pitch_baseline = 70 #@param {type:"slider", min:22, max:127, step:1}
minimum_notes_duration_baseline = 200 #@param {type:"slider", min:100, max:2000, step:100}

txt = '| ' + lyric1 + ' | ' + lyric2 + ' | ' + lyric3 + ' | ' + lyric4 + ' | ' + lyric5 + ' | ' + lyric6 + ' | ' + lyric7 + ' | ' + lyric8 + ' |'

txts = txt.split()
song = []
rating = 0
melody_baseline_pitch = 90
notes_match_rating = 40
p = ['=====', 60, 0]
x = ['=====', 0, 0]

print('Generating composition. Please wait...')

for t in auto.tqdm(txts):
  try:

    # simple base-line matching
    '''x = ['=====', 0, 0]
    while x[1] <= melody_baseline_pitch:
      x = words_music[words.index(t, secrets.randbelow(len(words)))]'''
    
    # fuzzywuzzy rating matching
    '''while rating < notes_match_rating:
      try:
        x = copy.deepcopy(words_music[words.index(t, secrets.randbelow(len(words)))])
        #print(x)
        rating = fuzz.ratio(str(x[2]), str(p[2]))
        # print(rating)
      except:
        x = ['=====', 22, 1600]
        rating = 0
        break'''
    # pitch/duration matching (produces nice results)
    while x[1] < minimum_notes_pitch_baseline or x[2] < minimum_notes_duration_baseline:
      try:
        x = copy.deepcopy(words_music[words.index(t, secrets.randbelow(len(words)))])

      except:
        x = ['=====', 22, 1600] # pitch > 21 for Google note-seq compatibility
        break

    song.append(x)
    x = ['=====', 0, 0]
    p = copy.deepcopy(x)
    rating = 0

  except KeyboardInterrupt:
    break

pprint(song, compact=True)

"""# Convert generated music composition to MIDI file and download/listen to the output :)"""

#@title Convert to MIDI
notes_durations_multiplier = 1 #@param {type:"slider", min:0.1, max:2, step:0.1}
out1 = []
out = []
time = 0
note = []
for s in song:
  if s[1] > 22:
    note = ['note', int(time), s[2], 0, s[1], 90 ]
  else:
    note = ['note', int(time), s[2], 0, s[1], 0 ]

 
  out.append(note)
  out1.append(note)
  
  kar = ['lyric', int(time), s[0] ]
  out.append(kar)

  time += int(s[2] * notes_durations_multiplier)

TMIDI.Tegridy_SONG_to_MIDI_Converter(out, output_file_name='/content/deep-muse-Output-MIDI')

#@title Plot and listen to the last generated composition
#@markdown NOTE: May be very slow with the long compositions
fname = '/content/deep-muse-Output-MIDI'

fn = os.path.basename(fname + '.mid')
fn1 = fn.split('.')[0]
print('Playing and plotting composition...')

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', sr=64000, cmap=plt.cm.hot)
plt.title('Composition: ' + fn1)

print('Synthesizing the last output MIDI. Please stand-by... ')
FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# Generate Chords

## NOTE: This is a very simple chords generator so do not expect any miracles, please :)
"""

# Commented out IPython magic to ensure Python compatibility.
#@title Download Fuzzy Chords Dataset
# %cd /content/

!wget --no-check-certificate -O Fuzzy-Chords-Dataset.zip "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118481&authkey=AKE0S57SHzG0rr8"
!unzip -j Fuzzy-Chords-Dataset.zip

# %cd /content/

#@title Load/Re-load processed dataset
full_path_to_processed_dataset = "/content/Fuzzy-Chords-Dataset" #@param {type:"string"}


# Writing dataset to memory
cho_list_f, mel_list_f = TMIDI.Tegridy_Pickle_File_Loader(full_path_to_processed_dataset)

#@title Generate chords
minimum_notes_per_chord = 7 #@param {type:"slider", min:1, max:10, step:1}

print('Generating chords for the melody. Please wait...')
print('Sorting chords...')

chor = []
le = []
hp = []
for c in auto.tqdm(cho_list_f):
  if len(c) >= minimum_notes_per_chord:
    c.sort(reverse=True, key=lambda x: x[4])
    chor.append(c)
    le.append(len(c))
    hp.append(c[0][4])

print('Looking for the matching chords...')

out3 = []

for m in out:
  if len(m) > 3:
    for i in hp:
      if m[4] == i:
        
        if secrets.randbelow(1000) == 0:
          z = hp.index(i)
          cho = copy.deepcopy(chor[z])
          ch = []
          cho[0][3] = 0
          cho[0][2] = m[2]
          ch.append(cho[0])
          for c in cho[1:]:
            c[2] = m[2]
            c[3] = 1
            ch.append(c)

          out3.append(ch)

          break

print('Finalizing the song...')

out1 = []

time = 0
pe = copy.deepcopy(out3[0][0])
pe[1] = 0
for o in out3[1:]:
  time = pe[1] + pe[2]
  
  for n in o:
    b = copy.deepcopy(n)
    b[1] = time

    out1.append(b)
  o[0][1] = time
  pe = copy.deepcopy(o[0])

print('Done!')
print('Final notes count: ', len(out1))
print('Enjoy! :)')

TMIDI.Tegridy_SONG_to_MIDI_Converter(out1, output_file_name='/content/deep-muse-Output-MIDI')

#@title Plot and listen to the last generated composition
#@markdown NOTE: May be very slow with the long compositions
fname = '/content/deep-muse-Output-MIDI'

fn = os.path.basename(fname + '.mid')
fn1 = fn.split('.')[0]
print('Playing and plotting composition...')

pm = pretty_midi.PrettyMIDI(fname + '.mid')

# Retrieve piano roll of the MIDI file
piano_roll = pm.get_piano_roll()

plt.figure(figsize=(14, 5))
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', sr=64000, cmap=plt.cm.hot)
plt.title('Composition: ' + fn1)

print('Synthesizing the last output MIDI. Please stand-by... ')
FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# English Karaoke Statistics Graphs"""

#@title Pitches-Words Graph
from matplotlib import pyplot as plt
from matplotlib import style
 
style.use('ggplot')
 
x = pitches_words.values()
y = pitches_words.keys()
 
plt.bar(x, y, align='center')
 
plt.title('Pitches Words Diagram')
plt.ylabel('Pitches')
plt.xlabel('Words')
 
plt.show()

#@title Pitches-Words Graph 2
colors = list("rgb")


x = pitches_words.keys()
y = pitches_words.values()
plt.scatter(x,y,color=colors.pop())

plt.legend(pitches_words.keys())
plt.savefig('/content/scatterplot.png', dpi=300)
plt.show()

#@title Pitches-Words Graph 3
labels, values = zip(*pitches_words.items())
plt.bar(labels, values)

#@title Pitches-Words Graph 4
plt.bar(range(len(pitches_words)), pitches_words.values(), align="center")
plt.xticks(range(len(pitches_words)), list(pitches_words.keys()))

"""# Congrats! You did it! :)"""