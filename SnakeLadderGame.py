import pygame
import random
import math
from enum import Enum

pygame.init()

# Screen dimensions
WIDTH = 700
HEIGHT = 800
BOARD_SIZE = 600
BOARD_OFFSET_X = 50
BOARD_OFFSET_Y = 120
CELL_SIZE = BOARD_SIZE // 10  # Each cell is 60x60
FPS = 90

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
BLUE = (50, 50, 220)
GREEN = (50, 200, 50)
YELLOW = (255, 215, 0)
PURPLE = (147, 112, 219)
ORANGE = (255, 140, 0)
CYAN = (0, 206, 209)
LIME = (50, 255, 50)
DARK_BLUE = (25, 25, 112)

# Game states enum
class GameState(Enum):
    MENU = 1
    PLAYING = 2
    ROLLING = 3
    MOVING = 4
    SNAKE_LADDER = 5
    GAME_OVER = 6

# Player class to handle player data and movement
class Player:
    def __init__(self, name, color, pos):
        self.name = name
        self.color = color
        self.position = 1  # starting position
        self.target_pos = 1
        self.x = pos[0]
        self.y = pos[1]
        self.target_x = pos[0]
        self.target_y = pos[1]
        self.radius = 15
        
    def get_board_position(self, position):
        row = (position - 1) // 10
        col = (position - 1) % 10
        
        # Board follows snake pattern - reverse every other row
        if row % 2 == 1:
            col = 9 - col
            
        # Board starts from bottom so flip the rows
        row = 9 - row
        
        x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
        
        return x, y
    
    # Set target position for smooth movement
    def move_to_position(self, position):
        self.target_pos = position
        self.target_x, self.target_y = self.get_board_position(position)
        print("Player moves to ",position)
    
    # Update player position with smooth animation
    def update(self):
        speed = 4
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > speed:
            # Move towards target
            self.x += dx / dist * speed
            self.y += dy / dist * speed
        else:
            # Reached target
            self.x = self.target_x
            self.y = self.target_y
            self.position = self.target_pos
        
        return dist < 1  # Return True when reached
    
    # Draw player as colored circle
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, 3)

# Dice class with rolling animation
class Dice:
    def __init__(self):
        self.value = 1
        self.rolling = False
        self.roll_timer = 0
        
        self.dice_images = {}
        for i in range(1, 7):
            try:
                img = pygame.image.load(f"dice{i}.png")
                img = pygame.transform.scale(img, (70, 70))
                self.dice_images[i] = img
            except:
                self.dice_images[i] = None
        
    def roll(self):
        self.rolling = True
        self.roll_timer = 30
        
    def update(self):
        if self.rolling:
            self.roll_timer -= 1
            # Change value during roll for animation effect
            if self.roll_timer % 6 == 0:
                self.value = random.randint(1, 6)
            if self.roll_timer <= 0:
                self.rolling = False
                self.value = random.randint(1, 6)  # Final value
                print("The dice drawn is " ,self.value)
                
    def draw(self, screen, x, y, ):
        if self.dice_images[self.value]:
            img = self.dice_images[self.value]
            img_rect = img.get_rect(center=(x, y))
            screen.blit(img, img_rect)
    

