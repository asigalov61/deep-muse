# -*- coding: utf-8 -*-
"""deep-muse.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zt2D0DvtYMM_0Ol4M96uiy1cUH6X2nmC

# deep-muse (ver 0.8) [WIP]

***

# Advanced text-to-music generator

***

## Inspired by https://github.com/lucidrains/deep-daze

## Powered by tegridy-tools TMIDI Optimus Processors

***

### Project Los Angeles
### Tegridy Code 2021

***

# Setup environment
"""

#@title Install dependencies
!git clone https://github.com/asigalov61/tegridy-tools
!pip install tqdm

# for data
!pip install fuzzywuzzy[speedup]

# for listening
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

from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from itertools import islice, accumulate

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

# Commented out IPython magic to ensure Python compatibility.
#@title Download English Karaoke MIDI classification model
# %cd /content/
!wget --no-check-certificate -O Karaoke-English-Full.pickle "https://onedrive.live.com/download?cid=8A0D502FC99C608F&resid=8A0D502FC99C608F%2118485&authkey=ABXca9Cn2L-64UE"

#@title Load and prep the model

print('Loading the Karaoke model. Please wait...')
data = TMIDI.Tegridy_Any_Pickle_File_Loader('/content/Karaoke-English-Full')

print('Done!')
print('Prepping data...')

kar_ev_f = data[2]

kar = []
karaoke = []

for k in auto.tqdm(kar_ev_f):
  k.sort(reverse=False, key=lambda x: x[1])
  for kk in k:
    
    if kk[0] == 'note' or kk[0] == 'text_event':
      kar.append(kk)

kar_words = []
for o in auto.tqdm(kar):
  if o[0] != 'note':
    kar_words.append(str(o[2]).lower())

print('Done! Enjoy! :)')

"""# Generate Music


"""

#@title Generate Music from the lyrics below

#@markdown NOTE: No symbols, special chars, commas, etc., please.

#@markdown ProTip: Be as ambiguous and general as possible for best results as the current dictionary is too small for anything specific.

randomize_words_matching = False #@param {type:"boolean"}

lyric1 = 'I love you very very much' #@param {type:"string"}
lyric2 = 'I can not live without you' #@param {type:"string"}
lyric3 = 'You always present on my mind' #@param {type:"string"}
lyric4 = 'I often think about you' #@param {type:"string"}

lyric5 = 'I am all out of love I am so lost without you' #@param {type:"string"}
lyric6 = 'I know you were right believing for so long' #@param {type:"string"}
lyric7 = 'I am all out of love what am I without you' #@param {type:"string"}
lyric8 = 'I cant be too late to say that I was so wrong' #@param {type:"string"}

text = [lyric1, lyric2, lyric3, lyric4, lyric5, lyric6, lyric7, lyric8]

song = []

words_lst = ''

print('=' * 100)

print('Deep-Muse Text to Music Generator')
print('Starting up...')

print('=' * 100)

for t in auto.tqdm(text):
  txt = t.lower().split(' ')
  
  kar_words_split = list(TMIDI.Tegridy_List_Slicer(kar_words, len(txt)))
  
  ratings = []

  for k in kar_words_split:
    ratings.append(fuzz.ratio(txt, k))
  
  if randomize_words_matching:
    
    try:
      ind = ratings.index(secrets.choice([max(ratings)-5, max(ratings)-4, max(ratings)-3, max(ratings)-2, max(ratings)-1, max(ratings)]))
    except:
      ind = ratings.index(max(ratings))
  
  else:
    ind = ratings.index(max(ratings))

  words_list = kar_words_split[ind]
  pos = ind * len(txt)
  

  print(words_list)

  words_lst += ' '.join(words_list) + chr(10)

  c = 0
  for i in range(len(kar)):
    if kar[i][0] != 'note':
      if c == pos:
        idx = i
        break

    if kar[i][0] != 'note':
      c += 1
 
  c = 0
  for i in range(idx, len(kar)):
    if kar[i][0] != 'note':
      if c == len(txt):
        break

    if kar[i][0] == 'note':
      song.append(kar[i])

    if kar[i][0] != 'note':
      c += 1
      song.append(kar[i])

so = [y for y in song if len(y) > 3]
if so != []: sigs = TMIDI.Tegridy_MIDI_Signature(so, so)

print('=' * 100)

print(sigs[0])

print('=' * 100)

song1 = []
p = song[0]
p[1] = 0
time = 0

song.sort(reverse=False, key=lambda x: x[1])

for i in range(len(song)-1):

    ss = copy.deepcopy(song[i])
    if song[i][1] != p[1]:
      
      if abs(song[i][1] - p[1]) > 1000:
        time += 300
      else:
        time += abs(song[i][1] - p[1])

      ss[1] = time 
      song1.append(ss)
      
      p = copy.deepcopy(song[i])
    else:
      
      ss[1] = time
      song1.append(ss)
      
      p = copy.deepcopy(song[i])

pprint(words_lst, compact=True)
print('=' * 100)

"""# Convert generated music composition to MIDI file and download/listen to the output :)"""

#@title Convert to MIDI

TMIDI.Tegridy_SONG_to_MIDI_Converter(song1, output_file_name='/content/deep-muse-Output-MIDI')

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
librosa.display.specshow(piano_roll, x_axis='time', y_axis='cqt_note', fmin=1, hop_length=160, sr=16000, cmap=plt.cm.hot)
plt.title('Composition: ' + fn1)

print('Synthesizing the last output MIDI. Please stand-by... ')
FluidSynth("/usr/share/sounds/sf2/FluidR3_GM.sf2", 16000).midi_to_audio(str(fname + '.mid'), str(fname + '.wav'))
Audio(str(fname + '.wav'), rate=16000)

"""# Congrats! You did it! :)"""