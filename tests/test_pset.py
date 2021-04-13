#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
from pathlib import Path
from unittest import TestCase

from luigi import build, execution_summary

from pset_4 import Stylize

SUCCESS = execution_summary.LuigiStatusCode.SUCCESS


class StylizeTests(TestCase):
    def setUp(self):
        self.stylize_args = dict(
            bucket="caleb-cscie29",
            s3_image_path="pset_4/images/luigi.jpg",
            local_image_path="temp/luigi.jpg",
            local_output_path="temp/luigi_mosaic.jpg",
            style_model="mosaic",
            content_scale=1.0,
            docker_tag="new-style",
            bind_mount=str(Path().parent.absolute()),
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
            self.assertEqual(hash, "bba7bfe92f1c89d1ef6b28aaf97b6b2b")

        # Cleanup
        for p in Path("temp").iterdir():
            p.unlink()
        Path("temp").rmdir()


class PackageModelTests(TestCase):
    def setUp(self):
        self.stylize_args = dict(
            bucket="caleb-cscie29",
            s3_image_path="pset_4/images/luigi.jpg",
            local_image_path="temp/luigi.jpg",
            local_output_path="temp/luigi_mosaic.jpg",
            style_model="mosaic",
            content_scale=1.0,
            docker_tag="new-style",
            bind_mount=str(Path().parent.absolute()),
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
            self.assertEqual(hash, "bba7bfe92f1c89d1ef6b28aaf97b6b2b")

        # Cleanup
        for p in Path("temp").iterdir():
            p.unlink()
        Path("temp").rmdir()
