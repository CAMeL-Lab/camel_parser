from typing import List, Union, Dict

from supar import Parser
from supar.utils import Dataset

from camel_tools.utils.dediac import dediac_ar

import time

"""
conll object from parser
iterate over sentences from this object
iterate over the columns per sentence
create token rows
create conll sentence of token row tuples

"""

def parser_conll_to_conll_tuples(parser_conll: Dataset) -> List[List[tuple]]:
    conll_sentences = []
    for parser_sentence in parser_conll:
        sentence_tree_token_tuples = []
        for i in range(len(parser_sentence.values[0])):
            token_tuple_row = tuple(column[i] for column in parser_sentence.values)
            sentence_tree_token_tuples.append(token_tuple_row)
        conll_sentences.append(sentence_tree_token_tuples)
    return conll_sentences

def filter_tatweel(form):
    if form.replace("_", "").replace("\u0640","").replace("\u005F", "") == "":
        return form
    return form.replace("_", "").replace("\u0640","").replace("\u005F", "")

def parse(conll_path_or_parsed_tuples: Union[List[List[tuple]], str], parse_model:str, logs: Dict[str, float] = None) -> List[List[tuple]]:
    st = time.time()
    
    parser = Parser.load(parse_model)

    et = time.time()
    if logs is not None:
        logs["Loading parsing model"] = et-st
    st = time.time()
    conll = parser.predict(conll_path_or_parsed_tuples, verbose=False, tree=True, proj=True)
    et = time.time()
    if logs is not None:
        logs["Parsing prediction"] = et-st
    return conll

def parse_text_tuples(sentence_tuples: List[List[tuple]], parse_model, logs: Dict[str, float] =  None) -> List[List[tuple]]:
    sentence_tuples = [[val[1:4] for val in sent] for sent in sentence_tuples]
    form_lemma_pos_tuple = [[(filter_tatweel(dediac_ar(val[0])), filter_tatweel(dediac_ar(val[1])), val[2]) for val in sent] for sent in sentence_tuples]
    conll = parse(form_lemma_pos_tuple, parse_model=parse_model, logs = logs)
    return parser_conll_to_conll_tuples(conll)

def parse_conll(conll_path: str, parse_model, logs: Dict[str, float] = None) -> List[List[tuple]]:
    conll = parse(conll_path, parse_model=parse_model, logs=logs)
    for i, sent in enumerate(conll):
        conll[i].values[1] = [filter_tatweel(form) for form in sent.values[1]]
    return parser_conll_to_conll_tuples(conll)
