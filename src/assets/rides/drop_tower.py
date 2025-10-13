# drow_tower.py
import math
from enum import Enum, StrEnum, auto
from typing import override
from src.animation import Animation, Frame, Line, Point, Fill, Segment
from src.assets.rides.ride import Ride
from src.entity import Size
from src.clock import ClockProtocol


class ShipState(StrEnum):
    STOPPED = auto()
    RUNNING = auto()


# Original hull points (0..1) and pivot in that space
_BASE_LOWER: Frame = [
    Fill(
        [
            Point(0.0586, 0.001),
            Point(0.0588, 0.0432),
            Point(0.0678, 0.064),
            Point(0.0803, 0.0796),
            Point(0.0986, 0.0934),
            Point(0.1204, 0.0983),
            Point(0.414, 0.1),
            Point(0.4332, 0.1),
            Point(0.4526, 0.0782),
            Point(0.4626, 0.063),
            Point(0.4688, 0.0474),
            Point(0.4702, 0.0298),
            Point(0.4702, 0.001),
            Point(0.0586, 0.001),
        ],
        "mediumturquoise",
        edgecolor="black",
    )
]

_BASE_UPPER: Frame = [
    Fill(
        [
            Point(0.1213, 0.08),
            Point(0.1225, 0.1085),
            Point(0.1332, 0.1176),
            Point(0.1457, 0.1204),
            Point(0.3917, 0.12),
            Point(0.4035, 0.1137),
            Point(0.4091, 0.1073),
            Point(0.4116, 0.08),
            Point(0.1213, 0.08),
        ],
        "lightseagreen",
    )
]

_FRAME: Frame = [
    Segment(Point(0.1457, 0.0891), Point(0.147, 0.8493), Line("red", 5)),
    Segment(Point(0.147, 0.8493), Point(0.385, 0.848), Line("red", 5)),
    Segment(Point(0.385, 0.848), Point(0.3823, 0.0838), Line("red", 5)),
    Segment(Point(0.3823, 0.0838), Point(0.1468, 0.2378), Line("red", 5)),
    Segment(Point(0.1468, 0.2378), Point(0.3842, 0.3898), Line("red", 5)),
    Segment(Point(0.3842, 0.3898), Point(0.148, 0.5438), Line("red", 5)),
    Segment(Point(0.148, 0.5438), Point(0.3842, 0.6995), Line("red", 5)),
    Segment(Point(0.3842, 0.6995), Point(0.1514, 0.8489), Line("red", 5)),
    Segment(Point(0.1514, 0.8489), Point(0.378, 0.8452), Line("red", 5)),
    Segment(Point(0.378, 0.8452), Point(0.146, 0.7004), Line("red", 5)),
    Segment(Point(0.146, 0.7004), Point(0.3856, 0.5433), Line("red", 5)),
    Segment(Point(0.3856, 0.5433), Point(0.1456, 0.3904), Line("red", 5)),
    Segment(Point(0.1456, 0.3904), Point(0.3856, 0.2368), Line("red", 5)),
    Segment(Point(0.3856, 0.2368), Point(0.1457, 0.0891), Line("red", 5)),
    Segment(Point(0.1466, 0.8485), Point(0.1252, 0.8483), Line("red", 5)),
    Segment(Point(0.1252, 0.8483), Point(0.1254, 0.8904), Line("red", 5)),
    Segment(Point(0.2648, 0.848), Point(0.2647, 0.9051), Line("red", 5)),
    Segment(Point(0.3844, 0.8492), Point(0.405, 0.8496), Line("red", 5)),
    Segment(Point(0.405, 0.8496), Point(0.405, 0.9045), Line("red", 5)),
]


