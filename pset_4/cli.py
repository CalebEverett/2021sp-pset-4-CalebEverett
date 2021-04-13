import argparse

from luigi import build

from pset_4 import Stylize

parser = argparse.ArgumentParser(description="Command line interface for Pset 4.")
parser.add_argument("--bucket", default="caleb-cscie29")
parser.add_argument("--s3_image_path", default="pset_4/images/luigi.jpg")
parser.add_argument("--local_image_path", default="pset_4/images/luigi.jpg")
parser.add_argument("--local_output_path", default="pset_4/images/luigi_mosaic.jpg")
parser.add_argument(
    "--style_model",
    default="mosaic",
    choices=["candy", "mosaic", "rain_princess", "udnie"],
)
parser.add_argument("--content_scale", default=1.0, type=float)
parser.add_argument("--docker_tag", default="new-style")
parser.add_argument("--bind_mount")


def main(args=None):
    args = parser.parse_args(args=args)
    build([Stylize(**vars(args))], local_scheduler=True)
