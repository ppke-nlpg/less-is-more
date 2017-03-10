#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# Select the words that belong to certain chunks such as SBAR,PP and VP with
# high frequency in the trainning set
# Options: Frequency, POS-RE
# Input: original trainning data and converted file
# Output: frequency table (format: word-chunkType frequency)

import argparse
import sys
import re
from collections import Counter
from operator import itemgetter


def check_args(args=None):
    parser = argparse.ArgumentParser(description='Select the words that belong to certain chunks such as SBAR,PP and VP\
                                                  with high frequency in the trainning set')
    parser.add_argument('-i', '--inp',
                        help='data file for input',
                        required=True)
    parser.add_argument('-f', '--freq',
                        help='minimum frequency', type=int,
                        default=50)
    parser.add_argument('-o', '--out',
                        help='output file pattern ("NUMBER" will be substituted): wch.devel.NUMBER.txt ->\
                        wch.devel.1.txt, wch.devel.2.txt ...',
                        required=True)
    parser.add_argument('-r', '--re',
                        help='chunktype  RE',
                        default='(NP|PP|VP|ADVP)$')  # AD(VP)

    results = parser.parse_args(args)

    return (results.inp,
            results.freq,
            results.out,
            results.re)


def make_freq_table(f, freq, outputfile, rex):
    seen = Counter()
    for line in f:
        line = line.strip()
        fields = line.split()
        if 1 < len(fields) <= 3 and fields[2] != 'O':
            _, chunk_type = fields[2].split('-')  # with words that may contain hypen...
            temp = fields[0] + '-' + chunk_type
            seen[temp] += 1

    # filter
    seen = [(k, v) for k, v in sorted(seen.items(), key=itemgetter(1), reverse=True)
            if v >= freq and regEx.search(k)]

    if len(seen) > 0:
        for f in range(freq, seen[0][1]):
            with open(outputfile.replace('NUMBER', str(f)), 'w', encoding='UTF-8') as fh:
                for k, v in seen:
                    if v >= f:
                        print(k, v, file=fh)
                    else:
                        break
    else:
        print("No element to write!", file=sys.stderr)

if __name__ == '__main__':

    data, freq, outputfile, rex = check_args(sys.argv[1:])
    regEx = re.compile(rex)

    if data == '-':
        data = sys.stdin
        make_freq_table(data, freq, outputfile, rex)
    else:
        with open(data, encoding='UTF-8') as f:
            make_freq_table(f, freq, outputfile, rex)