_BANNER_ENDS: Frame = [
    Fill(
        [
            Point(0.09214, 0.8992),
            Point(0.4362, 0.9005),
            Point(0.4352, 0.8873),
            Point(0.4273, 0.8754),
            Point(0.4178, 0.8713),
            Point(0.404, 0.872),
            Point(0.3956, 0.881),
            Point(0.3899, 0.8944),
            Point(0.3847, 0.8854),
            Point(0.378, 0.8748),
            Point(0.3668, 0.869),
            Point(0.3527, 0.8735),
            Point(0.344, 0.884),
            Point(0.3393, 0.8965),
            Point(0.3337, 0.882),
            Point(0.325, 0.873),
            Point(0.3136, 0.8697),
            Point(0.3014, 0.8757),
            Point(0.2942, 0.8868),
            Point(0.29, 0.897),
            Point(0.2844, 0.8824),
            Point(0.2755, 0.8735),
            Point(0.2654, 0.8691),
            Point(0.2548, 0.8719),
            Point(0.2464, 0.8816),
            Point(0.2405, 0.896),
            Point(0.235, 0.882),
            Point(0.226, 0.8732),
            Point(0.2137, 0.8691),
            Point(0.2012, 0.8765),
            Point(0.1956, 0.8827),
            Point(0.1913, 0.8942),
            Point(0.186, 0.8805),
            Point(0.176, 0.8719),
            Point(0.1652, 0.8686),
            Point(0.1536, 0.875),
            Point(0.1457, 0.8843),
            Point(0.1419, 0.8968),
            Point(0.1368, 0.8852),
            Point(0.1318, 0.8764),
            Point(0.1197, 0.8713),
            Point(0.1085, 0.8719),
            Point(0.1, 0.8792),
            Point(0.0936, 0.8881),
            Point(0.09214, 0.8992),
        ],
        "white",
    )
]

_BANNER_STRIPES: Frame = [
    Fill(
        [
            Point(0.265, 0.998),
            Point(0.0919, 0.899),
            Point(0.1328, 0.8997),
            Point(0.2649, 0.998),
            Point(0.1666, 0.899),
            Point(0.213, 0.8995),
            Point(0.2649, 0.998),
            Point(0.2486, 0.8998),
            Point(0.283, 0.9),
            Point(0.2649, 0.9977),
            Point(0.3209, 0.9),
            Point(0.3655, 0.9002),
            Point(0.2649, 0.9978),
            Point(0.3983, 0.8997),
            Point(0.437, 0.9004),
            Point(0.265, 0.998),
        ],
        "cyan",
    )
]


_BANNER_BASE: Frame = [
    Fill(
        [
            Point(0.2649, 0.998),
            Point(0.0919, 0.899),
            Point(0.4374, 0.9005),
            Point(0.2649, 0.998),
        ],
        "white",
    )
]


_SEAT_FRAME: Frame = [
    Segment(Point(0.007, 0.706), Point(0.5233, 0.7054), Line("red", 5)),
]

_SEAT_BACKS: Frame = [
    Fill(
        [
            Point(0.0322, 0.7097),
            Point(0.0328, 0.7389),
            Point(0.037, 0.748),
            Point(0.0457, 0.755),
            Point(0.0964, 0.755),
            Point(0.1057, 0.7498),
            Point(0.1106, 0.741),
            Point(0.1106, 0.7095),
            Point(0.0322, 0.7097),
        ],
        "navy",
    ),
    Fill(
        [
            Point(0.162, 0.7163),
            Point(0.1622, 0.7392),
            Point(0.1673, 0.7486),
            Point(0.1765, 0.7549),
            Point(0.2246, 0.755),
            Point(0.2338, 0.75),
            Point(0.2393, 0.7418),
            Point(0.24, 0.7162),
            Point(0.162, 0.7163),
        ],
        "navy",
    ),
    Fill(
        [
            Point(0.2909, 0.7147),
            Point(0.2912, 0.7408),
            Point(0.2958, 0.7504),
            Point(0.3055, 0.7538),
            Point(0.3546, 0.7543),
            Point(0.3646, 0.748),
            Point(0.3688, 0.7398),
            Point(0.369, 0.7146),
            Point(0.2909, 0.7147),
        ],
        "navy",
    ),
    Fill(
        [
            Point(0.4195, 0.715),
            Point(0.4198, 0.7414),
            Point(0.4258, 0.7508),
            Point(0.436, 0.7547),
            Point(0.482, 0.7552),
            Point(0.49, 0.7508),
            Point(0.4972, 0.7418),
            Point(0.4973, 0.715),
            Point(0.4195, 0.715),
        ],
        "navy",
    ),
]


