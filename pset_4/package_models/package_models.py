import os
import re
import zipfile
from pathlib import Path

import mlflow.pytorch
import torch
from torch.hub import download_url_to_file

from .transformer_net import TransformerNet


def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        zf.extractall(path=dest_dir)


def create_mlflow_model(
    state_dict_path: Path, output_dir: str, model: torch.nn.Module = TransformerNet()
):
    """Creates an mflow packaged model from a Pytorch state dict and model.
    Saves the model in a directory with the name of the file in the state_dict_path
    without extension.

    Args:
        state_dict_path: Path to pytorch state dict that can be loaded into `model`
        model: Pytorch model
        output_dir: Directory that mlflow models will be created in
    """

    output_dir = Path(f"{output_dir}/{state_dict_path.stem}")

    with torch.no_grad():
        style_model = model
        state_dict = torch.load(state_dict_path)
        # remove saved deprecated running_* keys in InstanceNorm from the checkpoint
        for k in list(state_dict.keys()):
            if re.search(r"in\d+\.running_(mean|var)$", k):
                del state_dict[k]
        style_model.load_state_dict(state_dict)
        style_model.to("cpu")

        mlflow.pytorch.save_model(style_model, path=output_dir)


def main():
    download_url_to_file(
        "https://www.dropbox.com/s/lrvwfehqdcxoza8/saved_models.zip?dl=1",
        "saved_models.zip",
        None,
        True,
    )
    unzip("saved_models.zip", ".")

    print(os.getcwd())

    for p in Path("saved_models").glob("*.pth"):
        create_mlflow_model(p, "models")


if __name__ == "__main__":
    main()
