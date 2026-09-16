import pygame
from hackMinigame import hackingMinigame #type: ignore

RED = (255, 50, 50)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (203, 195, 227)
BLACK = (0, 0, 0)

class Terminal:
    def __init__(self, x, y, walls, keyPos = None, exitPos = None, dummies = None, dummyCount = 1, timeLimit = 25.0, room="general"):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.timeLimit = timeLimit
        self.timeLeft = timeLimit
        self.isHacked = False
        self.alarmTriggered = False

        self.alarmBuffer = 10.0
        self.exitDelay = 0.5
        self.hasStarted = False

        self.minigame = hackingMinigame(
            keyPos = keyPos,
            exitPos = exitPos,
            walls = walls,
            dummies = dummies,
            dummyCount = dummyCount,
        )

        self.room = room

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
            color = LIGHT_PURPLE
        elif self.alarmTriggered:
            color = RED
        else:
            color = PURPLE

        pygame.draw.rect(surface, color, screenRect)
        pygame.draw.rect(surface, BLACK, screenRect, 2)

    def drawMinigame(self, surface, screenWidth, screenHeight, smallFont):
        self.minigame.draw(surface, screenWidth, screenHeight, smallFont)