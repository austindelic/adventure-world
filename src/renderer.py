"""Rendering backends for Adventure World.

Defines a simple renderer protocol and a Matplotlib-based implementation
that draws frames produced by EngineEntities.
"""

from __future__ import annotations

import time
from typing import Protocol

import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

from .animation import Fill, Frame, Point, Segment
from .camera import Camera
from .clock import ClockProtocol
from .entity import EngineEntity


class RendererProtocol(Protocol):
    def is_open(self) -> bool: ...
    def render(self, engine: "RenderEngineProtocol") -> None: ...


class RenderEngineProtocol(Protocol):
    # minimal surface used by the renderer; avoids circular imports
    entities: list[EngineEntity]
    background: EngineEntity | None
    clock: ClockProtocol
    camera: Camera
    xlim: float
    ylim: float
    fps_target: int
    centre: Point

    @property
    def keys_down(self) -> set[str]: ...

    def depth_key(self, e) -> float: ...
    def on_key_press(self, key: str) -> None: ...
    def on_key_release(self, key: str) -> None: ...


class MatplotlibRenderer(RendererProtocol):
    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots()
        self.ax.autoscale(True)
        self.z_index = 0

    # --- Window lifecycle ---
    def is_open(self) -> bool:
        return plt.fignum_exists(self.fig.number)

    # --- Input hookup ---
    def attach_input(self, engine: "RenderEngineProtocol") -> None:
        def _on_key_press(event):
            k = (event.key or "").lower()
            if k == "escape":
                plt.close(self.fig)
                return
            engine.on_key_press(k)

        def _on_key_release(event):
            k = (event.key or "").lower()
            engine.on_key_release(k)

        self.fig.canvas.mpl_connect("key_press_event", _on_key_press)
        self.fig.canvas.mpl_connect("key_release_event", _on_key_release)

    # --- Drawing helpers ---
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
                    scalex=False,
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

    def _get_transformed_frame(self, engine: "RenderEngineProtocol", entity) -> Frame:
        frame = entity.get_frame(engine.clock.frame, engine.fps_target)

        # Small constants for numerical safety and projection tuning
        EPS = 1e-6
        HEIGHT_SCALE_FACTOR = 1
        WORLD_X_FACTOR = 0.1
        PAD = 1e-6

        xmin, xmax = 0.0, float(engine.xlim)
        ymin, ymax = 0.0, float(engine.ylim)

        pos = entity.position
        cam_x = engine.camera.position.x * WORLD_X_FACTOR
        cam_y = engine.camera.position.y
        horizon_y = engine.centre.y
        centre_x = engine.centre.x
        distance = pos.y - cam_y
        if distance + EPS <= 0:
            return []

        def _project_ground_y(distance: float) -> float:
            return horizon_y - (engine.camera.horizon_speed / max(distance, EPS))

        def _perspective_scale(distance: float) -> float:
            return (engine.camera.render_distance_scale * 10) / max(distance, EPS)

        entity_h = max(EPS, float(entity.target_size.height))
        cam_h = max(EPS, float(engine.camera.height) * (HEIGHT_SCALE_FACTOR * 10.0))
        height_ratio = entity_h / cam_h

        base_scale = _perspective_scale(distance)
        parallax_scale = base_scale
        shape_scale = base_scale * height_ratio
        y_base = _project_ground_y(distance)

        def _to_screen(local_x: float, local_y: float) -> Point:
            world_x = (pos.x * WORLD_X_FACTOR - cam_x) * parallax_scale
            x_screen = centre_x + world_x + local_x * shape_scale
            y_screen = y_base + local_y * shape_scale
            return Point(x_screen, y_screen)

        def _in_view(p: Point) -> bool:
            return (xmin - PAD) <= p.x <= (xmax + PAD) and (ymin - PAD) <= p.y <= (
                ymax + PAD
            )

        transformed: Frame = []
        for draw in frame:
            if isinstance(draw, Segment):
                s = _to_screen(draw.start.x, draw.start.y)
                e = _to_screen(draw.end.x, draw.end.y)
                if _in_view(s) or _in_view(e):
                    transformed.append(Segment(start=s, end=e, line=draw.line))

            elif isinstance(draw, Fill):
                pts = [_to_screen(p.x, p.y) for p in draw.points]
                if len(pts) >= 3:
                    transformed.append(
                        Fill(
                            points=pts,
                            color=draw.color,
                            alpha=min(1.0, draw.alpha),
                            edgecolor=draw.edgecolor,
                        )
                    )

        return transformed

    # --- Main render ---
    def render(self, engine: "RenderEngineProtocol") -> None:
        self.ax.clear()

        # Camera input update
        engine.camera.update_from_input(engine.keys_down, engine.clock.dt)

        # Background first (no camera transforms)
        if engine.background:
            self._draw_frame(
                engine.background.get_frame(engine.clock.frame, engine.fps_target)
            )

        # Entities back-to-front
        for entity in sorted(engine.entities, key=engine.depth_key, reverse=True):
            frame = self._get_transformed_frame(engine, entity)
            self._draw_frame(frame)

        self.ax.set_xlim(0, engine.xlim)
        self.ax.set_ylim(0, engine.ylim)
        self.ax.set_aspect("equal", adjustable="box")
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()
        plt.pause(1e-6)
        self.z_index = 0
