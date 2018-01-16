#!/bin/bash

# echo 'export KALDI_ROOT=~/proj/kaldi' >> ~/.bashrc
# echo 'export VOCO_ROOT=~/proj/voco' >> ~/.bashrc
# echo 'export VOCO_DATA=~/proj/voco/data' >> ~/.bashrc
# . ~/.bashrc

# cat | echo $VOCO_ROOT

# rm $VOCO_ROOT/training/steps
# rm $VOCO_ROOT/training/utils

# rm -R $VOCO_ROOT/data
# rm $VOCO_ROOT/training/data
# rm $VOCO_ROOT/main/decode/model
# rm $VOCO_ROOT/main/decode/data

# ln -s $KALDI_ROOT/egs/wsj/s5/steps $VOCO_ROOT/training/steps
# ln -s $KALDI_ROOT/egs/wsj/s5/utils $VOCO_ROOT/training/utils


# mkdir -p $VOCO_ROOT/data/data
# mkdir -p $VOCO_ROOT/data/staging/audio_records
# mkdir -p $VOCO_ROOT/data/staging/audio_data

# ln -s $VOCO_ROOT/data/data $VOCO_ROOT/training/data
# ln -s $VOCO_ROOT/training/exp/tri1_ali $VOCO_ROOT/main/decode/model
# ln -s $VOCO_ROOT/data/staging $VOCO_ROOT/main/decode/data

# curl https://raw.githubusercontent.com/VoxForge/develop/master/lexicon/VoxForgeDict.txt > $VOCO_ROOT/data_creation/VoxForgeDict


# sudo apt install keynav
sudo apt install libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg libav-tools
pip install pyaudio

pip install numpy
