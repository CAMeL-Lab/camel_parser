""" Script used to set up different parts of the text_to_conll_cli.py"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download

def download_default_models(model_path: Path) -> None:
    # check if models folder exists
    if not os.path.exists(model_path):
        os.mkdir(model_path)

    # check if default models exist
    if not os.path.exists(model_path / "CAMeLBERT-CATiB-biaffine.model"):
        print('downloading catib model')
        hf_hub_download(repo_id="CAMeL-Lab/camelbert-catib-parser", filename="CAMeLBERT-CATiB-biaffine.model", local_dir=model_path)
    if not os.path.exists(model_path / "CAMeLBERT-UD-biaffine.model"):
        print('downloading ud model')
        hf_hub_download(repo_id="CAMeL-Lab/camelbert-ud-parser", filename="CAMeLBERT-UD-biaffine.model", local_dir=model_path)
    print('Default models downloaded.')

def get_model_name(parse_model: str, model_path: Path) -> str:
    if parse_model == "catib":
        if os.path.exists(model_path / "CAMeLBERT-CATiB-biaffine.model"):
            return "CAMeLBERT-CATiB-biaffine.model"
        else:
            assert False, "CATiB default model not found. Did you run 'python download_models'?"
    elif parse_model == "ud":
        if os.path.exists(model_path / "CAMeLBERT-UD-biaffine.model"):
            return "CAMeLBERT-UD-biaffine.model"
        else:
            assert False, "UD default model not found. Did you run 'python download_models'?"
    else:
        return parse_model