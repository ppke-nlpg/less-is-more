# Less is More
The program used in the paper 'Less is More, More or Less... – Finding the Optimal Threshold for Lexicalisation in Chunking' by Balázs Indig

This is a stripped and evolved version of [Gut, Besser, Chunker](https://github.com/ppke-nlpg/gut-besser-chunker).

## Prerequisites

- data folder: train.txt and test.txt (The [CoNLL-2000 data](http://www.cnts.ua.ac.be/conll2000/chunking/))
- CRFsuite installed and (crfsuite and chunking.py in path)
- Python3, JRE 1.8, GNU parallel (optional) installed

## Usage

- Set hosts file for parallel...
- Run ./start.sh and wait...
- See .sh and and .py files for documentation...

## Warning

- The whole process takes much time!

## License

The repository contains many 3rd-party code, that has its own license.
This code is made available under the GNU Lesser General Public License v3.0.


## Reference

If you use this program please cite:

```
    @inproceedings{indig2017less,
      author    = {{I}ndig, {B}al\'azs},
      title     = {{Less is More, More or Less...} -- {F}inding the {O}ptimal {T}hreshold for {L}exicalisation in {C}hunking},
      booktitle = {Computational Linguistics and Intelligent Text Processing - 18th International Conference, CICLing 2017, Budapest, Hungary, April 17-23, 2017},
      year      = {2017}
    }
```
