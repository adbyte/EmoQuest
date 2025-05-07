import os
import pygame
import random
import time
import json

# Game Constants
WIDTH, HEIGHT = 1000, 800
HOLE_SIZE = 100
MOLE_SIZE = 80
GRID_SIZE = 4
TIME_LIMIT = 10  # seconds
logs = []

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (1, 254, 64)
BLUE = (19, 55, 139)
RED = (255, 0, 0)

class RealmOfPortals:
    
    def __init__(self, screen):
        self.screen = screen

        self.mole_image = self.load_mole_image("Game3/Assets/mole.png")
        self.mole1_image = self.load_mole_image("Game3/Assets/rat.png")
        self.background = self.load_image("Game3/Assets/garden.jpg", (WIDTH, HEIGHT))
        self.use_image = self.mole_image is not None and self.mole1_image is not None
        self.holes = self.generate_holes()

    def load_image(self, path, size=None):
        """Load and scale an image."""
        try:
            image = pygame.image.load(path)
            if size:
                image = pygame.transform.scale(image, size)
            return image
        except:
            print(f"Image '{path}' not found.")
            return None

    def generate_holes(self):
        """Generate hole positions."""
        holes = []
        gap = (WIDTH - (GRID_SIZE * HOLE_SIZE)) // (GRID_SIZE + 5)
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = gap + col * (HOLE_SIZE + gap) + 90
                y = gap + row * (HOLE_SIZE + gap) + 70  # Adjusted for score/time display
                holes.append(pygame.Rect(x, y, HOLE_SIZE, HOLE_SIZE))
        return holes

    def load_mole_image(self, image_path):
        """Load and scale the mole image."""
        try:
            image = pygame.image.load(image_path)
            return pygame.transform.scale(image, (MOLE_SIZE, MOLE_SIZE))
        except:
            print(f"{image_path} not found, using fallback circle")
            return None

    def show_intro_image(self):
        """Show the surprise intro image with a fade-in effect."""
        try:
            # Load and scale the intro image
            intro_image = pygame.image.load(r"Game3/Assets/surprisebg.png").convert_alpha()
            intro_scaled = pygame.transform.scale(intro_image, (WIDTH, HEIGHT))
            
            # Create a surface for fade effect
            fade_surface = pygame.Surface((WIDTH, HEIGHT))
            fade_surface.fill((0, 0, 0))
            
            # Fade in effect
            for alpha in range(0, 255, 5):
                self.screen.fill((0, 0, 0))  # Clear the screen with black
                intro_scaled.set_alpha(alpha)
                self.screen.blit(intro_scaled, (0, 0))
                pygame.display.flip()
                pygame.time.delay(30)
            
            # Show the image fully
            self.screen.blit(intro_scaled, (0, 0))
            pygame.display.flip()
            
            # Wait for space key press
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                        waiting = False
            
        except Exception as e:
            print(f"Error loading intro image: {e}")
            # If image fails to load, just continue after a delay
            pygame.time.delay(1000)

    def main_menu(self):
        """Display the main menu (now not needed, intro image takes over)."""
        pass  # The main menu is skipped after the intro image.

    def game(self):
        """Run the main game loop."""
        count = 0
        score = 0
        active_moles = []
        game_over = False
        start_time = time.time()
        mole_timer = 0
        rat_timer = 0
        mole_frequency = 1.0  # Initial seconds between mole appearances
        rat_frequency = 1.5  # Initial seconds between rat appearances
        max_active_moles = 1
        max_active_moles1 = 2  # Multiple moles appear at once

        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(60) / 1000  # Delta time in seconds
            self.screen.blit(self.background, (0, 0))
            
            # Time Handling
            elapsed_time = time.time() - start_time
            remaining_time = max(0, TIME_LIMIT - int(elapsed_time))
            if remaining_time == 0:
                game_over = True
                running = False
            
            # Spawn new moles and rats randomly
            mole_timer += dt
            rat_timer += dt
            
            if mole_timer > mole_frequency and len(active_moles) < max_active_moles:
                mole_timer = 0
                available_holes = [hole for hole in self.holes if hole not in [m['rect'] for m in active_moles]]
                if available_holes:
                    new_mole_hole = random.choice(available_holes)
                    active_moles.append({
                        'rect': new_mole_hole,
                        'time_left': random.uniform(0.5, 2),
                        'spawn_time': time.time(),
                        'clicked': False,
                        'click_time': None
                    })
            
            if rat_timer > rat_frequency and len(active_moles) < max_active_moles1:
                rat_timer = 0
                available_holes = [hole for hole in self.holes if hole not in [m['rect'] for m in active_moles]]
                if available_holes:
                    new_rat_hole = random.choice(available_holes)
                    active_moles.append({
                        'rect': new_rat_hole,
                        'time_left': random.uniform(0.5, 2),
                        'spawn_time': time.time(),
                        'clicked': False,
                        'click_time': None,
                        'is_rat': True
                    })
            
            # Update mole and rat timers
            for mole in active_moles[:]:
                mole['time_left'] -= dt
                if mole['time_left'] <= 0:
                    # Log missed mole or rat
                    logs.append({
                        "type": "rat" if mole.get('is_rat') else "mole",
                        "spawn_time": mole['spawn_time'],
                        "click_time": None,
                        "reaction_time": None,
                        "clicked": False,
                        "position": [mole['rect'].x, mole['rect'].y]
                    })
                    active_moles.remove(mole)

            # Draw Moles and Rats
            for mole in active_moles:
                if mole.get('is_rat'):
                    if self.use_image:
                        self.screen.blit(self.mole1_image, (mole['rect'].x + 10, mole['rect'].y + 10))
                    else:
                        pygame.draw.circle(self.screen, GREEN, (mole['rect'].x + HOLE_SIZE // 2, mole['rect'].y + HOLE_SIZE // 2), MOLE_SIZE // 2)
                else:
                    if self.use_image:
                        self.screen.blit(self.mole_image, (mole['rect'].x + 10, mole['rect'].y + 10))
                    else:
                        pygame.draw.circle(self.screen, RED, (mole['rect'].x + HOLE_SIZE // 2, mole['rect'].y + HOLE_SIZE // 2), MOLE_SIZE // 2)
            
            # Display Score and Timer
            font = pygame.font.Font(None, 36)
            self.screen.blit(font.render(f"Score: {score}", True, WHITE), (20, 10))
            self.screen.blit(font.render(f"Time: {remaining_time}s", True, WHITE), (WIDTH - 150, 10))
            
            # Event Handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for mole in active_moles[:]:
                        current_time = time.time()
                        if mole['rect'].collidepoint(event.pos):  # Clicked on mole
                            score += 1
                            mole['clicked'] = True
                            mole['click_time'] = current_time
                            logs.append({
                                "type": "mole" if not mole.get('is_rat') else "rat",
                                "spawn_time": mole['spawn_time'],
                                "click_time": current_time,
                                "reaction_time": current_time - mole['spawn_time'],
                                "clicked": True,
                                "position": list(event.pos)
                            })
                            active_moles.remove(mole)
                            break

            pygame.display.flip()

        self.end_screen(score, count)
        return True  # Return True when the game is over

    def end_screen(self, score, count):
        """Display the end screen."""
        running = True
        font = pygame.font.Font(None, 48)
        while running:
            self.screen.fill(BLACK)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            final_count_text = font.render(f"Final count: {count}", True, WHITE)
            restart_text = font.render("Press R to Restart or Q to Quit", True, WHITE)
            self.screen.blit(final_count_text, (WIDTH // 2 - final_count_text.get_width() // 2, HEIGHT // 4))
            self.screen.blit(final_score_text, (WIDTH // 2 - final_score_text.get_width() // 2, HEIGHT // 3))
            self.screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.game()
                    if event.key == pygame.K_q:
                        with open("reaction_logs.json", "w") as f:
                            json.dump(logs, f, indent=4)

                        return True
                    
    def run(self):
        """Main method to run the game."""
          # Show the intro image before the game starts
        game_over = self.game()  # Start the game after the intro image
        return game_over
