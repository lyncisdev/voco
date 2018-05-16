#!/usr/bin/python


import re
import subprocess
import sys
import os


print(os.environ['VOCO_DATA'])

try:
    voco_data_base = os.environ['VOCO_DATA'] + "/audio_records/"
except:
    print('VOCO_DATA not defined')

################################ Create Lexicon

text_file = open(voco_data_base + 'text', 'r')
lexicon_file = open(voco_data_base + 'lexicon.txt', 'w')
corpus_file = open(voco_data_base + 'corpus.txt', 'w')

text_lines = text_file.readlines()

word_list = []
phones_list = []
corpus_list = []

for line in text_lines:
    parts = re.findall(r'\S+', line)
    word_list += parts[1:]

    phrase = ""
    for x in parts[1:]:
        phrase += "".join(x)
        phrase += " "
    corpus_list.append(phrase)

word_list = sorted(list(set(word_list)))
corpus_list = sorted(list(set(corpus_list)))

lexicon_file.write("!SIL sil" + "\n")
lexicon_file.write("<UNK> spn" + "\n")

for word in word_list:
    try:
        phones = subprocess.check_output(
            ['grep', "[[]" + word.upper() + "[]]", "VoxForgeDict"])
        phones = re.findall(r'\S+', phones)
        phones = phones[2:]
        phones_list += phones

        phrase = ""
        for x in phones:
            phrase += "".join(x)
            phrase += " "
        lexicon_file.write(word + " " + phrase + "\n")
    except:
        lexicon_file.write(
            word + " no dictionary entry found -----------------" + "\n")

for word in corpus_list:
    corpus_file.write(word + "\n")

################################ Create Lexicon
nonsilence_phones_file = open(voco_data_base + 'nonsilence_phones.txt', 'w')

phones_list = sorted(list(set(phones_list)))

for phone in phones_list:
    nonsilence_phones_file.write(phone + "\n")

silence_phones_file = open(voco_data_base + 'silence_phones.txt', 'w')
silence_phones_file.write("sil" + "\n")
silence_phones_file.write("spn" + "\n")

optional_silence_file = open(voco_data_base + 'optional_silence.txt', 'w')
optional_silence_file.write("sil" + "\n")
