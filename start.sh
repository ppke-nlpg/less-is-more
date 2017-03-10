#!/bin/bash
# -*- coding: utf-8, vim: expandtab:ts=4 -*-

realpath="`realpath $0`"
abspath="`dirname $realpath`"

# Colors: http://stackoverflow.com/a/5947802
LBLUE='\033[1;34m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color


# Clean up
./clean.sh

# Avoid crash (CRFSuite don't like :, TNT don't like %)
cat ./data/train.txt | sed -e 's/:/__COLON__/g' -e 's/%/__PERCENT__/g' > train_safe.txt
cat ./data/test.txt  | sed -e 's/:/__COLON__/g' -e 's/%/__PERCENT__/g' > test.txt


# Make devel set and training set from training set...
./separate_devel_and_train.py train_safe.txt devel.txt train_new.txt

# Choose this sufficiently low...
min=10

# Select corpus, to gather freqent words
for corp in "devel.txt" "test.txt"
do
    corpname=${corp%.txt}
    if [[ $corpname == "test" ]]; then  # Not fair, if we know the gold standard...
        re="-r ."
    else
        re="" 
    fi
    # For all frequencies for the current corpus
    printf "${LBLUE}"
    echo "Runing \"./doWCH.py -i devel.txt -f $min $re -o wch.$corpname.NUMBER.txt :"
    printf "${NC}"
    # Make freq table for lexicalisation  # GNU PARALLEL?
    ./doWCH.py -i $corp -f $min $re -o wch.$corpname.NUMBER.txt
    if [ $? -eq 0 ]; then printf "${GREEN}Done!${NC}"; echo; fi
done

# Convert training set to each format
mkdir converted
./conv_before_train.sh IOB2 ./train_new.txt converted
./conv_before_train.sh IOB2 devel.txt converted
./conv_before_train.sh IOB2 test.txt converted

# Do the lexicalisation for all train, devel and text set with all wch.[devel|test].[0-9]+.txt

mkdir temp
tempDir=`realpath $abspath/temp`
rm -rf temp/Makefile
i=1
for opt in "--just-words"  # "--none" " "
do
    lexSuff="${opt/--/}.lex"
    # lexSuff="${lexSuff/ /full}"
    for name in `ls converted | grep -v 'valid$' | grep -v '\.lex$'`
    do
	   # For all frequencies for all corpus
	   for wchf in `ls wch.*.txt`
	   do
		   wchname=${wchf%.txt}
		   wchname=${wchname#$wch}
		   #printf "${LBLUE}"
		   #echo "Runing ./lexicalise.py \"$abspath/converted/$name\" $wchf $opt > \"$abspath/converted/$name.$wchname.$lexSuff\" :"
		   #printf "${NC}"
		   echo -e "$i:\n\t$abspath/lexicalise.py \"$abspath/converted/$name\" $wchf $opt > \"$abspath/converted/$name.$wchname.$lexSuff\"\n" >> "$tempDir/Makefile"
		   i=$((i+1))
		   #./lexicalise.py "$abspath/converted/$name" $wchf $opt > "$abspath/converted/$name.$wchname.$lexSuff"
		   #printf "${LBLUE}"
		   #if [ $? -eq 0 ]; then printf "${GREEN}Done!${NC}"; echo; fi
	   done
    done
done
i=$((i-1))

echo -n 'all: ' > Makefile
seq -s ' ' 1 $i >> Makefile
echo >> Makefile
cat temp/Makefile >> Makefile
make -j$(($(nproc)+1))

# XXX PurePOS to be added
declare -A taggers=(
#              [tnt]='tnt.sh              '
#         [nltk-tnt]='nltk-tnt.py         '
#   [huntag3-bigram]='HunTag3-bigram.sh   '
#  [huntag3-trigram]='HunTag3.sh          '
# [huntag3-crfsuite]='HunTag3-CRFsuite.sh '
[crfsuite-official]='CRFsuite-official.sh'
)

# Train and tag with each tagger
#mkdir temp
rm -rf temp/Makefile
posField=2
i=1
for opt in "--just-words"  # "--none" " "
do
    lexSuff="${opt/--/}.lex"
    # lexSuff="${lexSuff/ /full}"
    if [[ "$lexSuff" == "none.lex" ]]; then
        omit="AAAA"
    else
        omit="huntag3"  # XXX TEST
    fi
    for name in `ls converted | grep "$lexSuff\$" | grep 'train_new.txt'`
    do
        for tname in "devel" "test"
        do
			testName=${name/train_new/$tname}  # replaces train_new -> test and devel
			trainFile=`realpath $abspath/converted/$name`
			testFile=`realpath $abspath/converted/$testName`
			outputFile=`realpath $abspath/converted/$testName`
			tempDir=`realpath $abspath/temp`
			posField="$posField"
			for key in "${!taggers[@]}"
			do
				if [[ ! $key =~ ^$omit ]]; then
					echo -e "$i:\n\t$abspath/taggers/${taggers[$key]} \"$trainFile\" \"$testFile\" \"$outputFile.$key.tagged\" \"$tempDir\" \"$posField\"\n" >> "$tempDir/Makefile"
					i=$((i+1))
				else
					echo "Omiting $regex* because long running time !"
				fi
			done
			if [ $? -eq 0 ]; then printf "${GREEN}Done!${NC}"; echo; fi
		done
    done
done
i=$((i-1))

echo -n 'all: ' > Makefile
seq -s ' ' 1 $i >> Makefile
echo >> Makefile
cat temp/Makefile >> Makefile
#make -j$(($(nproc)+1))

exit 1

# Tag on multiple computers, but shared mount...
seq 1 $i | parallel --no-notice --env PATH --sshloginfile nodefile make -f `realpath $abspath/Makefile` {}

# Delexicalise 

delexSuff="delex"
mkdir temp
tempDir=`realpath $abspath/temp`
rm -rf temp/Makefile
i=1
    for name in `ls converted | grep '\.tagged$'`
    do
	   echo -e "$i:\n\t$abspath/delexicalise.py \"$abspath/converted/$name\" > \"$abspath/delexicalise.py \"$abspath/converted/$name.$delexSuff\"\n" >> "$tempDir/Makefile"
	   i=$((i+1))
    done
i=$((i-1))

echo -n 'all: ' > Makefile
seq -s ' ' 1 $i >> Makefile
echo >> Makefile
cat temp/Makefile >> Makefile
make -j$(($(nproc)+1))

# Convert fix: Last column is the automatic tagging, that needed to be fixed by converting to the same representation by coreNLP IOButils...
#...

# Evalutate *.fixed one by one... And append the result to a file for GNUPlot...
#...

# Draw a graph for the paper by GNUPlot... 
#...
