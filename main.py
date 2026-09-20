import pygame
import copy
import sys
from player import Player # type: ignore
from saveManager import SaveManager, Button # type: ignore
from camera import Camera #type: ignore
from hackTerminal import Terminal #type: ignore
from enemy import Enemy #type: ignore
from door import Door #type: ignore
from lore import LoreKey, JournalManager, NotificationManager, JOURNAL_CHAPTERS, wrap_text #type: ignore
from warden import Warden #type: ignore
from checkpointManager import Checkpoint #type: ignore
from buildLevel import build_level, WARDEN_ARENA_ROOMS, ENDING_ROOM_INDEX #type: ignore
#imma be honest, idk why the three things above are that bugged lol

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Soul Forge")

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
ORANGE = (255, 140, 0)
LIGHT_ORANGE = (255, 180, 80)
PURPLE = (120, 60, 180)
LIGHT_PURPLE = (180, 120, 255)
DARK_PURPLE = (40, 20, 60)
CYAN = (100, 220, 220)
PALE_YELLOW = (255, 250, 200)

title_font = pygame.font.Font(None, 70)
menu_font = pygame.font.Font(None, 45)
small_font = pygame.font.Font(None, 30)
tiny_font = pygame.font.Font(None, 22)

clock = pygame.time.Clock()
FPS = 60

SAVE_FILE = "save_data.json"

#change these values later
WARDEN_ARENA_ROOMS = [20, 21, 22, 23]
ENDING_ROOM_INDEX = 24

MENU = "menu"
LEVEL_SELECT = "level_select"
PLAYING = "playing"
PAUSED = "paused"
HACKING = "hacking"
GAME_OVER = "game_over"
JOURNAL = "journal"
READING = "reading"
WARDEN_DIALOGUE = "warden_dialogue"
WARDEN_INTRO = "warden_intro"
ENDING = "ending"

PREVIOUS_STATE = PLAYING

wardenIntroStage = None
wardenIntroTimer = 0.0
wardenIntroDoor = None
WARDEN_INTRO_FADE_TIME = 1.0
WARDEN_INTRO_HOLD_TIME = 0.5
WARDEN_INTRO_TELEPORT_POS = (6025, -1600)

START_X = 100
START_Y = 675

DIRECTION_KEYS = {
    "left": [pygame.K_LEFT, pygame.K_a],
    "right": [pygame.K_RIGHT, pygame.K_d],
}



current_state = MENU
current_slot = 0

save_manager = SaveManager(SAVE_FILE)
journalManager = JournalManager()
notificationManager = NotificationManager()
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

terminals = []
activeTerminal = None
warden = None
reading_chapter = None
ending_text = ""
ending_scroll = 0

flashTimer = 0
alarmOverlay = False

world_timer = 0.0
timer_active = False
saveNotificationTimer = 0.0