_SEAT_CAGE: Frame = [
    Fill(
        [
            Point(0.01, 0.7184),
            Point(0.0106, 0.7489),
            Point(0.0168, 0.7613),
            Point(0.0253, 0.7706),
            Point(0.0405, 0.7781),
            Point(0.1002, 0.7782),
            Point(0.1148, 0.7735),
            Point(0.1259, 0.7638),
            Point(0.1332, 0.7512),
            Point(0.1335, 0.7188),
            Point(0.1264, 0.7189),
            Point(0.1264, 0.7455),
            Point(0.1213, 0.7544),
            Point(0.1141, 0.7627),
            Point(0.1049, 0.7688),
            Point(0.095, 0.7705),
            Point(0.0479, 0.7702),
            Point(0.0371, 0.7673),
            Point(0.0281, 0.7611),
            Point(0.0208, 0.7518),
            Point(0.0178, 0.7457),
            Point(0.0174, 0.7184),
            Point(0.01, 0.7184),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.1398, 0.7184),
            Point(0.1404, 0.7489),
            Point(0.1466, 0.7613),
            Point(0.1551, 0.7706),
            Point(0.1703, 0.7781),
            Point(0.23, 0.7782),
            Point(0.2446, 0.7735),
            Point(0.2557, 0.7638),
            Point(0.263, 0.7512),
            Point(0.2633, 0.7188),
            Point(0.2562, 0.7189),
            Point(0.2562, 0.7455),
            Point(0.2511, 0.7544),
            Point(0.2439, 0.7627),
            Point(0.2347, 0.7688),
            Point(0.2248, 0.7705),
            Point(0.1777, 0.7702),
            Point(0.1669, 0.7673),
            Point(0.1579, 0.7611),
            Point(0.1506, 0.7518),
            Point(0.1476, 0.7457),
            Point(0.1472, 0.7184),
            Point(0.1398, 0.7184),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.2696, 0.7184),
            Point(0.2702, 0.7489),
            Point(0.2764, 0.7613),
            Point(0.2849, 0.7706),
            Point(0.3001, 0.7781),
            Point(0.3598, 0.7782),
            Point(0.3744, 0.7735),
            Point(0.3855, 0.7638),
            Point(0.3928, 0.7512),
            Point(0.3931, 0.7188),
            Point(0.386, 0.7189),
            Point(0.386, 0.7455),
            Point(0.3809, 0.7544),
            Point(0.3737, 0.7627),
            Point(0.3645, 0.7688),
            Point(0.3546, 0.7705),
            Point(0.3075, 0.7702),
            Point(0.2967, 0.7673),
            Point(0.2877, 0.7611),
            Point(0.2804, 0.7518),
            Point(0.2774, 0.7457),
            Point(0.277, 0.7184),
            Point(0.2696, 0.7184),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.3994, 0.7184),
            Point(0.4, 0.7489),
            Point(0.4062, 0.7613),
            Point(0.4147, 0.7706),
            Point(0.4299, 0.7781),
            Point(0.4896, 0.7782),
            Point(0.5042, 0.7735),
            Point(0.5153, 0.7638),
            Point(0.5226, 0.7512),
            Point(0.5229, 0.7188),
            Point(0.5158, 0.7189),
            Point(0.5158, 0.7455),
            Point(0.5107, 0.7544),
            Point(0.5035, 0.7627),
            Point(0.4943, 0.7688),
            Point(0.4844, 0.7705),
            Point(0.4373, 0.7702),
            Point(0.4265, 0.7673),
            Point(0.4175, 0.7611),
            Point(0.4102, 0.7518),
            Point(0.4072, 0.7457),
            Point(0.4068, 0.7184),
            Point(0.3994, 0.7184),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.01, 0.7203),
            Point(0.134, 0.7209),
            Point(0.1335, 0.6731),
            Point(0.1265, 0.6605),
            Point(0.117, 0.6515),
            Point(0.1026, 0.6456),
            Point(0.0438, 0.645),
            Point(0.0286, 0.651),
            Point(0.018, 0.6603),
            Point(0.0105, 0.6735),
            Point(0.01, 0.7203),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.1398, 0.7203),
            Point(0.2638, 0.7209),
            Point(0.2633, 0.6731),
            Point(0.2563, 0.6605),
            Point(0.2468, 0.6515),
            Point(0.2324, 0.6456),
            Point(0.1736, 0.645),
            Point(0.1584, 0.651),
            Point(0.1478, 0.6603),
            Point(0.1403, 0.6735),
            Point(0.1398, 0.7203),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.2696, 0.7203),
            Point(0.3936, 0.7209),
            Point(0.3931, 0.6731),
            Point(0.3861, 0.6605),
            Point(0.3766, 0.6515),
            Point(0.3622, 0.6456),
            Point(0.3034, 0.645),
            Point(0.2882, 0.651),
            Point(0.2776, 0.6603),
            Point(0.2701, 0.6735),
            Point(0.2696, 0.7203),
        ],
        "cyan",
    ),
    Fill(
        [
            Point(0.3994, 0.7203),
            Point(0.5234, 0.7209),
            Point(0.5229, 0.6731),
            Point(0.5159, 0.6605),
            Point(0.5064, 0.6515),
            Point(0.492, 0.6456),
            Point(0.4332, 0.645),
            Point(0.418, 0.651),
            Point(0.4074, 0.6603),
            Point(0.3999, 0.6735),
            Point(0.3994, 0.7203),
        ],
        "cyan",
    ),
]


