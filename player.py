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
#the following things are because I have recereated titania from warframe essenitally, i thought i already added this failsafe... but nvm ig lol
MAX_STEP = 10
MAX_FALL_SPEED = 50
MAX_FAST_FALL_SPEED = 200
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
        self.slideTimer = 0
        self.wallGripDelay = 15
        self.slideAccelPerSec = 1
        self.slideAccelPerFrame = self.slideAccelPerSec / 60

        self.wallJumpForceX = 10
        self.wallJumpForceY = -12
        self.neutralXMult = 0.3
        self.wallLockout = 0

        self.maxSlideSpd = 10.0
        self.fastSlideSpd = 25.0
        self.fastFallForce = 1.5
        self.isFastFall = False

        self.justJumped = False
        self.justLanded = False
        self.justWalked = False
        self.footstepTimer = 0
        self.footstepInterval = 20

    def input(self,keys):
        moveInput = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x -= ACCEL
            moveInput = -1
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x += ACCEL
            moveInput = 1
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

        if self.isWallSlide:
            slideLimit = self.fastSlideSpd if self.isFastFall else self.maxSlideSpd

            if self.slideTimer <= self.wallGripDelay:
                currentCap = 0.01
            elif self.slideTimer <= 135:
                slowFrames = self.slideTimer - 15
                currentCap = 0.1 + (slowFrames * 0.015)
            else:
                fastFrames = self.slideTimer - 135

                currentCap = 2.0 + (fastFrames * 0.4)
                currentCap = min(currentCap, slideLimit)

            self.vel_y = currentCap
        else:
            if self.isFastFall:
                self.vel_y += GRAVITY * self.fastFallForce
            else:
                self.vel_y += GRAVITY

            self.vel_y = min(self.vel_y, MAX_FAST_FALL_SPEED if self.isFastFall else MAX_FALL_SPEED)

        self.moveX(platforms)

        wasOnGround = self.on_ground
        self.moveY(platforms)

        self.justLanded = not wasOnGround and self.on_ground

        isWalking = self.on_ground and abs(self.vel_x) > 0.5
        if isWalking:
            self.footstepTimer += 1
            if self.footstepTimer >= self.footstepInterval:
                self.footstepTimer = 0
                self.justWalked = True
            else:
                self.justWalked = False
        else:
            self.footstepTimer = 0
            self.justWalked = False

        if self.on_ground:
            self.isJump = False
            self.slideTimer = 0

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

    def moveX(self, platforms):
        rem = self.vel_x
        while rem != 0:
            step = max(-MAX_STEP, min(MAX_STEP, rem))
            rem -= step
            self.rect.x += step

            for p in platforms:
                if self.rect.colliderect(p):
                    if step > 0:
                        self.rect.right = p.left
                    else:
                        self.rect.left = p.right
                    return

    def moveY(self, platforms):
        rem = self.vel_y
        self.on_ground = False
        while rem != 0:
            step = max(-MAX_STEP, min(MAX_STEP, rem))
            rem -= step
            self.rect.y += step

            for p in platforms:
                if self.rect.colliderect(p):
                    if step > 0:
                        self.rect.bottom = p.top
                        self.on_ground = True
                    else:
                        self.rect.top = p.bottom

                    self.vel_y = 0
                    return
                    

    
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

            
        #wall mantle
        mantled = False
        if self.isTouchWall and not self.on_ground and self.vel_y >= 0 and not self.isWallSlide:
            headRect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 20) #uhhh, for in short, higher number, less area it can mantle, cuz its now long if ur legs are through that you can mantle, essentially :thumbsUp:
            if self.wallDir == -1:
                headRect.x -= 4
            else:
                headRect.x += 4

            headBlocked = any(headRect.colliderect(p) for p in platforms)

            if not headBlocked:
                self.mantleClimb()
                mantled = True

        if not mantled and not self.on_ground and self.isTouchWall and self.vel_y >= 0 and pushIntoWall  and self.wallLockout == 0:
            self.isWallSlide = True
        else:
            self.isWallSlide = False


        if self.isWallSlide:
            self.slideTimer += 1
        else:
            self.slideTimer = max(0, self.slideTimer - 0.5)

    def jump(self, moveInput):
        self.justJumped = False
        if(self.isWallSlide or self.isTouchWall) and not self.on_ground and self.wallLockout == 0:
            self.isFastFall = False
            self.isWallSlide = False
            self.wallLockout = 20 #10 frames to not be able to wall jump again instantly, u can remove if u think is not needed (this applies to any and all cd and lockout timers)

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
            self.justJumped = True
        elif self.on_ground or self.coyoteTimer > 0:
            self.vel_y = JUMP_STRENGTH
            self.coyoteTimer = 0
            self.isJump = True
            self.justJumped = True

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