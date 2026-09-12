import pygame

RED = (255, 50, 50)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (203, 195, 227)
BLACK = (0, 0, 0)

class Terminal:
    def __init__(self, x, y, timeLimit = 20.0):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.timeLimit = timeLimit
        self.timeLeft = timeLimit
        self.isHacked = False
        self.alarmTriggered = False

    def canInteract(self, playerRect):
        interactZone = self.rect.inflate(40, 40)
        return interactZone.colliderect(playerRect)

    def draw(self, surface, camera):
        screenRect = camera.apply(self.rect)

        if self.alarmTriggered:
            color = RED
        elif self.isHacked:
            color = LIGHT_PURPLE
        else:
            color = PURPLE

        pygame.draw.rect(surface, color, screenRect)
        pygame.draw.rect(surface, BLACK, screenRect, 2)