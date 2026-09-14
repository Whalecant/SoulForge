import pygame
import math
from collections import deque



PATROL_SPEED = 2.5
RETURN_SPEED = 3.75
CHASE_SPEED = 5
ENEMY_VISION_RANGE = 250
ENEMY_VISION_HEIGHT = 80
GRAVITY = 0.6
JUMP_STRENGTH = -15
CHASE_MEMORY_FRAMES = 180

# # BRACKEYS MY GOAT https://www.youtube.com/watch?v=jvtFUfJ6CP8
REPATH_INTERVAL_FRAMES = 20  # Re-path every ~0.3 seconds at 60 FPS
NEXT_WAYPOINT_DIST = 20      # Distance threshold to switch to next node
NEXT_WAYPOINT_DIST_Y = 40
WAYPOINT_STUCK_FRAMES = 90        # ~1.5s making no progress on a node before trying another route
NODE_BLOCK_DURATION_FRAMES = 300  # ~5s before a blocked node becomes usable again

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
ORANGE = (255, 140, 0)
LIGHT_ORANGE = (255, 180, 80)
CYAN = (40, 180, 90)
YELLOW = (255, 220, 50)
GREEN = (50, 200, 50)

class Enemy:
    def __init__(self, x, y, patrol_range=500, waypoints=None):
        self.rect = pygame.Rect(x, y, 30, 40)
        self.hitbox = self.rect.copy()
        self.vel_x = PATROL_SPEED
        self.vel_y = 0
        self.on_ground = False
        self.patrol_range = patrol_range
        self.start_x = x
        self.start_y = y
        self.spawn_x = x
        self.spawn_y = y + 30
        self.facing = 1

        self.state = "PATROL"
        self.chaseTimer = 0
        self.player_spotted = False
        self.lastKnownX = None
        self.lastKnownY = None

        self.hasdoubleJumped = False
        self.doubleJumpCd = 0

        self.waypoints = waypoints or {}
        self.path = []                     
        self.current_waypoint_idx = 0     
        self.repath_timer = 0
        self.waypoint_stall_timer = 0
        self.blocked_nodes = {}   # node_id -> frames remaining before it's usable again

        pygame.font.init()
        self.font = pygame.font.SysFont("Consolas", 14, bold=True)

    def update(self, platforms, player, forceChase = False):
        self.vel_y += GRAVITY

        if self.blocked_nodes:
            for node in list(self.blocked_nodes.keys()):
                self.blocked_nodes[node] -= 1
                if self.blocked_nodes[node] <= 0:
                    del self.blocked_nodes[node]

        if self.doubleJumpCd > 0:
            self.doubleJumpCd -= 1

        seePlayer = self.check_line_of_sight(player, platforms)

        if forceChase or seePlayer:
            if self.state == "RETURNING":
                self.clear_path()
            self.player_spotted = True
            self.state = "CHASE"
            self.chaseTimer = CHASE_MEMORY_FRAMES
            self.lastKnownX = player.rect.centerx
            self.lastKnownY = player.rect.centery
        else:
            self.player_spotted = False
            if self.state == "CHASE":
                self.chaseTimer -= 1
                if self.chaseTimer <= 0:
                    self.state = "RETURNING"
                    self.clear_path()
                    self.lastKnownX = None
                    self.lastKnownY = None

        if self.state == "CHASE":
            currSpeed = CHASE_SPEED
        elif self.state == "RETURNING":
            currSpeed = RETURN_SPEED
        else:
            currSpeed = PATROL_SPEED

        targetYCheck = None

        if self.state == "CHASE":

            if seePlayer or self.chaseTimer > 90:
                self.clear_path()
                self.moveTowards(player.rect.centerx, currSpeed)
                targetYCheck = player.rect.centery
            else:
                self.repath_timer += 1
                if self.repath_timer >= REPATH_INTERVAL_FRAMES:
                    self.repath_timer = 0
                    if self.lastKnownX is not None and self.lastKnownY is not None:
                        self.update_path_to(self.lastKnownX, self.lastKnownY)

                target_x, target_y = self.get_current_waypoint_pos()
                if target_x is not None:
                    self.moveTowards(target_x, currSpeed)
                    targetYCheck = target_y

                    dist_x = abs(self.rect.centerx - target_x)
                    dist_y = abs(self.rect.centery - target_y)
                    if dist_x < NEXT_WAYPOINT_DIST and dist_y < NEXT_WAYPOINT_DIST_Y and self.on_ground:
                        self.current_waypoint_idx += 1
                        self.waypoint_stall_timer = 0
                    else:
                        self.waypoint_stall_timer += 1
                        if self.waypoint_stall_timer >= WAYPOINT_STUCK_FRAMES and self.lastKnownX is not None:
                            self.block_current_node_and_repath(self.lastKnownX, self.lastKnownY)
                elif self.lastKnownX is not None:
                    self.moveTowards(self.lastKnownX, currSpeed)

            self.tryJumpTowards(targetYCheck)

        elif self.state == "RETURNING":

            if not self.path and not getattr(self, 'has_returned_path', False):
                self.update_path_to(self.spawn_x, self.spawn_y)
                self.has_returned_path = True

            target_x, target_y = self.get_current_waypoint_pos()

            if target_x is not None:
                self.moveTowards(target_x, currSpeed)
                targetYCheck = target_y

                dist_x = abs(self.rect.centerx - target_x)
                dist_y = abs(self.rect.centery - target_y)

                if dist_x < NEXT_WAYPOINT_DIST and dist_y < NEXT_WAYPOINT_DIST_Y and self.on_ground:
                    self.current_waypoint_idx += 1
                    self.waypoint_stall_timer = 0
                else:
                    self.waypoint_stall_timer += 1
                    if self.waypoint_stall_timer >= WAYPOINT_STUCK_FRAMES:
                        self.block_current_node_and_repath(self.spawn_x, self.spawn_y)
            else:
                self.moveTowards(self.spawn_x, currSpeed)
                targetYCheck = self.spawn_y

                self.waypoint_stall_timer += 1
                if self.waypoint_stall_timer >= WAYPOINT_STUCK_FRAMES * 5:
                    # Can't physically get back to spawn from here - stop trying
                    # and just settle into patrol wherever it currently is.
                    self.waypoint_stall_timer = 0
                    self.blocked_nodes.clear()
                    self.clear_path()
                    self.has_returned_path = False
                    self.start_x = self.rect.centerx
                    self.state = "PATROL"
                    self.vel_x = PATROL_SPEED * self.facing

            distToSpawn = math.hypot(self.spawn_x - self.rect.centerx, self.spawn_y - self.rect.centery)
            if distToSpawn < NEXT_WAYPOINT_DIST or (abs(self.spawn_x - self.rect.centerx) < 5 and abs(self.spawn_y - self.rect.centery) < NEXT_WAYPOINT_DIST_Y):
                self.clear_path()
                self.has_returned_path = False
                self.rect.centerx = self.spawn_x
                self.state = "PATROL"
                self.vel_x = PATROL_SPEED * self.facing

            self.tryJumpTowards(targetYCheck)

        elif self.state == "PATROL":
            if self.rect.centerx >= self.start_x + self.patrol_range:
                self.facing = -1
            elif self.rect.centerx <= self.start_x - self.patrol_range:
                self.facing = 1

            self.vel_x = PATROL_SPEED * self.facing

        probeX = self.rect.right if self.facing == 1 else self.rect.left - 12
        probeRect = pygame.Rect(probeX, self.rect.bottom, 12, 2)
        groundAhead = any(probeRect.colliderect(p) and p.top >= self.rect.bottom - 2 for p in platforms)

        followingPath = self.state == "CHASE" or (self.state == "RETURNING" and self.path)

        if self.on_ground and not groundAhead:
            if followingPath and abs(self.vel_x) > 0:
                self.vel_y = JUMP_STRENGTH
                self.on_ground = False
            else:
                self.facing *= -1
                self.vel_x = PATROL_SPEED * self.facing

        self.rect.x += self.vel_x
        self.hitbox.x = self.rect.x

        for p in platforms:
            if self.hitbox.colliderect(p):
                if self.vel_x > 0:
                    self.hitbox.right = p.left
                elif self.vel_x < 0:
                    self.hitbox.left = p.right

                self.rect.x = self.hitbox.x

                if followingPath:
                    if self.on_ground:
                        self.vel_y = JUMP_STRENGTH
                        self.on_ground = False
                else:
                    self.facing *= -1
                    self.vel_x = PATROL_SPEED * self.facing

        self.rect.y += self.vel_y
        self.hitbox.y = self.rect.y
        self.on_ground = False

        for p in platforms:
            if self.hitbox.colliderect(p):
                if self.vel_y > 0:
                    self.hitbox.bottom = p.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.hasdoubleJumped = False
                elif self.vel_y < 0:
                    self.hitbox.top = p.bottom
                    self.vel_y = 0
                self.rect.y = self.hitbox.y

    def moveTowards(self, target_x, speed):
        xDiff = target_x - self.rect.centerx
        if abs(xDiff) > 3:
            self.facing = 1 if xDiff > 0 else -1
            self.vel_x = speed * self.facing
        else:
            self.vel_x = 0

    def tryJumpTowards(self, targetYCheck):
        if targetYCheck is None or (targetYCheck - self.rect.centery) >= -10:
            return
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
        elif not self.hasdoubleJumped and self.doubleJumpCd == 0:
            self.vel_y = JUMP_STRENGTH * 0.9
            self.hasdoubleJumped = True
            self.doubleJumpCd = 20
    def update_path_to(self, target_x, target_y):
        if not self.waypoints:
            self.clear_path()
            return

        available = {n: d for n, d in self.waypoints.items() if n not in self.blocked_nodes}
        if not available:
            available = self.waypoints  # everything's blocked - fall back rather than give up entirely

        start_node = min(
            available.keys(),
            key=lambda n: (available[n][0] - self.rect.centerx) ** 2 + (available[n][1] - self.rect.centery) ** 2
        )
        end_node = min(
            available.keys(),
            key=lambda n: (available[n][0] - target_x) ** 2 + (available[n][1] - target_y) ** 2
        )

        if start_node == end_node:
            self.path = [start_node]
            self.current_waypoint_idx = 0
            return

        queue = deque([[start_node]])
        visited = {start_node}

        while queue:
            current_path = queue.popleft()
            node = current_path[-1]

            if node == end_node:
                self.path = current_path
                self.current_waypoint_idx = 0
                return

        
            #BFS pathfinding, checks nearest one first and expands from there, good for finding shortest path
            neighbors = self.waypoints[node][2] if len(self.waypoints[node]) > 2 else []
            for neighbor in neighbors:
                if neighbor in available and neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(current_path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        self.clear_path()

    def get_current_waypoint_pos(self):
        if self.path and self.current_waypoint_idx < len(self.path):
            node_id = self.path[self.current_waypoint_idx]
            if node_id in self.waypoints:
                return self.waypoints[node_id][0], self.waypoints[node_id][1]
        return None, None

    def clear_path(self):
        self.path = []
        self.current_waypoint_idx = 0
        self.has_returned_path = False
        self.waypoint_stall_timer = 0

    def block_current_node_and_repath(self, final_x, final_y):
        if self.path and self.current_waypoint_idx < len(self.path):
            stuck_node = self.path[self.current_waypoint_idx]
            self.blocked_nodes[stuck_node] = NODE_BLOCK_DURATION_FRAMES
        self.waypoint_stall_timer = 0
        self.update_path_to(final_x, final_y)

    def hasLOStoPlayer(self, player, platforms):
        startPoint = self.rect.center
        endPoint = player.rect.center

        for p in platforms:
            if p.clipline(startPoint, endPoint):
                return False
        return True

    def check_line_of_sight(self, player, platforms = None):
        if platforms is not None:
            if not self.hasLOStoPlayer(player, platforms):
                return False

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        if (dx * dx + dy * dy) < 22500:
            return True

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
                self.rect.left - visionRange,
                self.rect.centery - ENEMY_VISION_HEIGHT // 2,
                visionRange,
                ENEMY_VISION_HEIGHT
            )

    def draw(self, surface, camera=None):
        vision = self.get_vision_rect()

        drawRect = camera.apply(self.rect) if camera else self.rect
        visionRect = camera.apply(vision) if camera else vision

        bodyColor = RED if self.state == "CHASE" else (ORANGE if self.state == "RETURNING" else CYAN)
        visionColor = RED if self.state == "CHASE" else (LIGHT_ORANGE if self.state == "RETURNING" else YELLOW)

        vision_surface = pygame.Surface((visionRect.width, visionRect.height))
        vision_surface.set_alpha(60)
        vision_surface.fill(visionColor)
        surface.blit(vision_surface, visionRect.topleft)

        pygame.draw.rect(surface, bodyColor, drawRect)
        pygame.draw.rect(surface, WHITE, drawRect, 2)

        eye_x = drawRect.centerx + (8 if self.facing == 1 else -8)
        eye_y = drawRect.y + 12
        pygame.draw.circle(surface, WHITE, (eye_x, eye_y), 4)
        pygame.draw.circle(surface, BLACK, (eye_x, eye_y), 2)

        if self.state == "CHASE":
            seconds_left = max(0, self.chaseTimer / 60.0)
            timer_text = f"{self.chaseTimer}f ({seconds_left:.1f}s)"
            text_surface = self.font.render(timer_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(drawRect.centerx, drawRect.top - 12))
            surface.blit(text_surface, text_rect)

    def draw_waypoints(self, surface, camera=None):
        spawn_rect = pygame.Rect(self.spawn_x - 15, self.spawn_y - 20, 30, 40)
        draw_spawn = camera.apply(spawn_rect) if camera else spawn_rect

        pygame.draw.rect(surface, GREEN, draw_spawn, 2)
        pygame.draw.line(surface, GREEN, (draw_spawn.centerx - 8, draw_spawn.centery), (draw_spawn.centerx + 8, draw_spawn.centery), 2)
        pygame.draw.line(surface, GREEN, (draw_spawn.centerx, draw_spawn.centery - 8), (draw_spawn.centerx, draw_spawn.centery + 8), 2)

        if not self.waypoints:
            return

        for node_id, data in self.waypoints.items():
            x, y, neighbors = data[:3]
            point = (x, y)
            draw_pos = camera.apply_point(point) if camera and hasattr(camera, 'apply_point') else (camera.apply(pygame.Rect(x, y, 1, 1)).topleft if camera else point)

            color = (255, 50, 50) if self.path and node_id in self.path else (255, 0, 255)
            pygame.draw.circle(surface, color, draw_pos, 5)

            for n_id in neighbors:
                if n_id in self.waypoints:
                    nx, ny = self.waypoints[n_id][:2]
                    n_draw_pos = camera.apply_point((nx, ny)) if camera and hasattr(camera, 'apply_point') else (camera.apply(pygame.Rect(nx, ny, 1, 1)).topleft if camera else (nx, ny))
                    pygame.draw.line(surface, (0, 255, 255), draw_pos, n_draw_pos, 1)