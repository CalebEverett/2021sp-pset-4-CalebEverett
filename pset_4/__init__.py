import logging
import os

import docker
from csci_utils.luigi import S3DownloadTask, SuffixPreservingLocalTarget
from luigi import FloatParameter, Parameter, Task, format

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
        description="Scaling factor to apply to original image.", default=1.0
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

    def requires(self):
        return S3DownloadTask(
            bucket=self.bucket,
            s3_path=self.s3_image_path,
            local_path=self.local_image_path,
        )

    def run(self):
        client = docker.from_env()

        logger.info("Building Docker image.")
        client.images.build(path="pset_4", tag=self.docker_tag, nocache=False)

        logger.info("Styling image.")
        with self.output().temporary_path() as self.temp_output_path:
            client.containers.run(
                self.docker_tag,
                command=[
                    "--content_image",
                    f"data/{self.local_image_path}",
                    "--output_image",
                    f"data/{self.temp_output_path}",
                    "--style_model",
                    f"models/{self.style_model}",
                ],
                volumes={self.bind_mount: {"bind": "/data", "mode": "rw"}},
            )

    def output(self):
        return SuffixPreservingLocalTarget(
            path=self.local_output_path, format=format.Nop
        )
