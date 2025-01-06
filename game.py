import pygame
import sys
import random
import time
import json
import requests 
pygame.init()
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height), pygame.RESIZABLE)
pygame.display.set_caption("Pratyush Snake Game")
black = (0, 0, 0)
green = (0, 255, 0)
red = (255, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
yellow = (255, 255, 0)
font = pygame.font.SysFont(None, 55)
score_font = pygame.font.SysFont(None, 35)
background_image = pygame.image.load("DSC05874.JPG")
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
food_sound = pygame.mixer.Sound("snake.mp3")
clock = pygame.time.Clock()
developer_name = "Pratyush Joshi"
leaderboard_file = "leaderboard.json"
def load_leaderboard():
    try:
        with open(leaderboard_file, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
def save_leaderboard(leaderboard):
    with open(leaderboard_file, 'w') as f:
        json.dump(leaderboard, f, indent=4)
leaderboard = load_leaderboard()
def text_screen(text, font, color, x, y):
    screen_text = font.render(text, True, color)
    screen.blit(screen_text, [x, y])
def start_menu():
    while True:
        screen.fill(black)
        text_screen("Welcome to the Snake Game", font, green, screen_width // 6, screen_height // 4)
        text_screen(f"Developed by: {developer_name}", score_font, blue, screen_width // 4, screen_height // 3)
        text_screen("Press S to Start", score_font, white, screen_width // 3, screen_height // 2.5)
        text_screen("Press Q to Quit", score_font, white, screen_width // 3, screen_height // 2.2)
        text_screen("Press L for Leaderboard", score_font, yellow, screen_width // 3, screen_height // 2)
        text_screen("Press F for Fullscreen", score_font, yellow, screen_width // 3, screen_height // 1.8)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return level_selection_menu()
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_l:
                    leaderboard_screen()
                if event.key == pygame.K_f:
                    pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
def leaderboard_screen():
    screen.fill(black)
    text_screen("Leaderboard", font, green, screen_width // 3, screen_height // 4)
    if len(leaderboard) == 0:
        text_screen("No entries yet.", score_font, white, screen_width // 3, screen_height // 2)
    else:
        y_position = screen_height // 4 + 50
        for i, entry in enumerate(leaderboard):
            text_screen(f"{i+1}. {entry['name']} - Score: {entry['score']} - Time: {entry['time']:.2f}s", score_font, white, screen_width // 6, y_position)
            y_position += 40
    text_screen("Press Esc to go back", score_font, red, screen_width // 4, screen_height // 1.5)
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
def level_selection_menu():
    selected_level = 1
    while True:
        screen.fill(black)
        text_screen("Select Starting Level", font, green, screen_width // 4, screen_height // 4)
        text_screen(f"Level: {selected_level}", font, yellow, screen_width // 3, screen_height // 2)
        text_screen("Use UP/DOWN to change level", score_font, white, screen_width // 4, screen_height // 1.8)
        text_screen("Press Enter to Start", score_font, green, screen_width // 4, screen_height // 1.6)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_level += 1
                if event.key == pygame.K_DOWN and selected_level > 1:
                    selected_level -= 1
                if event.key == pygame.K_RETURN:
                    return selected_level
def generate_obstacles(level):
    snake_size = 20
    obstacle_count = level * 2 + 3  # Number of obstacles increases with level
    new_obstacles = []
    for _ in range(obstacle_count):
        obs_x = random.randint(0, (screen_width - snake_size) // snake_size) * snake_size
        obs_y = random.randint(0, (screen_height - snake_size) // snake_size) * snake_size
        new_obstacles.append([obs_x, obs_y])  # Static position only
    return new_obstacles
def game_over_menu(score, elapsed_time):
    player_name = "Player"
    while True:
        screen.fill(black)
        text_screen("Game Over", font, red, screen_width // 3, screen_height // 4)
        text_screen("Press R to Restart", score_font, white, screen_width // 3, screen_height // 2.5)
        text_screen("Press Q to Quit", score_font, white, screen_width // 3, screen_height // 2.2)
        text_screen(f"Name: {player_name}", score_font, yellow, screen_width // 3, screen_height // 1.8)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    starting_level = level_selection_menu()
                    game_loop(starting_level)
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
def submit_score(name, score, elapsed_time):
    url = 'http://127.0.0.1:5000/leaderboard'
    data = {"name": name, "score": score, "time": elapsed_time}
    try:
        response = requests.post(url, json=data)
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error submitting score: {e}")
def game_loop(starting_level):
    snake_size = 20
    snake_x = screen_width // 2
    snake_y = screen_height // 2
    snake_speed = 20
    snake_body = [(snake_x, snake_y)]
    direction = 'RIGHT'
    change_to = direction
    food_size = 20
    food_x = random.randint(0, (screen_width - food_size) // food_size) * food_size
    food_y = random.randint(0, (screen_height - food_size) // food_size) * food_size
    score = 0
    level = starting_level
    obstacles = generate_obstacles(level)
    start_time = time.time()
    running = True
    while running:
        elapsed_time = time.time() - start_time
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and direction != 'RIGHT':
            change_to = 'LEFT'
        if keys[pygame.K_RIGHT] and direction != 'LEFT':
            change_to = 'RIGHT'
        if keys[pygame.K_UP] and direction != 'DOWN':
            change_to = 'UP'
        if keys[pygame.K_DOWN] and direction != 'UP':
            change_to = 'DOWN'
        direction = change_to
        if direction == 'LEFT':
            snake_x -= snake_speed
        if direction == 'RIGHT':
            snake_x += snake_speed
        if direction == 'UP':
            snake_y -= snake_speed
        if direction == 'DOWN':
            snake_y += snake_speed
        if snake_x < 0 or snake_x >= screen_width or snake_y < 0 or snake_y >= screen_height:
            game_over_menu(score, elapsed_time)
        for obs in obstacles:
            if snake_x == obs[0] and snake_y == obs[1]:
                game_over_menu(score, elapsed_time)
        snake_body.append((snake_x, snake_y))
        if len(snake_body) > score + 1:
            snake_body.pop(0)
        if snake_x == food_x and snake_y == food_y:
            food_x = random.randint(0, (screen_width - food_size) // food_size) * food_size
            food_y = random.randint(0, (screen_height - food_size) // food_size) * food_size
            score += 1
            food_sound.play()
            if score % 5 == 0:
                level += 1
                obstacles = generate_obstacles(level)
        if snake_body[-1] in snake_body[:-1]:
            game_over_menu(score, elapsed_time)
        screen.blit(background_image, (0, 0))
        for segment in snake_body:
            pygame.draw.circle(screen, green, (segment[0] + snake_size // 2, segment[1] + snake_size // 2), snake_size // 2)
        pygame.draw.rect(screen, red, (food_x, food_y, food_size, food_size))
        for obs in obstacles:
            pygame.draw.rect(screen, blue, (obs[0], obs[1], snake_size, snake_size))
        text_screen(f"Score: {score} | Level: {level}", score_font, white, 5, 5)
        text_screen(f"Time: {elapsed_time:.2f} sec", score_font, yellow, 5, 35)
        pygame.display.flip()
        clock.tick(15)
starting_level = start_menu()
game_loop(starting_level)
