#!/bin/bash
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

# Stanford CoreNLP source: https://github.com/stanfordnlp/CoreNLP/blob/master/src/edu/stanford/nlp/sequences/IOBUtils.java

realpath="`realpath $0`"
abspath="`dirname $realpath`"
LIBS=".:$abspath/stanford-corenlp-3.5.2.jar:$abspath/iobUtilsTest.jar"

# Compile main (need java 1.8)
# javac -cp "$LIBS" Test.java
# Run main (need java 1.8)
# java -cp "$LIBS:iobUtilsTest.jar" nlpTest.Test  -f test.iob2.txt  -outlabel ioe2 > result

if [ $# -lt 4 ]; then
     echo "USAGE: $0 from.format to.format input.file output.file" >&2
     echo 'Valid labelsets: IOB1, IOB2 or BIO, IOE1, IOE2, IO, SBIEO or IOBES, BILOU, NOPREFIX !' >&2
     exit 1
fi

fromFormat="$1"
toFormat="$2"
inputFile="$3"
outputFile="$4"

if [ "$fromFormat" == "$toFormat" -a "$5" != "--fix" ]; then
     echo "Validating not supported !" >&2
     exit 2
fi

if [ "$toFormat" == 'O+C' -o "$toFormat" == 'OC' ]; then
        echo 'Please do not ask such thing (valid labelsets: IOB1, IOB2 or BIO, IOE1, IOE2, IO, SBIEO or IOBES, BILOU, NOPREFIX)!' >&2
    exit 2
fi

java -cp "$LIBS" nlpTest.Test -f "$inputFile" -outlabel "$toFormat" > "$outputFile"
