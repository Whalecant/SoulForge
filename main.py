import pygame
import copy
import sys
from player import Player # type: ignore
from saveManager import SaveManager, Button # type: ignore
from camera import Camera #type: ignore
from hackTerminal import Terminal #type: ignore
from enemy import Enemy #type: ignore
from door import Door #type: ignore
#imma be honest, idk why the three things above are that bugged lol

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Stealth Platformer")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (50, 100, 200)
LIGHT_BLUE = (100, 150, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (60, 60, 60)
RED = (200, 50, 50)
LIGHT_RED = (255, 100, 100)
GREEN = (50, 200, 50)
LIGHT_GREEN = (100, 255, 100)
YELLOW = (255, 220, 50)
PURPLE = (128, 0, 128)
LIGHT_PURPLE = (203, 195, 227)

title_font = pygame.font.Font(None, 70)
menu_font = pygame.font.Font(None, 45)
small_font = pygame.font.Font(None, 30)

clock = pygame.time.Clock()
FPS = 60

SAVE_FILE = "save_data.json"

MENU = "menu"
LEVEL_SELECT = "level_select"
PLAYING = "playing"
PAUSED = "paused"
HACKING = "hacking"
GAME_OVER = "game_over"

PREVIOUS_STATE = PLAYING

START_X = 100
START_Y = 675

DIRECTION_KEYS = {
    "left": [pygame.K_LEFT, pygame.K_a],
    "right": [pygame.K_RIGHT, pygame.K_d],
}

PUZZLES = [ #add more accordingly
    #Room 0 Puzzle (as well as example for if you wanna use fixed positions)
    {
        "keyPos": [5, 1],
        "exitPos": [5, 7],
        "walls": [[0, 2], [1, 2], [2, 2], [3, 4], [4, 4], [5, 4]],
        "dummies": [[1, 4], [3, 2]]
    },
    #Room 1 Puzzle (as well as example for if you wanna use randomized positions)
    {
        "walls": [[1, 1], [1, 2], [1, 3], [1, 4], [3, 3], [3, 4], [3, 5], [3, 6]],
        "dummyCount": 3
    },
    #Room 2 Puzzle
    {
        "walls": [[2, 0], [2, 1], [2, 2], [2, 3], [4, 4], [4, 5], [4, 6], [4, 7]],
        "dummyCount": 4
    }

]

# for the enemy AI (this will be hell :DDDD)
WAYPOINTS = {
    # --- ROOM 0 (World X: 0 - 1000, Y: 0 - 750) ---
    "r0_floor_left": (175, 685, ["r0_floor_right", "r0_plat_mid"]),
    "r0_floor_right": (650, 685, ["r0_floor_left", "r0_plat_high"]),
    "r0_floor_right_backup": (725, 685, ["r0_floor_right"]),
    "r0_floor_left_backup": (400, 500, ["r0_floor_left", "r0_plat_mid", "r0_floor_right"]),
    "r0_plat_mid": (275, 510, ["r0_floor_left", "r0_floor_left_backup"]),
    "r0_plat_high": (830, 610, ["r0_floor_right", "r1_plat_low"]),
    "r0_trans": (475, 685, ["r0_floor_left", "r0_floor_right", "r2_plat_4"]),

    # --- ROOM 1 (World X: 1000 - 2000, Y: 0 - 750) ---
    "r1_plat_low": (1125, 510, ["r0_plat_high", "r1_floor", "r1_plat_mid"]),
    "r1_floor": (1500, 685, ["r1_plat_low"]),
    "r1_plat_mid": (1325, 410, ["r1_plat_low", "r1_plat_high"]),
    "r1_plat_high": (1500, 210, ["r1_plat_mid"]),

    # --- ROOM 2 (World X: 0 - 1000, Y: 750 - 1500) ---
    "r2_floor": (400, 1435, ["r2_floor_right", "r2_floor_left_air", "r2_floor_above"]),
    "r2_floor_above": (450, 1375, ["r2_floor", "r2_plat_2"]),
    "r2_plat_2": (650, 1310, ["r2_floor_above", "r2_plat_1", "r2_floor_right"]),
    "r2_plat_1": (300, 1185, ["r2_plat_4", "r2_plat_2", "r2_floor_left_air"]),
    "r2_plat_3": (550, 1010, ["r2_plat_4", "r2_plat_1"]),
    "r2_plat_4": (475, 835, ["r2_plat_1", "r2_plat_3", "r0_trans"]),
    "r2_floor_right": (900, 1400, ["r2_floor", "r2_plat_2"]),
    "r2_floor_left_air": (125, 1300, ["r2_floor", "r2_plat_1"]),
}

current_state = MENU
current_slot = 0

save_manager = SaveManager(SAVE_FILE)
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

terminals = []
activeTerminal = None

flashTimer = 0
alarmOverlay = False

def build_level(level):
    rooms = [
        pygame.Rect(0, 0, 1000, 750),
        pygame.Rect(1000, 0, 1000, 750),
        pygame.Rect(0, 750, 1000, 750), 
        #build rooms off of this :thumbsUp:
    ]

    platforms = [
        #room 0
        pygame.Rect(0, 725, 450, 40),
        pygame.Rect(550, 725, 450, 40),
        pygame.Rect(200, 550, 150, 20),
        pygame.Rect(700, 650, 260, 20),
        pygame.Rect(0, 0, 50, 750),
        pygame.Rect(0, 0, 2000, 25),

        #room 1
        pygame.Rect(1000, 725, 1000, 40),
        pygame.Rect(1050, 550, 150, 20),
        pygame.Rect(1250, 450, 150, 20),
        pygame.Rect(1400, 250, 200, 50),
        pygame.Rect(1700, 100, 200, 650),

        #room 2
        pygame.Rect(0, 1475, 1000, 40),
        pygame.Rect(200, 1225, 200, 30),
        pygame.Rect(500, 1350, 300, 30),
        pygame.Rect(500, 1050, 100, 30),
        pygame.Rect(350, 875, 250, 30),
        pygame.Rect(0, 750, 50, 1000),
        pygame.Rect(175, 1325, 75, 25)
    ]

    terminals = [
        Terminal(x = 250, y = 500, **copy.deepcopy(PUZZLES[0]) ,timeLimit = 20.0),
        Terminal(x = 1300, y = 400, **copy.deepcopy(PUZZLES[1]),timeLimit = 20.0),
        Terminal(x = 300, y = 1175, **copy.deepcopy(PUZZLES[2]),timeLimit = 20.0),
    ]

    doors = [
        Door(x = 450, y = 725, width=100, height = 20, openX=-100, openY = -0, requiredTerminals=[terminals[0]]),
        Door(x = 990, y = 25, width = 20, height = 700, openX = 0, openY = -800, requiredTerminals=[terminals[0], terminals[2]]),
        Door(x = 1700, y = 25, width = 50, height = 75, openX = 0, openY = -100, requiredTerminals=[terminals[0], terminals[1], terminals[2]]),
    ]

    enemies = [
        Enemy(750, 600, patrol_range = 500, waypoints = WAYPOINTS),
        Enemy(600, 1300, patrol_range = 500, waypoints = WAYPOINTS),
    ]

    return {
        "rooms": rooms,
        "platforms": platforms,
        "terminals": terminals,
        "enemies": enemies,
        "doors": doors,
    }

levelData = build_level(0)
rooms = levelData["rooms"]
platforms = levelData["platforms"]
terminals = levelData["terminals"]
enemies = levelData["enemies"]
doors = levelData["doors"]
currRoom = 0

player = Player(100, 675)

def draw_text(text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)

btn_start = Button("START", SCREEN_WIDTH // 2 - 100, 250, 200, 55, BLUE, LIGHT_BLUE, menu_font)
btn_quit = Button("QUIT", SCREEN_WIDTH // 2 - 100, 330, 200, 55, RED, LIGHT_RED, menu_font)

btn_back_menu = Button("BACK", SCREEN_WIDTH // 2 - 100, 500, 200, 55, GRAY, LIGHT_BLUE,menu_font)

btn_resume = Button("RESUME", SCREEN_WIDTH // 2 - 100, 250, 200, 55, GREEN, LIGHT_GREEN, menu_font)
btn_main_menu = Button("MAIN MENU", SCREEN_WIDTH // 2 - 100, 330, 200, 55, RED, LIGHT_RED, menu_font)

respawnBtn = Button("RESPAWN", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, 200, 50, RED, LIGHT_RED, menu_font)
gameOverMenuBtn = Button("MAIN MENU", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 55, GREEN, LIGHT_GREEN, menu_font)

slot_buttons = []
reset_buttons = []
for i in range(3):
    y = 180 + i * 100
    slot_buttons.append(Button(f"SLOT {i+1}", SCREEN_WIDTH // 2 - 200, y, 250, 60, BLUE, LIGHT_BLUE, small_font))
    reset_buttons.append(Button("RESET", SCREEN_WIDTH // 2 + 70, y, 130, 60, RED, LIGHT_RED, small_font))

def resetPlayerPos(p):
    global currRoom
    p.rect.x = START_X
    p.rect.y = START_Y
    p.vel_x = 0
    p.vel_y = 0
    currRoom = 0
    camera.snapToRoom(rooms[currRoom])

def resetLevel():
    global player, levelData, rooms, platforms, terminals, enemies, currRoom, doors

    levelData = build_level(0)
    rooms = levelData["rooms"]
    platforms = levelData["platforms"]
    terminals = levelData["terminals"]
    enemies = levelData["enemies"]
    doors = levelData["doors"]

    player = Player(START_X, START_Y)
    currRoom = 0
    camera.snapToRoom(rooms[currRoom])

def start_game(slot_index):
    global current_slot, player, levelData, rooms, platforms, currRoom, terminals, enemies, doors
    current_slot = slot_index
    slot = save_manager.get_slot(slot_index)
    level = slot["level"]

    levelData = build_level(level)
    rooms = levelData["rooms"]
    platforms = levelData["platforms"]
    terminals = levelData["terminals"]
    enemies = levelData["enemies"]
    doors = levelData["doors"]

    if slot["exists"] and "terminals" in slot:
        savedTerminals = slot["terminals"]
        for i, t in enumerate(terminals):
            if i <  len(savedTerminals):
                t.loadDict(savedTerminals[i])

    if not slot.get("exists"):
        pX, pY = 100, 675
    else:
        pX = slot["player_x"]
        pY = slot["player_y"]
    currRoom = 0

    for i, room in enumerate(rooms):
        if room.left <= pX < room.right and room.top <= pY < room.bottom:
            currRoom = i
            break

    player = Player(pX, pY)
    print(f"SPAWNED AT: {player.rect.x}, {player.rect.y}")
    camera.snapToRoom(rooms[currRoom])
    return PLAYING

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if current_state == HACKING and activeTerminal:
                activeTerminal.input(event)

            if event.key == pygame.K_ESCAPE:
                if current_state == PLAYING or current_state == HACKING:
                    PREVIOUS_STATE = current_state
                    current_state = PAUSED
                elif current_state == PAUSED:
                    current_state = PREVIOUS_STATE
                elif current_state == LEVEL_SELECT:
                    current_state = MENU

            elif event.key == pygame.K_e:
                if current_state == PLAYING:
                    for t in terminals:
                        if t.canInteract(player.rect) and not t.isHacked:
                            activeTerminal = t
                            current_state = HACKING
                            activeTerminal.hasStarted = True

                            if activeTerminal.timeLeft == activeTerminal.timeLimit:
                                activeTerminal.timeLeft -= 0.01 #just allows for some minor consistency of logic loops
                                
                            break
                elif current_state == HACKING:
                    activeTerminal = None
                    current_state = PLAYING

        if current_state == MENU:
            if btn_start.is_clicked(event):
                current_state = LEVEL_SELECT
            if btn_quit.is_clicked(event):
                running = False
        elif current_state == LEVEL_SELECT:
            for i, btn in enumerate(slot_buttons):
                if btn.is_clicked(event):
                    current_state = start_game(i)
            for i, btn in enumerate(reset_buttons):
                if btn.is_clicked(event):
                    save_manager.reset_slot(i)
            if btn_back_menu.is_clicked(event):
                current_state = MENU
        elif current_state == PAUSED:
            if btn_resume.is_clicked(event):
                current_state = PLAYING
            if btn_main_menu.is_clicked(event):
                slot = save_manager.get_slot(current_slot)

                terminalsData = [t.saveDict() for t in terminals]

                save_manager.write_slot(current_slot, slot["level"], player.rect.x, player.rect.y, terminalsData)
                current_state = MENU
        elif current_state == GAME_OVER:
            if respawnBtn.is_clicked(event):
                resetLevel()
                current_state = PLAYING
            if gameOverMenuBtn.is_clicked(event):
                resetLevel()
                current_state = MENU
        
    if current_state == PLAYING or current_state == HACKING:
        for t in terminals:

            autoExit = t.updateTimer(1 / FPS, t.hasStarted)

            if autoExit and current_state == HACKING and activeTerminal == t:
                activeTerminal = None
                current_state = PLAYING

        for door in doors:
            door.update(dt=1/FPS, isPause = (current_state == PAUSED))

        if current_state == PLAYING:
            camera.update()

            if not camera.isTrans:
                keys = pygame.key.get_pressed()
                moveInput = player.input(keys)

                activePhysicsPlatforms = platforms + [door.rect for door in doors]
                anyAlarm = any(t.alarmTriggered for t in terminals)

                for enemy in enemies:
                    enemy.update(activePhysicsPlatforms, player, forceChase = anyAlarm)
                    if enemy.hitbox.colliderect(player.rect):
                        current_state = GAME_OVER

            player.update(activePhysicsPlatforms, None, camera.isTrans, moveInput)

            playerCenter = player.rect.center
            for i, room in enumerate(rooms):
                if i != currRoom and room.collidepoint(playerCenter):
                    currRoom = i
                    camera.targetRoom(rooms[currRoom])
                    break
    
            if player.rect.top > 2000: #change this later for whenever more rooms are added upwards
                resetPlayerPos(player)

    anyAlarm = any(t.alarmTriggered for t in terminals)
    if anyAlarm:
        flashTimer += 1
        if flashTimer % 30 == 0:
            alarmOverlay = not alarmOverlay 
    else:
        flashTimer = 0
        alarmOverlay = False   

    if current_state == MENU:
        btn_start.update(mouse_pos)
        btn_quit.update(mouse_pos)
    elif current_state == LEVEL_SELECT:
        for btn in slot_buttons:
            btn.update(mouse_pos)
        for btn in reset_buttons:
            btn.update(mouse_pos)
        btn_back_menu.update(mouse_pos)
    elif current_state == PAUSED:
        btn_resume.update(mouse_pos)
        btn_main_menu.update(mouse_pos)
    elif current_state == GAME_OVER:
        respawnBtn.update(mouse_pos)
        gameOverMenuBtn.update(mouse_pos)

    if current_state == MENU:
        screen.fill(BLACK)
        draw_text("PLATFORMER", title_font, WHITE, (SCREEN_WIDTH // 2, 130))
        btn_start.draw(screen)
        btn_quit.draw(screen)

    elif current_state == LEVEL_SELECT:
        screen.fill(BLACK)
        draw_text("SELECT SAVE SLOT", menu_font, WHITE, (SCREEN_WIDTH // 2, 100))
        for i in range(3):
            slot = save_manager.get_slot(i)
            slot_buttons[i].draw(screen)
            reset_buttons[i].draw(screen)
            if slot["exists"]:
                info = f"Lv {slot['level']}  X:{slot['player_x']}  Y:{slot['player_y']}"
            else:
                info = "Empty"
            info_surf = small_font.render(info, True, YELLOW)
            screen.blit(info_surf, (SCREEN_WIDTH // 2 - 200, 180 + i * 100 + 65))
        btn_back_menu.draw(screen)

    elif current_state in (PLAYING, HACKING, PAUSED, GAME_OVER):
        screen.fill((30, 30, 60))
        for p in platforms:
            screenRect = camera.apply(p)
            pygame.draw.rect(screen, GREEN, screenRect)
            #pygame.draw.rect(screen, WHITE, screenRect, 2)
        
        for door in doors:
            door.draw(screen, camera)

        for t in terminals:
            t.draw(screen, camera)
        
        if not camera.isTrans:
            for door in doors:
                door.draw(screen, camera)

            for enemy in enemies:
                enemy.draw(screen, camera)
                enemy.draw_waypoints(screen, camera)

        player.draw(screen, camera)
        hint = small_font.render("ESC to pause", True, WHITE)
        screen.blit(hint, (10, 10))

        if current_state == PLAYING:
            for t in terminals:
                if t.canInteract(player.rect) and not t.isHacked:
                    prompt = small_font.render("Press E to Hack", True, WHITE)
                    screen.blit(prompt, (SCREEN_WIDTH // 2 - 80, 50))
                    break

        if anyAlarm and alarmOverlay:
            redTint = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            redTint.set_alpha(80)
            redTint.fill(RED)
            screen.blit(redTint, (0, 0))

        if current_state == PAUSED:
            screen.fill((30, 30, 60))
            for p in platforms:
                screenRect = camera.apply(p)
                pygame.draw.rect(screen, GREEN, screenRect)
                pygame.draw.rect(screen, WHITE, screenRect, 2)
            player.draw(screen, camera)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            draw_text("PAUSED", title_font, WHITE, (SCREEN_WIDTH // 2, 150))
            btn_resume.draw(screen)
            btn_main_menu.draw(screen)

        elif current_state == GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            draw_text("YOU HAVE BEEN CAUGHT!", title_font, RED, (SCREEN_WIDTH // 2, 220))
            respawnBtn.draw(screen)
            gameOverMenuBtn.draw(screen)

        elif current_state == HACKING and activeTerminal:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(220)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            draw_text("System Terminal Hack", menu_font, LIGHT_PURPLE, ((SCREEN_WIDTH // 2, 35)))

            if activeTerminal.isHacked:
                statusText = "Acces Granted"
                statusColor = GREEN
            elif activeTerminal.alarmTriggered:
                statusText = "Alarm Triggered"
                statusColor = RED
            else:
                statusText = "Collect Key Code and Head to the Exit"
                statusColor = WHITE

            draw_text(statusText, menu_font, statusColor, (SCREEN_WIDTH // 2, 75))

            activeTerminal.drawMinigame(screen, SCREEN_WIDTH, SCREEN_HEIGHT, small_font)

            if activeTerminal.timeLeft < 2.5:
                timeColor = RED
            elif activeTerminal.timeLeft < 5.0:
                timeColor = YELLOW
            else:
                timeColor = WHITE

            draw_text(f"Time Remaining: {activeTerminal.timeLeft:.1f}s", menu_font, timeColor, (SCREEN_WIDTH // 2, 680))
            
            draw_text("Press [E] to exit", small_font, WHITE, (SCREEN_WIDTH // 2, 720))
                        
            

    pygame.display.flip()
    clock.tick(FPS)

save_manager.save()
pygame.quit()
sys.exit()