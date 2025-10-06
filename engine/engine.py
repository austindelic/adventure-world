"""
File: engine.py
Author: Austin Delic (austin@austindelic.com)
"""

from __future__ import annotations
import time
import matplotlib.pyplot as plt
from .object import EngineObject
from .camera import Camera
from .time import CLock
from math import exp, cos, sin


class Engine:
    def __init__(
        self,
        eng_objects: list[EngineObject] | None = None,
        xlim: tuple[float, float] = (0.0, 1.0),
        ylim: tuple[float, float] = (0.0, 1.0),
        fps_target: int = 24,
    ) -> None:
        self.eng_objects: list[EngineObject] = (
            [] if eng_objects is None else eng_objects
        )
        self.xlim = xlim
        self.ylim = ylim
        self.fps_target = fps_target
        self.clock = CLock()
        self.camera = Camera()

        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        self._move_speed = 1.0  # world units per second (before zoom compensation)
        self._zoom_rate = 1.5  # multiplicative per second (exp-based)
        self._rot_speed = 1.0  # radians per second
        self._keys_down: set[str] = set()

        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self._on_key_release)

    def _on_key_press(self, event):
        k = (event.key or "").lower()
        if k == "escape":
            plt.close(self.fig)  # quit on ESC
            return
        self._keys_down.add(k)

    def _on_key_release(self, event):
        k = (event.key or "").lower()
        self._keys_down.discard(k)

    # --- apply held keys every frame ---
    def _apply_camera_controls(self):
        dt = self.clock.dt
        kd = self._keys_down

        # pan (WASD/Arrows). Use camera rotation + zoom compensation so it feels consistent.
        pan_x = ("right" in kd) - ("left" in kd)
        pan_y = ("up" in kd) - ("down" in kd)
        if pan_x or pan_y:
            # rotate pan vector by camera rotation so W is "forward"
            c, s = cos(self.camera.rot), sin(self.camera.rot)
            wx = pan_x * c - pan_y * s
            wy = pan_x * s + pan_y * c
            speed = (self._move_speed * dt) / max(self.camera.zoom, 1e-6)
            self.move_camera(dx=wx * speed, dy=wy * speed)

        # zoom (Q = in, E = out) – exponential, scale-invariant
        zoom_dir = int("z" in kd) - int("c" in kd)
        if zoom_dir:
            factor = exp(zoom_dir * self._zoom_rate * dt)
            self.zoom_camera(factor)

        # rotate (R = CCW, F = CW)
        rot_dir = int("r" in kd) - int("f" in kd)
        if rot_dir:
            self.set_camera(rot=self.camera.rot + rot_dir * self._rot_speed * dt)

    def add(self, objects: list[EngineObject]) -> None:
        for object in objects:
            self.eng_objects.append(object)

    def set_camera(
        self,
        x: float | None = None,
        y: float | None = None,
        zoom: float | None = None,
        rot: float | None = None,
    ) -> None:
        if x is not None:
            self.camera.x = x
        if y is not None:
            self.camera.y = y
        if zoom is not None:
            self.camera.set_zoom(zoom)
        if rot is not None:
            self.camera.set_rot(rot)

    def move_camera(self, dx: float = 0.0, dy: float = 0.0) -> None:
        self.camera.move(dx, dy)

    def zoom_camera(self, factor: float) -> None:
        self.camera.set_zoom(self.camera.zoom * factor)

    def draw_frame(self) -> None:
        self.ax.clear()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        # ← move the "screen" via camera before drawing EVERYTHING
        self._apply_camera_controls()

        for obj in self.eng_objects:
            obj.update(self.clock)
            obj.draw(self.ax, self.clock.frame, self.fps_target, camera=self.camera)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    @staticmethod
    def sec_to_frames(seconds: float, fps: int = 24) -> int:
        return int(round(seconds * fps))

    def run(self, fps_target: int | None = None) -> None:
        if fps_target is not None:
            self.fps_target = fps_target
        target_dt = 1.0 / self.fps_target
        plt.ion()
        while True:
            frame_start = time.perf_counter()
            self.clock.tick()
            self.draw_frame()
            elapsed = time.perf_counter() - frame_start
            sleep_for = target_dt - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)
            actual = time.perf_counter() - frame_start
            if actual > 0:
                print(f"FPS: {1.0/actual:.2f}")
            plt.pause(1e-6)
