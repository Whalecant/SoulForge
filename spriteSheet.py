import pygame
import sys
import os

def resourcePath(relativePath):
    basePath = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(basePath, relativePath)


class spriteSheet:
    def __init__ (self, filePath, frameWidth, frameHeight, scale = 1):
        self.sheet = pygame.image.load(resourcePath(filePath)).convert_alpha()
        self.frameWidth = frameWidth
        self.frameHeight = frameHeight
        self.frames = self.sliceFrames(scale)

    def sliceFrames(self, scale):
        sheetWidth, sheetHeight = self.sheet.get_size()
        cols = sheetWidth // self.frameWidth
        rows = sheetHeight // self.frameHeight

        frames = []
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * self.frameWidth, row * self.frameHeight, self.frameWidth, self.frameHeight)
                frame = self.sheet.subsurface(rect).copy()
                if scale != 1:
                    frame = pygame.transform.scale(frame, (int(self.frameWidth * scale), int(self.frameHeight * scale)))
                frames.append(frame)
        return frames

class animation:
    def __init__(self, frames, frameDuration = 6, loop = True):
        self.frames = frames
        self.frameDuration = frameDuration
        self.loop = loop
        self.currFrame = 0
        self.timer = 0
        self.finished = False

    def update(self):
        if self.finished:
            return

        self.timer += 1
        if self.timer >= self.frameDuration:
            self.timer = 0
            self.currFrame += 1
            if self.currFrame >= len(self.frames):
                if self.loop:
                    self.currFrame = 0
                else:
                    self.currFrame = len(self.frames) - 1
                    self.finished = True

    def getCurrFrame(self):
        return self.frames[self.currFrame]

    def reset(self):
        self.currFrame = 0
        self.timer = 0
        self.finished = False