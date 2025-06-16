import pygame
import sys
import random
import time
import os
from pygame import mixer

# Initialize Pygame
pygame.init()
try:
    mixer.init()
except pygame.error:
    print("Warning: Audio device not available. Sound will be disabled.")
    # Create dummy sound class to avoid errors
    class DummySound:
        def play(self):
            pass
    match_sound = DummySound()
    swap_sound = DummySound()
    game_over_sound = DummySound()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 8
CELL_SIZE = 60
GRID_OFFSET_X = (SCREEN_WIDTH - GRID_SIZE * CELL_SIZE) // 2
GRID_OFFSET_Y = 120

# Colors
BACKGROUND_COLOR = (25, 26, 30)
TEXT_COLOR = (230, 230, 230)
BUTTON_COLOR = (45, 50, 60)
BUTTON_HOVER_COLOR = (65, 70, 80)
GRID_COLOR = (40, 42, 50)

# Candy colors
CANDY_COLORS = [
    (255, 0, 0),     # Red
    (0, 255, 0),     # Green
    (0, 0, 255),     # Blue
    (255, 255, 0),   # Yellow
    (255, 0, 255),   # Magenta
    (0, 255, 255),   # Cyan
]

# Game settings
MAX_MOVES = 20
MATCH_SCORE = 10
COMBO_BONUS = 5

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Candy Crush")

# Load fonts
try:
    font_path = os.path.join("assets", "fonts", "Roboto-Bold.ttf")
    if os.path.exists(font_path):
        font = pygame.font.Font(font_path, 36)
        small_font = pygame.font.Font(font_path, 24)
    else:
        font = pygame.font.SysFont("Arial", 36)
        small_font = pygame.font.SysFont("Arial", 24)
except:
    font = pygame.font.SysFont("Arial", 36)
    small_font = pygame.font.SysFont("Arial", 24)

# Load sounds
try:
    match_sound = mixer.Sound(os.path.join("assets", "sounds", "match.wav"))
    swap_sound = mixer.Sound(os.path.join("assets", "sounds", "swap.wav"))
    game_over_sound = mixer.Sound(os.path.join("assets", "sounds", "game_over.wav"))
except:
    match_sound = None
    swap_sound = None
    game_over_sound = None

