"""
File: animation.py
Author: Austin Delic (austin@austindelic.com)
"""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float


@dataclass(slots=True)
class Line:
    color: Literal["b", "g", "r", "c", "m", "y", "k", "w"]
    weight: float
    style: Literal["-", "--", "-. ", ":"] = "-"
    marker: Literal["", "o", "s", "^", "v", "x", "+"] = ""
    alpha: float = 1.0

    def __post_init__(self) -> None:
        if self.color not in {"b", "g", "r", "c", "m", "y", "k", "w"}:
            raise ValueError("Invalid color")
        if self.style not in {"-", "--", "-. ", ":"}:
            raise ValueError("Invalid style")
        if self.marker not in {"", "o", "s", "^", "v", "x", "+"}:
            raise ValueError("Invalid marker")
        if not (0.0 <= self.alpha <= 1.0):
            raise ValueError("alpha 0..1")


@dataclass(slots=True)
class Segment:
    start: Point
    end: Point
    line: Line


type Frame = list[Segment]


class ThisIsATest:
    pp: Point
    dd: Point
    gg: Line


class Animation:
    """Holds geometry frames (sprite sheet)."""

    def __init__(self, frames: list[Frame] | None = None) -> None:
        self.frames: list[Frame] = [] if frames is None else frames

    def _get_index(
        self, frame_clock: int, animation_fps: int, engine_fps: int = 24
    ) -> int:
        if not self.frames:
            raise IndexError("No frames available.")
        fps_ratio = animation_fps / engine_fps
        anim_frame = int(frame_clock * fps_ratio)
        return anim_frame % len(self.frames)

    def get_current_frame(
        self, frame_clock: int, animation_fps: int, engine_fps: int = 24
    ) -> Frame:
        return self.frames[self._get_index(frame_clock, animation_fps, engine_fps)]
