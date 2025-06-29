import pygame
import sys
import os
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 650  # Increased height for UI
GRID_SIZE = 8
TILE_SIZE = 70
GRID_OFFSET_X = (WIDTH - GRID_SIZE * TILE_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * TILE_SIZE) // 2 - 30
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)      # Fire (dangerous)
DARK_RED = (180, 0, 0)   # Fire (original)
BLUE = (50, 50, 255)     # Water (safe)
BROWN = (139, 69, 19)    # Earth (blocking)
CYAN = (100, 255, 255)   # Air (safe)
GOLD = (255, 215, 0)     # Exit
GREEN = (50, 255, 50)    # Player
DARK_GREEN = (0, 100, 0) # Health bar
DARK_BLUE = (0, 0, 100)  # Background
GRAY = (100, 100, 100)   # Walls
YELLOW = (255, 255, 0)   # Ammo

# Elements
EMPTY, FIRE, WATER, EARTH, AIR, EXIT, WALL = 0, 1, 2, 3, 4, 5, 6

# Game states
MENU, PLAYING, LEVEL_COMPLETE, GAME_OVER = 0, 1, 2, 3

# Setup the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyPuzzle: Elemental Shift - Enhanced")
clock = pygame.time.Clock()

# Create dummy sound objects if files don't exist
class DummySound:
    def play(self): pass

try:
    swap_sound = mixer.Sound("swap.wav")
    win_sound = mixer.Sound("win.wav")
    move_sound = mixer.Sound("move.wav")
    fire_sound = mixer.Sound("fire.wav")
    water_sound = mixer.Sound("water.wav")
    hurt_sound = mixer.Sound("hurt.wav")
    ammo_sound = mixer.Sound("ammo.wav")
except:
    swap_sound = win_sound = move_sound = fire_sound = water_sound = hurt_sound = ammo_sound = DummySound()

# Fonts
font_large = pygame.font.SysFont("Arial", 72)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)

