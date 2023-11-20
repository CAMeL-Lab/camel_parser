from dataclasses import dataclass
from typing import List, Union
from dataclasses import astuple, dataclass
import pandas as pd
from camel_tools.disambig.bert import BERTUnfactoredDisambiguator
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.utils.charmap import CharMapper


@dataclass
class ConllParams:
    file_path: str
    parse_model_path: str
    
    def __iter__(self):
        return iter(astuple(self))

@dataclass
class RawParams:
    lines: List[str]
    parse_model_path: str
    arclean: CharMapper
    disambiguator: Union[BERTUnfactoredDisambiguator, MLEDisambiguator]
    clitic_feats_df: pd.DataFrame
    tagset: str
    
    def __iter__(self):
        return iter(astuple(self))

@dataclass
class TokenizedParams:
    lines: List[str]
    parse_model_path: str
    disambiguator: Union[BERTUnfactoredDisambiguator, MLEDisambiguator]
    clitic_feats_df: pd.DataFrame
    tagset: str
    
    def __iter__(self):
        return iter(astuple(self))

@dataclass
class ParseTokParams:
    lines: List[str]
    parse_model_path: str

@dataclass
class TokTaggedParams:
    lines: List[str]
    parse_model_path: str

@dataclass
class Token:
    ID: int = -1
    FORM: str = '_'
    LEMMA: str = '_'
    UPOS: str = '_'
    XPOS: str = '_'
    FEATS: str = '_'
    HEAD: int = 0
    DEPREL: str = '_'
    DEPS: str = '_'
    MISC: str = '_'
    
    def to_conll_row(self):
        col_vals = [str(getattr(self, key)) for key in self.__dataclass_fields__.keys()]
        return '\t'.join(col_vals)