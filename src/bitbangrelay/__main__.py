# Copyright (c) 2021-2022 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse

from . import __progname__, __description__, __version__
from .relay import Relay, Channel


def parse_args():
    parser = argparse.ArgumentParser(prog=__progname__, description=__description__)
    parser.add_argument(
        "--version", action="version", version=f"{__progname__} {__version__}"
    )
    parser.add_argument(
        "-c",
        "--config-file",
        help="Config file to load, defaults to ~/.config/bitbangrelay.yml",
    )
    parser.add_argument(
        "-d",
        "--device",
        default="default",
        help="Relay device to control, defaults to 'default'",
    )
    parser.add_argument("channel", help="Relay channel to control")
    parser.add_argument("action", help="Action to perform: 'on', 'off' or 'cycle'")
    return parser.parse_args()


def main():
    args = parse_args()

    relay = Relay(config_file=args.config_file, device_name=args.device)
    if args.channel == "all":
        if args.action in ["on", "1"]:
            relay.all_on()
        elif args.action in ["off", "0"]:
            relay.all_off()
        elif args.action == "cycle":
            relay.all_cycle()
        else:
            raise NotImplementedError
    else:
        channel = Channel(relay, args.channel)
        if args.action in ["on", "1"]:
            channel.on()
        elif args.action in ["off", "0"]:
            channel.off()
        elif args.action == "cycle":
            channel.cycle()
        else:
            raise NotImplementedError


if __name__ == "__main__":
    main()