btn_start = Button("START", SCREEN_WIDTH // 2 - 100, 250, 200, 55, BLUE, LIGHT_BLUE, menu_font)
btn_quit = Button("QUIT", SCREEN_WIDTH // 2 - 100, 330, 200, 55, RED, LIGHT_RED, menu_font)

btn_back_menu = Button("BACK", SCREEN_WIDTH // 2 - 100, 500, 200, 55, GRAY, LIGHT_BLUE,menu_font)

btn_resume = Button("RESUME", SCREEN_WIDTH // 2 - 100, 220, 200, 55, GREEN, LIGHT_GREEN, menu_font)
btn_journal = Button("JOURNAL", SCREEN_WIDTH // 2 - 100, 290, 200, 55, PURPLE, LIGHT_PURPLE)
btn_main_menu = Button("MAIN MENU", SCREEN_WIDTH // 2 - 100, 360, 200, 55, RED, LIGHT_RED, menu_font)

respawnBtn = Button("RESPAWN", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 20, 200, 50, RED, LIGHT_RED, menu_font)
gameOverMenuBtn = Button("MAIN MENU", SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 80, 200, 55, GREEN, LIGHT_GREEN, menu_font)

btn_journal_back = Button("BACK", 30, 540, 120, 45, GRAY, LIGHT_BLUE, small_font)
btn_journal_prev = Button("<", 30, 100, 50, 40, DARK_GRAY, GRAY, small_font)
btn_journal_next = Button(">", 920, 100, 50, 40, DARK_GRAY, GRAY, small_font)

btn_take_place = Button("TAKE THE WARDEN'S PLACE", SCREEN_WIDTH // 2 - 200, 400, 400, 60, PURPLE, LIGHT_PURPLE)
btn_break_cycle = Button("BREAK THE CYCLE", SCREEN_WIDTH // 2 - 200, 480, 400, 60, RED, LIGHT_RED)

slot_buttons = []
reset_buttons = []
for i in range(3):
    y = 180 + i * 100
    slot_buttons.append(Button(f"SLOT {i+1}", SCREEN_WIDTH // 2 - 200, y, 250, 60, BLUE, LIGHT_BLUE, small_font))
    reset_buttons.append(Button("RESET", SCREEN_WIDTH // 2 + 70, y, 130, 60, RED, LIGHT_RED, small_font))




levelData = build_level(0)
rooms = levelData["rooms"]
platforms = levelData["platforms"]
terminals = levelData["terminals"]
enemies = levelData["enemies"]
doors = levelData["doors"]
loreKeys = levelData["loreKeys"]
checkPoints = levelData["checkPoints"]
warden = levelData["warden"]
currRoom = 0


player = Player(100, 675)

def draw_text(text, font, color, center):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    screen.blit(surf, rect)

def save_game():
    slot = save_manager.get_slot(current_slot)
    terminalsData = [t.saveDict() for t in terminals]
    enemiesData = [e.saveDict(checkPoints) for e in enemies]

    save_manager.write_slot(
        current_slot,
        slot.get("level", 1),
        player.rect.x,
        player.rect.y,
        terminalsData,
        enemiesData,
        timer = world_timer,
        room = currRoom
    )

    save_manager.get_slot(current_slot)["journal"] = journalManager.to_list()
    save_manager.save()

def resetPlayerPos(p):
    global currRoom
    p.rect.x = START_X
    p.rect.y = START_Y
    p.vel_x = 0
    p.vel_y = 0
    currRoom = 0
    camera.snapToRoom(rooms[currRoom])

def resetLevel():
    global player, levelData, rooms, platforms, terminals, enemies, currRoom, doors, loreKeys

    levelData = build_level(0)
    rooms = levelData["rooms"]
    platforms = levelData["platforms"]
    terminals = levelData["terminals"]
    enemies = levelData["enemies"]
    doors = levelData["doors"]
    loreKeys = levelData["loreKeys"]

    for key in loreKeys:
        if key.chapter_id in journalManager.unlocked:
            key.collected = True

    player = Player(START_X, START_Y)
    currRoom = 0
    camera.snapToRoom(rooms[currRoom])

def start_game(slot_index, restoreTimeAndJournal = True):
    global current_slot, player, levelData, rooms, platforms, currRoom, terminals, enemies, doors, loreKeys, checkPoints, world_timer, timer_active, warden
    current_slot = slot_index
    slot = save_manager.get_slot(slot_index)
    level = slot["level"]

    if restoreTimeAndJournal:
        journalManager.load_from_slot(slot.get("journal", []))
        world_timer = slot.get("timer", 0.0)
    timer_active = True

    levelData = build_level(level)
    rooms = levelData["rooms"]
    platforms = levelData["platforms"]
    terminals = levelData["terminals"]
    enemies = levelData["enemies"]
    doors = levelData["doors"]
    loreKeys = levelData["loreKeys"]
    checkPoints = levelData["checkPoints"]
    warden = levelData["warden"]

    if warden:
        warden.canSkip = slot.get("wardenIntroSeen", False)

    for key in loreKeys:
        if key.chapter_id in journalManager.unlocked:
            key.collected = True

    if slot["exists"] and "terminals" in slot:
        savedTerminals = slot["terminals"]
        for i, t in enumerate(terminals):
            if i <  len(savedTerminals):
                t.loadDict(savedTerminals[i])

    if slot["exists"] and "enemies" in slot:
            savedEnemies = slot["enemies"]
            for i, e in enumerate(enemies):
                if i <  len(savedEnemies):
                    e.loadDict(savedEnemies[i])

    for door in doors:
        door.syncToTerminalState()

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

def check_lore_keys():
    global reading_chapter, current_state
    for key in loreKeys:
        if not key.collected and player.rect.colliderect(key.rect):
            key.collected = True
            if journalManager.unlock(key.chapter_id):
                reading_chapter = key.chapter_id
                current_state = READING

def checkCheckpoints():
    global saveNotificationTimer
    for c in checkPoints:
        touching = player.rect.colliderect(c.rect)
        if touching and not c.playerEntry:
            save_game()
            saveNotificationTimer = 2.0
        c.playerEntry = touching

def finishWardenIntro():
    global current_state
    save_manager.markWardenIntroSeen(current_slot)
    if warden:
        warden.canSkip = True
    current_state = PLAYING

def apply_choice(choice):
    global ending_text, ending_scroll, current_state, timer_active
    timer_active = False
    if choice == "warden":
        ending_text = (
            "ENDING: THE NEW WARDEN\n\n"
            "You take the Warden's place. The screen fades to black. "
            "You hear Gerard's voice, now at peace: 'Thank you. Thank you for freeing me. "
            "And I am sorry for what you must become.'\n\n"
            "The cycle continues. A new Warden rises. A new Soul Forge will come. "
            "And the Outer Ones will keep watching. And the realm will keep living. "
            "And you will keep sacrificing. Forever. Because that is the price of "
            "prosperity for the many. You carve your own name into your own code. "
            "You are the 73rd Warden. There will be more."
        )
        save_manager.add_ending(current_slot, "new_warden")
    else:
        ending_text = (
            "ENDING: THE BROKEN CYCLE\n\n"
            "You refuse. Gerard nods slowly, tears in his eyes: "
            "'I understand. I would have chosen the same, once.'\n\n"
            "The screen begins to flicker. Platforms dissolve. Enemies fade. "
            "The world begins to unravel. Everyone you saved... everyone you loved... "
            "they are fading. But you are free. You are finally, truly free. "
            "And somewhere, in the Sea of Souls, a new dimension is being born. "
            "Perhaps it will be kinder. Perhaps it will not need a Warden. Perhaps."
        )
        save_manager.add_ending(current_slot, "broken_cycle")
    ending_scroll = 0
    current_state = ENDING

def draw_journal():
    screen.fill(DARK_PURPLE)
    draw_text("JOURNAL", title_font, WHITE, (SCREEN_WIDTH // 2, 40))
    draw_text("Soul Forge Archives", tiny_font, GRAY, (SCREEN_WIDTH // 2, 80))

    visible = journalManager.get_visible_chapters()

    if not visible:
        draw_text("No entries yet.", small_font, GRAY, (SCREEN_WIDTH // 2, 300))
        btn_journal_back.draw(screen)
        return

    if journalManager.current_page >= len(visible):
        journalManager.current_page = len(visible) - 1
    if journalManager.current_page < 0:
        journalManager.current_page = 0

    current_id = visible[journalManager.current_page]
    chapter = JOURNAL_CHAPTERS[current_id]

    draw_text(f"{journalManager.current_page + 1} / {len(visible)}", tiny_font, CYAN,
              (SCREEN_WIDTH // 2, 100))
    draw_text(chapter["title"], small_font, YELLOW, (SCREEN_WIDTH // 2, 120))

    lines = wrap_text(chapter["content"], tiny_font, 660)
    textBlockX = (SCREEN_WIDTH - 660) // 2
    y = 160 - journalManager.scroll_offset
    for line in lines:
        if 140 <= y <= SCREEN_HEIGHT - 80:
            surf = tiny_font.render(line, True, WHITE)
            lineRect = surf.get_rect(centerx=SCREEN_WIDTH // 2, y = y)
            screen.blit(surf, lineRect)
        y += 24

    max_scroll = max(0, len(lines) * 24 - (SCREEN_HEIGHT - 240))
    if journalManager.scroll_offset > max_scroll:
        journalManager.scroll_offset = max_scroll
    if journalManager.scroll_offset < 0:
        journalManager.scroll_offset = 0

    btn_journal_prev.draw(screen)
    btn_journal_next.draw(screen)
    btn_journal_back.draw(screen)

    if len(visible) > 1:
        hint = tiny_font.render("Use < > to switch entries. Scroll with arrow keys.", True, GRAY)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 30))

def draw_reading():
    screen.fill(DARK_PURPLE)
    chapter = JOURNAL_CHAPTERS[reading_chapter]
    draw_text(chapter["title"], menu_font, YELLOW, (SCREEN_WIDTH // 2, 80))
    lines = wrap_text(chapter["content"], small_font, 660)
    y = 160
    for line in lines:
        surf = small_font.render(line, True, WHITE)
        screen.blit(surf, (70, y))
        y += 28
    hint = tiny_font.render("CLICK or SPACE to close", True, GRAY)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40))

def draw_ending():
    screen.fill(BLACK)
    lines = ending_text.split("\n")
    y = 60 - ending_scroll
    for line in lines:
        if 20 <= y <= SCREEN_HEIGHT - 40:
            if line.startswith("ENDING:"):
                surf = menu_font.render(line, True, YELLOW)
            else:
                surf = tiny_font.render(line, True, WHITE)
            screen.blit(surf, (50, y))
        y += 30
    hint = tiny_font.render("UP/DOWN to scroll. ESC to return to menu.", True, GRAY)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 25))

def draw_warden_dialogue():
    # background: draw the room like normal, then dim it and show a dialogue box
    screen.fill((30, 30, 60))
    for p in platforms:
        screenRect = camera.apply(p)
        pygame.draw.rect(screen, GREEN, screenRect)
    if warden:
        warden.draw(screen, camera)
    player.draw(screen, camera)

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(140)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    if not warden:
        return

    boxRect = pygame.Rect(50, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 100, 150)
    pygame.draw.rect(screen, DARK_PURPLE, boxRect, border_radius=8)
    pygame.draw.rect(screen, LIGHT_PURPLE, boxRect, 3, border_radius=8)

    if 0 <= warden.dialogue_index < len(warden.dialogue_lines):
        line = warden.dialogue_lines[warden.dialogue_index]
        revealed = line[:int(warden.charsShown)]
        lines = wrap_text(revealed, small_font, boxRect.width - 40)
        y = boxRect.top + 20
        for l in lines:
            surf = small_font.render(l, True, WHITE)
            screen.blit(surf, (boxRect.left + 20, y))
            y += 28

    if warden.defeated:
        btn_take_place.draw(screen)
        btn_break_cycle.draw(screen)
    else:
        hint = tiny_font.render("SPACE / click to continue", True, GRAY)
        screen.blit(hint, (boxRect.centerx - hint.get_width() // 2, boxRect.bottom - 25))
        warden.drawSkipPrompt(screen)

def draw_warden_intro():
    screen.fill((30, 30, 60))
    for p in platforms:
        screenRect = camera.apply(p)
        pygame.draw.rect(screen, GREEN, screenRect)
    for door in doors:
        door.draw(screen, camera)
    if warden:
        warden.draw(screen, camera)
    player.draw(screen, camera)

    if wardenIntroStage == "fade_out":
        alpha = min(255, int(255 * (wardenIntroTimer / WARDEN_INTRO_FADE_TIME)))
    elif wardenIntroStage == "hold":
        alpha = 255
    elif wardenIntroStage == "fade_in":
        alpha = max(0, 255 - int(255 * (wardenIntroTimer / WARDEN_INTRO_FADE_TIME)))
    else:
        alpha = 0

    if alpha > 0:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

running = True
while running:
    dt = clock.tick(FPS) / 1000.0 #convert delta time to seconds

    if saveNotificationTimer > 0:
        saveNotificationTimer -= dt
        if saveNotificationTimer < 0:
            saveNotificationTimer = 0

    if current_state == WARDEN_DIALOGUE and warden and not warden.defeated:
        holdingY = pygame.key.get_pressed()[pygame.K_y]
        if warden.tickDialogue(dt) or warden.tickSkip(dt, holdingY):
            finishWardenIntro()

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
                elif current_state == JOURNAL:
                    current_state = PAUSED
                elif current_state == READING:
                    current_state = PLAYING
                elif current_state == ENDING:
                    current_state = MENU

            elif event.key == pygame.K_SPACE and current_state == READING:
                current_state = PLAYING

            elif event.key == pygame.K_e and current_state in (PLAYING, HACKING):
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

            if current_state == JOURNAL:
                if event.key == pygame.K_UP:
                    journalManager.scroll_offset -= 30
                elif event.key == pygame.K_DOWN:
                    journalManager.scroll_offset += 30
                elif event.key == pygame.K_LEFT:
                    journalManager.current_page -= 1
                    journalManager.scroll_offset = 0
                elif event.key == pygame.K_RIGHT:
                    journalManager.current_page += 1
                    journalManager.scroll_offset = 0

            if current_state == ENDING:
                if event.key == pygame.K_UP:
                    ending_scroll -= 40
                elif event.key == pygame.K_DOWN:
                    ending_scroll += 40
                if ending_scroll < 0:
                    ending_scroll = 0
            
            if current_state == WARDEN_DIALOGUE and warden and not warden.defeated:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    currLine = warden.dialogue_lines[warden.dialogue_index]
                    if warden.charsShown < len(currLine):
                        warden.charsShown = len(currLine)
                    elif warden.advanceDialogue():
                        finishWardenIntro()
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == READING:
                current_state = PLAYING
            elif current_state == WARDEN_DIALOGUE and warden and not warden.defeated:
                currLine = warden.dialogue_lines[warden.dialogue_index]
                if warden.charsShown < len(currLine):
                    warden.charsShown = len(currLine)
                elif warden.advanceDialogue():
                    finishWardenIntro()

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
            if btn_journal.is_clicked(event):
                current_state = JOURNAL
            if btn_main_menu.is_clicked(event):
                current_state = MENU
        elif current_state == JOURNAL:
            if btn_journal_back.is_clicked(event):
                current_state = PAUSED
            if btn_journal_prev.is_clicked(event):
                journalManager.current_page -= 1
                journalManager.scroll_offset = 0
            if btn_journal_next.is_clicked(event):
                journalManager.current_page += 1
                journalManager.scroll_offset = 0
        elif current_state == GAME_OVER:
            if respawnBtn.is_clicked(event):
                current_state = start_game(current_slot, restoreTimeAndJournal=False)
            if gameOverMenuBtn.is_clicked(event):
                current_state = MENU
        elif current_state == WARDEN_DIALOGUE and warden and warden.defeated:
            if btn_take_place.is_clicked(event):
                apply_choice("warden")
            elif btn_break_cycle.is_clicked(event):
                apply_choice("break")
        
    if current_state == PLAYING or current_state == HACKING or current_state == WARDEN_INTRO:
        for t in terminals:

            autoExit = t.updateTimer(1 / FPS, t.hasStarted)

            if autoExit and current_state == HACKING and activeTerminal == t:
                activeTerminal = None
                current_state = PLAYING

        for door in doors:
            door.update(dt=dt, isPause = (current_state == PAUSED) or camera.isTrans)

        for key in loreKeys:
            key.update()

        if timer_active and not camera.isTrans:
            world_timer += dt


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

                if warden:
                    warden.update(player, activePhysicsPlatforms, alarmActive = anyAlarm)

                    if warden.rect.colliderect(player.rect) and not warden.talking and not warden.defeated:
                        current_state = GAME_OVER

                    if currRoom in WARDEN_ARENA_ROOMS and warden:
                        hackedCount = sum(1 for t in terminals if t.room == "warden" and t.isHacked)
                        if hackedCount >= 8 and not warden.defeated:
                            warden.defeated = True
                            warden.talking = True
                            warden.dialogue_lines = [
                                "smth smth smth",
                                "Take their place and continue the cycle,",
                                "or break it and let the realm fade?",
                            ]
                            warden.dialogue_index = 0
                            current_state = WARDEN_DIALOGUE

            player.update(activePhysicsPlatforms, None, camera.isTrans, moveInput)

            check_lore_keys()
            checkCheckpoints()

            playerCenter = player.rect.center
            for i, room in enumerate(rooms):
                if i != currRoom and room.collidepoint(playerCenter):
                    currRoom = i
                    camera.targetRoom(rooms[currRoom])

                    if warden and currRoom in WARDEN_ARENA_ROOMS:
                        warden.relocateToRoom(rooms[currRoom])
                        if warden.talking and not warden.defeated:
                            current_state = WARDEN_INTRO
                            wardenIntroStage = "fade_out"
                            wardenIntroTimer = 0.0
                            wardenIntroDoor = doors[30]
                    break
    
            if player.rect.top > 5000: #change this later for whenever more rooms are added upwards
                resetPlayerPos(player)

        elif current_state == WARDEN_INTRO:
            wardenIntroTimer += dt
            if wardenIntroStage == "fade_out":
                if wardenIntroTimer >= WARDEN_INTRO_FADE_TIME:
                    player.rect.x, player.rect.y = WARDEN_INTRO_TELEPORT_POS
                    player.vel_x = 0
                    player.vel_y = 0

                    camera.snapToRoom(rooms[currRoom])

                    if wardenIntroDoor:
                        wardenIntroDoor.forceClose()

                    wardenIntroStage = "hold"
                    wardenIntroTimer = 0.0

            elif wardenIntroStage == "hold":
                if wardenIntroTimer >= WARDEN_INTRO_HOLD_TIME:
                    wardenIntroStage = "fade_in"
                    wardenIntroTimer = 0.0

            elif wardenIntroStage == "fade_in":
                if wardenIntroTimer >= WARDEN_INTRO_FADE_TIME:
                    wardenIntroStage = None
                    current_state = WARDEN_DIALOGUE

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
        btn_journal.update(mouse_pos)
        btn_main_menu.update(mouse_pos)
    elif current_state == JOURNAL:
        btn_journal_prev.update(mouse_pos)
        btn_journal_next.update(mouse_pos)
        btn_journal_back.update(mouse_pos)
    elif current_state == GAME_OVER:
        respawnBtn.update(mouse_pos)
        gameOverMenuBtn.update(mouse_pos)
    elif current_state == WARDEN_DIALOGUE and warden and warden.defeated:
        btn_take_place.update(mouse_pos)
        btn_break_cycle.update(mouse_pos)

    if current_state == MENU:
            screen.fill(BLACK)
            draw_text("SOUL FORGE", title_font, PURPLE, (SCREEN_WIDTH // 2, 130))
            draw_text("The 73rd cycle", tiny_font, GRAY, (SCREEN_WIDTH // 2, 185))
            btn_start.draw(screen)
            btn_quit.draw(screen)

    elif current_state == LEVEL_SELECT:
        screen.fill(BLACK)
        draw_text("SELECT SAVE SLOT", menu_font, WHITE, (SCREEN_WIDTH // 2, 100))
        for i in range(3):
            slot = save_manager.get_slot(i)
            slot_buttons[i].draw(screen)
            reset_buttons[i].draw(screen)

            journalCount = len(slot.get("journal", []))
            timer = slot.get("timer", 0.0)
            hasProgress = slot["exists"] or journalCount > 0 or timer > 0.0

            if hasProgress:
                timer = slot.get('timer', 0.0)
                mins = int(timer // 60)
                secs = int(timer % 60)
                milis = int((timer%1) *1000)
                journalCount = len(slot.get("journal", []))
                info = f"{mins:02d}:{secs:02d}.{milis:03d}             Room: {slot.get('room', 0)+1}             Logs: {journalCount}"
            else:
                info = "Empty"
            info_surf = small_font.render(info, True, YELLOW)
            screen.blit(info_surf, (SCREEN_WIDTH // 2 - 200, 180 + i * 100 + 65))
        btn_back_menu.draw(screen)

    elif current_state == JOURNAL:
        draw_journal()

    elif current_state == READING:
        draw_reading()

    elif current_state == ENDING:
        draw_ending()

    elif current_state == WARDEN_DIALOGUE:
        draw_warden_dialogue()

    elif current_state == WARDEN_INTRO:
        draw_warden_intro()

    elif current_state in (PLAYING, HACKING, PAUSED, GAME_OVER):
        screen.fill((30, 30, 60))

        # if currRoom == 18 and not camera.isTrans:
        #     roomText = small_font.render("WATCH OUT!", True, WHITE)
        #     worldRect = pygame.Rect(7450, -1250, roomText.get_width(), roomText.get_height())
        #     screenRect = camera.apply(worldRect)
        #     screen.blit(roomText, screenRect.topleft)

        if currRoom == 19 and not camera.isTrans:
            lines = [
                "Something is different..."
            ]
            startX, startY = 6500, -1375
            lineSpacing = 30

            for i, line in enumerate(lines):
                lineSurf = small_font.render(line, True, WHITE)
                worldRect = lineSurf.get_rect(center=(startX, startY + i * lineSpacing))
                screenRect = camera.apply(worldRect)
                screen.blit(lineSurf, screenRect)

        for door in doors:
            door.draw(screen, camera)

        for p in platforms:
            screenRect = camera.apply(p)
            pygame.draw.rect(screen, GREEN, screenRect)
            #pygame.draw.rect(screen, WHITE, screenRect, 2)

        for t in terminals:
            t.draw(screen, camera)

        for key in loreKeys:
            key.draw(screen, camera)

        for c in checkPoints:
            screenRect = camera.apply(c.rect)
            cSurf = pygame.Surface((screenRect.width, screenRect.height), pygame.SRCALPHA)
            cSurf.fill((255, 255, 0, 90))
            screen.blit(cSurf, screenRect.topleft)
            pygame.draw.rect(screen, YELLOW, screenRect, 2)
        
        if not camera.isTrans:

            for enemy in enemies:
                enemy.draw(screen, camera)
                enemy.draw_waypoints(screen, camera)

            if warden:
                warden.draw(screen, camera)

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

        if current_state == PLAYING:
            mins = int(world_timer // 60)
            secs = int(world_timer % 60)
            milis = int((world_timer%1) * 1000)
            timerText = f"{mins:02d}:{secs:02d}.{milis:03d}"
            timerSurf = small_font.render(timerText, True, WHITE)
            screen.blit(timerSurf, (SCREEN_WIDTH - timerSurf.get_width() - 50, 25))

            if saveNotificationTimer > 0:
                alpha = min(255, int(255 * (saveNotificationTimer / 2.0) * 3)) #added fade transition for teh saved message for hceckpoints
                saveSurf = small_font.render("SAVED", True, WHITE)
                saveSurf.set_alpha(alpha)
                saveRect = saveSurf.get_rect(center = (SCREEN_WIDTH // 2, 50))
                screen.blit(saveSurf, saveRect)

            if terminals[20].isHacked:
                trollText = small_font.render("WATCH OUT!", True, WHITE)
                worldRect = pygame.Rect(7450, -1250, trollText.get_width(), trollText.get_height())
                screenRect = camera.apply(worldRect)
                screen.blit(trollText, screenRect.topleft)
        

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
            btn_journal.draw(screen)
            btn_main_menu.draw(screen)

        elif current_state == GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
            draw_text("You have been reset by the Warden's design.", menu_font, RED, (SCREEN_WIDTH // 2, 220))
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

save_manager.save()
pygame.quit()
sys.exit()