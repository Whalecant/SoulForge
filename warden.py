import pygame

GRAVITY = 0.6
JUMP_STRENGTH = -15
SCREEN_WIDTH = 1000

PURPLE = (120, 60, 180)
WHITE = (255, 255, 255)
CYAN = (100, 220, 220)
DARK_GRAY = (60, 60, 60)
RED = (200, 50, 50)

class Warden:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 70)
        self.hitbox = self.rect.copy()

        self.vel_x = 0
        self.vel_y = 0
        self.speed = 4.5
        self.facing = 1

        self.onGround = False
        self.hasDoubleJumped = False
        self.doubleJumpCd = 0

        self.dialogue_index = 0
        self.talking = True
        self.defeated = False

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

    def relocateToRoom(self, roomRect):
        self.rect.x = roomRect.right - 100
        self.rect.y = roomRect.bottom - 120
        self.hitbox.x = self.rect.x
        self.hitbox.y = self.rect.y
        self.vel_x = 0
        self.vel_y = 0

    def update(self, player, platforms, alarmActive = False):
        if self.talking or self.defeated:
            return

        if self.doubleJumpCd > 0:
            self.doubleJumpCd -= 1

        self.vel_y += GRAVITY

        currSpeed = self.speed * 2 if alarmActive else self.speed

        if player.rect.centerx > self.rect.centerx + 10:
            self.vel_x = currSpeed
            self.facing = 1
        elif player.rect.centerx < self.rect.centerx - 10:
            self.vel_x = -currSpeed
            self.facing = -1
        else:
            self.vel_x = 0

        probeX = self.rect.right + 8 if self.facing == 1 else self.rect.left - 8
        wallAhead = any(p.collidepoint(probeX, self.rect.centery) for p in platforms)
        playerAbove = (player.rect.bottom < self.rect.top - 20)

        if(wallAhead or playerAbove) and self.onGround:
            self.vel_y = JUMP_STRENGTH
            self.onGround = False

        elif not self.onGround and not self.hasDoubleJumped and self.doubleJumpCd == 0:
            if playerAbove or wallAhead:
                self.vel_y = JUMP_STRENGTH * 0.9
                self.hasDoubleJumped = True
                self.doubleJumpCd = 30

        self.rect.x += self.vel_x
        self.hitbox.x = self.rect.x

        for p in platforms:
            if self.hitbox.colliderect(p):
                if self.vel_x > 0:
                    self.hitbox.right = p.left
                elif self.vel_x < 0:
                    self.hitbox.left = p.right
                self.rect.x = self.hitbox.x

        self.rect.y += self.vel_y
        self.hitbox.y = self.rect.y
        self.onGround = False

        for p in platforms:
            if self.hitbox.colliderect(p):
                if self.vel_y > 0:
                    self.hitbox.bottom = p.top
                    self.vel_y = 0
                    self.onGround = True
                    self.hasDoubleJumped = False
                elif self.vel_y < 0:
                    self.hitbox.top = p.bottom
                    self.vel_y = 0
                self.rect.y = self.hitbox.y

    def draw(self, surface, camera=None):
        if self.defeated and self.phase == 0:
            return

        color = PURPLE if not self.defeated else (100, 60, 140)
        drawRect = camera.apply(self.rect) if camera else self.rect

        # Body
        pygame.draw.rect(surface, color, drawRect, border_radius=6)
        pygame.draw.rect(surface, WHITE, drawRect, 2, border_radius=6)

        # Eye
        eye_color = RED if (not self.talking and not self.defeated) else CYAN
        eye_y = drawRect.y + 20
        pygame.draw.circle(surface, WHITE, (drawRect.centerx - 10, eye_y), 5)
        pygame.draw.circle(surface, WHITE, (drawRect.centerx + 10, eye_y), 5)
        pygame.draw.circle(surface, eye_color, (drawRect.centerx - 10, eye_y), 3)
        pygame.draw.circle(surface, eye_color, (drawRect.centerx + 10, eye_y), 3)