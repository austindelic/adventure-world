# pirate_ship.py
import math
from enum import StrEnum, auto
from typing import override
from src.animation import Animation, Draw, Frame, Line, Point, Segment, Fill
from src.assets.rides.ride import Ride
from src.entity import EngineEntity, Size
from src.clock import ClockProtocol


# Original hull points (0..1) and pivot in that space
_FRAME: Frame = [
    Segment(
        Point(0.222, 0.053), Point(0.5313, 0.7204), Line(color="dimgray", weight=8.0)
    ),
    Segment(
        Point(0.5313, 0.7204), Point(0.848, 0.0484), Line(color="dimgray", weight=8.0)
    ),
]

_BASE: Frame = [
    Fill(
        [
            Point(0.09, 0),
            Point(0.1845, 0.0856),
            Point(0.8883, 0.0856),
            Point(0.981, 0),
            Point(0.09, 0),
        ],
        "silver",
    )
]


_HULL: Frame = [
    Fill(
        [
            Point(0.0487, 0.433),
            Point(0.0728, 0.3592),
            Point(0.1198, 0.2854),
            Point(0.2042, 0.22),
            Point(0.2798, 0.189),
            Point(0.384, 0.174),
            Point(0.698, 0.175),
            Point(0.7743, 0.1936),
            Point(0.854, 0.228),
            Point(0.926, 0.289),
            Point(0.964, 0.343),
            Point(0.987, 0.402),
            Point(0.9977, 0.4337),
            Point(0.807, 0.433),
            Point(0.722, 0.3575),
            Point(0.32, 0.359),
            Point(0.233, 0.433),
            Point(0.0487, 0.433),
        ],
        "sandybrown",
    )
]

_HULL_DETAILS: Frame = [
    Segment(Point(0.008, 0.442), Point(0.239, 0.4415), Line("red", 5)),
    Segment(Point(0.239, 0.4415), Point(0.3276, 0.366), Line("red", 5)),
    Segment(Point(0.3276, 0.366), Point(0.7206, 0.369), Line("red", 5)),
    Segment(Point(0.7206, 0.369), Point(0.809, 0.444), Line("red", 5)),
    Segment(Point(0.809, 0.444), Point(0.996, 0.4435), Line("red", 5)),
]

_CORE: Frame = [
    Segment(Point(0.53, 0.3675), Point(0.5312, 0.664), Line("red", 5)),
    Segment(Point(0.5313, 0.664), Point(0.4984, 0.6765), Line("red", 5)),
    Segment(Point(0.4984, 0.6765), Point(0.475, 0.705), Line("red", 5)),
    Segment(Point(0.475, 0.705), Point(0.4785, 0.747), Line("red", 5)),
    Segment(Point(0.4785, 0.747), Point(0.515, 0.779), Line("red", 5)),
    Segment(Point(0.515, 0.779), Point(0.556, 0.775), Line("red", 5)),
    Segment(Point(0.556, 0.775), Point(0.584, 0.744), Line("red", 5)),
    Segment(Point(0.584, 0.744), Point(0.587, 0.701), Line("red", 5)),
    Segment(Point(0.587, 0.701), Point(0.5516, 0.6672), Line("red", 5)),
    Segment(Point(0.5516, 0.6672), Point(0.5313, 0.664), Line("red", 5)),
]


def _frames() -> list[Frame]:
    return [_FRAME + _BASE + _HULL + _HULL_DETAILS + _CORE]


class ShipState(StrEnum):
    STOPPED = auto()
    RUNNING = auto()


class PirateShip(Ride):
    def __init__(self, position: Point) -> None:
        anim = Animation(_frames())
        super().__init__(animation=anim, position=position, size=Size(20, 10, 5))
        self._pivot_local = Point(0.5313, 0.7204)  # local model pivot now at origin
        self._period_s = 2.0
        self._amp_rad = math.radians(20)
        self.state: ShipState = ShipState.RUNNING

    @override
    def update(self, clock: ClockProtocol) -> None:
        self.pivot = self._pivot_local
        if self.state is ShipState.RUNNING:
            phase = 2 * math.pi * (clock.time / self._period_s)
            self.pose_rotation = self._amp_rad * math.sin(phase)
        else:
            self.pose_rotation = 0.0

    @staticmethod
    def _rotate_point(p: Point, pivot: Point, cos_a: float, sin_a: float) -> Point:
        """Return a rotated copy of point p around pivot."""
        dx, dy = p.x - pivot.x, p.y - pivot.y
        return Point(
            pivot.x + dx * cos_a - dy * sin_a,
            pivot.y + dx * sin_a + dy * cos_a,
        )

    @override
    def get_frame(self, frame_clock: int, engine_fps: int = 24) -> Frame:
        """Rebuilds and rotates the dynamic parts of the pirate ship each frame."""
        # Base static parts stay fixed
        frame = []
        frame.extend(_FRAME)
        frame.extend(_BASE)

        # Time-based rotation for moving sections
        t = frame_clock / engine_fps
        if self.state is ShipState.RUNNING:
            phase = 2 * math.pi * (t / self._period_s)
            angle = self._amp_rad * math.sin(phase + math.pi / 6)
        else:
            angle = 0.0

        cos_a, sin_a = math.cos(angle), math.sin(angle)
        pivot = self._pivot_local

        # Rotate and append hull parts
        for part in (_HULL, _HULL_DETAILS, _CORE):
            for draw in part:
                if isinstance(draw, Segment):
                    s = self._rotate_point(draw.start, pivot, cos_a, sin_a)
                    e = self._rotate_point(draw.end, pivot, cos_a, sin_a)
                    frame.append(Segment(s, e, draw.line))
                elif isinstance(draw, Fill):
                    pts = [
                        self._rotate_point(p, pivot, cos_a, sin_a) for p in draw.points
                    ]
                    frame.append(Fill(pts, draw.color, draw.alpha, draw.edgecolor))
                else:
                    frame.append(draw)

        return frame

    def toggle(self) -> None:
        self.state = (
            ShipState.RUNNING if self.state is ShipState.STOPPED else ShipState.STOPPED
        )
