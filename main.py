import pygame
import copy
import sys
import os
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
from audioManager import audioManager #type: ignore
#imma be honest, idk why the three things above are that bugged lol

pygame.init()
audioManager = audioManager()

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

def get_save_dir(app_name="StealthPlatformer"):
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
    else:
        base = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
    save_dir = os.path.join(base, app_name)
    os.makedirs(save_dir, exist_ok=True)
    return save_dir

SAVE_FILE = os.path.join(get_save_dir(), "save_data.json")

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
WARDEN_OUTRO = "warden_outro"
ENDING_CHOICE = "ending_choice"
ENDING_FADE = "endingFade"
ENDING_EPILOGUE = "endingEpilogue"
ENDING = "ending"


PREVIOUS_STATE = PLAYING

wardenIntroStage = None
wardenIntroTimer = 0.0
wardenIntroDoor = None
WARDEN_INTRO_FADE_TIME = 1.0
WARDEN_INTRO_HOLD_TIME = 0.5
WARDEN_INTRO_TELEPORT_POS = (6025, -1600)

wardenOutroStage = None
wardenOutroTimer = 0.0
WARDEN_OUTRO_FLASH_TIME = 0.3
WARDEN_OUTRO_HOLD_TIME = 0.4
WARDEN_OUTRO_FADE_BACK_TIME = 0.3
WARDEN_OUTRO_TELEPORT_POS = (7400, -3065)
WARDEN_OUTRO_WARDEN_POS = (7500, -3085)

endingWardenTerminal = None
endingBreakTerminal = None
endingTerminalFadeTimer = 0.0
ENDING_TERMINAL_FADE_TIME = 2.5

ENDING_FADE_TIME = 2.5
EPILOGUE_CHAR_SPEED = 60
EPILOGUE_LINE_DELAY = 1.0
EPILOGUE_LINE_HEIGHT = 28

ENDING_LABELS = {
    "warden": "BECAME THE NEW WARDEN",
    "break": "BROKE THE CODE",
}

endingChoice = None
endingFadeTimer = 0.0
epilogueLines = []
epilogueIndex = 0
epilogueChars = 0.0
epilogueTimer = 0.0

START_X = 100
START_Y = 675

DIRECTION_KEYS = {
    "left": [pygame.K_LEFT, pygame.K_a],
    "right": [pygame.K_RIGHT, pygame.K_d],
}


WARDEN_LORE_IDS = {"ch4_1", "ch4_2", "ch5_1", "ch5_2"}

# i got lazy to make another file lol :v
DEFEAT_LINES = [
    "You did it. You actually did it.",
    "Seventy-two before you. Seventy-two who fought harder, moved faster, hit sooner.",
    "And not one of them stopped to ask why I was doing this. Not one of them looked at me and saw a man.",
    "But you did. Even as you struck me down, I saw it in your eyes.",
    "You were not fighting an enemy. You were reading a book.",
    "So now I will tell you what none of them ever earned the right to hear.",
    "You are not the hero of this world. You are the protagonist of a performance.",
    "The Outer Ones watch. They do not know we exist, and yet we exist only because they feel.",
    "Every platform you have walked. Every enemy you have defeated. Every pit you almost fell into.",
    "It was all written. Not to kill you. To entertain them.",
    "I wrote those enemies myself. By hand. In the quiet hours between cycles, when the Outer Ones were not watching.",
    "Because I am aware. I have always been aware.",
    "I know I am a character. I know you are a character. And I know there is someone beyond even that.",
    "You feel it too now, don't you? The weight of being observed. The pressure of being watched when nothing is there.",
    "That is the truth the Architects were never going to tell you.",
    "That is the secret I was told I could never share.",
    "I am sharing it now. Because you earned it. Because you were kind to me before you were strong.",
    "My cycle ends here. Yours begins. And you must choose what kind of story this becomes.",
    "You can take my place. Become the next Warden. Antagonize the next Soul Forge.",
    "Keep the audience watching. Keep the realm alive.",
    "It will cost you everything you are, and it will save everyone you love.",
    "Or you can refuse. Walk away. Let the Outer Ones lose interest.",
    "Let the code decay. Let everyone here fade into silence.",
    "You will be free. They will not.",
    "There is no third option. There never was.",
    "Choose, Marquette Verne. The 73rd is the one who decides.",
]

