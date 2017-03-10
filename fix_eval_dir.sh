#!/bin/bash
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

realpath="`realpath $0`"
abspath="`dirname $realpath`"

# Colors: http://stackoverflow.com/a/5947802
LBLUE='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

if [ $# -lt 4 ]; then
     echo 'Fix IOB tagging and Eval with eval.pl !' 
     echo "USAGE: $0 input.format delex.file.suffix output.file.suffix input.dir.glob" >&2
     echo 'Valid labelsets: IOB1, IOB2, IOE1, IOE2, IOBES !' >&2
     exit 1
fi

inputFormat=$1
delexSuffix=$2
outputSuffix=$3
shift
shift
shift
rm -f result_$inputFormat.txt
for file in "$@"; do
    baseDelexName="`basename $file$delexSuffix`"
    printf "${LBLUE}"
    echo "Runing $abspath/delexicalise.py $file > $abspath/temp/$baseDelexName"
    printf "${NC}"
    $abspath/delexicalise.py $file > $abspath/temp/$baseDelexName
    if [ $? -eq 0 ]; then printf "${GREEN}Done!${NC}"; echo; else exit $?; fi

    printf "${LBLUE}"
    echo "Runing $abspath/fix_tagging.sh $inputFormat $abspath/temp/$baseDelexName $file$outputSuffix :"
    printf "${NC}"
    $abspath/fix_tagging.sh $inputFormat $abspath/temp/$baseDelexName $file$outputSuffix
    if [ $? -eq 0 ]; then printf "${GREEN}Done!${NC}"; echo; else exit $?; fi

    baseOutputFile=`basename $file$outputSuffix`
    echo "$baseOutputFile" >> result_$inputFormat.txt
    cat $file$outputSuffix | $abspath/conlleval.pl >> result_$inputFormat.txt
    echo "" >> result_$inputFormat.txt
done