class Candy:
    def __init__(self, row, col, color_index):
        self.row = row
        self.col = col
        self.color_index = color_index
        self.color = CANDY_COLORS[color_index]
        self.x = GRID_OFFSET_X + col * CELL_SIZE
        self.y = GRID_OFFSET_Y + row * CELL_SIZE
        self.target_x = self.x
        self.target_y = self.y
        self.moving = False
        self.scale = 1.0
        self.target_scale = 1.0
        self.animation_speed = 0.2

    def update(self):
        # Handle movement animation
        if self.x != self.target_x or self.y != self.target_y:
            self.moving = True
            self.x += (self.target_x - self.x) * self.animation_speed
            self.y += (self.target_y - self.y) * self.animation_speed
            
            # If close enough to target, snap to it
            if abs(self.x - self.target_x) < 1:
                self.x = self.target_x
            if abs(self.y - self.target_y) < 1:
                self.y = self.target_y
                
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False
        
        # Handle scale animation
        if self.scale != self.target_scale:
            self.scale += (self.target_scale - self.scale) * self.animation_speed
            if abs(self.scale - self.target_scale) < 0.01:
                self.scale = self.target_scale

    def draw(self, surface):
        size = int(CELL_SIZE * 0.8 * self.scale)
        x_center = self.x + CELL_SIZE // 2
        y_center = self.y + CELL_SIZE // 2
        pygame.draw.circle(surface, self.color, (int(x_center), int(y_center)), size // 2)
        pygame.draw.circle(surface, (255, 255, 255, 100), (int(x_center - size // 5), int(y_center - size // 5)), size // 8)

    def set_position(self, row, col):
        self.row = row
        self.col = col
        self.target_x = GRID_OFFSET_X + col * CELL_SIZE
        self.target_y = GRID_OFFSET_Y + row * CELL_SIZE

    def animate_match(self):
        self.target_scale = 0.1

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.text_color = TEXT_COLOR
        self.hovered = False
        
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, 2, border_radius=10)
        
        text_surf = small_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hovered:
            if self.action:
                self.action()
            return True
        return False

class Game:
    def __init__(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.moves_left = MAX_MOVES
        self.selected_candy = None
        self.game_over = False
        self.animations_running = False
        # Position the New Game button in the top right corner next to moves text
        self.restart_button = Button(SCREEN_WIDTH - 150, 20, 130, 40, "New Game", self.reset)
        self.fill_grid()
        
    def fill_grid(self):
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                # Avoid creating matches when filling the grid
                color_options = list(range(len(CANDY_COLORS)))
                
                # Check horizontal matches
                if col >= 2:
                    if self.grid[row][col-1] and self.grid[row][col-2]:
                        if self.grid[row][col-1].color_index == self.grid[row][col-2].color_index:
                            if self.grid[row][col-1].color_index in color_options:
                                color_options.remove(self.grid[row][col-1].color_index)
                
                # Check vertical matches
                if row >= 2:
                    if self.grid[row-1][col] and self.grid[row-2][col]:
                        if self.grid[row-1][col].color_index == self.grid[row-2][col].color_index:
                            if self.grid[row-1][col].color_index in color_options:
                                color_options.remove(self.grid[row-1][col].color_index)
                
                # If no valid colors, use any color
                if not color_options:
                    color_options = list(range(len(CANDY_COLORS)))
                    
                color_index = random.choice(color_options)
                self.grid[row][col] = Candy(row, col, color_index)
    
    def draw(self):
        # Draw background
        screen.fill(BACKGROUND_COLOR)
        
        # Draw grid background
        grid_rect = pygame.Rect(
            GRID_OFFSET_X - 10, 
            GRID_OFFSET_Y - 10, 
            CELL_SIZE * GRID_SIZE + 20, 
            CELL_SIZE * GRID_SIZE + 20
        )
        pygame.draw.rect(screen, GRID_COLOR, grid_rect, border_radius=15)
        
        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            # Horizontal lines
            pygame.draw.line(
                screen, 
                (60, 63, 70), 
                (GRID_OFFSET_X, GRID_OFFSET_Y + i * CELL_SIZE),
                (GRID_OFFSET_X + GRID_SIZE * CELL_SIZE, GRID_OFFSET_Y + i * CELL_SIZE),
                1
            )
            # Vertical lines
            pygame.draw.line(
                screen, 
                (60, 63, 70), 
                (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y),
                (GRID_OFFSET_X + i * CELL_SIZE, GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE),
                1
            )
        
        # Draw candies
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].draw(screen)
        
        # Draw selected candy highlight
        if self.selected_candy:
            row, col = self.selected_candy
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE and self.grid[row][col]:
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                pygame.draw.rect(screen, (255, 255, 255), (x, y, CELL_SIZE, CELL_SIZE), 3, border_radius=5)
        
        # Draw score
        score_text = font.render(f"Score: {self.score}", True, TEXT_COLOR)
        screen.blit(score_text, (20, 20))
        
        # Draw moves left
        moves_text = font.render(f"Moves: {self.moves_left}", True, TEXT_COLOR)
        moves_rect = moves_text.get_rect()
        moves_rect.right = SCREEN_WIDTH - 160
        moves_rect.top = 20
        screen.blit(moves_text, moves_rect)
        
        # Draw restart button (positioned next to moves text)
        self.restart_button.draw(screen)
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("Game Over!", True, TEXT_COLOR)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, game_over_rect)
            
            final_score_text = font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(final_score_text, final_score_rect)
            
            play_again_text = small_font.render("Click New Game to play again", True, TEXT_COLOR)
            play_again_rect = play_again_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(play_again_text, play_again_rect)
    
    def update(self):
        # Update all candies
        any_moving = False
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col]:
                    self.grid[row][col].update()
                    if self.grid[row][col].moving or self.grid[row][col].scale != self.grid[row][col].target_scale:
                        any_moving = True
        
        self.animations_running = any_moving
        
        # Update button
        mouse_pos = pygame.mouse.get_pos()
        self.restart_button.update(mouse_pos)
    
    def handle_click(self, pos):
        if self.game_over or self.animations_running:
            return
            
        # Check if click is on grid
        x, y = pos
        if (GRID_OFFSET_X <= x <= GRID_OFFSET_X + GRID_SIZE * CELL_SIZE and
            GRID_OFFSET_Y <= y <= GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE):
            
            col = (x - GRID_OFFSET_X) // CELL_SIZE
            row = (y - GRID_OFFSET_Y) // CELL_SIZE
            
            if self.selected_candy is None:
                self.selected_candy = (row, col)
            else:
                selected_row, selected_col = self.selected_candy
                
                # Check if adjacent
                if ((abs(selected_row - row) == 1 and selected_col == col) or
                    (abs(selected_col - col) == 1 and selected_row == row)):
                    
                    # Swap candies
                    self.swap_candies(selected_row, selected_col, row, col)
                    self.moves_left -= 1
                    
                    # Play swap sound
                    if swap_sound:
                        swap_sound.play()
                    
                    # Check if game over
                    if self.moves_left <= 0:
                        self.game_over = True
                        if game_over_sound:
                            game_over_sound.play()
                
                self.selected_candy = None
    
    def swap_candies(self, row1, col1, row2, col2):
        # Swap positions in grid
        self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
        
        # Update candy positions
        if self.grid[row1][col1]:
            self.grid[row1][col1].set_position(row1, col1)
        if self.grid[row2][col2]:
            self.grid[row2][col2].set_position(row2, col2)
        
        # Check for matches after swap
        matches = self.find_matches()
        if not matches:
            # Swap back if no matches
            self.grid[row1][col1], self.grid[row2][col2] = self.grid[row2][col2], self.grid[row1][col1]
            if self.grid[row1][col1]:
                self.grid[row1][col1].set_position(row1, col1)
            if self.grid[row2][col2]:
                self.grid[row2][col2].set_position(row2, col2)
            self.moves_left += 1  # Restore the move
        else:
            # Process matches
            self.process_matches(matches)
    
    def find_matches(self):
        matches = []
        
        # Check horizontal matches
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE - 2):
                if (self.grid[row][col] and self.grid[row][col+1] and self.grid[row][col+2] and
                    self.grid[row][col].color_index == self.grid[row][col+1].color_index == self.grid[row][col+2].color_index):
                    
                    # Find how long this match is
                    match_length = 3
                    while col + match_length < GRID_SIZE and self.grid[row][col + match_length] and self.grid[row][col + match_length].color_index == self.grid[row][col].color_index:
                        match_length += 1
                    
                    # Add all positions in this match
                    match = [(row, col + i) for i in range(match_length)]
                    matches.append(match)
                    
                    # Skip the matched candies to avoid counting them multiple times
                    col += match_length - 1
        
        # Check vertical matches
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE - 2):
                if (self.grid[row][col] and self.grid[row+1][col] and self.grid[row+2][col] and
                    self.grid[row][col].color_index == self.grid[row+1][col].color_index == self.grid[row+2][col].color_index):
                    
                    # Find how long this match is
                    match_length = 3
                    while row + match_length < GRID_SIZE and self.grid[row + match_length][col] and self.grid[row + match_length][col].color_index == self.grid[row][col].color_index:
                        match_length += 1
                    
                    # Add all positions in this match
                    match = [(row + i, col) for i in range(match_length)]
                    matches.append(match)
                    
                    # Skip the matched candies to avoid counting them multiple times
                    row += match_length - 1
        
        return matches
    
    def process_matches(self, matches):
        # Animate and remove matched candies
        matched_positions = set()
        for match in matches:
            for row, col in match:
                matched_positions.add((row, col))
                if self.grid[row][col]:
                    self.grid[row][col].animate_match()
        
        # Calculate score
        match_count = len(matched_positions)
        combo_bonus = len(matches) - 1 if len(matches) > 1 else 0
        points = match_count * MATCH_SCORE + combo_bonus * COMBO_BONUS
        self.score += points
        
        # Play match sound
        if match_sound:
            match_sound.play()
        
        # Wait for animations to complete
        pygame.time.delay(300)
        
        # Remove matched candies
        for row, col in matched_positions:
            self.grid[row][col] = None
        
        # Drop candies down
        self.drop_candies()
        
        # Fill empty spaces
        self.fill_empty_spaces()
        
        # Check for new matches
        new_matches = self.find_matches()
        if new_matches:
            self.process_matches(new_matches)
    
    def drop_candies(self):
        for col in range(GRID_SIZE):
            # Count empty spaces and move candies down
            for row in range(GRID_SIZE - 1, -1, -1):
                if self.grid[row][col] is None:
                    # Find the next candy above to drop down
                    for above_row in range(row - 1, -1, -1):
                        if self.grid[above_row][col]:
                            self.grid[row][col] = self.grid[above_row][col]
                            self.grid[above_row][col] = None
                            self.grid[row][col].set_position(row, col)
                            break
    
    def fill_empty_spaces(self):
        for col in range(GRID_SIZE):
            for row in range(GRID_SIZE):
                if self.grid[row][col] is None:
                    color_index = random.randint(0, len(CANDY_COLORS) - 1)
                    # Create new candy above the grid and let it fall
                    new_candy = Candy(row, col, color_index)
                    new_candy.y = GRID_OFFSET_Y - CELL_SIZE * (GRID_SIZE - row)
                    new_candy.target_y = GRID_OFFSET_Y + row * CELL_SIZE
                    self.grid[row][col] = new_candy
    
    def reset(self):
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.score = 0
        self.moves_left = MAX_MOVES
        self.selected_candy = None
        self.game_over = False
        self.animations_running = False
        self.fill_grid()

def main():
    game = Game()
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if game.restart_button.handle_event(event):
                        pass  # Button handles its own action
                    else:
                        game.handle_click(event.pos)
        
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
