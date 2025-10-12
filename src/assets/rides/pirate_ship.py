# pirate_ship.py
import math
from enum import StrEnum, auto
from typing import override
from src.animation import Animation, Draw, Frame, Line, Point, Segment, Fill
from src.assets.rides.ride import Ride
from src.entity import EngineEntity, Size
from src.clock import ClockProtocol


class ShipState(StrEnum):
    STOPPED = auto()
    RUNNING = auto()


# Original hull points (0..1) and pivot in that space
_PIVOT_SRC = Point(0, 0.0)

_HULL_SRC: Frame = [
    Fill(
        [
            Point(0.068, 0.429),
            Point(0.103, 0.318),
            Point(0.180, 0.244),
            Point(0.312, 0.184),
            Point(0.417, 0.173),
            Point(0.597, 0.173),
            Point(0.731, 0.185),
            Point(0.833, 0.232),
            Point(0.906, 0.292),
            Point(0.950, 0.369),
            Point(0.974, 0.434),
            Point(0.802, 0.432),
            Point(0.705, 0.353),
            Point(0.524, 0.353),
            Point(0.524, 0.703),
            Point(0.524, 0.352),
            Point(0.328, 0.353),
            Point(0.225, 0.430),
            Point(0.070, 0.430),
        ],
        "c",
    )
]

_HULL_OUTLINE: Frame = [
    Segment(Point(0.068, 0.429), Point(0.103, 0.318), Line("k", 2.0)),
    Segment(Point(0.103, 0.318), Point(0.180, 0.244), Line("k", 2.0)),
    Segment(Point(0.180, 0.244), Point(0.312, 0.184), Line("k", 2.0)),
    Segment(Point(0.312, 0.184), Point(0.417, 0.173), Line("k", 2.0)),
    Segment(Point(0.417, 0.173), Point(0.597, 0.173), Line("k", 2.0)),
    Segment(Point(0.597, 0.173), Point(0.731, 0.185), Line("k", 2.0)),
    Segment(Point(0.731, 0.185), Point(0.833, 0.232), Line("k", 2.0)),
    Segment(Point(0.833, 0.232), Point(0.906, 0.292), Line("k", 2.0)),
    Segment(Point(0.906, 0.292), Point(0.950, 0.369), Line("k", 2.0)),
    Segment(Point(0.950, 0.369), Point(0.974, 0.434), Line("k", 2.0)),
    Segment(Point(0.974, 0.434), Point(0.802, 0.432), Line("k", 2.0)),
    Segment(Point(0.802, 0.432), Point(0.705, 0.353), Line("k", 2.0)),
    Segment(Point(0.705, 0.353), Point(0.524, 0.353), Line("k", 2.0)),
    Segment(Point(0.524, 0.353), Point(0.524, 0.703), Line("k", 2.0)),
    Segment(Point(0.524, 0.703), Point(0.524, 0.352), Line("k", 2.0)),
    Segment(Point(0.524, 0.352), Point(0.328, 0.353), Line("k", 2.0)),
    Segment(Point(0.328, 0.353), Point(0.225, 0.430), Line("k", 2.0)),
    Segment(Point(0.225, 0.430), Point(0.070, 0.430), Line("k", 2.0)),
]

_SUPPORT_SRC: Frame = [
    Segment(Point(0.200, 0.000), Point(0.524, 0.703), Line("m", 2.0)),
    Segment(Point(0.524, 0.703), Point(0.850, 0.000), Line("m", 2.0)),
    Segment(Point(0.850, 0.000), Point(0.200, 0.000), Line("m", 2.0)),
]


def _frames() -> list[Frame]:
    return [_HULL_SRC + _SUPPORT_SRC + _HULL_OUTLINE]


class PirateShip(Ride):
    def __init__(self, position: Point) -> None:
        anim = Animation(_frames())
        super().__init__(animation=anim, position=position, size=Size(10, 10, 5))
        self._pivot_local = Point(0.0, 0.0)  # local model pivot now at origin
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
