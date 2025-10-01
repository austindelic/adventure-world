# main.py

from assets.pirate_ship import PirateShip
from assets.person import Person
from engine.engine import Engine
import matplotlib.pyplot as plt

if __name__ == "__main__":
    engine = Engine(fps_target=24)

    # Create a person with a custom animation framerate
    person = Person(engine)
    person.fps = 12  # Make the walking animation slower (12 FPS instead of default 24)

    engine.add(person)
    engine.run()
    plt.show()
