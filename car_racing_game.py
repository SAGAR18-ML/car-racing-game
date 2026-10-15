import random
import sys
import math
from array import array
import pygame

# Window and road settings from the project brief
WIDTH = 400
HEIGHT = 600
ROAD_LEFT = 50
ROAD_RIGHT = 350
CAR_WIDTH = 40
CAR_HEIGHT = 80
PLAYER_START_X = 180
PLAYER_Y = 500
PLAYER_STEP = 10
FPS = 60

# Brighter natural colors keep the road and cars easy to see.
GRASS = (91, 143, 101)
ROAD = (48, 55, 64)
ROAD_EDGE = (238, 222, 185)
WHITE = (247, 245, 237)
INK = (35, 39, 43)
MUTED = (113, 119, 121)
PLAYER_COLOR = (61, 132, 184)
OBSTACLE_COLOR = (207, 96, 72)
GLASS = (190, 222, 225)


def draw_car(surface, x, y, color):
    """Draw a simple car using shapes, so no image files are needed."""
    body = pygame.Rect(x, y, CAR_WIDTH, CAR_HEIGHT)

    # Wheels behind the body
    pygame.draw.rect(surface, INK, (x - 3, y + 13, 6, 18), border_radius=3)
    pygame.draw.rect(surface, INK, (x + CAR_WIDTH - 3, y + 13, 6, 18), border_radius=3)
    pygame.draw.rect(surface, INK, (x - 3, y + 51, 6, 18), border_radius=3)
    pygame.draw.rect(surface, INK, (x + CAR_WIDTH - 3, y + 51, 6, 18), border_radius=3)

    # Main body and windows
    pygame.draw.rect(surface, color, body, border_radius=10)
    pygame.draw.rect(surface, GLASS, (x + 7, y + 14, 26, 19), border_radius=5)
    pygame.draw.rect(surface, GLASS, (x + 7, y + 47, 26, 17), border_radius=5)
    pygame.draw.line(surface, WHITE, (x + 7, y + 40), (x + 33, y + 40), 2)

    # Headlights and tail lights
    pygame.draw.rect(surface, (248, 226, 160), (x + 5, y + 3, 8, 4), border_radius=2)
    pygame.draw.rect(surface, (248, 226, 160), (x + 27, y + 3, 8, 4), border_radius=2)
    pygame.draw.rect(surface, (133, 52, 47), (x + 5, y + 73, 8, 4), border_radius=2)
    pygame.draw.rect(surface, (133, 52, 47), (x + 27, y + 73, 8, 4), border_radius=2)


def new_obstacle():
    """Create an obstacle at a lane position above the screen."""
    x = random.randint(ROAD_LEFT, ROAD_RIGHT - CAR_WIDTH)
    return {"x": x, "y": -CAR_HEIGHT, "counted": False}


def make_tone(frequency, duration, volume=0.12):
    """Make a short sound in memory, so the game needs no audio files."""
    sample_rate = 22050
    sample_count = int(sample_rate * duration)
    samples = array("h")

    for sample_number in range(sample_count):
        time = sample_number / sample_rate
        fade = 1 - sample_number / sample_count
        value = math.sin(2 * math.pi * frequency * time) * volume * fade
        samples.append(int(value * 32767))

    return pygame.mixer.Sound(buffer=samples.tobytes())


