# engine.py

from engine.object import EngineObject
import matplotlib.pyplot as plt
import time


class Engine:
    """
    Minimal renderer:
      - holds SimulationObject instances
      - draws a single (static) frame on a Matplotlib Axes
      - no physics/update step (assumes objects are already in final positions)
    Expect each SimulationObject to implement:
        draw(self, ax) -> None
    """

    def __init__(
        self,
        eng_objects: list[EngineObject] = [],
        xlim: tuple[int, int] = (0, 1),
        ylim: tuple[int, int] = (0, 1),
        fps_target: int = 24,
    ) -> None:
        self.eng_objects: list[EngineObject] = eng_objects
        self.xlim = xlim
        self.ylim = ylim
        self.fps_target = fps_target

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)
        self.ax.set_aspect("equal", adjustable="box")

        self.frame_clock = 0

    def add(self, obj: EngineObject) -> None:
        self.eng_objects.append(obj)

    def draw_frame(self) -> None:
        """Draw a single static frame."""
        self.ax.clear()
        self.ax.set_aspect("equal", adjustable="box")
        self.ax.set_xlim(self.xlim)
        self.ax.set_ylim(self.ylim)

        for obj in self.eng_objects:
            obj.draw(self.ax, self.frame_clock, self.fps_target)
            obj.update(self.frame_clock)

        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    @staticmethod
    def frames_to_sec(time: int, frame_clock: int = 24):
        return time * frame_clock

    def run(self, fps_target: int | None = None) -> None:
        """
        Re-draws the same frame 'frames' times.
        Useful if you want a persistent window without updates.
        """
        if fps_target is not None:
            self.fps_target = fps_target

        target_frame_time: float = 1.0 / self.fps_target  # seconds per frame
        plt.ion()
        start = time.perf_counter()
        while True:
            # start timer
            self.draw_frame()
            self.frame_clock += 1
            end = time.perf_counter()
            start = time.perf_counter()
            frame_time = end - start
            remaining = target_frame_time - frame_time
            if remaining > 0:
                time.sleep(remaining)
            actual_frame_time = time.perf_counter() - start
            actual_fps = (
                1.0 / actual_frame_time if actual_frame_time > 0 else float("inf")
            )
            print(f"FPS: {actual_fps:.2f}")
            # Needed to let matplotlib update the window
            plt.pause(10e-6)  # tiny pause to keep GUI responsive
