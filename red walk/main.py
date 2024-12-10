import os
os.system('pip install pygame')
import pygame
import random
import math
import colorsys

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Infinite Maze")
clock = pygame.time.Clock()

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
WALL_COLOR = (150, 0, 0)  # Base wall color

# Load footstep sounds
footstep_sounds = [
    pygame.mixer.Sound('footstep1.wav'),
    pygame.mixer.Sound('footstep2.wav'),
    pygame.mixer.Sound('footstep3.wav'),
    pygame.mixer.Sound('footstep4.wav'),
    pygame.mixer.Sound('footstep5.wav'),
    pygame.mixer.Sound('footstep6.wav')
]

# Define a short pause between footsteps in milliseconds
footstep_pause = 600
last_footstep_time = 0
last_played_footstep = footstep_sounds[0]

# Timer for wall changes
wall_change_interval = 1000  # 1 seconds
last_wall_change_time = 0

# Radius around the player for wall changes (in cells)
wall_change_radius = 10


def shift_hue(r, g, b, shift_amount):
    # Convert RGB to HSV
    r, g, b = [x / 255.0 for x in (r, g, b)]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Shift the hue
    h = (h + shift_amount) % 1.0

    # Convert back to RGB
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    r, g, b = [int(x * 255) for x in (r, g, b)]

    return r, g, b

def play_footstep_sound():
    global last_footstep_time
    global last_played_footstep
    current_time = pygame.time.get_ticks()
    if current_time - last_footstep_time >= footstep_pause:
        sound = random.choice(footstep_sounds)
        while sound == last_played_footstep:
            sound = random.choice(footstep_sounds)
        sound.play()
        last_played_footstep = sound
        last_footstep_time = current_time

# Maze settings
cell_size = 25
maze_width, maze_height = 20, 20
grid = {}

def generate_maze_section(offset_x, offset_y):
    section = [[1 for _ in range(maze_width)] for _ in range(maze_height)]
    stack = [(0, 0)]
    section[0][0] = 0

    while stack:
        current_x, current_y = stack[-1]
        neighbors = []

        if current_x > 1 and section[current_y][current_x - 2] == 1:
            neighbors.append((current_x - 2, current_y))
        if current_x < maze_width - 2 and section[current_y][current_x + 2] == 1:
            neighbors.append((current_x + 2, current_y))
        if current_y > 1 and section[current_y - 2][current_x] == 1:
            neighbors.append((current_x, current_y - 2))
        if current_y < maze_height - 2 and section[current_y + 2][current_x] == 1:
            neighbors.append((current_x, current_y + 2))

        if neighbors:
            next_x, next_y = random.choice(neighbors)
            if next_x == current_x:
                section[(current_y + next_y) // 2][current_x] = 0
            else:
                section[current_y][(current_x + next_x) // 2] = 0
            section[next_y][next_x] = 0
            stack.append((next_x, next_y))
        else:
            stack.pop()

    grid[(offset_x, offset_y)] = section

def get_cell(x, y):
    section_x = (x // maze_width) * maze_width
    section_y = (y // maze_height) * maze_height
    if (section_x, section_y) not in grid:
        generate_maze_section(section_x, section_y)
    return grid[(section_x, section_y)][y % maze_height][x % maze_width]

def set_cell(x, y, value):
    section_x = (x // maze_width) * maze_width
    section_y = (y // maze_height) * maze_height
    if (section_x, section_y) not in grid:
        generate_maze_section(section_x, section_y)
    grid[(section_x, section_y)][y % maze_height][x % maze_width] = value

def find_empty_cell():
    while True:
        start_x, start_y = random.randint(0, maze_width - 1), random.randint(0, maze_height - 1)
        if get_cell(start_x, start_y) == 0:
            return [start_x * cell_size, start_y * cell_size]

def get_cell_size():
    screen_width, screen_height = screen.get_size()
    return min(screen_width // maze_width, screen_height // maze_height)

def handle_input():
    global player_pos, player_angle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        new_x = player_pos[0] + math.cos(player_angle) * player_speed
        new_y = player_pos[1] + math.sin(player_angle) * player_speed
        if get_cell(int(new_x // cell_size), int(new_y // cell_size)) == 0:
            player_pos[0] = new_x
            player_pos[1] = new_y
            play_footstep_sound()
    if keys[pygame.K_s]:
        new_x = player_pos[0] - math.cos(player_angle) * player_speed
        new_y = player_pos[1] - math.sin(player_angle) * player_speed
        if get_cell(int(new_x // cell_size), int(new_y // cell_size)) == 0:
            player_pos[0] = new_x
            player_pos[1] = new_y
            play_footstep_sound()
    if keys[pygame.K_a]:
        player_angle -= player_rotation_speed
    if keys[pygame.K_d]:
        player_angle += player_rotation_speed
        """
    if keys[pygame.K_SPACE]:
        # Determine the direction the player is facing and break the wall in that direction
        break_x = int(player_pos[0] + math.cos(player_angle) * cell_size // 2) // cell_size
        break_y = int(player_pos[1] + math.sin(player_angle) * cell_size // 2) // cell_size
        if get_cell(break_x, break_y) == 1:
            set_cell(break_x, break_y, 0)
            """

def cast_rays():
    screen_width, screen_height = screen.get_size()
    for ray in range(num_rays):
        ray_angle = player_angle - half_fov + field_of_view * ray / num_rays
        sin_a = math.sin(ray_angle)
        cos_a = math.cos(ray_angle)
        for depth in range(max_depth):
            target_x = player_pos[0] + depth * cos_a
            target_y = player_pos[1] + depth * sin_a
            map_x, map_y = int(target_x // cell_size), int(target_y // cell_size)
            if get_cell(map_x, map_y) == 1:
                wall_height = int(screen_height / (depth * 0.05 + 0.0001))
                shade_factor = max(0, min(1, 1 - depth / max_depth))
                color = (int(WALL_COLOR[0] * shade_factor), int(WALL_COLOR[1] * shade_factor), int(WALL_COLOR[2] * shade_factor))
                pygame.draw.rect(screen, color, (ray * (screen_width // num_rays), (screen_height // 2) - wall_height // 2, screen_width // num_rays, wall_height))
                break


def randomly_update_walls():
    current_time = pygame.time.get_ticks()
    global last_wall_change_time
    if current_time - last_wall_change_time >= wall_change_interval:
        player_cell_x = int(player_pos[0] // cell_size)
        player_cell_y = int(player_pos[1] // cell_size)
        # Randomly remove a wall near the player
        while True:
            x = random.randint(player_cell_x - wall_change_radius, player_cell_x + wall_change_radius)
            y = random.randint(player_cell_y - wall_change_radius, player_cell_y + wall_change_radius)
            if get_cell(x, y) == 1:  # Now corners can also be changed
                set_cell(x, y, 0)
                break
        # Randomly add a wall near the player
        last_wall_change_time = current_time

# Player settings
player_pos = find_empty_cell()
player_angle = 0
player_speed = 0.5  # Halved player speed
player_rotation_speed = 0.1
field_of_view = (math.pi / 3) * 2
half_fov = field_of_view / 2
num_rays = 360
max_depth = 300
r,g,b = 255,0,0
# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

    shift_amount = 0.2 / 255
    r, g, b = shift_hue(r, g, b, shift_amount)
    WALL_COLOR = r, g, b

    handle_input()
    screen.fill(BLACK)  # Clear screen

    randomly_update_walls()
    cast_rays()

    pygame.display.flip()  # Update display
    clock.tick(60)  # Maintain 60 FPS

pygame.quit()
