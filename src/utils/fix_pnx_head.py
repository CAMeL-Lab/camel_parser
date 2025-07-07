



def fix_pnx_parent(row, conllx_df):
    if row.UPOS != 'PNX' and conllx_df[conllx_df.ID == row.HEAD].iloc[0].UPOS == 'PNX':
        return 0
    return row.HEAD

def pnx_head_fix(conllx_df):
    "If a token that is not a PNX attaches to a token that is a PNX, adjust the attachment such that it attaches to ROOT"
    conllx_df.HEAD = conllx_df.apply(fix_pnx_parent, axis=1, args=(conllx_df,))
    return conllx_df