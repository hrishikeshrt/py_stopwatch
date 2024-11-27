#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stopwatch class for timing portions of python code
"""
# Created on Sun Feb 28 20:00:59 2021

__author__ = "Hrishikesh Terdalkar"

###############################################################################

import time
import logging
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass

###############################################################################
# Constants

STATE_ACTIVE = "state_active"
STATE_INACTIVE = "state_inactive"
STATE_PAUSE = "state_pause"

ACTION_START = "action_start"
ACTION_STOP = "action_stop"
ACTION_PAUSE = "action_pause"
ACTION_RESUME = "action_resume"
ACTION_TICK = "action_tick"

ACTIONS = [ACTION_START, ACTION_STOP, ACTION_PAUSE, ACTION_RESUME, ACTION_TICK]

###############################################################################


@dataclass
class Tick:
    id: int
    name: str
    time: float
    duration: float
    action: str

###############################################################################


class Stopwatch:
    """
    Stopwatch Instance

    A typical lifecycle of the stopwatch:
        [creation] --> [start] --> [tick, pause, resume] --> [stop]
    """

    def __init__(self, precision=None):
        self.__state = STATE_INACTIVE
        self.__ticks = []
        self.__index_name = defaultdict(list)
        self.__index_action = defaultdict(list)
        self.precision = precision
        self.logger = logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

    # ----------------------------------------------------------------------- #

    def __perform_tick(self, name=None, action=ACTION_TICK):
        """Record a tick without any checks"""
        tick_time = time.perf_counter() - self.__start_time
        if self.precision:
            round(tick_time, self.precision)
        if action == ACTION_START:
            tick_time = 0
        tick_id = len(self.__ticks)
        if action is None or action not in ACTIONS:
            action = ACTION_TICK
        self.__index_name[name].append(tick_id)
        self.__index_action[action].append(tick_id)
        if tick_id > 0:
            last_tick = self.__ticks[-1]
            duration = tick_time - last_tick.time
        else:
            duration = 0
        self.__ticks.append(
            Tick(
                id=tick_id,
                name=name,
                duration=duration,
                time=tick_time,
                action=action,
            )
        )

    # ----------------------------------------------------------------------- #
    # Actions

    def start(self):
        """Start the stopwatch"""
        if self.__state == STATE_INACTIVE:
            self.__state = STATE_ACTIVE
            self.__ticks = []
            self.__index_name = defaultdict(list)
            self.__index_action = defaultdict(list)
            self.__start_time = time.perf_counter()
            self.__perform_tick(action=ACTION_START)
            return True
        else:
            self.logger.warning("Stopwatch is already active.")
            return None

    def tick(self, name=None):
        """
        Record a tick

        Returns
        -------
        Time since the last tick
        """
        if self.__state == STATE_ACTIVE:
            if name is not None:
                name = str(name)
            self.__perform_tick(name=name)
            return self.last()
        else:
            self.logger.warning("Failed to record tick.")
            return None

    def pause(self):
        """
        Pause the stopwatch
        (Ticks are not recorded until resumed)
        """
        if self.__state == STATE_ACTIVE:
            self.__state = STATE_PAUSE
            self.__perform_tick(action=ACTION_PAUSE)
            return True
        else:
            self.logger.warning("Failed to pause.")
            return None

    def resume(self):
        """
        Resume

        Returns
        -------
        Time for which the instance was paused
        """
        if self.__state == STATE_PAUSE:
            self.__state = STATE_ACTIVE
            self.__perform_tick(action=ACTION_RESUME)
            return self.last()
        else:
            self.logger.warning("Failed to resume.")
            return None

    def stop(self):
        """
        Stops the stopwatch

        Returns
        -------
        Total time (including pause-time)
        """
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
        """Get pause-time between different ticks"""
        pause_time = 0
        pause_start = 0
        pause_end = 0
        _end_idx = end_idx + 1
        ticks = (
            self.__ticks[start_idx:_end_idx]
            if _end_idx
            else self.__ticks[start_idx:]
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
        return self.get_time_elapsed(exclude_pause=True)

    @property
    def time_total(self):
        return self.get_time_elapsed(exclude_pause=False)

    # ----------------------------------------------------------------------- #

    def get_time_elapsed(
        self,
        start_key: int or str = 0,
        end_key: int or str = -1,
        exclude_pause: bool = True,
    ):
        """
        Get time elapsed between different ticks

        If there are multiple matches for start or end ticks, the following
        two ticks are selected:
        - the chronologically first matching tick for start
        - the chronologically last matching tick for end

        Parameters
        ----------

        start_key: int or str


        exclude_pause: bool
            If True, pause-time is not counted.
            The default is True.

        Returns
        -------
        Total runtime (with or without pause-time)
        """
        if not self.__ticks:
            return 0

        start_matches = self.get_ticks(start_key)
        end_matches = self.get_ticks(end_key)
        if not start_matches:
            self.logger.warning(f"No matching start tick found for '{start_key}'.")
            return None
        elif not end_matches:
            self.logger.warning(f"No matching end tick found for '{end_key}'.")
            return None
        else:
            start_tick = start_matches[0]
            start_idx = start_tick.id
            end_tick = end_matches[-1]
            end_idx = end_tick.id

        pause_time = (
            self.get_time_paused(start_idx, end_idx) if exclude_pause else 0
        )

        return end_tick.time - start_tick.time - pause_time

    time_elapsed = property(get_time_elapsed)

    # ----------------------------------------------------------------------- #

    def get_ticks(self, key=None):
        id_match_ticks = []
        name_match_ticks = []
        ticks = []
        total_ticks = len(self.__ticks)

        if key is None:
            key = []
        if isinstance(key, str) or not isinstance(key, Iterable):
            key = [key]

        search_keys = set()
        for k in key:
            try:
                int_k = int(k)
                int_conversion = True
                search_keys.add(int_k)
                if int_k < 0:
                    search_keys.add(total_ticks + int_k)
            except Exception:
                int_conversion = False
            try:
                str_k = str(k)
                str_conversion = True
                search_keys.add(str_k)
            except Exception:
                str_conversion = False

            if not int_conversion and not str_conversion:
                self.logger.warning(
                    f"Ignored search key {k} ({type(k)}) ."
                )

        for tick_idx, tick in enumerate(self.__ticks):
            if tick_idx in search_keys:
                id_match_ticks.append(tick)
            if tick.name in search_keys:
                name_match_ticks.append(tick)
            ticks.append(tick)

        if search_keys:
            ticks = id_match_ticks + name_match_ticks

        return ticks

    # ----------------------------------------------------------------------- #

    def last(self):
        """Return the time duration of the last tick
        i.e. time between the last two ticks"""
        if len(self.__ticks):
            return self.__ticks[-1].duration
        else:
            return 0

    def current(self):
        """Return the time elapsed since the last tick"""
        if self.__state != STATE_INACTIVE:
            if self.__ticks:
                return time.perf_counter() - self.__ticks[-1].time
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
        return (
            f"<{self.__class__.__name__}: "
            f"({self.__state}), "
            f"{len(self.__ticks)} ticks, "
            f"time_paused: {self.time_paused:.2f} sec, "
            f"time_active: {self.time_active:.2f} sec>"
        )

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
    tij = t.get_time_elapsed(start_key="Named Tick-1", end_key="Named Tick-2")
    print(f"Time between 'Named Tick-1' and 'Named Tick-2': {tij:.4f}")
    return t


if __name__ == "__main__":
    t = main()
