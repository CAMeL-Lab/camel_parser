from pathlib import Path
from src.utils.model_downloader import download_default_models

if __name__ == "__main__":
    download_default_models(Path('models'))