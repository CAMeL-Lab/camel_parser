"""Given a list of list of analyses (one analysis per token),
get features based on a given criteria.

If no criteria is given, return atbtok and catib6
"""

import re
from typing import List
import json
from camel_tools.utils.dediac import dediac_ar
from camel_tools.utils.charmap import CharMapper
from camel_tools.utils.transliterate import Transliterator
import pandas as pd

FEATURES_LIST = ["pos", "prc3", "prc2", "prc1", "prc0", "enc0", "asp", "vox", "mod", "gen", "num", "stt", "cas", "per", "rat"]

def feats_dict_to_string(feats_dict):
    # prc3=na|prc2=na|prc1=na|prc0=na|per=na|asp=na|vox=na|mod=na|gen=na|num=na|stt=na|cas=na|enc0=na|rat=na
    feats_str = json.dumps(feats_dict)
    return feats_str.replace('", "', "|").replace('": "', "=").replace('{"', '').replace('"}', '')

def build_clitic_feats_dict(clitic_feat_list):
    assert len(clitic_feat_list) != 0, f'invalid clitic, {clitic_feat_list}'
    assert len(clitic_feat_list) == 1, f'multiple clitics matched when only one should, {clitic_feat_list}'
    clitic_feat_list[0]['deciding_feat']
    final_clitic_feats = {k: v for k,v in clitic_feat_list[0].items() if k in FEATURES_LIST}
    final_clitic_feats['token_type'] = clitic_feat_list[0]['deciding_feat'].split(':')[0]
    return final_clitic_feats

def get_clitic_feats(token, clitic_order, clitic_feats, stem_feats):
    mapper = CharMapper.builtin_mapper('ar2bw')
    transliterator = Transliterator(mapper)
    token = transliterator.transliterate(dediac_ar(token))
    filtered_clitics = clitic_feats[(clitic_feats.clitic == token) & (clitic_feats.deciding_feat.str.startswith(clitic_order))]
    clitic_list = [f'{k}:{v}' for k, v in stem_feats.items() if k.startswith(clitic_order) and v not in ['0', 'na']]

    for feat_check in clitic_list:
        clitic_feat_list = filtered_clitics[filtered_clitics.deciding_feat == feat_check].to_dict('records')
        if clitic_feat_list:
            return build_clitic_feats_dict(clitic_feat_list)
    assert False, f"clitic '{token}' does not exist in clitics list. Stem features: {stem_feats}"

def get_stem_feats(word_analysis):
    return {feat: word_analysis[feat] for feat in FEATURES_LIST}

def get_clitic_order(token):
    if token.endswith('+'):
        clitic_order = 'prc'
    elif token.startswith('+'):
        clitic_order = 'enc'
    return clitic_order

def is_clitic(token):
    return (token.startswith('+') or token.endswith('+')) and not re.match(r'^\++$', token)

def empty_clitic_feats_from_baseword(stem_feats):
    clitic_type_list = ["prc3", "prc2", "prc1", "prc0", "enc0"]
    for clitic_type in clitic_type_list:
        if stem_feats[clitic_type] not in ['0', 'na', 'Al_det']:
            stem_feats[clitic_type] = '0'
    return stem_feats
    

