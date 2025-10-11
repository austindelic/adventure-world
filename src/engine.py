from __future__ import annotations
import time
from math import cos, exp, isfinite, sin
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Polygon

from src.scenario import Scenario

from .animation import Frame, Point, Segment, Fill
from .camera import Camera
from .entity import EngineEntity
from .clock import Clock


class Engine:
    def __init__(self, scenario: Scenario) -> None:
        self.rides = scenario.rides
        self.eng_objects: list[EngineEntity] = []
        self.background: EngineEntity | None = scenario.background
        self.xlim = 1
        self.ylim = 1
        self.fps_target = scenario.rules.target_fps
        self.clock = Clock()
        self.camera = Camera()
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        self._move_speed = 1.0
        self._zoom_rate = 1.5
        self._rot_speed = 1.0
        self._keys_down: set[str] = set()

        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self._on_key_release)
        self.cull_pad_frac = 0.05

    # ---------- Input Handling ----------
    def add_engine_objects(self, engine_objects: list[EngineEntity]) -> None:
        for engine_object in engine_objects:
            self.eng_objects.append(engine_object)

    def _on_key_press(self, event):
        k = (event.key or "").lower()
        if k == "escape":
            plt.close(self.fig)
            return
        self._keys_down.add(k)

    def _on_key_release(self, event):
        k = (event.key or "").lower()
        self._keys_down.discard(k)

    # ---------- Camera Controls ----------
    def _apply_camera_controls(self):
        dt = self.clock.dt
        kd = self._keys_down

        pan_x = ("right" in kd) - ("left" in kd)
        pan_y = ("up" in kd) - ("down" in kd)
        if pan_x or pan_y:
            c, s = cos(self.camera.rot), sin(self.camera.rot)
            wx = pan_x * c - pan_y * s
            wy = pan_x * s + pan_y * c
            speed = (self._move_speed * dt) / max(self.camera.zoom, 1e-6)
            self.move_camera(dx=wx * speed, dy=wy * speed)

        zoom_dir = int("z" in kd) - int("c" in kd)
        if zoom_dir:
            factor = exp(zoom_dir * self._zoom_rate * dt)
            self.zoom_camera(factor)

        rot_dir = int("r" in kd) - int("f" in kd)
        if rot_dir:
            self.set_camera(rot=self.camera.rot + rot_dir * self._rot_speed * dt)

    # ---------- Camera helpers ----------
    def set_camera(self, x=None, y=None, zoom=None, rot=None):
        if x is not None:
            self.camera.x = x
        if y is not None:
            self.camera.y = y
        if zoom is not None:
            self.camera.set_zoom(zoom)
        if rot is not None:
            self.camera.set_rot(rot)

    def move_camera(self, dx=0.0, dy=0.0):
        self.camera.move(dx, dy)

    def zoom_camera(self, factor: float):
        self.camera.set_zoom(self.camera.zoom * factor)

    # ---------- Core Draw ----------
    def _draw_frame(self, frame: Frame):
        """Draw a single animation frame (Segments + Fills)."""
        lines, colors, widths, alphas = [], [], [], []

        for draw in frame:
            # ---- Handle line segments ----
            if isinstance(draw, Segment):
                s = self.camera.to_view(draw.start)
                e = self.camera.to_view(draw.end)

                # Skip if both endpoints are off-screen
                if not self._in_view(s) and not self._in_view(e):
                    continue

                lines.append([(s.x, s.y), (e.x, e.y)])
                colors.append(draw.line.color)
                widths.append(draw.line.weight)
                alphas.append(draw.line.alpha)

            # ---- Handle polygon fills ----
            elif isinstance(draw, Fill):
                transformed = [self.camera.to_view(p) for p in draw.points]
                if all(not self._in_view(p) for p in transformed):
                    continue

                polygon = Polygon(
                    [(p.x, p.y) for p in transformed],
                    closed=True,
                    facecolor=draw.color,
                    edgecolor=draw.edgecolor or draw.color,
                    alpha=draw.alpha,
                )
                self.ax.add_patch(polygon)

        # ---- Batch render all line segments ----
        if lines:
            lc = LineCollection(lines, colors=colors, linewidths=widths, alpha=None)
            if len(set(alphas)) == 1:
                lc.set_alpha(alphas[0])
            self.ax.add_collection(lc)

    def _in_view(self, p: Point) -> bool:
        x_lo, x_hi = self.ax.get_xlim()
        y_lo, y_hi = self.ax.get_ylim()
        pad_x = self.cull_pad_frac * (x_hi - x_lo)
        pad_y = self.cull_pad_frac * (y_hi - y_lo)
        ex_lo, ex_hi = x_lo - pad_x, x_hi + pad_x
        ey_lo, ey_hi = y_lo - pad_y, y_hi + pad_y
        return (
            isfinite(p.x)
            and isfinite(p.y)
            and (ex_lo <= p.x <= ex_hi)
            and (ey_lo <= p.y <= ey_hi)
        )

    # ---------- Frame Collection + Draw ----------
    def _collect_frames(self) -> Frame:
        """Collect all frames (background + all objects) before drawing."""
        frames: list[Frame] = []

        # Background first (if any)
        if self.background:
            frames.append(self.background.get_frame(self.clock.frame, self.fps_target))

        # Then all entities
        for obj in self.eng_objects:
            frames.append(obj.get_frame(self.clock.frame, self.fps_target))

        # Flatten all drawables into one frame
        combined: Frame = [draw for frame in frames for draw in frame]
        return combined

    def _draw_scene(self):
        """Draw all collected frames at once."""
        self.ax.clear()

        self._apply_camera_controls()

        full_frame = self._collect_frames()
        self._draw_frame(full_frame)

        # Refresh display
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    # ---------- Update Cycle ----------
    def _update_all(self):
        """Update logic for all entities after drawing."""
        if self.background:
            self.background.update(self.clock)
        for obj in self.eng_objects:
            obj.update(self.clock)

    # ---------- Run Loop ----------
    def run(self, fps_target: int | None = None):
        """Main render/update loop."""
        if fps_target is not None:
            self.fps_target = fps_target
        target_dt = 1.0 / self.fps_target
        plt.ion()

        while plt.fignum_exists(self.fig.number):
            frame_start = time.perf_counter()

            # Tick timing
            self.clock.tick()

            # ---- Collect + Draw all ----
            self._draw_scene()

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
