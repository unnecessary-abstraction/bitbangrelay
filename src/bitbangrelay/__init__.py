# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse


__progname__ = "bitbangrelay"
__version__ = "0.1.0"


def parse_args():
    parser = argparse.ArgumentParser(
        prog=__progname__, description="USB BitBang Relay Controller"
    )
    parser.add_argument(
        "--version", action="version", version=f"{__progname__} {__version__}"
    )
    return parser.parse_args()


def main():
    parse_args()
