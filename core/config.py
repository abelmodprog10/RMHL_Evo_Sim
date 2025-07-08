import math
# === World dimensions ===
WORLD_WIDTH = 800
WORLD_HEIGHT = 500

# === Simulation parameters ===
FPS = 200               # Frames per second (controls simulation speed)
GROWTH_RATE = 5          # Number of plants that grow per step
PLANT_GROWTH_INTERVAL = 5  # World grows plants every N steps
REPRO_CHANCE = 1
REPRO_DISTANCE = 20

# === Agent counts ===
N_PREDATORS = 0
MAX_PREDATORS = math.inf

N_PREY = 10
MAX_PREY = 200

N_PLANTS = 1000
MAX_PLANTS = 1500

# === Energy and health ===
MAX_ENERGY = 100
MAX_HEALTH = 100
ENERGY_PER_STEP = 0.3    # Energy consumed per step

# === Movement defaults ===
DEFAULT_SPEED = 1
DEFAULT_TURN_RATE = 0.3

# Predator-specific movement
PREDATOR_SPEED = 1.5
PREDATOR_TURN_RATE = 0.4

# Prey-specific movement
PREY_SPEED = 0.8
PREY_TURN_RATE = 0.2

# === Hunger and damage ===
STARVATION_DAMAGE = 1    # Damage taken when very hungry (if used)

# === Energy values for food ===
PLANT_ENERGY_VALUE = 50
PREY_ENERGY_VALUE = 100  # Should be higher than plants

# === Plant growth parameters ===
PLANT_MATURITY_AGE = 100      # Steps before a plant can spread
PLANT_SPREAD_CHANCE = 0.1    # 10% chance per step for mature plants to spread
PLANT_SPREAD_RADIUS = 10

# === Genome ===
GENOME_DEFAULTS = {}
