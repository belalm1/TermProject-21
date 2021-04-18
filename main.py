
# Imports
import pygame, random

# NOTES

# ------ BOX ------
# Check if within X bounds of the BOX. If so, activate "second floor". Second floor is the main primary floor, if below
# second floor, use typical floor as the floor.

# ------ WEAPONS ------
# NO PHYSICAL WEAPONS!! YAY!!
# The cursor functions as a weapon, click on enemies within range to kill them (they turn white to show hurt)
# There is always a "pointer" where the cursor is, it is marked with a red "do not" symbol if out of range
# If within range, it should be a sword or a pointer
# When clicking (and click is within range of character), cycle through a dictionary of all enemies, if
# the cursor pointer is within the hitbox of any enemy, apply damage to them

# ------ ENEMY COLLISION ------
# Every frame, the player checks the enemy dictionary to see if within the hitbox of any, [might wanna implement a
# checkInEnemyHitbox() function at this point], if so, deduct a health point from the player, and set them to IMMUNE for
# X amount of time. The player should not check for enemy collision if immune.

class gameValues(object):
    def __init__(self):
        # Dimensions
        wSize = pygame.display.get_window_size()
        self.width = wSize[0]
        self.height = wSize[1]

        # Floor
        self.floor = int(self.height * (8/10))
        self.chestFloor = self.floor + 2
        self.bounds = [0, 0, self.width, self.floor]
        self.spawnPoint = [self.width//2, self.floor]

        # Character values
        self.maxSpeed = 1.5
        self.jumpStrength = 5
        self.charFrames = 64
        self.gravity = -0.11
        self.minYVelocity = -3
        self.coinMultiplier = 1

        # Player-game Values
        self.health = 100
        self.coins = 0

        # Changeable values
        self.map = 0
        self.mapVals = {  # Set this later
            0: [None, None, None],
            1: [None, None, None]}

    # Add coins to the player's storage
    def addCoins(self):
        # Add multipliers in the future
        self.coins += self.coinMultiplier


# Box class
class boxObject(pygame.sprite.Sprite):
    def __init__(self, vars):

        # Variables
        self.size = 70
        self.rad = 35
        self.xCenter = vars.width//2
        self.yBottom = vars.floor
        self.yTop = vars.floor - self.size
        self.isHit = False
        self.hurtingFrames = 0
        self.maxHurt = 10 # Amount of frames to look "hurt"

        # Images
        self.idle = pygame.image.load("resources/grassBlock.png").convert_alpha()
        self.hit = pygame.image.load("resources/grassBlock_hit.png").convert_alpha()

        # Sets starting image and rect
        self.image = self.idle
        self.rect = self.image.get_rect()

    # Checks if player within x bounds of box
    def withinBounds(self, playerX):
        xStart = self.xCenter - self.rad
        xEnd = self.xCenter + self.rad
        if xStart <= playerX <= xEnd:
            return True
        return False

    # Player landed on box, display box flash (aka hurt)
    def getHit(self):
        self.isHit = True

    # Render box
    def render(self, screen, vars):
        # Check if box has been landed on
        if self.isHit:
            self.image = self.hit

            # Increment hurting frames, reset if necessary
            self.hurtingFrames += 1
            if self.hurtingFrames == self.maxHurt:
                self.isHit = False
                self.hurtingFrames = 0
            elif self.hurtingFrames == 1:
                # Add coins!!!
                vars.addCoins()

            # Add hurt sound?
        else:
            self.image = self.idle
        self.rect.midbottom = (self.xCenter, self.yBottom)
        screen.blit(self.image, self.rect)

# Player character class, descended from the pygame Sprite class
class player(pygame.sprite.Sprite):
    def __init__(self, vars):
        super(player, self).__init__()

        # Variables
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

    # Returns sprite rect
    def getRect(self):
            return self.rect

    # Sets player's X velocity
    def setVelocity(self, value):
        self.velocity = value

    # Updates the player position and logic
    def update(self, screen, box):
        # Variables
        newX = self.xPos + self.velocity
        self.halfWidth = self.rect.width // 2
        startX = newX - self.halfWidth
        endX = newX + self.halfWidth

        # Box-Player Logic
        if self.yPos <= (box.yTop + 5) and box.withinBounds(self.xPos):
            currentFloor = box.yTop
            isSecondFloor = True
        else:
            currentFloor = self.floor
            isSecondFloor = False

        # Check if player is within screen bounds
        if self.bounds[0] < startX and endX < self.bounds[2]:
            self.xPos = newX

        # Change image direction based on velocity
        if self.velocity < 0:
            self.flipped = True
        elif self.velocity > 0:
            self.flipped = False

        # Apply gravity and grounding to velocity
        if self.yPos < currentFloor and self.yVelocity > self.minYVelocity:
            self.yVelocity += self.gravity
        elif self.yPos > currentFloor and self.yVelocity < 0:
            if isSecondFloor:
                box.getHit()
            self.yPos = currentFloor
            self.yVelocity = 0

        # Apply velocity
        self.yPos -= self.yVelocity

        # Render
        self.render(screen)
        self.frame += 1
        if self.frame >= self.charFrames:
            self.frame = 0

    # Renders the player
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
    box = boxObject(vals)

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
        #print(int(fps // 1))
        #print(vals.coins)

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
        box.render(gameScreen, vals)
        plr.update(gameScreen, box)
        pygame.display.flip()
    pygame.quit()

# Run Game
game()