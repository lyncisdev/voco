# Kaldi

git clone https://github.com/kaldi-asr/kaldi.git kaldi --origin upstream

# Starting point

clean install of Ubuntu 17.10



# general tools
## i3wm


## Emacs and Spacemacs



# Installing and configuring Voco
## Directory structure


## Setting environment variables

add $KALDI_ROOT AND $ VOCO_ROOT to ~/.bashrc

## Kaldi

### tools:


```bash
cd $KALDI_ROOT/tools
sudo apt-get install libatlas3-base
sudo apt-get install zlib1g-dev automake autoconf libtool subversion
make
```

### SRC

```bash


```


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

## setting up voco

Clone the Voco repository:

```bash
git clone https://github.com/lyncisdev/voco.git
```

Set up symlinks for the steps and utils directories in the WSJ recipe:

```bash
ln -s $KALDI_ROOT/egs/wsj/s5/steps $VOCO_ROOT/training/steps
ln -s $KALDI_ROOT/egs/wsj/s5/utils $VOCO_ROOT/training/utils
```

Download VoxForgeDict:

```bash
curl https://raw.githubusercontent.com/VoxForge/develop/master/lexicon/VoxForgeDict.txt > $VOCO_ROOT/data_creation/VoxForgeDict
```
## Other 

Install Keynav and Rofi

```bash
sudo apt install keynav rofi
```


