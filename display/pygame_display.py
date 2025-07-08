import pygame
import math
from core import config
from systems.vision import vision_system
import colorsys
from systems.colour import Colour
from systems.size import Size
class PygameDisplay:
    def __init__(self, world):

        self.draw_fov = False

        self.world = world
        self.width = int(world.width)
        self.height = int(world.height)
        self.clock = pygame.time.Clock()
        # Add extra space at the top for UI elements
        self.ui_height = 60
        self.total_height = self.height + self.ui_height
        self.sidebar_width = 300
        self.total_width = self.width + self.sidebar_width
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))

        # Changed: Remove max_history_length to keep all data
        self.entity_counts_history = {
            "Plant": [],
            "Prey": [],
            "Predator": [],
        }

        pygame.init()
        self.screen = pygame.display.set_mode((self.total_width, self.total_height))
        pygame.display.set_caption("EvoSim Continuous")
        self.clock = pygame.time.Clock()

                
        # Initialize font for text rendering
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Define colors
        self.colors = {
            "Plant": (34, 139, 34),     # green
            "Prey": (30, 144, 255),     # blue
            "Predator": (220, 20, 60),  # red
            "Background": (20, 30, 40), # dark blue-gray
            "UI_Background": (50, 50, 50),  # dark gray for UI
            "Text": (255, 255, 255),    # white text
            "Grid": (60, 60, 60),       # subtle grid lines
        }

        # Entity display properties
        self.entity_sizes = {
            "Plant": 4,
            "Prey": 6,
            "Predator": 8,
        }

    def draw(self):
        # Fill the entire screen with background
        self.screen.fill(self.colors["Background"])
        
        # Draw optional grid for reference (background layer)
        self.draw_grid()
        
        # Draw all entities (main simulation layer)
        self.draw_entities()
        
        # Draw all agents' FOVs (overlay on entities)
        if self.draw_fov:
            for agent in self.world.entities:
                if hasattr(agent, 'genome'):  # Only for agents with vision
                    self.draw_agent_fov(agent, vision_system)
        
        # Update data for UI elements
        self.update_counts_history()
        trait_averages = self.world.compute_trait_averages()

        # Draw UI elements on top (foreground layer)
        self.draw_sidebar(self.screen, self.font, trait_averages, self.width)
        self.draw_ui()


        pygame.display.flip()
        fps = self.clock.get_fps()
        fps_text = self.font.render(f'FPS: {fps:.2f}', True, pygame.Color('white'))
        self.screen.blit(fps_text, (10, 10))  # draw at top-left corner

        self.clock.tick(config.FPS or 30)

    def draw_grid(self):
        """Draw subtle grid lines for reference"""
        grid_size = 50  # Grid spacing
        grid_y_offset = self.ui_height
        
        # Vertical lines
        for x in range(0, self.width, grid_size):
            pygame.draw.line(self.screen, self.colors["Grid"], 
                           (x, grid_y_offset), (x, self.total_height), 1)
        
        # Horizontal lines
        for y in range(grid_y_offset, self.total_height, grid_size):
            pygame.draw.line(self.screen, self.colors["Grid"], 
                           (0, y), (self.width, y), 1)

    def draw_entities(self):
        """Draw all entities in the world"""
        grid_y_offset = self.ui_height
        
        for entity in self.world.entities:
            entity_type = getattr(entity, 'type', 'Unknown')
            
           # Get color based on genome or fallback to default
            if hasattr(entity, 'genome') and hasattr(entity.genome, 'get_trait'):
                entity_colour = Colour(entity)
                color = entity_colour.get_rgb()
            else:
                color = self.colors.get(entity_type, (169, 169, 169))
            
            base_size = self.entity_sizes.get(entity_type, 5)

            if hasattr(entity, 'genome') and hasattr(entity.genome, 'get_trait'):
                size = Size(entity, base_size).get_size()
            else:
                size = base_size


            
            # Position with UI offset
            x = int(entity.x)
            y = int(entity.y) + grid_y_offset
            
            # Draw entity based on type
            if entity_type == 'Predator':
                self.draw_triangle(x, y, size, color, entity)
            elif entity_type == 'Plant':
                self.draw_plant_rect(x, y, size, color)
            else:
                # Draw as circle for Prey and other entities
                pygame.draw.circle(self.screen, color, (x, y), size)
                
                # Draw border for better visibility
                border_color = tuple(max(0, c - 50) for c in color)
                pygame.draw.circle(self.screen, border_color, (x, y), size, 2)
            
            # Draw health bar for agents
            #if hasattr(entity, 'health') and entity_type in ['Prey', 'Predator']:
                #self.draw_health_bar(entity, x, y, size)
            
            # Draw energy level indicator
            #if hasattr(entity, 'energy') and entity_type in ['Prey', 'Predator']:
               # self.draw_energy_indicator(entity, x, y, size)

    ''''def get_genome_color(self, entity):
        """Convert genome color trait to RGB color using HSV"""
        if not hasattr(entity, 'genome') or not hasattr(entity.genome, 'get_trait'):
            return self.colors.get(entity.type, (169, 169, 169))
        
        # Get color trait (0.0 to 1.0) and use as hue
        hue = entity.genome.get_trait('colour') or 0.5
        
        # Use fixed saturation and value for all entities since shapes distinguish them
        saturation = 0.8
        value = 0.9
        
        # Convert HSV to RGB
        r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # Convert to 0-255 range
        return (int(r * 255), int(g * 255), int(b * 255))'''

    def draw_plant_rect(self, x, y, size, color):
        """Draw an elongated rectangle for plants"""
        # Make it narrow and tall (like a plant stem/blade)
        width = max(2, size // 2)  # Narrow width
        height = size * 2          # Tall height
        
        # Create rectangle centered on the position
        rect = pygame.Rect(x - width//2, y - height//2, width, height)
        
        # Draw filled rectangle
        pygame.draw.rect(self.screen, color, rect)
        
        # Draw border for better visibility
        border_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.rect(self.screen, border_color, rect, 1)

    def draw_triangle(self, x, y, size, color, entity):
        """Draw a triangle for predators, pointing in the direction they're facing"""
        # Get the entity's angle (direction it's facing)
        angle = getattr(entity, 'angle', 0)
        
        # Calculate triangle points relative to center
        # Base triangle pointing right (0 radians)
        points = [
            (size, 0),           # tip
            (-size//2, -size//2), # bottom left
            (-size//2, size//2)   # top left
        ]
        
        # Rotate points based on entity's angle
        rotated_points = []
        for px, py in points:
            # Rotate point around origin
            rotated_x = px * math.cos(angle) - py * math.sin(angle)
            rotated_y = px * math.sin(angle) + py * math.cos(angle)
            
            # Translate to entity position
            rotated_points.append((x + rotated_x, y + rotated_y))
        
        # Draw filled triangle
        pygame.draw.polygon(self.screen, color, rotated_points)
        
        # Draw border for better visibility
        border_color = tuple(max(0, c - 50) for c in color)
        pygame.draw.polygon(self.screen, border_color, rotated_points, 2)

    def draw_health_bar(self, entity, x, y, size):
        """Draw health bar above entity"""
        bar_width = size * 2
        bar_height = 3
        bar_x = x - bar_width // 2
        bar_y = y - size - 8

        # Background
        pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Clamp health_ratio between 0 and 1
        health_ratio = max(0.0, min(entity.health / 100.0, 1.0))

        health_width = int(bar_width * health_ratio)
        health_color = (255, int(255 * health_ratio), 0)  # Red to yellow

        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_width, bar_height))

    def draw_energy_indicator(self, entity, x, y, size):
        """Draw energy level as inner circle brightness"""
        if hasattr(entity, 'energy'):
            max_energy = getattr(config, 'MAX_ENERGY', 100)
            energy_ratio = max(0, min(1, entity.energy / max_energy))

            # Draw inner circle with brightness based on energy
            inner_size = max(1, size - 2)
            brightness = int(100 + 155 * energy_ratio)  # range: 100–255
            inner_color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, inner_color, (x, y), inner_size)


    def draw_ui(self):
        """Draw the UI elements at the top of the screen"""
        # Fill UI background
        ui_rect = pygame.Rect(0, 0, self.width, self.ui_height)
        pygame.draw.rect(self.screen, self.colors["UI_Background"], ui_rect)
        
        # Get entity counts
        plant_count = len(self.world.get_all_entities_by_type("Plant"))
        prey_count = len(self.world.get_all_entities_by_type("Prey"))
        predator_count = len(self.world.get_all_entities_by_type("Predator"))
        total_entities = len(self.world.entities)
        
        # Draw step counter
        step_text = self.font.render(f"Step: {self.world.step_count}", True, self.colors["Text"])
        self.screen.blit(step_text, (10, 10))
        
        # Draw entity counts
        y_pos = 35
        counts_text = self.small_font.render(
            f"Plants: {plant_count}  Prey: {prey_count}  Predators: {predator_count}  Total: {total_entities}", 
            True, self.colors["Text"]
        )
        self.screen.blit(counts_text, (10, y_pos))
        
        # Draw colored legend
        legend_x = self.width - 300
        legend_y = 10
        
        # Plant legend
        pygame.draw.circle(self.screen, self.colors["Plant"], (legend_x + 8, legend_y + 8), 8)
        plant_legend = self.small_font.render("Plant", True, self.colors["Text"])
        self.screen.blit(plant_legend, (legend_x + 20, legend_y))
        
        # Prey legend
        pygame.draw.circle(self.screen, self.colors["Prey"], (legend_x + 88, legend_y + 8), 8)
        prey_legend = self.small_font.render("Prey", True, self.colors["Text"])
        self.screen.blit(prey_legend, (legend_x + 100, legend_y))
        
        # Predator legend
        pygame.draw.circle(self.screen, self.colors["Predator"], (legend_x + 158, legend_y + 8), 8)
        predator_legend = self.small_font.render("Predator", True, self.colors["Text"])
        self.screen.blit(predator_legend, (legend_x + 170, legend_y))
        
        # FPS counter
        fps_text = self.small_font.render(f"FPS: {int(self.clock.get_fps())}", True, self.colors["Text"])
        self.screen.blit(fps_text, (self.width - 80, 35))

    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                elif event.key == pygame.K_SPACE:
                    # Pause/unpause functionality
                    print(f"Current step: {self.world.step_count}")
                    print(f"Entities - Plants: {len(self.world.get_all_entities_by_type('Plant'))}, "
                          f"Prey: {len(self.world.get_all_entities_by_type('Prey'))}, "
                          f"Predators: {len(self.world.get_all_entities_by_type('Predator'))}")
                elif event.key == pygame.K_g:
                    # Toggle grid visibility
                    pass  # Could implement grid toggle
                elif event.key == pygame.K_r:
                    # Reset world
                    print("Reset not implemented yet")

    def update_counts_history(self):
        # Changed: No longer limit history length - keep all data
        for species in self.entity_counts_history:
            count = len(self.world.get_all_entities_by_type(species))
            self.entity_counts_history[species].append(count)

    def draw_sidebar(self, screen, font, trait_averages, x_offset):
        padding_x = 10
        padding_y = 10
        line_height_title = 24
        line_height_trait = 20
        y = padding_y

        # Draw trait averages (keep your improved version)
        for species, traits in trait_averages.items():
            text = font.render(f"{species}:", True, (255, 255, 255))
            screen.blit(text, (x_offset + padding_x, y))
            y += line_height_title

            for trait, value in traits.items():
                trait_text = font.render(f"{trait}: {value:.2f}", True, (200, 200, 200))
                screen.blit(trait_text, (x_offset + padding_x + 10, y))
                y += line_height_trait
            y += padding_y

        # Draw entity counts plot below trait averages
        plot_width = self.sidebar_width - 2 * padding_x
        plot_height = 100
        plot_x = x_offset + padding_x
        plot_y = y + padding_y

        # Background of plot area
        pygame.draw.rect(screen, (30, 30, 30), (plot_x, plot_y, plot_width, plot_height))
        pygame.draw.line(screen, (255, 255, 255), (self.width, 0), (self.width, self.total_height))
        # Draw axes lines
        pygame.draw.line(screen, (100, 100, 100), (plot_x, plot_y + plot_height), (plot_x + plot_width, plot_y + plot_height), 2)  # x-axis
        pygame.draw.line(screen, (100, 100, 100), (plot_x, plot_y), (plot_x, plot_y + plot_height), 2)  # y-axis

        species_colors = {
            "Plant": (34, 139, 34),
            "Prey": (30, 144, 255),
            "Predator": (220, 20, 60),
        }

        # Find max count to scale y-axis
        max_count = 1
        for counts in self.entity_counts_history.values():
            if counts:
                max_count = max(max_count, max(counts))

        # Changed: Draw line plots for each species with full history compression
        for species, counts in self.entity_counts_history.items():
            if len(counts) < 2:
                continue
            color = species_colors.get(species, (200, 200, 200))
            points = []
            n = len(counts)
            
            # Calculate points based on total data length (compression)
            for i, count in enumerate(counts):
                # X position spreads all data across the plot width
                x = plot_x + int((i / max(1, n - 1)) * plot_width)
                y_pos = plot_y + plot_height - int((count / max_count) * plot_height)
                points.append((x, y_pos))
            
            if len(points) > 1:
                pygame.draw.lines(screen, color, False, points, 2)

        # Draw legend below plot
        legend_y = plot_y + plot_height + 5
        for i, species in enumerate(self.entity_counts_history.keys()):
            legend_text = font.render(species, True, species_colors.get(species, (200, 200, 200)))
            screen.blit(legend_text, (plot_x + i * 70, legend_y))

        # Add step range indicator
        if any(self.entity_counts_history.values()):
            total_steps = len(next(iter(self.entity_counts_history.values())))
            if total_steps > 0:
                step_text = self.small_font.render(f"Steps 1-{total_steps}", True, (150, 150, 150))
                screen.blit(step_text, (plot_x, plot_y + plot_height + 25))

    def draw_agent_fov(self, agent, vision_system):
        """Draw agent's field of view"""
        if not hasattr(agent, 'visible_entities'):
            return
        
        # Get the UI offset
        grid_y_offset = self.ui_height
        
        # Get eye positions
        eye_positions = vision_system._get_eye_positions(agent)
        
        # Colors for different eyes
        eye_colors = [(255, 100, 100, 50), (100, 255, 100, 50)]  # Red, Green with alpha
        
        for eye_idx, eye_angle in enumerate(eye_positions):
            # Calculate absolute eye angle (relative to world)
            absolute_eye_angle = agent.angle + eye_angle
            
            # Calculate FOV boundaries
            fov_start = absolute_eye_angle - vision_system.eye_fov / 2
            fov_end = absolute_eye_angle + vision_system.eye_fov / 2
            
            # Create FOV arc points with UI offset
            points = [(int(agent.x), int(agent.y) + grid_y_offset)]  # Start at agent center with offset
            
            # Add arc points
            num_points = 20
            for i in range(num_points + 1):
                angle = fov_start + (fov_end - fov_start) * i / num_points
                x = int(agent.x + math.cos(angle) * vision_system.max_vision_range)
                y = int(agent.y + math.sin(angle) * vision_system.max_vision_range) + grid_y_offset
                points.append((x, y))
            
            # Clip points to stay within the main simulation area (not overlap sidebar)
            clipped_points = []
            for x, y in points:
                # Keep points within the main simulation area
                if x <= self.width and y >= grid_y_offset:
                    clipped_points.append((min(x, self.width), y))
            
            # Draw FOV cone only if we have enough points and they're in the simulation area
            if len(clipped_points) > 2:
                pygame.draw.polygon(self.screen, eye_colors[eye_idx % len(eye_colors)], clipped_points)
        
        # Draw visible entities with lines (with UI offset and clipping)
        for entity_data in agent.visible_entities:
            entity = entity_data['entity']
            color = (255, 255, 0) if entity_data['binocular'] else (255, 255, 255)  # Yellow if binocular
            
            # Apply UI offset to both start and end points
            start_pos = (int(agent.x), int(agent.y) + grid_y_offset)
            end_pos = (int(entity.x), int(entity.y) + grid_y_offset)
            
            # Only draw lines that stay within the simulation area
            if start_pos[0] <= self.width and end_pos[0] <= self.width:
                pygame.draw.line(self.screen, color, start_pos, end_pos, 1)