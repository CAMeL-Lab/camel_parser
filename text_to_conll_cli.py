"""
Disambiguator and Conll builder CLI.

Usage:
    text_to_conll_cli (-i <input> | --input=<input> | -s <string> | --string=<string>)
        (-f <file_type> | --file_type=<file_type>)
        [-b <morphology_db> | --morphology_db=<morphology_db>]
        [-d <disambiguator> | --disambiguator=<disambiguator>]
        [-m <model> | --model=<model>]
        [-t  <tagset>| --tagset=<tagset>]
        [-l | --log]
    text_to_conll_cli (-h | --help)

Options:
    -i <input> --input=<input>
        A text file or conll file.
    -s <string> --string=<string>
        A string to parse.
    -f <file_type> --file_type=<file_type>
        The type of file passed. Could be 
            conll: conll
            raw: raw text
            tokenized: whitespace tokenized text (text will not be cleaned)
            tok_tagged: text is already tokenized and POS tagged
            parse_tok: text is already tokenized, only parse tokenized input; don't disambiguate to add POS tags or features
    -b <morphology_db> --morphology_db=<morphology_db>
        The morphology database to use; will use camel_tools built-in by default [default: r13]
    -d <disambiguator> --disambiguator=<disambiguator>
        The disambiguation technique used to tokenize the text lines, either 'mle' or 'bert' [default: bert]
    -m <model> --model=<model>
        The name BERT model used to parse (to be placed in the model directory) [default: catib]
    -t <tagset> --tagset=<tagset>
        Selecting either catib6 or UD as the POS tagset [default: catib6]
    -l --log
        Log execution time for various stages
    -h --help
        Show this screen.
"""

from pathlib import Path
from typing import List
from camel_tools.disambig.common import DisambiguatedWord
from camel_tools.utils.charmap import CharMapper
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
from src.disambiguation.disambiguator_interface import get_disambiguator
from src.initialization import setup_parsing_model
from src.parse_disambiguation.disambiguation_analysis import to_sentence_analysis_list
from src.parse_disambiguation.feature_extraction import to_sentence_features_list
from src.text_cleaner import clean_lines, split_lines_words
from src.biaff_parser import parse_tuples, parse_conll
from docopt import docopt
from transformers.utils import logging
from datetime import datetime
import re
import time
from pandas import read_csv

arguments = docopt(__doc__)

logging.set_verbosity_error()

def print_to_conll(sentence_tuples, annotations=None, sentences=None):
    if sentences is not None: 
        sentences = list(filter(lambda x : len(re.sub(r"\s+", "", x, flags=re.UNICODE)) > 0, sentences))
    tokens = [[tup[1] for tup in sent] for sent in sentence_tuples]
    for i in range(len(sentence_tuples)):
        if sentences != None:
            print(f"# text = {sentences[i].strip()}")
            print(f"# treeTokens = {' '.join(tokens[i])}")
        elif annotations != None:
            [print(annotation) for annotation in annotations[i]]
        print("\n".join(["\t".join([str(i) for i in tup]) for tup in sentence_tuples[i]])+"\n")

def merge_tuples(parsed_tuples, sent_tuples):
    merged_tuples = []
    for i, sent in enumerate(parsed_tuples):
        col_list = []
        for j, col in enumerate(sent_tuples[i]):
            if j != 6 and j!= 7:
                col_list.append(col)
            else:
                col_list.append(sent[j])
        merged_tuples.append(tuple(col_list))
    return merged_tuples

def parse_tok_pos(sent):
    sentence_tuples = []
    
    # split on space, and using positive lookbehind and lookahead
    # to detect parentheses around the space
    for tup in re.split(r'(?<=\)) (?=\()', sent.strip()):
        tup_items = tup[1:-1]
        form = (','.join(tup_items.split(',')[:-1])).strip() # account for comma tokens
        pos = (tup_items.split(',')[-1]).strip()
        sentence_tuples.append((form, pos))

    return sentence_tuples

