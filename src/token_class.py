from dataclasses import dataclass


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