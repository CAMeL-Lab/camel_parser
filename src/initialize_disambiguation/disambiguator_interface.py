from typing import Union
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.disambig.bert import BERTUnfactoredDisambiguator

from src.initialize_disambiguation.bert_disambiguator import create_bert_disambiguator
from src.initialize_disambiguation.mle_disambiguator import MLEDisambiguatorAdapter


def get_disambiguator(model_name: str, analyzer: Analyzer) -> Union[MLEDisambiguatorAdapter, BERTUnfactoredDisambiguator]:
    if model_name == 'mle':
        model = MLEDisambiguatorAdapter(analyzer)
    elif model_name == 'bert':
        model = create_bert_disambiguator(analyzer)
    else:
        raise ValueError('Invalid model')
    
    return model