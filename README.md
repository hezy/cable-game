# Cable Game

Cable Game is a game inspired by the classic Snake game, but with a unique twist. The objective is to navigate a cable through a field of moving obstacles to reach the outlet.

## How to Play

- Use the arrow keys (up, down, left, right) to control the direction of the cable.
- Guide the cable through the obstacles without colliding with them or the walls.
- Reach the red outlet to win the game.
- If the cable collides with an obstacle, wall, or itself, the game ends.

## Features

- Randomly generated obstacles that move in different directions.
- Correlated obstacle generation for a more challenging gameplay.
- Sound effects for success and failure.
- Customizable game board size and number of obstacles.

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/your-username/cable-game.git
   ```

2. Install the required dependencies:

   ```
   pip install pygame
   ```

3. Run the game:

   ```
   python cable_game.py
   ```

## Customization

You can customize the game by modifying the following parameters in the `__main__` section of the code:

- `width`: The width of the game board (default: 40).
- `height`: The height of the game board (default: 40).
- `num_obstacles`: The number of obstacles to generate (default: 50).

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).