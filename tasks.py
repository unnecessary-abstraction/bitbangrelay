# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

from invoke import task


@task
def install(c):
    """Install the project locally"""
    c.run("pip install .")


@task
def build(c):
    """Build the project"""
    c.run("python3 -m build .")


@task
def clean(c):
    """Remove build output"""
    c.run("rm -rf build dist src/*.egg-info")


@task
def check(c):
    """Check the code for errors"""
    c.run("pre-commit run -a")
