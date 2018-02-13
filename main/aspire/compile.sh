#!/usr/bin/env bash


cp /home/lyncis/proj/voco/main/aspire/online-wav-nnet3-latgen-faster.cc /home/lyncis/proj/kaldi/src/online2bin/
cd /home/lyncis/proj/kaldi/src/online2bin/
make online-wav-nnet3-latgen-faster

cd /home/lyncis/proj/voco/main/aspire/
