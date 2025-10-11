"""
File: ferris_wheel.py
Author: Austin Delic (austin@austindelic.com)
"""

from enum import StrEnum, auto
from typing import override
from src.animation import Animation, Frame, Line, Point, Segment
from src.entity import EngineEntity
from src.clock import ClockProtocol
from src.entity import Ride


class FerrisWheelState(StrEnum):
    IDLE = auto()
    SPINNING = auto()


def _frames() -> list[Frame]:
    g = Line("g", 2.0)

    base: Frame = [
        Segment(Point(0.503, 0.106), Point(0.689, 0.105), Line("g", 2.0)),
        Segment(Point(0.689, 0.105), Point(0.69, 0.003), Line("g", 2.0)),
        Segment(Point(0.69, 0.003), Point(0.233, 0.003), Line("g", 2.0)),
        Segment(Point(0.233, 0.003), Point(0.232, 0.106), Line("g", 2.0)),
        Segment(Point(0.232, 0.106), Point(0.425, 0.106), Line("g", 2.0)),
        Segment(Point(0.425, 0.106), Point(0.4246, 0.4722), Line("g", 2.0)),
        Segment(Point(0.4246, 0.4722), Point(0.405, 0.486), Line("g", 2.0)),
        Segment(Point(0.405, 0.486), Point(0.3916, 0.5035), Line("g", 2.0)),
        Segment(Point(0.3916, 0.5035), Point(0.383, 0.526), Line("g", 2.0)),
        Segment(Point(0.383, 0.526), Point(0.381, 0.5514), Line("g", 2.0)),
        Segment(Point(0.381, 0.5514), Point(0.389, 0.5786), Line("g", 2.0)),
        Segment(Point(0.389, 0.5786), Point(0.4085, 0.605), Line("g", 2.0)),
        Segment(Point(0.4085, 0.605), Point(0.432, 0.6195), Line("g", 2.0)),
        Segment(Point(0.432, 0.6195), Point(0.458, 0.6266), Line("g", 2.0)),
        Segment(Point(0.458, 0.6266), Point(0.4907, 0.6214), Line("g", 2.0)),
        Segment(Point(0.4907, 0.6214), Point(0.522, 0.6026), Line("g", 2.0)),
        Segment(Point(0.522, 0.6026), Point(0.5396, 0.5744), Line("g", 2.0)),
        Segment(Point(0.5396, 0.5744), Point(0.546, 0.5495), Line("g", 2.0)),
        Segment(Point(0.546, 0.5495), Point(0.543, 0.5194), Line("g", 2.0)),
        Segment(Point(0.543, 0.5194), Point(0.5307, 0.495), Line("g", 2.0)),
        Segment(Point(0.5307, 0.495), Point(0.5175, 0.482), Line("g", 2.0)),
        Segment(Point(0.5175, 0.482), Point(0.4935, 0.4667), Line("g", 2.0)),
        Segment(Point(0.4935, 0.4667), Point(0.4696, 0.461), Line("g", 2.0)),
        Segment(Point(0.4696, 0.461), Point(0.4456, 0.4628), Line("g", 2.0)),
        Segment(Point(0.4456, 0.4628), Point(0.4246, 0.4722), Line("g", 2.0)),
        Segment(Point(0.4246, 0.4722), Point(0.4456, 0.4628), Line("g", 2.0)),
        Segment(Point(0.4456, 0.4628), Point(0.4696, 0.461), Line("g", 2.0)),
        Segment(Point(0.4696, 0.461), Point(0.4935, 0.4667), Line("g", 2.0)),
        Segment(Point(0.4935, 0.4667), Point(0.5018, 0.4718), Line("g", 2.0)),
        Segment(Point(0.5018, 0.4718), Point(0.503, 0.106), Line("g", 2.0)),
        Segment(Point(0.503, 0.106), Point(0.425, 0.106), Line("g", 2.0)),
        Segment(Point(0.425, 0.106), Point(0.503, 0.106), Line("g", 2.0)),
    ]

    hub: Frame = [
        Segment(Point(0.3446, 0.3557), Point(0.3328, 0.371), Line("g", 2.0)),
        Segment(Point(0.3328, 0.371), Point(0.3213, 0.3816), Line("g", 2.0)),
        Segment(Point(0.3213, 0.3816), Point(0.359, 0.4286), Line("g", 2.0)),
        Segment(Point(0.359, 0.4286), Point(0.3817, 0.4676), Line("g", 2.0)),
        Segment(Point(0.3817, 0.4676), Point(0.3919, 0.5027), Line("g", 2.0)),
        Segment(Point(0.3919, 0.5027), Point(0.3863, 0.5162), Line("g", 2.0)),
        Segment(Point(0.3863, 0.5162), Point(0.366, 0.5259), Line("g", 2.0)),
        Segment(Point(0.366, 0.5259), Point(0.3096, 0.5483), Line("g", 2.0)),
        Segment(Point(0.3096, 0.5483), Point(0.249, 0.566), Line("g", 2.0)),
        Segment(Point(0.249, 0.566), Point(0.2578, 0.5812), Line("g", 2.0)),
        Segment(Point(0.2578, 0.5812), Point(0.2646, 0.6), Line("g", 2.0)),
        Segment(Point(0.2646, 0.6), Point(0.329, 0.5866), Line("g", 2.0)),
        Segment(Point(0.329, 0.5866), Point(0.3775, 0.5864), Line("g", 2.0)),
        Segment(Point(0.3775, 0.5864), Point(0.4084, 0.604), Line("g", 2.0)),
        Segment(Point(0.4084, 0.604), Point(0.426, 0.628), Line("g", 2.0)),
        Segment(Point(0.426, 0.628), Point(0.438, 0.6743), Line("g", 2.0)),
        Segment(Point(0.438, 0.6743), Point(0.4434, 0.7115), Line("g", 2.0)),
        Segment(Point(0.4434, 0.7115), Point(0.4448, 0.7422), Line("g", 2.0)),
        Segment(Point(0.4448, 0.7422), Point(0.4676, 0.741), Line("g", 2.0)),
        Segment(Point(0.4676, 0.741), Point(0.49145, 0.7413), Line("g", 2.0)),
        Segment(Point(0.49145, 0.7413), Point(0.4915, 0.6882), Line("g", 2.0)),
        Segment(Point(0.4915, 0.6882), Point(0.4973, 0.6454), Line("g", 2.0)),
        Segment(Point(0.4973, 0.6454), Point(0.5083, 0.6112), Line("g", 2.0)),
        Segment(Point(0.5083, 0.6112), Point(0.522, 0.6029), Line("g", 2.0)),
        Segment(Point(0.522, 0.6029), Point(0.5298, 0.5904), Line("g", 2.0)),
        Segment(Point(0.5298, 0.5904), Point(0.556, 0.5851), Line("g", 2.0)),
        Segment(Point(0.556, 0.5851), Point(0.5867, 0.5844), Line("g", 2.0)),
        Segment(Point(0.5867, 0.5844), Point(0.65525, 0.5892), Line("g", 2.0)),
        Segment(Point(0.65525, 0.5892), Point(0.6574, 0.5724), Line("g", 2.0)),
        Segment(Point(0.6574, 0.5724), Point(0.6646, 0.5579), Line("g", 2.0)),
        Segment(Point(0.6646, 0.5579), Point(0.602, 0.5429), Line("g", 2.0)),
        Segment(Point(0.602, 0.5429), Point(0.5617, 0.527), Line("g", 2.0)),
        Segment(Point(0.5617, 0.527), Point(0.5408, 0.5146), Line("g", 2.0)),
        Segment(Point(0.5408, 0.5146), Point(0.5295, 0.4929), Line("g", 2.0)),
        Segment(Point(0.5295, 0.4929), Point(0.5356, 0.4535), Line("g", 2.0)),
        Segment(Point(0.5356, 0.4535), Point(0.5528, 0.408), Line("g", 2.0)),
        Segment(Point(0.5528, 0.408), Point(0.5798, 0.3536), Line("g", 2.0)),
        Segment(Point(0.5798, 0.3536), Point(0.5692, 0.3375), Line("g", 2.0)),
        Segment(Point(0.5692, 0.3375), Point(0.5591, 0.317), Line("g", 2.0)),
        Segment(Point(0.5591, 0.317), Point(0.5317, 0.3729), Line("g", 2.0)),
        Segment(Point(0.5317, 0.3729), Point(0.5087, 0.4094), Line("g", 2.0)),
        Segment(Point(0.5087, 0.4094), Point(0.4895, 0.4346), Line("g", 2.0)),
        Segment(Point(0.4895, 0.4346), Point(0.46104, 0.4617), Line("g", 2.0)),
        Segment(Point(0.46104, 0.4617), Point(0.4528, 0.4621), Line("g", 2.0)),
        Segment(Point(0.4528, 0.4621), Point(0.4173, 0.4358), Line("g", 2.0)),
        Segment(Point(0.4173, 0.4358), Point(0.3786, 0.3967), Line("g", 2.0)),
        Segment(Point(0.3786, 0.3967), Point(0.3446, 0.3557), Line("g", 2.0)),
    ]
    return [base + hub]


class FerrisWheel(Ride):
    def __init__(self) -> None:
        # 1) immutable base geometry (animation frames)
        anim = Animation(_frames())

        # 2) world pose (start at origin, scale down a bit)
        super().__init__(animation=anim, start_point=Point(0.0, 0.0), size=0.2, fps=12)

        # 3) behaviour/state
        self.state: FerrisWheelState = FerrisWheelState.SPINNING
        self._speed = 0.25  # units per second in world coords

    @override
    def update(self, clock: ClockProtocol) -> None:
        # animation frame selection uses Eng ineEntity.fps (12 fps here)
        # motion uses real seconds so it’s frame-rate independent
        if self.state is FerrisWheelState.SPINNING:
            # reassign a NEW Point (Point is frozen/immutable)
            self.start_point = Point(
                self.start_point.x + self._speed * clock.dt, self.start_point.y
            )
        else:
            # idle: no movement
            ...
