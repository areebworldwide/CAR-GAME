import pygame
import random
import json
import os
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (239, 68, 68)
BLUE = (59, 130, 246)
GREEN = (34, 197, 94)
GRAY = (55, 65, 81)
DARK_GRAY = (31, 41, 55)
YELLOW = (251, 191, 36)
LIGHT_BLUE = (96, 165, 250)

# Create window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Speed Racer - AreebWorldwide")
clock = pygame.time.Clock()

# Fonts
title_font = pygame.font.Font(None, 60)
large_font = pygame.font.Font(None, 48)
medium_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)
tiny_font = pygame.font.Font(None, 18)

# Game variables
class Car:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.speed = 7
        
    def draw(self, is_player=False):
        # Car body
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Car details
        detail_color = (30, 64, 175) if is_player else (75, 85, 99)
        pygame.draw.rect(screen, detail_color, (self.x + 5, self.y + 10, self.width - 10, self.height - 40))
        # Windows
        pygame.draw.rect(screen, LIGHT_BLUE, (self.x + 10, self.y + 15, self.width - 20, 20))
        # Wheels
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + 15, 8, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + 15, 8, 15))
        pygame.draw.rect(screen, BLACK, (self.x - 5, self.y + self.height - 30, 8, 15))
        pygame.draw.rect(screen, BLACK, (self.x + self.width - 3, self.y + self.height - 30, 8, 15))

