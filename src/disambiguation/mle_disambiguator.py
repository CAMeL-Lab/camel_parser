from typing import List
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.disambig.common import DisambiguatedWord
from camel_tools.morphology.analyzer import Analyzer

class MLEDisambiguatorAdapter():
    def __init__(self, analyzer: Analyzer):
        self.disambiguator = MLEDisambiguator(analyzer=analyzer)
    
    # def pretrained(self, analyzer):
    #     self.disambiguator = self.disambiguator
    
    def disambiguate(self, sentence: List[str]) -> List[DisambiguatedWord]:
        return self.disambiguator.disambiguate(sentence)
    
    def disambiguate_sentences(self, lines: List[List[str]]) -> List[List[DisambiguatedWord]]:
        return [self.disambiguator.disambiguate(line) for line in lines]