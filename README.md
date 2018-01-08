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
The entire system is written in Python and 


## Based on Kaldi and Silvius
This work is based on the Kaldi speech recognition system and the Silvius grammar parser. My thanks to David Williams-King and Tavis Rudd for discussing how they dealt with not being able to use a keyboard and sharing their solutions. I developed this system, based on theirs, when I developed RSI and needed a low error, low resource and easy to customize replacement for my keyboard.


Coding by Voice with Open Source Speech Recognition - https://www.youtube.com/watch?v=YRyYIIFKsdU  
Using Python to Code by Voice - https://www.youtube.com/watch?v=8SkdfdXWYaI  

Related links:
- Kaldi: http://kaldi-asr.org/
- Silvius: http://voxhub.io/silvius


## Prerequisites:

### Cloning Voco

Clone the Voco by issuing the following command:
```bash
git clone https://github.com/lyncisdev/voco.git
```

### Cloning Silvius
My version of Silvius is currently bundled in the git repository. The plan is to push the changes to the Silvius repository and use the latest version of Silvius.

### Installing Kaldi:

To clone Kaldi execute the following command:

```bash
git clone https://github.com/kaldi-asr/kaldi.git kaldi --origin upstream
```

1. Go to kaldi/tools/ and follow INSTALL instructions there.

2. Go to kaldi/src/ and follow INSTALL instructions there.


For a crash course check out: http://kaldi-asr.org/doc/kaldi_for_dummies.html
But be warned, Kaldi is more of a research project than a finished user friendly program. Dont delve too deep unless you need to.

### Installing openFSTR:


### Downloading VoxForgeDict:
You will need to get the VoxForge phone dictionary (which maps words to their phonetic representation) from the VoxForge github repository (https://github.com/VoxForge/develop/lexicon)

```bash
curl https://raw.githubusercontent.com/VoxForge/develop/master/lexicon/VoxForgeDict.txt > VOCO_BASE\data_creation\VoxForgeDict
```
Where ```VOCO_BASE``` is the root of the voco directory

### Emacs with Spacemacs
Emacs is a text editor / IDE (depending who you ask) that is well suited to voice operation since all commands are accessible via the keyboard. Spacemacs is an addon layer for Emacs that makes it prettier and easier to use.  

To install EMACS in ubuntu or debian execute:
```bash
sudo apt install emacs
```

Then to install Spacemacs:
```bash
git clone https://github.com/syl20bnr/spacemacs ~/.emacs.d
```

When you start emacs the first time it will ask you to choose a kayboard style, choose "EVIL mode". 

You can find more information about Spacemacs at http://spacemacs.org/


### Keynav
Keynav is the Keyboard emulation program that actually executes the keystrokes on your computer.

To install Keynav in Ubuntu or Debian execute:
```bash
sudo apt install keynav
```


You can find more information on Keynav at: http://www.semicomplete.com/projects/keynav

### Rofi




### Python libraries

### symlink decode/data 

should this just be taken from the data_base



### Final direcotry structure

Base Directory

- Kaldi [kaldi_root]
    - tools
    - src
- Silvius
    - grammar (where the grammar parser lives) 
    - stream 
- Voco [voco_root]
    - data [where all data related to your model lives]
    - data_creation [module that creates your training set]
    - main [decoder module]
    - parse_log 
    - training [training module]







## How to use Voco
### Create the training dataset


### Train a GMM based Kaldi model


copy model

### Use the system

setup KALDI_ROOT in path file

### Improve results by adding previously decoded samples



## Limitations:

## Next steps:


## Contact:

# TODO


remove backup models  
remove   
scripts/int2sym  

symlink from training decore to main model  to   


symlink training steps an utils
