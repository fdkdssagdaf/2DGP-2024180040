import random
import pygame

# --------------------------------------------------
# Pico-2D style bird animation
# --------------------------------------------------

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bird Flight Animation")

clock = pygame.time.Clock()

# sprite sheet
bird_sheet = pygame.image.load("bird_animation.png").convert_alpha()
frame_width = 64
frame_height = 64
frame_count = 4

frames = []
for i in range(frame_count):
    frame = bird_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
    frames.append(frame)

birds = []
for i in range(10):
    birds.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(60, HEIGHT - 60),
        "vx": random.uniform(60, 140),
        "direction": random.choice([-1, 1]),
        "frame_index": random.randint(0, frame_count - 1),
        "animation_timer": random.random(),
        "flap_interval": random.uniform(0.08, 0.18),
    })

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for bird in birds:
        bird["x"] += bird["vx"] * bird["direction"] * dt

        if bird["x"] < -frame_width:
            bird["x"] = WIDTH
            bird["direction"] = 1
        elif bird["x"] > WIDTH:
            bird["x"] = -frame_width
            bird["direction"] = -1

        bird["y"] += random.uniform(-5, 5)
        if bird["y"] < 20:
            bird["y"] = 20
        elif bird["y"] > HEIGHT - 40:
            bird["y"] = HEIGHT - 40

        bird["animation_timer"] += dt
        if bird["animation_timer"] >= bird["flap_interval"]:
            bird["animation_timer"] = 0
            bird["frame_index"] = (bird["frame_index"] + 1) % frame_count

        image = frames[bird["frame_index"]]
        if bird["direction"] == -1:
            image = pygame.transform.flip(image, True, False)

        screen.blit(image, (bird["x"], bird["y"]))

    pygame.display.flip()

pygame.quit()
