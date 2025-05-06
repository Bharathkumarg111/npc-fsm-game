import pygame
import sys
import math

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("NPC FSM Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
TRANSPARENT_OVERLAY = (0, 0, 0, 128)  # 50% transparent background for the instructions
REPLAY_BUTTON_COLOR = (0, 255, 0)  # Green for the replay button

# Set font for instructions, game over, and replay button
font = pygame.font.SysFont(None, 30)
game_over_font = pygame.font.SysFont(None, 50)
button_font = pygame.font.SysFont(None, 40)

clock = pygame.time.Clock()

# Load images
player_image = pygame.image.load('assets/player.png')  # Ensure you have this file
npc_image = pygame.image.load('assets/npc.png')        # Ensure you have this file
sword_image = pygame.image.load('assets/sword.png')    # Sword image for player (optional)
dead_image = pygame.image.load('assets/dead.png')      # Dead image for NPC (ensure you have this file)

# Resize images (Optional, adjust to your needs)
player_image = pygame.transform.scale(player_image, (50, 100))  # Adjust size
npc_image = pygame.transform.scale(npc_image, (50, 100))        # Adjust size
sword_image = pygame.transform.scale(sword_image, (30, 60))      # Adjust size
dead_image = pygame.transform.scale(dead_image, (50, 100))      # Adjust size for dead NPC

class Player:
    def __init__(self):
        self.rect = player_image.get_rect()
        self.rect.x = 100
        self.rect.y = 300
        self.speed = 5
        self.sword_angle = 0  # Initial sword angle
        self.sword_rect = sword_image.get_rect()  # To hold the sword's position

    def move(self, keys):
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
        if keys[pygame.K_UP]:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.rect.y += self.speed

    def update_sword(self):
        # Update the sword's position based on player's position and movement
        self.sword_rect.center = (self.rect.x + 50, self.rect.y + 40)  # Position it beside the player

    def draw(self, win):
        # Draw player image
        win.blit(player_image, (self.rect.x, self.rect.y))
        
        # Draw sword beside the player
        rotated_sword = pygame.transform.rotate(sword_image, self.sword_angle)
        sword_rect = rotated_sword.get_rect(center=self.sword_rect.center)  # Position sword relative to player
        win.blit(rotated_sword, sword_rect)

class NPC:
    def __init__(self):
        self.rect = npc_image.get_rect()
        self.rect.x = 600
        self.rect.y = 300
        self.speed = 2
        self.state = "Patrolling"
        self.patrol_dir = 1
        self.patrol_range = (500, 700)
        self.health = 100
        self.cooldown = 0

    def distance_to(self, player):
        dx = self.rect.centerx - player.rect.centerx
        dy = self.rect.centery - player.rect.centery
        return math.hypot(dx, dy)

    def update(self, player):
        if self.health <= 0:
            self.state = "Dead"
        elif self.distance_to(player) < 50:
            self.state = "Attacking"
        elif self.distance_to(player) < 200:
            self.state = "Chasing"
        else:
            self.state = "Patrolling"

        if self.state == "Patrolling":
            self.rect.x += self.patrol_dir * self.speed
            if self.rect.x <= self.patrol_range[0] or self.rect.x >= self.patrol_range[1]:
                self.patrol_dir *= -1

        elif self.state == "Chasing":
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            distance = max(math.hypot(dx, dy), 1)
            self.rect.x += int(self.speed * dx / distance)
            self.rect.y += int(self.speed * dy / distance)

        elif self.state == "Attacking":
            if self.cooldown == 0:
                print("NPC is attacking the player!")
                self.cooldown = 60
            else:
                self.cooldown -= 1

    def draw(self, win):
        # Use dead image if the NPC is dead, else use normal image
        if self.state == "Dead":
            win.blit(dead_image, (self.rect.x, self.rect.y))  # Draw the dead NPC image
        else:
            win.blit(npc_image, (self.rect.x, self.rect.y))  # Draw normal NPC image

def draw_instructions():
    # Transparent background surface for instructions
    instructions_surface = pygame.Surface((WIDTH, 100), pygame.SRCALPHA)  # Smaller surface for instructions
    instructions_surface.fill(TRANSPARENT_OVERLAY)  # Fill with semi-transparent color

    # Render the instructions text
    instructions = font.render("Use arrows to control player", True, BLACK)
    instructions_surface.blit(instructions, (WIDTH // 2 - instructions.get_width() // 2, 10))

    attack_instr = font.render("Press SPACE to attack ", True, BLACK)
    instructions_surface.blit(attack_instr, (WIDTH // 2 - attack_instr.get_width() // 2, 40))

    # Blit the transparent background with instructions text onto the main window
    win.blit(instructions_surface, (0, 0))

def draw_game_over():
    # Game Over text
    game_over_text = game_over_font.render("GAME OVER", True, BLACK)
    win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    
    # Dead text
    dead_text = game_over_font.render("Devil is Dead!", True, BLACK)
    win.blit(dead_text, (WIDTH // 2 - dead_text.get_width() // 2, HEIGHT // 2))

def draw_replay_button():
    # Draw the Replay Button at the top
    button_text = button_font.render("Replay", True, BLACK)
    button_rect = pygame.Rect(WIDTH // 2 - 60, 20, 120, 40)  # Button position and size
    pygame.draw.rect(win, REPLAY_BUTTON_COLOR, button_rect)  # Draw button rectangle
    win.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2,
                           button_rect.y + (button_rect.height - button_text.get_height()) // 2))
    return button_rect

def main():
    player = Player()
    npc = NPC()

    while True:
        win.fill(WHITE)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if npc.state != "Dead":
                    # Check if sword is touching NPC's hitbox (simple overlap check)
                    if player.sword_rect.colliderect(npc.rect):
                        npc.health -= 25  # Damage NPC
                        print("NPC health:", npc.health)
                    player.sword_angle = 90  # Rotate sword to the right (attack)
            if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                player.sword_angle = 0  # Reset sword to original position

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if replay button was clicked
                button_rect = draw_replay_button()
                if button_rect.collidepoint(event.pos):
                    # Reset the game when replay button is clicked
                    if npc.state == "Dead":
                        player = Player()
                        npc = NPC()

        player.move(keys)
        player.update_sword()  # Update sword position as player moves
        npc.update(player)

        player.draw(win)
        npc.draw(win)

        # Draw instructions (with transparent background)
        if npc.state != "Dead":
            draw_instructions()

        # Check if NPC is dead and show "Game Over"
        if npc.state == "Dead":
            draw_game_over()
            # Draw replay button
            draw_replay_button()

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
