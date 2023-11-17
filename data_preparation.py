
from dataclasses import dataclass
from typing import List, Union
from camel_tools.disambig.common import DisambiguatedWord
from src.dependency_parser.biaff_parser import parse_conll, parse_text_tuples
from src.parse_disambiguation.disambiguation_analysis import to_sentence_analysis_list
from src.parse_disambiguation.feature_extraction import to_conll_fields_list
from src.utils.text_cleaner import clean_lines, split_lines_words
from text_to_conll_cli import add_feats, get_feats_from_text_tuples, get_tree_tokens, string_to_tuple_list

# @dataclass
# class Conll:
#     file_path: str

# @dataclass
# class Raw:
#     lines: List[str]

# @dataclass
# class Tokenized:
#     lines: List[str]

# @dataclass
# class ParseTok:
#     lines: List[str]

# @dataclass
# class TokTagged:
#     lines: List[str]

# FileType = Union[Conll, Raw, Tokenized, ParseTok, TokTagged]

def handle_conll(file_path, parse_model_path):
    # pass the path to the text file and the model path and name, and get the tuples
    parsed_text_tuples = parse_conll(file_path, parse_model=parse_model_path)

def handle_raw_or_tokenized(lines, arclean, file_type, disambiguator, clitic_feats_df, tagset):
    # clean lines for raw only
    token_lines = clean_lines(lines, arclean) if file_type == 'raw' else split_lines_words(lines)
    # run the disambiguator on the sentence list to get an analysis for all sentences
    disambiguated_sentences: List[List[DisambiguatedWord]] = disambiguator.disambiguate_sentences(token_lines)
    # get a single analysis for each word (top or match, match not implemented yet)
    sentence_analysis_list: List[List[dict]] = to_sentence_analysis_list(disambiguated_sentences)
    # extract the relevant items from each analysis into conll fields
    text_tuples = to_conll_fields_list(sentence_analysis_list, clitic_feats_df, tagset)

def parse_text(lines, # all
               file_type, # all
               file_path, # conll only, though can be changed
               parse_model_path, # conll, 3
               arclean, # raw, tokenized
               disambiguator, # raw, tokenized
               clitic_feats_df, # raw, tokenized
               tagset): # raw, tokenized
    if file_type == 'conll':
        handle_conll(file_path, parse_model_path)
    else:
        text_tuples: List[List[tuple]] = []
        if file_type in ['raw', 'tokenized']:
            handle_raw_or_tokenized(lines, arclean, file_type, disambiguator, clitic_feats_df, tagset)
        elif file_type == 'parse_tok':
            # construct tuples before sending them to the parser
            text_tuples = [[(0, tok, '_' ,'UNK', '_', '_', '_', '_', '_', '_') for tok in line.strip().split(' ')] for line in lines]
        elif file_type == 'tok_tagged':
            # convert input tuple list into a tuple data structure
            tok_pos_tuples_list = [string_to_tuple_list(line) for line in lines]
            # since we did not start with sentences, we make sentences using the tokens (which we call tree tokens)
            lines = get_tree_tokens(tok_pos_tuples_list)
            # construct tuples before sending them to the parser
            text_tuples = [[(0, tup[0],'_' ,tup[1], '_', '_', '_', '_', '_', '_') for tup in tok_pos_tuples] for tok_pos_tuples in tok_pos_tuples_list]

        # the text tuples created from the above processes is passed to the dependency parser
        parsed_text_tuples = parse_text_tuples(text_tuples, parse_model=parse_model_path)
        # for raw/tokenized, we want to extract the features to place in parsed_text_tuples
        # TODO: check if this step can be skipped by placing features in a step above
        text_feats: List[List[str]] = get_feats_from_text_tuples(text_tuples)
        # place features in FEATS column
        parsed_text_tuples = add_feats(parsed_text_tuples, text_feats)
    
    return parsed_text_tuples