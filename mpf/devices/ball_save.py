"""Device that implements a ball save."""
# ball_save.py
# Mission Pinball Framework
# MPF is written by Brian Madden & Gabe Knuth
# This module originally written by Jan Kantert
# Released under the MIT License. (See license info at the end of this file.)

# Documentation and more info at http://missionpinball.com/mpf


from mpf.system.device import Device
from mpf.system.tasks import DelayManager
from mpf.system.timing import Timing
from mpf.system.config import Config

class BallSave(Device):

    config_section = 'ball_saves'
    collection = 'ball_saves'
    class_label = 'ball_save'

    def __init__(self, machine, name, config, collection=None, validate=True):
        super(BallSave, self).__init__(machine, name, config, collection,
                                       validate=validate)

        self.delay = DelayManager()
        self.enabled = False
        self.saves_remaining = 0

        if self.config['balls_to_save'] == -1:
            self.unlimited_saves = True
        else:
            self.unlimited_saves = False

        self.source_playfield = self.config['source_playfield']

        # todo change the delays to timers so we can add pause and extension
        # events, but that will require moving timers out of mode conde

    def enable(self, **kwargs):
        if self.enabled:
            return

        self.saves_remaining = self.config['balls_to_save']
        self.enabled = True
        self.log.debug("Enabling. Auto launch: %s, Balls to save: %s",
                       self.config['auto_launch'],
                       self.config['balls_to_save'])

        # Enable shoot again
        self.machine.events.add_handler('ball_drain',
                                        self._ball_drain_while_active,
                                        priority=1000)

        if (self.config['active_time'] > 0 and
                not self.config['timer_start_events']):
            self.timer_start()

        self.machine.events.post('ball_save_{}_enabled'.format(self.name))

    def disable(self, **kwargs):
        if not self.enabled:
            return

        self.enabled = False
        self.log.debug("Disabling...")
        self.machine.events.remove_handler(self._ball_drain_while_active)
        self.delay.remove('disable')
        self.delay.remove('hurry_up')
        self.delay.remove('grace_period')

        self.machine.events.post('ball_save_{}_disabled'.format(self.name))

    def timer_start(self, **kwargs):
        if self.config['active_time'] > 0:
            if self.debug:
                self.log.debug('Starting ball save timer: %ss',
                               self.config['active_time']/1000.0)

            self.delay.add(name='disable',
                           ms=(self.config['active_time'] +
                               self.config['grace_period']),
                           callback=self.disable)
            self.delay.add(name='grace_period',
                           ms=self.config['active_time'],
                           callback=self._grace_period)
            self.delay.add(name='hurry_up',
                           ms=(self.config['active_time'] -
                               self.config['hurry_up_time']),
                           callback=self._hurry_up)

    def _hurry_up(self):
        if self.debug:
            self.log.debug("Starting Hurry Up")

        self.machine.events.post('ball_save_{}_hurry_up'.format(self.name))

    def _grace_period(self):
        if self.debug:
            self.log.debug("Starting Grace Period")

        self.machine.events.post('ball_save_{}_grace_period'.format(self.name))

    def _ball_drain_while_active(self, balls, **kwargs):
        if balls <= 0:
            return {'balls': balls}

        no_balls_in_play = False

        try:
            if not self.machine.game.balls_in_play:
                no_balls_in_play = True
        except AttributeError:
            no_balls_in_play = True

        if no_balls_in_play:
            self.log.debug("Received request to save ball, but no balls are in"
                           " play. Discarding request.")
            return {'balls': balls}

        self.log.debug("Ball(s) drained while active. Requesting new one(s). "
                       "Autolaunch: %s", self.config['auto_launch'])

        self.machine.events.post('ball_save_{}_saving_ball'.format(self.name),
                                 balls=balls)

        self.source_playfield.add_ball(balls=balls,
            player_controlled=self.config['auto_launch']^1)

        if not self.unlimited_saves:
            self.saves_remaining -= balls
            if self.debug:
                self.log.debug("Saves remaining: %s", self.saves_remaining)
        elif self.debug:
            self.log.debug("Unlimited Saves enabled")

        if self.saves_remaining <= 0:
            if self.debug:
                self.log.debug("Disabling since there are no saves remaining")
            self.disable()

        return {'balls': 0}

    def remove(self):
        if self.debug:
            self.log.debug("Removing...")

        self.disable()


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
