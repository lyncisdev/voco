# Create your own speech recognition system for programming by voice

Voco allows you to create a Kaldi speech recognition system based on your own voice that will allow you to program by predominantly using your voice. This is intended for programmers who have developed RSI or have other injuries or disabilities and need to continue their work but are unable to use a traditional keyboard and mouse setup for extended periods of time. This software was developed to be used primarily with EMACS (Spacemacs with VIM emulation) as the modal navigation menus are crucial to its use).

Some examples of supported commands:
- "alpha bravo charlie" -> abc
- "switch firefox" -> show the Firefox window 
- "page down" -> page down
- "up three" -> up up up
- "jump three zero eight" -> move cursor to line 308 in emacs
- "jump india foxtrot" -> move cursor to "if" using evil-avy-goto-char in emacs 

## What is Voco

Voco packages the following things together:
1. A data creation module that helps you create a training set.
2. A Kaldi training script that trains a GMM model on the data you created.
3. A decoding module that records your voice when you speak, decodes it, parses it and executes the keystrokes on your computer.

## Why use Voco

By using a training set that is representive of what Voco will see during operation and by keeping the dictionary of possible words small Voco is able to provide the following advantages:

1. **Low error rates:**
By keeping the dictionary small (I am currently using ~90 possible commands) and by training on the microphone and noise profile that will be used during operation the system is able to achieve WER (word error rates) of ~0.5% and SER (sentence error rates) of ~1.35%. This is achieved with a low cost USB microphone (Platronics 628 USB) that has very poor signal sepperation. In my opinion these error rates are the mininum for a keyboard replacement system since anything higher results in frustration.

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

Once you have trained a model execute Python3 record_decode.py in the main direcotry to run voco.


## Customizing

### Adding a new word to the dictionary

1. Modify the commands.csv file to include the new word. 
2. Then execute data_creation/1_create_recording_list.py, this will randomly sample the commands list and create a "script" of phrases for you to say.
3. Executing 2_record.py will present you with the phrases generated above, one at a time, and ask you to say them.
4. You can then run 3_create_training_set.sh which will generate the files required by Kaldi to train your model.
5. Execute training/run.sh to train the model.

### Adding new rule 

Rules can either be static or dynamic. Static rules are phrases that execute a specific action when the phrase is said. For example, "open" opens a new window.\\
An example of a dynamic rule would be "sky Charlie" which should be equivalent to shift+c. You would want this rule to be generic and work for any letter of the alphabet. 

Static rules are defined in main/parser/static_rules.json.
Dynamic rules are defined in main/parser/dynamic_rules.json.
Comments in both the above files will help you write your own rules. each rule will also require an implementation function to be defined in main/parser/implementation.py

## Next steps:

Some features planned for the future:
1. Dictation mode, where the model can decode natural speech. Most likely based on the Aspire model.
2. True real time decoding, based on Kaldi's real time routines. Currently the model is working in "Batch mode", which is sufficient but not optimal.
3. Better support for Emacs snippets,

## Contact:
If you are using voco, would like to or have any questions, please email voco at lyncis dot co dot za]
