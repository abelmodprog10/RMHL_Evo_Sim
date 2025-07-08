import pygame
import numpy as np
import noise
import sys

# Parameters
WIDTH, HEIGHT = 800, 500
TILE_SIZE = 4  # Each tile will be 4x4 pixels
MAP_W, MAP_H = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE
SCALE = 30.0
THRESHOLD = 0.2
OCTAVES = 3
SEED = np.random.randint(0, 10000)

# Colors
ROCK_COLOR = (50, 50, 50)
GROUND_COLOR = (180, 180, 180)

def generate_rock_map(width, height, scale, threshold, octaves, seed):
    rock_map = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            value = noise.pnoise2((x + seed) / scale,
                                  (y + seed) / scale,
                                  octaves=octaves)
            rock_map[y, x] = 1 if value > threshold else 0
    return rock_map

def draw_map(screen, rock_map):
    for y in range(MAP_H):
        for x in range(MAP_W):
            color = ROCK_COLOR if rock_map[y, x] == 1 else GROUND_COLOR
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, color, rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Perlin Rock Map (Fast Pygame)")
    clock = pygame.time.Clock()

    rock_map = generate_rock_map(MAP_W, MAP_H, SCALE, THRESHOLD, OCTAVES, SEED)
    draw_map(screen, rock_map)

    pygame.display.flip()

    # Main loop
    running = True
    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
