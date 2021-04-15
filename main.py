
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
        self.maxSpeed = 6

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
        self.xPos = vars.spawnPoint[0]
        self.yPos = vars.spawnPoint[1]
        self.bounds = vars.bounds
        self.velocity = 0

        self.originalImage = pygame.image.load("resources/idle.png")
        self.image = pygame.image.load("resources/idle.png")
        self.rect = self.image.get_rect()
        self.flipped = False

    def getRect(self):
            return self.rect

    def setVelocity(self, value):
        self.velocity = value

    def update(self, screen):
        newX = self.xPos + self.velocity
        self.halfWidth = self.rect.width // 2
        startX = newX - self.halfWidth
        endX = newX + self.halfWidth

        if self.bounds[0] < startX and endX < self.bounds[2]:
            self.xPos = newX

        if self.velocity < 0:
            self.flipped = True
        else:
            self.flipped = False

        self.render(screen)

    def render(self, screen):
        if self.flipped:
            self.image = pygame.transform.flip(self.originalImage, True, False)
        else:
            self.image = pygame.transform.flip(self.originalImage, False, False)

        self.rect.midbottom = (self.xPos, self.yPos)
        screen.blit(self.image, self.rect)

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
    background = pygame.image.load("resources/background.png")
    background = pygame.transform.scale(background, [vals.width, vals.height])
    backgroundRect = background.get_rect()

    # Ground
    ground = pygame.image.load("resources/ground.png")
    ground = pygame.transform.scale(ground, [vals.width, vals.height])
    groundRect = ground.get_rect()

    black = 0, 0, 0

    # Run Loop
    running = True
    while running:

        # Managing fps
        time = clock.tick(60)

        # Checking for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    print("RIGHT")
                    if plr.velocity <= 0:
                        plr.velocity = 4
                    if abs(plr.velocity) < vals.maxSpeed:
                        plr.setVelocity(plr.velocity * 1.5)
                elif event.key == pygame.K_LEFT:
                    print("LEFT")
                    if plr.velocity >= 0:
                        plr.velocity = -4
                    if abs(plr.velocity) < vals.maxSpeed:
                        plr.setVelocity(plr.velocity * 1.5)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    print("OUT")
                    plr.setVelocity(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Mouse events
                pass

        # Rendering
        gameScreen.fill(black)
        gameScreen.blit(background, backgroundRect)
        gameScreen.blit(ground, groundRect)
        plr.update(gameScreen)
        pygame.display.flip()
    pygame.quit()

# Run Game
game()