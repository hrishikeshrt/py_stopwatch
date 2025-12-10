import unittest
from unittest import mock

from stopwatch import Stopwatch


class StopwatchTimingTests(unittest.TestCase):
    @mock.patch("stopwatch.stopwatch.time.perf_counter")
    def test_tick_returns_interval_since_last_tick(self, perf_counter_mock):
        # start(): perf_counter called twice -> 0, 0
        # first tick(): 1, second tick(): 2
        perf_counter_mock.side_effect = [0, 0, 1, 2]

        sw = Stopwatch()
        self.assertTrue(sw.start())

        interval1 = sw.tick()
        interval2 = sw.tick()

        self.assertEqual(interval1, 1)
        self.assertEqual(interval2, 1)

    @mock.patch("stopwatch.stopwatch.time.perf_counter")
    def test_current_returns_elapsed_since_last_tick(self, perf_counter_mock):
        # start(): 0, 0
        # tick(): 2  -> last tick at t=2
        # current(): 5 -> elapsed since last tick = 3
        perf_counter_mock.side_effect = [0, 0, 2, 5]

        sw = Stopwatch()
        sw.start()
        sw.tick()

        current = sw.current()
        self.assertEqual(current, 3)

    @mock.patch("stopwatch.stopwatch.time.perf_counter")
    def test_time_active_excludes_paused_duration(self, perf_counter_mock):
        # start(): 0, 0
        # tick(): 1
        # pause(): 2
        # resume(): 5  -> pause duration = 3
        # stop(): 7    -> total time = 7, active = 4
        perf_counter_mock.side_effect = [0, 0, 1, 2, 5, 7]

        sw = Stopwatch()
        sw.start()
        sw.tick()
        sw.pause()
        sw.resume()
        sw.stop()

        self.assertEqual(sw.time_paused, 3)
        self.assertEqual(sw.time_total, 7)
        self.assertEqual(sw.time_active, 4)


class StopwatchTicksTests(unittest.TestCase):
    @mock.patch("stopwatch.stopwatch.time.perf_counter")
    def test_get_time_elapsed_by_tick_name(self, perf_counter_mock):
        # start(): 0, 0
        # tick('a'): 1
        # tick('b'): 3
        perf_counter_mock.side_effect = [0, 0, 1, 3]

        sw = Stopwatch()
        sw.start()
        sw.tick("a")
        sw.tick("b")

        elapsed = sw.get_time_elapsed("a", "b")
        self.assertEqual(elapsed, 2)

    def test_get_ticks_supports_index_and_name(self):
        sw = Stopwatch()
        sw.start()
        sw.tick("first")
        sw.tick("second")

        # -1 should refer to the last tick; "first" by name
        ticks = sw.get_ticks([-1, "first"])

        self.assertGreaterEqual(len(ticks), 2)
        # first returned tick corresponds to index -1 (last)
        self.assertEqual(ticks[0].name, "second")
        # second returned tick corresponds to name "first"
        self.assertEqual(ticks[1].name, "first")

    def test_get_ticks_without_key_returns_all_ticks(self):
        sw = Stopwatch()
        sw.start()
        sw.tick("first")
        sw.tick("second")

        ticks = sw.get_ticks()
        self.assertEqual(len(ticks), 3)  # start + two ticks


if __name__ == "__main__":
    unittest.main()

