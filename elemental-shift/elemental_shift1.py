import pygame
import sys
import os
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 8
TILE_SIZE = 70
GRID_OFFSET_X = (WIDTH - GRID_SIZE * TILE_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * TILE_SIZE) // 2
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)      # Fire
BLUE = (50, 50, 255)     # Water
BROWN = (139, 69, 19)    # Earth
CYAN = (100, 255, 255)   # Air
GOLD = (255, 215, 0)     # Exit
GREEN = (50, 255, 50)    # Player
DARK_BLUE = (0, 0, 100)  # Background

# Elements
EMPTY, FIRE, WATER, EARTH, AIR, EXIT = 0, 1, 2, 3, 4, 5

# Game states
MENU, PLAYING, LEVEL_COMPLETE, GAME_OVER = 0, 1, 2, 3

# Setup the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyPuzzle: Elemental Shift")
clock = pygame.time.Clock()

# Load sounds
try:
    swap_sound = mixer.Sound("swap.wav")
    win_sound = mixer.Sound("win.wav")
    move_sound = mixer.Sound("move.wav")
    fire_sound = mixer.Sound("fire.wav")
    water_sound = mixer.Sound("water.wav")
except:
    # Create dummy sound objects if files don't exist
    class DummySound:
        def play(self): pass
    swap_sound = win_sound = move_sound = fire_sound = water_sound = DummySound()

# Fonts
font_large = pygame.font.SysFont("Arial", 72)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)

