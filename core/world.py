from collections import defaultdict
from random import randint

print("Loading core.world module...")

class World:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Store entities by (x,y) position
        self.grid = defaultdict(list)

    def is_occupied(self, x, y):
        # Check if the cell at (x,y) is occupied by any entity
        return len(self.grid[(x % self.width, y % self.height)]) > 0

    def add_entity(self, entity, x=None, y=None):
        if x is None or y is None:
            # Try random positions until finding an unoccupied one
            attempts = 0
            while True:
                x_try = randint(0, self.width - 1)
                y_try = randint(0, self.height - 1)
                if not self.is_occupied(x_try, y_try):
                    x, y = x_try, y_try
                    break
                attempts += 1
                if attempts > 1000:
                    raise RuntimeError("Could not find an empty cell to add entity.")
        else:
            # If specific coordinates given, ensure unoccupied
            if self.is_occupied(x, y):
                raise ValueError(f"Cell ({x},{y}) is already occupied.")

        entity.x = x
        entity.y = y
        entity.world = self
        self.grid[(x, y)].append(entity)

    def move_entity(self, entity, new_x, new_y):
        new_x %= self.width
        new_y %= self.height
        if self.is_occupied(new_x, new_y):
            # Can't move: target cell is occupied
            # Optionally: just do nothing or raise an exception
            # Here we just do nothing (prevent move)
            return False
        # Remove from old cell
        self.grid[(entity.x, entity.y)].remove(entity)
        # Add to new cell
        entity.x = new_x
        entity.y = new_y
        self.grid[(new_x, new_y)].append(entity)
        return True

    def get_entities_at(self, x, y):
        return self.grid.get((x % self.width, y % self.height), [])

    def step(self):
        # Placeholder for world update logic if needed
        pass

    def display(self):
        cell_width = 2
        for y in range(self.height):
            row = ""
            for x in range(self.width):
                entities = self.get_entities_at(x, y)
                if entities:
                    e = entities[0]
                    if hasattr(e, 'type'):
                        if e.type == "Plant":
                            cell_str = "P"
                        elif e.type == "Prey":
                            cell_str = "r"
                        elif e.type == "Predator":
                            cell_str = "D"
                        else:
                            cell_str = "?"
                    else:
                        cell_str = "?"
                else:
                    cell_str = "."
                
                row += cell_str.ljust(cell_width)
            print(row)
        print()
