============
py-stopwatch
============

.. image:: https://img.shields.io/pypi/v/py-stopwatch?color=success
        :target: https://pypi.python.org/pypi/py_stopwatch

.. image:: https://readthedocs.org/projects/py-stopwatch/badge/?version=latest
        :target: https://py-stopwatch.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/py-stopwatch
        :target: https://pypi.python.org/pypi/py-stopwatch
        :alt: Python Version Support

.. image:: https://img.shields.io/github/issues/hrishikeshrt/py_stopwatch
        :target: https://github.com/hrishikeshrt/py_stopwatch/issues
        :alt: GitHub Issues

.. image:: https://img.shields.io/github/followers/hrishikeshrt?style=social
        :target: https://github.com/hrishikeshrt
        :alt: GitHub Followers

.. image:: https://img.shields.io/twitter/follow/hrishikeshrt?style=social
        :target: https://twitter.com/hrishikeshrt
        :alt: Twitter Followers


Stopwatch class for timing portions of python code.

* Free software: MIT license
* Documentation: https://py-stopwatch.readthedocs.io.


Features
========

* Tick-based stopwatch
* Support for Pause/Resume
* Support for multiple named-ticks
* Utility functions for time between different ticks
* No third party requirements.

Usage
=====

.. code-block:: python

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
