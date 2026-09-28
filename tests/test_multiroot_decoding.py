from types import SimpleNamespace
from unittest.mock import Mock

import torch

from src.dependency_parser import biaff_parser


def test_multiroot_decoder_keeps_valid_projective_forest():
    dependency_parser = SimpleNamespace(
        NAME="biaffine-dependency",
        model=SimpleNamespace(),
    )
    biaff_parser.enable_multiroot_decoding(dependency_parser)

    # Both tokens prefer the artificial root. This is a valid multi-root
    # projective forest and should therefore not be repaired to one root.
    s_arc = torch.tensor(
        [[[0.0, 0.0, 0.0], [5.0, 0.0, 1.0], [5.0, 1.0, 0.0]]]
    )
    s_rel = torch.zeros(1, 3, 3, 2)
    mask = torch.tensor([[False, True, True]])

    arc_preds, _ = dependency_parser.model.decode(
        s_arc,
        s_rel,
        mask,
        tree=True,
        proj=True,
    )

    assert arc_preds[0, 1:].tolist() == [0, 0]


def test_parse_enables_multiroot_by_default_and_allows_opt_out(monkeypatch):
    multiroot_parser = Mock()
    multiroot_parser.NAME = "biaffine-dependency"
    multiroot_parser.model = SimpleNamespace()
    multiroot_parser.predict.return_value = "multiroot"
    standard_parser = Mock()
    standard_parser.predict.return_value = "standard"
    load = Mock(side_effect=[multiroot_parser, standard_parser])
    monkeypatch.setattr(biaff_parser.Parser, "load", load)

    assert biaff_parser.parse("input.conllx", "model") == "multiroot"
    assert callable(multiroot_parser.model.decode)
    assert biaff_parser.parse(
        "input.conllx",
        "model",
        multiroot=False,
    ) == "standard"

    multiroot_parser.predict.assert_called_once_with(
        "input.conllx",
        verbose=False,
        tree=True,
        proj=True,
    )
    standard_parser.predict.assert_called_once_with(
        "input.conllx",
        verbose=False,
        tree=True,
        proj=True,
    )
