
# Imports
import pygame, random

class gameValues(object):
    def __init__(self):
        # Dimensions
        wSize = pygame.display.get_window_size()
        self.width = wSize[0]
        self.height = wSize[1]

        # Floor
        self.floor = int(self.height * (8/10))
        self.bounds = [0, 0, self.width, self.floor]
        self.spawnPoint = [self.width//2, self.floor]

        # Character values
        self.maxSpeed = 1.5
        self.jumpStrength = 5
        self.charFrames = 32
        self.gravity = -0.1
        self.minYVelocity = -3

        # Changeable values
        self.map = 0
        self.mapVals = {  # Set this later
            0: [None, None, None],
            1: [None, None, None]
        }

# Player character class, descended from the pygame Sprite class
class player(pygame.sprite.Sprite):
    def __init__(self, vars):
        super(player, self).__init__()
        self.health = 100
        self.floor = vars.floor
        self.xPos = vars.spawnPoint[0]
        self.yPos = vars.spawnPoint[1]
        self.jumpStrength = vars.jumpStrength
        self.bounds = vars.bounds
        self.velocity = 0
        self.yVelocity = 0
        self.minYVelocity = vars.minYVelocity
        self.gravity = vars.gravity
        self.frame = 0
        self.charFrames = vars.charFrames

        # Image Assets
        self.iIdle = pygame.image.load("resources/idle.png").convert_alpha()
        self.iWalk1 = pygame.image.load("resources/walk1.png").convert_alpha()
        self.iWalk2 = pygame.image.load("resources/walk2.png").convert_alpha()
        self.iJump = pygame.image.load("resources/jump.png").convert_alpha()
        self.iFall = pygame.image.load("resources/fall.png").convert_alpha()
        self.walkImages = [self.iWalk1, self.iWalk2]
        self.image = self.iIdle

        # Sets starting image
        self.rect = self.image.get_rect()
        self.flipped = False

    def getRect(self):
            return self.rect

    def setVelocity(self, value):
        self.velocity = value

    def update(self, screen):
        # Variables
        newX = self.xPos + self.velocity
        self.halfWidth = self.rect.width // 2
        startX = newX - self.halfWidth
        endX = newX + self.halfWidth

        # Check if player is within screen bounds
        if self.bounds[0] < startX and endX < self.bounds[2]:
            self.xPos = newX

        # Change image direction based on velocity
        if self.velocity < 0:
            self.flipped = True
        elif self.velocity > 0:
            self.flipped = False

        # Apply gravity and grounding to velocity
        if self.yPos < self.floor and self.yVelocity > self.minYVelocity:
            self.yVelocity += self.gravity
        elif self.yPos >= self.floor and self.yVelocity < 0:
            self.yPos = self.floor
            self.yVelocity = 0

        # Apply velocity
        self.yPos -= self.yVelocity

        # Render
        self.render(screen)
        self.frame += 1
        if self.frame >= self.charFrames:
            self.frame = 0

    def render(self, screen):
        # Set walking image frame (if walking)
        if abs(self.velocity) > 0:
            f = self.frame // int(self.charFrames / 2)
            self.image = self.walkImages[f]
        else:
            self.image = self.iIdle

        # Set jumping/falling image frame (if either)
        if self.yVelocity > 0:
            self.image = self.iJump
        elif self.yVelocity < 0:
            self.image = self.iFall

        if self.flipped:
            self.newImage = pygame.transform.flip(self.image, True, False)
        else:
            self.newImage = pygame.transform.flip(self.image, False, False)

        # Set position
        self.rect.midbottom = (self.xPos, self.yPos)
        screen.blit(self.newImage, self.rect)

# Main game function
def game():
    # Initialization
    pygame.init()
    clock = pygame.time.Clock()
    gameScreen = pygame.display.set_mode((960, 960))
    vals = gameValues()

    # Main Assets
    plr = player(vals)

    # Background
    background = pygame.image.load("resources/background.png").convert_alpha()
    background = pygame.transform.scale(background, [vals.width, vals.height])
    backgroundRect = background.get_rect()

    # Ground
    ground = pygame.image.load("resources/ground.png").convert_alpha()
    ground = pygame.transform.scale(ground, [vals.width, vals.height])
    groundRect = ground.get_rect()

    black = 0, 0, 0

    # Run Loop
    running = True
    while running:

        # Managing fps
        clock.tick(144)
        fps = clock.get_fps()
        print(int(fps // 1))

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Checking keys pressed
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT]:
            if plr.velocity <= 0:
                plr.velocity = 1
            if abs(plr.velocity) < vals.maxSpeed:
                plr.setVelocity(plr.velocity * 1.5)
        if pressed[pygame.K_LEFT]:
            if plr.velocity >= 0:
                plr.velocity = -1
            if abs(plr.velocity) < vals.maxSpeed:
                plr.setVelocity(plr.velocity * 1.5)
        if pressed[pygame.K_UP] or pressed[pygame.K_SPACE]:
            if plr.yVelocity == 0:
                plr.yVelocity = plr.jumpStrength
        if not pressed[pygame.K_RIGHT] and not pressed[pygame.K_LEFT]:
            plr.setVelocity(0)

        # Rendering
        gameScreen.fill(black)
        gameScreen.blit(background, backgroundRect)
        gameScreen.blit(ground, groundRect)
        plr.update(gameScreen)
        pygame.display.flip()
    pygame.quit()

# Run Game
game()