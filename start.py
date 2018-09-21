#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import argparse
import sys
import re
import os
import subprocess
from collections import Counter
import datetime
import socket


def check_args(args=None):
    parser = argparse.ArgumentParser(description='Lexicalise, train, test, fix, delexicalise, eval')
    parser.add_argument('-t', '--train', help='data file for train', required=True)
    parser.add_argument('-m', '--test', help='data file for test', required=True)
    parser.add_argument('-f', '--freq', help='frequency', type=int, required=True)
    parser.add_argument('-o', '--out', help='result file (conlleval.pl output)', required=True)
    parser.add_argument('-r', '--re', help='chunktype  RE', default='(NP|PP|VP|ADVP)$')  # AD(VP)

    results = parser.parse_args(args)

    return results.train, results.test, results.freq, results.out, results.re


def make_freq_table(data, freq, outputfile, rex):
    """
    # Select the words that belong to certain chunks such as SBAR,PP and VP with
    # high frequency in the trainning set
    # Options: Frequency, POS-RE
    # Input: original trainning data and converted file
    # Output: frequency table (format: word-chunkType frequency or word frequency)
    """
    regex = None
    if rex != '':
        regex = re.compile(rex)

    seen = Counter()
    with open(data, encoding='UTF-8') as fh:
        for line in fh:
            if len(line) > 1:
                line = line.strip()
                fields = line.split()
                if regex:  # If there is gold standard annotation use chunk type else regex should be empty
                    if 1 < len(fields) <= 3 and fields[2] != 'O':
                        _, chunk_type = fields[2].split('-')  # with words that may contain hypen...
                        temp = fields[0] + '-' + chunk_type
                        seen[temp] += 1
                else:
                    temp = fields[0]
                    seen[temp] += 1

    # filter
    seen = [(k, v) for k, v in seen.most_common() if v >= freq and (regex is None or regex.search(k))]

    if len(seen) > 0:
        with open(outputfile.replace('NUMBER', str(freq)), 'w', encoding='UTF-8') as fh:
            for k, v in seen:
                print(k, v, file=fh)
    else:
        print("No element to write!", file=sys.stderr)


def lexicalise(data, lex_wordsfile, outputfile, level='none', chunk_regex=''):
    """
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
    """
    regex = None
    if chunk_regex != '':
        regex = re.compile(chunk_regex)

    with open(data, encoding='UTF-8') as original_data, \
            open(lex_wordsfile, encoding='UTF-8') as lex_words, \
            open(outputfile, 'w', encoding='UTF-8') as outfile:

        if level == 'none':  # Do nothing
            for line_origin in original_data:
                print(line_origin, end='', file=outfile)
        else:
            # -----Build set for selected words(lex)-----------
            lex = {line_lex.strip().split()[0] for line_lex in lex_words if len(line_lex) > 1}

            # -----Build new trainning file--------------------
            words_origin = ''
            for i, line_origin in enumerate(original_data):
                words_origin = line_origin.strip().split()
                if len(words_origin) == 0:  # blank line
                    print(file=outfile)
                else:
                    words_origin_ch = words_origin[2].split('-')
                    if level == 'Full':
                        if (words_origin_ch[0] != 'O' and '{0}-{1}'.format(words_origin[0], words_origin_ch[1]) in lex)\
                                or (words_origin[0] in lex and (regex is None or regex.match(words_origin_ch[1]))):
                            print(words_origin[0],  # Word
                                  words_origin[0] + '+' + words_origin[1],  # Word+POS-tag
                                  words_origin[0] + '+' + words_origin[1] + '+' + words_origin[2],  # Word+POS-tag+IOB
                                  file=outfile)
                        else:
                            print(words_origin[0],  # Word
                                  words_origin[1],  # POS-tag
                                  words_origin[1] + '+' + words_origin[2],  # POS-tag+IOB-label
                                  file=outfile)
                    elif level == 'Just words':
                        if (words_origin_ch[0] != 'O' and '{0}-{1}'.format(words_origin[0], words_origin_ch[1]) in lex)\
                                or (words_origin[0] in lex and (regex is None or regex.match(words_origin_ch[1]))):
                            print(words_origin[0],  # Word
                                  words_origin[0] + '+' + words_origin[1],  # Word+POS-tag
                                  words_origin[0] + '+' + words_origin[1] + '+' + words_origin[2],  # Word+POS-tag+IOB
                                  file=outfile)
                        else:
                            print(words_origin[0],  # Word
                                  words_origin[1],  # POS-tag
                                  words_origin[2], file=outfile)  # IOB-label
                    else:
                        print('ERROR: Lexicalisation level malformed:', level, file=sys.stderr)
            if len(words_origin) > 0:  # Last line is not blank line -> Add a blank line
                print(file=outfile)


def prepare_chunking(data, outputfile):
    with open(data) as infile, open(outputfile, "w") as outfile:
        subprocess.run('./utils/chunking.py', stdin=infile, stdout=outfile)


def train_tag(data_featurized, test_featurized, test, outputfile, model_file, log_file):
    with open(log_file, 'wb') as logfile:
        subprocess.run(['crfsuite', 'learn', '-m', model_file, data_featurized], stdout=logfile)
    ret = subprocess.run(['crfsuite', 'tag', '-m', model_file, test_featurized], stdout=subprocess.PIPE)
    with open(test, encoding='UTF-8') as testfile, open(outputfile, 'w', encoding='UTF-8') as outfile:
        for d, t in zip(testfile, ret.stdout.decode('UTF-8').split('\n')):
            if len(d) > 1:
                print(d.strip(), t, file=outfile)
            else:
                print(file=outfile)


