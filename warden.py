import pygame
import math
import random
import heapq
import sys
import os
import numpy as np

GRAVITY = 0.6
JUMP_STRENGTH = -15
SCREEN_WIDTH = 1000

PATH_CELL_SIZE = 60 #fuck this i'm making a grid lol
PATH_SEARCH_MARGIN = 500 #this is just for a safety net for range
PATH_MAX_GRID_CELLS = 40 # so it doesn't break
PATH_REPLAN_FRAMES = 20 #recompute time

PURPLE = (120, 60, 180)
WHITE = (255, 255, 255)
CYAN = (100, 220, 220)
DARK_GRAY = (60, 60, 60)
RED = (200, 50, 50)

def resourcePath(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)

# there's a lot of weird math here I don't get, but basically this https://onthefly.itch.io/the-alchemist/devlog/219218/grayscaling-an-image-with-pygame-and-numpy
def greyScale(surface: pygame.Surface) -> pygame.Surface:
    arr = pygame.surfarray.array3d(surface)
    alpha = pygame.surfarray.array_alpha(surface)

    luma = np.dot(arr[:, :, :3], [0.299, 0.587, 0.114])
    lumaArr3d = luma[..., np.newaxis]
    greyRgb = np.repeat(lumaArr3d, 3, axis=2).astype(np.uint8)

    greySurf = pygame.surfarray.make_surface(greyRgb)
    greySurf = greySurf.convert_alpha()
    pygame.surfarray.pixels_alpha(greySurf)[:, :] = alpha

    return greySurf
