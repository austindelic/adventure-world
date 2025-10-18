"""
Lightweight frame clock utilities.

Exposes a simple protocol and an implementation that tracks elapsed time,
delta time, and frame count using perf_counter for high-resolution timing.
"""

from typing import Protocol
from time import perf_counter


class ClockProtocol(Protocol):
    @property
    def time(self) -> float: ...
    @property
    def dt(self) -> float: ...
    @property
    def frame(self) -> int: ...

    def tick(self) -> None: ...


class Clock(ClockProtocol):
    def __init__(self) -> None:
        self._t0 = perf_counter()
        self._last = self._t0
        self._time = 0.0
        self._dt = 0.0
        self._frame = 0

    def tick(self) -> None:
        now = perf_counter()
        self._dt = now - self._last
        self._time = now - self._t0
        self._last = now
        self._frame += 1

    @property
    def time(self) -> float:
        return self._time

    @property
    def dt(self) -> float:
        return self._dt

    @property
    def frame(self) -> int:
        return self._frame
