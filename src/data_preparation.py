
import re
from typing import List, Union
import pandas as pd
from camel_tools.disambig.common import DisambiguatedWord
from src.classes import ConllParams, TextParams, PreprocessedTextParams, TokenizedParams, TokenizedTaggedParams
from src.dependency_parser.biaff_parser import parse_conll, parse_text_tuples
from src.initialize_disambiguator.disambiguator_interface import get_disambiguator
from src.parse_disambiguation.disambiguation_analysis import to_sentence_analysis_list
from src.parse_disambiguation.feature_extraction import to_conll_fields_list
from src.utils.text_cleaner import clean_lines, split_lines_words
from src.logger import log


FileTypeParams = Union[ConllParams, TextParams, PreprocessedTextParams, TokenizedParams, TokenizedTaggedParams]


def get_feats_from_text_tuples(text_tuples: List[List[tuple]]) -> List[List[str]]:
    """Extract the FEATS columns from the unparsed data.
    FEATS will exist only for text and pre-processed text inputs.

    Args:
        text_tuples (List[List[tuple]]): unparsed data

    Returns:
        List[List[str]]: the FEATS column (or _ if it does not exist)
    """
    try:
        return [[col_items[5] for col_items in tup_list] for tup_list in text_tuples]
    except:
        import pdb; pdb.set_trace()


def add_feats(text_tuples: List[List[tuple]], text_feats: List[List[str]]) -> List[List[tuple]]:
    """Add FEATS data to the text tuples.
    The parent list (text_tuples) is a list of sentences.
    Each sentence is a list of tuples.
    Each tuple represents a token.

    Args:
        text_tuples (List[List[tuple]]): list of list of tuples
        text_feats (List[List[str]]): list of list of FEATS

    Returns:
        List[List[tuple]]: text_tuples but with the FEATS column filled
    """
    text_tuples_with_feats = []
    for sentence_tuples, sentence_feats in zip(text_tuples, text_feats):
        
        # get first 5 and last 4 items from parsed tuple using lists, and add features.
        # Convert the list of fields to a tuple
        merged_tuples = [
            tuple(list(token_tuple[:5]) + [token_feats] + list(token_tuple[6:]))
            for token_tuple, token_feats in zip(sentence_tuples, sentence_feats)
        ]
        text_tuples_with_feats.append(merged_tuples)
    return text_tuples_with_feats

def string_to_tuple_list(string_of_tuples: str) -> List[tuple[str, str]]:
    """Take a string of space-separated tuples and convert it to a tuple list.
    Example input: '(جامعة, NOM) (نيويورك, PROP)'
    Example output: [(جامعة, NOM), (نيويورك, PROP)]

    Args:
        string_of_tuples (str): string of tuples

    Returns:
        List(tuple[str, str]): list of token-pos tuple pairs
    """
    sentence_tuples = []
    
    # split on space, and using positive lookbehind and lookahead
    # to detect parentheses around the space
    for tup in re.split(r'(?<=\)) (?=\()', string_of_tuples.strip()):
        # tup = (جامعة, NOM)
        tup_items = tup[1:-1] # removes parens
        form = (','.join(tup_items.split(',')[:-1])).strip() # account for comma tokens
        pos = (tup_items.split(',')[-1]).strip()
        sentence_tuples.append((form, pos))
    return sentence_tuples

def get_tree_tokens(tok_pos_tuples):
    sentences = []
    for sentence_tuples in tok_pos_tuples:
        sentence = ' '.join([tok_pos_tuple[0] for tok_pos_tuple in sentence_tuples])
        sentences.append(sentence)
    return sentences

def handle_conll(file_type_params):
    file_path, parse_model_path = file_type_params
    # pass the path to the text file and the model path and name, and get the tuples
    return parse_conll(file_path, parse_model=parse_model_path)

