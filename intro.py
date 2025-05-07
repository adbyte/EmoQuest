import pygame
import sys

from report import display_report_from_json


# Import your mini-games
from Game1.fear import RealmOfFear
from Game2.main import BrawlerGame
from Game3.mysterydoor import RealmOfPortals
from Game4.smile import ExpressionPlatformer

# Initialize Pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EmoQuest")

# Define states
INTRO = "intro"
GAME1 = "game1"
GAME2 = "game2"
GAME3 = "game3"
GAME4 = "game4"
END = "end"

class GameManager:
    def __init__(self):
        self.state = INTRO
        self.games = {}
        self.screen = screen
        self.WIDTH, self.HEIGHT = screen.get_width(), screen.get_height()
        
        self.game_order = [GAME1, GAME3, GAME4, GAME2]  # Game 2 plays last
        self.current_game_index = 0
        
        self.intro_images = {
            GAME1: "Game1/Assets/bg1fear.png",
            GAME2: "Game2/Assets/images/background/ragebg.png",
            GAME3: "Game3/Assets/surprisebg.png",
            GAME4: "Game4/Assets/graphics/happybg.png"
        }

    def initialize_game(self, game_name):
        if game_name not in self.games:
            if game_name == GAME1:
                self.games[GAME1] = RealmOfFear(self.screen)
            elif game_name == GAME2:
                self.games[GAME2] = BrawlerGame(self.screen)
            elif game_name == GAME3:
                self.games[GAME3] = RealmOfPortals(self.screen)
            elif game_name == GAME4:
                self.games[GAME4] = ExpressionPlatformer(self.screen)

    def show_intro_image(self, image_path, fade_time=2000):
        try:
            intro_image = pygame.image.load(image_path).convert_alpha()
            intro_scaled = pygame.transform.scale(intro_image, (self.WIDTH, self.HEIGHT))
        except Exception as e:
            print(f"Error loading intro image: {e}")
            self.screen.fill((0, 0, 0))
            pygame.display.flip()
            return False

        for alpha in range(0, 255, 5):
            self.screen.fill((0, 0, 0))
            intro_scaled.set_alpha(alpha)
            self.screen.blit(intro_scaled, (0, 0))
            pygame.display.flip()
            pygame.time.delay(fade_time // 255)

        self.screen.blit(intro_scaled, (0, 0))
        pygame.display.flip()
        self.wait_for_space()
        return True

    def wait_for_space(self):
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    waiting = False

    def run_intro(self):
        self.show_intro_image("mainbg.png")  # Replace with your actual main intro image path
        self.state = self.game_order[0]
        return True

    def run(self):
        if not self.run_intro():
            return

        running = True
        while running:
            if self.state in self.game_order:
                self.initialize_game(self.state)

                if self.state in self.intro_images:
                    self.show_intro_image(self.intro_images[self.state])

                game_over = self.games[self.state].run()

                if game_over:
                    self.current_game_index += 1
                    if self.current_game_index < len(self.game_order):
                        self.state = self.game_order[self.current_game_index]
                    else:
                        self.state = END

            elif self.state == END:
                    pygame.quit()
                    display_report_from_json()
                    return



            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

        pygame.quit()
       

# Run the game manager
if __name__ == "__main__":
    manager = GameManager()
    manager.run()