class Game:
    def __init__(self):
        self.state = MENU
        self.current_level = 0
        self.max_level = 3
        self.player_pos = [0, 0]
        self.moves = 0
        self.health = 100
        self.max_health = 100
        self.ammo = 5
        self.min_moves = 0
        self.load_level(self.current_level)
        
    def load_level(self, level_num):
        self.moves = 0
        self.ammo = 5 + level_num * 2  # More ammo in later levels
        self.health = self.max_health
        self.player_pos = [0, 0]
        
        if level_num == 0:
            # Tutorial level - teaches mechanics
            self.level = [
                [0, 6, 6, 6, 6, 6, 6, 6],
                [0, 0, 0, 0, 0, 0, 0, 6],
                [6, 0, 1, 3, 0, 0, 0, 6],
                [6, 0, 3, 0, 0, 0, 5, 6],
                [6, 0, 0, 0, 0, 3, 0, 6],
                [6, 0, 2, 0, 3, 0, 0, 6],
                [6, 0, 0, 0, 0, 0, 0, 6],
                [6, 6, 6, 6, 6, 6, 6, 6]
            ]
            self.level_name = "Tutorial: Learn the Elements"
            self.min_moves = 8
            
        elif level_num == 1:
            # First real puzzle
            self.level = [
                [0, 6, 6, 6, 6, 6, 6, 6],
                [0, 0, 1, 0, 0, 3, 0, 6],
                [6, 0, 0, 2, 0, 0, 0, 6],
                [6, 0, 0, 0, 4, 0, 0, 6],
                [6, 0, 0, 0, 0, 0, 0, 6],
                [6, 0, 0, 0, 0, 0, 0, 6],
                [6, 0, 0, 0, 0, 0, 5, 6],
                [6, 6, 6, 6, 6, 6, 6, 6]
            ]
            self.level_name = "Level 1: Fire and Water"
            self.min_moves = 12
            self.player_pos = [1, 1]
            
        elif level_num == 2:
            # More complex puzzle
            self.level = [
                [0, 0, 6, 6, 6, 6, 6, 6],
                [6, 0, 1, 0, 0, 3, 0, 6],
                [6, 0, 0, 2, 0, 0, 0, 6],
                [6, 0, 0, 0, 4, 0, 0, 6],
                [6, 0, 0, 0, 0, 3, 0, 6],
                [6, 0, 0, 0, 0, 0, 2, 6],
                [6, 0, 0, 0, 0, 0, 5, 6],
                [6, 6, 6, 6, 6, 6, 6, 6]
            ]
            self.level_name = "Level 2: Chain Reactions"
            self.min_moves = 15
            self.player_pos = [1, 1]
            
        elif level_num == 3:
            # Advanced puzzle
            self.level = [
                [6, 6, 6, 6, 6, 6, 6, 6],
                [6, 0, 1, 0, 0, 3, 0, 6],
                [6, 0, 0, 2, 0, 0, 0, 6],
                [6, 0, 0, 0, 4, 0, 0, 6],
                [6, 0, 0, 0, 0, 3, 0, 6],
                [6, 0, 0, 0, 0, 0, 2, 6],
                [6, 0, 0, 0, 0, 0, 5, 6],
                [6, 6, 6, 6, 6, 6, 6, 6]
            ]
            self.level_name = "Level 3: Master Shifter"
            self.min_moves = 20
            self.player_pos = [1, 1]
    
    def draw(self):
        screen.fill(DARK_BLUE)
        
        if self.state == MENU:
            title = font_large.render("PyPuzzle: Elemental Shift", True, WHITE)
            subtitle = font_medium.render("Enhanced Edition", True, YELLOW)
            start_text = font_medium.render("Press SPACE to Start", True, WHITE)
            instructions = [
                "Use ARROWS to move",
                "SPACE to swap with adjacent tile",
                "R to rotate 2x2 block",
                "Avoid fire (lose health)",
                "Collect blue ammo drops",
                "Reach the golden exit"
            ]
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//4))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//4 + 80))
            screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2))
            
            for i, line in enumerate(instructions):
                text = font_small.render(line, True, WHITE)
                screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 + 60 + i*30))
                
        elif self.state == GAME_OVER:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            game_over = font_large.render("Game Over!", True, RED)
            restart = font_medium.render("Press R to restart", True, WHITE)
            
            screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, HEIGHT//2 - 50))
            screen.blit(restart, (WIDTH//2 - restart.get_width()//2, HEIGHT//2 + 50))
            
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
                    elif element == WALL:
                        pygame.draw.rect(screen, GRAY, rect)
                    
                    pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines
            
            # Draw player
            player_rect = pygame.Rect(
                GRID_OFFSET_X + self.player_pos[0] * TILE_SIZE + TILE_SIZE//4,
                GRID_OFFSET_Y + self.player_pos[1] * TILE_SIZE + TILE_SIZE//4,
                TILE_SIZE//2, TILE_SIZE//2
            )
            pygame.draw.rect(screen, GREEN, player_rect)
            
            # Draw UI
            level_text = font_small.render(f"{self.level_name}", True, WHITE)
            moves_text = font_small.render(f"Moves: {self.moves} (Min: {self.min_moves})", True, WHITE)
            ammo_text = font_small.render(f"Ammo: {self.ammo}", True, YELLOW)
            
            screen.blit(level_text, (20, 20))
            screen.blit(moves_text, (20, 50))
            screen.blit(ammo_text, (WIDTH - 120, 20))
            
            # Health bar
            health_width = 200
            current_health_width = (self.health / self.max_health) * health_width
            pygame.draw.rect(screen, GRAY, (WIDTH//2 - health_width//2, 20, health_width, 20))
            pygame.draw.rect(screen, DARK_GREEN, (WIDTH//2 - health_width//2, 20, current_health_width, 20))
            health_text = font_small.render(f"Health: {self.health}/{self.max_health}", True, WHITE)
            screen.blit(health_text, (WIDTH//2 - health_text.get_width()//2, 22))
            
            if self.state == LEVEL_COMPLETE:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                complete_text = font_large.render("Level Complete!", True, WHITE)
                moves_made = font_medium.render(f"Moves: {self.moves} (Min: {self.min_moves})", True, WHITE)
                next_text = font_medium.render("Press SPACE to continue", True, WHITE)
                
                screen.blit(complete_text, (WIDTH//2 - complete_text.get_width()//2, HEIGHT//2 - 80))
                screen.blit(moves_made, (WIDTH//2 - moves_made.get_width()//2, HEIGHT//2))
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 80))
    
    def move_player(self, dx, dy):
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        
        if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
            target = self.level[new_y][new_x]
            
            # Check if tile is passable
            if target in [EMPTY, FIRE, WATER, AIR, EXIT]:  # Can walk through these
                self.player_pos[0] = new_x
                self.player_pos[1] = new_y
                self.moves += 1
                move_sound.play()
                
                # Take damage from fire
                if target == FIRE:
                    self.health -= 10
                    hurt_sound.play()
                    if self.health <= 0:
                        self.state = GAME_OVER
                
                # Collect water (heals)
                elif target == WATER:
                    self.health = min(self.health + 5, self.max_health)
                    water_sound.play()
                    self.level[new_y][new_x] = EMPTY
                
                return True
        return False
    
    def swap_tiles(self, x1, y1, x2, y2):
        if self.ammo <= 0:
            return False
            
        if (0 <= x1 < GRID_SIZE and 0 <= y1 < GRID_SIZE and 
            0 <= x2 < GRID_SIZE and 0 <= y2 < GRID_SIZE):
            # Can't swap exit or walls
            if (self.level[y1][x1] in [EXIT, WALL] or 
                self.level[y2][x2] in [EXIT, WALL]):
                return False
                
            self.level[y1][x1], self.level[y2][x2] = self.level[y2][x2], self.level[y1][x1]
            self.moves += 1
            self.ammo -= 1
            swap_sound.play()
            
            # Check for elemental reactions
            self.check_reactions(x1, y1)
            self.check_reactions(x2, y2)
            return True
        return False
    
    def rotate_2x2(self, x, y):
        if self.ammo <= 0:
            return False
            
        if x < GRID_SIZE - 1 and y < GRID_SIZE - 1:
            # Can't rotate if exit or walls are in the block
            for dy in range(2):
                for dx in range(2):
                    if self.level[y+dy][x+dx] in [EXIT, WALL]:
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
            self.ammo -= 1
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
                    
                # Create ammo pickup sometimes
                if element == AIR and neighbor == AIR and random.random() < 0.1:
                    self.level[ny][nx] = 7  # Ammo pickup (not implemented fully)
    
    def check_win(self):
        return self.level[self.player_pos[1]][self.player_pos[0]] == EXIT and self.health > 0
    
    def update(self):
        if self.state == PLAYING:
            if self.check_win():
                win_sound.play()
                self.state = LEVEL_COMPLETE
            elif self.health <= 0:
                self.state = GAME_OVER
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == MENU:
                if event.key == pygame.K_SPACE:
                    self.state = PLAYING
                    
            elif self.state == GAME_OVER:
                if event.key == pygame.K_r:
                    self.load_level(self.current_level)
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
                elif event.key == pygame.K_SPACE and self.ammo > 0:
                    # Swap with adjacent tile (right)
                    self.swap_tiles(
                        self.player_pos[0], self.player_pos[1],
                        self.player_pos[0] + 1, self.player_pos[1]
                    )
                elif event.key == pygame.K_r and self.ammo > 0:
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
    import random  # For random ammo drops
    main()