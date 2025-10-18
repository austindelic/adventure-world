"""Camera model handling panning and simple depth illusion.

This camera is extremely lightweight and intended for a 2D scene with a
parallax-like depth cue provided by y-position.
"""

from .animation import Point


class Camera:
    """Mutable camera state and update logic."""

    position: Point = Point(0.0, -10)
    height: float = 1.0  # m
    zoom: float = 1.0
    x_movement_speed: float = 0.5
    y_movement_speed: float = x_movement_speed
    render_distance_scale: float = 1
    horizon_speed: float = 1

    def move(self, dx: float, dy: float) -> None:
        """Move camera position by delta."""
        self.position.x += dx
        self.position.y += dy

    def set_pos(self, x: float, y: float) -> None:
        """Set camera position to absolute coordinates."""
        self.position = Point(x, y)

    def set_zoom(self, zoom: float) -> None:
        """Clamp and set zoom, preventing non-positive values."""
        self.zoom = max(1e-6, zoom)

    # ---------- New movement logic ---------- #
    def update_from_input(self, keys_down: set[str], dt: float) -> None:
        """
        Handles top-down panning and forward/backward illusion control.
        - Up increases _depth_scale (move forward into scene)
        - Down decreases _depth_scale (move backward)
        - Left/Right pan across grid
        """
        # Forward/backward movement (Up/Down)
        if "up" in keys_down:
            self.position.y += self.y_movement_speed
        if "down" in keys_down:
            self.position.y -= self.y_movement_speed
        if "left" in keys_down:
            self.position.x -= self.x_movement_speed
        if "right" in keys_down:
            self.position.x += self.x_movement_speed
        if "a" in keys_down:
            self.x_movement_speed *= 0.9
            self.y_movement_speed *= 0.9
        if "d" in keys_down:
            self.x_movement_speed *= 1.1
            self.y_movement_speed *= 1.1