def delexicalise(data, outputfile, column=-3, sep='+'):
    """
    # Delexicalise (remove everything before the separator character (+) from the specified column (-3))
    # Input: Tagged file last column (or else it specified in the commandline arguments)
    #        is the chunk separated by '+' or specified separator.
    # Output: Input line with stripped chunk
    """
    with open(data, encoding='UTF-8') as infile, open(outputfile, 'w', encoding='UTF-8') as outfile:
        for line in infile:
            words = line.strip().split()
            if len(words) == 0:  # blank line
                print(file=outfile)
            else:
                words[column:] = [elem.split(sep)[-1] for elem in words[column:]]  # Last part of chunk
                print(' '.join(words), file=outfile)


def fix_tags(data, outputfile, tempfile_name, tempoutfile_name):
    with open(data, encoding='UTF-8') as infile, open(tempfile_name, 'w', encoding='UTF-8') as tempfile:
        for line in infile:
            if len(line) > 1:
                word, pos, _, auto = line.strip().split()
                print(word, pos, auto, file=tempfile)
            else:
                print(file=tempfile)

    subprocess.run(['./utils/conv_iob_corenlp/conv_iob_corenlp.sh',
                    'IOBES', 'IOBES', tempfile_name, tempoutfile_name, '--fix'])

    with open(tempoutfile_name, encoding='UTF-8') as tempoutfile, open(data, encoding='UTF-8') as infile, \
            open(outputfile, 'w', encoding='UTF-8') as outfile:
        for temp_line, in_line in zip(tempoutfile, infile):
            if len(temp_line) > 1:
                word, pos, auto = temp_line.strip().split()
                _, _, gold, _ = in_line.strip().split()
                print(word, pos, gold, auto, file=outfile)
            else:
                print(file=outfile)


def conll_eval(data, outputfile):
    with open(data) as infile, open(outputfile, 'wb') as outfile:
        subprocess.run(['./utils/conlleval.pl'],
                       stdin=infile, stdout=outfile)


def print_result(train, test, freq, output_deatiled):
    fscore = 0.00
    with open(output_deatiled, encoding='UTF-8') as outfile:
        for line in outfile:
            if line.startswith('accuracy:'):
                fscore = line.split('  ')[4]
                break

    print(train, test, freq, fscore)


def main(train, test, freq, out, rex):
    abs_path = os.getcwd()
    train = os.path.join(abs_path, 'train', train)
    test = os.path.join(abs_path, 'test', test)
    devel = os.path.join(abs_path, 'train', train).replace('train_new', 'devel').replace('train', 'devel')
    lex_wordsfile = '{0}/{1}/{2}.{3}.wch'.format(abs_path, 'freq_tables', os.path.basename(devel), freq)

    train_lex = '{0}/{1}/{2}.{3}.{4}.lex'.format(abs_path, 'lexicalised', os.path.basename(train),
                                                 os.path.basename(lex_wordsfile), freq)
    test_lex = '{0}/{1}/{2}.{3}.{4}.lex'.format(abs_path, 'lexicalised', os.path.basename(test),
                                                os.path.basename(lex_wordsfile), freq)

    train_featurized = '{0}/{1}/{2}.train'.format(abs_path, 'featurized', os.path.basename(train_lex))
    test_featurized = '{0}/{1}/{2}.test'.format(abs_path, 'featurized', os.path.basename(test_lex))

    test_tagged = '{0}/{1}/{2}.tagged'.format(abs_path, 'tagged', os.path.basename(test_lex))
    model = '{0}/{1}/{2}.model'.format(abs_path, 'tagged', os.path.basename(train_lex))
    logfile = '{0}.log'.format(model)
    test_delex = '{0}/{1}/{2}.delex'.format(abs_path, 'delex', os.path.basename(test_tagged))
    test_fixed = '{0}/{1}/{2}.fixed'.format(abs_path, 'fixed', os.path.basename(test_delex))
    tempfn = '{0}.temp'.format(test_delex)
    tempoutfn = '{0}.out.temp'.format(test_delex)
    out_detailed = '{0}/{1}/{2}.detailed'.format(abs_path, 'out', os.path.basename(out))

    make_freq_table(devel, freq, lex_wordsfile, rex)

    lexicalise(train, lex_wordsfile, train_lex, level='Just words', chunk_regex=rex)
    lexicalise(test, lex_wordsfile, test_lex, level='Just words')  # NEVER USE THE GOLD ANNOTATION DURING MEASUREMENT!

    prepare_chunking(train_lex, train_featurized)
    prepare_chunking(test_lex, test_featurized)

    print('XXX TRAIN start', socket.gethostname(), datetime.datetime.now(), train, test, freq, flush=True)
    train_tag(train_featurized, test_featurized, test_lex, test_tagged, model, logfile)
    print('XXX TRAIN stop', socket.gethostname(), datetime.datetime.now(), train, test, freq, flush=True)

    print('XXX DELEX start', socket.gethostname(), datetime.datetime.now(), train, test, freq, flush=True)
    delexicalise(test_tagged, test_delex)
    print('XXX DELEX stop', socket.gethostname(), datetime.datetime.now(), train, test, freq, flush=True)

    fix_tags(test_delex, test_fixed, tempfn, tempoutfn)

    conll_eval(test_fixed, out_detailed)

    print_result(train, test, freq, out_detailed)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        cli_args = sys.argv[1:]
    else:
        cli_args = sys.argv[1].split()   # GNU parallel pastes parameters quoted
    main(*check_args(cli_args))
