"""
Cable Game
A snake - like game. Use the arrow keys to navigate the cable (green) to the power outlet (red square). Don't let the cable's head come in contact with the walls, obstacles, and the cable itslef.
"""

import pygame
import sys
import random
from enum import Enum
from typing import List, Tuple, Set


class Direction(Enum):
    """Enum representing the four cardinal directions."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class Game:
    def __init__(
        self, width: int = 40, height: int = 40, num_obstacles: int = 50
    ):
        """
        Initialize the game.

        Args:
            width (int): The width of the game grid. Default is 40.
            height (int): The height of the game grid. Default is 40.
            num_obstacles (int): The number of obstacles to generate. Default is 50.
        """
        pygame.init()
        self.cell_size = 20
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode(
            (width * self.cell_size, height * self.cell_size)
        )
        pygame.display.set_caption("Cable Game")

        self.cable = [(1, height - 2)]
        self.direction = Direction.RIGHT
        self.obstacles = self._generate_correlated_obstacles(num_obstacles)
        self.outlet = self._generate_outlet()
        self.running = True

    def _get_valid_neighbors(
        self, pos: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Get the valid neighboring positions of a given position.

        Args:
            pos (Tuple[int, int]): The position to get neighbors for.

        Returns:
            List[Tuple[int, int]]: A list of valid neighboring positions.
        """
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                new_x, new_y = pos[0] + dx, pos[1] + dy
                if (
                    0 <= new_x < self.width
                    and 0 <= new_y < self.height
                    and (new_x, new_y) != self.cable[0]
                ):
                    neighbors.append((new_x, new_y))
        return neighbors

    def _generate_correlated_obstacles(
        self, num_obstacles: int
    ) -> Set[Tuple[int, int]]:
        """
        Generate spatially correlated obstacles.

        Args:
            num_obstacles (int): The number of obstacles to generate.

        Returns:
            Set[Tuple[int, int]]: A set of obstacle positions.
        """
        obstacles = set()
        # Start with random seed obstacles
        while len(obstacles) < num_obstacles // 4:
            pos = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )
            if pos != self.cable[0] and pos != (1, self.height - 2):
                obstacles.add(pos)

        # Grow obstacles with spatial correlation
        while len(obstacles) < num_obstacles:
            existing = random.choice(list(obstacles))
            neighbors = self._get_valid_neighbors(existing)
            if neighbors:
                new_pos = random.choice(neighbors)
                if new_pos not in obstacles:
                    obstacles.add(new_pos)

        return obstacles

    def _generate_outlet(self) -> Tuple[int, int]:
        """
        Generate a valid outlet position.

        Returns:
            Tuple[int, int]: The position of the outlet.
        """
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
        """Handle user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._process_direction_change(event.key)

    def _process_direction_change(self, key: int) -> None:
        """
        Process direction change based on user input.

        Args:
            key (int): The key code of the pressed key.
        """
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
        """Update the game state."""
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
            self.running = False
            return

        self.cable.append(new_head)

        if new_head == self.outlet:
            print("You win!")
            self.running = False

    def draw(self) -> None:
        """Draw the game objects on the screen."""
        self.screen.fill((0, 0, 0))

        for obstacle in self.obstacles:
            rect = pygame.Rect(
                obstacle[0] * self.cell_size,
                obstacle[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(self.screen, (128, 128, 128), rect)

        for segment in self.cable:
            rect = pygame.Rect(
                segment[0] * self.cell_size,
                segment[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(self.screen, (0, 255, 0), rect)

        outlet_rect = pygame.Rect(
            self.outlet[0] * self.cell_size,
            self.outlet[1] * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(self.screen, (255, 0, 0), outlet_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Run the game loop."""
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