def r13_fixes(token, stem_feats):
    # handling edge cases where li comes from variations of wa li>n (i.e. li>nhu, li>nanY)
    li_feats = {'pos': 'conj_sub', 'prc3': '0', 'prc2': 'wa_conj', 'prc1': '0', 'prc0': 'na', 'enc0': '3ms_pron', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'}
    if {k for k, _ in stem_feats.items() ^ li_feats.items()} == {'enc0'}:
        stem_feats['prc1'] = 'li_conj'
    
    # handling edge cases where li comes from variations of li>n (i.e. li>nhu, li>nanY)
    li_feats = {'pos': 'conj_sub', 'prc3': '0', 'prc2': '0', 'prc1': '0', 'prc0': 'na', 'enc0': '0', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'}
    if {k for k, _ in stem_feats.items() ^ li_feats.items()} == {'enc0'}:
        stem_feats['prc1'] = 'li_conj'
        
    # handling edge cases where li comes from li>n
    if token == 'لِ+' and stem_feats == {'pos': 'conj_sub', 'prc3': '0', 'prc2': '0', 'prc1': '0', 'prc0': 'na', 'enc0': '0', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'}:
            stem_feats['prc1'] = 'li_conj'
    
    # handling edge cases where li comes from wa li>n
    if token == 'لِ+' and stem_feats == {'pos': 'conj_sub', 'prc3': '0', 'prc2': 'wa_conj', 'prc1': '0', 'prc0': 'na', 'enc0': '3ms_pron', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'}:
            stem_feats['prc1'] = 'li_conj'
    
    # handling edge cases where mA comes from qlmA
    if token == '+ما' and stem_feats == {'pos': 'conj', 'prc3': '0', 'prc2': '0', 'prc1': '0', 'prc0': 'na', 'enc0': '0', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'n'}:
            stem_feats['enc0'] = 'mA_sub'
    
    # handling an edge case where li comes from likY
    # added li_conj to clitic_feats.csv
    if token == 'لِ+' and stem_feats == {'pos': 'conj', 'prc3': '0', 'prc2': '0', 'prc1': '0', 'prc0': 'na', 'enc0': '0', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'}:
        stem_feats['prc1'] = 'li_conj'

def add_remaining_features(tokens_df, stem_feats, clitic_feats):
    existing_clitics = ['prc0']

    clitic_feats_list = []

    for _, row in tokens_df.iterrows():
        token = row['token']
        if not is_clitic(token):
            baseword_feats_dict = empty_clitic_feats_from_baseword(dict(stem_feats))
            baseword_feats_dict['token_type'] = 'baseword'
            clitic_feats_list.append(baseword_feats_dict)
        else:
            clitic_order = get_clitic_order(token)
            # handling an edge case where lA is negative
            if token == 'لِ+' and \
                (stem_feats == {'pos': 'conj_sub', 'prc3': '0', 'prc2': '0', 'prc1': '0', 'prc0': 'na', 'enc0': 'lA_neg', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'}
                or stem_feats == {'pos': 'conj_sub', 'prc3': '0', 'prc2': 'fa_conj', 'prc1': '0', 'prc0': 'na', 'enc0': 'lA_neg', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'} 
                or stem_feats == {'pos': 'conj_sub', 'prc3': '0', 'prc2': 'wa_part', 'prc1': '0', 'prc0': 'na', 'enc0': 'lA_neg', 'asp': 'na', 'vox': 'na', 'mod': 'na', 'gen': 'na', 'num': 'na', 'stt': 'na', 'cas': 'na', 'per': 'na', 'rat': 'na'} 
                ):
                    stem_feats['prc1'] = 'li_prep'
            
            r13_fixes(token, stem_feats)
            
            clitic_feats_list.append(get_clitic_feats(token.replace('+', ''), clitic_order, clitic_feats, stem_feats))

    feats_df = pd.DataFrame(clitic_feats_list)
    assert tokens_df.shape[0] == feats_df.shape[0], f'token-feature mismatch!,\ntokens: \n{tokens_df},\n\n features: \n{feats_df}'
    
    return pd.concat([tokens_df, feats_df], axis=1)

def get_lemmas(lemma, tokens):
    lemmas = []
    for token in tokens:
        if '+' in token:
            lemmas.append(token)
        else:
            lemmas.append(lemma)
    return lemmas

def get_main_features_df(word_analysis):
    # if there are no clitics
    if '+' not in word_analysis['catib6']:
        tokens = [word_analysis['atbtok']]
        catib6 = [word_analysis['catib6']]
        ud = [word_analysis['ud']]
        lemmas = [word_analysis['lex']]
    else:    
        tokens = word_analysis['atbtok'].split('_')
        catib6 = word_analysis['catib6'].split('+')
        ud = word_analysis['ud'].split('+')
        lemmas = get_lemmas(word_analysis['lex'], tokens)
    
    if len(catib6) < len(tokens):
        print(tokens)
        print(catib6)
        catib6.append("NOM")
        ud.append("NOUN")
        return pd.DataFrame({'token': tokens, 'catib6': catib6, 'ud': ud, 'lemma': lemmas})
    try:
        return pd.DataFrame({'token': tokens, 'catib6': catib6, 'ud': ud, 'lemma': lemmas})
    except:
        print('Discrepency in length of token, catib6, and/or ud list')
        print(f'Lengths: token = {len(tokens)}, catib6 = {len(catib6)}, ud = {len(ud)}')
        assert False

def get_word_features_df(word_analysis, clitic_feats):
    """if a word is composed of multiple tokens, return them all.
    otherwise, just return the word and catib6 tag

    Args:
        word_analysis (dict): analysis generated from a cameltools disambiguator

    Returns:
        List[tuple]: a list of one or more tokens
    """
    # gets forms, tokens, feats, ...
    main_feats = get_main_features_df(word_analysis)
    stem_feats = get_stem_feats(word_analysis)
    return add_remaining_features(main_feats, stem_feats, clitic_feats)

def join_feats(word_feats_df, tagset):
    word_features = {
        'tokens': list(word_feats_df['token']),
        'pos_tags': list(word_feats_df[tagset]),
        'lemmas': list(word_feats_df['lemma']),
    }
    
    word_feats_df.drop(['token', tagset, 'lemma'], axis=1, inplace=True)
    feats = word_feats_df.to_dict('records')
    word_features['feats'] = [feats_dict_to_string(row) for row in feats]

    return word_features

def update_sentence_features(sentence_features, word_features):
    sentence_features['tokens'] += word_features['tokens']
    sentence_features['lemmas'] += word_features['lemmas']
    sentence_features['pos_tags'] += word_features['pos_tags']
    sentence_features['feats'] += word_features['feats']
    
    return sentence_features

def build_token_list(sentence_features):
    return [
        (idx, dediac_ar(token), lemma, pos_tag, '_', feats, '_', '_', '_', '_')
        for idx, (token, lemma, pos_tag, feats) in enumerate(
            zip(sentence_features['tokens'], sentence_features['lemmas'], sentence_features['pos_tags'], sentence_features['feats'])
        , 1)
    ]

def to_conll_fields_list(sentence_analysis_list: List[List[dict]], clitic_feats, tagset):
    sentence_features_list = []
    
    for sentence_analysis in sentence_analysis_list:
        sentence_features = {'tokens': [], 'lemmas': [], 'pos_tags': [], 'feats': []}
        for word_analysis in sentence_analysis:
            word_features_df = get_word_features_df(word_analysis, clitic_feats)
            
            word_features = join_feats(word_features_df, tagset)
            sentence_features = update_sentence_features(sentence_features, word_features)
        token_list = build_token_list(sentence_features)
        sentence_features_list.append(token_list)
    
    return sentence_features_list
