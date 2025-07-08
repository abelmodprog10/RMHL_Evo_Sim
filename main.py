from core import config
from core.world import World
from entities.agent import Agent
from entities.plant import Plant
from entities.prey import Prey
from entities.predator import Predator


from display.pygame_display import PygameDisplay

def main():
    w = World(config.WORLD_WIDTH, config.WORLD_HEIGHT)

    plants = [Plant() for _ in range(config.N_PLANTS)]
    preys = [Prey() for _ in range(config.N_PREY)]
    predators = [Predator() for _ in range(config.N_PREDATORS)]

    agents = preys + predators

    for entity in plants + agents:
        w.add_entity(entity)

    display = PygameDisplay(w)

    while True:
        for agent in agents:
            agent.step()
        w.step()
        display.handle_events()
        display.draw()

if __name__ == "__main__":
    main()
