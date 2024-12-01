import pygame
import sys
import random

WIDTH = 40
HEIGHT = 40
NUM_OBSTACLES = 50
CELL_SIZE = 20
SUCCESS_SOUND_FREQ = 440
FAIL_SOUND_FREQ = 220
SOUND_DURATION = 1

def load_sound(filename, synth_params):
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

def random_direction():
    return random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

def get_valid_neighbors(pos):
    neighbors = []
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            new_x, new_y = pos[0] + dx, pos[1] + dy
            if (
                0 <= new_x < WIDTH
                and 0 <= new_y < HEIGHT
                and (new_x, new_y) != cable[0]
            ):
                neighbors.append((new_x, new_y))
    return neighbors

def generate_correlated_obstacles():
    obstacles = set()
    while len(obstacles) < NUM_OBSTACLES // 4:
        pos = (
            random.randint(0, WIDTH - 1),
            random.randint(0, HEIGHT - 1),
        )
        if pos != cable[0] and pos != (1, HEIGHT - 2):
            obstacles.add(pos)

    while len(obstacles) < NUM_OBSTACLES:
        existing = random.choice(list(obstacles))
        neighbors = get_valid_neighbors(existing)
        if neighbors:
            new_pos = random.choice(neighbors)
            if new_pos not in obstacles:
                obstacles.add(new_pos)
    return obstacles

def generate_outlet():
    while True:
        pos = (
            random.randint(0, WIDTH - 1),
            random.randint(0, HEIGHT - 1),
        )
        if (
            pos not in obstacles
            and pos != cable[0]
            and abs(pos[0] - cable[0][0])
            + abs(pos[1] - cable[0][1])
            > WIDTH / 2
        ):
            return pos

def update_obstacles():
    global obstacles, obstacle_directions
    new_obstacles = set()
    new_directions = {}

    for obs in obstacles:
        if random.random() < 0.1:
            obstacle_directions[obs] = random_direction()

        dx, dy = obstacle_directions[obs]
        new_pos = (obs[0] + dx, obs[1] + dy)

        if (
            0 < new_pos[0] < WIDTH - 1
            and 0 < new_pos[1] < HEIGHT - 1
            and new_pos not in cable
            and new_pos != outlet
        ):
            new_obstacles.add(new_pos)
            new_directions[new_pos] = obstacle_directions[obs]
        else:
            new_obstacles.add(obs)
            obstacle_directions[obs] = random_direction()
            new_directions[obs] = obstacle_directions[obs]

    obstacles = new_obstacles
    obstacle_directions = new_directions

def handle_input():
    global running, direction
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            current_dx, current_dy = direction
            if event.key == pygame.K_UP and current_dy == 0:
                direction = (0, -1)
            elif event.key == pygame.K_DOWN and current_dy == 0:
                direction = (0, 1)
            elif event.key == pygame.K_LEFT and current_dx == 0:
                direction = (-1, 0)
            elif event.key == pygame.K_RIGHT and current_dx == 0:
                direction = (1, 0)

def update():
    global running, cable
    update_obstacles()

    head = cable[-1]
    dx, dy = direction
    new_head = (head[0] + dx, head[1] + dy)

    if (
        new_head[0] < 0
        or new_head[0] >= WIDTH
        or new_head[1] < 0
        or new_head[1] >= HEIGHT
        or new_head in cable
        or new_head in obstacles
    ):
        fail_sound.play()
        running = False
        return

    cable.append(new_head)

    if new_head == outlet:
        success_sound.play()
        print("You win!")
        running = False

def draw():
    screen.fill((0, 0, 0))

    for obstacle in obstacles:
        dx, dy = obstacle_directions[obstacle]
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
            obstacle[0] * CELL_SIZE,
            obstacle[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(screen, color, rect)

    for segment in cable:
        rect = pygame.Rect(
            segment[0] * CELL_SIZE,
            segment[1] * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
        pygame.draw.rect(screen, (0, 255, 0), rect)

    outlet_rect = pygame.Rect(
        outlet[0] * CELL_SIZE,
        outlet[1] * CELL_SIZE,
        CELL_SIZE,
        CELL_SIZE,
    )
    pygame.draw.rect(screen, (255, 0, 0), outlet_rect)

    pygame.display.flip()

def run():
    global running
    clock = pygame.time.Clock()
    while running:
        handle_input()
        update()
        draw()
        clock.tick(5)
    pygame.quit()

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Cable Game")

    cable = [(1, HEIGHT - 2)]
    direction = (1, 0)
    obstacles = generate_correlated_obstacles()
    obstacle_directions = {obs: random_direction() for obs in obstacles}
    outlet = generate_outlet()
    running = True

    success_sound = load_sound("success.wav", (SUCCESS_SOUND_FREQ, 0, SOUND_DURATION))
    fail_sound = load_sound("fail.wav", (FAIL_SOUND_FREQ, 0, SOUND_DURATION))

    run()