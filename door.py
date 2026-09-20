import pygame

class Door:
    def __init__(self, x, y, width=20, height = 80, openX = 0, openY = -80, moveSpd = 1.5, openDelay = 1.0, requiredTerminals = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.closedPos = pygame.Vector2(x, y)
        self.targetPos = pygame.Vector2(x, y)
        self.currentPos = pygame.Vector2(x, y)

        self.openPos = pygame.Vector2(x + openX, y + openY)
        self.moveSpd = moveSpd
        self.openDelay = openDelay
        self.delayTimer = 0.0
        self.requiredTerminals = requiredTerminals or []

        self.forcedClose = False

    def forceClose(self):
        self.forcedClose = True
        self.delayTimer = 0.0
        self.targetPos = self.closedPos

    def releaseForceClose(self):
        self.forcedClose = False

    def syncToTerminalState(self):
        if self.allTerminalsHacked():
            self.delayTimer = self.openDelay
            self.currentPos = pygame.Vector2(self.openPos)
            self.targetPos = pygame.Vector2(self.openPos)
            self.rect.x = int(self.openPos.x)
            self.rect.y = int(self.openPos.y)

    def update(self, dt=1/60,  isPause = False):
        if isPause:
            return

        if self.forcedClose:
            self.delayTimer = 0.0
            self.targetPos = self.closedPos
        elif self.allTerminalsHacked():
            if self.delayTimer < self.openDelay:
                self.delayTimer += dt
                self.targetPos = self.closedPos
            else:
                self.targetPos = self.openPos
        else:
            self.delayTimer = 0.0
            self.targetPos = self.closedPos

        if self.currentPos != self.targetPos:
            direction = self.targetPos - self.currentPos
            distance = direction.length()

            if distance <= self.moveSpd:
                self.currentPos = pygame.Vector2(self.targetPos)
            else:
                self.currentPos += direction.normalize() * self.moveSpd

            self.rect.x = int(self.currentPos.x)
            self.rect.y = int(self.currentPos.y)

    def allTerminalsHacked(self):
        if not self.requiredTerminals:
            return False
        return all(term.isHacked for term in self.requiredTerminals)

    def draw(self, surface, camera=None):
        screenRect = camera.apply(self.rect) if camera else self.rect

        isFullyOpen = self.allTerminalsHacked() and self.delayTimer >= self.openDelay
        color = (100, 100, 100) if isFullyOpen else (139, 69, 19)

        pygame.draw.rect(surface, color, screenRect)
        pygame.draw.rect(surface, (0, 0, 0), screenRect, 2)

        
