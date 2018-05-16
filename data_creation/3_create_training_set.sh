#!/bin/bash

rm -R $VOCO_DATA/data
python create_lang_files.py
python create_test_train.py
