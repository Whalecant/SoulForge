import pygame


GRAVITY = 0.6
JUMP_STRENGTH = -13
SHORT_HOP_CUTOFF = -4
ACCEL = 0.8
FRICTION = 0.8
#adding these two for preference, feels more... right iykwim
MOVE_SPEED = 5
SCREEN_WIDTH = 1000
COYOTE_TIME_MAX = 5
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

        self.isTouchWall = False
        self.wallDir = 0
        self.isWallSlide = False

        self.wallJumpForceX = 10
        self.wallJumpForceY = -12
        self.neutralXMult = 0.3
        self.wallLockout = 0

        self.maxSlideSpd = 3
        self.fastSlideSpd = 7
        self.fastFallForce = 1.5
        self.isFastFall = False

    def input(self,keys):
        moveInput = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= ACCEL
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += ACCEL
        else:
            if self.on_ground:
                self.vel_x *= FRICTION

        downPressed = keys[pygame.K_s] or keys[pygame.K_DOWN]
        if downPressed and not self.on_ground and not self.isWallSlide:
            self.isFastFall = True
        else:
            self.isFastFall = False

        if keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]:
            self.jump(moveInput)

        if not (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.vel_y < SHORT_HOP_CUTOFF and self.isJump:
            self.vel_y = SHORT_HOP_CUTOFF

        if self.vel_x > MOVE_SPEED:
            self.vel_x = MOVE_SPEED
        elif self.vel_x < -MOVE_SPEED:
            self.vel_x = -MOVE_SPEED

        return moveInput

    def update(self, platforms, roomRect = None, isTrans = False, moveInput = 0):
        if isTrans:
            return

        self.checkSurroundings(platforms, moveInput)

        if self.isFastFall:
            self.vel_y += GRAVITY * self.fastFallForce
        else:
            self.vel_y += GRAVITY

        if self.isWallSlide:
            if self.isFastFall:
                slideLimit = self.fastSlideSpd
            else:
                self.maxSlideSpd

            if self.vel_y > slideLimit:
                self.vel_y = slideLimit
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

    
    def checkSurroundings(self, platforms, moveInput):
        if self.wallLockout > 0:
            self.wallLockout -= 1

        #for wall related movements
        leftBox = self.rect.inflate(4, -8)
        leftBox.x -= 2

        rightBox = self.rect.inflate(4, -8)
        rightBox.x += 2

        touchLeft = any(leftBox.colliderect(p) for p in platforms)
        touchRight = any(rightBox.colliderect(p) for p in platforms)

        if touchLeft:
            self.isTouchWall = True
            self.wallDir = -1
        elif touchRight:
            self.isTouchWall = True
            self.wallDir = 1
        else:
            self.isTouchWall = False
            self.wallDir = 0

        #Wall Slide
        if (self.wallDir == -1 and moveInput < 0) or (self.wallDir == 1 and moveInput > 0):
            pushIntoWall = True
        else:
            pushIntoWall = False

        if not self.on_ground and self.isTouchWall and self.vel_y >= 0 and pushIntoWall  and self.wallLockout == 0:
            self.isWallSlide = True
        else:
            self.isWallSlide = False

        #wall mantle
        if self.isTouchWall and not self.on_ground and self.vel_y >= 0:
            headRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 20) #uhhh, for in short, higher number, less area it can mantle, cuz its now long if ur legs are through that you can mantle, essentially :thumbsUp:
            if self.wallDir == -1:
                headRect.x -= 4
            else:
                headRect.x += 4

            headBlocked = any(headRect.colliderect(p) for p in platforms)

            if not headBlocked:
                self.mantleClimb()

    def jump(self, moveInput):
        if(self.isWallSlide or self.isTouchWall) and not self.on_ground:
            self.isFastFall = False
            self.isWallSlide = False
            self.wallLockout = 10 #10 frames to not be able to wall jump again instantly, u can remove if u think is not needed (this applies to any and all cd and lockout timers)

            if (self.wallDir == -1 and moveInput > 0) or (self.wallDir == 1 and moveInput < 0):
                holdAway = True
            else:
                holdAway = False

            if holdAway:
                appliedX = -self.wallDir * self.wallJumpForceX
            else:
                appliedX = -self.wallDir * (self.wallJumpForceX * self.neutralXMult)

            self.vel_x = appliedX
            self.vel_y = self.wallJumpForceY
            self.isJump = True
        elif self.on_ground or self.coyoteTimer > 0:
            self.vel_y = JUMP_STRENGTH
            self.coyoteTimer = 0
            self.isJump = True

    def mantleClimb(self):
        self.vel_y = JUMP_STRENGTH * 0.6
        self.vel_x = self.wallDir *  MOVE_SPEED * 0.8
        self.wallLockout = 10
        self.isTouchWall = False
        self.isWallSlide = False

    def draw(self, surface, camera):
        screenRect = camera.apply(self.rect)
        pygame.draw.rect(surface, BLUE, screenRect)
        pygame.draw.rect(surface, WHITE, screenRect, 2)