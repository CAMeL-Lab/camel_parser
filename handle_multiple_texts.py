"""
Script to handle multiple texts.

Usage:
    text_to_conll_cli (-i <input> | --input=<input>)
        (-o <output> | --output=<output>)
        [-m <model> | --model=<model>]
    text_to_conll_cli (-h | --help)

Options:
    -i <input> --input=<input>
        A directory of text files
    -o <output> --output=<output>
        The directory to save the parsed CoNLL-X files
    -m <model> --model=<model>
        The name BERT model used to parse (to be placed in the model directory) [default: catib]
    -h --help
        Show this screen.
"""

import os
from pathlib import Path
from camel_tools.utils.charmap import CharMapper
from src.classes import TextParams
from src.conll_output import save_to_file, text_tuples_to_string
from src.data_preparation import get_tagset, parse_text
from src.initialize_disambiguator.disambiguator_interface import get_disambiguator
from src.utils.model_downloader import get_model_name
from docopt import docopt
from pandas import read_csv
from transformers.utils import logging

logging.set_verbosity_error()

arguments = docopt(__doc__)

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
    input_path = arguments['--input']
    output_path = arguments['--output']
    parse_model = arguments['--model']


    #
    ### Set up parsing model 
    # (download defaults models, and get correct model name from the models directory)
    #
    model_name = get_model_name(parse_model, model_path=model_path)
    
    # 
    ### get tagset (depends on model)
    #
    tagset = get_tagset(parse_model)
    
    disambiguator = get_disambiguator("bert", "r13")
    
    #
    ### main code ###
    #
    for root, _, files in os.walk(input_path):
        for text_file in files:
            print(f'processing {text_file}')
            lines = []
            with open(f'{root}/{text_file}', 'r') as f:
                lines = [line for line in f.readlines() if line.strip()]
            file_type_params = TextParams(lines, model_path/model_name, arclean, disambiguator, clitic_feats_df, tagset, "")
            parsed_text_tuples = parse_text("text", file_type_params)

            new_name = '.'.join((text_file.split('.')[:-1])) + '.conllx'
            
            save_to_file(
                text_tuples_to_string(parsed_text_tuples, file_type='text', sentences=lines),
                Path(output_path) / new_name
            )

if __name__ == '__main__':
    main()
