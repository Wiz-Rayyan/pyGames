import pygame
import sys
from pygame import mixer

# Initialize Pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 650
GRID_SIZE = 8
TILE_SIZE = 70
GRID_OFFSET_X = (WIDTH - GRID_SIZE * TILE_SIZE) // 2
GRID_OFFSET_Y = (HEIGHT - GRID_SIZE * TILE_SIZE) // 2 - 20
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
PURPLE = (150, 50, 255)  # Swap Gate
GREEN = (50, 255, 50)    # Phase Gate
YELLOW = (255, 255, 0)   # Entangler
GRAY = (100, 100, 100)   # Walls

# Game states
MENU, PLAYING, LEVEL_COMPLETE = 0, 1, 2

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Grid: Quantum Pathfinder")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.SysFont("Arial", 72)
font_medium = pygame.font.SysFont("Arial", 36)
font_small = pygame.font.SysFont("Arial", 24)

class QuantumGame:
    def __init__(self):
        self.state = MENU
        self.current_level = 0
        self.load_level(self.current_level)
        
    def load_level(self, level_num):
        self.red_pos = [1, 1]  # Starting positions
        self.blue_pos = [6, 6]
        self.moves = 0
        self.red_phased = False
        self.blue_phased = False
        self.entangled = False
        
        if level_num == 0:  # Tutorial
            self.level = [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
            self.red_goal = [7, 6]
            self.blue_goal = [2, 1]
            self.level_name = "Tutorial: Basic Movement"
        
        elif level_num == 1:  # Swap Gate
            self.level = [
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0, 0, 0, 0],
                [0, 0, 0, 3, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 2, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0]
            ]
            self.red_goal = [6, 1]
            self.blue_goal = [1, 6]
            self.level_name = "Level 1: Quantum Swap"
    
    def draw(self):
        screen.fill(BLACK)
        
        if self.state == MENU:
            title = font_large.render("NEON GRID", True, PURPLE)
            subtitle = font_medium.render("Quantum Pathfinder", True, WHITE)
            start = font_medium.render("Press E to toggle mirrored/opposite movement. Press SPACE to Begin", True, GREEN)
            
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, HEIGHT//3 + 80))
            screen.blit(start, (WIDTH//2 - start.get_width()//2, HEIGHT//2))
        
        elif self.state == PLAYING or self.state == LEVEL_COMPLETE:
            # Draw grid
            for y in range(GRID_SIZE):
                for x in range(GRID_SIZE):
                    rect = pygame.Rect(
                        GRID_OFFSET_X + x * TILE_SIZE,
                        GRID_OFFSET_Y + y * TILE_SIZE,
                        TILE_SIZE, TILE_SIZE
                    )
                    
                    # Draw gates/walls
                    cell = self.level[y][x]
                    if cell == 1:  # Swap Gate
                        pygame.draw.rect(screen, PURPLE, rect)
                    elif cell == 2:  # Phase Gate
                        pygame.draw.rect(screen, GREEN, rect)
                    elif cell == 3:  # Wall
                        pygame.draw.rect(screen, GRAY, rect)
                    
                    pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # Grid lines
            
            # Draw goals
            pygame.draw.circle(
                screen, RED, 
                (GRID_OFFSET_X + self.red_goal[0] * TILE_SIZE + TILE_SIZE//2,
                 GRID_OFFSET_Y + self.red_goal[1] * TILE_SIZE + TILE_SIZE//2),
                TILE_SIZE//3, 2
            )
            pygame.draw.circle(
                screen, BLUE, 
                (GRID_OFFSET_X + self.blue_goal[0] * TILE_SIZE + TILE_SIZE//2,
                 GRID_OFFSET_Y + self.blue_goal[1] * TILE_SIZE + TILE_SIZE//2),
                TILE_SIZE//3, 2
            )
            
            # Draw particles
            pygame.draw.circle(
                screen, RED,
                (GRID_OFFSET_X + self.red_pos[0] * TILE_SIZE + TILE_SIZE//2,
                 GRID_OFFSET_Y + self.red_pos[1] * TILE_SIZE + TILE_SIZE//2),
                TILE_SIZE//3
            )
            pygame.draw.circle(
                screen, BLUE,
                (GRID_OFFSET_X + self.blue_pos[0] * TILE_SIZE + TILE_SIZE//2,
                 GRID_OFFSET_Y + self.blue_pos[1] * TILE_SIZE + TILE_SIZE//2),
                TILE_SIZE//3
            )
            
            # Draw UI
            level_text = font_small.render(self.level_name, True, WHITE)
            moves_text = font_small.render(f"Moves: {self.moves}", True, WHITE)
            screen.blit(level_text, (20, 20))
            screen.blit(moves_text, (20, 50))
            
            if self.state == LEVEL_COMPLETE:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                complete = font_large.render("LEVEL COMPLETE!", True, GREEN)
                next_text = font_medium.render("Press SPACE to continue", True, WHITE)
                screen.blit(complete, (WIDTH//2 - complete.get_width()//2, HEIGHT//2 - 50))
                screen.blit(next_text, (WIDTH//2 - next_text.get_width()//2, HEIGHT//2 + 50))
    
    def move_particles(self, dx, dy):
        if self.entangled:
            dx, dy = -dx, -dy  # Reverse for blue particle
        
        # Try to move red particle
        new_red_x = self.red_pos[0] + dx
        new_red_y = self.red_pos[1] + dy
        
        # Check if red can move
        red_can_move = False
        if 0 <= new_red_x < GRID_SIZE and 0 <= new_red_y < GRID_SIZE:
            if self.level[new_red_y][new_red_x] != 3 or self.red_phased:  # Wall check
                red_can_move = True
        
        # Try to move blue particle
        new_blue_x = self.blue_pos[0] + (-dx if self.entangled else dx)
        new_blue_y = self.blue_pos[1] + (-dy if self.entangled else dy)
        
        # Check if blue can move
        blue_can_move = False
        if 0 <= new_blue_x < GRID_SIZE and 0 <= new_blue_y < GRID_SIZE:
            if self.level[new_blue_y][new_blue_x] != 3 or self.blue_phased:  # Wall check
                blue_can_move = True
        
        # If both can move, update positions
        if red_can_move and blue_can_move:
            self.red_pos = [new_red_x, new_red_y]
            self.blue_pos = [new_blue_x, new_blue_y]
            self.moves += 1
            
            # Check for gate interactions
            self.check_gates()
    
    def check_gates(self):
        # Check if red is on a gate
        red_cell = self.level[self.red_pos[1]][self.red_pos[0]]
        blue_cell = self.level[self.blue_pos[1]][self.blue_pos[0]]
        
        if red_cell == 1 or blue_cell == 1:  # Swap Gate
            self.red_pos, self.blue_pos = self.blue_pos, self.red_pos
        
        if red_cell == 2:  # Phase Gate (red)
            self.red_phased = not self.red_phased
        
        if blue_cell == 2:  # Phase Gate (blue)
            self.blue_phased = not self.blue_phased
        
        # Check if both reached goals
        if (self.red_pos == self.red_goal and 
            self.blue_pos == self.blue_goal):
            self.state = LEVEL_COMPLETE
    
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == MENU and event.key == pygame.K_SPACE:
                self.state = PLAYING
            
            elif self.state == PLAYING:
                if event.key == pygame.K_LEFT:
                    self.move_particles(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    self.move_particles(1, 0)
                elif event.key == pygame.K_UP:
                    self.move_particles(0, -1)
                elif event.key == pygame.K_DOWN:
                    self.move_particles(0, 1)
                elif event.key == pygame.K_e:  # Toggle entanglement
                    self.entangled = not self.entangled
            
            elif self.state == LEVEL_COMPLETE and event.key == pygame.K_SPACE:
                self.current_level += 1
                if self.current_level > 1:  # Only 2 levels in this demo
                    self.current_level = 0
                    self.state = MENU
                else:
                    self.load_level(self.current_level)
                    self.state = PLAYING

# Main game loop
def main():
    game = QuantumGame()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_input(event)
        
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()