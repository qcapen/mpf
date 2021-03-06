""" Contains the base class for driver-enabled devices."""
# driver_enabled.py
# Mission Pinball Framework
# Written by Brian Madden & Gabe Knuth
# Released under the MIT License. (See license info at the end of this file.)

# Documentation and more info at http://missionpinball.com/mpf

from mpf.devices.driver import Driver


class DriverEnabled(Driver):
    """Represents a "driver-enabled" device in a pinball machine.
    """
    config_section = 'driver_enabled'
    collection = 'driver_enabled'
    class_label = 'driver_enabled'

    enable_driver_mappings = dict()  # k: driver, v: DriverEnabled device list

    @classmethod
    def add_driver_enabled_device(cls, driver, device):
        if driver not in DriverEnabled.enable_driver_mappings:
            DriverEnabled.enable_driver_mappings[driver] = set()

        DriverEnabled.enable_driver_mappings[driver].add(device)

    def __init__(self, machine, name, config, collection=None, validate=True):
        super(DriverEnabled, self).__init__(machine, name, config, collection,
                                            validate=validate)

        DriverEnabled.add_driver_enabled_device(self.hw_driver, self)

    def enable(self, **kwargs):
        super(DriverEnabled, self).enable()
        for device in DriverEnabled.enable_driver_mappings[self.hw_driver]:
            device._enable()

    def _enable(self):
        pass
        self.log.debug('Enabling')
        # print self, "enabling"

    def disable(self, **kwargs):
        super(DriverEnabled, self).disable()
        # self.driver.disable()
        for device in DriverEnabled.enable_driver_mappings[self.hw_driver]:
            device._disable()

    def _disable(self):
        pass
        self.log.debug('Disabling')
        # print self, "disabling"

    def pulse(self, *args, **kwargs):
        self.log.warning("Received request to pulse a driver-enabled device. "
                         "Ignoring...")

    def timed_enable(self, *args, **kwargs):
        self.log.warning("Received request to timed-enable a driver-enabled "
                         "device. Ignoring...")


# The MIT License (MIT)

# Copyright (c) 2013-2015 Brian Madden and Gabe Knuth

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
