import pygame
import random
import time
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Realm of Portals 🌌")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
TRANSPARENT = (0, 0, 0, 128)  # Semi-transparent black

# Load assets (replace with your own high-quality assets)
BACKGROUND_IMG = pygame.transform.scale(pygame.image.load("mystery door/magical_forest.jpg"), (WIDTH, HEIGHT))  # Mystical background
PORTAL_IMG = pygame.transform.scale(pygame.image.load("mystery door/portal.png"), (100, 100))  # Glowing portal texture
TRAP_IMG = pygame.transform.scale(pygame.image.load("mystery door/trap.png"), (100, 100))  # Trap texture
FONT = pygame.font.Font(None, 36)
TITLE_FONT = pygame.font.Font(None, 72)
ICON_FONT = pygame.font.Font(None, 24)

# Load sounds
pygame.mixer.init()
PORTAL_OPEN_SOUND = pygame.mixer.Sound("mystery door/door_open.mp3")
PORTAL_CLOSE_SOUND = pygame.mixer.Sound("mystery door/door_close.mp3")
TRAP_SOUND = pygame.mixer.Sound("mystery door/trap_music.mp3")
BACKGROUND_MUSIC = pygame.mixer.Sound("mystery door/mystery_theme.mp3")

# Portal properties
PORTAL_WIDTH, PORTAL_HEIGHT = 100, 100
NUM_PORTALS = 5
PORTAL_OPEN_TIME = 0.5  # Time in seconds the portal stays open
PORTAL_MOVE_SPEED = 2  # Speed at which portals move

# Game variables
score = 0
reaction_times = []
game_active = False
start_time = 0
show_rules = True

# Portal class
class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PORTAL_WIDTH
        self.height = PORTAL_HEIGHT
        self.is_open = False
        self.is_trap = False
        self.angle = 0  # For rotation effect
        self.speed = PORTAL_MOVE_SPEED

    def draw(self):
        if self.is_open:
            portal_img = TRAP_IMG if self.is_trap else PORTAL_IMG
            rotated_portal = pygame.transform.rotate(portal_img, self.angle)
            screen.blit(rotated_portal, (self.x, self.y))

    def update(self):
        # Rotate and move portals for added complexity
        self.angle = (self.angle + self.speed) % 360
        self.x += random.choice([-1, 1]) * self.speed
        self.y += random.choice([-1, 1]) * self.speed

# Create portals
portals = [Portal(random.randint(0, WIDTH - PORTAL_WIDTH), random.randint(0, HEIGHT - PORTAL_HEIGHT)) for _ in range(NUM_PORTALS)]

# Function to open a random portal
def open_random_portal():
    global start_time
    portal = random.choice(portals)
    portal.is_open = True
    portal.is_trap = random.choice([True, False])  # 50% chance of being a trap
    PORTAL_OPEN_SOUND.play()
    start_time = time.time()

# Function to close all portals
def close_all_portals():
    for portal in portals:
        portal.is_open = False
    PORTAL_CLOSE_SOUND.play()

# Function to draw gradient background
def draw_gradient_background(surface, color1, color2):
    for y in range(HEIGHT):
        r = color1[0] + (color2[0] - color1[0]) * y // HEIGHT
        g = color1[1] + (color2[1] - color1[1]) * y // HEIGHT
        b = color1[2] + (color2[2] - color1[2]) * y // HEIGHT
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

