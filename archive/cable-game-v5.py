import pygame
import sys
import random
from enum import Enum
from typing import List, Tuple, Set


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Game:
    # More pattern variations
    STILL_LIFE_PATTERNS = [
        [(0, 0), (1, 0), (0, 1), (1, 1)],  # Block
        [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1), (1, 2)],  # Beehive
        [(0, 1), (1, 0), (1, 2), (2, 1)],  # Diamond
    ]

    OSCILLATOR_PATTERNS = [
        [(0, 0), (1, 0), (2, 0)],  # Blinker
        [(0, 0), (0, 1), (0, 2), (2, 0), (2, 1), (2, 2)],  # Toad
        [(1, 0), (0, 1), (2, 1), (1, 2)],  # Cross
        [(0, 0), (1, 0), (2, 0), (0, 2), (1, 2), (2, 2)],  # Snake
    ]

    UNSTABLE_PATTERNS = [
        [(0, 0), (1, 0), (2, 0), (2, 1), (1, 2)],  # Glider
        [(0, 0), (0, 1), (1, 0), (2, 1), (1, 2)],  # R-pentomino
        [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0)],  # 5-cell line
        [(0, 0), (1, 0), (0, 1), (2, 1)],  # Ship
        [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2)],  # Noise maker
        [(0, 0), (1, 1), (2, 2), (3, 3)],  # Diagonal
        [(0, 0), (1, 0), (2, 0), (0, 1), (2, 1)],  # U-shape
    ]

    def __init__(self, width: int = 40, height: int = 40):
        self.width = width
        self.height = height
        self.cell_size = 20
        self.running = True
    
        # Initialize pygame and create screen
        pygame.init()
        self.screen = pygame.display.set_mode((width * self.cell_size, height * self.cell_size))
    
        # Initialize game state
        self.direction = Direction.RIGHT
        self.cable = [(0, 0)]  # Start at top-left corner
        self.obstacles = self._generate_mixed_patterns()
        self.outlet = self._generate_outlet()

        # Initialize counter for life updates
        self.update_counter = 0
        self.life_update_frequency = 2

        # Initialize sounds
        self.success_sound = pygame.mixer.Sound("success.wav")
        self.fail_sound = pygame.mixer.Sound("fail.wav")

    def _generate_random_soup(
        self, center: Tuple[int, int], size: int = 4
    ) -> Set[Tuple[int, int]]:
        soup = set()
        x, y = center
        for dx in range(-size, size + 1):
            for dy in range(-size, size + 1):
                if random.random() < 0.5:  # Increased probability to 50%
                    new_x, new_y = x + dx, y + dy
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    soup.add((new_x, new_y))
        return soup

    def _generate_mixed_patterns(self) -> Set[Tuple[int, int]]:
        obstacles = set()

        # Increased pattern counts
        pattern_counts = {"still": 3, "oscillator": 4, "unstable": 5, "soup": 3}

        for pattern_type, count in pattern_counts.items():
            attempts = 0
        
    placed = 0
            while placed < count and attempts < 50:
                x = random.randint(2, self.width - 8)
                y = random.randint(2, self.height - 8)

                # Reduced buffer zone for denser placement
                area_clear = True
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        check_pos = (x + dx, y + dy)
                        if check_pos in obstacles or check_pos in self.cable:
                            area_clear = False
                            break

                if area_clear:
                    new_cells = set()
                    if pattern_type == "still":
                        pattern = random.choice(self.STILL_LIFE_PATTERNS)
                        new_cells = self._place_pattern(pattern, (x, y))
                    elif pattern_type == "oscillator":
                        pattern = random.choice(self.OSCILLATOR_PATTERNS)
                        # Randomly flip oscillators
                        if random.random() < 0.5:
                            pattern = [(y, x) for (x, y) in pattern]
                        new_cells = self._place_pattern(pattern, (x, y))
                    elif pattern_type == "unstable":
                        pattern = random.choice(self.UNSTABLE_PATTERNS)
                        rotated = self._rotate_pattern(
                            pattern, random.randint(0, 3)
                        )
                        new_cells = self._place_pattern(rotated, (x, y))
                    else:  # soup
                        new_cells = self._generate_random_soup(
                            (x, y), size=5
                        )  # Increased soup size

                    if new_cells:
                        obstacles.update(new_cells)
                        placed += 1

                attempts += 1

        return obstacles

    def _rotate_pattern(
        self, pattern: List[Tuple[int, int]], rotations: int
    ) -> List[Tuple[int, int]]:
        for _ in range(rotations):
            pattern = [(y, -x) for (x, y) in pattern]
        min_x = min(x for x, y in pattern)
        min_y = min(y for x, y in pattern)
        return [(x - min_x, y - min_y) for (x, y) in pattern]

    def _place_pattern(
        self, pattern: List[Tuple[int, int]], offset: Tuple[int, int]
    ) -> Set[Tuple[int, int]]:
        placed_cells = set()
        for x, y in pattern:
            new_x, new_y = x + offset[0], y + offset[1]
            if (
                0 <= new_x < self.width
                and 0 <= new_y < self.height
                and (new_x, new_y) not in self.cable
            ):
                placed_cells.add((new_x, new_y))
        return placed_cells

    def _get_neighbors_count(self, pos: Tuple[int, int]) -> int:
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                neighbor = (pos[0] + dx, pos[1] + dy)
                if (
                    0 <= neighbor[0] < self.width
                    and 0 <= neighbor[1] < self.height
                    and neighbor in self.obstacles
                ):
                    count += 1
        return count

    def _update_life(self) -> None:
        new_obstacles = set()
        for x in range(self.width):
            for y in range(self.height):
                pos = (x, y)
                if pos in self.cable or pos == self.outlet:
                    continue

                neighbors = self._get_neighbors_count(pos)

                if pos in self.obstacles:
                    if neighbors in [2, 3]:
                        new_obstacles.add(pos)
                else:
                    if neighbors == 3:
                        new_obstacles.add(pos)

        self.obstacles = new_obstacles

    def _generate_outlet(self) -> Tuple[int, int]:
        while True:
            pos = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )
            if (
                pos not in self.obstacles
                and pos != self.cable[0]
                and abs(pos[0] - self.cable[0][0])
                + abs(pos[1] - self.cable[0][1])
                > self.width / 2
            ):
                return pos

    def handle_input(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._process_direction_change(event.key)

    def _process_direction_change(self, key: int) -> None:
        current_dx, current_dy = self.direction.value
        new_direction = None

        if key == pygame.K_UP and current_dy == 0:
            new_direction = Direction.UP
        elif key == pygame.K_DOWN and current_dy == 0:
            new_direction = Direction.DOWN
        elif key == pygame.K_LEFT and current_dx == 0:
            new_direction = Direction.LEFT
        elif key == pygame.K_RIGHT and current_dx == 0:
            new_direction = Direction.RIGHT

        if new_direction:
            self.direction = new_direction

    def update(self) -> None:
        self.update_counter += 1
        if self.update_counter >= self.life_update_frequency:
            self._update_life()
            self.update_counter = 0

        head = self.cable[-1]
        dx, dy = self.direction.value
        new_head = (head[0] + dx, head[1] + dy)

        if (
            new_head[0] < 0
            or new_head[0] >= self.width
            or new_head[1] < 0
            or new_head[1] >= self.height
            or new_head in self.cable
            or new_head in self.obstacles
        ):
            self.fail_sound.play()
            self.running = False
            return

        self.cable.append(new_head)

        if new_head == self.outlet:
            self.success_sound.play()
            print("You win!")
            self.running = False

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))

        # Draw obstacles with neighbor-based coloring
        for obstacle in self.obstacles:
            rect = pygame.Rect(
                obstacle[0] * self.cell_size,
                obstacle[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            neighbor_count = self._get_neighbors_count(obstacle)
            # Ensure color values stay within valid range (0-255)
            intensity = min(100 + neighbor_count * 20, 255)
            color = (intensity, intensity, 128)
            pygame.draw.rect(self.screen, color, rect)

        # Draw cable
        for segment in self.cable:
            rect = pygame.Rect(
                segment[0] * self.cell_size,
                segment[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(self.screen, (0, 255, 0), rect)

        # Draw outlet
        outlet_rect = pygame.Rect(
            self.outlet[0] * self.cell_size,
            self.outlet[1] * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(self.screen, (255, 0, 0), outlet_rect)

        pygame.display.flip()

    def run(self) -> None:
        clock = pygame.time.Clock()
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(5)
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
