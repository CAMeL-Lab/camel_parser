

import sys
from typing import List, Union
from pandas import DataFrame

def get_children_ids_of(current_token_id, conllx_df) -> List[int]:
    """Returns a list of ids of the children of the current token.

    Args:
        current_token_id (int): ID of the parent token
        conllx_df (DataFrame): tree data

    Returns:
        List[int]: list of children ids
    """
    # return list(conllx_df[conllx_df['HEAD'] == str(current_token_id)]["ID"])
    return list(conllx_df[conllx_df['HEAD'] == current_token_id]["ID"])

#####

def update_ordered_tokens(
    parent_token_id: int,
    children_ids: List[int], 
    ordered_tokens: List[int]
    ) -> List[int]:
    """Update ordered_tokens list by first combining the parent and children
    ids, sorting them, then replacing the parent in ordered_tokens with the 
    result.

    Args:
        parent_token_id (int): parent id
        children_ids (List[int]): children ids
        ordered_tokens (List[int]): list of ids to determine projectivity

    Returns:
        List[int]: new ordered_tokens list
    """
    parent_and_children_ids = children_ids.copy()
    parent_and_children_ids.append(parent_token_id)
    temp_list = sorted(parent_and_children_ids)
    p_tok_location = ordered_tokens.index(parent_token_id)
    return ordered_tokens[:p_tok_location] + temp_list + ordered_tokens[p_tok_location+1:]

def get_projectivity_list(current_token_id: int, conllx_df: DataFrame, ordered_tokens: List[int] = None) -> List[int]:
    """projectivity algorithm
    let ordered_tokens be the final list to check for projectivity
    let root be p_tok (for parent token)
    let children of p_tok be c_tok_list
    if c_tok_list is empty
        return the list of ordered_tokens
    else
        get order of p_tok and c_tok_list and update ordered_tokens
        run alg on each child, passing ordered_tokens
        the return value is ordered_tokens

    Args:
        current_token_id (int): parent id
        conllx_df (DataFrame): dependency tree DataFrame
        ordered_tokens (List[int], optional): list of tokens in projective order. Defaults to [0].

    Returns:
        List[int]: [description]
    """
    if ordered_tokens is None:
        ordered_tokens = [0]
    children = get_children_ids_of(current_token_id, conllx_df)
    if not children:
        return ordered_tokens
    
    try:
        ordered_tokens = update_ordered_tokens(current_token_id, children, ordered_tokens)
    except:
        import pdb; pdb.set_trace()
    
    for child in children:
        ordered_tokens = get_projectivity_list(child, conllx_df, ordered_tokens)
    return ordered_tokens
    

def projective_checker(conllx_df: DataFrame) -> dict:
    """Given a tree DataFrame, determine whether or not it is projective.

    Args:
        conllx_df (DataFrame): a dependency tree DataFrame

    Returns:
        dict: key is PROJECTIVITY, value is true or false
    """
    proj_list = get_projectivity_list(0, conllx_df)
    # return {'PROJECTIVITY': list(range(len(proj_list))) == proj_list}
    if proj_list != list(range(len(proj_list))):
        return [{"flagged_issue": "FLAG_NONPROJECTIVE"}]
    else:
        return []
    # return list(range(len(proj_list))) == proj_list


#########

def is_possible_parent_behind(token_id: int, conllx_df: DataFrame) -> bool:
    # checks if the comma is connected to the token ahead of it
    token_dict = conllx_df[conllx_df['ID'] == token_id].to_dict('records')[0]
    return token_dict['ID'] < int(token_dict['HEAD'])

def can_move_token(token_id, new_parent_id, conllx_df: DataFrame) -> bool:
    # sourcery skip: return-identity
    # performs the following checks:
    # is the the token a root?
    if new_parent_id == 0:
        return False
    # is the the token ahead of the comma?
    if new_parent_id > token_id:
        return False
    # does connecting to the token cause non-projectivity?
    temp_df = conllx_df.copy()
    temp_df = update_comma_head(token_id, new_parent_id, temp_df)
    if projective_checker(temp_df):
        return False
    
    return True

def get_parent_id(current_token_id: int, conllx_df: DataFrame) -> int:
    """gets the id of the parent of the curent token

    Args:
        current_token_id (int): token id
        conllx_df (DataFrame): dependency tree

    Returns:
        int: parent id
    """
    if current_token_id == 0: # the comma is the first token, so parent is an invalid ID of 0
        # import pdb; pdb.set_trace()
        # keep the comma pointing to current token
        return int(conllx_df[conllx_df['ID'] == 1].to_dict('records')[0]['HEAD'])

    return int(conllx_df[conllx_df['ID'] == current_token_id].to_dict('records')[0]['HEAD'])

def update_comma_head(comma_id: int, new_parent_id: int, conllx_df: DataFrame) -> DataFrame:
    """attaches the comma to the new parent

    Args:
        comma_id (int): token id
        new_parent_id (int): the id of the new parent of the comma token
        conllx_df (DataFrame): dependency tree

    Returns:
        DataFrame: updated dependency tree
    """

    conllx_df.iloc[comma_id-1, conllx_df.columns.get_loc('HEAD')] = new_parent_id
    return conllx_df

def get_comma_id_list(conllx_df: DataFrame) -> List[int]:
    """Gets all commas in the sentence

    Args:
        conllx_df (DataFrame): dependency tree DataFrame

    Returns:
        List[int]: list of comma token ids
    """
    comma_tokens = conllx_df[(conllx_df['FORM'] == ',') | (conllx_df['FORM'] == '،')]
    return list(comma_tokens['ID'])

# def fix_comma(comma_id: int, conllx_df: DataFrame) -> Union[DataFrame, Exception]:
def fix_comma(comma_id: int, conllx_df: DataFrame) -> Union[DataFrame, bool]:
    """The algorithm is as follows:
    check if the tree is projective, otherwise raise an exception
    get the token before it
        is the the token a root?
        is the the token ahead of the comma?
        does connecting to the token cause non-projectivity?
    if it is false for all three, connect to the token.
    """
    # tree is not projective (an error list is returned), 
    # so return conllx_df without fixing commas
    if projective_checker(conllx_df):
        return conllx_df
        # TODO: raise Exception('tree is not projective')
    # initial new parent is the token before the comma token
    new_parent_id = comma_id - 1

    # the default will be the previous token.
    # if the comma is the first token in the sentence, don't change the parent.
    while True:
        # test the parent of the previous token
        possible_parent_id = get_parent_id(new_parent_id, conllx_df)
        if not can_move_token(comma_id, possible_parent_id, conllx_df):
            break # we can no longer move the token
        else:
            # if we can move the token, update the new parent id
            new_parent_id = possible_parent_id
    
    # conllx_df = update_comma_head(comma_id, new_parent_id, conllx_df)
    return update_comma_head(comma_id, new_parent_id, conllx_df)

def fix_commas(conllx_df):
    comma_list = get_comma_id_list(conllx_df)
    for comma_id in comma_list:
        data = fix_comma(comma_id, conllx_df)
        if type(data) is bool:
            return True
        conllx_df = data
    return conllx_df

def fix_sentence_commas(df):
    # for sentence in sen_list:
    data = fix_commas(df)
    if type(data) is bool:
        print('nonprojective sentence', file=sys.stderr)
        return df
    return data