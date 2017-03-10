#!/bin/bash
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

realpath="`realpath $0`"
abspath="`dirname $realpath`"
huntagpath="$abspath/HunTag3/HunTag3/huntag.py"
huntagconfig="$abspath/HunTag3/HunTag3/configs/hunchunk.Just.krPatt.yaml"

if [ $# -ne 5 ]; then
     echo "USAGE: $0 train.file test.file output.file temp.dir pos.field  !" >&2
     exit 1
fi

trainfile="$1"
trainfileBase=`basename $1`
testfile="$2"
testfileBase=`basename $2`
outputfile="$3"
tempdir="$4"
posField="$5"  # Needed for cut
crfsuiteTrain="$testfileBase.CRFsuite-official.train"
crfsuiteTest="$testfileBase.CRFsuite-official.test"
crfmodel="$testfileBase.CRFsuite-official.CRFmodel"

# Featurize train
chunking.py < "$trainfile" > "$tempdir/$crfsuiteTrain"


# Featurize test
chunking.py < "$testfile" > "$tempdir/$crfsuiteTest"

crfsuite learn -m "$tempdir/$crfmodel" "$tempdir/$crfsuiteTrain"

crfsuite tag -m "$tempdir/$crfmodel" "$tempdir/$crfsuiteTest" | paste -d' ' "$testfile" - | sed 's/^ *$//' > "$outputfile"
