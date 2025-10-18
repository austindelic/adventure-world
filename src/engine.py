from __future__ import annotations

"""Main render/update engine for Adventure World.

This module wires together the clock, camera, and entities, handling
input, update, and drawing with matplotlib.
"""

import time
from typing import Protocol

from src.scenario import Scenario

from .animation import Fill, Frame, Point, Segment
from .camera import Camera
from .clock import Clock, ClockProtocol
from .entity import EngineEntity
from .renderer import MatplotlibRenderer, RendererProtocol


class EngineProtocol(Protocol):
    """Formal interface describing the minimal Engine API."""

    # --- Core state ---
    entities: list[EngineEntity]
    clock: ClockProtocol

    # --- Entity management ---
    def add_engine_objects(self, engine_objects: list[EngineEntity]) -> None: ...

    # --- Time and update ---
    def _update_all(self) -> None: ...

    # --- Rendering (optional) ---
    def run(self, fps_target: int | None = None) -> None: ...

    # renderer hooks
    @property
    def keys_down(self) -> set[str]: ...
    def depth_key(self, e: EngineEntity) -> float: ...
    def on_key_press(self, key: str) -> None: ...
    def on_key_release(self, key: str) -> None: ...


class Engine(EngineProtocol):
    def __init__(self, scenario: Scenario) -> None:
        self.rides = scenario.rides
        self.entities: list[EngineEntity] = scenario.rides
        self.background: EngineEntity | None = scenario.background
        self.xlim: float = 1.0
        self.ylim: float = self.xlim
        self.fps_target = scenario.rules.target_fps
        self.clock: ClockProtocol = Clock()
        self.camera = Camera()
        self.centre = Point(self.xlim / 2, self.ylim / 2)
        self._move_speed = 1.0
        self._zoom_rate = 1.5
        self._rot_speed = 1.0
        self._keys_down: set[str] = set()
        self.renderer: RendererProtocol = MatplotlibRenderer()
        # hook input to renderer window
        if isinstance(self.renderer, MatplotlibRenderer):
            self.renderer.attach_input(self)

    # ---------- Input Handling ----------
    def add_engine_objects(self, engine_objects: list[EngineEntity]) -> None:
        for engine_object in engine_objects:
            self.entities.append(engine_object)

    # Add this helper inside Engine
    def _depth_key(self, e: EngineEntity) -> float:
        # Larger positive => farther away (back). Use camera-relative y.
        return e.position.y - self.camera.position.y

    def on_key_press(self, key: str) -> None:
        self._keys_down.add(key)

    def on_key_release(self, key: str) -> None:
        self._keys_down.discard(key)

    # Renderer drives drawing; expose helpers used by renderer
    @property
    def keys_down(self) -> set[str]:
        return self._keys_down

    # ---------- Update Cycle ----------
    def _update_all(self):
        """Update logic for all entities after drawing."""
        if self.background:
            self.background.update(self.clock)
        for obj in self.entities:
            obj.update(self.clock)

    # ---------- Run Loop ----------
    def run(self, fps_target: int | None = None):
        """Main render/update loop."""
        if fps_target is not None:
            self.fps_target = fps_target
        target_dt = 1.0 / self.fps_target
        import matplotlib.pyplot as plt

        plt.ion()
        while self.renderer.is_open():
            frame_start = time.perf_counter()

            # Tick timing
            self.clock.tick()

            # ---- Collect + Draw all via renderer ----
            self.renderer.render(self)
            # ---- Update after draw ----
            self._update_all()

            # ---- FPS sync ----
            elapsed = time.perf_counter() - frame_start
            sleep_for = target_dt - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

            actual = time.perf_counter() - frame_start
            if actual > 0:
                print(f"FPS: {1.0 / actual:.2f}")

            plt.pause(1e-6)
