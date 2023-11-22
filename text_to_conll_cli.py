"""
Disambiguator and Conll builder CLI.

Usage:
    text_to_conll_cli (-i <input> | --input=<input> | -s <string> | --string=<string>)
        (-f <file_type> | --file_type=<file_type>)
        [-b <morphology_db_type> | --morphology_db_type=<morphology_db_type>]
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
            tok_tagged: text is already tokenized and POS tagged, in tuple form
            parse_tok: text is already tokenized, only parse tokenized input; don't disambiguate to add POS tags or features
    -b <morphology_db_type> --morphology_db_type=<morphology_db_type>
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
from camel_tools.utils.charmap import CharMapper
from src.conll_output import print_to_conll
from src.data_preparation import get_file_type_params, parse_text
from src.utils.model_downloader import get_model_name
from docopt import docopt
from transformers.utils import logging
from datetime import datetime
import time
from pandas import read_csv

arguments = docopt(__doc__)

logging.set_verbosity_error()

def get_file_type(file_type):
    if file_type in ['conll', 'raw', 'tokenized', 'tok_tagged', 'parse_tok']:
        return file_type 
    assert False, 'Unknown file type'


def main():
    root_dir = Path(__file__).parent
    model_path = root_dir/"models"
    
    # camel_tools import used to clean text
    arclean = CharMapper.builtin_mapper("arclean")

    #
    ### Get clitic features
    #
    clitic_feats_df = read_csv(root_dir / 'data/clitic_feats.csv')
    clitic_feats_df = clitic_feats_df.astype(str).astype(object) # so ints read are treated as string objects
    

    #
    ### cli user input ###
    #
    file_path = arguments['--input']
    string_text = arguments['--string']
    file_type = get_file_type(arguments['--file_type'])
    morphology_db_type = arguments['--morphology_db_type']
    disambiguator_type = arguments['--disambiguator']
    parse_model = arguments['--model']
    # log = arguments['--log']
    tagset = arguments['--tagset']


    #
    ### Set up parsing model 
    # (download defaults models, and get correct model name from the models directory)
    #
    model_name = get_model_name(parse_model, model_path=model_path)
    
    #
    ### main code ###
    #
    lines = []
    if string_text is not None:
        lines = [string_text]
    elif file_path is not None:
        with open(file_path, 'r') as f:
            lines = [line for line in f.readlines() if line.strip()]

    # import pdb; pdb.set_trace()

    file_type_params = get_file_type_params(lines, file_type, file_path, model_path/model_name,
        arclean, disambiguator_type, clitic_feats_df, tagset, morphology_db_type)
    parsed_text_tuples = parse_text(file_type, file_type_params)

    print_to_conll(parsed_text_tuples, sentences=lines)

if __name__ == '__main__':
    main()
