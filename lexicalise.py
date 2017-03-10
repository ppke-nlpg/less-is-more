#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# Lexicalise and generate input to a Tagger: WORD POS CHUNK -> WORD POS (WORD-POS-CHUNK|POS-CHUNK)
# Parameters:
#     a) data in 'WORD POS CHUNK' format (CoNLL-2000 format with any chunk type)
#     b) W_s set: one word per line (anything, but first column is ignored)
#     c) Lexicalization Type (default: Full):
#         c1) Full: if word in W_s than word+POS+chunk else POS+chunk
#             (as described in Molina, Antonio, and Ferran Pla. "Shallow parsing using specialized hmms."
#              The Journal of Machine Learning Research 2 (2002): 595-613.)
#         c2) Just words: if word in W_s than word+POS+chunk else chunk
#         c3) None: chunk (Nothing is done)
# Output: word pos-tag chunk-tag (format either words-pos words-pos-chunk or word pos pos-chunk or word pos chunk)
import sys

if len(sys.argv) == 1:
    print('USAGE: {0} data W_Set-file [--just-words|--none]'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

just_words = False
do_nothing = False
if len(sys.argv) > 3 and sys.argv[3] in {'--just-words', '--none'}:
    if sys.argv[3] == '--just-words':
        just_words = True
    else:
        do_nothing = True

data = sys.argv[1]
if sys.argv[1] == '-':
    data = sys.stdin

with open(data, encoding='UTF-8') as FP_origin,\
     open(sys.argv[2], encoding='UTF-8') as FP_lex:  # eg. train.iob2.wch

    if do_nothing:
        for line_origin in FP_origin:
            print(line_origin, end='')
    else:
        # -----Build set for selected words(lex)-----------
        lex = {line_lex.strip().split()[0] for line_lex in FP_lex if len(line_lex) > 1}

        # -----Build new trainning file--------------------
        for line_origin in FP_origin:
            words_origin = line_origin.strip().split()
            if len(words_origin) == 0:  # blank line
                print()
            else:
                words_origin_ch = words_origin[2].split('-')
                if words_origin_ch[0] != 'O' and '{0}-{1}'.format(words_origin[0], words_origin_ch[1]) in lex:
                    print(words_origin[0],  # Word 
                          words_origin[0] + '+' + words_origin[1],  # Word+POS-tag
                          words_origin[0] + '+' + words_origin[1] + '+' + words_origin[2])   # Word+POS-tag+IOB-label
                elif just_words:
                    print(words_origin[0],  # Word
                          words_origin[1],  # POS-tag
                          words_origin[2])  # IOB-label
                else:
                    print(words_origin[0],  # Word
                          words_origin[1],  # POS-tag
                          words_origin[1] + '+' + words_origin[2])  # POS-tag+IOB-label
