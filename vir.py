import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GRAVITY = .8
FRICTION = 0.85
BOUNCE_DAMPING = 0.7

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 100, 255)
RED = (255, 100, 100)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)

class Player:
    def __init__(self, x, y, color, controls):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 60
        self.color = color
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.controls = controls
        self.jump_power = -18
        self.speed = 8
        self.push_force = 12
        self.push_cooldown = 0
        
    def update(self, keys, other_player=None):
        # Handle input
        if keys[self.controls['left']]:
            self.vel_x = -self.speed
        elif keys[self.controls['right']]:
            self.vel_x = self.speed
        else:
            self.vel_x *= FRICTION
            
        if keys[self.controls['jump']] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
            
        # Handle push ability
        if self.push_cooldown > 0:
            self.push_cooldown -= 1
            
        if keys[self.controls['push']] and self.push_cooldown == 0 and other_player:
            self.push_player(other_player)
            self.push_cooldown = 30  # 0.5 second cooldown at 60 FPS
            
        # Apply gravity
        if not self.on_ground:
            self.vel_y += GRAVITY
            
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Ground collision
        if self.y + self.height >= SCREEN_HEIGHT - 20:
            self.y = SCREEN_HEIGHT - 20 - self.height
            self.vel_y = 0
            self.on_ground = True
            
        # Screen boundaries
        if self.x < 0:
            self.x = 0
        elif self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width
            
    def push_player(self, other_player):
        # Calculate direction to other player
        dx = other_player.x + other_player.width // 2 - (self.x + self.width // 2)
        dy = other_player.y + other_player.height // 2 - (self.y + self.height // 2)
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Only push if players are close enough
        if distance < 80 and distance > 0:
            # Normalize direction and apply push force
            nx = dx / distance
            ny = dy / distance
            
            other_player.vel_x += nx * self.push_force
            other_player.vel_y += ny * self.push_force
            
            # If pushed upward, player is no longer on ground
            if ny < 0:
                other_player.on_ground = False
            
    def collide_with_player(self, other_player):
        # Simple rectangle collision
        if (self.x < other_player.x + other_player.width and
            self.x + self.width > other_player.x and
            self.y < other_player.y + other_player.height and
            self.y + self.height > other_player.y):
            
            # Calculate overlap and separate players
            overlap_x = min(self.x + self.width - other_player.x, 
                           other_player.x + other_player.width - self.x)
            
            # Separate players based on who's moving toward whom
            if self.x < other_player.x:
                # Self is on the left, move both apart
                self.x -= overlap_x // 2
                other_player.x += overlap_x // 2
            else:
                # Self is on the right, move both apart
                self.x += overlap_x // 2
                other_player.x -= overlap_x // 2
                
            # Exchange some velocity (bounce off each other)
            temp_vel = self.vel_x
            self.vel_x = other_player.vel_x * 0.5
            other_player.vel_x = temp_vel * 0.5
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Draw simple face
        pygame.draw.circle(screen, BLACK, (int(self.x + 15), int(self.y + 15)), 2)
        pygame.draw.circle(screen, BLACK, (int(self.x + 15), int(self.y + 25)), 2)
        
        # Draw push cooldown indicator
        if self.push_cooldown > 0:
            cooldown_bar_width = 20
            cooldown_progress = (30 - self.push_cooldown) / 30
            pygame.draw.rect(screen, RED, (self.x + 5, self.y - 8, cooldown_bar_width, 4))
            pygame.draw.rect(screen, GREEN, (self.x + 5, self.y - 8, cooldown_bar_width * cooldown_progress, 4))

