
# Imports
import pygame, random, math

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

        # Background Visibility
        self.blackScreen = [0, 0, 0, 0]
        self.dimStarted = False
        self.dimming = False
        self.dimPhase = -1
        self.dimTimer = 0
        self.dimSpeed = 1
        self.dimMap = -1

        # Floor
        self.floor = int(self.height * (8/10))
        self.chestFloor = self.floor + 2
        self.bounds = [0, 0, self.width, self.floor]
        self.spawnPoint = [100, self.floor]

        # Character values
        self.maxSpeed = 1.5
        self.jumpStrength = 5
        self.charFrames = 64
        self.gravity = -0.11
        self.minYVelocity = -3
        self.coinMultiplier = 50
        self.margin = 50
        self.maxHurt = 350

        # Player-game Values
        self.maxHealth = 3
        self.healthPoints = self.maxHealth
        self.coins = 0
        self.clickDistance = 250
        self.clickInterval = 10

        # Enemy values
        self.timerInterval = 90
        self.maxMove = 50
        self.enemyTimer = 0
        self.spawnTimer = (400, 800)
        self.maxEnemies = 5
        self.listOfEnemies = []
        self.defeatedEnemies = 0
        self.enemiesToDefeat = 5

        # Health Point Display Location
        self.healthPos = [75, self.height - 75]
        self.healthSpacing = 55

        # Upgrades Display Location (center)
        self.upgradeStartX = 130
        self.upgradeStartY = 300
        self.upgradeMargin = 100
        self.upgradeTextPos = [self.width // 2, 500]

        # Changeable values
        self.map = 0
        self.mapVals = [
            # Number : [Map_Name, BackgroundImage, GroundImage]
            ["Home", "resources/background.png", "resources/ground.png"],
            ["Arena", "resources/background2.png", "resources/ground2.png"]]
        self.swordFiles = [
            "resources/sword1.png",
            "resources/sword2.png",
            "resources/sword3.png"]
        self.upgrades = {
            # ID: [Level, MaxLevel, Name, Tooltip, Costs]
            0: [0, 2, "Sword", "The strength of your sword!", [50, 100, 150]],
            1: [0, 1, "Auto Jump", "Your player jumps on the box automatically!", [45]]
        }

    # Add coins to the player's storage
    def addCoins(self):
        # Add multiplier upgrades in the future
        self.coins += self.coinMultiplier

    def buyUpgrade(self, id):
        upgrade = self.upgrades[id]
        if upgrade[0] < upgrade[1] and self.coins >= upgrade[4][upgrade[0]]:
            self.coins -= upgrade[4][upgrade[0]]
            self.upgrades[id][0] += 1

    def changeScene(self, newMap, changeType):
        self.dimStarted = True
        self.dimPhase = 0
        self.dimMap = newMap
        if changeType == "loss":
            self.dimType = 0
        elif changeType == "win":
            self.dimType = 1


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

# Enemy character class
class enemyObject(pygame.sprite.Sprite):
    def __init__(self, vars, player):

        validSpawnX = False
        while not validSpawnX:
            self.xPos = random.randint(vars.margin, vars.width - vars.margin)
            if abs(player.xPos - self.xPos) > 150:
                validSpawnX = True
        self.yPos = vars.floor
        self.iIdle = "resources/slime.png"
        self.iPrep = "resources/slimePrep.png"
        self.iMove = "resources/slimeMove.png"
        self.iHit = "resources/slimeHit.png"
        self.timer = 0
        self.startX = self.xPos
        self.direction = 1
        self.hp = 3

        # States: "idle", "prep", "move", "hit"
        self.state = "idle"
        self.lastState = self.state

        self.image = pygame.image.load(self.iIdle).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.midbottom = (self.xPos, self.yPos)

    def click(self, mousePos, player, power, vals):
        mouseX = mousePos[0]
        mouseY = mousePos[1]

        xStart = self.rect.left
        xEnd = self.rect.right
        yStart = self.rect.top
        yEnd = self.rect.bottom

        plrX = player.xPos
        plrY = player.yPos

        a = (plrX - mouseX) ** 2
        b = (plrY - mouseY) ** 2
        c = abs(math.sqrt(a + b))

        if c < vals.clickDistance:
            if xStart <= mouseX <= xEnd and yStart <= mouseY <= yEnd:
                self.hp -= power
                if self.hp == 0:
                    return True
        return False


    def hit(self):
        self.changeImage(self.iHit)
        self.state = "hit"
        self.timer = 0

    def changeImage(self, newImage):
        newImageTemp = pygame.image.load(newImage).convert_alpha()
        if self.direction == 1:
            self.image = pygame.transform.flip(newImageTemp, True, False)
        else:
            self.image = newImageTemp
        self.rect = self.image.get_rect()
        self.rect.midbottom = (self.xPos, self.yPos)

    def update(self, screen, player, vars):
        # Check for player collision
        if self.rect.colliderect(player.rect) and player.hurting == 0 and vars.healthPoints > 0:
            # Apply damage
            self.changeImage(self.iIdle)
            player.hurting = vars.maxHurt
            vars.healthPoints -= 0.5
            print(vars.healthPoints)
            self.state = "idle"
            self.timer = 0

        # Movement and animations
        self.lastState = self.state
        if self.lastState == "idle":
            #print("count idle")
            if self.timer > vars.timerInterval // 3:
                #print("Switch to prep")
                self.changeImage(self.iPrep)
                self.state = "prep"
                self.timer = 0
        if self.lastState == "prep":
            #print("count prep")
            if self.timer > vars.timerInterval:
                #print("Switch to move")
                self.changeImage(self.iMove)
                self.state = "move"
                self.startX = self.xPos
                self.timer = 0
        if self.lastState == "move":
            if self.timer == 0:
                self.changeImage()
            self.direction = 1
            startX = self.startX
            if player.xPos < self.startX:
                self.direction = -1
            endX = startX + (self.direction * vars.maxMove)
            currentPosition = self.xPos + ((endX - startX) / vars.maxMove)
            self.xPos = currentPosition
            if abs(currentPosition - endX) <= 2:
                #print("Switch to idle")
                self.changeImage(self.iIdle)
                self.state = "idle"
                self.timer = 0
        self.timer += 1
        self.render(screen)

    def render(self, screen):
        self.rect.midbottom = (self.xPos, self.yPos)
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
        self.paused = False
        self.hurting = 0

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

    def resetPosition(self, vars):
        self.xPos = vars.spawnPoint[0]
        self.yPos = vars.spawnPoint[1]
        self.image = self.iIdle
        self.flipped = False
        self.velocity = 0
        self.yVelocity = 0

    # Updates the player position and logic
    def update(self, screen, box, vars):
        if not self.paused:
            # Variables
            newX = self.xPos + self.velocity
            self.halfWidth = self.rect.width // 2
            startX = newX - self.halfWidth
            endX = newX + self.halfWidth


            # Box-Enemy Logic
            if self.hurting > 0:
                self.hurting -= 1

            # Box-Player Logic
            if self.yPos <= (box.yTop + 5) and box.withinBounds(self.xPos) and vars.map == 0:
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

            # Increments walking frames
            self.frame += 1
            if self.frame >= self.charFrames:
                self.frame = 0
        # Render
        self.render(screen)

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

class upgradeMenuObj(pygame.sprite.Sprite):
    def __init__(self, vals):
        self.menuOpen = False
        self.upgradeList = []
        self.selectedUpgrade = -1

    def getClicked(self, mousePos):
        if self.menuOpen == True:
            mouseX = mousePos[0]
            mouseY = mousePos[1]
            for i in range(len(self.upgradeList)):
                u = self.upgradeList[i]
                rad = u[1].width // 2
                centerPoint = u[1].center
                startX = centerPoint[0] - rad
                endX = centerPoint[0] + rad
                startY = centerPoint[1] - rad
                endY = centerPoint[1] + rad
                if startX <= mouseX <= endX and startY <= mouseY <= endY:
                    self.selectedUpgrade = i

    def updateMenu(self, screen, vals):
        if self.menuOpen:
            # Handle each upgrade
            startX = vals.upgradeStartX
            startY = vals.upgradeStartY
            margin = vals.upgradeMargin

            # Erase upgrade list to start over
            self.upgradeList = []

            i = 0
            if len(self.upgradeList) == 0 or self.selectedUpgrade != -1:
                for uName in vals.upgrades:
                    u = vals.upgrades[uName]
                    position = (margin//2 + (i * margin) + startX, startY)
                    levelText = u[2] + " : " + str(u[0]) + "/" + str(u[1])
                    costs = u[4]
                    currentUpgrade = u[0]

                    if currentUpgrade < len(costs) and currentUpgrade < u[1]:
                        costText = "Cost: " + str(costs[currentUpgrade])
                    else:
                        costText = "Maxed Out!"

                    borderImage = pygame.image.load("resources/panel.png").convert_alpha()
                    borderImage = pygame.transform.scale(borderImage, (70, 70))
                    borderImageRect = borderImage.get_rect()
                    borderImageRect.center = position

                    self.upgradeList += [[borderImage, borderImageRect, levelText, costText]]
                    i += 1
            self.renderMenu(screen, vals)


    def renderMenu(self, screen, vals):
        # Draw backplate
        w, h = screen.get_width(), screen.get_height()
        backBoard = pygame.Surface((w, h))
        backBoard.set_alpha(200)
        backBoard.fill((0, 0, 0))
        backBoardRect = backBoard.get_rect()
        backBoardRect.topleft = (0, 0)
        screen.blit(backBoard, backBoardRect)

        for u in self.upgradeList:
            screen.blit(u[0], u[1])

        if self.selectedUpgrade != -1:
            upgrade = self.upgradeList[self.selectedUpgrade]

            costPos = vals.upgradeTextPos
            costFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 36)
            costText = costFont.render(upgrade[3], False, (224, 160, 117))
            costTextRect = costText.get_rect()
            costTextRect.center = costPos
            screen.blit(costText, costTextRect)

            levelPosX = vals.upgradeTextPos[0]
            levelPosY = vals.upgradeTextPos[1] + 30
            levelFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 30)
            levelText = levelFont.render(upgrade[2], False, (224, 160, 117))
            levelTextRect = levelText.get_rect()
            levelTextRect.center = (levelPosX, levelPosY)
            screen.blit(levelText, levelTextRect)

            buyPosX = vals.upgradeTextPos[0]
            buyPosY = vals.upgradeTextPos[1] + 60
            buyFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 14)
            buyText = buyFont.render("Press B to Buy", False, (237, 77, 71))
            buyTextRect = buyText.get_rect()
            buyTextRect.center = (buyPosX, buyPosY)
            screen.blit(buyText, buyTextRect)

