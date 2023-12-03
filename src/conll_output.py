

import re


def print_to_conll(sentence_tuples, annotations=None, sentences=None):
    if sentences is not None: 
        sentences = list(filter(lambda x : len(re.sub(r"\s+", "", x, flags=re.UNICODE)) > 0, sentences))
    tokens = [[tup[1] for tup in sent] for sent in sentence_tuples]
    for i in range(len(sentence_tuples)):
        if sentences != None:
            print(f"# text = {sentences[i].strip()}")
            print(f"# treeTokens = {' '.join(tokens[i])}")
        elif annotations != None:
            [print(annotation) for annotation in annotations[i]]
        print("\n".join(["\t".join([str(i) for i in tup]) for tup in sentence_tuples[i]])+"\n")