class Ball:
    def __init__(self, x, y, ball_type="regular"):
        self.x = x
        self.y = y
        self.radius = 15
        self.vel_x = random.choice([-5, 5])
        self.vel_y = -8
        self.floor_bounces = 0  # Track how many times ball has bounced off floor
        self.max_floor_bounces = 1  # Ball can bounce once before being removed
        
        # Ball type and properties
        self.ball_type = ball_type
        self.setup_ball_type()
        
    def setup_ball_type(self):
        if self.ball_type == "regular":
            self.color = WHITE
            self.physics_multiplier = 1.0
        elif self.ball_type == "bomb":
            self.color = (255, 100, 0)  # Orange/red
            self.physics_multiplier = 1.0
        elif self.ball_type == "quick":
            self.color = (255, 255, 0)  # Yellow
            self.physics_multiplier = 2.0  # Faster physics
        elif self.ball_type == "slow":
            self.color = (100, 100, 255)  # Light blue
            self.physics_multiplier = 0.5  # Slower physics
        
    def update(self):
        # Apply gravity with physics multiplier
        gravity_effect = GRAVITY * 0.5 * self.physics_multiplier
        self.vel_y += gravity_effect
        
        # Update position with physics multiplier
        self.x += self.vel_x * self.physics_multiplier
        self.y += self.vel_y * self.physics_multiplier
        
        # Screen boundaries
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.vel_x *= -BOUNCE_DAMPING
            if self.x - self.radius <= 0:
                self.x = self.radius
            else:
                self.x = SCREEN_WIDTH - self.radius
                
        # Ground collision with bounce tracking
        if self.y + self.radius >= SCREEN_HEIGHT - 20:
            self.y = SCREEN_HEIGHT - 20 - self.radius
            
            # Only bounce if we haven't used up our bounces AND we're moving downward
            if self.floor_bounces < self.max_floor_bounces and self.vel_y > 0:
                # Bounce off floor like normal (flip velocity)
                self.vel_y = -self.vel_y * 0.8  # Normal bounce with slight energy loss
                self.floor_bounces += 1
            elif self.vel_y > 0:
                # Stop the ball if it has no bounces left
                self.vel_y = 0
                self.vel_x *= 0.8
            
    def collide_with_player(self, player):
        # Simple circle-rectangle collision
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                               self.radius * 2, self.radius * 2)
        player_rect = player.get_rect()
        
        if ball_rect.colliderect(player_rect):
            # Calculate bounce direction based on hit position
            hit_pos = (self.x - (player.x + player.width // 2)) / (player.width // 2)
            
            # Bounce ball away from player
            self.vel_x = hit_pos * 8 + player.vel_x * 0.3
            self.vel_y = min(self.vel_y, -8)  # Always bounce up
            
            # Move ball out of player
            if self.x < player.x + player.width // 2:
                self.x = player.x - self.radius
            else:
                self.x = player.x + player.width + self.radius
                
    def collide_with_net(self, net_x, net_width, net_height):
        # Check collision with net
        if (self.x + self.radius > net_x and 
            self.x - self.radius < net_x + net_width and
            self.y + self.radius > SCREEN_HEIGHT - net_height - 20):
            
            # Bounce off net
            if self.x < net_x + net_width // 2:
                self.x = net_x - self.radius
                self.vel_x = abs(self.vel_x) * -1
            else:
                self.x = net_x + net_width + self.radius
                self.vel_x = abs(self.vel_x)
                
    def collide_with_ball(self, other_ball):
        # Calculate distance between ball centers
        dx = other_ball.x - self.x
        dy = other_ball.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Check if balls are colliding
        if distance < self.radius + other_ball.radius and distance > 0:
            # Normalize the collision vector
            nx = dx / distance
            ny = dy / distance
            
            # Separate overlapping balls first
            overlap = self.radius + other_ball.radius - distance
            separation = overlap / 2 + 1  # Add 1 pixel buffer
            
            self.x -= separation * nx
            self.y -= separation * ny
            other_ball.x += separation * nx
            other_ball.y += separation * ny
            
            # Calculate relative velocity
            rel_vel_x = other_ball.vel_x - self.vel_x
            rel_vel_y = other_ball.vel_y - self.vel_y
            
            # Calculate relative velocity in collision normal direction
            speed = rel_vel_x * nx + rel_vel_y * ny
            
            # Only resolve if balls are moving towards each other
            if speed > 0:
                return
                
            # Apply collision response (elastic collision)
            impulse = 2 * speed / 2  # Assuming equal mass
            
            # Update velocities
            self.vel_x += impulse * nx
            self.vel_y += impulse * ny
            other_ball.vel_x -= impulse * nx
            other_ball.vel_y -= impulse * ny
        
    def reset(self, x, y, ball_type="regular"):
        self.x = x
        self.y = y
        self.vel_x = random.choice([-5, 5])
        self.vel_y = -8
        self.floor_bounces = 0  # Reset bounce counter
        self.ball_type = ball_type
        self.setup_ball_type()
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw ball type indicator
        if self.ball_type == "bomb":
            # Draw explosion symbol
            pygame.draw.line(screen, RED, (int(self.x - 5), int(self.y)), (int(self.x + 5), int(self.y)), 2)
            pygame.draw.line(screen, RED, (int(self.x), int(self.y - 5)), (int(self.x), int(self.y + 5)), 2)
        elif self.ball_type == "quick":
            # Draw speed lines
            pygame.draw.line(screen, BLACK, (int(self.x - 8), int(self.y - 3)), (int(self.x - 4), int(self.y - 3)), 2)
            pygame.draw.line(screen, BLACK, (int(self.x - 8), int(self.y + 3)), (int(self.x - 4), int(self.y + 3)), 2)
        elif self.ball_type == "slow":
            # Draw ZZZ for sleep
            font = pygame.font.Font(None, 12)
            zzz_text = font.render("Z", True, BLACK)
            screen.blit(zzz_text, (int(self.x + 8), int(self.y - 8)))

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("2-Player Volleyball")
        self.clock = pygame.time.Clock()
        
        # Create players
        player1_controls = {
            'left': pygame.K_a,
            'right': pygame.K_d,
            'jump': pygame.K_w,
            'push': pygame.K_e
        }
        player2_controls = {
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'jump': pygame.K_UP,
            'push': pygame.K_p
        }
        
        self.player1 = Player(100, SCREEN_HEIGHT - 100, BLUE, player1_controls)
        self.player2 = Player(SCREEN_WIDTH - 130, SCREEN_HEIGHT - 100, RED, player2_controls)
        
        # Create balls list
        self.balls = [Ball(SCREEN_WIDTH // 2, 200)]
        
        # Net properties
        self.net_x = SCREEN_WIDTH // 2 - 5
        self.net_width = 10
        self.net_height = 100
        
        # Score
        self.score1 = 0
        self.score2 = 0
        self.font = pygame.font.Font(None, 48)
        
        # Game state
        self.serving = 1  # 1 for player 1, 2 for player 2
        self.total_points = 0  # Track total points for adding balls
        
        # Visual effects
        self.explosions = []  # List to store active explosions
        
    def create_random_ball(self, x, y):
        ball_types = ["regular", "bomb", "quick", "slow"]
        ball_type = random.choice(ball_types)
        return Ball(x, y, ball_type)
    
    def create_shockwave(self, bomb_x, bomb_y):
        # Apply shockwave effect to all other balls and players, store knockback vectors
        shockwave_radius = 600  # Massive explosion range (doubled again)
        shockwave_force = 40  # Much stronger force for balls
        player_force = 30  # Much stronger force for players
        knockback_lines = []
        
        # Affect other balls
        for ball in self.balls:
            if ball.x == bomb_x and ball.y == bomb_y:
                continue  # Skip the bomb ball itself
                
            # Calculate distance from bomb
            dx = ball.x - bomb_x
            dy = ball.y - bomb_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < shockwave_radius and distance > 0:
                # Apply force proportional to distance (closer = stronger)
                force_multiplier = (shockwave_radius - distance) / shockwave_radius
                force = shockwave_force * force_multiplier
                
                # Normalize direction and apply force
                nx = dx / distance
                ny = dy / distance
                
                # Store knockback line for visual effect
                knockback_lines.append({
                    'start_x': bomb_x,
                    'start_y': bomb_y,
                    'end_x': ball.x,
                    'end_y': ball.y,
                    'force': force,
                    'type': 'ball'
                })
                
                ball.vel_x += nx * force
                ball.vel_y += ny * force
        
        # Affect players
        for player in [self.player1, self.player2]:
            # Calculate distance from bomb to player center
            player_center_x = player.x + player.width // 2
            player_center_y = player.y + player.height // 2
            
            dx = player_center_x - bomb_x
            dy = player_center_y - bomb_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < shockwave_radius and distance > 0:
                # Apply force proportional to distance (closer = stronger)
                force_multiplier = (shockwave_radius - distance) / shockwave_radius
                force = player_force * force_multiplier
                
                # Normalize direction and apply force
                nx = dx / distance
                ny = dy / distance
                
                # Store knockback line for visual effect
                knockback_lines.append({
                    'start_x': bomb_x,
                    'start_y': bomb_y,
                    'end_x': player_center_x,
                    'end_y': player_center_y,
                    'force': force,
                    'type': 'player'
                })
                
                # Apply force to player
                player.vel_x += nx * force
                player.vel_y += ny * force
                
                # If player gets launched upward, they're no longer on ground
                if ny < 0:  # Upward force
                    player.on_ground = False
        
        # Add explosion visual effect with knockback lines
        self.explosions.append({
            'x': bomb_x,
            'y': bomb_y,
            'radius': 0,
            'max_radius': 600,  # Match the massive shockwave radius
            'timer': 30,  # Duration in frames
            'knockback_lines': knockback_lines
        })
        
    def check_point(self):
        # Check balls that have used all bounces and are on ground
        balls_to_remove = []
        point_scored = False
        bomb_positions = []  # Store positions of bomb balls for shockwave
        
        for i, ball in enumerate(self.balls):
            # Remove ball if it has used all floor bounces and is touching ground
            if (ball.y + ball.radius >= SCREEN_HEIGHT - 20 and 
                ball.floor_bounces >= ball.max_floor_bounces and
                abs(ball.vel_y) < 1):  # Make sure ball is settled on ground
                
                # Store bomb position for shockwave
                if ball.ball_type == "bomb":
                    bomb_positions.append((ball.x, ball.y))
                
                if ball.x < SCREEN_WIDTH // 2:
                    # Point for player 2
                    self.score2 += 1
                    self.serving = 2
                else:
                    # Point for player 1
                    self.score1 += 1
                    self.serving = 1
                
                balls_to_remove.append(i)
                point_scored = True
                self.total_points += 1
        
        # Remove balls that have bounced max times
        for i in reversed(balls_to_remove):
            del self.balls[i]
            
        # Create shockwaves from bomb balls
        for bomb_x, bomb_y in bomb_positions:
            self.create_shockwave(bomb_x, bomb_y)
            
        # Add new ball when point is scored (if no balls left, always add one)
        if point_scored or len(self.balls) == 0:
            if self.serving == 1:
                new_ball = self.create_random_ball(200, 300)
            else:
                new_ball = self.create_random_ball(SCREEN_WIDTH - 200, 300)
            self.balls.append(new_ball)
            
        # Add extra ball every 5 total points (capped at 6 balls)
        if (self.total_points > 0 and self.total_points % 5 == 0 and 
            point_scored and len(self.balls) < 6):
            # Add ball from random side
            if random.choice([True, False]):
                extra_ball = self.create_random_ball(150 + random.randint(0, 100), 200 + random.randint(0, 100))
            else:
                extra_ball = self.create_random_ball(SCREEN_WIDTH - 250 + random.randint(0, 100), 200 + random.randint(0, 100))
            self.balls.append(extra_ball)
            
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Update players with push ability
        self.player1.update(keys, self.player2)
        self.player2.update(keys, self.player1)
        
        # Check player-to-player collision
        self.player1.collide_with_player(self.player2)
        
        # Update all balls
        for ball in self.balls:
            ball.update()
            
            # Check collisions with players
            ball.collide_with_player(self.player1)
            ball.collide_with_player(self.player2)
            ball.collide_with_net(self.net_x, self.net_width, self.net_height)
        
        # Check ball-to-ball collisions
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                self.balls[i].collide_with_ball(self.balls[j])
        
        # Update explosions
        self.explosions = [exp for exp in self.explosions if self.update_explosion(exp)]
        
        # Check for points
        self.check_point()
        
    def update_explosion(self, explosion):
        # Expand explosion radius
        explosion['radius'] += explosion['max_radius'] / 30  # Expand over 30 frames
        explosion['timer'] -= 1
        
        # Remove explosion when timer runs out
        return explosion['timer'] > 0
        
    def draw(self):
        # Clear screen
        self.screen.fill(GREEN)
        
        # Draw court
        pygame.draw.rect(self.screen, BROWN, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
        
        # Draw center line
        pygame.draw.line(self.screen, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20), 
                        (SCREEN_WIDTH // 2, SCREEN_HEIGHT), 3)
        
        # Draw net
        pygame.draw.rect(self.screen, GRAY, 
                        (self.net_x, SCREEN_HEIGHT - self.net_height - 20, 
                         self.net_width, self.net_height))
        
        # Draw net pattern
        for i in range(0, self.net_height, 10):
            for j in range(0, self.net_width, 5):
                if (i + j) % 20 == 0:
                    pygame.draw.rect(self.screen, WHITE,
                                   (self.net_x + j, SCREEN_HEIGHT - self.net_height - 20 + i, 2, 2))
        
        # Draw players
        self.player1.draw(self.screen)
        self.player2.draw(self.screen)
        
        # Draw all balls
        for ball in self.balls:
            ball.draw(self.screen)
            
        # Draw explosions
        for explosion in self.explosions:
            # Draw knockback force lines
            if 'knockback_lines' in explosion:
                line_alpha = int(255 * (explosion['timer'] / 30))
                for line in explosion['knockback_lines']:
                    # Different colors for different target types
                    if line.get('type') == 'player':
                        line_color = (255, 100, 100)  # Reddish for players
                    else:
                        line_color = (255, min(255, line_alpha), 0)  # Orange/yellow for balls
                    
                    line_thickness = max(1, int(line['force'] / 3))  # Thicker lines for stronger forces
                    
                    pygame.draw.line(self.screen, line_color,
                                   (int(line['start_x']), int(line['start_y'])),
                                   (int(line['end_x']), int(line['end_y'])),
                                   line_thickness)
                    
                    # Draw small explosion burst at target locations
                    pygame.draw.circle(self.screen, line_color,
                                     (int(line['end_x']), int(line['end_y'])), 5)
            
            # Draw expanding shockwave circles
            alpha = int(255 * (explosion['timer'] / 30))  # Fade out over time
            
            # Create multiple rings for visual effect
            for ring in range(2):
                ring_radius = explosion['radius'] - ring * 25
                if ring_radius > 0:
                    # Draw explosion ring
                    ring_alpha = max(0, alpha - ring * 100)
                    if ring_alpha > 0:
                        explosion_color = (255, min(255, ring_alpha), 0)  # Orange to yellow
                        
                        # Draw the explosion ring
                        if ring_radius < explosion['max_radius']:
                            pygame.draw.circle(self.screen, explosion_color, 
                                             (int(explosion['x']), int(explosion['y'])), 
                                             int(ring_radius), 4)
        
        # Draw score
        score_text = self.font.render(f"{self.score1} - {self.score2}", True, BLACK)
        text_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(score_text, text_rect)
        
        # Draw ball count
        ball_count_font = pygame.font.Font(None, 24)
        ball_text = ball_count_font.render(f"Balls: {len(self.balls)}", True, BLACK)
        self.screen.blit(ball_text, (SCREEN_WIDTH // 2 - 30, 80))
        
        # Draw total points (for tracking when new balls are added)
        points_text = ball_count_font.render(f"Total Points: {self.total_points}", True, BLACK)
        self.screen.blit(points_text, (SCREEN_WIDTH // 2 - 50, 100))
        
        # Draw controls
        controls_font = pygame.font.Font(None, 24)
        p1_text = controls_font.render("Player 1: W/A/D/E", True, BLUE)
        p2_text = controls_font.render("Player 2: Arrows/P", True, RED)
        self.screen.blit(p1_text, (10, 10))
        self.screen.blit(p2_text, (SCREEN_WIDTH - 150, 10))
        
        # Draw new ball notification
        if self.total_points > 0 and self.total_points % 5 == 0:
            new_ball_text = controls_font.render("NEW BALL ADDED!", True, YELLOW)
            new_ball_rect = new_ball_text.get_rect(center=(SCREEN_WIDTH // 2, 130))
            pygame.draw.rect(self.screen, BLACK, new_ball_rect.inflate(10, 5))
            self.screen.blit(new_ball_text, new_ball_rect)
        
        pygame.display.flip()
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # Reset game
                        self.score1 = 0
                        self.score2 = 0
                        self.total_points = 0
                        self.balls = [self.create_random_ball(SCREEN_WIDTH // 2, 200)]
                        self.serving = 1
                        
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
