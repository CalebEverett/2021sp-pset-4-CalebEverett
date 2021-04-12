from csci_utils.luigi import S3DownloadTask, SuffixPreservingLocalTarget
from luigi import Parameter, format
from luigi.contrib.external_program import ExternalProgramTask


class Stylize(ExternalProgramTask):
    bucket = Parameter()
    s3_image_path = Parameter()
    local_image_path = Parameter()
    s3_model_path = Parameter()
    local_model_path = Parameter()
    local_output_path = Parameter()

    def requires(self):
        return {
            "image": S3DownloadTask(
                bucket=self.bucket,
                s3_path=self.s3_image_path,
                local_path=self.local_image_path,
            ),
            "model": S3DownloadTask(
                bucket=self.bucket,
                s3_path=self.s3_model_path,
                local_path=self.local_model_path,
            ),
        }

    def program_args(self):

        return [
            "pipenv",
            "run",
            "python",
            "-m",
            "neural_style",
            "eval",
            "--content-image",
            self.local_image_path,
            "--model",
            self.local_model_path,
            "--output-image",
            self.temp_output_path,
            "--cuda",
            "0",
        ]

    def run(self):
        with self.output().temporary_path() as self.temp_output_path:
            super().run()

    def output(self):
        return SuffixPreservingLocalTarget(
            path=self.local_output_path, format=format.Nop
        )
