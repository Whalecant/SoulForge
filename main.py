import pygame
import sys
from player import Player # type: ignore
from saveManager import SaveManager, Button # type: ignore
from camera import Camera #type: ignore
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

DIRECTION_KEYS = {
    "left": [pygame.K_LEFT, pygame.K_a],
    "right": [pygame.K_RIGHT, pygame.K_d],
}

current_state = MENU
current_slot = 0

save_manager = SaveManager(SAVE_FILE)
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

def build_level(level):
    rooms = [
        pygame.Rect(0, 0, 1000, 750),
        pygame.Rect(1000, 0, 1000, 750),
        pygame.Rect(1000, -750, 1000, 750), 
        #build rooms off of this :thumbsUp:
    ]

    doors = [
        {
            "trigger": pygame.Rect(960, 550, 40, 100),
            "targetRoom": 1,
            "type": "directional",
            "direction": "right",
            "spawnX": 1000,
            "keepY": True,
            "armed": False,
        },
        {
            "trigger": pygame.Rect(1000, 550, 40, 100),
            "targetRoom": 0,
            "type": "directional",
            "direction": "left",
            "spawnX": 970,
            "keepY": True,
            "armed": False, 
        },
        {
            "trigger": pygame.Rect(1400, 0, 100, 20),
            "targetRoom": 2,
            "type": "touch",
            "spawnY": 730,
            "keepX": True,
            "armed": False,
        },
        {
            "trigger": pygame.Rect(1400, 730, 100, 20),
            "targetRoom": 1,
            "type": "touch",
            "spawnY": 0,
            "keepX": True,
            "armed": False,
        }
    ]

    platforms = [
        #room 0
        pygame.Rect(0, 710, 1000, 40),
        pygame.Rect(200, 550, 150, 20),

        #room 1
        pygame.Rect(1000, 710, 1000, 40),
        pygame.Rect(1200, 450, 150, 20),
    ]

    return {
        "rooms": rooms,
        "doors": doors,
        "platforms": platforms
    }

levelData = build_level(1)
rooms = levelData["rooms"]
doors = levelData["doors"]
platforms = levelData["platforms"]
currRoom = 0

player = Player(100, 400)

def draw_text(text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)

btn_start = Button("START", SCREEN_WIDTH // 2 - 100, 250, 200, 55, BLUE, LIGHT_BLUE, menu_font)
btn_quit = Button("QUIT", SCREEN_WIDTH // 2 - 100, 330, 200, 55, RED, LIGHT_RED, menu_font)

btn_back_menu = Button("BACK", SCREEN_WIDTH // 2 - 100, 500, 200, 55, GRAY, LIGHT_BLUE,menu_font)

btn_resume = Button("RESUME", SCREEN_WIDTH // 2 - 100, 250, 200, 55, GREEN, LIGHT_GREEN, menu_font)
btn_main_menu = Button("MAIN MENU", SCREEN_WIDTH // 2 - 100, 330, 200, 55, RED, LIGHT_RED, menu_font)

slot_buttons = []
reset_buttons = []
for i in range(3):
    y = 180 + i * 100
    slot_buttons.append(Button(f"SLOT {i+1}", SCREEN_WIDTH // 2 - 200, y, 250, 60, BLUE, LIGHT_BLUE, small_font))
    reset_buttons.append(Button("RESET", SCREEN_WIDTH // 2 + 70, y, 130, 60, RED, LIGHT_RED, small_font))

def start_game(slot_index):
    global current_slot, player, levelData, rooms, doors, platforms, currRoom
    current_slot = slot_index
    slot = save_manager.get_slot(slot_index)
    level = slot["level"]

    levelData = build_level(level)
    rooms = levelData["rooms"]
    doors = levelData["doors"]
    platforms = levelData["platforms"]

    pX = slot["player_x"]
    pY = slot["player_y"]
    currRoom = 0

    for i, room in enumerate(rooms):
        if room.left <= pX < room.right and room.top <= pY < room.bottom:
            currRoom = i
            break

    player = Player(pX, pY)
    camera.snapToRoom(rooms[currRoom])
    return PLAYING

running = True
while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if current_state == PLAYING:
                current_state = PAUSED
            elif current_state == PAUSED:
                current_state = PLAYING
            elif current_state == LEVEL_SELECT:
                current_state = MENU

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
                save_manager.write_slot(current_slot, slot["level"], player.rect.x, player.rect.y)
                current_state = MENU

    if current_state == PLAYING:
        camera.update()

        if not camera.isTrans:
            keys = pygame.key.get_pressed()
            player.input(keys)

            for door in doors:
                touch = player.rect.colliderect(door["trigger"])

                if door["type"] == "directional":
                    keyHeld = any(keys[k] for k in DIRECTION_KEYS[door["direction"]])
                    satisfied = touch and keyHeld
                else:
                    satisfied = touch

                if satisfied and not door["armed"] and player.doorCd <= 0:
                    currRoom = door["targetRoom"]
                    camera.targetRoom(rooms[currRoom])

                    if not door.get("keepX", False):
                        player.rect.x = door["spawnX"]
                    if not door.get("keepY", False):
                        player.rect.y = door["spawnY"]

                    player.doorCd = 30

                    for d in doors:
                        stillTouch = player.rect.colliderect(d["trigger"])
                        if d["type"] == "directional":
                            stillKeyheld = any(keys[k] for k in DIRECTION_KEYS[d["direction"]])
                            d["armed"] = stillTouch and stillKeyheld
                        else:
                            d["armed"] = stillTouch

                    break
                else:
                    door["armed"] = satisfied
        
        player.update(platforms, rooms[currRoom], camera.isTrans)

        if player.rect.top > 2000: #change this later for whenever more rooms are added upwards
            slot = save_manager.get_slot(current_slot)
            save_manager.write_slot(current_slot, slot["level"], 100, 400)
            player = Player(100, 400)

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

    elif current_state == PLAYING:
        screen.fill((30, 30, 60))
        for p in platforms:
            screenRect = camera.apply(p)
            pygame.draw.rect(screen, GREEN, screenRect)
            pygame.draw.rect(screen, WHITE, screenRect, 2)

        player.draw(screen, camera)
        hint = small_font.render("ESC to pause", True, WHITE)
        screen.blit(hint, (10, 10))

    elif current_state == PAUSED:
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

    pygame.display.flip()
    clock.tick(FPS)

save_manager.save()
pygame.quit()
sys.exit()