def handle_preprocessed_text(file_type_params):
    lines, _, disambiguator_type, clitic_feats_df, tagset, morphology_db_type = file_type_params

    token_lines = split_lines_words(lines)

    disambiguator = get_disambiguator(disambiguator_type, morphology_db_type)
    # run the disambiguator on the sentence list to get an analysis for all sentences
    disambiguated_sentences: List[List[DisambiguatedWord]] = disambiguator.disambiguate_sentences(token_lines)
    # get a single analysis for each word (top or match, match not implemented yet)
    sentence_analysis_list: List[List[dict]] = to_sentence_analysis_list(disambiguated_sentences)
    # extract the relevant items from each analysis into conll fields
    return to_conll_fields_list(sentence_analysis_list, clitic_feats_df, tagset)

def handle_text(file_type_params):
    lines, _, arclean, disambiguator_type, clitic_feats_df, tagset, morphology_db_type = file_type_params
    # clean lines
    token_lines = clean_lines(lines, arclean)

    disambiguator = get_disambiguator(disambiguator_type, morphology_db_type)
    # run the disambiguator on the sentence list to get an analysis for all sentences
    disambiguated_sentences: List[List[DisambiguatedWord]] = disambiguator.disambiguate_sentences(token_lines)
    # get a single analysis for each word (top or match, match not implemented yet)
    sentence_analysis_list: List[List[dict]] = to_sentence_analysis_list(disambiguated_sentences)
    # extract the relevant items from each analysis into conll fields
    return to_conll_fields_list(sentence_analysis_list, clitic_feats_df, tagset)

def handle_tokenized(file_type_params):
    lines = file_type_params.lines
    # construct tuples before sending them to the parser
    return [[(0, tok, '_' ,'UNK', '_', '_', '_', '_', '_', '_') for tok in line.strip().split(' ')] for line in lines]

def handle_tokenized_tagged(file_type_params):
    lines = file_type_params.lines
    # convert input tuple list into a tuple data structure
    tok_pos_tuples_list = [string_to_tuple_list(line) for line in lines]
    # since we did not start with sentences, we make sentences using the tokens (which we call tree tokens)
    lines = get_tree_tokens(tok_pos_tuples_list)
    # construct tuples before sending them to the parser
    return [[(0, tup[0],'_' ,tup[1], '_', '_', '_', '_', '_', '_') for tup in tok_pos_tuples] for tok_pos_tuples in tok_pos_tuples_list]

def get_file_type_params(lines, file_type, file_path, parse_model_path,
    arclean, disambiguator_type, clitic_feats_df, tagset, morphology_db_type):
    if file_type == 'conll':
        return ConllParams(file_path, parse_model_path)
    elif file_type == 'text':
        return TextParams(lines, parse_model_path, arclean, disambiguator_type, clitic_feats_df, tagset, morphology_db_type)
    elif file_type == 'preprocessed_text':
        return PreprocessedTextParams(lines, parse_model_path, disambiguator_type, clitic_feats_df, tagset, morphology_db_type)
    elif file_type == 'tokenized':
        return TokenizedParams(lines, parse_model_path)
    elif file_type == 'tokenized_tagged':
        return TokenizedTaggedParams(lines, parse_model_path)

def parse_text(file_type: str, file_type_params: FileTypeParams):
    if file_type == 'conll':
        # handle_conll(file_path, parse_model_path)
        parsed_text_tuples = handle_conll(file_type_params)
    else:
        text_tuples: List[List[tuple]] = []
        if file_type == 'text':
            text_tuples = handle_text(file_type_params)
        elif file_type == 'preprocessed_text':
            text_tuples = handle_preprocessed_text(file_type_params)
        elif file_type == 'tokenized':
            text_tuples = handle_tokenized(file_type_params)
        elif file_type == 'tokenized_tagged':
            text_tuples = handle_tokenized_tagged(file_type_params)

        # the text tuples created from the above processes is passed to the dependency parser
        parsed_text_tuples = parse_text_tuples(text_tuples, parse_model=file_type_params.parse_model_path)
        # for text/preprocessed_text, we want to extract the features to place in parsed_text_tuples
        # TODO: check if this step can be skipped by placing features in a step above
        text_feats: List[List[str]] = get_feats_from_text_tuples(text_tuples)
        # place features in FEATS column
        parsed_text_tuples = add_feats(parsed_text_tuples, text_feats)

    return parsed_text_tuples