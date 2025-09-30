# main.py

from assets.pirate_ship import PirateShip
from engine.engine import Engine
import matplotlib.pyplot as plt

if __name__ == "__main__":
    engine = Engine()
    engine.add(PirateShip(engine))
    engine.run(fps_target=24)
    plt.show()