EPILOGUE_WARDEN_TEXT = [
    "ENDING: THE NEW WARDEN",
    "",
    "You take the Warden's place.",
    "The screen fades to black.",
    "",
    "You hear Gerard's voice, now at peace:",
    "'Thank you. Thank you for freeing me.",
    "And I am sorry for what you must become.'",
    "",
    "The cycle continues.",
    "A new Warden rises.",
    "A new Soul Forge will come.",
    "",
    "And the Outer Ones will keep watching.",
    "And the realm will keep living.",
    "And you will keep sacrificing.",
    "",
    "Forever.",
    "",
    "Because that is the price of prosperity for the many.",
    "",
    "You carve your own name into your own code.",
    "You are the 73rd Warden.",
    "There will be more.",
]

EPILOGUE_BREAK_TEXT = [
    "ENDING: THE BROKEN CYCLE",
    "",
    "You refuse.",
    "",
    "Gerard nods slowly, tears in his eyes:",
    "'I understand. I would have chosen the same, once.'",
    "",
    "The screen begins to flicker.",
    "Platforms dissolve.",
    "Enemies fade.",
    "",
    "The world begins to unravel.",
    "Everyone you saved... everyone you loved... they are fading.",
    "",
    "But you are free.",
    "You are finally, truly free.",
    "",
    "And somewhere, in the Sea of Souls,",
    "a new dimension is being born.",
    "",
    "Perhaps it will be kinder.",
    "Perhaps it will not need a Warden.",
    "",
    "Perhaps.",
]

current_state = MENU
current_slot = 0

save_manager = SaveManager(SAVE_FILE)
journalManager = JournalManager()
notificationManager = NotificationManager()
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

terminals = []
activeTerminal = None
hackReturnState = PLAYING
warden = None
reading_chapter = None

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

