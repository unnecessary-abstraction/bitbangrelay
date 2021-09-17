<!--
Copyright (c) 2021 SanCloud Ltd
SPDX-License-Identifier: CC-BY-4.0
-->

[![build-and-test](https://github.com/SanCloudLtd/bitbangrelay/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/SanCloudLtd/bitbangrelay/actions/workflows/build-and-test.yml)

# bitbangrelay

A simple tool for controlling USB relay boards
based around an FTDI FT232R/FT245R chip in bitbang mode,
for example SainSmart 4 or 8 channel USB relay modules.

Copyright (c) 2021 SanCloud Ltd.

Code distributed under the
[Apache 2.0 License](https://choosealicense.com/licenses/apache-2.0/),
documentation distributed under the
[CC BY 4.0 License](https://creativecommons.org/licenses/by/4.0/).

---

**NOTE:** This project is a work in progress,
documentation and testing are currently very limited.
If this project is useful to you,
please let us know how it can be improved.

---

## Configuration

The bitbangrelay library parses a configuration file in yaml syntax
to determine the available relay devices and channels.

Example configuration:

```yaml
# Top level keys give names for the available relay devices. A relay device
# named "default" will be the default if no other device name is given.
default:

    # The id is required for each relay device. This is passed to pylibftdi
    # to select the appropriate USB device and is typically the device's
    # serial number.
    id: AAAAAAAA

    # The number of channels supported by the relay device. If this is not
    # provided then it is assumed that 8 channels are available.
    channels: 4

    # Channels can be selected by index or by alias. A dictionary mapping
    # alises to channel numbers may be provided for convenience.
    aliases:
        bbe: 0
        bbe-lite: 1
        beaglebone-black: 2
        raspberrypi4: 3
```

## Command Line Interface

```
usage: bitbangrelay [-h] [--version] [-c CONFIG_FILE] [-d DEVICE] channel action

USB BitBang Relay Controller

positional arguments:
  channel               Relay channel to control
  action                Action to perform: 'on', 'off' or 'cycle'

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -c CONFIG_FILE, --config-file CONFIG_FILE
                        Config file to load, defaults to ~/.config/bitbangrelay.yml
  -d DEVICE, --device DEVICE
                        Relay device to control, defaults to 'default'
```

### Example usage

* To turn on a channel: `bitbangrelay bbe on`

* To turn off a channel: `bitbangrelay bbe off`

* To power cycle a channel: `bitbangrelay bbe cycle`
  * The connected device will be powered off and then
    5 seconds later it will be powered back on.

* To turn off all channels of a relay: `bitbangrelay all off`

## Dependencies

bitbangrelay relies on the following Python modules:

* [PyYAML](https://pypi.org/project/PyYAML/)
  for config file parsing.

* [pylibftdi](https://pypi.org/project/pylibftdi/)
  for interacting with FTDI devices.

  * Note that the C library libftdi must be installed separately
    for pylibftdi to import correctly.