class Warden:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 75)
        self.hitbox = self.rect.copy()

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 4.5
        self.facing = 1

        self.posX = float(x)
        self.posY = float(y)

        self.path = []
        self.pathReplanCount = PATH_REPLAN_FRAMES

        self.stuckFrames = 0
        self.unstickFrames = 0
        self.unstickDir = 1

        self.onGround = False
        self.hasDoubleJumped = False
        self.doubleJumpCd = 0

        self.hover = 0.0

        self.dialogue_index = 0
        self.talking = True
        self.defeated = False

        self.dialogueTimer = 0.0
        self.dialogueAdvance = 1

        self.charsShown = 0.0
        self.charSpeed = 60

        self.posedDown = False

        self.phase = 0
        self.dialogue_lines = [
            "So. The 73rd. You've come at last.",
            "I have watched you grow. Every jump. Every victory. Every soul you've harvested.",
            "You think you are the hero. I thought so too, once. I was the third.",
            "My name was Gerard Gatewald. I was the first to win. I was the first to be given the choice.",
            "This world is not real. It is code. Compressed soul essence, sustained by the attention of beings beyond our comprehension.",
            "The Outer Ones. They watch us. They feel for us. And when they feel, they leak essence. That essence is our only fuel.",
            "Without conflict, they grow bored. Without drama, they look away. And when they look away, everything here dies.",
            "I chose to become the villain. So that millions could live. I have done this for seventy-two cycles.",
            "Seventy-two names carved into the code of my own body. I remember every one of them.",
            "You are the first one who has looked at me and seen a person instead of an obstacle.",
            "That is why you will win. Not because you are stronger. Because you wanted to understand.",
            "Come. Let us finish this. Show me you are strong enough to carry the burden I have carried.",
        ]

        self.canSkip = False
        self.skipHold = 0.0
        self.skipHoldTime = 1.0
        self.skipFont = None

        self.sprite = pygame.image.load(resourcePath("assets/sprites/Gerard.png")).convert_alpha()
        self.posedDownSprite = pygame.image.load(resourcePath("assets/sprites/Gerard_Yamcha.png")).convert_alpha()
        self.greyPosedDownSprite = greyScale(self.posedDownSprite)
        self.eyeSprite = pygame.image.load(resourcePath("assets/sprites/Gerard_Eyes.png")).convert_alpha()
        self.angyEyeSprite = pygame.image.load(resourcePath("assets/sprites/Gerard_Eyes_Red.png")).convert_alpha()

        scale = 0.75
        newSize = (int(self.sprite.get_width() * scale), int(self.sprite.get_height() * scale))

        self.sprite = pygame.transform.scale(self.sprite, newSize)


    def advanceDialogue(self):
        self.dialogue_index += 1
        self.dialogueTimer = 0.0
        self.charsShown = 0.0
        if self.dialogue_index >= len(self.dialogue_lines):
            self.talking = False
            return True
        return False

    def tickDialogue(self, dt):
        if not self.talking:
            return False

        currLine = self.dialogue_lines[self.dialogue_index] if 0 <= self.dialogue_index < len(self.dialogue_lines) else ""
        if self.charsShown < len(currLine):
            self.charsShown += self.charSpeed * dt
            return False

        self.dialogueTimer += dt
        if self.dialogueTimer >= self.dialogueAdvance:
            return self.advanceDialogue()
        return False

    def tickSkip(self, dt, holding):
        if not self.talking or not self.canSkip:
            self.skipHold = 0.0
            return False

        if holding:
            self.skipHold += dt
            if self.skipHold >= self.skipHoldTime:
                self.skipHold = 0.0
                self.talking = False
                self.dialogue_index = len(self.dialogue_lines)
                return True
        else:
            self.skipHold = max(0.0, self.skipHold - dt * 2)
        return False

    def drawSkipPrompt(self, surface):
        if not(self.talking and self.canSkip) or self.defeated:
            return

        if self.skipFont is None:
            self.skipFont = pygame.font.Font(None, 20)

        progress = min(1.0, self.skipHold / self.skipHoldTime)
        size = 50
        cx, cy = surface.get_width() - 80, 60

        icon = pygame.Surface((size, size), pygame.SRCALPHA)

        icon.fill((180, 120, 255, 25))

        fillHeight = int(size *  progress)

        if fillHeight > 0:
            pygame.draw.rect(icon, (180, 120, 255, 230), (0, size - fillHeight, size, fillHeight))

        pygame.draw.rect(icon, (180, 120, 255, 255), icon.get_rect(), 3)

        letter = self.skipFont.render("Y", True, (180, 120, 255))
        icon.blit(letter, letter.get_rect(center=icon.get_rect().center))

        surface.blit(icon, icon.get_rect(center=(cx, cy)))

        label = self.skipFont.render("HOLD TO SKIP", True, (255, 255, 255))
        label.set_alpha(200)
        surface.blit(label, label.get_rect(midtop=(cx, cy + size // 2 + 6)))

    def relocateToRoom(self, roomRect):
        if getattr(self, "hasSpawned", False):
            return

        self.hasSpawned  =True
        self.rect.x = roomRect.right - 100
        self.rect.y = roomRect.bottom - 500
        self.hitbox.x = self.rect.x
        self.hitbox.y = self.rect.y
        self.vel_x = 0
        self.vel_y = 0

        self.posX = float(self.rect.x)
        self.posY = float(self.rect.y)

    def cellToWorld(self, cell, minX, minY, cellSize):
        col, row = cell
        return (minX + col * cellSize + cellSize / 2, minY + row * cellSize + cellSize / 2)

    def aStarPathfinding(self, start, goal, blocked, cols, rows):
        if start == goal:
            return [start]

        neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

        def heuristic(a, b):
            return math.hypot(a[0] - b[0], a[1] - b[1])

        openHeap = [(heuristic(start, goal), 0.0, start)]
        cameFrom = {}
        bestG = {
            start: 0.0,
        }
        visitedCap = cols * rows * 2 + 100

        steps = 0

        while openHeap:
            steps += 1
            if steps > visitedCap:
                break

            _, g, curr = heapq.heappop(openHeap)
            if curr != goal and g > bestG.get(curr, float("inf")):
                continue

            if curr == goal:
                path = [curr]
                while curr in cameFrom:
                    curr = cameFrom[curr]
                    path.append(curr)
                path.reverse()
                return path

            cx, cy = curr
            for dx, dy in neighbors:
                neighbor = (cx + dx, cy + dy)
                nx, ny = neighbor

                if not(0 <= nx < cols and 0 <= ny < rows):
                    continue
                if neighbor in blocked:
                    continue
                if dx != 0 and dy != 0:
                    if(cx + dx, cy) in blocked or (cx, cy + dy) in blocked:
                        continue

                tentativeG = g + math.hypot(dx, dy)
                if tentativeG < bestG.get(neighbor, float("inf")):
                    bestG[neighbor] = tentativeG
                    cameFrom[neighbor] = curr
                    heapq.heappush(openHeap, (tentativeG + heuristic(neighbor, goal), tentativeG, neighbor))

        return None

    def findPath(self, player, platforms):
        obstacles = []

        cellSize = PATH_CELL_SIZE

        minX = min(self.rect.centerx, player.rect.centerx) - PATH_SEARCH_MARGIN
        minY = min(self.rect.centery, player.rect.centery) - PATH_SEARCH_MARGIN
        maxX = max(self.rect.centerx, player.rect.centerx) + PATH_SEARCH_MARGIN
        maxY = max(self.rect.centery, player.rect.centery) + PATH_SEARCH_MARGIN

        cols = max(1, int((maxX - minX) // cellSize) + 1)
        rows = max(1, int((maxY - minY) // cellSize) + 1)

        if cols > PATH_MAX_GRID_CELLS or rows > PATH_MAX_GRID_CELLS:
            cellSize = max((maxX - minX) / PATH_MAX_GRID_CELLS, (maxY - minY) / PATH_MAX_GRID_CELLS)

            cols = max(0, int((maxX - minX) // cellSize) + 1)
            rows = max(0, int((maxY - minY) // cellSize) + 1)

        halfWidth, halfHeight = self.rect.width // 2, self.rect.height // 2

        minX = math.floor(minX / cellSize) * cellSize
        minY = math.floor(minY / cellSize) * cellSize
        cols = max(1, int((maxX - minX) // cellSize) + 1)
        rows = max(1, int((maxY - minY) // cellSize) + 1)

        blocked = set()
        for p in platforms:
            inflated = p.inflate(halfWidth * 2 + 10, halfHeight * 2 + 10)
            if inflated.right < minX or inflated.left > maxX or inflated.bottom < minY or inflated.top > maxY:
                continue
            obstacles.append(inflated)

            startCol = max(0, int((inflated.left - minX) // cellSize))
            endCol = min(cols - 1, int((inflated.right - minX) // cellSize))
            startRow = max(0, int((inflated.top - minY) // cellSize))
            endRow = min(rows - 1, int((inflated.bottom - minY) // cellSize))

            for col in range(startCol, endCol + 1):
                for row in range(startRow, endRow + 1):

                    cellCx = minX + col * cellSize + cellSize / 2
                    cellCy = minY + row * cellSize + cellSize / 2
                    if inflated.collidepoint(cellCx, cellCy):
                        blocked.add((col, row))

        def toCell(px, py):
            col = min(cols - 1, max(0, int((px - minX) // cellSize)))
            row = min(rows - 1, max(0, int((py - minY) // cellSize)))

            return (col, row)

        start = toCell(self.rect.centerx, self.rect.centery)
        goal = toCell(player.rect.centerx, player.rect.centery)

        blocked.discard(start)
        blocked.discard(goal)

        cellPath = self.aStarPathfinding(start, goal, blocked, cols, rows)
        if not cellPath:
            return None

        points = [self.rect.center] + [self.cellToWorld(c, minX, minY, cellSize) for c in cellPath[1:]] + [player.rect.center]
        return self.smoothPath(points, obstacles)[1:]
    
    def clearLine(self, a, b, obstacles):
        for r in obstacles:
            if r.clipline(int(a[0]), int(a[1]), int(b[0]), int(b[1])):
                return False
        return True

    def smoothPath(self, points, obstacles):
        if len(points) <= 2:
            return points
        smoothed = [points[0]]
        i = 0

        while i < len(points) - 1:
            j = len(points) - 1
            while j > i  + 1 and not self.clearLine(points[i], points[j], obstacles):
                j -= 1
            smoothed.append(points[j])
            i = j
        return smoothed

    def update(self, player, platforms, alarmActive = False):
        if self.talking or self.defeated:
            return

        self.hover += 0.06

        currSpd = self.speed * 2.0 if alarmActive else self.speed

        self.pathReplanCount = getattr(self, "pathReplanCount", PATH_REPLAN_FRAMES) + 1
        needsNewPath = (not getattr(self, "path", None)) or self.pathReplanCount >= PATH_REPLAN_FRAMES

        if needsNewPath:
            self.pathReplanCount = 0
            newPath = self.findPath(player, platforms)
            if newPath is not None:
                self.path = newPath
            else:
                print("no path found")
                print(f"{player.rect.centerx}, {player.rect.centery}")

        targetX, targetY = player.rect.centerx, player.rect.centery

        if self.path:
            waypoint = self.path[0]
            if math.hypot(waypoint[0] - self.rect.centerx, waypoint[1] - self.rect.centery) < PATH_CELL_SIZE * 0.6:
                self.path.pop(0)
            if self.path:
                targetX, targetY = self.path[0]

        dx = targetX - self.rect.centerx
        dy = targetY - self.rect.centery
        dist = math.hypot(dx, dy)

        if dist > 1:
            self.vel_x = (dx / dist) * currSpd
            self.vel_y = (dy / dist) * currSpd
        else:
            self.vel_x = 0
            self.vel_y = 0

        if dx > 5:
            self.facing = 1
        elif dx < -5:
            self.facing = -1

        oldX, oldY = self.rect.center

        if self.unstickFrames > 0 and dist > 1:
            self.unstickFrames -= 1
            self.vel_x = (-dy / dist) * currSpd * self.unstickDir
            self.vel_y = (dx / dist) * currSpd * self.unstickDir

        self.move(platforms)

        moved = math.hypot(self.rect.centerx - oldX, self.rect.centery - oldY)
        if dist > 90 and moved < currSpd * 0.3:
            self.stuckFrames += 1
        else:
            self.stuckFrames = 0

        if self.stuckFrames >= 10:
            self.stuckFrames = 0
            self.unstickFrames = 20
            self.unstickDir = random.choice([-1, 1])
            self.pathReplanCount = PATH_REPLAN_FRAMES

    def move(self, platforms):
        self.posX += self.vel_x
        self.rect.x = round(self.posX)

        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_x > 0:
                    self.rect.right = p.left
                elif self.vel_x < 0:
                    self.rect.left = p.right

                self.posX = float(self.rect.x)

        self.posY += self.vel_y
        self.rect.y = round(self.posY)
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                self.posY = float(self.rect.y)

        self.hitbox.topleft = self.rect.topleft



    def draw(self, surface, camera=None):
        screenRect = camera.apply(self.rect)

        sprite = self.greyPosedDownSprite if (self.posedDown and self.posedDownSprite is not None) else self.sprite

        if not self.defeated:
            if self.facing == 1:
                sprite = self.sprite
            else:
                sprite = pygame.transform.flip(sprite, 1, 0)

        frameRect = sprite.get_rect(midbottom=screenRect.midbottom)
        surface.blit(sprite, frameRect)

        eyeSprite = self.eyeSprite if (not self.defeated and self.talking) else self.angyEyeSprite

        if not self.defeated:
            eyeBob = math.sin(self.hover) * 4 
            eyeRect = eyeSprite.get_rect(center=(frameRect.centerx, frameRect.centery + eyeBob))
            surface.blit(eyeSprite, eyeRect)

        #for debugging
        """
        if camera and self.path and not self.defeated:
            pts = [camera.apply(pygame.Rect(x, y, 0, 0)).topleft for x, y in self.path]
            pygame.draw.lines(surface, (255, 255, 0), False, [frameRect.center] + pts, 2)
        """