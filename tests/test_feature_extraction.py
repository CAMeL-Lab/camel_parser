import pytest
from pandas import read_csv

from src.parse_disambiguation.feature_extraction import get_word_features_df, join_feats

@pytest.fixture
def word_analysis():
    return {'diac': 'بِسْمِ', 'lex': 'ٱِسْم', 'caphi': 'b_i_s_m_i', 
        'gloss': 'in/by_+_(the)_Name_of_+_[def.gen.]', 
        'bw': 'بِ/PREP+ٱِسْم/NOUN+ِ/CASE_DEF_GEN', 'pos': 'noun', 
        'catib6': 'PRT+NOM', 'ud': 'ADP+NOUN', 'root': 'س.م.#', 
        'pattern': 'بِ1ْ2ِ', 'prc3': '0', 'prc2': '0', 'prc1': 
        'bi_prep', 'prc0': '0', 'per': 'na', 'asp': 'na', 
        'vox': 'na', 'mod': 'na', 'form_gen': 'm', 'gen': 'm', 
        'form_num': 's', 'num': 's', 'stt': 'c', 'cas': 'g', 
        'enc0': '0', 'rat': 'i', 'source': 'lex', 'd1seg': 'بِسْمِ', 
        'd2seg': 'بِ+_سْمِ', 'd3seg': 'بِ+_سْمِ', 'atbseg': 'بِ+_سْمِ', 
        'd1tok': 'بِسْمِ', 'd2tok': 'بِ+_اِسْمِ', 'd3tok': 'بِ+_اِسْمِ', 
        'atbtok': 'بِ+_اِسْمِ', 'bwtok': 'بِ+_ٱِسْم_+ِ', 'pos_logprob': -0.4344233, 
        'lex_logprob': -3.156274, 'pos_lex_logprob': -3.156274, 
        'stem': 'بِسْمِ', 'stemgloss': 'in/by_+_(the)_Name_of_+_[def.gen.]', 'stemcat': 'FW-Wa'
    }

@pytest.fixture
def clitic_feats():
    return read_csv('data/clitic_feats.csv')

@pytest.fixture
def word_feats():
    df = read_csv('tests/test_feats.tsv', sep='\t')
    return df.astype(str).astype(object)
    

def test_get_word_features_df(word_analysis, clitic_feats, word_feats):
    tagset = "catib6"
    
    df = get_word_features_df(word_analysis, clitic_feats)
    df = df.astype(str).astype(object)
    assert word_feats.equals(df)

def test_join_feats_catib6(word_feats):
    word_feats = join_feats(word_feats, 'catib6')
    
    assert word_feats['tokens'] == ['بِ+', 'اِسْمِ']
    assert word_feats['pos_tags'] == ['PRT', 'NOM']
    assert word_feats['lemmas'] == ['بِ+', 'ٱِسْم']
    assert word_feats['feats'] == ['ud=ADP|prc3=0|prc2=0|prc1=0|prc0=na|per=na|asp=na|vox=na|mod=na|gen=na|num=na|stt=na|cas=na|enc0=0|rat=na', 'ud=NOUN|prc3=0|prc2=0|prc1=bi_prep|prc0=0|per=na|asp=na|vox=na|mod=na|gen=m|num=s|stt=c|cas=g|enc0=0|rat=i']

def test_join_feats_ud(word_feats):
    word_feats = join_feats(word_feats, 'ud')
    
    assert word_feats['tokens'] == ['بِ+', 'اِسْمِ']
    assert word_feats['pos_tags'] == ['ADP', 'NOUN']
    assert word_feats['lemmas'] == ['بِ+', 'ٱِسْم']
    assert word_feats['feats'] == ['catib6=PRT|prc3=0|prc2=0|prc1=0|prc0=na|per=na|asp=na|vox=na|mod=na|gen=na|num=na|stt=na|cas=na|enc0=0|rat=na', 'catib6=NOM|prc3=0|prc2=0|prc1=bi_prep|prc0=0|per=na|asp=na|vox=na|mod=na|gen=m|num=s|stt=c|cas=g|enc0=0|rat=i']