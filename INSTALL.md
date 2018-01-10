# Setup instructions

building Kaldi

## tools:

sudo apt-get install libatlas3-base
sudo apt-get install zlib1g-dev automake autoconf libtool subversion


make

## SRC

./configure --shared

complains about not finding ATLAS

Tried:
sudo apt-get install libatlas-base-dev

trying to install openblas
tools/extras/install_openblas.sh

openblas requires fortran
sudo apt install gfortran

openblas installed sucessfully

cd to src

./configure  --openblas-root=../tools/OpenBLAS/install


completed sucessfully
make depend -j 2

make -j 2


# setting up voco

symlink steps and utils in training
linked from wsj


ln -s $KALDI_ROOT/egs/wsj/s5/steps $VOCO_ROOT/training/steps
ln -s $KALDI_ROOT/egs/wsj/s5/utils $VOCO_ROOT/training/utils


add $KALDI_ROOT AND $ VOCO_ROOT to ~/.bashrc
