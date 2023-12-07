"""
Script to handle multiple conll files.

Usage:
    text_to_conll_cli (-i <input> | --input=<input>)
        (-o <output> | --output=<output>)
        [-m <model> | --model=<model>]
        [-t  <tagset>| --tagset=<tagset>]
    text_to_conll_cli (-h | --help)

Options:
    -i <input> --input=<input>
        A directory of conll files
    -o <output> --output=<output>
        The directory to save the parsed CoNLL-X files
    -m <model> --model=<model>
        The name BERT model used to parse (to be placed in the model directory) [default: catib]
    -t <tagset> --tagset=<tagset>
        Selecting either catib6 or UD as the POS tagset [default: catib6]
    -h --help
        Show this screen.
"""

import os
from pathlib import Path
import re
from typing import List
from camel_tools.utils.charmap import CharMapper
from src.classes import ConllParams
from src.conll_output import print_to_conll, save_to_file, text_tuples_to_string
from src.data_preparation import parse_text
from src.initialize_disambiguator.disambiguator_interface import get_disambiguator
from src.utils.model_downloader import get_model_name
from docopt import docopt
from pandas import read_csv
from transformers.utils import logging

logging.set_verbosity_error()

arguments = docopt(__doc__)

def get_list_of_comments(conll_lines) -> List[List[str]]:
    """Initializes the class variable comments as a list of lists of comments.
    Within the comments list:
    Each list represents the comments of the given tree.
    
    An empty list represents a tree with no comments.

    Returns:
        List[List[str]]: a list of lists of comments
    """
    # get lines starting with # and blank lines
    # the blank lines represent the end of the tree/tree comments.
    matcher = re.compile(r'^(# text.*)$', re.MULTILINE)
    
    # a flat list of all comments
    lines: List[str] = matcher.findall(conll_lines)
    
    lines = [line[9:] for line in lines]
    # # create a list of lists of comments
    # final_list: List[List[str]] = []
    # temp_list: List[str] = []
    # for line in lines:
    #     if line == '': # an empty string represents the end of comments of the given tree.
    #         final_list.append(temp_list)
    #         temp_list = []
    #     else:
    #         temp_list.append(line)
    return lines


def main():
    root_dir = Path(__file__).parent
    model_path = root_dir/"models"

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
    ### main code ###
    #
    for root, _, files in os.walk(input_path):
        for text_file in files:
            print(f'processing {text_file}')
            file_type_params = ConllParams(str(Path(input_path) / text_file), model_path/model_name)
            parsed_text_tuples = parse_text("conll", file_type_params)

            lines = []
            with open(f'{root}/{text_file}', 'r') as f:
                lines = [line for line in f.readlines() if line.strip()]
            
            lines = get_list_of_comments(''.join(lines))
            
            conll_name = f"{'.'.join(text_file.split('.')[:-1])}.conllx"
            save_to_file(
                text_tuples_to_string(parsed_text_tuples, sentences=lines),
                Path(output_path) / conll_name
            )

if __name__ == '__main__':
    main()
