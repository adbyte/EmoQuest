import pygame
import speech_recognition as sr
import random

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound, is_bot=False):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.offset = data[2]
        self.flip = flip
        self.animation_list = self.load_images(sprite_sheet, animation_steps)
        self.action = 0  # 0:idle, 1:run, 2:jump, 3:attack1, 4:attack2, 5:hit, 6:death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.update_time = pygame.time.get_ticks()
        self.rect = pygame.Rect((x, y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.attack_sound = sound
        self.hit = False
        self.health = 100
        self.alive = True
        self.is_bot = is_bot  # Set bot flag

        # Voice recognition setup for player 1
        if self.player == 1 and not self.is_bot:
            self.recognizer = sr.Recognizer()
            self.voice_command = None  # Stores the last recognized command

    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y * self.size, self.size, self.size)
                temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
            animation_list.append(temp_img_list)
        return animation_list

    def listen_for_commands(self):
        """Listens for voice commands and updates movement accordingly."""
        try:
            with sr.Microphone() as source:
                print("Listening for commands...")
                audio = self.recognizer.listen(source, timeout=2)
                command = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized command: {command}")
                self.voice_command = command
        except sr.UnknownValueError:
            print("Could not understand voice command.")
        except sr.RequestError:
            print("Could not connect to speech recognition service.")

    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10
        BOT_SPEED = 4  # Reduced bot speed
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False
        self.attack_type = 0

        if self.is_bot:
            # Bot logic (move toward player slowly)
            if target.rect.centerx > self.rect.centerx:
                dx = BOT_SPEED  # Move right
            elif target.rect.centerx < self.rect.centerx:
                dx = -BOT_SPEED  # Move left

            # Randomly jump or attack
            if random.randint(1, 50) == 1:  
                self.vel_y = -30  # Occasional jump
            if abs(target.rect.centerx - self.rect.centerx) < 100 and self.attack_cooldown == 0:
                self.attack(target)
                self.attack_type = random.choice([1, 2])

        elif self.player == 1:  # Voice-controlled player
            self.listen_for_commands()
            if self.voice_command == "left":
                dx = -SPEED
                self.running = True
            elif self.voice_command == "right":
                dx = SPEED
                self.running = True
            elif self.voice_command == "jump" and not self.jump:
                self.vel_y = -30
                self.jump = True
            elif self.voice_command == "kill":
                self.attack(target)
                self.attack_type = 1

        # Apply gravity
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Ensure player stays on screen
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # Ensure players face each other
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # Apply attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

    def update(self):
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # Death
        elif self.hit:
            self.update_action(5)  # Hit
        elif self.attacking:
            if self.attack_type == 1:
                self.update_action(3)  # Attack 1
            elif self.attack_type == 2:
                self.update_action(4)  # Attack 2
        elif self.jump:
            self.update_action(2)  # Jump
        elif self.running:
            self.update_action(1)  # Run
        else:
            self.update_action(0)  # Idle

        animation_cooldown = 50
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        if self.frame_index >= len(self.animation_list[self.action]):
            if not self.alive:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if self.action in [3, 4]:  # Attack actions
                    self.attacking = False
                    self.attack_cooldown = 20
                if self.action == 5:  # Hit action
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale)))
