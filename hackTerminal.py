import pygame
from hackMinigame import hackingMinigame #type: ignore
from spriteSheet import spriteSheet, animation

RED = (255, 50, 50)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (203, 195, 227)
BLACK = (0, 0, 0)

class Terminal:
    def __init__(self, x, y, walls, keyPos = None, exitPos = None, dummies = None, rotation = 0, dummyCount = 1, timeLimit = 25.0, room="general"):
        
        width, height = 40, 50

        if rotation == 90 or rotation == -90:
            width, height = height, width
        self.rect = pygame.Rect(x, y, width, height)

        self.rotation = rotation
        self.timeLimit = timeLimit
        self.timeLeft = timeLimit
        self.isHacked = False
        self.alarmTriggered = False

        self.alarmBuffer = 10.0
        self.exitDelay = 0.5
        self.hasStarted = False

        self.spawnAlpha = 255

        self.minigame = hackingMinigame(
            keyPos = keyPos,
            exitPos = exitPos,
            walls = walls,
            dummies = dummies,
            dummyCount = dummyCount,
        )

        self.room = room

        self.sheet = spriteSheet("assets/sprites/Hack_Console-Sheet.png", 64, 64)


    def saveDict(self):
        return{
            "x": self.rect.x,
            "y": self.rect.y,
            "timeLeft": self.timeLeft,
            "timeLimit": self.timeLimit,
            "isHacked": self.isHacked,
            "alarmTriggered": self.alarmTriggered,
            "alarmBuffer": self.alarmBuffer,
        }

    def loadDict(self, data):
        self.timeLeft = data.get("timeLeft", self.timeLimit)
        self.isHacked = data.get("isHacked", False)
        self.alarmTriggered = data.get("alarmTriggered", False)
        self.alarmBuffer = data.get("alarmBuffer", 10.0)
        if self.isHacked:
            self.minigame.isComplete = True

    def canInteract(self, playerRect):
        interactZone = self.rect.inflate(40, 50)
        return interactZone.colliderect(playerRect)

    def updateTimer(self, dt, isActive = False):
        if self.timeLeft > 0 and not self.isHacked and isActive:
            self.timeLeft -= dt
            if self.timeLeft <= 0:
                self.timeLeft = 0
                self.alarmTriggered = True
                self.alarmBuffer = 10.0

        if self.alarmTriggered and self.isHacked:
            self.alarmBuffer -= dt
            if self.alarmBuffer <= 0.0:
                self.alarmBuffer = 0.0
                self.alarmTriggered = False

        if self.isHacked and self.exitDelay > 0:
            self.exitDelay -= dt
            if self.exitDelay <= 0:
                self.exitDelay = 0
                return True

        return False

    def input(self, event):
        if not self.isHacked:
            self.minigame.input(event, terminal = self)
            if self.minigame.isComplete:
                self.isHacked = True

    def draw(self, surface, camera):
        screenRect = camera.apply(self.rect)

        if self.isHacked:
            sprite = self.sheet.frames[2]  # success
        elif self.alarmTriggered:
            sprite = self.sheet.frames[1]  # failed
        else:
            sprite = self.sheet.frames[0]  # default

        spriteToDraw = sprite.copy()
        spriteToDraw.set_alpha(self.spawnAlpha)

        if self.rotation != 0:
            spriteToDraw = pygame.transform.rotate(spriteToDraw, self.rotation)
            frameRect = spriteToDraw.get_rect(center=screenRect.center)
        else:
            frameRect = spriteToDraw.get_rect(midbottom=screenRect.midbottom)
        surface.blit(spriteToDraw, frameRect)

    def drawMinigame(self, surface, screenWidth, screenHeight, smallFont):
        self.minigame.draw(surface, screenWidth, screenHeight, smallFont)