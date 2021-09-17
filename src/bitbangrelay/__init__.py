# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import time


__progname__ = "bitbangrelay"
__version__ = "0.1.0"


class Channel:
    def __init__(self, relay, name):
        self.relay = relay
        self.name = name
        if name in self.relay.config.get("aliases", []):
            self.number = self.relay.config["aliases"][name]
        else:
            self.number = int(self.name)

    def on(self):
        return self.relay.set_channel(self.number)

    def off(self):
        return self.relay.clear_channel(self.number)

    def cycle(self, interval=5):
        self.off()
        time.sleep(interval)
        self.on()

    def set(self, value):
        if value:
            self.on()
        else:
            self.off()

    def get(self):
        return self.relay.get_channel(self.number)


class Relay:
    def __init__(
        self, config=None, config_file=None, device_name="default", device_class=None
    ):
        if not device_class:
            import pylibftdi

            device_class = pylibftdi.BitBangDevice

        if config:
            self.config = config
        else:
            import yaml

            if not config_file:
                config_file = os.path.expanduser("~/.config/bitbangrelay.yml")
            with open(config_file, "r") as f:
                self.config = yaml.safe_load(f)[device_name]

        self.device_name = device_name
        self.device = device_class(self.config.get("id"))
        self.device.direction = 0xFF
        self.channels = self.config.get("channels", 8)

    def channel(self, name):
        return Channel(self, name)

    def __getitem__(self, name):
        return self.channel(name)

    def set_channel(self, i):
        if i > self.channels:
            raise IndexError
        self.device.port |= 1 << i

    def clear_channel(self, i):
        if i > self.channels:
            raise IndexError
        self.device.port &= ~(1 << i)

    def get_channel(self, i):
        if i > self.channels:
            raise IndexError
        return bool(self.device.port & (1 << i))

    def all_on(self):
        self.device.port = (1 << self.channels) - 1

    def all_off(self):
        self.device.port = 0

    def all_cycle(self, interval=5):
        self.all_off()
        time.sleep(interval)
        self.all_on()

    def all_set(self, value):
        if value:
            self.all_on()
        else:
            self.all_off()


def main():
    parser = argparse.ArgumentParser(
        prog=__progname__, description="USB BitBang Relay Controller"
    )
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
    args = parser.parse_args()

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
