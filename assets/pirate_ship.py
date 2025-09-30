import math
from engine.animation import Animation, Frame, Line, Point, Segment
from engine.engine import Engine
from engine.object import EngineObject

class PirateShip(EngineObject):
    def __init__(self, engine: Engine):
        self.hull_frame: Frame = [
            Segment(Point(0.068, 0.429), Point(0.103, 0.318), Line('g', 2.0)),
            Segment(Point(0.103, 0.318), Point(0.180, 0.244), Line('g', 2.0)),
            Segment(Point(0.180, 0.244), Point(0.312, 0.184), Line('g', 2.0)),
            Segment(Point(0.312, 0.184), Point(0.417, 0.173), Line('g', 2.0)),
            Segment(Point(0.417, 0.173), Point(0.597, 0.173), Line('g', 2.0)),
            Segment(Point(0.597, 0.173), Point(0.731, 0.185), Line('g', 2.0)),
            Segment(Point(0.731, 0.185), Point(0.833, 0.232), Line('g', 2.0)),
            Segment(Point(0.833, 0.232), Point(0.906, 0.292), Line('g', 2.0)),
            Segment(Point(0.906, 0.292), Point(0.950, 0.369), Line('g', 2.0)),
            Segment(Point(0.950, 0.369), Point(0.974, 0.434), Line('g', 2.0)),
            Segment(Point(0.974, 0.434), Point(0.802, 0.432), Line('g', 2.0)),
            Segment(Point(0.802, 0.432), Point(0.705, 0.353), Line('g', 2.0)),
            Segment(Point(0.705, 0.353), Point(0.524, 0.353), Line('g', 2.0)),
            Segment(Point(0.524, 0.353), Point(0.524, 0.703), Line('g', 2.0)),
            Segment(Point(0.524, 0.703), Point(0.524, 0.352), Line('g', 2.0)),
            Segment(Point(0.524, 0.352), Point(0.328, 0.353), Line('g', 2.0)),
            Segment(Point(0.328, 0.353), Point(0.225, 0.430), Line('g', 2.0)),
            Segment(Point(0.225, 0.430), Point(0.070, 0.430), Line('g', 2.0)),
        ]
        self.support_frame: Frame = [
            Segment(Point(0.2, 0.0), Point(0.525, 0.700), Line('r', 2.0)),
            Segment(Point(0.525, 0.700), Point(0.85, 0.0), Line('r', 2.0)),
            Segment(Point(0.85, 0.0), Point(0.2, 0.0), Line('r', 2.0)),
        ]
        anim = Animation([self.hull_frame + self.support_frame])
        size = 0.5
        start_point=Point(0.5, 0.5)
        self._pivot = (0.524, 0.703)         
        self._period_frames = 48               
        self._amp_deg = 20               


        self._hull_base = [
            (seg.start.x, seg.start.y, seg.end.x, seg.end.y)
            for seg in self.hull_frame
        ]

        self.running = False

        super().__init__(animation=anim, engine=engine, start_point=start_point, size=size)

    def update(self, frame_clock: int):
        if self.running:
    # advance time (keep your existing timing fields)
            current_frame = frame_clock % self._period_frames
            theta = math.radians(self._amp_deg) * math.sin(2 * math.pi * (current_frame / self._period_frames))
            origin = Point(*self._pivot)  # pivot as a Point

            for seg, (sx, sy, ex, ey) in zip(self.hull_frame, self._hull_base):
                seg.start = self._rotate(Point(sx, sy), theta, origin)
                seg.end   = self._rotate(Point(ex, ey), theta, origin)

        if frame_clock % self.engine.frames_to_sec(2) == 0:
                self.running =  not self.running
            
