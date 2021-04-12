#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 28 20:00:59 2021

@author: Hrishikesh Terdalkar

Stopwatch Class
"""

###############################################################################

import time
import logging
from collections import namedtuple, defaultdict

###############################################################################

Tick = namedtuple('Tick', ['time', 'action', 'name'])

###############################################################################

STATE_ACTIVE = 'state_active'
STATE_INACTIVE = 'state_inactive'
STATE_PAUSE = 'state_pause'

ACTION_START = 'action_start'
ACTION_STOP = 'action_stop'
ACTION_PAUSE = 'action_pause'
ACTION_RESUME = 'action_resume'
ACTION_TICK = 'action_tick'

ACTIONS = [ACTION_START, ACTION_STOP, ACTION_PAUSE, ACTION_RESUME, ACTION_TICK]

###############################################################################


class Stopwatch:
    '''Stopwatch Instance'''

    def __init__(self):
        self.__state = STATE_INACTIVE
        self.__ticks = []
        self.__index_name = defaultdict(list)
        self.__index_action = defaultdict(list)
        self.logger = logging.getLogger(
            f'{__name__}.{self.__class__.__name__}'
        )

    # ----------------------------------------------------------------------- #

    def __perform_tick(self, name=None, action=ACTION_TICK):
        '''Record a tick without any checks'''
        index = len(self.__ticks)
        if action is None or action not in ACTIONS:
            action = ACTION_TICK
        self.__index_name[name].append(index)
        self.__index_action[action].append(index)
        self.__ticks.append(
            Tick(time=time.time(), action=action, name=name)
        )

    # ----------------------------------------------------------------------- #
    # Actions

    def start(self):
        '''Start the stopwatch'''
        if self.__state == STATE_INACTIVE:
            self.__state = STATE_ACTIVE
            self.__ticks = []
            self.__index_name = defaultdict(list)
            self.__index_action = defaultdict(list)
            self.__perform_tick(action=ACTION_START)
            return True
        else:
            self.logger.warning("Stopwatch is already active.")
            return None

    def tick(self, name=None):
        '''
        Record a tick

        Returns
        -------
        Time since the last tick
        '''
        if self.__state == STATE_ACTIVE:
            if name is not None:
                name = str(name)
            self.__perform_tick(name=name)
            return self.last()
        else:
            self.logger.warning("Failed to record tick.")
            return None

    def pause(self):
        '''
        Pause the stopwatch
        (Ticks are not recorded until resumed)
        '''
        if self.__state == STATE_ACTIVE:
            self.__state = STATE_PAUSE
            self.__perform_tick(action=ACTION_PAUSE)
            return True
        else:
            self.logger.warning("Failed to pause.")
            return None

    def resume(self):
        '''
        Resume

        Returns
        -------
        Time for which the instance was paused
        '''
        if self.__state == STATE_PAUSE:
            self.__state = STATE_ACTIVE
            self.__perform_tick(action=ACTION_RESUME)
            return self.last()
        else:
            self.logger.warning("Failed to resume.")
            return None

    def stop(self):
        '''
        Stops the stopwatch

        Returns
        -------
        Total time (including pause-time)
        '''
        if self.__state != STATE_INACTIVE:
            self.__state = STATE_INACTIVE
            self.__perform_tick(action=ACTION_STOP)
            return self.time_active
        else:
            self.logger.warning("Stopwatch is already inactive.")
            return None

    # ----------------------------------------------------------------------- #
    # Calculated Properties

    def get_time_paused(self, start_idx=0, end_idx=-1):
        '''Get pause-time'''
        pause_time = 0
        pause_start = 0
        pause_end = 0
        _end_idx = end_idx + 1
        ticks = (
            self.__ticks[start_idx:_end_idx]
            if _end_idx else self.__ticks[start_idx:]
        )
        for tick in ticks:
            if tick.action == ACTION_PAUSE:
                pause_start = tick.time
            if tick.action == ACTION_RESUME:
                if pause_start:
                    pause_end = tick.time
                pause_time += pause_end - pause_start
        return pause_time

    time_paused = property(get_time_paused)

    @property
    def time_active(self):
        return self.time_elapsed(exclude_pause=True)

    @property
    def time_total(self):
        return self.time_elapsed(exclude_pause=False)

    # ----------------------------------------------------------------------- #

    def time_elapsed(self, start_idx=0, end_idx=-1,
                     start_name=None, end_name=None, exclude_pause=True):
        '''
        Get time elapsed between different ticks

        Parameters
        ----------

        exclude_pause: boolean
            If True, pause-time is not counted.
            The default is True.

        Returns
        -------
        Total runtime (with or without pause-time)
        '''
        if not self.__ticks:
            return 0

        if start_name is not None and end_name is not None:
            start_indices = self.__index_name.get(start_name, None)
            end_indices = self.__index_name.get(end_name, None)
            if start_indices is None:
                self.logger.warning(f"start_name='{start_name}' not found.")
                return None
            elif end_indices is None:
                self.logger.warning(f"end_name='{end_name}' not found.")
                return None
            else:
                start_idx = start_indices[0]
                end_idx = end_indices[0]

        pause_time = (
            self.get_time_paused(start_idx, end_idx) if exclude_pause else 0
        )

        try:
            start_tick = self.__ticks[start_idx]
            end_tick = self.__ticks[end_idx]
        except IndexError:
            self.logger.warning("IndexError")
            return None
        return end_tick.time - start_tick.time - pause_time

    # ----------------------------------------------------------------------- #

    def last(self):
        '''Return the time between the last two ticks'''
        if len(self.__ticks) > 1:
            return self.__ticks[-1].time - self.__ticks[-2].time
        else:
            return 0

    def current(self):
        '''Return the time elapsed since the last tick'''
        if self.__state != STATE_INACTIVE:
            if self.__ticks:
                return time.time() - self.__ticks[-1].time
            else:
                return 0
        else:
            self.logger.warning("Stopwatch is inactive.")
            return None

    # ----------------------------------------------------------------------- #

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    # ----------------------------------------------------------------------- #

    def __repr__(self):
        classname = self.__class__.__name__
        output = (
            f'<{classname}: '
            f'({self.__state}), '
            f'{len(self.__ticks)} ticks, '
            f'time_paused: {self.time_paused:.2f} sec, '
            f'time_active: {self.time_active:.2f} sec>'''
        )
        return output

    # ----------------------------------------------------------------------- #

###############################################################################


def main():
    t = Stopwatch()
    t.start()
    print("Started ..")
    time.sleep(0.24)
    print(f"t.tick(): {t.tick():.4f} seconds")
    time.sleep(0.48)
    print(f"t.tick(): {t.tick():.4f} seconds")
    time.sleep(0.16)
    print(f"t.tick('Named Tick-1'): {t.tick('Named Tick-1'):.4f} seconds")
    t.pause()
    print("Paused ..")
    time.sleep(0.12)
    t.resume()
    print("Resumed ..")
    print(f"t.last(): {t.last():.4f} seconds")
    time.sleep(0.12)
    print(f"t.tick(): {t.tick():.4f} seconds")
    time.sleep(0.12)
    print(f"t.tick('Named Tick-2'): {t.tick('Named Tick-2'):.4f} seconds")
    t.stop()
    print("Timer stopped.")
    print("---")
    print(f"Total pause: {t.time_paused:.2f} seconds.")
    print(f"Total runtime: {t.time_active:.2f} seconds.")
    print(f"Total time: {t.time_total:.2f} seconds.")
    tij = t.time_elapsed(start_name='Named Tick-1', end_name='Named Tick-2')
    print(f"Time between 'Named Tick-1' and 'Named Tick-2': {tij:.4f}")
    return t


if __name__ == '__main__':
    t = main()
