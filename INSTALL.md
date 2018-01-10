# Starting point
Start here to install and configure Voco on a fresh installation of Ubuntu 17.10. I 


## i3wm
I'm using i3wm [https://i3wm.org/screenshots/](Screenshots) which is a great option for a keyboard only window manager. if you decide to use it the tutorial is located [https://i3wm.org/docs/userguide.html](here).

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




# Installing and configuring Voco
## Final directory structure

note: replace with tree command output

- Kaldi [kaldi_root]
    - tools
    - src
- Silvius
    - grammar (where the grammar parser lives) 
    - stream 
- Voco [voco_root]
    - data [where all data related to your model lives]
        - audio_data [audio files that will be trained on]
        - audio_records [supporting files, in Kaldi format, describing the above audio files]
        - data [training data conforming to structure required by Kaldi]
        - staging [audio files and records still to be reviewed from live recording]
    - data_creation [module that creates your training set]
        - commands.csv [list of the commands you want to use]
        - create_recording_list.py [converts commands.csv to recording list]
        - record.py [does the actual recording]
        - create_dataset.sh [creates the voco\training\data directory]
    - training [Kaldi training recipe]
        - run.sh [runs the training]
        - exp\tri1_ali [final trained model]
    - main [decoder module]
        - record_decode.py [the script that runs the decoder]
    - parse_log
        - log [logfile you want to parse]
        - parse_log.py
        - parse_counter.txt [saves the linenumber of the last processed entry in log]
    


## Setting environment variables

add $KALDI_ROOT, $VOCO_ROOT, $VOCO_DATA to ~/.bashrc

## Compiling Kaldi

For a crash course check out: http://kaldi-asr.org/doc/kaldi_for_dummies.html
But be warned, Kaldi is more of a research project than a finished user friendly program. Dont delve too deep unless you need to.



### clone the Kaldi repository

```bashrc
git clone https://github.com/kaldi-asr/kaldi.git kaldi --origin upstream
```

### tools


```bash
cd $KALDI_ROOT/tools
sudo apt-get install libatlas3-base
sudo apt-get install zlib1g-dev automake autoconf libtool subversion
make
```

### src

```bash
cd $KALDI_ROOT/src
./configure --shared
```

The config file complains about not finding ATLAS

I tried ```sudo apt-get install libatlas-base-dev``` but it didnt help

Therefore try to install openblas:

```bash
cd $KALDI_ROOT/tools
sudo apt install gfortran
tools/extras/install_openblas.sh
```

Openblas installed sucessfully.  

Now compile Kaldi

```bash
cd $KALDI_ROOT/src
./configure  --openblas-root=../tools/OpenBLAS/install
make depend -j 2
make -j 2
```

## Setting up Voco

Clone the Voco repository:

```bash
git clone https://github.com/lyncisdev/voco.git
```

Set up symlinks for the steps and utils directories in the WSJ recipe:

```bash
ln -s $KALDI_ROOT/egs/wsj/s5/steps $VOCO_ROOT/training/steps
ln -s $KALDI_ROOT/egs/wsj/s5/utils $VOCO_ROOT/training/utils
```


You will need to get the VoxForge phone dictionary (which maps words to their phonetic representation) from the VoxForge github repository (https://github.com/VoxForge/develop/lexicon)

```bash
curl https://raw.githubusercontent.com/VoxForge/develop/master/lexicon/VoxForgeDict.txt > $VOCO_ROOT/data_creation/VoxForgeDict
```



voco_data directory:
should this just be taken from the data_base


## Other 

### Keynav
Keynav is the Keyboard emulation program that actually executes the keystrokes on your computer.

To install Keynav in Ubuntu or Debian execute:
```bash
sudo apt install keynav
```


You can find more information on Keynav at: http://www.semicomplete.com/projects/keynav

### Rofi

Task switcher that is started with the "switch" command. "Switch window" just presses "alt + tab"

To install rofi in Ubuntu or Debian execute:
```bash
sudo apt install rofi
```

You can find more information on Rofi at: https://github.com/DaveDavenport/rofi

