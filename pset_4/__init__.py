import logging
import os

import docker
from csci_utils.luigi import S3DownloadTask, SuffixPreservingLocalTarget
from luigi import BoolParameter, FloatParameter, Parameter, Task, format

logger = logging.getLogger("luigi-interface")


class Stylize(Task):
    """Task to stylize an image. Will be downloaded from s3 first if it doesn't exist
    locally. Image is stylized using mlflow models in an isolated environment within
    a Docker container. The image for the Docker container will be built if it doesn't
    already existing, including the packaging of Pytorch to mflow format.
    """

    bucket = Parameter(description="S3 bucket where image is stored.")
    s3_image_path = Parameter(
        description="Path to image inside of bucket without s://."
    )
    local_image_path = Parameter(
        description="Path where the image should be downloaded to."
    )
    local_output_path = Parameter(description="Path to write stylized image to.")
    style_model = Parameter(description="Model to use for stylizing.")
    content_scale = FloatParameter(
        description="Scaling factor to apply to original image.", default=None
    )
    docker_tag = Parameter(
        default="new-style", description="Tag to apply to Docker image."
    )
    bind_mount = Parameter(
        description=(
            "Local path to mount Docker container to so it can access local images"
            " and write the stylized image."
        ),
        default=os.getcwd(),
    )
    force = BoolParameter(
        description=(
            "Set to True to force download of file from S3 even"
            "if it already exists locally"
        ),
        default=False,
    )

    def requires(self):
        return S3DownloadTask(
            bucket=self.bucket,
            s3_path=self.s3_image_path,
            local_path=self.local_image_path,
            force=self.force,
        )

    def run(self):
        client = docker.from_env()

        logger.info("Building Docker image.")
        client.images.build(path="pset_4", tag=self.docker_tag, nocache=False)

        logger.info("Styling image.")
        with self.output().temporary_path() as self.temp_output_path:

            command = [
                "--content_image",
                f"data/{self.local_image_path}",
                "--output_image",
                f"data/{self.temp_output_path}",
                "--style_model",
                f"models/{self.style_model}",
            ]

            if self.content_scale is not None:
                command.extend(["--content_scale", self.content_scale])

            client.containers.run(
                self.docker_tag,
                command=command,
                volumes={self.bind_mount: {"bind": "/data", "mode": "rw"}},
            )

    def output(self):
        return SuffixPreservingLocalTarget(
            path=self.local_output_path, format=format.Nop
        )
