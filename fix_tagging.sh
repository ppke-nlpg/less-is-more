#!/bin/bash
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

realpath="`realpath $0`"
abspath="`dirname $realpath`"

# Colors: http://stackoverflow.com/a/5947802
LBLUE='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

declare -A converters=(
#[balazs]='conv_iob_balazs'
# [pisti]='conv_iob_pisti'
#[ss05]='conv_iob_ss05'
[corenlp]='conv_iob_corenlp'
)

if [ $# -ne 3 ]; then
     echo 'Fix IOB tagging, by converting to the input format by CoreNLP !' 
     echo "USAGE: $0 input.format input.file output.file" >&2
     echo 'Valid labelsets: IOB1, IOB2, IOE1, IOE2, IOBES, OC !' >&2
     exit 1
fi

inputFormat=$1
inputFile=$2
baseInputFile=`basename $2`
outputFile=$3
baseOutputFile=`basename  $3`

# Prepare input
cut -d' ' -f1,2,4 $inputFile > "$abspath/temp/$baseInputFile.temp"
# Actual conversion (From input to input tagset)
$abspath/converters/${converters[corenlp]}/run.sh $inputFormat $inputFormat "$abspath/temp/$baseInputFile.temp" "$abspath/temp/$baseInputFile.temp.fixed" --fix
res=$?
if [ $res -eq 1 -o $res -gt 2 ]; then exit $?; fi
# Put parts together (token POS GOLD AUTO.FIXED)
echo "Running cut -d' ' -f3 \"$abspath/temp/$baseInputFile.temp.fixed\" | paste -d' ' <(cut -d' ' -f1-3 $inputFile) - | sed 's/^ $//' > $outputFile :"
cut -d' ' -f3 "$abspath/temp/$baseInputFile.temp.fixed" | paste -d' ' <(cut -d' ' -f1-3 $inputFile) - | sed 's/^ $//' > $outputFile
