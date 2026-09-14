import pygame


PATROL_SPEED = 1
CHASE_SPEED = 3.5
ENEMY_VISION_RANGE = 250
ENEMY_VISION_HEIGHT = 80
GRAVITY = 0.6
JUMP_STRENGTH = -10
CHASE_MEMORY_FRAMES = 180

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 50, 50)
YELLOW = (255, 220, 50)
ORANGE = (255, 140, 0)
LIGHT_ORANGE = (255, 180, 80)

class Enemy:
    def __init__(self, x, y, patrol_range=500):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.hitbox = self.rect.copy()
        self.vel_x = PATROL_SPEED
        self.vel_y = 0
        self.on_ground = False
        self.patrol_range = patrol_range
        self.start_x = x
        self.facing = 1
        self.player_spotted = False
        self.state = "PATROL"
        self.chaseTimer = 0

    def update(self, platforms, player):
        self.vel_y += GRAVITY

        seePlayer = self.check_line_of_sight(player)
        if seePlayer:
            self.player_spotted = True
            self.state = "CHASE"
            self.chaseTimer = CHASE_MEMORY_FRAMES
        else:
            self.player_spotted = False
            if self.state == "CHASE":
                self.chaseTimer -= 1
                if self.chaseTimer <= 0:
                    self.state = "PATROL"
                    self.start_x = self.rect.x

        currSpeed = CHASE_SPEED if self.state == "CHASE" else PATROL_SPEED

        if self.state == "CHASE":
            xDiff = player.rect.centerx - self.rect.centerx
            yDiff = abs(player.rect.centery - self.rect.centery)

            if abs(xDiff) > 4 or yDiff > 30:
                if xDiff > 0:
                    self.facing = 1
                    self.vel_x = currSpeed
                else:
                    self.facing = -1
                    self.vel_x = -currSpeed
            else:
                self.vel_x = 0
        else:
            if self.rect.x > self.start_x + self.patrol_range:
                self.vel_x = -PATROL_SPEED
                self.facing = -1
            elif self.rect.x < self.start_x - self.patrol_range:
                self.vel_x = PATROL_SPEED
                self.facing = 1

        if self.facing == 1:
            probeRect = pygame.Rect(self.rect.right, self.rect.bottom, 12, 2)
        else:
            probeRect = pygame.Rect(self.rect.left - 12, self.rect.bottom, 12, 2)

        groundAhead = any(probeRect.colliderect(p) and p.top >= self.rect.bottom - 2 for p in platforms)

        if self.on_ground and not groundAhead:
            if self.state == "CHASE":
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
            else:
                self.vel_x = -self.vel_x
                self.facing = -self.facing

        self.rect.x += self.vel_x
        self.hitbox.x = self.rect.x

        for p in platforms:
            if self.hitbox.colliderect(p):
                if self.vel_x > 0:
                    self.hitbox.right = p.left
                elif self.vel_x < 0:
                    self.hitbox.left = p.right
                self.rect.x = self.hitbox.x

                if self.state == "CHASE" and self.on_ground:
                    self.vel_y = JUMP_STRENGTH
                    self.on_ground = False
                else:
                    self.vel_x = -self.vel_x
                    self.facing = -self.facing

        self.rect.y += self.vel_y
        self.hitbox.y = self.rect.y
        self.on_ground = False

        for p in platforms:
            if self.hitbox.colliderect(p):
                if self.vel_y > 0:
                    self.hitbox.bottom = p.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.hitbox.top = p.bottom
                    self.vel_y = 0
                self.rect.y = self.hitbox.y

    def check_line_of_sight(self, player):
        visionRect = self.get_vision_rect()
        return visionRect.colliderect(player.rect)

    def get_vision_rect(self):
        visionRange = ENEMY_VISION_RANGE + (100 if self.state == "CHASE" else 0)
        
        if self.facing == 1:
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - ENEMY_VISION_HEIGHT // 2,
                visionRange,
                ENEMY_VISION_HEIGHT
            )
        else:
            return pygame.Rect(
                self.rect.left - ENEMY_VISION_RANGE,
                self.rect.centery - ENEMY_VISION_HEIGHT // 2,
                ENEMY_VISION_RANGE,
                ENEMY_VISION_HEIGHT
            )

    def draw(self, surface, camera=None):
        vision = self.get_vision_rect()

        if camera:
            drawRect = camera.apply(self.rect)
            visionRect = camera.apply(vision)
        else:
            drawRect = self.rect
            visionRect = vision
        
        vision_surface = pygame.Surface((visionRect.width, visionRect.height))
        vision_surface.set_alpha(60)
        if self.player_spotted:
            vision_surface.fill(RED)
        else:
            vision_surface.fill(YELLOW)
        surface.blit(vision_surface, visionRect.topleft)

        color = LIGHT_ORANGE if self.player_spotted else ORANGE
        pygame.draw.rect(surface, color, drawRect)
        pygame.draw.rect(surface, WHITE, drawRect, 2)

        eye_x = drawRect.centerx + (8 if self.facing == 1 else -8)
        eye_y = drawRect.y + 12
        pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 4)
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 2)