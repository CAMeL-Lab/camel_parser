from typing import List, Union, Dict

from supar import Parser

from camel_tools.utils.dediac import dediac_ar

import time

def conll_to_parsed_tuples(conll):
    parsed_tuples = []
    for sent in conll:
        sentence = []
        for i in range(len(sent.values[0])):
            word = [col[i] for col in sent.values]
            sentence.append(tuple(word))
        parsed_tuples.append(sentence)

    return parsed_tuples

def filter_tatweel(form):
    if form.replace("_", "").replace("\u0640","").replace("\u005F", "") == "":
        return form
    return form.replace("_", "").replace("\u0640","").replace("\u005F", "")

def parse(conll_path_or_parsed_tuples: Union[List[List[tuple]], str], model_path:str = "./models/patb+cameltb-all_msa.model", logs: Dict[str, float] = None) -> List[List[tuple]]:
    st = time.time()
    # TODO: use __file__ to solve import issues
    parser = Parser.load(model_path)
    et = time.time()
    if logs is not None:
        logs["Loading parsing model"] = et-st
    st = time.time()
    conll = parser.predict(conll_path_or_parsed_tuples, verbose=False, tree=True, proj=True)
    et = time.time()
    if logs is not None:
        logs["Parsing prediction"] = et-st
    return conll

def parse_tuples(sentence_tuples: List[List[tuple]], model_path, logs: Dict[str, float] =  None) -> List[List[tuple]]:
    sentence_tuples = [[val[1:4] for val in sent] for sent in sentence_tuples]
    form_lemma_pos_tuple = [[(filter_tatweel(dediac_ar(val[0])), filter_tatweel(dediac_ar(val[1])), val[2]) for val in sent] for sent in sentence_tuples]
    conll = parse(form_lemma_pos_tuple, model_name=model_path, logs = logs)
    return conll_to_parsed_tuples(conll)

def parse_conll(conll_path: str, model_path, logs: Dict[str, float] = None) -> List[List[tuple]]:
    conll = parse(conll_path, model_name=model_path, logs=logs)
    for i, sent in enumerate(conll):
        conll[i].values[1] = [filter_tatweel(form) for form in sent.values[1]]
    [print(sent) for sent in conll]
    return
