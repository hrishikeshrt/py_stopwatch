============
py-stopwatch
============

.. image:: https://readthedocs.org/projects/py-stopwatch/badge/?version=latest
        :target: https://py-stopwatch.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Stopwatch class for timing your python code, with support for pause, resume and multiple named-ticks.

* Free software: MIT license
* Documentation: https://py-stopwatch.readthedocs.io.


Usage
-----

    from stopwatch import Stopwatch

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

Features
--------

* Tick-based stopwatch
* Pause, Resume, Tick
* Multiple named-ticks
* Utility functions for time between different ticks
