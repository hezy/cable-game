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
    def __init__(self, width: int = 40, height: int = 40, num_obstacles: int = 50):
        pygame.init()
        self.cell_size = 20  # Smaller cells for larger grid
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width * self.cell_size, height * self.cell_size))
        pygame.display.set_caption("Cable Game")
        
        # Initialize game state
        self.cable = [(1, height-2)]
        self.direction = Direction.RIGHT
        self.obstacles = self._generate_obstacles(num_obstacles)
        self.outlet = self._generate_outlet()
        self.running = True
        
    def _generate_obstacles(self, num_obstacles: int) -> Set[Tuple[int, int]]:
        obstacles = set()
        while len(obstacles) < num_obstacles:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if pos != self.cable[0] and pos != (1, self.height-2):  # Avoid start position
                obstacles.add(pos)
        return obstacles
    
    def _generate_outlet(self) -> Tuple[int, int]:
        while True:
            pos = (random.randint(0, self.width-1), random.randint(0, self.height-1))
            if (pos not in self.obstacles and 
                pos != self.cable[0] and 
                abs(pos[0] - self.cable[0][0]) + abs(pos[1] - self.cable[0][1]) > self.width/2):
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
        head = self.cable[-1]
        dx, dy = self.direction.value
        new_head = (head[0] + dx, head[1] + dy)
        
        # Check for collisions
        if (new_head[0] < 0 or new_head[0] >= self.width or
            new_head[1] < 0 or new_head[1] >= self.height or
            new_head in self.cable or
            new_head in self.obstacles):
            self.running = False
            return
            
        self.cable.append(new_head)
        
        # Check win condition
        if new_head == self.outlet:
            print("You win!")
            self.running = False
    
    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        
        # Draw obstacles
        for obstacle in self.obstacles:
            rect = pygame.Rect(
                obstacle[0] * self.cell_size,
                obstacle[1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, (128, 128, 128), rect)
        
        # Draw cable
        for segment in self.cable:
            rect = pygame.Rect(
                segment[0] * self.cell_size,
                segment[1] * self.cell_size,
                self.cell_size,
                self.cell_size
            )
            pygame.draw.rect(self.screen, (0, 255, 0), rect)
        
        # Draw outlet
        outlet_rect = pygame.Rect(
            self.outlet[0] * self.cell_size,
            self.outlet[1] * self.cell_size,
            self.cell_size,
            self.cell_size
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
