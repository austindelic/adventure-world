"""
File: main.py
Author: Austin Delic (austin@austindelic.com)
"""

from assets import FerrisWheel
from engine import Engine
import matplotlib.pyplot as plt

if __name__ == "__main__":
    engine = Engine(fps_target=24)
    engine.add([FerrisWheel()])
    engine.add([FerrisWheel()])

    engine.run()
    engine.add([FerrisWheel()])
    plt.show()
