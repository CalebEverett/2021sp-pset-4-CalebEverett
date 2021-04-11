import argparse

from luigi import build

from pset_4 import Stylize


# https://stackoverflow.com/a/43357954/5943133
def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


parser = argparse.ArgumentParser(description="Command line interface for Pset 4.")
parser.add_argument("--bucket", default="caleb-cscie29")
parser.add_argument("--s3_image_path", default="pset_4/images/luigi.jpg")
parser.add_argument("--local_image_path", default="pset_4/data/images/luigi.jpg")
parser.add_argument("--s3_model_path", default="pset_4/saved_models/mosaic.pth")
parser.add_argument("--local_model_path", default="pset_4/data/saved_models/mosaic.pth")
parser.add_argument(
    "--local_output_path", default="pset_4/data/images/luigi_mosaic.jpg"
)


def main(args=None):
    args = parser.parse_args(args=args)
    build([Stylize(**vars(args))], local_scheduler=True)
