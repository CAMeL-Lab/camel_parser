from types import MethodType
from typing import List, Union, Dict

import torch
from supar import Dependency2oCRF, DependencyCRF, MatrixTree, Parser
from supar.utils import Dataset
from supar.utils.transform import CoNLL

from camel_tools.utils.dediac import dediac_ar

from ..logger import log

"""
conll object from parser
iterate over sentences from this object
iterate over the columns per sentence
create token rows
create conll sentence of token row tuples

"""

def parser_conll_to_conll_tuples(parser_conll: Dataset) -> List[List[tuple]]:
    conll_sentences = []
    for parser_sentence in parser_conll:
        sentence_tree_token_tuples = []
        for i in range(len(parser_sentence.values[0])):
            token_tuple_row = tuple(column[i] for column in parser_sentence.values)
            sentence_tree_token_tuples.append(token_tuple_row)
        conll_sentences.append(sentence_tree_token_tuples)
    return conll_sentences

def filter_tatweel(form):
    if form.replace("_", "").replace("\u0640","").replace("\u005F", "") == "":
        return form
    return form.replace("_", "").replace("\u0640","").replace("\u005F", "")


def enable_multiroot_decoding(dependency_parser: Parser) -> None:
    """Configure a loaded SuPar parser for projective multi-root decoding.

    SuPar's stock tree decoder and CRF marginals assume a single token attached
    to the artificial root. This replaces the relevant prediction methods so
    that both MBR inference and tree repair accept multiple roots while keeping
    the projectivity constraint requested by :func:`parse`.
    """

    def decode_first_order(self, s_arc, s_rel, mask, tree=False, proj=False):
        lens = mask.sum(1)
        arc_preds = s_arc.argmax(-1)
        bad = [
            not CoNLL.istree(seq[1:i + 1], proj=proj, multiroot=True)
            for i, seq in zip(lens.tolist(), arc_preds.tolist())
        ]
        if tree and any(bad):
            distribution = DependencyCRF if proj else MatrixTree
            arc_preds[bad] = distribution(
                s_arc[bad],
                mask[bad].sum(-1),
                multiroot=True,
            ).argmax
        rel_preds = s_rel.argmax(-1).gather(
            -1,
            arc_preds.unsqueeze(-1),
        ).squeeze(-1)
        return arc_preds, rel_preds

    def decode_second_order(
        self,
        s_arc,
        s_sib,
        s_rel,
        mask,
        tree=False,
        mbr=True,
        proj=False,
    ):
        lens = mask.sum(1)
        arc_preds = s_arc.argmax(-1)
        bad = [
            not CoNLL.istree(seq[1:i + 1], proj=proj, multiroot=True)
            for i, seq in zip(lens.tolist(), arc_preds.tolist())
        ]
        if tree and any(bad):
            if proj:
                arc_preds[bad] = Dependency2oCRF(
                    (s_arc[bad], s_sib[bad]),
                    mask[bad].sum(-1),
                    multiroot=True,
                ).argmax
            else:
                arc_preds[bad] = MatrixTree(
                    s_arc[bad],
                    mask[bad].sum(-1),
                    multiroot=True,
                ).argmax
        rel_preds = s_rel.argmax(-1).gather(
            -1,
            arc_preds.unsqueeze(-1),
        ).squeeze(-1)
        return arc_preds, rel_preds

    @torch.no_grad()
    def crf_pred_step(self, batch):
        distribution = DependencyCRF if self.args.proj else MatrixTree
        words, _, *feats = batch
        mask, lens = batch.mask, batch.lens - 1
        mask[:, 0] = 0
        s_arc, s_rel = self.model(words, feats)
        if self.args.mbr:
            s_arc = distribution(
                s_arc,
                lens,
                multiroot=True,
            ).marginals
        arc_preds, rel_preds = self.model.decode(
            s_arc,
            s_rel,
            mask,
            self.args.tree,
            self.args.proj,
        )
        lengths = lens.tolist()
        batch.arcs = [i.tolist() for i in arc_preds[mask].split(lengths)]
        batch.rels = [
            self.REL.vocab[i.tolist()]
            for i in rel_preds[mask].split(lengths)
        ]
        if self.args.prob:
            arc_probs = s_arc if self.args.mbr else s_arc.softmax(-1)
            batch.probs = [
                prob[1:i + 1, :i + 1].cpu()
                for i, prob in zip(lengths, arc_probs.unbind())
            ]
        return batch

    @torch.no_grad()
    def crf2o_pred_step(self, batch):
        words, _, *feats = batch
        mask, lens = batch.mask, batch.lens - 1
        mask[:, 0] = 0
        s_arc, s_sib, s_rel = self.model(words, feats)
        if self.args.mbr:
            s_arc, s_sib = Dependency2oCRF(
                (s_arc, s_sib),
                lens,
                multiroot=True,
            ).marginals
        arc_preds, rel_preds = self.model.decode(
            s_arc,
            s_sib,
            s_rel,
            mask,
            self.args.tree,
            self.args.mbr,
            self.args.proj,
        )
        lengths = lens.tolist()
        batch.arcs = [i.tolist() for i in arc_preds[mask].split(lengths)]
        batch.rels = [
            self.REL.vocab[i.tolist()]
            for i in rel_preds[mask].split(lengths)
        ]
        if self.args.prob:
            arc_probs = s_arc if self.args.mbr else s_arc.softmax(-1)
            batch.probs = [
                prob[1:i + 1, :i + 1].cpu()
                for i, prob in zip(lengths, arc_probs.unbind())
            ]
        return batch

    parser_name = dependency_parser.NAME
    if parser_name == "crf2o-dependency":
        dependency_parser.model.decode = MethodType(
            decode_second_order,
            dependency_parser.model,
        )
        dependency_parser.pred_step = MethodType(
            crf2o_pred_step,
            dependency_parser,
        )
    else:
        dependency_parser.model.decode = MethodType(
            decode_first_order,
            dependency_parser.model,
        )
        if parser_name == "crf-dependency":
            dependency_parser.pred_step = MethodType(
                crf_pred_step,
                dependency_parser,
            )


@log
def parse(
    conll_path_or_parsed_tuples: Union[List[List[tuple]], str],
    parse_model: str,
    multiroot: bool = True,
) -> List[List[tuple]]:
    parser = Parser.load(parse_model)
    if multiroot:
        enable_multiroot_decoding(parser)
    return parser.predict(conll_path_or_parsed_tuples, verbose=False, tree=True, proj=True)


def parse_text_tuples(
    sentence_tuples: List[List[tuple]],
    parse_model,
    multiroot: bool = True,
) -> List[List[tuple]]:
    sentence_tuples = [[val[1:4] for val in sent] for sent in sentence_tuples]
    form_lemma_pos_tuple = [[(filter_tatweel(dediac_ar(val[0])), filter_tatweel(dediac_ar(val[1])), val[2]) for val in sent] for sent in sentence_tuples]
    conll = parse(
        form_lemma_pos_tuple,
        parse_model=parse_model,
        multiroot=multiroot,
    )
    return parser_conll_to_conll_tuples(conll)

def parse_conll(
    conll_path: str,
    parse_model,
    multiroot: bool = True,
) -> List[List[tuple]]:
    conll = parse(
        conll_path,
        parse_model=parse_model,
        multiroot=multiroot,
    )
    for i, sent in enumerate(conll):
        conll[i].values[1] = [filter_tatweel(form) for form in sent.values[1]]
    return parser_conll_to_conll_tuples(conll)