def draw_scene(screen, player_x, obstacles, score, stripe_offset, animation_time, font, small_font):
    """Draw the roadside, road, moving lane markers, cars, and score panel."""
    screen.fill(GRASS)

    # Road and its pale edge lines
    pygame.draw.rect(screen, ROAD, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
    pygame.draw.rect(screen, ROAD_EDGE, (ROAD_LEFT, 0, 4, HEIGHT))
    pygame.draw.rect(screen, ROAD_EDGE, (ROAD_RIGHT - 4, 0, 4, HEIGHT))

    # Dashed center line scrolls down to make the road feel like it is moving
    marker_y = -80 + stripe_offset
    while marker_y < HEIGHT:
        pygame.draw.rect(screen, (207, 204, 190), (198, marker_y, 4, 42), border_radius=2)
        marker_y += 90

    # Small roadside posts add depth without distracting from the cars
    for post_y in range(20, HEIGHT, 100):
        y = (post_y + stripe_offset) % HEIGHT
        pygame.draw.rect(screen, ROAD_EDGE, (35, y, 7, 22), border_radius=3)
        pygame.draw.rect(screen, ROAD_EDGE, (358, y, 7, 22), border_radius=3)

    # Rounded bushes scroll past on the grass beside the road.
    for bush_y in range(-30, HEIGHT + 40, 130):
        y = (bush_y + stripe_offset * 1.4) % (HEIGHT + 30) - 15
        pygame.draw.ellipse(screen, (65, 101, 71), (12, y, 27, 15))
        pygame.draw.ellipse(screen, (65, 101, 71), (361, y + 52, 27, 15))

    for obstacle in obstacles:
        draw_car(screen, obstacle["x"], obstacle["y"], OBSTACLE_COLOR)
    # A tiny up-and-down bounce gives the player's car some life.
    player_bounce = round(math.sin(animation_time * 8) * 2)
    draw_car(screen, player_x, PLAYER_Y + player_bounce, PLAYER_COLOR)

    # Compact score card at the top of the road
    pygame.draw.rect(screen, WHITE, (67, 16, 266, 52), border_radius=10)
    pygame.draw.rect(screen, (219, 225, 222), (67, 16, 266, 52), 2, border_radius=10)
    label = small_font.render("SCORE", True, MUTED)
    value = font.render(str(score), True, INK)
    screen.blit(label, (84, 25))
    screen.blit(value, (84, 39))
    hint = small_font.render("←  →  STEER", True, MUTED)
    screen.blit(hint, (220, 35))


def draw_game_over(screen, score, font, small_font):
    """Show a readable game-over panel over the final scene."""
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((24, 29, 32, 155))
    screen.blit(overlay, (0, 0))

    panel = pygame.Rect(38, 205, 324, 190)
    pygame.draw.rect(screen, WHITE, panel, border_radius=16)
    pygame.draw.rect(screen, (219, 225, 222), panel, 2, border_radius=16)

    title = font.render("RACE OVER", True, INK)
    final_score = small_font.render(f"Final score: {score}", True, MUTED)
    restart = small_font.render("Press R to race again", True, PLAYER_COLOR)
    quit_hint = small_font.render("Press Esc to quit", True, MUTED)

    screen.blit(title, title.get_rect(center=(WIDTH // 2, 255)))
    screen.blit(final_score, final_score.get_rect(center=(WIDTH // 2, 300)))
    screen.blit(restart, restart.get_rect(center=(WIDTH // 2, 344)))
    screen.blit(quit_hint, quit_hint.get_rect(center=(WIDTH // 2, 370)))


def draw_pause_message(screen, font, small_font):
    """Show a simple pause message over the road."""
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((24, 29, 32, 125))
    screen.blit(shade, (0, 0))
    title = font.render("PAUSED", True, WHITE)
    hint = small_font.render("Press P to continue", True, WHITE)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 270)))
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 310)))


def run_game():
    # Configure audio before starting Pygame. The game still works without audio.
    pygame.mixer.pre_init(22050, -16, 1, 512)
    pygame.init()
    sounds = {"steer": None, "score": None, "crash": None}
    try:
        sounds["steer"] = make_tone(520, 0.06, 0.08)
        sounds["score"] = make_tone(760, 0.12, 0.12)
        sounds["crash"] = make_tone(110, 0.35, 0.24)
    except pygame.error:
        # Some computers have no audio output device available.
        pass

    pygame.display.set_caption("Road Run — Car Racing Game")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 34)
    small_font = pygame.font.Font(None, 22)

    player_x = PLAYER_START_X
    obstacles = [new_obstacle()]
    score = 0
    road_speed = 4
    stripe_offset = 0
    spawn_timer = 0
    game_over = False
    paused = False
    running = True

    while running:
        # Read keyboard and window events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game_over and event.key == pygame.K_p:
                    paused = not paused
                elif not game_over and not paused and event.key == pygame.K_LEFT:
                    player_x = max(ROAD_LEFT, player_x - PLAYER_STEP)
                    if sounds["steer"]:
                        sounds["steer"].play()
                elif not game_over and not paused and event.key == pygame.K_RIGHT:
                    player_x = min(ROAD_RIGHT - CAR_WIDTH, player_x + PLAYER_STEP)
                    if sounds["steer"]:
                        sounds["steer"].play()
                elif game_over and event.key == pygame.K_r:
                    # Reset all game values for a fresh run
                    player_x = PLAYER_START_X
                    obstacles = [new_obstacle()]
                    score = 0
                    road_speed = 4
                    stripe_offset = 0
                    spawn_timer = 0
                    game_over = False

        if not game_over and not paused:
            # Steering moves 10 pixels for each KEYDOWN event.
            stripe_offset = (stripe_offset + road_speed) % 90

            # Add a new obstacle every few seconds
            spawn_timer += 1
            if spawn_timer >= 90:
                obstacles.append(new_obstacle())
                spawn_timer = 0

            player_rect = pygame.Rect(player_x, PLAYER_Y, CAR_WIDTH, CAR_HEIGHT)
            for obstacle in obstacles:
                obstacle["y"] += road_speed
                obstacle_rect = pygame.Rect(obstacle["x"], obstacle["y"], CAR_WIDTH, CAR_HEIGHT)

                if player_rect.colliderect(obstacle_rect):
                    game_over = True
                    if sounds["crash"]:
                        sounds["crash"].play()

                # Score each obstacle once, after its bottom passes the screen edge
                if not obstacle["counted"] and obstacle["y"] >= HEIGHT:
                    obstacle["counted"] = True
                    score += 1
                    if sounds["score"]:
                        sounds["score"].play()
                    # A gentle speed increase keeps later runs interesting
                    road_speed = min(road_speed + 0.2, 8)

            # Remove cars after they are fully off-screen
            obstacles = [car for car in obstacles if car["y"] < HEIGHT]

        animation_time = pygame.time.get_ticks() / 1000
        draw_scene(screen, player_x, obstacles, score, stripe_offset, animation_time, font, small_font)
        if game_over:
            draw_game_over(screen, score, font, small_font)
        elif paused:
            draw_pause_message(screen, font, small_font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    run_game()

