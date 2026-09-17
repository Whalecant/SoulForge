import pygame

class Checkpoint:
    def __init__(self, x, y, width = 60, height = 120):
        self.rect = pygame.Rect(x, y, width, height)
        self.playerEntry = False