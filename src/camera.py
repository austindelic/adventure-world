from .animation import Point


class Camera:
    position: Point = Point(0.0, -10)
    height: float = 1.75  # m
    zoom: float = 1.0
    x_movement_speed: float = 0.1
    y_movement_speed: float = 0.5
    render_distance_scale: float = 1
    horizon_speed: float = 1

    def move(self, dx: float, dy: float) -> None:
        """Move camera position by delta."""
        self.position.x += dx
        self.position.y += dy

    def set_pos(self, x: float, y: float) -> None:
        self.position = Point(x, y)

    def set_zoom(self, zoom: float) -> None:
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
