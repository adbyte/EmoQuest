import pygame
import sys
import math
import random

class RealmOfFear:
    def __init__(self, screen):
        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_width(), screen.get_height()
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.CYAN = (0, 255, 255)

        # Load images and adjust sizes
        self.player_img = pygame.image.load(r"Game1\Assets\spaceship.png").convert_alpha()
        self.player_img = pygame.transform.scale(self.player_img, (80, 80))  # Fixed size for player

        self.enemy_img = pygame.image.load(r"Game1\Assets\enemy.png").convert_alpha()
        self.enemy_img = pygame.transform.scale(self.enemy_img, (180, 120))  # Fixed size for enemy

        self.trap_img = pygame.image.load(r"Game1\Assets\bomb.png").convert_alpha()
        self.trap_img = pygame.transform.scale(self.trap_img, (60, 80))  # Fixed size for traps

        self.power_up_imgs = {
            'speed_boost': pygame.transform.scale(pygame.image.load(r"Game1\Assets\speed.png").convert_alpha(), (40, 40)),
            'shield': pygame.transform.scale(pygame.image.load(r"Game1\Assets\shield.png").convert_alpha(), (40, 40)),
            'trap_disabler': pygame.transform.scale(pygame.image.load(r"Game1\Assets\key.png").convert_alpha(), (40, 40)),
            'enemy_freeze': pygame.transform.scale(pygame.image.load(r"Game1\Assets\freeze.png").convert_alpha(), (40, 40))
        }

        self.background_img = pygame.image.load(r"Game1\Assets\bg2.jpg").convert()
        self.background_img = pygame.transform.scale(self.background_img, (self.WIDTH, self.HEIGHT))  # Scale background to screen size

        # Load sounds
        pygame.mixer.init()
        self.background_music = pygame.mixer.Sound(r"Game1\Sounds\bg_music.ogg")
        self.power_up_sound = pygame.mixer.Sound(r"Game1\Sounds\powerup.wav")
        self.trap_collision_sound = pygame.mixer.Sound(r"Game1\Sounds\trap_sound.wav")
        self.game_over_sound = pygame.mixer.Sound(r"Game1\Sounds\gameover.wav")

        # Cube properties
        self.cube_size = 40
        self.player_x = random.randint(0, self.WIDTH - self.cube_size)
        self.player_y = random.randint(0, self.HEIGHT - self.cube_size)
        self.enemy_x = random.randint(0, self.WIDTH - self.cube_size)
        self.enemy_y = random.randint(0, self.HEIGHT - self.cube_size)
        self.enemy_speed = 3

        # Shadowy Traps properties
        self.num_traps = 5
        self.traps = []
        for _ in range(self.num_traps):
            self.traps.append([random.randint(0, self.WIDTH - self.cube_size), random.randint(0, self.HEIGHT - self.cube_size),
                              random.choice([-2, 2]), random.choice([-2, 2])])  # Moving traps

        # Power-Ups
        self.power_ups = []  # List of power-ups
        self.power_up_types = {
            'speed_boost': 'speed_boost',
            'shield': 'shield',
            'trap_disabler': 'trap_disabler',
            'enemy_freeze': 'enemy_freeze'
        }
        self.power_up_duration = 300  # Duration of power-ups in frames

        # Game variables
        self.game_over = False
        self.paused = False
        self.score = 0
        self.clock = pygame.time.Clock()

        # Player power-up states
        self.player_shield = False
        self.player_speed_boost = False
        self.trap_disabled = False
        self.enemy_frozen = False
        self.power_up_timer = 0

    def reset_game(self):
        self.player_x = random.randint(0, self.WIDTH - self.cube_size)
        self.player_y = random.randint(0, self.HEIGHT - self.cube_size)
        self.enemy_x = random.randint(0, self.WIDTH - self.cube_size)
        self.enemy_y = random.randint(0, self.HEIGHT - self.cube_size)
        self.traps = []
        for _ in range(self.num_traps):
            self.traps.append([random.randint(0, self.WIDTH - self.cube_size), random.randint(0, self.HEIGHT - self.cube_size),
                              random.choice([-2, 2]), random.choice([-2, 2])])
        self.power_ups = []
        self.game_over = False
        self.score = 0
        self.player_shield = False
        self.player_speed_boost = False
        self.trap_disabled = False
        self.enemy_frozen = False
        self.power_up_timer = 0

    def draw_player(self, x, y):
        self.screen.blit(self.player_img, (x, y))
        if self.player_shield:
            shield_radius = max(self.player_img.get_width(), self.player_img.get_height()) // 2 + 15  # Increase radius
            pygame.draw.circle(self.screen, self.CYAN, (x + self.player_img.get_width() // 2, y + self.player_img.get_height() // 2), shield_radius, 5)  # Thicker border

    def draw_enemy(self, x, y):
        self.screen.blit(self.enemy_img, (x, y))

    def draw_traps(self):
        for trap in self.traps:
            self.screen.blit(self.trap_img, (trap[0], trap[1]))

    def draw_power_ups(self):
        for power_up in self.power_ups:
            self.screen.blit(self.power_up_imgs[power_up[3]], (power_up[0], power_up[1]))

    def draw_power_up_timer(self):
        if self.power_up_timer > 0:
            bar_width = 100
            bar_height = 10
            bar_x = self.player_x + self.cube_size // 2 - bar_width // 2
            bar_y = self.player_y - 20
            pygame.draw.rect(self.screen, self.WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
            fill_width = (self.power_up_timer / self.power_up_duration) * bar_width
            pygame.draw.rect(self.screen, self.CYAN, (bar_x, bar_y, fill_width, bar_height))

    def move_traps(self):
        for trap in self.traps:
            trap[0] += trap[2]
            trap[1] += trap[3]

            # Reverse direction if hitting boundaries
            if trap[0] <= 0 or trap[0] >= self.WIDTH - self.cube_size:
                trap[2] *= -1
            if trap[1] <= 0 or trap[1] >= self.HEIGHT - self.cube_size:
                trap[3] *= -1

    def check_collision(self, rect1, rect2):
        return rect1.colliderect(rect2)

    def move_towards_player(self, player_x, player_y, enemy_x, enemy_y, speed):
        if not self.enemy_frozen:
            dx = player_x - enemy_x
            dy = player_y - enemy_y
            distance = math.hypot(dx, dy)
            if distance == 0:
                return enemy_x, enemy_y
            dx /= distance
            dy /= distance
            enemy_x += dx * speed
            enemy_y += dy * speed
        return enemy_x, enemy_y

    def spawn_power_ups(self):
        if random.randint(1, 300) <= 1.5:  # 0.33% chance to spawn a power-up
            power_up_type = random.choice(list(self.power_up_types.keys()))
            self.power_ups.append([random.randint(0, self.WIDTH - 20), random.randint(0, self.HEIGHT - 20), self.power_up_types[power_up_type], power_up_type])

    def apply_power_up(self, power_up_type):
        if power_up_type == 'shield':
            self.player_shield = True
        elif power_up_type == 'speed_boost':
            self.player_speed_boost = True
        elif power_up_type == 'trap_disabler':
            self.trap_disabled = True
        elif power_up_type == 'enemy_freeze':
            self.enemy_frozen = True
        self.power_up_timer = self.power_up_duration
        self.power_up_sound.play()

    def update_power_ups(self):
        if self.power_up_timer > 0:
            self.power_up_timer -= 1
        else:
            self.player_shield = False
            self.player_speed_boost = False
            self.trap_disabled = False
            self.enemy_frozen = False

    def run(self):
        self.background_music.play(-1)  # Play background music
        while True:
            self.screen.blit(self.background_img, (0, 0))  # Draw background

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_r:  # Restart the game
                            self.reset_game()
                        if event.key == pygame.K_q:  # Quit the game
                            pygame.quit()
                            sys.exit()
                    if event.key == pygame.K_p:  # Pause the game
                        self.paused = not self.paused

            if not self.game_over and not self.paused:
                # Player movement
                keys = pygame.key.get_pressed()
                player_speed = 10 if self.player_speed_boost else 7
                if keys[pygame.K_LEFT] and self.player_x > 0:
                    self.player_x -= player_speed
                if keys[pygame.K_RIGHT] and self.player_x < self.WIDTH - self.cube_size:
                    self.player_x += player_speed
                if keys[pygame.K_UP] and self.player_y > 0:
                    self.player_y -= player_speed
                if keys[pygame.K_DOWN] and self.player_y < self.HEIGHT - self.cube_size:
                    self.player_y += player_speed

                # Enemy movement (bot chases player)
                self.enemy_x, self.enemy_y = self.move_towards_player(self.player_x, self.player_y, self.enemy_x, self.enemy_y, self.enemy_speed)

                # Move traps
                if not self.trap_disabled:
                    self.move_traps()

                # Spawn power-ups
                self.spawn_power_ups()

                # Check for collision with power-ups
                player_rect = pygame.Rect(self.player_x, self.player_y, self.cube_size, self.cube_size)
                for power_up in self.power_ups[:]:
                    power_up_rect = pygame.Rect(power_up[0], power_up[1], 30, 30)
                    if self.check_collision(player_rect, power_up_rect):
                        self.power_ups.remove(power_up)
                        self.apply_power_up(power_up[3])

                # Update power-up states
                self.update_power_ups()

                # Draw everything
                self.draw_player(self.player_x, self.player_y)
                self.draw_enemy(self.enemy_x, self.enemy_y)
                self.draw_traps()
                self.draw_power_ups()
                self.draw_power_up_timer()

                # Check for collision between player and enemy
                if not self.player_shield:
                    enemy_rect = pygame.Rect(self.enemy_x, self.enemy_y, self.cube_size, self.cube_size)
                    if self.check_collision(player_rect, enemy_rect):
                        self.game_over = True
                        self.game_over_sound.play()
                        return True  # Signal game over

                # Check collision with traps
                if not self.player_shield and not self.trap_disabled:
                    for trap in self.traps:
                        trap_rect = pygame.Rect(trap[0], trap[1], self.cube_size, self.cube_size)
                        if self.check_collision(player_rect, trap_rect):
                            self.game_over = True
                            self.trap_collision_sound.play()
                            return True  # Signal game over

                # Increase score over time
                self.score += 1

            elif self.paused:
                # Draw pause menu
                font = pygame.font.SysFont(None, 55)
                text = font.render("Paused", True, self.WHITE)
                self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - text.get_height() // 2))
            else:
                # Game over screen
                font = pygame.font.SysFont(None, 55)
                text = font.render(f"Game Over! Score: {self.score}", True, self.WHITE)
                self.screen.blit(text, (self.WIDTH // 2 - text.get_width() // 2, self.HEIGHT // 2 - text.get_height() // 2))
                text2 = font.render("Press R to Restart or Q to Quit", True, self.WHITE)
                self.screen.blit(text2, (self.WIDTH // 2 - text2.get_width() // 2, self.HEIGHT // 2 + 50))

            # Update the display
            pygame.display.update()
            self.clock.tick(30)

# Initialize Pygame
