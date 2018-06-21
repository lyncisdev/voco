

wget -O - https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz | tar xvfz -


virtualenv -p python3 ~/proj/deepspeech-venv/
source ~/proj/deepspeech-venv/bin/activate
pip3 install deepspeech
pip3 install --upgrade deepspeech


deepspeech models/output_graph.pb test.wav models/alphabet.txt models/lm.binary models/trie
