#!/usr/bin/env python3
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

import sys
from collections import defaultdict

output = defaultdict(dict)
with open(sys.argv[1]) as fh:
    for line in fh:
        line = line.rstrip()
        if line.startswith('devel.txt') or line.startswith('test.txt'):
            line_parts = line.split('.')
            data_type = line_parts[0]
            representation = line_parts[4]
            lex_type = line_parts[6]

            lex_level = line_parts[7]
            outfile = representation + '_' + data_type + '_' + lex_type
        elif line.startswith('accuracy:'):
            f1 = line.split('  ')[4]
            output[outfile][int(lex_level)] = f1
        else:
            continue

for k,v in output.items():
    with open(k + '.txt','w') as of:
        for level, f1 in sorted(v.items(), key=lambda x: x[0]):
            print(level, f1, file=of)