class Game:
    def __init__(self):
        self.state = MENU
        self.current_level = 0
        self.max_level = 2
        self.player_pos = [0, 0]
        self.moves = 0
        self.load_level(self.current_level)
        
    def load_level(self, level_num):
        self.moves = 0
        self.player_pos = [0, 0]
        
        if level_num == 0:
            # Tutorial level
            self.level = [
                [3, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 2, 0, 0, 3, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 4, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 5]
            ]
            self.level_name = "Tutorial: Learn the Elements"
            
        elif level_num == 1:
            # First real puzzle
            self.level = [
                [3, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 3, 0, 0],
                [0, 0, 2, 0, 0, 0, 0, 0],
                [0, 0, 0, 4, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 5]
            ]
            self.level_name = "Level 1: Basic Interactions"
            
        elif level_num == 2:
            # More complex puzzle
            self.level = [
                [3, 0, 0, 0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0, 3, 0, 0],
                [0, 0, 2, 0, 0, 0, 0, 0],
                [0, 0, 0, 4, 0, 0, 0, 0],
                [0, 0, 0, 0, 3, 0, 0, 0],
                [0, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 5]
            ]
            self.level_name = "Level 2: Chain Reactions"
    
    def draw(self):
        screen.fill(DARK_BLUE)
        
        if self.state == MENU:
            title = font_large.render("PyPuzzle: Elemental Shift", True, WHITE)
            start_text = font_medium.render("Press SPACE to Start", True, WHITE)
            instructions = font_small.render("Use ARROWS to move, SPACE to swap, R to rotate", True, WHITE)
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
            screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT*2//3))
            
        elif self.state == PLAYING or self.state == LEVEL_COMPLETE:
            # Draw grid background
            pygame.draw.rect(screen, BLACK, (GRID_OFFSET_X-2, GRID_OFFSET_Y-2, 
                                           GRID_SIZE*TILE_SIZE+4, GRID_SIZE*TILE_SIZE+4))
            
            # Draw tiles
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    rect = pygame.Rect(GRID_OFFSET_X + x * TILE_SIZE, 
                                     GRID_OFFSET_Y + y * TILE_SIZE, 
                                     TILE_SIZE, TILE_SIZE)
                    element = self.level[y][x]
                    
                    if element == FIRE:
                        pygame.draw.rect(screen, RED, rect)
                    elif element == WATER:
                        pygame.draw.rect(screen, BLUE, rect)
                    elif element == EARTH:
                        pygame.draw.rect(screen, BROWN, rect)
                    elif element == AIR:
                        pygame.draw.rect(screen, CYAN, rect)
                    elif element == EXIT:
                        pygame.draw.rect(screen, GOLD, rect)
                    
                    pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines
            
            # Draw player
            player_rect = pygame.Rect(
                GRID_OFFSET_X + self.player_pos[0] * TILE_SIZE + TILE_SIZE//4,
                GRID_OFFSET_Y + self.player_pos[1] * TILE_SIZE + TILE_SIZE//4,
                TILE_SIZE//2, TILE_SIZE//2
            )
            pygame.draw.rect(screen, GREEN, player_rect)
            
            # Draw UI
            level_text = font_small.render(f"{self.level_name} - Moves: {self.moves}", True, WHITE)
            screen.blit(level_text, (20, 20))
            
            if self.state == LEVEL_COMPLETE:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                complete_text = font_large.render("Level Complete!", True, WHITE)
                next_text = font_medium.render("Press SPACE to continue", True, WHITE)
                
                screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 50))
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 50))
    
    def move_player(self, dx, dy):
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            # Check if tile is passable (Earth blocks unless pushed)
            if self.level[new_y][new_x] != EARTH:
                self.player_pos[0] = new_x
                self.player_pos[1] = new_y
                self.moves += 1
                move_sound.play()
                return True
        return False
    
    def swap_tiles(self, x1, y1, x2, y2):
        if (0 <= x1 < GRID_SIZE and 0 <= y1 < GRID_SIZE and 
            0 <= x2 < GRID_SIZE and 0 <= y2 < GRID_SIZE):
            # Can't swap exit tile
            if self.level[y1][x1] == EXIT or self.level[y2][x2] == EXIT:
                return False
                
            self.level[y1][x1], self.level[y2][x2] = self.level[y2][x2], self.level[y1][x1]
            self.moves += 1
            swap_sound.play()
            
            # Check for elemental reactions
            self.check_reactions(x1, y1)
            self.check_reactions(x2, y2)
            return True
        return False
    
    def rotate_2x2(self, x, y):
        if x < GRID_SIZE - 1 and y < GRID_SIZE - 1:
            # Can't rotate if exit is in the block
            for dy in range(2):
                for dx in range(2):
                    if self.level[y+dy][x+dx] == EXIT:
                        return False
            
            # Store the 2x2 block
            a = self.level[y][x]
            b = self.level[y][x + 1]
            c = self.level[y + 1][x]
            d = self.level[y + 1][x + 1]
            
            # Rotate clockwise
            self.level[y][x] = c
            self.level[y][x + 1] = a
            self.level[y + 1][x] = d
            self.level[y + 1][x + 1] = b
            
            self.moves += 1
            swap_sound.play()
            
            # Check reactions on all rotated tiles
            for dy in range(2):
                for dx in range(2):
                    self.check_reactions(x+dx, y+dy)
            return True
        return False
    
    def check_reactions(self, x, y):
        """Handle elemental interactions between adjacent tiles"""
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return
            
        element = self.level[y][x]
        
        # Check all 4 directions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                neighbor = self.level[ny][nx]
                
                # Fire + Water = both disappear (steam)
                if (element == FIRE and neighbor == WATER) or (element == WATER and neighbor == FIRE):
                    self.level[y][x] = EMPTY
                    self.level[ny][nx] = EMPTY
                    water_sound.play()
                    fire_sound.play()
                
                # Fire + Earth = Earth becomes Fire (spreads)
                elif element == FIRE and neighbor == EARTH:
                    self.level[ny][nx] = FIRE
                    fire_sound.play()
                
                # Water + Earth = Earth becomes Water (erosion)
                elif element == WATER and neighbor == EARTH:
                    self.level[ny][nx] = WATER
                    water_sound.play()
    
    def check_win(self):
        return self.level[self.player_pos[1]][self.player_pos[0]] == EXIT
    
    def update(self):
        if self.state == PLAYING and self.check_win():
            win_sound.play()
            self.state = LEVEL_COMPLETE
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == MENU:
                if event.key == pygame.K_SPACE:
                    self.state = PLAYING
                    
            elif self.state == PLAYING:
                if event.key == pygame.K_LEFT:
                    self.move_player(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_player(1, 0)
                elif event.key == pygame.K_UP:
                    self.move_player(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.move_player(0, 1)
                elif event.key == pygame.K_SPACE:
                    # Swap with adjacent tile (right)
                    self.swap_tiles(
                        self.player_pos[0], self.player_pos[1],
                        self.player_pos[0] + 1, self.player_pos[1]
                    )
                elif event.key == pygame.K_r:
                    # Rotate 2x2 block at player's position
                    self.rotate_2x2(self.player_pos[0], self.player_pos[1])
            
            elif self.state == LEVEL_COMPLETE:
                if event.key == pygame.K_SPACE:
                    self.current_level += 1
                    if self.current_level > self.max_level:
                        self.current_level = 0
                        self.state = MENU
                    else:
                        self.load_level(self.current_level)
                        self.state = PLAYING

# Main game loop
def main():
    game = Game()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()