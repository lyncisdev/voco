# Setup instructions

building Kaldi

## tools:

sudo apt-get install libatlas3-base
sudo apt-get install zlib1g-dev automake autoconf libtool subversion


make

## SRC
complains about not finding ATLAS

Tried:
sudo apt-get install libatlas-base-dev

No luck

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


