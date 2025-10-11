"""
File: pirate_ship.py
Author: Austin Delic (austin@austindelic.com)
"""

import math
from enum import StrEnum, auto
from typing import override
from src.animation import Animation, Frame, Line, Point, Segment
from src.engine import EngineEntity
from src.clock import ClockProtocol


class ShipState(StrEnum):
    STOPPED = auto()
    RUNNING = auto()


def _geometry() -> Frame:
    g = Line("g", 2.0)
    r = Line("r", 2.0)
    hull = [
        Segment(Point(0.068, 0.429), Point(0.103, 0.318), g),
        Segment(Point(0.103, 0.318), Point(0.180, 0.244), g),
        Segment(Point(0.180, 0.244), Point(0.312, 0.184), g),
        Segment(Point(0.312, 0.184), Point(0.417, 0.173), g),
        Segment(Point(0.417, 0.173), Point(0.597, 0.173), g),
        Segment(Point(0.597, 0.173), Point(0.731, 0.185), g),
        Segment(Point(0.731, 0.185), Point(0.833, 0.232), g),
        Segment(Point(0.833, 0.232), Point(0.906, 0.292), g),
        Segment(Point(0.906, 0.292), Point(0.950, 0.369), g),
        Segment(Point(0.950, 0.369), Point(0.974, 0.434), g),
        Segment(Point(0.974, 0.434), Point(0.802, 0.432), g),
        Segment(Point(0.802, 0.432), Point(0.705, 0.353), g),
        Segment(Point(0.705, 0.353), Point(0.524, 0.353), g),
        Segment(Point(0.524, 0.353), Point(0.524, 0.703), g),
        Segment(Point(0.524, 0.703), Point(0.524, 0.352), g),
        Segment(Point(0.524, 0.352), Point(0.328, 0.353), g),
        Segment(Point(0.328, 0.353), Point(0.225, 0.430), g),
        Segment(Point(0.225, 0.430), Point(0.070, 0.430), g),
    ]
    support = [
        Segment(Point(0.2, 0.0), Point(0.525, 0.700), r),
        Segment(Point(0.525, 0.700), Point(0.85, 0.0), r),
        Segment(Point(0.85, 0.0), Point(0.2, 0.0), r),
    ]
    return hull + support


class PirateShip(EngineEntity):
    def __init__(self) -> None:
        base = _geometry()
        super().__init__(
            animation=Animation([base]), start_point=Point(0.5, 0.5), size=0.5
        )
        self._pivot_local = Point(0.524, 0.703)
        self._period_s = 2.0
        self._amp_rad = math.radians(20)
        self.state: ShipState = ShipState.STOPPED

    @override
    def update(self, clock: ClockProtocol) -> None:
        self.pivot = self._pivot_local
        if self.state is ShipState.RUNNING:
            phase = 2 * math.pi * (clock.time / self._period_s)
            self.pose_rotation = self._amp_rad * math.sin(phase)
        else:
            self.pose_rotation = 0.0

    def toggle(self) -> None:
        self.state = (
            ShipState.RUNNING if self.state is ShipState.STOPPED else ShipState.STOPPED
        )
