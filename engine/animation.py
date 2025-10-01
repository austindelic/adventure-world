# animation.py

from dataclasses import dataclass
from typing import Literal


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Line:
    color: Literal["b", "g", "r", "c", "m", "y", "k", "w"]
    weight: float
    style: Literal["-", "--", "-.", ":"] = "-"
    marker: Literal["", "o", "s", "^", "v", "x", "+"] = ""
    alpha: float = 1.0

    def __post_init__(self):
        allowed_colors = {"b", "g", "r", "c", "m", "y", "k", "w"}
        if self.color not in allowed_colors:
            raise ValueError(
                f"Invalid color {self.color}, must be one of {allowed_colors}"
            )
        allowed_styles = {"-", "--", "-.", ":"}
        if self.style not in allowed_styles:
            raise ValueError(
                f"Invalid style {self.style}, must be one of {allowed_styles}"
            )
        allowed_markers = {"", "o", "s", "^", "v", "x", "+"}
        if self.marker not in allowed_markers:
            raise ValueError(
                f"Invalid marker {self.marker}, must be one of {allowed_markers}"
            )
        if not (0.0 <= self.alpha <= 1.0):
            raise ValueError("alpha must be between 0 and 1")


@dataclass
class Segment:
    start: Point
    end: Point
    line: Line


type Frame = list[Segment]


class Animation:
    """A collection of frames for an object."""

    def __init__(self, frames: list[Frame] | None = None) -> None:
        self.frames = [] if frames is None else frames

    def _get_index(
        self, frame_clock: int, animation_fps: int, engine_fps: int = 24
    ) -> int:
        """Get index safely, wrapping around if needed.

        Args:
            frame_clock: Current engine frame count
            animation_fps: Target FPS for this animation
            engine_fps: Engine's target FPS (default 24)

        Returns:
            The current frame index for this animation
        """
        if not self.frames:
            raise IndexError("No frames available.")

        # Calculate how many animation frames should have passed
        # based on the ratio of animation_fps to engine_fps
        fps_ratio = animation_fps / engine_fps
        animation_frame = int(frame_clock * fps_ratio)

        return animation_frame % len(self.frames)

    def get_current_frame(
        self, frame_clock: int, animation_fps: int, engine_fps: int = 24
    ) -> Frame:
        """Return the current Frame based on animation's target framerate.

        Args:
            frame_clock: Current engine frame count
            animation_fps: Target FPS for this animation
            engine_fps: Engine's target FPS (default 24)

        Returns:
            The current frame for this animation
        """
        index = self._get_index(frame_clock, animation_fps, engine_fps)
        return self.frames[index]