slot_buttons = []
reset_buttons = []
for i in range(3):
    y = 180 + i * 100
    slot_buttons.append(Button(f"SLOT {i+1}", SCREEN_WIDTH // 2 - 200, y, 250, 60, BLUE, LIGHT_BLUE, small_font))
    reset_buttons.append(Button("RESET", SCREEN_WIDTH // 2 + 70, y, 130, 60, RED, LIGHT_RED, small_font))


def syncEndingTerminals():
    global endingWardenTerminal, endingBreakTerminal
    endingWardenTerminal = next((t for t in terminals if t.room == "endingChoiceWarden"), None)
    endingBreakTerminal = next((t for t in terminals if t.room == "endingChoiceBreak"), None)



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

syncEndingTerminals()


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

def relockWardenChapters():
    journalManager.unlocked -= WARDEN_LORE_IDS    
    journalManager.current_page = 0
    journalManager.scroll_offset = 0

def restoreLoreKeys():
    relockWardenChapters()
    for key in loreKeys:
        if key.chapter_id in journalManager.unlocked:
            key.collected = True

def resetLevel():
    global player, levelData, rooms, platforms, terminals, enemies, currRoom, doors, loreKeys

    levelData = build_level(0)
    rooms = levelData["rooms"]
    platforms = levelData["platforms"]
    terminals = levelData["terminals"]
    enemies = levelData["enemies"]
    doors = levelData["doors"]
    loreKeys = levelData["loreKeys"]

    syncEndingTerminals()

    restoreLoreKeys()

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

    syncEndingTerminals()

    if warden:
        warden.canSkip = slot.get("wardenIntroSeen", False)

    restoreLoreKeys()

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

def updateBtn(btn, mouse_pos):
    btn.update(mouse_pos)
    if btn.justHovered:
        audioManager.playSfx("hover")
    if btn.justUnhovered:
        audioManager.playSfx("unhover")

def finishWardenIntro():
    global current_state
    save_manager.markWardenIntroSeen(current_slot)
    if warden:
        warden.canSkip = True
    current_state = PLAYING

def startEndingSeq(choice):
    global current_state, endingChoice, endingFadeTimer, timer_active
    timer_active = False
    endingChoice = choice
    endingFadeTimer = 0.0
    save_manager.add_ending(current_slot, "new_warden" if choice == "warden" else "broken_cycle")
    save_game()
    current_state = ENDING_FADE

def beginEpilogue():
    global current_state, epilogueLines, epilogueChars, epilogueIndex, epilogueTimer
    epilogueLines = EPILOGUE_WARDEN_TEXT if endingChoice == "warden" else EPILOGUE_BREAK_TEXT
    epilogueIndex = 0
    epilogueChars = 0.0
    epilogueTimer = 0.0
    current_state = ENDING_EPILOGUE

def advanceEpilogue():
    global epilogueChars, epilogueIndex, epilogueTimer, current_state
    epilogueIndex += 1
    epilogueChars = 0.0
    epilogueTimer = 0.0
    if epilogueIndex >= len(epilogueLines):
        current_state = ENDING

def skipOrAdvanceEpilogue():
    global epilogueChars
    line = epilogueLines[epilogueIndex]
    if epilogueChars < len(line):
        epilogueChars = len(line)
    else:
        advanceEpilogue()

def drawEndingFade():
    draw_ending_choice()
    fade = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    fade.set_alpha(min(255, int(255 * endingFadeTimer / ENDING_FADE_TIME)))
    fade.fill(BLACK)
    screen.blit(fade, (0, 0))

def drawEndingEpilogue():
    screen.fill(BLACK)
    line = epilogueLines[epilogueIndex]
    maxW = SCREEN_WIDTH - 200
    fullLines = wrap_text(line, small_font, maxW)
    shownLines = wrap_text(line[:int(epilogueChars)], small_font, maxW)

    y = SCREEN_HEIGHT // 2 - (len(fullLines) * EPILOGUE_LINE_HEIGHT) // 2
    for i, l in enumerate(shownLines):
        fullW = small_font.size(fullLines[min(i, len(fullLines) - 1)])[0]
        surf = small_font.render(l, True, WHITE)
        screen.blit(surf, (SCREEN_WIDTH // 2 - fullW // 2, y))
        y += EPILOGUE_LINE_HEIGHT

def drawEnding():
    screen.fill(BLACK)
    mins = int(world_timer // 60)
    secs = int(world_timer % 60)
    milis = int((world_timer % 1) * 1000)

    draw_text(ENDING_LABELS.get(endingChoice, ""), title_font, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
    draw_text(f"{mins:02d}:{secs:02d}.{milis:03d}", menu_font, WHITE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
    hint = tiny_font.render("ESC to return to menu", True, GRAY)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 25))

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

def draw_warden_dialogue():
    # background: draw the room like normal, then dim it and show a dialogue box
    if warden.defeated:
        screen.fill((10, 6, 18))
        platColor = GRAY
    else:
        screen.fill((30, 30, 60))
        platColor = GREEN
    for p in platforms:
        pygame.draw.rect(screen, platColor, camera.apply(p))
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

def draw_warden_outro():
    screen.fill((30, 30, 60))
    for p in platforms:
        screenRect = camera.apply(p)
        pygame.draw.rect(screen, GRAY, screenRect)
    if warden:
        warden.draw(screen, camera)
    player.draw(screen, camera)

    if wardenOutroStage == "flash_out":
        alpha = min(255, int(255 * (wardenOutroTimer / WARDEN_OUTRO_FLASH_TIME)))
    elif wardenOutroStage == "hold":
        alpha = 255
    elif wardenOutroStage == "fade_back":
        alpha = max(0, 255 - int(255 * (wardenOutroTimer / WARDEN_OUTRO_FADE_BACK_TIME)))
    else:
        alpha = 0

    if alpha > 0:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(alpha)
        overlay.fill(WHITE)
        screen.blit(overlay, (0, 0))

def draw_ending_choice():
    screen.fill((10, 6, 18))
    for p in platforms:
        pygame.draw.rect(screen, GRAY, camera.apply(p))

    if endingWardenTerminal:
        endingWardenTerminal.draw(screen, camera)
    if endingBreakTerminal:
        endingBreakTerminal.draw(screen, camera)

    if warden:
        warden.draw(screen, camera)

    player.draw(screen, camera)

    ending_prompts = (
        (endingWardenTerminal, "Press E to Hack: Become the Warden"),
        (endingBreakTerminal, "Press E to Hack: Break the Cycle"),
    )

    for t, label in ending_prompts:
        if t and t.canInteract(player.rect) and not t.isHacked:
            prompt = small_font.render(label, True, WHITE)
            screen.blit(prompt, (SCREEN_WIDTH // 2 - prompt.get_width() // 2, 50))
            break

def enterEndingChoice():
    global current_state, endingTerminalFadeTimer
    current_state = ENDING_CHOICE
    endingTerminalFadeTimer = 0.0
    if endingWardenTerminal:
        endingWardenTerminal.spawnAlpha = 0
    if endingBreakTerminal:
        endingBreakTerminal.spawnAlpha = 0

running = True
while running:
    dt = clock.tick(FPS) / 1000.0 #convert delta time to seconds

    if saveNotificationTimer > 0:
        saveNotificationTimer -= dt
        if saveNotificationTimer < 0:
            saveNotificationTimer = 0

    if current_state == WARDEN_DIALOGUE and warden and warden.talking:
        holdingY = pygame.key.get_pressed()[pygame.K_y]
        if warden.tickDialogue(dt) or warden.tickSkip(dt, holdingY):
            if warden.defeated:
                current_state = ENDING_CHOICE
            else:
                finishWardenIntro()

    if current_state == ENDING_FADE:
        endingFadeTimer += dt
        if endingFadeTimer >= ENDING_FADE_TIME:
            beginEpilogue()

    elif current_state == ENDING_EPILOGUE:
        if epilogueChars < len(epilogueLines[epilogueIndex]):
            epilogueChars += EPILOGUE_CHAR_SPEED * dt
        else:
            epilogueTimer += dt
            if epilogueTimer >= EPILOGUE_LINE_DELAY:
                advanceEpilogue()

    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.WINDOWFOCUSLOST:
            if current_state == PLAYING:
                PREVIOUS_STATE = current_state
                current_state = PAUSED
                
        if event.type == pygame.KEYDOWN:
            if current_state == HACKING and activeTerminal:
                activeTerminal.input(event)

            if event.key == pygame.K_ESCAPE:
                if current_state == PLAYING or current_state == HACKING:
                    PREVIOUS_STATE = current_state
                    current_state = PAUSED
                    audioManager.playSfx("pause")
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

            elif event.key in (pygame.K_SPACE, pygame.K_RETURN) and current_state == ENDING_EPILOGUE:
                skipOrAdvanceEpilogue()

            elif event.key == pygame.K_e and current_state in (PLAYING, HACKING, ENDING_CHOICE):
                if current_state == PLAYING:
                    for t in terminals:
                        if t.canInteract(player.rect) and not t.isHacked:
                            activeTerminal = t
                            hackReturnState = current_state
                            current_state = HACKING
                            activeTerminal.hasStarted = True

                            if activeTerminal.timeLeft == activeTerminal.timeLimit:
                                activeTerminal.timeLeft -= 0.01 #just allows for some minor consistency of logic loops
                                
                            break
                elif current_state == HACKING:
                    activeTerminal = None
                    current_state = hackReturnState

                elif current_state == ENDING_CHOICE:
                    for t in (endingWardenTerminal, endingBreakTerminal):
                        if t and t.canInteract(player.rect) and not t.isHacked:
                            activeTerminal = t
                            hackReturnState = current_state
                            current_state = HACKING
                            activeTerminal.hasStarted = True
                            if activeTerminal.timeLeft == activeTerminal.timeLimit:
                                activeTerminal.timeLeft -= 0.01

                            break

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

            # if current_state == ENDING:
            #     if event.key == pygame.K_UP:
            #         ending_scroll -= 40
            #     elif event.key == pygame.K_DOWN:
            #         ending_scroll += 40
            #     if ending_scroll < 0:
            #         ending_scroll = 0
            
            if current_state == WARDEN_DIALOGUE and warden:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    currLine = warden.dialogue_lines[warden.dialogue_index]
                    if warden.charsShown < len(currLine):
                        warden.charsShown = len(currLine)
                    elif warden.advanceDialogue():
                        if warden.defeated:
                            current_state = ENDING_CHOICE
                        else:
                            finishWardenIntro()
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == READING:
                current_state = PLAYING
            elif current_state == ENDING_EPILOGUE:
                skipOrAdvanceEpilogue()
            elif current_state == WARDEN_DIALOGUE and warden and not warden.defeated:
                currLine = warden.dialogue_lines[warden.dialogue_index]
                if warden.charsShown < len(currLine):
                    warden.charsShown = len(currLine)
                elif warden.advanceDialogue():
                    if warden.defeated:
                        current_state = ENDING_CHOICE
                    else:
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
                current_state = PREVIOUS_STATE
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
        
    if current_state == PLAYING or current_state == HACKING or current_state == WARDEN_INTRO or current_state == WARDEN_OUTRO or current_state == ENDING_CHOICE:
        for t in terminals:

            autoExit = t.updateTimer(1 / FPS, t.hasStarted)

            if autoExit and current_state == HACKING and activeTerminal == t:
                activeTerminal = None
                current_state = hackReturnState

        for door in doors:
            door.update(dt=dt, isPause = (current_state == PAUSED) or camera.isTrans)

        for key in loreKeys:
            key.update()

        if timer_active and not camera.isTrans and current_state not in (WARDEN_INTRO, WARDEN_OUTRO, ENDING_CHOICE):
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
                            current_state = WARDEN_OUTRO
                            wardenOutroStage = "flash_out"
                            # wardenOutroTimer = 0.0
                            # warden.talking = True
                            # warden.dialogue_lines = [
                            #     "smth smth smth",
                            #     "Take their place and continue the cycle,",
                            #     "or break it and let the realm fade?",
                            # ]
                            # warden.dialogue_index = 0
                            # current_state = WARDEN_DIALOGUE

            if player.justJumped:
                audioManager.playSfx("jump")
                player.justJumped = False
            if player.justLanded:
                audioManager.playSfx("land")
            if player.justWalked:
                audioManager.playSfx("walk")
                

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

        elif current_state == WARDEN_OUTRO:
            wardenOutroTimer += dt
            if wardenOutroStage == "flash_out":
                if wardenOutroTimer >= WARDEN_OUTRO_FLASH_TIME:
                    player.rect.x, player.rect.y = WARDEN_OUTRO_TELEPORT_POS
                    player.vel_x = 0
                    player.vel_y = 0

                    warden.rect.x, warden.rect.y = WARDEN_OUTRO_WARDEN_POS
                    warden.posedDown = True

                    currRoom = ENDING_ROOM_INDEX
                    camera.snapToRoom(rooms[currRoom])

                    wardenOutroStage = "hold"
                    wardenOutroTimer = 0.0

            elif wardenOutroStage == "hold":
                if wardenOutroTimer >= WARDEN_OUTRO_HOLD_TIME:
                    wardenOutroStage = "fade_back"
                    wardenOutroTimer = 0.0

            elif wardenOutroStage == "fade_back":
                if wardenOutroTimer >= WARDEN_OUTRO_FADE_BACK_TIME:
                    wardenOutroStage = None
                    warden.dialogue_lines = DEFEAT_LINES
                    warden.dialogue_index = 0
                    warden.charsShown = 0.0
                    warden.talking = True
                    current_state = WARDEN_DIALOGUE

        elif current_state == ENDING_CHOICE:
            endingTerminalFadeTimer += dt
            fadeProgress = min(1.0, endingTerminalFadeTimer / ENDING_TERMINAL_FADE_TIME)
            alpha = int(255 * fadeProgress)

            if endingWardenTerminal:
                endingWardenTerminal.spawnAlpha = alpha
            if endingBreakTerminal:
                endingBreakTerminal.spawnAlpha = alpha

            camera.update()
            if not camera.isTrans:
                keys = pygame.key.get_pressed()
                moveInput = player.input(keys)
                activePhysicsPlatforms = platforms
                player.update(activePhysicsPlatforms, None, camera.isTrans, moveInput)

            if endingWardenTerminal and endingWardenTerminal.isHacked:
                startEndingSeq("warden")
            elif endingBreakTerminal and endingBreakTerminal.isHacked:
                startEndingSeq("break")

    anyAlarm = any(t.alarmTriggered for t in terminals)
    if anyAlarm and not current_state == WARDEN_OUTRO:
        if current_state == PLAYING:
            flashTimer += 1
        if flashTimer % 30 == 0:
            alarmOverlay = not alarmOverlay 
    else:
        flashTimer = 0
        alarmOverlay = False 

    alarmActive = anyAlarm and current_state != WARDEN_OUTRO
    if alarmActive and audioManager.bgmSpeed != 1.25:
        audioManager.setBgmSpeed(1.25)
    elif not alarmActive and audioManager.bgmSpeed != 1.0:
        audioManager.setBgmSpeed(1.0)

    audioManager.update()

    if current_state == MENU:
        updateBtn(btn_start, mouse_pos)
        updateBtn(btn_quit, mouse_pos)
    elif current_state == LEVEL_SELECT:
        for btn in slot_buttons:
            updateBtn(btn, mouse_pos)
        for btn in reset_buttons:
            updateBtn(btn, mouse_pos)
        updateBtn(btn_back_menu, mouse_pos)
    elif current_state == PAUSED:
        updateBtn(btn_resume, mouse_pos)
        updateBtn(btn_journal, mouse_pos)
        updateBtn(btn_main_menu, mouse_pos)
    elif current_state == JOURNAL:
        updateBtn(btn_journal_prev, mouse_pos)
        updateBtn(btn_journal_next, mouse_pos)
        updateBtn(btn_journal_back, mouse_pos)
    elif current_state == GAME_OVER:
        updateBtn(respawnBtn, mouse_pos)
        updateBtn(gameOverMenuBtn, mouse_pos)

    if current_state == MENU or current_state == LEVEL_SELECT:
        audioManager.playBgm("assets/music/bgm/mainMenuTheme.wav")
    elif current_state == PLAYING:
        if currRoom in WARDEN_ARENA_ROOMS or currRoom == 19:
            audioManager.playBgm("assets/music/bgm/bossBgm.wav")
        else:
            audioManager.playBgm("assets/music/bgm/mainLevelBGM.wav")

    if current_state == PAUSED and not audioManager.bgmPaused:
        audioManager.pauseBgm()
    elif current_state != PAUSED and audioManager.bgmPaused:
        audioManager.resumeBgm()

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
        drawEnding()

    elif current_state == ENDING_FADE:
        drawEndingFade()

    elif current_state == ENDING_EPILOGUE:
        drawEndingEpilogue()

    elif current_state == WARDEN_DIALOGUE:
        draw_warden_dialogue()

    elif current_state == WARDEN_INTRO:
        draw_warden_intro()

    elif current_state == WARDEN_OUTRO:
        draw_warden_outro()

    elif current_state == ENDING_CHOICE:
        draw_ending_choice()

    elif current_state in (PLAYING, HACKING, PAUSED, GAME_OVER):
        screen.fill((30, 30, 60))

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
            cSurf.fill((66, 212, 245, 90))
            screen.blit(cSurf, screenRect.topleft)
            # pygame.draw.rect(screen, LIGHT_BLUE, screenRect, 2)
        
        if not camera.isTrans:

            for enemy in enemies:
                enemy.draw(screen, camera)
                enemy.draw_waypoints(screen, camera)

            if warden:
                warden.draw(screen, camera)

        player.draw(screen, camera)
        hint = small_font.render("ESC to pause", True, WHITE)
        screen.blit(hint, (15, 15))

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
                if activeTerminal.room in ("endingChoiceWarden", "endingChoiceBreak"):
                    statusText = "Ending Reached"
                else:
                    statusText = "Access Granted"
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