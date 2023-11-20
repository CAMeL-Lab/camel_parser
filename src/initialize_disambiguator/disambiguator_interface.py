from typing import Union
from camel_tools.morphology.database import MorphologyDB
from camel_tools.morphology.analyzer import Analyzer
from camel_tools.disambig.bert import BERTUnfactoredDisambiguator

from src.initialize_disambiguator.bert_disambiguator import create_bert_disambiguator
from src.initialize_disambiguator.mle_disambiguator import MLEDisambiguatorAdapter

def set_up_analyzer(morphology_db: str) -> Analyzer:
    # used to initialize an Analyzer with ADD_PROP backoff 
    # db = MorphologyDB.builtin_db('calima-msa-s31')
    db_type = None if morphology_db == 'r13' else morphology_db
    db = MorphologyDB.builtin_db(db_name=db_type)
    return Analyzer(db=db, backoff='ADD_PROP', cache_size=100000)

def get_disambiguator(model_name: str, morphology_db: str) -> Union[MLEDisambiguatorAdapter, BERTUnfactoredDisambiguator]:
    analyzer = set_up_analyzer(morphology_db)
    
    if model_name == 'mle':
        model = MLEDisambiguatorAdapter(analyzer)
    elif model_name == 'bert':
        model = create_bert_disambiguator(analyzer)
    else:
        raise ValueError('Invalid model')
    
    return model