from __future__ import annotations
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from src.scenario import Scenario

from .animation import Frame, Point, Segment, Fill
from .camera import Camera
from .entity import EngineEntity
from .clock import Clock


class Engine:
    def __init__(self, scenario: Scenario) -> None:
        self.rides = scenario.rides
        self.entities: list[EngineEntity] = scenario.rides
        self.background: EngineEntity = scenario.background

        self.xlim = 1
        self.ylim = self.xlim
        self.fps_target = scenario.rules.target_fps
        self.clock = Clock()
        self.camera = Camera()
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.centre = Point(self.xlim / 2, self.ylim / 2)
        self._move_speed = 1.0
        self._zoom_rate = 1.5
        self._rot_speed = 1.0
        self._keys_down: set[str] = set()

        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self._on_key_release)
        self.cull_pad_frac = 0.05
        self.z_index = 0

    # ---------- Input Handling ----------
    def add_engine_objects(self, engine_objects: list[EngineEntity]) -> None:
        for engine_object in engine_objects:
            self.entities.append(engine_object)

    # Add this helper inside Engine
    def _depth_key(self, e: EngineEntity) -> float:
        # Larger positive => farther away (back). Use camera-relative y.
        return e.position.y - self.camera.position.y

    def _on_key_press(self, event):
        k = (event.key or "").lower()
        if k == "escape":
            plt.close(self.fig)
            return
        self._keys_down.add(k)

    def _on_key_release(self, event):
        k = (event.key or "").lower()
        self._keys_down.discard(k)

    def _draw_frame(self, frame: Frame):
        for draw in frame:
            if isinstance(draw, Segment):
                self.ax.plot(
                    [draw.start.x, draw.end.x],
                    [draw.start.y, draw.end.y],
                    color=draw.line.color,
                    linestyle=draw.line.style,
                    marker=draw.line.marker,
                    linewidth=draw.line.weight,
                    alpha=draw.line.alpha,
                    scalex=False,  # <-- stop x autoscale
                    scaley=False,
                    zorder=self.z_index,
                )
            elif isinstance(draw, Fill):
                poly = Polygon(
                    [(p.x, p.y) for p in draw.points],
                    closed=True,
                    facecolor=draw.color,
                    edgecolor=draw.edgecolor or draw.color,
                    alpha=draw.alpha,
                    zorder=self.z_index,
                )
                self.ax.add_patch(poly)
            self.z_index += 1

    def _get_transformed_frame(self, entity: EngineEntity) -> Frame:
        frame = entity.get_frame(self.clock.frame, self.fps_target)

        EPS = 1e-6
        HEIGHT_SCALE_FACTOR = 7.0
        WORLD_X_FACTOR = 0.2

        pos = entity.position
        cam_x = self.camera.position.x
        cam_y = self.camera.position.y
        horizon_y = self.centre.y
        centre_x = self.centre.x

        def project_ground_y(distance: float) -> float:
            return horizon_y - (self.camera.horizon_speed / max(distance, EPS))

        def perspective_scale(distance: float) -> float:
            return (self.camera.render_distance_scale * 10.0) / max(distance, EPS)

        entity_h = max(EPS, float(entity.size.height))
        cam_h = max(EPS, float(self.camera.height) * HEIGHT_SCALE_FACTOR)
        height_ratio = entity_h / cam_h

        distance = max(EPS, pos.y - cam_y)
        scale = perspective_scale(distance) * height_ratio
        y_base = project_ground_y(distance)

        def to_screen(local_x: float, local_y: float) -> Point:
            x_screen = ((pos.x * WORLD_X_FACTOR + local_x - cam_x) * scale) + centre_x
            y_screen = y_base + (local_y * scale)
            return Point(x_screen, y_screen)

        transformed: Frame = []
        for draw in frame:
            if isinstance(draw, Segment):
                transformed.append(
                    Segment(
                        start=to_screen(draw.start.x, draw.start.y),
                        end=to_screen(draw.end.x, draw.end.y),
                        line=draw.line,
                    )
                )
            elif isinstance(draw, Fill):
                pts = [to_screen(p.x, p.y) for p in draw.points]
                transformed.append(
                    Fill(
                        points=pts,
                        color=draw.color,
                        alpha=min(1.0, draw.alpha),
                        edgecolor=draw.edgecolor,
                    )
                )

        return transformed

    def _draw_scene(self):
        self.ax.clear()
        self.camera.update_from_input(self._keys_down, self.clock.dt)

        # Background first (no camera transforms)
        if self.background:
            self._draw_frame(
                self.background.get_frame(self.clock.frame, self.fps_target)
            )

        # Entities back-to-front
        for entity in sorted(self.entities, key=self._depth_key, reverse=True):
            frame = self._get_transformed_frame((entity))
            self._draw_frame(frame)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        self.z_index = 0

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
