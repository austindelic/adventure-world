"""Geometry primitives and sprite animation.

Defines simple vector-graphics primitives (Point, Segment, Fill) and
an Animation container that returns frames at a requested playback fps.
All coordinates are normalised to [0, 1] space by convention and are
converted to world/screen space by the engine.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(slots=True)
class Point:
    x: float
    y: float


CSSColorName = Literal[
    "aliceblue",
    "antiquewhite",
    "aqua",
    "aquamarine",
    "azure",
    "beige",
    "bisque",
    "black",
    "blanchedalmond",
    "blue",
    "blueviolet",
    "brown",
    "burlywood",
    "cadetblue",
    "chartreuse",
    "chocolate",
    "coral",
    "cornflowerblue",
    "cornsilk",
    "crimson",
    "cyan",
    "darkblue",
    "darkcyan",
    "darkgoldenrod",
    "darkgray",
    "darkgreen",
    "darkgrey",
    "darkkhaki",
    "darkmagenta",
    "darkolivegreen",
    "darkorange",
    "darkorchid",
    "darkred",
    "darksalmon",
    "darkseagreen",
    "darkslateblue",
    "darkslategray",
    "darkslategrey",
    "darkturquoise",
    "darkviolet",
    "deeppink",
    "deepskyblue",
    "dimgray",
    "dimgrey",
    "dodgerblue",
    "firebrick",
    "floralwhite",
    "forestgreen",
    "fuchsia",
    "gainsboro",
    "ghostwhite",
    "gold",
    "goldenrod",
    "gray",
    "green",
    "greenyellow",
    "grey",
    "honeydew",
    "hotpink",
    "indianred",
    "indigo",
    "ivory",
    "khaki",
    "lavender",
    "lavenderblush",
    "lawngreen",
    "lemonchiffon",
    "lightblue",
    "lightcoral",
    "lightcyan",
    "lightgoldenrodyellow",
    "lightgray",
    "lightgreen",
    "lightgrey",
    "lightpink",
    "lightsalmon",
    "lightseagreen",
    "lightskyblue",
    "lightslategray",
    "lightslategrey",
    "lightsteelblue",
    "lightyellow",
    "lime",
    "limegreen",
    "linen",
    "magenta",
    "maroon",
    "mediumaquamarine",
    "mediumblue",
    "mediumorchid",
    "mediumpurple",
    "mediumseagreen",
    "mediumslateblue",
    "mediumspringgreen",
    "mediumturquoise",
    "mediumvioletred",
    "midnightblue",
    "mintcream",
    "mistyrose",
    "moccasin",
    "navajowhite",
    "navy",
    "oldlace",
    "olive",
    "olivedrab",
    "orange",
    "orangered",
    "orchid",
    "palegoldenrod",
    "palegreen",
    "paleturquoise",
    "palevioletred",
    "papayawhip",
    "peachpuff",
    "peru",
    "pink",
    "plum",
    "powderblue",
    "purple",
    "rebeccapurple",
    "red",
    "rosybrown",
    "royalblue",
    "saddlebrown",
    "salmon",
    "sandybrown",
    "seagreen",
    "seashell",
    "sienna",
    "silver",
    "skyblue",
    "slateblue",
    "slategray",
    "slategrey",
    "snow",
    "springgreen",
    "steelblue",
    "tan",
    "teal",
    "thistle",
    "tomato",
    "turquoise",
    "violet",
    "wheat",
    "white",
    "whitesmoke",
    "yellow",
    "yellowgreen",
]


@dataclass(slots=True)
class Line:
    color: CSSColorName
    weight: float
    style: Literal["-", "--", "-. ", ":"] = "-"
    marker: Literal["", "o", "s", "^", "v", "x", "+"] = ""
    alpha: float = 1.0


@dataclass(slots=True)
class Segment:
    start: Point
    end: Point
    line: Line


@dataclass(slots=True)
class Fill:
    points: list[Point]
    color: CSSColorName
    alpha: float = 1.0
    edgecolor: str | None = None


type Draw = Segment | Fill
type Frame = list[Draw]


class Animation:
    """Holds geometry frames (sprite sheet)."""

    def __init__(self, frames: list[Frame] | None = None) -> None:
        self.frames: list[Frame] = [] if frames is None else frames

    def _get_index(
        self, frame_clock: int, animation_fps: int, engine_fps: int = 24
    ) -> int | None:
        if not self.frames:
            return None
        fps_ratio = animation_fps / engine_fps
        anim_frame = int(frame_clock * fps_ratio)
        return anim_frame % len(self.frames)

    def get_current_frame(
        self, frame_clock: int, animation_fps: int, engine_fps: int = 24
    ) -> Frame:
        frame_index = self._get_index(frame_clock, animation_fps, engine_fps)
        if frame_index is not None:
            return self.frames[frame_index]
        else:
            return []
