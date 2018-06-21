#!/bin/bash
source ~/proj/deepspeech-venv/bin/activate
cd ~/proj/deepspeech
value=$(<audio.txt)
echo "$value"
deepspeech models/output_graph.pb $value models/alphabet.txt models/lm.binary models/trie
deactivate
