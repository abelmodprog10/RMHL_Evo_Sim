from core import config
from core.world import World
from entities.agent import Agent
from entities.plant import Plant
from entities.prey import Prey
from entities.predator import Predator


def main():
    w = World(config.WORLD_WIDTH, config.WORLD_HEIGHT)  # Use World directly

    plants = [Plant() for _ in range(config.N_PLANTS)]
    preys = [Prey() for _ in range(config.N_PREY)]
    predators = [Predator() for _ in range(config.N_PREDATORS)]

    # Add all entities to the world
    for plant in plants:
        w.add_entity(plant)
    for prey in preys:
        w.add_entity(prey)
    for predator in predators:
        w.add_entity(predator)

    # Combine all agents for stepping
    agents = plants + preys + predators

    steps = 10
    for step in range(steps):
        print(f"Step {step + 1}")
        for agent in agents:
            agent.step()
        w.step()
        w.display()  # show the grid after each step

if __name__ == "__main__":
    main()
