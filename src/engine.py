from __future__ import annotations

import time
from typing import Protocol

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.patches import Polygon

from src.scenario import Scenario
from .animation import Fill, Frame, Line, Point, Segment
from .camera import Camera
from .clock import Clock, ClockProtocol
from .entity import EngineEntity


class EngineProtocol(Protocol):
    entities: list[EngineEntity]
    clock: ClockProtocol

    def add_engine_objects(self, engine_objects: list[EngineEntity]) -> None: ...
    def _update_all(self) -> None: ...
    def _draw_scene(self) -> None: ...
    def run(self, fps_target: int | None = None) -> None: ...


class Engine(EngineProtocol):
    def __init__(self, scenario: Scenario) -> None:
        self.rides = scenario.rides
        self.entities: list[EngineEntity] = scenario.rides
        self.background: EngineEntity = scenario.background

        # Viewport
        self.xlim = 1.0
        self.ylim = self.xlim
        self.centre = Point(self.xlim / 2, self.ylim / 2)

        # Timing / camera
        self.fps_target = scenario.rules.target_fps
        self.clock = Clock()
        self.camera = Camera()

        # Matplotlib
        self.fig, self.ax = plt.subplots()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(0, self.xlim)
        self.ax.set_ylim(0, self.ylim)
        self.ax.set_facecolor("white")
        self.fig.canvas.mpl_connect("key_press_event", self._on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", self._on_key_release)

        # Input
        self._keys_down: set[str] = set()

        # Misc
        self.cull_pad_frac = 0.05
        self._fps_print_every = 30
        self._frame_counter = 0

    # ---------- Input Handling ----------
    def add_engine_objects(self, engine_objects: list[EngineEntity]) -> None:
        self.entities.extend(engine_objects)

    def _depth_key(self, e: EngineEntity) -> float:
        return e.position.y - self.camera.position.y  # farther back => larger

    def _on_key_press(self, event):
        k = (event.key or "").lower()
        if k == "escape":
            plt.close(self.fig)
            return
        self._keys_down.add(k)

    def _on_key_release(self, event):
        k = (event.key or "").lower()
        self._keys_down.discard(k)

    # ---------- Projection helpers (high-level) ----------
    def _project_entity_frames(self, entity: EngineEntity) -> tuple[Frame, Frame]:
        """
        Returns (back_and_sides, front) frames for the entity.
        Back/sides are drawn first, then front on top (seal).
        """
        frame = entity.get_frame(self.clock.frame, self.fps_target)

        EPS = 1e-6
        HEIGHT_SCALE_FACTOR = 1.0
        WORLD_X_FACTOR = 0.1
        PAD = 1e-6

        xmin, xmax = 0.0, float(self.xlim)
        ymin, ymax = 0.0, float(self.ylim)

        pos = entity.position
        cam_x = self.camera.position.x * WORLD_X_FACTOR
        cam_y = self.camera.position.y
        horizon_y = self.centre.y
        centre_x = self.centre.x

        # Early reject: object behind camera
        distance = pos.y - cam_y
        if distance <= EPS:
            return ([], [])

        def _project_ground_y(dist: float) -> float:
            return horizon_y - (self.camera.horizon_speed / max(dist, EPS))

        def _perspective_scale(dist: float) -> float:
            return (self.camera.render_distance_scale * 10.0) / max(dist, EPS)

        # Cache constant ratios for this entity
        ent_h = max(EPS, float(entity.target_size.height))
        cam_h = max(EPS, float(self.camera.height) * (HEIGHT_SCALE_FACTOR * 10.0))
        height_ratio = ent_h / cam_h

        def _project_point(local_x: float, local_y: float, entity_y: float) -> Point:
            dist = entity_y - cam_y
            if dist <= EPS:
                # offscreen/behind, return sentinel outside viewport for culling
                return Point(-1e9, -1e9)
            base_scale = _perspective_scale(dist)
            shape_scale = base_scale * height_ratio
            world_x = (pos.x * WORLD_X_FACTOR - cam_x) * base_scale
            return Point(
                centre_x + world_x + local_x * shape_scale,
                _project_ground_y(dist) + local_y * shape_scale,
            )

        def _in_view(p: Point) -> bool:
            return (xmin - PAD) <= p.x <= (xmax + PAD) and (ymin - PAD) <= p.y <= (
                ymax + PAD
            )

        depth = getattr(entity.size, "depth", 0.1)

        back_and_sides: Frame = []
        front: Frame = []

        for draw in frame:
            if isinstance(draw, Segment):
                s_front = _project_point(draw.start.x, draw.start.y, pos.y)
                e_front = _project_point(draw.end.x, draw.end.y, pos.y)
                s_back = _project_point(draw.start.x, draw.start.y, pos.y + depth)
                e_back = _project_point(draw.end.x, draw.end.y, pos.y + depth)

                # Back edge
                if _in_view(s_back) or _in_view(e_back):
                    back_and_sides.append(
                        Segment(
                            start=s_back,
                            end=e_back,
                            line=Line(
                                color=draw.line.color,
                                weight=draw.line.weight * 0.8,
                                style=draw.line.style,
                                marker=draw.line.marker,
                                alpha=draw.line.alpha * 0.6,
                            ),
                        )
                    )
                # Side connectors
                if _in_view(s_front) or _in_view(s_back):
                    back_and_sides.append(
                        Segment(
                            start=s_front,
                            end=s_back,
                            line=Line(
                                color=draw.line.color,
                                weight=draw.line.weight * 0.6,
                                style=":",
                                marker="",
                                alpha=draw.line.alpha * 0.5,
                            ),
                        )
                    )
                if _in_view(e_front) or _in_view(e_back):
                    back_and_sides.append(
                        Segment(
                            start=e_front,
                            end=e_back,
                            line=Line(
                                color=draw.line.color,
                                weight=draw.line.weight * 0.6,
                                style=":",
                                marker="",
                                alpha=draw.line.alpha * 0.5,
                            ),
                        )
                    )
                # Front edge
                if _in_view(s_front) or _in_view(e_front):
                    front.append(Segment(start=s_front, end=e_front, line=draw.line))

            elif isinstance(draw, Fill):
                front_pts = [_project_point(p.x, p.y, pos.y) for p in draw.points]
                back_pts = [
                    _project_point(p.x, p.y, pos.y + depth) for p in draw.points
                ]

                # Back face
                back_and_sides.append(
                    Fill(
                        points=back_pts,
                        color=draw.color,
                        alpha=draw.alpha * 0.6,
                        edgecolor=draw.edgecolor,
                    )
                )

                # Side walls (quads)
                n = len(draw.points)
                for i in range(n):
                    p1f, p2f = front_pts[i], front_pts[(i + 1) % n]
                    p1b, p2b = back_pts[i], back_pts[(i + 1) % n]
                    if any((_in_view(p) for p in (p1f, p2f, p1b, p2b))):
                        back_and_sides.append(
                            Fill(
                                points=[p1f, p2f, p2b, p1b],
                                color=draw.color,
                                alpha=draw.alpha * 0.4,
                                edgecolor=draw.edgecolor,
                            )
                        )

                # Front face
                front.append(
                    Fill(
                        points=front_pts,
                        color=draw.color,
                        alpha=draw.alpha,
                        edgecolor=draw.edgecolor,
                    )
                )

        return (back_and_sides, front)

    # ---------- Batched drawing ----------
    def _draw_scene(self):
        self.ax.cla()
        self.ax.set_xlim(0, self.xlim)
        self.ax.set_ylim(0, self.ylim)
        self.ax.set_aspect("equal", adjustable="box")

        # Update camera from input once per frame
        self.camera.update_from_input(self._keys_down, self.clock.dt)

        # --- Accumulators for batched drawing ---
        lines_back = []  # list of ((x0,y0),(x1,y1))
        lw_back = []  # linewidths
        lc_back = []  # colors
        la_back = []  # alphas
        polys_back = []  # list of Nx2 arrays for PatchCollection
        pc_face_back = []  # facecolors (rgba or color str)
        pc_edge_back = []  # edgecolors
        pa_back = []  # alphas

        lines_front, lw_front, lc_front, la_front = [], [], [], []
        polys_front, pc_face_front, pc_edge_front, pa_front = [], [], [], []

        # Background (no transform, drawn in its own small batch)
        if self.background:
            bg_frame = self.background.get_frame(self.clock.frame, self.fps_target)
            for draw in bg_frame:
                if isinstance(draw, Segment):
                    lines_back.append(
                        [(draw.start.x, draw.start.y), (draw.end.x, draw.end.y)]
                    )
                    lw_back.append(draw.line.weight)
                    lc_back.append(draw.line.color)
                    la_back.append(draw.line.alpha)
                elif isinstance(draw, Fill):
                    polys_back.append([(p.x, p.y) for p in draw.points])
                    pc_face_back.append(draw.color)
                    pc_edge_back.append(draw.edgecolor or draw.color)
                    pa_back.append(draw.alpha)

        # Entities back-to-front (farther first)
        for entity in sorted(self.entities, key=self._depth_key, reverse=True):
            back_and_sides, front = self._project_entity_frames(entity)

            # --- back & sides
            for draw in back_and_sides:
                if isinstance(draw, Segment):
                    lines_back.append(
                        [(draw.start.x, draw.start.y), (draw.end.x, draw.end.y)]
                    )
                    lw_back.append(draw.line.weight)
                    lc_back.append(draw.line.color)
                    la_back.append(draw.line.alpha)
                else:  # Fill
                    polys_back.append([(p.x, p.y) for p in draw.points])
                    pc_face_back.append(draw.color)
                    pc_edge_back.append(draw.edgecolor or draw.color)
                    pa_back.append(draw.alpha)

            # --- front
            for draw in front:
                if isinstance(draw, Segment):
                    lines_front.append(
                        [(draw.start.x, draw.start.y), (draw.end.x, draw.end.y)]
                    )
                    lw_front.append(draw.line.weight)
                    lc_front.append(draw.line.color)
                    la_front.append(draw.line.alpha)
                else:  # Fill
                    polys_front.append([(p.x, p.y) for p in draw.points])
                    pc_face_front.append(draw.color)
                    pc_edge_front.append(draw.edgecolor or draw.color)
                    pa_front.append(draw.alpha)

        # --- Explicit painter's algorithm control ---
        Z_BACK_FILL = 1.0
        Z_BACK_LINES = 1.1
        Z_FRONT_FILL = 1.2
        Z_FRONT_LINES = 1.3

        # BACK FILLS
        if polys_back:
            pc_back = PatchCollection(
                [Polygon(p, closed=True) for p in polys_back], match_original=True
            )
            pc_back.set_facecolor(pc_face_back)
            pc_back.set_edgecolor(pc_edge_back)
            pc_back.set_zorder(Z_BACK_FILL)
            if len(set(pa_back)) == 1:
                pc_back.set_alpha(pa_back[0])
            self.ax.add_collection(pc_back, autolim=False)

        # BACK SEGMENTS
        if lines_back:
            lc_back = LineCollection(lines_back, linewidths=lw_back, colors=lc_back)
            lc_back.set_zorder(Z_BACK_LINES)  # <- override auto zorder
            if len(set(la_back)) == 1:
                lc_back.set_alpha(la_back[0])
            self.ax.add_collection(lc_back, autolim=False)

        # FRONT FILLS
        if polys_front:
            pc_front = PatchCollection(
                [Polygon(p, closed=True) for p in polys_front], match_original=True
            )
            pc_front.set_facecolor(pc_face_front)
            pc_front.set_edgecolor(pc_edge_front)
            pc_front.set_zorder(Z_FRONT_FILL)
            if len(set(pa_front)) == 1:
                pc_front.set_alpha(pa_front[0])
            self.ax.add_collection(pc_front, autolim=False)

        # FRONT SEGMENTS
        if lines_front:
            lc_front = LineCollection(lines_front, linewidths=lw_front, colors=lc_front)
            lc_front.set_zorder(Z_FRONT_LINES)  # <- override auto zorder
            if len(set(la_front)) == 1:
                lc_front.set_alpha(la_front[0])
            self.ax.add_collection(lc_front, autolim=False)

        # One draw call
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    # ---------- Update Cycle ----------
    def _update_all(self):
        if self.background:
            self.background.update(self.clock)
        for obj in self.entities:
            obj.update(self.clock)

    # ---------- Run Loop ----------
    def run(self, fps_target: int | None = None):
        if fps_target is not None:
            self.fps_target = fps_target
        target_dt = 1.0 / self.fps_target
        plt.ion()
        while plt.fignum_exists(self.fig.number):
            frame_start = time.perf_counter()
            self.clock.tick()

            self._draw_scene()
            self._update_all()

            # Soft sync
            elapsed = time.perf_counter() - frame_start
            sleep_for = target_dt - elapsed
            if sleep_for > 0:
                time.sleep(sleep_for)

            self._frame_counter += 1
            if self._frame_counter % self._fps_print_every == 0:
                actual = time.perf_counter() - frame_start
                if actual > 0:
                    print(f"FPS: {1.0 / actual:.2f}")

            plt.pause(1e-6)

