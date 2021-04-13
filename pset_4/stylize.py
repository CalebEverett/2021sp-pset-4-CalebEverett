import argparse

import mlflow.pytorch
import torch
from PIL import Image
from torchvision import transforms


def load_image(filename, size=None, scale=None):
    img = Image.open(filename).convert("RGB")
    if size is not None:
        img = img.resize((size, size), Image.ANTIALIAS)
    elif scale is not None:
        img = img.resize(
            (int(img.size[0] / scale), int(img.size[1] / scale)), Image.ANTIALIAS
        )
    return img


def save_image(filename, data):
    img = data.clone().clamp(0, 255).numpy()
    img = img.transpose(1, 2, 0).astype("uint8")
    img = Image.fromarray(img)
    img.save(filename)


def stylize(args):
    content_image = load_image(args.content_image, scale=args.content_scale)
    content_transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Lambda(lambda x: x.mul(255))]
    )
    content_image = content_transform(content_image)
    content_image = content_image.unsqueeze(0)

    with torch.no_grad():
        style_model = mlflow.pytorch.load_model(args.style_model)

        output = style_model(content_image)
        save_image(args.output_image, output[0])


def main():
    arg_parser = argparse.ArgumentParser(
        description="parser for fast-neural-style with mlflow"
    )

    arg_parser.add_argument(
        "--content_image",
        type=str,
        required=True,
        help="path to content image you want to stylize",
    )
    arg_parser.add_argument(
        "--content_scale",
        type=float,
        default=None,
        help="factor for scaling down the content image",
    )
    arg_parser.add_argument(
        "--output_image",
        type=str,
        required=True,
        help="path for saving the output image",
    )
    arg_parser.add_argument(
        "--style_model",
        type=str,
        required=True,
        help=("saved Mlflow model to be used for stylizing the image."),
    )

    args = arg_parser.parse_args()

    stylize(args)


if __name__ == "__main__":
    main()
