

# class BertDisambiguatorAdapter:
#     pass

from camel_tools.disambig.bert import BERTUnfactoredDisambiguator

def create_bert_disambiguator(analyzer):
    model = BERTUnfactoredDisambiguator.pretrained("msa", top=1000, pretrained_cache=False)
    model._analyzer = analyzer
    return model
