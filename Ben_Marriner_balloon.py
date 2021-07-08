import sys
import pygame  # Using version 2.0.0
import random
from pygame.constants import K_DOWN, K_ESCAPE, K_SPACE, K_UP

RES = WIDTH, HEIGHT = 640, 480
SPRITE_SIZE = 64
FPS = 60

BACKGROUND_COLOUR = (255, 255, 255)
pygame.init()
window = pygame.display.set_mode(RES)

# Initialise font
FONT_SIZE = 30
pygame.font.init()
font = pygame.font.SysFont("Calibri", FONT_SIZE)

# Initialise a clock for the game
clock = pygame.time.Clock()

BALLOON_IMAGE = pygame.image.load("Resources\\Balloon_Placeholder.png")
PLAYER_IMAGE = pygame.image.load('Resources\\Player_Placeholder.png')
BULLET_IMAGE = pygame.image.load('Resources\\Bullet_Placeholder.png')

# Game object boundaries
LBOUNDARY = 0
RBOUNDARY = WIDTH - SPRITE_SIZE
TBOUNDARY = 0
BBOUNDARY = HEIGHT - SPRITE_SIZE

# Game object stats
PLAYER_MOVE_SPEED = 10
BALLOON_MOVE_SPEED = 10
BULLET_VELOCITY = -(10 * BALLOON_MOVE_SPEED)

# Change direction interval range for balloon
BALLOON_CHANGE_DIRECTION_INTERVAL_MIN = 0.25
BALLOON_CHANGE_DIRECTION_INTERVAL_MAX = 1

# True when the escape button is pressed
quit_requested = False

# Define base class for all game objects (i.e.: Player, balloon, bullet)
class GameObject(pygame.sprite.Sprite):

    def __init__(self, image, pos, move_speed) -> None:
        
        super().__init__()
        
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.move_speed = move_speed

    def detect_collisions(self):
        # left and right boundaries
        if self.rect.x < LBOUNDARY: self.rect.x = LBOUNDARY
        elif self.rect.y > RBOUNDARY: self.rect.y = RBOUNDARY

        # top and bottom boundaries
        if self.rect.y < TBOUNDARY: self.rect.y = TBOUNDARY
        elif self.rect.y > BBOUNDARY: self.rect.y = BBOUNDARY

    def update(self):
        self.detect_collisions()



# Player class
class Player(GameObject):

    def __init__(self, image=PLAYER_IMAGE, pos=(620, HEIGHT / 2), move_speed=PLAYER_MOVE_SPEED) -> None:
        
        super().__init__(image, pos, move_speed)
       
        # This boolean will prevent the player from rapidly firing bullets due to the shoot() function being called for every frame the fire button is pressed
        self.has_fired = False

        # Missed shots counter
        self.missed_shots = 0

    def handle_input(self):
        
        pressed_keys = pygame.key.get_pressed()
        
        # Move player up
        if pressed_keys[K_UP]:
            self.rect.y -= 10
        
        # Move player down
        if pressed_keys[K_DOWN]:
            self.rect.y += 10
        
        # Shoot bullet
        if pressed_keys[K_SPACE]:
            
            if not self.has_fired:

                self.shoot()
                self.has_fired = True

        else:
            self.has_fired = False
                
        # Quit game
        if pressed_keys[K_ESCAPE]:
            quit_requested = True
    
    def shoot(self):
        bullets.append(Bullet(pos=(self.rect.left, self.rect.top)))


# Bullet class
class Bullet(GameObject):

    def __init__(self, image=BULLET_IMAGE, pos=(0,0), move_speed=BULLET_VELOCITY) -> None:
        
        super().__init__(image, pos, move_speed)

    def update(self):
        
        super(Bullet, self).update()
        
        self.rect.x += self.move_speed

    def detect_collisions(self):
        
        super(Bullet, self).detect_collisions()

        # If the bullet has reached the end of the screen, delete the bullet from the game
        if self.rect.x == 0:
            player.missed_shots += 1
            bullets.remove(self)
            self.kill()


# Balloon class
class Balloon(GameObject):

    def __init__(self, image=BALLOON_IMAGE, pos=(50, random.randint(0, HEIGHT)), move_speed=BALLOON_MOVE_SPEED) -> None:
        
        super().__init__(image, pos, move_speed)
        self.balloon_hit = False
        # False = down, True = Up. Upon game starting, the balloon will choose at random to move up or down
        self.move_direction = random.choice([True, False])
        # The interval at which the direction of the balloon movement will change. This is being stored in the constructor to prevent
        # the writing of new values every frame.
        self.change_direction_interval = self.calculate_new_interval()
        
    def update(self):
        
        super(Balloon, self).update()
        
        if self.rect.y <= TBOUNDARY:
            self.set_move_direction(True)
        
        elif self.rect.y >= BBOUNDARY:
            self.set_move_direction(False)

        # Choose a random 3 to 5 second interval
        if pygame.time.get_ticks() % self.change_direction_interval == 0:
        
            # Set move speed and alternate move direction of balloon
            self.set_move_direction(not self.move_direction)
            
            # Set new interval for the next change in direction
            self.change_direction_interval = self.calculate_new_interval()

        # Apply movement to balloon
        self.rect.y += self.move_speed

    def detect_collisions(self):
        
        super(Balloon, self).detect_collisions()    
        self.balloon_hit = pygame.sprite.spritecollide(self, bullets, False)

    def set_move_direction(self, direction):
        
        self.move_direction = direction

        if direction:
                self.move_speed = abs(self.move_speed)               
        else:
                self.move_speed = -(abs(self.move_speed))

    def calculate_new_interval(self):
        return round(FPS * random.uniform(BALLOON_CHANGE_DIRECTION_INTERVAL_MIN, BALLOON_CHANGE_DIRECTION_INTERVAL_MAX))



# Update game logic
def update(queue):
    
    for game_object in update_queue:
        game_object.update()

# Handle input
def handle_input():
    
    player.handle_input()

# Render game
def draw_game(queue):
    
    window.fill(BACKGROUND_COLOUR)
    
    for game_object in render_queue:
        window.blit(game_object.image, game_object.rect)

    display_message('Missed Shots: %d' % player.missed_shots, (WIDTH / 2, HEIGHT - FONT_SIZE))

    pygame.display.flip()

def display_message(message, coords):
    message = font.render(message, False, (0, 0, 0))
    window.blit(message, coords)

# Set up game objects
player = Player()
balloon = Balloon()

# Bullets fired by the player will be placed in this array
bullets = []

# Game loop
while not (pygame.event.get(pygame.QUIT) or quit_requested):
    
    pygame.event.pump()

    handle_input()

    # Game will play out until the balloon is hit. When the balloon is hit, the win message is displayed
    if not balloon.balloon_hit:
        
        update_queue = [player]
        if not balloon.balloon_hit: update_queue.append(balloon)
        update_queue.extend(bullets)

        update(update_queue)

        render_queue = [player]
        if not balloon.balloon_hit: render_queue.append(balloon)
        render_queue.extend(bullets)

        draw_game(render_queue)

        display_message('Missed shots: %d' % player.missed_shots, (0, 0))

    else:
        window.fill(BACKGROUND_COLOUR)
        display_message('You win!', (WIDTH / 2, HEIGHT / 2))
        pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
exit()