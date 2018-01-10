# Create your own speech recognition system for programming by voice

Voco allows you to create a Kaldi speech recognition system based on your own voice that will allow you to program by predominantly using your voice. This is intended for programmers who have developed RSI or have other injuries or disabilities and need to continue their work but are unable to use a traditional keyboard and mouse setup for extended periods of time. This software was developed to be used primarily with EMACS (Spacemacs with VIM emulation) as the modal navigation menus are crucial to its use).

Some examples of supported commands:
- "alpha bravo charlie" -> abc
- "switch window" -> alt + tab
- "page down" -> page down
- "up three" -> up up up
- "jump three zero eight" -> move cursor to line 308 in emacs
- "jump india foxtrot" -> move cursor to "if" using evil-avy-goto-char in emacs 

## What is Voco

Voco packages the following things together:
1. A data creation module that helps you create a training set
2. A Kaldi training script that trains a GMM model on the data you created
3. A decoding module that records your voice when you speak, decodes it, parses it and executes the keystrokes on your computer

## Why use Voco

By using Da training set that is representive of what Voco will see during operation and by keeping the dictionary of possible words small Voco is able to provide the following advantages:

1. **Low error rates:**
By keeping the dictionary small (I am using 86 possible commands) and by training on the microphone and noise profile that will be used during operation the system is able to achieve WER (word error rates) of ~0.5% and SER (sentence error rates) of ~1.35%. This is achieved with a low cost USB microphone (Platronics XXX) that has a unipressive XXX dB of signal sepperation. In my opinion these error rates are the mininum for a keyboard replacement system since anything higher results in frustration.

2. **Low latency and low recourse utilization:**
Since the model is small the system does not require much processing power to decode samples and samples are decoded *almost* in real time (<500ms). This system runs in the background on a Thinkpad T420 with 8GB Ram and and i5-2540M (Geekbench Multicore score of ~5000) while programming with no appreciable performance issues. In addition, since the model is small a "first draft" can be trained on just 500 samples and re-trained on correctly decoded samples creaded during operation. 

3. **Easy to modify:**
The entire system is written in Python and can easily be modified to suit your particular needs. Voco comes with enough commands to get you started but if you would like to add any custom commands, see [Customizing](#customizing) below.


## Based on Kaldi and Silvius
This work is based on the Kaldi speech recognition system and the Silvius grammar parser. My thanks to David Williams-King and Tavis Rudd for discussing how they dealt with not being able to use a keyboard and sharing their solutions. I developed this system, based on theirs, when I developed RSI and needed a low error, low resource and easy to customize replacement for my keyboard.


Coding by Voice with Open Source Speech Recognition - https://www.youtube.com/watch?v=YRyYIIFKsdU  
Using Python to Code by Voice - https://www.youtube.com/watch?v=8SkdfdXWYaI  

Related links:
- Kaldi: http://kaldi-asr.org/
- Silvius: http://voxhub.io/silvius


## Install instructions:

See INSTALL.md

## How to use Voco
### Create the training dataset


### Train a GMM based Kaldi model


copy model

### Use the system

setup KALDI_ROOT in path file

### Improve results by adding previously decoded samples

## Customizing

### Adding a new word to the dictionary

Modify the commands.csv file to include the new word. If you already have a training dataset then increase the frequency of the new word so that it is sampled more frequently in the recording list. Then follow the same process as with training your first model.

TODO: check if word is in VoxForgeDict

### Linking a word to a command

All commands that are not supported by Silvius are handled by the process_line.py file. Commands starting with a keyword contained in the Escape_keywords dictionary are handled by functions withing process_line.py and all others are passed to Silvius. Escape keywords are mapped to functions by function_dict.

## Next steps:

Some features planned for the future:
1. Dictation mode, where the model can decode natural speech. Most likely based on Kaldi's Aspire model.
2. True real time decoding, based on Kaldi's real time routines. Currently the model is working in "Batch mode", which is sufficient but not optimal.
3. Better support for Emacs snippets 

## Contact:
If you are using voco, would like to or have any questions, please email [lyncisdev at gmail dot com]


# TODO


remove backup models  
remove   
scripts/int2sym  

symlink from training decore to main model  to   


symlink training steps an utils
