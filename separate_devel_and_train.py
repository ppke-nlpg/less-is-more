#!/usr/bin/python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# Create development and training sets from the original training set: "Every 10th sentence is the development set..."
# Parameters:
#     a) Original train.txt CoNLL-2000 format
#     b) Development set name (devel.txt)
#     c) New training set (train_new.txt)
# Output: The two files with respect to "Every 10th sentence is the development set..."
import sys

if len(sys.argv) != 4:
    print('USAGE: {0} train.txt devel.txt train_new.txt'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

sent_count = 1

with open(sys.argv[1], encoding='UTF-8') as FP_train, open(sys.argv[2], 'w', encoding='UTF-8') as FP_devel,\
     open(sys.argv[3], 'w', encoding='UTF-8') as FP_train_new:
    for l in FP_train:
        if sent_count % 10 != 0:  # Every 10th sentence is omited from train_new
            FP = FP_train_new
        else:
            FP = FP_devel
        if len(l) > 1:  # Every empty line is a start of a new sentence
            print(l, end='', file=FP)
        else:
            sent_count += 1
            print(file=FP)
