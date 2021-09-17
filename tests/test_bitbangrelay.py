# Copyright (c) 2021 SanCloud Ltd
# SPDX-License-Identifier: Apache-2.0

from bitbangrelay import Relay, Channel


class DummyDeviceClass:
    def __init__(self, ident):
        self.ident = ident
        self.direction = 0
        self.port = 0


def test_on_off():
    config = {
        "id": "12345678",
        "channels": 8,
        "aliases": {
            "test_a": 0,
            "test_b": 3,
        },
    }

    relay = Relay(config=config, device_class=DummyDeviceClass)
    ch_a = relay["test_a"]
    ch_b = Channel(relay, "test_b")
    ch_c = relay[5]
    ch_d = Channel(relay, 6)

    assert relay.device.port == 0
    ch_a.on()
    assert relay.device.port == 0b00000001
    ch_b.on()
    assert relay.device.port == 0b00001001
    ch_c.set(True)
    assert relay.device.port == 0b00101001
    ch_a.cycle(1)
    assert relay.device.port == 0b00101001
    ch_b.off()
    assert relay.device.port == 0b00100001
    ch_d.off()
    assert relay.device.port == 0b00100001
    ch_d.on()
    assert relay.device.port == 0b01100001
    ch_a.set(False)
    assert relay.device.port == 0b01100000
    relay.all_off()
    assert relay.device.port == 0
    relay.all_on()
    assert relay.device.port == 0xFF
    relay.all_cycle(1)
    assert relay.device.port == 0xFF
