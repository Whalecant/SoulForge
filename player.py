import pygame


GRAVITY = 0.6
JUMP_STRENGTH = -15
SHORT_HOP_CUTOFF = -5
ACCEL = 0.8
FRICTION = 0.85
#adding these two for preference, feels more... right iykwim
MOVE_SPEED = 5
SCREEN_WIDTH = 1000
COYOTE_TIME_MAX = 8
"""
for ur reference (宋理), coyote time is the time the player has to still input the jump button and for the game to recognize that input after the player has left the platform, it overall just lets the gameplay feel more fun
https://www.youtube.com/watch?v=LBFNXBblf9c (for reference for u)
the number above is the number of frames that the game lets you, since you set the game to be in 60 fps, that's roughly 1/3rd of a second to let the player input the jump button
change it as you will later if u want
- Wilson
"""

BLUE = (50, 100, 200)
WHITE = (255, 255, 255)

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.coyoteTimer = 0
        self.isJump = False
        self.doorCd = 0
        #as an extra heads up, i code in camelCase (i.e. the first letter of the second word is capitalized, i don't mind snake case, but that's just as a heads up since our coding styles are different)

    def input(self,keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= ACCEL
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += ACCEL
        else:
            self.vel_x *= FRICTION

        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump()

        if not (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.vel_y < SHORT_HOP_CUTOFF and self.isJump:
            self.vel_y = SHORT_HOP_CUTOFF

        if self.vel_x > MOVE_SPEED:
            self.vel_x = MOVE_SPEED
        elif self.vel_x < -MOVE_SPEED:
            self.vel_x = -MOVE_SPEED


    def update(self, platforms, roomRect = None, isTrans = False):
        if isTrans:
            return

        self.vel_y += GRAVITY

        # keys = pygame.key.get_pressed()
        # moving = keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]
        # if not moving:
        #     self.vel_x *= FRICTION

        self.rect.x += self.vel_x
        
        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_x > 0:
                    self.rect.right = p.left
                elif self.vel_x < 0:
                    self.rect.left = p.right
                self.vel_x = 0

        if roomRect:
            if self.rect.left < roomRect.left:
                self.rect.left = roomRect.left
                self.vel_x = 0
            if self.rect.right > roomRect.right:
                self.rect.right = roomRect.right
                self.vel_x = 0

        self.rect.y += self.vel_y
        wasOnGround = self.on_ground # added for coyote Time
        self.on_ground = False

        for p in platforms:
            if self.rect.colliderect(p):
                if self.vel_y > 0:
                    self.rect.bottom = p.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = p.bottom
                    self.vel_y = 0

        if self.on_ground:
            self.isJump = False

        #just as a precautionary method just in case this causes future bugs lol
        if self.doorCd > 0:
            self.doorCd -= 1

        #coyote time code :thumbsUp:
        if self.on_ground:
            self.coyoteTimer = COYOTE_TIME_MAX
        elif wasOnGround and not self.on_ground and self.vel_y >= 0:
            self.coyoteTimer = COYOTE_TIME_MAX
        else:
            if self.coyoteTimer > 0:
                self.coyoteTimer -= 1

    def jump(self):
        if self.on_ground or self.coyoteTimer > 0:
            self.vel_y = JUMP_STRENGTH
            self.coyoteTimer = 0
            self.isJump = True

    def draw(self, surface, camera):
        screenRect = camera.apply(self.rect)
        pygame.draw.rect(surface, BLUE, screenRect)
        pygame.draw.rect(surface, WHITE, screenRect, 2)