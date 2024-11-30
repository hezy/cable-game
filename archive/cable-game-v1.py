import pygame
import sys
from enum import Enum
from typing import List, Tuple

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Game:
    def __init__(self, width: int = 20, height: int = 20):
        pygame.init()
        self.cell_size = 30
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width * self.cell_size, height * self.cell_size))
        pygame.display.set_caption("Cable Game")
        
        # Initialize game state
        self.cable = [(1, height-2)]  # Start near bottom left
        self.direction = Direction.RIGHT
        self.outlet = (width-2, 1)  # Power outlet near top right
        self.running = True
        
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
            new_head in self.cable):
            self.running = False
            return
            
        self.cable.append(new_head)
        
        # Check win condition
        if new_head == self.outlet:
            print("You win!")
            self.running = False
    
    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        
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
            clock.tick(5)  # 5 FPS for visible cable growth
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