# Main game class
class SnakeLadderGame:
    def __init__(self):
        # screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake and Ladder Game")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        self.bg_image = pygame.image.load("Bg.jpg")
        self.bg_image = pygame.transform.scale(self.bg_image, (BOARD_SIZE, BOARD_SIZE))
        
        # game state
        self.state = GameState.MENU
        self.num_players = 2
        self.players = []
        self.current_player = 0
        self.dice = Dice()
        self.winner = None
        self.message = ""
        self.message_timer = 0
        self.snake_ladder_timer = 0
        
        # snakes Logic 
        self.snakes = {
            40: 3,
            27: 5,
            43: 18,
            54: 31,
            66: 45,
            76: 58,
            89: 53,
            99: 41,
        }

        #ladders logic
        self.ladders = {
            4: 25,
            13: 46,
            33: 49,
            42: 63,
            50: 69,
            62: 81,
            74: 92
        }
        
    def setup_game(self):
        self.players = []
        colors = [RED, BLUE, GREEN, YELLOW]
        
        # Starting position (bottom left)
        start_x = BOARD_OFFSET_X + CELL_SIZE // 2
        start_y = BOARD_OFFSET_Y + 9 * CELL_SIZE + CELL_SIZE // 2
        
        # Creating players
        for i in range(self.num_players):
            offset = (i - self.num_players / 2 + 0.5) * 20
            player = Player(f"Player {i+1}", colors[i], (start_x + offset, start_y))
            self.players.append(player)
        
        self.current_player = 0
        self.state = GameState.PLAYING
        self.winner = None
        
    # Check if landed on snake or ladder
    def check_snake_or_ladder(self, position):
        if position in self.snakes:
            return self.snakes[position], "snake"
        elif position in self.ladders:
            return self.ladders[position], "ladder"
        return position, None
    
    # Handle all events
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                # ESC key returns to menu
                if event.key == pygame.K_ESCAPE:
                    self.state = GameState.MENU
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == GameState.MENU:
                    self.handle_menu_click(event.pos)
                elif self.state == GameState.PLAYING:
                    self.handle_roll_click(event.pos)
                elif self.state == GameState.GAME_OVER:
                    self.state = GameState.MENU
                    
        return True
    
    # Handle menu button clicks
    def handle_menu_click(self, pos):
        # Check which button was clicked
        if 200 < pos[0] < 500 and 300 < pos[1] < 370:
            self.num_players = 2
            self.setup_game()
        elif 200 < pos[0] < 500 and 400 < pos[1] < 470:
            self.num_players = 3
            self.setup_game()
        elif 200 < pos[0] < 500 and 500 < pos[1] < 570:
            self.num_players = 4
            self.setup_game()
    
    # Handle dice click
    def handle_roll_click(self, pos):
        dice_x = WIDTH - 80
        dice_y = 60
        dist = math.sqrt((pos[0] - dice_x)**2 + (pos[1] - dice_y)**2)
        
        # Check if clicked near dice
        if dist < 50 and not self.dice.rolling:
            self.dice.roll()
            self.state = GameState.ROLLING
    
    # Main game update loop
    def update(self):
        # Handle dice rolling
        if self.state == GameState.ROLLING:
            self.dice.update()
            if not self.dice.rolling:
                player = self.players[self.current_player]
                new_pos = min(player.position + self.dice.value, 100)
                player.move_to_position(new_pos)
                self.state = GameState.MOVING
        
        # Handle player movement
        elif self.state == GameState.MOVING:
            player = self.players[self.current_player]
            if player.update():  # If reached destination
                new_pos, encounter = self.check_snake_or_ladder(player.position)
                
                if encounter == "snake":
                    self.message = f"Snake bite! Sliding to {new_pos}"
                    self.message_timer = 90
                    self.snake_ladder_timer = 30
                    self.state = GameState.SNAKE_LADDER
                elif encounter == "ladder":
                    self.message = f"Climbing ladder to {new_pos}!"
                    self.message_timer = 90
                    self.snake_ladder_timer = 30
                    self.state = GameState.SNAKE_LADDER
                else:
                    # Check for win
                    if player.position == 100:
                        self.winner = player
                        self.state = GameState.GAME_OVER
                    else:
                        # Next player's turn
                        self.current_player = (self.current_player + 1) % self.num_players
                        self.state = GameState.PLAYING
        
        # Handle snake/ladder movement
        elif self.state == GameState.SNAKE_LADDER:
            if self.snake_ladder_timer > 0:
                self.snake_ladder_timer -= 1
            else:
                player = self.players[self.current_player]
                if player.update():
                    new_pos, _ = self.check_snake_or_ladder(player.position)
                    if new_pos != player.position:
                        player.move_to_position(new_pos)
                    else:
                        if player.position == 100:
                            self.winner = player
                            self.state = GameState.GAME_OVER
                        else:
                            self.current_player = (self.current_player + 1) % self.num_players
                            self.state = GameState.PLAYING
        else:
            # Update all players
            for player in self.players:
                player.update()
        
        # Update message timer
        if self.message_timer > 0:
            self.message_timer -= 1
    
    # Main draw function
    def draw(self):
        self.screen.fill((20, 20, 40))
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()
            self.draw_game_over()
        else:
            self.draw_game()
    
    # Draw main menu
    def draw_menu(self):
        self.screen.fill((30, 30, 60))
        
        # Title
        title = self.large_font.render("SNAKE & LADDER", True, YELLOW)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        # Subtitle
        subtitle = self.small_font.render("Roll the dice and climb to victory!", True, WHITE)
        self.screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 180))
        
        # Player selection buttons
        buttons = [
            ("2 Players", 300, ORANGE),
            ("3 Players", 400, CYAN),
            ("4 Players", 500, LIME)
        ]
        
        for text, y, color in buttons:
            rect = pygame.Rect(200, y, 300, 60)
            pygame.draw.rect(self.screen, color, rect, border_radius=15)
            pygame.draw.rect(self.screen, WHITE, rect, 4, border_radius=15)
            
            label = self.font.render(text, True, WHITE)
            self.screen.blit(label, (WIDTH//2 - label.get_width()//2, y + 15))
        
        # Footer
        footer = self.small_font.render("Press ESC to return to menu anytime", True, (200, 200, 200))
        self.screen.blit(footer, (WIDTH//2 - footer.get_width()//2, HEIGHT - 50))
    
    #  game board and elements
    def draw_game(self):
        self.screen.fill((40, 40, 60))
         #  board background image
        if self.bg_image:
            self.screen.blit(self.bg_image, (BOARD_OFFSET_X, BOARD_OFFSET_Y))
        
        # Draw title
        title = self.font.render("Snake And Ladder", True, WHITE)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Show current player indicator
        if self.state != GameState.GAME_OVER:
            player = self.players[self.current_player]
            indicator_rect = pygame.Rect(10, 60, 180, 50)
            pygame.draw.rect(self.screen, player.color, indicator_rect, border_radius=10)
            pygame.draw.rect(self.screen, BLACK, indicator_rect, 3, border_radius=10)
            
            text = self.small_font.render(f"{player.name}'s Turn", True, WHITE)
            self.screen.blit(text, (20, 75))
        
        # Draw dice
        self.dice.draw(self.screen, WIDTH - 80, 60)
        
        # Show roll instruction
        if self.state == GameState.PLAYING and not self.dice.rolling:
            roll_text = self.small_font.render("Click Dice!", True, WHITE)
            self.screen.blit(roll_text, (WIDTH - 120, 100))
        
        # Draw all players
        for player in self.players:
            player.draw(self.screen)
            
        # Show player positions at bottom
        for i, player in enumerate(self.players):
            info_y = 730 + i * 18
            info_rect = pygame.Rect(10, info_y, 200, 16)
            pygame.draw.rect(self.screen, player.color, info_rect, border_radius=5)
            
            info = self.small_font.render(f"{player.name}: Pos {player.position}", True, WHITE)
            self.screen.blit(info, (15, info_y))
        
        # Show messages (snake/ladder notifications)
        if self.message_timer > 0:
            msg = self.font.render(self.message, True, WHITE)
            padding = 20
            bg_rect = pygame.Rect(WIDTH//2 - msg.get_width()//2 - padding,
                                HEIGHT//2 - 40, msg.get_width() + padding * 2, 70)
            
            pygame.draw.rect(self.screen, PURPLE, bg_rect, border_radius=15)
            pygame.draw.rect(self.screen, YELLOW, bg_rect, 4, border_radius=15)
            self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 18))
    
    # game over screen
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Winner announcement
        winner_text = f"{self.winner.name} Wins!"
        winner_surface = self.large_font.render(winner_text, True, self.winner.color)
        winner_rect = winner_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(winner_surface, winner_rect)
        
        # Continue instruction
        continue_text = self.small_font.render("Click anywhere to return to menu", True, WHITE)
        continue_rect = continue_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        self.screen.blit(continue_text, continue_rect)
    
    # Main game loop
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        
if __name__ == "__main__":
    game = SnakeLadderGame()
    game.run()