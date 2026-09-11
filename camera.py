import pygame

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.x = 0
        self.y = 0
        self.targetX = 0
        self.targetY = 0
        self.isTrans = False
        self.transSpeed = 0.08 # put it as a lower number for smoother transitions (i love lerp - dw abt it)

    def targetRoom(self, roomRect):
        self.targetX = roomRect.x
        self.targetY = roomRect.y

    def snapToRoom(self, roomRect):
        self.x = roomRect.x
        self.y = roomRect.y
        self.targetX = roomRect.x
        self.targetY = roomRect.y
        self.isTrans = False

    def update(self):
        if self.x != self.targetX or self.y != self.targetY:
            self.isTrans = True

            self.x += (self.targetX - self.x) * self.transSpeed
            self.y += (self.targetY - self.y) * self.transSpeed

            if abs(self.targetX - self.x) < 0.5:
                self.x = self.targetX
            if abs(self.targetY - self.y) < 0.5:
                self.y = self.targetY
        else:
            self.isTrans = False

    def apply(self, rect):
        return rect.move(-int(self.x), -int(self.y))