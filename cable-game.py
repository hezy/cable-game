"""
A game, inspired by snake, but different
"""

import pygame
import sys
import random
from enum import Enum
from typing import List, Tuple, Set


class Direction(Enum):
    """Represents the four cardinal directions."""

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

        :param width: The width of the game board (default: 40).
        :param height: The height of the game board (default: 40).
        :param num_obstacles: The number of obstacles to generate (default: 50).
        """
        pygame.init()
        pygame.mixer.init()
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
        self.obstacle_directions = {
            obs: self._random_direction() for obs in self.obstacles
        }
        self.outlet = self._generate_outlet()
        self.running = True

        self.success_sound = self._load_sound("success.wav", (440, 0, 1))
        self.fail_sound = self._load_sound("fail.wav", (220, 0, 1))

    def _load_sound(
        self, filename: str, synth_params: Tuple[int, int, int]
    ) -> pygame.mixer.Sound:
        """
        Load a sound file or synthesize a sound.

        :param filename: The name of the sound file to load.
        :param synth_params: The parameters for sound synthesis (frequency, start, duration).
        :return: The loaded or synthesized sound.
        """
        try:
            return pygame.mixer.Sound(filename)
        except:
            freq, start, duration = synth_params
            sample_rate = 44100
            samples = [
                min(
                    max(
                        int(
                            32767
                            * pygame.math.sin(
                                2 * 3.14159 * freq * t / sample_rate
                            )
                        ),
                        -32767,
                    ),
                    32767,
                )
                for t in range(int(sample_rate * duration))
            ]
            return pygame.mixer.Sound(buffer=bytes(samples))

    def _random_direction(self) -> Tuple[int, int]:
        """
        Generate a random direction.

        :return: A tuple representing the random direction.
        """
        return random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

    def _get_valid_neighbors(
        self, pos: Tuple[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Get the valid neighbors of a given position.

        :param pos: The position to get the neighbors of.
        :return: A list of valid neighboring positions.
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
        Generate correlated obstacles.

        :param num_obstacles: The number of obstacles to generate.
        :return: A set of obstacle positions.
        """
        obstacles = set()
        while len(obstacles) < num_obstacles // 4:
            pos = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )
            if pos != self.cable[0] and pos != (1, self.height - 2):
                obstacles.add(pos)

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
        Generate the outlet position.

        :return: The position of the outlet.
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

    def _update_obstacles(self) -> None:
        """Update the positions and directions of the obstacles."""
        new_obstacles = set()
        new_directions = {}

        for obs in self.obstacles:
            if random.random() < 0.1:
                self.obstacle_directions[obs] = self._random_direction()

            dx, dy = self.obstacle_directions[obs]
            new_pos = (obs[0] + dx, obs[1] + dy)

            if (
                0 < new_pos[0] < self.width - 1
                and 0 < new_pos[1] < self.height - 1
                and new_pos not in self.cable
                and new_pos != self.outlet
            ):
                new_obstacles.add(new_pos)
                new_directions[new_pos] = self.obstacle_directions[obs]
            else:
                new_obstacles.add(obs)
                self.obstacle_directions[obs] = self._random_direction()
                new_directions[obs] = self.obstacle_directions[obs]

        self.obstacles = new_obstacles
        self.obstacle_directions = new_directions

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

        :param key: The key code of the pressed key.
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
        self._update_obstacles()

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
        """Draw the game objects on the screen."""
        self.screen.fill((0, 0, 0))

        for obstacle in self.obstacles:
            dx, dy = self.obstacle_directions[obstacle]
            color = (128, 128, 128)
            if dx > 0:
                color = (160, 128, 128)
            elif dx < 0:
                color = (128, 160, 128)
            elif dy > 0:
                color = (128, 128, 160)
            elif dy < 0:
                color = (160, 160, 128)

            rect = pygame.Rect(
                obstacle[0] * self.cell_size,
                obstacle[1] * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(self.screen, color, rect)

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