# Function to display the end game pop-up
def show_end_game_popup(avg_reaction_time, startled_percentage):
    popup_width, popup_height = 600, 400
    popup_surface = pygame.Surface((popup_width, popup_height), pygame.SRCALPHA)
    popup_surface.fill((0, 0, 0, 200))  # Semi-transparent black

    # Draw gradient background
    draw_gradient_background(popup_surface, (50, 50, 50), (20, 20, 20))

    # Title
    title_text = TITLE_FONT.render("Congratulations!", True, GOLD)
    popup_surface.blit(title_text, (popup_width // 2 - title_text.get_width() // 2, 50))

    # Reaction time
    reaction_text = FONT.render(f"Avg Reaction Time: {avg_reaction_time:.2f}s", True, WHITE)
    popup_surface.blit(reaction_text, (popup_width // 2 - reaction_text.get_width() // 2, 150))

    # Startled responsiveness percentage
    startled_text = FONT.render(f"Startled Responsiveness: {startled_percentage:.2f}%", True, WHITE)
    popup_surface.blit(startled_text, (popup_width // 2 - startled_text.get_width() // 2, 200))

    # Message
    message_text = ICON_FONT.render("You have a high tendency for startled behavior!", True, WHITE)
    popup_surface.blit(message_text, (popup_width // 2 - message_text.get_width() // 2, 300))

    # Display popup
    screen.blit(popup_surface, (WIDTH // 2 - popup_width // 2, HEIGHT // 2 - popup_height // 2))

# Function to display the rules screen
def show_rules_screen():
    rules_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    rules_surface.fill((0, 0, 0, 200))  # Semi-transparent black

    # Title
    title_text = TITLE_FONT.render("Realm of Portals", True, GOLD)
    rules_surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    # Rules
    rules_text = [
        "Welcome to the Realm of Portals!",
        "Rules:",
        "1. Click on the glowing portals (Artifacts) to gain points.",
        "2. Avoid the red portals (Traps) as they deduct points.",
        "3. Be quick! Portals disappear fast.",
        "Press SPACE to start the game."
    ]
    for i, line in enumerate(rules_text):
        text = FONT.render(line, True, WHITE)
        rules_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, 150 + i * 50))

    # Display artifact and trap images below the text
    artifact_text = ICON_FONT.render("Artifact", True, WHITE)
    trap_text = ICON_FONT.render("Trap", True, WHITE)

    # Position images and labels
    image_y = 450  # Position below the rules text
    artifact_x = WIDTH // 2 - 150  # Left side
    trap_x = WIDTH // 2 + 50  # Right side

    # Draw artifact image and label
    rules_surface.blit(PORTAL_IMG, (artifact_x, image_y))
    rules_surface.blit(artifact_text, (artifact_x + PORTAL_WIDTH // 2 - artifact_text.get_width() // 2, image_y + PORTAL_HEIGHT + 10))

    # Draw trap image and label
    rules_surface.blit(TRAP_IMG, (trap_x, image_y))
    rules_surface.blit(trap_text, (trap_x + PORTAL_WIDTH // 2 - trap_text.get_width() // 2, image_y + PORTAL_HEIGHT + 10))

    # Display on screen
    screen.blit(rules_surface, (0, 0))

# Main game loop
clock = pygame.time.Clock()
BACKGROUND_MUSIC.play(-1)  # Loop background music

running = True
while running:
    screen.blit(BACKGROUND_IMG, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if show_rules:
                    show_rules = False
                    game_active = True
                elif not game_active:
                    game_active = True  # Restart the game
                    score = 0  # Reset score
                    reaction_times = []  # Reset reaction times
            if event.key == pygame.K_ESCAPE:  # Exit the game when ESC is pressed
                running = False
        if event.type == pygame.MOUSEBUTTONDOWN and game_active:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for portal in portals:
                if portal.is_open and portal.x <= mouse_x <= portal.x + portal.width and portal.y <= mouse_y <= portal.y + portal.height:
                    if portal.is_trap:
                        TRAP_SOUND.play()
                        score -= 1
                    else:
                        reaction_time = time.time() - start_time
                        reaction_times.append(reaction_time)
                        score += 1
                    close_all_portals()

    if show_rules:
        show_rules_screen()
    elif game_active:
        # Update portals
        for portal in portals:
            portal.update()
            portal.draw()

        # Open a random portal periodically
        if random.random() < 0.01:  # Adjust probability for difficulty
            open_random_portal()

        # Display score
        score_text = FONT.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

    # End game and display results
    if len(reaction_times) >= 5:  # End after 5 attempts
        game_active = False
        avg_reaction_time = sum(reaction_times) / len(reaction_times)
        startled_percentage = (sum(1 for rt in reaction_times if rt < 0.5) / len(reaction_times)) * 100
        show_end_game_popup(avg_reaction_time, startled_percentage)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()