class Game:
    def __init__(self):
        self.state = "menu"  # menu, playing, paused, gameover, history
        self.score = 0
        self.high_score = self.load_high_score()
        self.lives = 3
        self.speed = 5
        self.time = 0
        self.road_offset = 0
        self.player = Car(175, 450, 50, 80, RED)
        self.enemies = []
        self.last_enemy_spawn = 0
        self.last_speed_increase = 0
        self.invincible = False
        self.invincible_until = 0
        self.game_history = self.load_history()
        self.start_time = 0
        
    def load_high_score(self):
        try:
            if os.path.exists('high_score.txt'):
                with open('high_score.txt', 'r') as f:
                    return int(f.read())
        except:
            pass
        return 0
    
    def save_high_score(self):
        try:
            with open('high_score.txt', 'w') as f:
                f.write(str(self.high_score))
        except:
            pass
    
    def load_history(self):
        try:
            if os.path.exists('game_history.json'):
                with open('game_history.json', 'r') as f:
                    return json.load(f)
        except:
            pass
        return []
    
    def save_history(self):
        try:
            with open('game_history.json', 'w') as f:
                json.dump(self.game_history[:10], f)
        except:
            pass
    
    def reset_game(self):
        self.score = 0
        self.lives = 3
        self.speed = 5
        self.time = 0
        self.road_offset = 0
        self.player = Car(175, 450, 50, 80, RED)
        self.enemies = []
        self.last_enemy_spawn = 0
        self.last_speed_increase = 0
        self.invincible = False
        self.invincible_until = 0
        self.start_time = pygame.time.get_ticks()
        
    def spawn_enemy(self):
        lanes = [75, 175, 275]
        lane = random.choice(lanes)
        enemy = Car(lane, -100, 50, 80, BLUE)
        enemy.speed = self.speed + random.uniform(0, 2)
        self.enemies.append(enemy)
    
    def check_collision(self, rect1, rect2):
        return (rect1.x < rect2.x + rect2.width and
                rect1.x + rect1.width > rect2.x and
                rect1.y < rect2.y + rect2.height and
                rect1.y + rect1.height > rect2.y)
    
    def draw_road(self):
        # Grass
        screen.fill(GREEN)
        # Road
        pygame.draw.rect(screen, GRAY, (50, 0, 300, SCREEN_HEIGHT))
        # Road edges
        pygame.draw.rect(screen, WHITE, (50, 0, 5, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, (345, 0, 5, SCREEN_HEIGHT))
        
        # Lane markings
        marking_height = 40
        marking_gap = 30
        for i in range(-marking_height, SCREEN_HEIGHT + marking_height, marking_height + marking_gap):
            y = (i + self.road_offset) % (SCREEN_HEIGHT + marking_height + marking_gap)
            pygame.draw.rect(screen, YELLOW, (148, y, 4, marking_height))
            pygame.draw.rect(screen, YELLOW, (248, y, 4, marking_height))
    
    def draw_button(self, text, x, y, width, height, color, hover_color):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        if x < mouse[0] < x + width and y < mouse[1] < y + height:
            pygame.draw.rect(screen, hover_color, (x, y, width, height), border_radius=10)
            if click[0]:
                return True
        else:
            pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
        
        text_surf = small_font.render(text, True, WHITE)
        text_rect = text_surf.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(text_surf, text_rect)
        return False
    
    def format_time(self, seconds):
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins}:{secs:02d}"
    
    def draw_menu(self):
        screen.fill(DARK_GRAY)
        
        # Title
        title = title_font.render("Speed Racer", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Car emoji
        car_text = large_font.render("🏎️", True, WHITE)
        car_rect = car_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(car_text, car_rect)
        
        # Instructions
        inst1 = small_font.render("Arrow Keys to control", True, (200, 200, 200))
        inst2 = small_font.render("Avoid traffic & survive!", True, (200, 200, 200))
        screen.blit(inst1, (SCREEN_WIDTH // 2 - inst1.get_width() // 2, 220))
        screen.blit(inst2, (SCREEN_WIDTH // 2 - inst2.get_width() // 2, 250))
        
        # Start button
        if self.draw_button("START RACE", 100, 320, 200, 60, RED, (220, 38, 38)):
            self.reset_game()
            self.state = "playing"
        
        # History button
        if self.draw_button("HISTORY", 100, 400, 200, 50, (147, 51, 234), (126, 34, 206)):
            self.state = "history"
        
        # High score
        if self.high_score > 0:
            hs_text = medium_font.render(f"🏆 High Score: {self.high_score}", True, YELLOW)
            hs_rect = hs_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
            screen.blit(hs_text, hs_rect)
        
        # Credit
        credit = medium_font.render("AreebWorldwide", True, (100, 150, 255))
        credit_rect = credit.get_rect(center=(SCREEN_WIDTH // 2, 560))
        screen.blit(credit, credit_rect)
        
        dev_text = tiny_font.render("Game Developer", True, (150, 150, 150))
        dev_rect = dev_text.get_rect(center=(SCREEN_WIDTH // 2, 585))
        screen.blit(dev_text, dev_rect)
    
    def draw_history(self):
        screen.fill(DARK_GRAY)
        
        # Title
        title = large_font.render("Game History", True, WHITE)
        screen.blit(title, (50, 30))
        
        # Back button
        if self.draw_button("BACK", 20, 20, 80, 40, GRAY, (75, 85, 99)):
            self.state = "menu"
        
        # History list
        y = 100
        if not self.game_history:
            no_games = small_font.render("No games played yet", True, (150, 150, 150))
            screen.blit(no_games, (SCREEN_WIDTH // 2 - no_games.get_width() // 2, 250))
        else:
            for i, game in enumerate(self.game_history[:10]):
                pygame.draw.rect(screen, GRAY, (30, y, 340, 60), border_radius=5)
                
                rank = small_font.render(f"#{i + 1}", True, YELLOW)
                screen.blit(rank, (45, y + 10))
                
                score_text = medium_font.render(f"{game['score']} pts", True, WHITE)
                screen.blit(score_text, (120, y + 8))
                
                time_text = tiny_font.render(f"Time: {self.format_time(game['time'])} • {game['date']}", True, (180, 180, 180))
                screen.blit(time_text, (45, y + 38))
                
                y += 70
                if y > SCREEN_HEIGHT - 100:
                    break
    
    def draw_playing(self):
        self.draw_road()
        
        # Draw player (with invincibility flashing)
        current_time = pygame.time.get_ticks()
        if self.invincible and current_time < self.invincible_until:
            if (current_time // 100) % 2 == 0:
                self.player.draw(True)
        else:
            self.invincible = False
            self.player.draw(True)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw()
        
        # Draw HUD
        self.draw_hud()
    
    def draw_hud(self):
        # Top bar background
        pygame.draw.rect(screen, (0, 0, 0, 180), (0, 0, SCREEN_WIDTH, 80))
        
        # Score
        score_text = small_font.render(f"Score: {self.score}", True, YELLOW)
        screen.blit(score_text, (10, 10))
        
        # Speed
        speed_text = small_font.render(f"Speed: {self.speed:.1f}x", True, LIGHT_BLUE)
        screen.blit(speed_text, (10, 35))
        
        # Time
        time_text = small_font.render(f"Time: {self.format_time(self.time)}", True, GREEN)
        screen.blit(time_text, (SCREEN_WIDTH - 120, 10))
        
        # Lives
        for i in range(3):
            if i < self.lives:
                pygame.draw.circle(screen, RED, (SCREEN_WIDTH - 90 + i * 30, 50), 10)
            else:
                pygame.draw.circle(screen, (80, 80, 80), (SCREEN_WIDTH - 90 + i * 30, 50), 10)
        
        # High Score
        if self.high_score > 0:
            hs_text = tiny_font.render(f"🏆 {self.high_score}", True, YELLOW)
            screen.blit(hs_text, (10, 58))
        
        # Pause hint
        pause_hint = tiny_font.render("P: Pause", True, (150, 150, 150))
        screen.blit(pause_hint, (SCREEN_WIDTH // 2 - pause_hint.get_width() // 2, 58))
    
    def draw_paused(self):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Title
        title = large_font.render("⏸️ PAUSED", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        
        # Stats
        score_text = medium_font.render(f"Score: {self.score}", True, WHITE)
        time_text = small_font.render(f"Time: {self.format_time(self.time)}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 220))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 270))
        
        # Buttons
        if self.draw_button("RESUME", 75, 330, 250, 60, GREEN, (34, 197, 94)):
            self.state = "playing"
        
        if self.draw_button("MAIN MENU", 75, 410, 250, 50, RED, (220, 38, 38)):
            self.state = "menu"
    
    def draw_gameover(self):
        screen.fill(DARK_GRAY)
        
        # Title
        title = large_font.render("Game Over!", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        
        # Stats
        score_text = medium_font.render(f"Final Score: {self.score}", True, WHITE)
        time_text = small_font.render(f"Time: {self.format_time(self.time)}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 180))
        screen.blit(time_text, (SCREEN_WIDTH // 2 - time_text.get_width() // 2, 230))
        
        # High score notification
        if self.score == self.high_score and self.score > 0:
            new_hs = medium_font.render("🎉 New High Score!", True, YELLOW)
            screen.blit(new_hs, (SCREEN_WIDTH // 2 - new_hs.get_width() // 2, 270))
        elif self.high_score > 0:
            hs_text = small_font.render(f"High Score: {self.high_score}", True, (180, 180, 180))
            screen.blit(hs_text, (SCREEN_WIDTH // 2 - hs_text.get_width() // 2, 270))
        
        # Play again button
        if self.draw_button("PLAY AGAIN", 75, 340, 250, 60, BLUE, (37, 99, 235)):
            self.reset_game()
            self.state = "playing"
        
        # Menu button
        if self.draw_button("MAIN MENU", 75, 420, 250, 50, GRAY, (75, 85, 99)):
            self.state = "menu"
        
        # Credit
        credit = medium_font.render("AreebWorldwide", True, (100, 150, 255))
        credit_rect = credit.get_rect(center=(SCREEN_WIDTH // 2, 540))
        screen.blit(credit, credit_rect)
    
    def update(self):
        if self.state != "playing":
            return
        
        # Update time
        current_time = pygame.time.get_ticks()
        self.time = (current_time - self.start_time) // 1000
        
        # Move road
        self.road_offset += self.speed
        if self.road_offset > 70:
            self.road_offset = 0
        
        # Spawn enemies
        if current_time - self.last_enemy_spawn > 1500 - (self.speed * 50):
            self.spawn_enemy()
            self.last_enemy_spawn = current_time
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.y += enemy.speed
            
            # Check collision
            if not self.invincible and self.check_collision(self.player, enemy):
                self.invincible = True
                self.invincible_until = current_time + 2000
                self.lives -= 1
                self.enemies.remove(enemy)
                
                if self.lives <= 0:
                    # Save game data
                    game_data = {
                        'score': self.score,
                        'time': self.time,
                        'date': datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    self.game_history.insert(0, game_data)
                    self.game_history = self.game_history[:10]
                    self.save_history()
                    
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                    
                    self.state = "gameover"
            
            # Remove if off screen and add score
            elif enemy.y > SCREEN_HEIGHT:
                self.enemies.remove(enemy)
                self.score += 10
        
        # Increase difficulty
        if current_time - self.last_speed_increase > 10000:
            self.speed = min(self.speed + 0.5, 12)
            self.last_speed_increase = current_time

# Create game instance
game = Game()

# Main game loop
running = True
while running:
    clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Keyboard controls
        if event.type == pygame.KEYDOWN:
            if game.state == "playing":
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    game.state = "paused"
            elif game.state == "paused":
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    game.state = "playing"
    
    # Handle continuous key presses for movement
    if game.state == "playing":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and game.player.x > 75:
            game.player.x -= game.player.speed
        if keys[pygame.K_RIGHT] and game.player.x < 275:
            game.player.x += game.player.speed
        if keys[pygame.K_UP] and game.player.y > 300:
            game.player.y -= game.player.speed
        if keys[pygame.K_DOWN] and game.player.y < 500:
            game.player.y += game.player.speed
    
    # Update game logic
    game.update()
    
    # Draw based on state
    if game.state == "menu":
        game.draw_menu()
    elif game.state == "history":
        game.draw_history()
    elif game.state == "playing":
        game.draw_playing()
    elif game.state == "paused":
        game.draw_playing()
        game.draw_paused()
    elif game.state == "gameover":
        game.draw_gameover()
    
    pygame.display.flip()

pygame.quit()