# Main game function
def game():
    # Initialization
    pygame.init()
    clock = pygame.time.Clock()
    gameScreen = pygame.display.set_mode((960, 960))
    vals = gameValues()
    pygame.mouse.set_visible(False)

    # Main Assets
    plr = player(vals)
    box = boxObject(vals)
    upgradeMenu = upgradeMenuObj(vals)

    # Cursor
    cursorFile = "resources/cursor.png"
    if vals.map == 1:
        swordLevel = vals.upgrades[0][0]
        cursorFile = vals.swordFiles[swordLevel]
    cursor = pygame.image.load(cursorFile).convert_alpha()
    cursorRect = cursor.get_rect()
    clickTimer = 0

    # Background
    bgFile = vals.mapVals[vals.map][1]
    background = pygame.image.load(bgFile).convert_alpha()
    background = pygame.transform.scale(background, [vals.width, vals.height])
    backgroundRect = background.get_rect()

    # Ground
    gFile = vals.mapVals[vals.map][2]
    ground = pygame.image.load(gFile).convert_alpha()
    ground = pygame.transform.scale(ground, [vals.width, vals.height])
    groundRect = ground.get_rect()

    black = 0, 0, 0

    # Run Loop
    running = True
    while running:

        # Managing fps
        clock.tick(144)
        fps = clock.get_fps()

        # Change cursor location
        cursorRect.topleft = pygame.mouse.get_pos()
        clickTimer += 1

        # Check for quit
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e and vals.map == 0:
                    if upgradeMenu.menuOpen:
                        upgradeMenu.menuOpen = False
                        plr.paused = False
                    else:
                        upgradeMenu.selectedUpgrade = -1
                        upgradeMenu.menuOpen = True
                        plr.paused = True
                elif event.key == pygame.K_b and upgradeMenu.menuOpen:
                    if upgradeMenu.selectedUpgrade != -1:
                        vals.buyUpgrade(upgradeMenu.selectedUpgrade)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                upgradeMenu.getClicked(pygame.mouse.get_pos())
                if vals.map == 1 and clickTimer >= vals.clickInterval:
                    clickTimer = 0
                    for enemy in vals.listOfEnemies:
                        isDead = enemy.click(pygame.mouse.get_pos(), plr, vals.upgrades[0][0] + 1, vals)
                        if isDead:
                            vals.listOfEnemies.remove(enemy)
                            vals.defeatedEnemies += 1

        # Checking keys pressed
        pressed = pygame.key.get_pressed()
        if (pressed[pygame.K_RIGHT] or pressed[pygame.K_d]) and not plr.paused:
            if plr.velocity <= 0:
                plr.velocity = 1
            if abs(plr.velocity) < vals.maxSpeed:
                plr.setVelocity(plr.velocity * 1.5)
        if (pressed[pygame.K_LEFT] or pressed[pygame.K_a]) and not plr.paused:
            if plr.velocity >= 0:
                plr.velocity = -1
            if abs(plr.velocity) < vals.maxSpeed:
                plr.setVelocity(plr.velocity * 1.5)
        if (pressed[pygame.K_UP] or pressed[pygame.K_SPACE] or pressed[pygame.K_w]) and not plr.paused:
            if plr.yVelocity == 0:
                plr.yVelocity = plr.jumpStrength
        if not pressed[pygame.K_RIGHT] and not pressed[pygame.K_d] and not plr.paused:
            if not pressed[pygame.K_LEFT] and not pressed[pygame.K_a]:
                plr.setVelocity(0)

        # Managing scene switch to arena
        if vals.map == 0 and plr.xPos >= (vals.width - 52):
            print("Scene Switch")
            plr.resetPosition(vals)
            vals.map = 1

            bgFile = vals.mapVals[vals.map][1]
            background = pygame.image.load(bgFile).convert_alpha()
            background = pygame.transform.scale(background, [vals.width, vals.height])
            backgroundRect = background.get_rect()

            gFile = vals.mapVals[vals.map][2]
            ground = pygame.image.load(gFile).convert_alpha()
            ground = pygame.transform.scale(ground, [vals.width, vals.height])
            groundRect = ground.get_rect()

            swordLevel = vals.upgrades[0][0]
            cursorFile = vals.swordFiles[swordLevel]
            cursor = pygame.image.load(cursorFile).convert_alpha()
            cursorRect = cursor.get_rect()

        # Rendering Background Assets
        gameScreen.fill(black)
        gameScreen.blit(background, backgroundRect)
        gameScreen.blit(ground, groundRect)

        # Render Box
        if vals.map == 0:
            box.render(gameScreen, vals)

        # Render Player
        plr.update(gameScreen, box, vals)

        # Creating enemies
        if vals.map == 1:
            enemyMsg = "Enemies Defeated: " + str(vals.defeatedEnemies) + "/" + str(vals.enemiesToDefeat)
            enemyFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 40)
            enemyText = enemyFont.render(enemyMsg, False, (255, 185, 110))
            enemyTextRect = enemyText.get_rect()
            enemyTextRect.center = (vals.width // 2, 100)
            gameScreen.blit(enemyText, enemyTextRect)

        if vals.defeatedEnemies >= vals.enemiesToDefeat:
            vals.changeScene(0, "win")
            vals.listOfEnemies = []
            vals.enemyTimer = 0
        if vals.map == 1:
            vals.enemyTimer += 1
            if len(vals.listOfEnemies) < vals.maxEnemies:
                s = vals.spawnTimer
                randSpawn = random.randint(s[0], s[1])
                if vals.enemyTimer > randSpawn:
                    vals.enemyTimer = 0
                    newEnemy = enemyObject(vals, plr)
                    vals.listOfEnemies += [newEnemy]
                    print("new enemy created")
        else:
            vals.listOfEnemies = []

        if vals.map == 1:
            for enemy in vals.listOfEnemies:
                enemy.update(gameScreen, plr, vals)

        # Health
        if vals.map == 1 and vals.healthPoints <= 0:
            vals.changeScene(0, "loss")

        healthPointsTemp = vals.healthPoints
        healthPointsList = []
        for i in range(vals.maxHealth):
            positionX = vals.healthPos[0] + (i * vals.healthSpacing)
            positionY = vals.healthPos[1]

            healthImageName = "resources/noHealth.png"
            if healthPointsTemp >= 1:
                healthImageName = "resources/fullHealth.png"
            elif 0 < healthPointsTemp < 1:
                healthImageName = "resources/halfHealth.png"

            healthImage = pygame.image.load(healthImageName).convert_alpha()
            healthImage = pygame.transform.scale(healthImage, (64, 64))
            healthImageRect = healthImage.get_rect()
            healthImageRect.center = (positionX, positionY)
            healthPointsList += [[healthImage, healthImageRect]]
            healthPointsTemp -= 1

        # Render Health Point elements
        if vals.map != 0:
            for healthPoint in healthPointsList:
                gameScreen.blit(healthPoint[0], healthPoint[1])

        # Render Upgrade Menu
        if vals.map == 0:
            upgradeMenu.updateMenu(gameScreen, vals)

        # Render Coin Count
        if vals.map == 0:
            coinFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 35)
            coinText = coinFont.render("Coins: " + str(vals.coins), False, (252, 169, 3))
            coinTextRect = coinText.get_rect()
            coinTextRect.center = (gameScreen.get_width() // 2, 75)
            gameScreen.blit(coinText, coinTextRect)

        # Render Shop tooltip
        if vals.map == 0:
            shopFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 20)
            shopText = shopFont.render("Press E to open/close the shop!", False, (255, 185, 110))
            shopTextRect = shopText.get_rect()
            shopTextRect.midtop = (gameScreen.get_width() // 2, 100)
            gameScreen.blit(shopText, shopTextRect)

        # Render Black Screen
        if vals.dimStarted == True:
            if vals.dimming and vals.blackScreen[3] < 255 and vals.dimTimer > vals.dimSpeed:
                vals.blackScreen[3] += 2.5
                vals.dimTimer = 0
            elif vals.dimming == False and vals.blackScreen[3] > 0:
                vals.blackScreen[3] = 0
                vals.dimTimer = 0
                vals.dimStarted = False
            elif vals.dimming and vals.blackScreen[3] == 255:
                vals.dimPhase = 1

            blackBoard = pygame.Surface((vals.width, vals.height))
            blackBoard.set_alpha(vals.blackScreen[3])
            blackBoard.fill((0, 0, 0))
            blackBoardRect = blackBoard.get_rect()
            blackBoardRect.topleft = (0, 0)
            gameScreen.blit(blackBoard, blackBoardRect)
            print(vals.dimPhase, vals.dimTimer)
            if vals.dimPhase == 0:
                vals.dimming = True
            elif vals.dimPhase == 1:
                if vals.dimTimer > 250:
                    plr.resetPosition(vals)
                    vals.map = 0

                    bgFile = vals.mapVals[vals.map][1]
                    background = pygame.image.load(bgFile).convert_alpha()
                    background = pygame.transform.scale(background, [vals.width, vals.height])
                    backgroundRect = background.get_rect()

                    gFile = vals.mapVals[vals.map][2]
                    ground = pygame.image.load(gFile).convert_alpha()
                    ground = pygame.transform.scale(ground, [vals.width, vals.height])
                    groundRect = ground.get_rect()

                    cursor = pygame.image.load("resources/cursor.png").convert_alpha()
                    cursorRect = cursor.get_rect()

                    vals.healthPoints = vals.maxHealth
                    vals.defeatedEnemies = 0
                    vals.blackScreen[3] = 0
                    vals.dimStarted = False
                else:
                    if vals.dimType == 0:
                        dimMessage = "Game Over!"
                    elif vals.dimType == 1:
                        dimMessage = "You Win!!"

                    dimFont = pygame.font.Font('resources/KenneyFutureNarrow.ttf', 40)
                    dimText = dimFont.render(dimMessage, False, (255, 185, 110))
                    dimTextRect = dimText.get_rect()
                    dimTextRect.center = (vals.width//2, vals.height//2)
                    gameScreen.blit(dimText, dimTextRect)
            elif vals.dimPhase == 2:
                vals.blackScreen[3] = 0
                vals.dimStarted = False
            vals.dimTimer += 1

        # Render Cursor
        gameScreen.blit(cursor, cursorRect)
        pygame.display.flip()
    pygame.quit()

# Run Game
game()