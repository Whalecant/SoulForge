import pygame
import random

RED = (200, 50, 50)
GREEN = (50, 200, 50)
BLACK = (0, 0, 0)
DARK_BG = (10, 10, 25)
CYAN = (0, 230, 255)
YELLOW = (255, 220, 50)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (203, 195, 227)
GRAY = (100, 100, 100)
WHITE = (255, 255, 255)

class hackingMinigame:
    def __init__(self, walls, dummies=None, dummyCount=1, keyPos=None, exitPos=None, rows = 6, cols=8, dummyPenalty = 5.0):
        self.rows = rows
        self.cols = cols
        self.walls = walls
        self.dummyPenalty = dummyPenalty

        self.codeFont = pygame.font.Font(None, 15)

        self.occupied = set(tuple(p) for p in self.walls + [[0, 0]])

        if keyPos is not None:
            self.keyPos = keyPos
        else:
            self.keyPos = self.getRandomOpenTile()

        self.occupied.add(tuple(self.keyPos))

        if exitPos is not None:
            self.exitPos = exitPos
        else:
            self.exitPos = self.getRandomOpenTile()

        self.occupied.add(tuple(self.exitPos))

        if dummies is not None:
            self.dummies = dummies
        else:
            self.dummies = [self.getRandomOpenTile() for _ in range(dummyCount)]
        
        self.reset()

    def reset(self):
        self.playerPos = [0, 0]
        self.hasKey = False
        self.isComplete = False
        self.collectedDummies = set()
        self.lastPenaltyMessage = ""

    def getRandomOpenTile(self):
        while True:
            r = random.randint(0, self.rows - 1)
            c = random.randint(0, self.cols - 1)

            if (r, c) not in self.occupied:
                self.occupied.add((r, c))
                return [r, c]
        
    def input(self, event, terminal = None):
        if self.isComplete or event.type != pygame.KEYDOWN:
            return

        newR, newC = self.playerPos[0], self.playerPos[1]

        if event.key == pygame.K_UP or event.key == pygame.K_w:
            newR -= 1
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
            newR += 1
        elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
            newC -= 1
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
            newC += 1
        else:
            return

        if 0 <= newR < self.rows and 0 <= newC < self.cols:
            if [newR, newC] not in self.walls:
                self.playerPos = [newR, newC]

        if self.playerPos == self.keyPos:
            self.hasKey = True

        playerTuple = tuple(self.playerPos)
        if self.playerPos in self.dummies and playerTuple not in self.collectedDummies:
            self.collectedDummies.add(playerTuple)
            if terminal is not None:
                terminal.timeLeft = max(0.0, terminal.timeLeft - self.dummyPenalty)
                if terminal.timeLeft == 0.0:
                    terminal.alarmTriggered = True


        if self.playerPos == self.exitPos and self.hasKey:
            self.isComplete = True

    def drawCenteredWrappedText(self, surface, text, font, color, rect):
        words = text.split(' ')
        lines = []
        currLine = []

        maxWidth = rect.width - 10

        for word in words:
            testLine = ' '.join(currLine + [word])
            if font.size(testLine)[0] <= maxWidth:
                currLine.append(word)
            else:
                if currLine:
                    lines.append(' '.join(currLine))
                currLine = [word]
        if currLine:
            lines.append(' '.join(currLine))

        totalHeight = sum(font.size(line)[1] for line in lines)
        startY = rect.centery - (totalHeight // 2)

        for line in lines:
            textSurf = font.render(line, True, color)
            textRect = textSurf.get_rect(center = (rect.centerx, startY + textSurf.get_height() // 2))
            surface.blit(textSurf, textRect)
            startY += textSurf.get_height()

    def draw(self, surface, screenWidth, screenHeight, smallFont):
        cellSize = 80
        boardWidth = self.cols * cellSize
        boardHeight = self.rows * cellSize
        boardX = (screenWidth - boardWidth) // 2
        boardY = (screenHeight - boardHeight) // 2 + 20

        pygame.draw.rect(surface, DARK_BG, (boardX - 10, boardY - 10, boardWidth + 20, boardHeight + 20))
        pygame.draw.rect(surface, CYAN, (boardX - 10, boardY - 10, boardWidth + 20, boardHeight + 20), 2)

        for r in range(self.rows):
            for c in range(self.cols):
                cX = boardX + c * cellSize
                cY = boardY + r * cellSize
                rect = pygame.Rect(cX, cY, cellSize, cellSize)

                pygame.draw.rect(surface, (20, 35, 45), rect, 1)

                if [r, c] in self.walls:
                    pygame.draw.rect(surface, RED, rect.inflate(-4, -4))

                elif [r, c] in self.dummies and (r, c) not in self.collectedDummies:
                    pygame.draw.rect(surface, GRAY, rect.inflate(-16, -16))
                    self.drawCenteredWrappedText(surface, "ACCESS = FALSE", self.codeFont, WHITE, rect)

                elif [r, c] == self.keyPos and not self.hasKey:
                    pygame.draw.rect(surface, LIGHT_PURPLE, rect.inflate(-12, -12))
                    self.drawCenteredWrappedText(surface, "ACCESS = TRUE", self.codeFont, BLACK, rect)

                elif [r, c] == self.exitPos:
                    if self.hasKey:
                        exitColor = GREEN
                    else:
                        exitColor = GRAY
                    pygame.draw.rect(surface, exitColor, rect.inflate(-8, -8), 3)
                    self.drawCenteredWrappedText(surface, "Insert Code", self.codeFont, exitColor, rect)

        pR, pC = self.playerPos
        pX = boardX + pC * cellSize + cellSize // 2
        pY = boardY + pR * cellSize + cellSize // 2
        pygame.draw.circle(surface, CYAN, (pX, pY), 16)
        pygame.draw.circle(surface, WHITE, (pX, pY), 16, 2)