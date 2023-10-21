from typing import List
from camel_tools.disambig.common import DisambiguatedWord
from src.token_class import Token

def get_analysis_by_criteria(disambig_word: DisambiguatedWord, selection_criteria: dict) -> dict:
    # runs assertions to ensure the data is good
    is_analysis(disambig_word)
    
    for scored_analysis in disambig_word.analyses:
        analysis = scored_analysis.analysis
        if all(analysis[key] == selection_criteria[key] for key in selection_criteria):
            return analysis
    
    # if the criteria is not found, return the first analysis
    print(f"No analysis found for the given criteria on {disambig_word.word}, will return the first analysis.")
    return get_first_analysis(disambig_word)

def is_analysis(disambig_word: DisambiguatedWord) -> dict:
    # this should not be empty
    assert disambig_word, "Disambiguated word not found!"
    
    # this could be empty if there is no backoff, and this code assumes backoff
    assert disambig_word.analyses, "No analyses found, are you using backoff?"
    assert disambig_word.analyses[0], "No analyses found, are you using backoff?"

def get_first_analysis(disambig_word: DisambiguatedWord):
    # runs assertions to ensure the data is good
    is_analysis(disambig_word)
    
    return disambig_word.analyses[0].analysis


def get_sentence_analysis(disambiguated_sentence: List[DisambiguatedWord], selection: str='top', selection_criteria: dict=None) -> List[dict]:
    # sourcery skip: switch
    # get an analysis based on the selection criteria
    # top means take first
    # match means take the first analysis that matches the selection criteria.
    # selection criteria: {'criteria1': 'value1', 'criteria2': 'value2'...}
    # return None if criteria not fulfilled.
    # TODO: check if selection criteria contains valid keys
    if selection == 'top':
        return [get_first_analysis(disambig_word) for disambig_word in disambiguated_sentence]
    elif selection == 'match':
        return [get_analysis_by_criteria(disambig_word, selection_criteria) for disambig_word in disambiguated_sentence]
    else:
        raise ValueError(f"the selection {selection} is not valid!")

def to_sentence_analysis_list(disambiguated_sentences: List[List[DisambiguatedWord]]) -> List[List[Token]]:
    return [get_sentence_analysis(disambiguated_sentence, 'top') for disambiguated_sentence in disambiguated_sentences]