def _frames() -> list[Frame]:
    return [
        _FRAME
        + _BASE_UPPER
        + _BASE_LOWER
        + _BANNER_ENDS
        + _BANNER_BASE
        + _BANNER_STRIPES
        + _SEAT_FRAME
        + _SEAT_BACKS
        + _SEAT_CAGE
    ]


class TowerState(Enum):
    STOPPED = auto()
    ASCENDING = auto()
    DESCENDING = auto()
    WAITING_BOTTOM = auto()


class DropTower(Ride):
    def __init__(self, position: Point) -> None:
        anim = Animation(_frames())
        super().__init__(animation=anim, position=position, size=Size(20, 10, 5))

        self._pivot_local = Point(0.5, 0.5)
        self.state: TowerState = TowerState.STOPPED

        # Movement parameters
        self._min_height = -0.5
        self._max_height = 0.00
        self._seat_y = self._min_height
        self._velocity = 0.0
        self._gravity = -1.0
        self._ascend_speed = 0.25
        self._max_fall_speed = -2.5
        self._ease_factor = 2.5

        # Timing
        self._wait_time_bottom = 1.0  # seconds to wait before next ascent
        self._wait_timer = 0.0
        self.toggle()

    @override
    def update(self, clock: ClockProtocol) -> None:
        dt = clock.dt

        if self.state is TowerState.STOPPED:
            return

        if self.state is TowerState.ASCENDING:
            # Ease-out near top
            distance_to_top = self._max_height - self._seat_y
            ease = max(0.05, min(1.0, distance_to_top * self._ease_factor))
            self._seat_y += self._ascend_speed * dt * ease

            if self._seat_y >= self._max_height:
                self._seat_y = self._max_height
                self._velocity = 0.0
                self.state = TowerState.DESCENDING

        elif self.state is TowerState.DESCENDING:
            # Accelerate downward
            self._velocity += self._gravity * dt * 4.0
            self._velocity = max(self._velocity, self._max_fall_speed)
            self._seat_y += self._velocity * dt

            # --- Earlier & stronger easing near bottom ---
            if self._seat_y <= self._min_height + 0.25:  # easing starts higher
                distance_to_bottom = abs(self._seat_y - self._min_height)
                # progressive damping curve (stronger near bottom)
                damping = max(0.15, min(0.95, distance_to_bottom * 4.5))
                self._velocity *= damping

            if self._seat_y <= self._min_height:
                self._seat_y = self._min_height
                self._velocity = 0.0
                self._wait_timer = self._wait_time_bottom
                self.state = TowerState.WAITING_BOTTOM

        elif self.state is TowerState.WAITING_BOTTOM:
            # Wait briefly at bottom before next ascent
            self._wait_timer -= dt
            if self._wait_timer <= 0:
                self.state = TowerState.ASCENDING

    @override
    def get_frame(self, frame_clock: int, engine_fps: int = 24) -> Frame:
        """Return a frame where the seat is vertically translated."""
        base_frame = (
            _FRAME
            + _BASE_UPPER
            + _BASE_LOWER
            + _BANNER_ENDS
            + _BANNER_BASE
            + _BANNER_STRIPES
        )

        seat_parts: Frame = []
        for part in (_SEAT_FRAME, _SEAT_BACKS, _SEAT_CAGE):
            for draw in part:
                if isinstance(draw, Segment):
                    s = Point(draw.start.x, draw.start.y + self._seat_y)
                    e = Point(draw.end.x, draw.end.y + self._seat_y)
                    seat_parts.append(Segment(s, e, draw.line))
                elif isinstance(draw, Fill):
                    pts = [Point(p.x, p.y + self._seat_y) for p in draw.points]
                    seat_parts.append(Fill(pts, draw.color, draw.alpha, draw.edgecolor))

        return base_frame + seat_parts

    def toggle(self) -> None:
        """Toggle continuous motion on/off."""
        if self.state is TowerState.STOPPED:
            # Start from bottom going up
            self.state = TowerState.ASCENDING
        else:
            # Stop wherever it currently is
            self.state = TowerState.STOPPED
            self._velocity = 0.0