def get_file_type(file_type):
    if file_type in ['conll', 'raw', 'tokenized', 'tok_tagged', 'parse_tok']:
        return file_type 
    assert False, 'Unknown file type'


def main():
    root_dir = Path(__file__).parent
    model_path = root_dir/"models"
    
    #
    ### cli user input ###
    #
    file_path = arguments['--input']
    string_text = arguments['--string']
    file_type = get_file_type(arguments['--file_type'])
    morphology_db = arguments['--morphology_db']
    disambiguator_type = arguments['--disambiguator']
    parse_model = arguments['--model']
    log = arguments['--log']
    tagset = arguments['--tagset']


    #
    ### Set up logger
    #
    log_file = None
    logs = {}
    if log:
        log_file = "log-"+datetime.now().strftime("%d-%m-%Y-%H:%M:%S")
    if file_type == 'conll':
        parse_conll(file_path, logs=logs, parse_model=model_path/model_name)
        if log:
            with open("./logs/"+log_file,'w') as f:
                for key, value in logs.items():   
                    f.write('%s = %s\n' % (key, value))
        return


    st = time.time()
    
    #
    ### camel_tools imports ###
    #
    # used to clean text
    arclean = CharMapper.builtin_mapper("arclean")
    # used to initialize an Analyzer with ADD_PROP backoff 
    # db = MorphologyDB.builtin_db('calima-msa-s31')
    db_type = None if morphology_db == 'r13' else morphology_db
    db = MorphologyDB.builtin_db(db_name=db_type)
    analyzer = Analyzer(db=db, backoff='ADD_PROP', cache_size=100000)
    disambiguator = get_disambiguator(disambiguator_type, analyzer)
    
    #
    ### Set up parsing model
    #
    model_name = setup_parsing_model(parse_model, model_path=model_path)
    
    
    #
    ### Get clitic features
    #
    clitic_feats_df = read_csv('data/clitic_feats.csv')
    clitic_feats_df = clitic_feats_df.astype(str).astype(object) # so ints read are treated as string objects
    
    #
    ### main code ###
    #
    lines = []
    if string_text is not None:
        lines = [string_text]
    elif file_path is not None:
        with open(file_path, 'r') as f:
            lines = [line for line in f.readlines() if line.strip()]
    et = time.time()
    logs["reading input"] = et-st

    st = time.time()
    sentence_tuples = []
    if file_type in ['raw', 'tokenized']:
        # clean lines for raw only
        token_lines = clean_lines(lines, arclean) if file_type == 'raw' else split_lines_words(lines)
        disambiguated_sentences: List[List[DisambiguatedWord]] = disambiguator.disambiguate_sentences(token_lines)
        sentence_analysis_list: List[List[dict]] = to_sentence_analysis_list(disambiguated_sentences)
        sentence_tuples: List[List[tuple]] = to_sentence_features_list(sentence_analysis_list, clitic_feats_df, tagset)
    elif file_type == 'parse_tok':
        sentence_tuples = [[(0, tok, '_' ,'UNK') for tok in line.strip().split(' ')] for line in lines]
    elif file_type == 'tok_tagged':
        sentence_tuples =  [[(0, tup[0],'_' ,tup[1]) for tup in parse_tok_pos(line)] for line in lines]

    et = time.time()
    logs["input preparation"] = et-st
    parsed_tuples = parse_tuples(sentence_tuples, logs=logs, parse_model=model_path/model_name)
    st = time.time()
    # print_to_conll(merge_tuples(parsed_tuples, sentence_tuples), sentences=lines)
    print_to_conll(parsed_tuples, sentences=lines)
    et = time.time()
    logs["printing to conll"] = et-st
    if log:
        with open("./logs/"+log_file,'w') as f:
            for key, value in logs.items(): 
                f.write('%s = %s\n' % (key, value))

if __name__ == '__main__':
    main()
