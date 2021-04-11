#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from pathlib import Path
from unittest import TestCase

import boto3
from luigi import build
from luigi.contrib.s3 import S3Client
from moto import mock_s3

from pset_4 import Stylize

AWS_ACCESS_KEY = "XXXXXXXXXXXXXXXXXXXX"
AWS_SECRET_KEY = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
AWS_SESSION_TOKEN = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"


def create_bucket():
    conn = boto3.resource("s3", region_name="us-east-1")
    # We need to create the bucket since this is all in Moto's 'virtual' AWS account
    conn.create_bucket(Bucket="mybucket")
    return conn


class StylizeTests(TestCase):
    def setUp(self):
        self.mock_s3 = mock_s3()
        self.mock_s3.start()
        self.addCleanup(self.mock_s3.stop)
        self.stylize_args = dict(
            bucket="mybucket",
            s3_image_path="luigi.jpg",
            local_image_path="temp/luigi.jpg",
            s3_model_path="mosaic.pth",
            local_model_path="temp/mosaic.pth",
            local_output_path="temp/luigi_mosaic.jpg",
        )

    def test_stylize(self):
        """Ensure Stylize Task completes successfully and produces the
        correct output."""

        client = S3Client(AWS_ACCESS_KEY, AWS_SECRET_KEY)
        create_bucket()
        client.put("tests/luigi.jpg", "s3://mybucket/luigi.jpg")
        client.put("tests/mosaic.pth", "s3://mybucket/mosaic.pth")
        result = build(
            [Stylize(**self.stylize_args)],
            local_scheduler=True,
        )

        # Check to make sure the task completed correctly
        self.assertEqual(result, True)

        # Check to make sure neuralstyle produced the correct output
        with open(self.stylize_args["local_output_path"], "rb") as f:
            hash = hashlib.md5(f.read()).hexdigest()
            self.assertEqual(hash, "bba7bfe92f1c89d1ef6b28aaf97b6b2b")

        # Cleanup
        for p in Path("temp").iterdir():
            p.unlink()
        Path("temp").rmdir()
