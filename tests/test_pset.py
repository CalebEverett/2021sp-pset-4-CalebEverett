#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import hashlib
import shutil
from pathlib import Path
from unittest import TestCase

from luigi import build, execution_summary

from pset_4 import Stylize
from pset_4.package_models.package_models import create_mlflow_model
from pset_4.stylize import stylize

SUCCESS = execution_summary.LuigiStatusCode.SUCCESS


class StylizeTests(TestCase):
    def setUp(self):
        self.stylize_args = dict(
            bucket="caleb-cscie29",
            s3_image_path="pset_4/images/luigi.jpg",
            local_image_path="temp/luigi.jpg",
            local_output_path="temp/luigi_mosaic.jpg",
            style_model="mosaic",
            docker_tag="new-style",
        )

    def test_stylize(self):
        """Ensure Stylize Task completes successfully and produces the
        correct output."""

        result = build(
            [Stylize(**self.stylize_args)], local_scheduler=True, detailed_summary=True
        )

        # Check to make sure the task completed correctly
        self.assertEqual(result.status, SUCCESS)

        # Check to make sure neuralstyle produced the correct output
        with open(self.stylize_args["local_output_path"], "rb") as f:
            hash = hashlib.md5(f.read()).hexdigest()
            print(hash, "bba7bfe92f1c89d1ef6b28aaf97b6b2b")
            self.assertEqual(hash, "bba7bfe92f1c89d1ef6b28aaf97b6b2b")

        # Cleanup
        for p in Path("temp").iterdir():
            p.unlink()
        Path("temp").rmdir()


class PackageModelTests(TestCase):
    def test_create_model(self):
        """Ensure model is created correctly."""

        create_mlflow_model(Path("tests/mosaic.pth"), "temp")

        args = argparse.Namespace(
            content_image="tests/luigi.jpg",
            output_image="temp/luigi_mosaic.jpg",
            style_model="temp/mosaic",
            content_scale=None,
        )

        stylize(args)

        # Check to make sure neuralstyle produced the correct output
        with open(args.output_image, "rb") as f:
            hash = hashlib.md5(f.read()).hexdigest()
            print(hash)
            self.assertEqual(hash, "bba7bfe92f1c89d1ef6b28aaf97b6b2b")

        # Cleanup
        shutil.rmtree(Path("temp"))
