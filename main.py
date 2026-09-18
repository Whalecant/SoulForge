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
ENDING = "ending"

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
    },
    {
        "walls": [[2, 1], [2, 2], [0, 2], [2, 4], [5, 4], [1, 5], [4, 5], [1, 7]],
        "dummyCount": 4
    },
    {
        "walls": [[1, 2], [0, 2], [0, 2], [2, 3], [4, 4], [2, 5], [2, 6] , [2, 7], [3, 7]],
        "dummyCount": 4
    },
    {
        "walls": [[2, 1], [3, 1], [3, 2], [3, 2], [1, 5], [3, 6], [1, 7] , [4, 7]],
        "dummyCount": 5
    },
    {
        "keyPos": [5, 4],
        "exitPos": [5, 6],
        "walls": [[3,2], [2, 3], [4, 4], [1, 5], [2, 5], [4, 5], [5, 5], [4, 6], [2, 7]],
        "dummies": [[3, 3], [1, 4], [0, 5], [3, 5]],
    },
    {
        "keyPos": [5, 4],
        "exitPos": [5, 6],
        "walls": [[3,0], [0, 2], [1, 2], [2, 2], [2, 3], [4, 4], [5, 5], [3, 6], [1, 7]],
        "dummies": [[1, 0], [4, 2], [5, 2], [2, 5], [4, 6]],
    },
    {
        "walls": [[1, 0], [3, 0], [1, 2], [3, 2], [0, 3], [5, 3], [0, 5], [2, 6], [1, 7], [2, 7]],
        "dummyCount": 5,
    },
    {
        "walls": [[1, 0], [5, 0], [1, 1], [4, 1], [4, 4], [0, 5], [2, 5], [1, 7], [3, 7], [4, 7]],
        "dummyCount": 5,
    },


]

# for the enemy AI (this will be hell :DDDD) - it was in fact... hell...
WAYPOINTS = {
    # room 0 (x: 0 - 1000, y: 0 - 750)
    "r0_floor_left": (175, 685, ["r0_floor_right", "r0_plat_1"]),
    "r0_floor_right": (650, 685, ["r0_floor_left", "r0_plat_2"]),
    "r0_floor_right_backup": (725, 685, ["r0_floor_right"]),
    "r0_floor_left_backup": (400, 500, ["r0_floor_left", "r0_plat_1", "r0_floor_right"]),
    "r0_plat_1": (275, 510, ["r0_floor_left", "r0_floor_left_backup",  "r0_plat_3"]),
    "r0_plat_2": (830, 590, ["r0_floor_right", "r0_plat_1", "r2_plat_1"]),
    "r0_trans": (475, 685, ["r0_floor_left", "r0_floor_right", "r1_plat_4"]),
    "r0_plat_3": (450, 350, ["r0_plat_1"]),

    
    # room 1 (x: 0 - 1000, y: 750 - 1500)
    "r1_floor": (400, 1435, ["r1_floor_right", "r1_floor_left_air", "r1_floor_above"]),
    "r1_floor_above": (450, 1375, ["r1_floor", "r1_plat_2"]),
    "r1_plat_2": (650, 1310, ["r1_floor_above", "r1_plat_1", "r1_floor_right", "r1_plat_5"]),
    "r1_connector_1": (600, 850, ["r1_plat_4", "r1_plat_3"]),
    "r1_connector_2": (325, 875, ["r1_plat_4", "r1_plat_1"]),
    "r1_plat_1": (300, 1185, ["r1_connector_2", "r1_plat_3", "r1_floor_left_air", "r1_plat_2"]),
    "r1_plat_3": (650, 1010, ["r1_plat_1", "r1_connector_1", "r1_plat_5"]),
    "r1_plat_4": (475, 835, ["r0_trans", "r1_connector_1", "r1_connector_2"]),
    "r1_plat_5": (770, 1110, ["r1_plat_3", "r1_plat_2"]),
    "r1_floor_right": (900, 1400, ["r1_floor", "r1_plat_2"]),
    "r1_floor_left_air": (125, 1300, ["r1_floor", "r1_plat_1"]),

    # room 2 (x: 1000 - 2000, y: 0 - 750)
    "r2_plat_1": (1125, 510, ["r0_plat_2", "r2_floor", "r2_plat_2"]),
    "r2_floor": (1500, 685, ["r2_plat_1"]),
    "r2_plat_2": (1325, 410, ["r2_plat_1", "r2_plat_3"]),
    "r2_plat_3": (1500, 210, ["r2_plat_2"]),

    # room 3 (x: 2000 - 3000 y: 0 - 750)
    "r3_floor_right": (2750, 675, ["r3_floor_left", "r3_floor_mid_1", "r3_floor_mid_2"]),
    "r3_floor_left": (2250, 675, ["r3_floor_right", "r3_floor_mid_1", "r3_floor_mid_2"]),
    "r3_floor_mid_1": (2350, 650, ["r3_floor_right", "r3_floor_left", "r3_floor_mid_2", "r3_plat_1", "r3_wall_1", "r3_wall_2"]),
    "r3_floor_mid_2": (2650, 650, ["r3_floor_left", "r3_floor_right", "r3_floor_mid_1", "r3_plat_1", "r3_wall_1", "r3_wall_2"]),
    "r3_plat_1": (2750, 550, ["r3_floor_right", "r3_floor_mid_1", "r3_floor_mid_2"]),
    "r3_wall_1": (2440, 350, ["r3_floor_mid_1", "r3_wall_2", "r3_floor_mid_2"]),
    "r3_wall_2": (2570, 350, ["r3_floor_mid_1", "r3_wall_1", "r3_plat_1", "r3_floor_mid_2"]),

    # room 4(x: 2000 - 3000, y: -750  - 0)
    "r4_floor_right": (2700, -75, ["r4_floor_left"]),
    "r4_floor_left": (2420, -75, ["r4_floor_right", "r4_floor_2", "r4_plat_left_2_2"]),
    "r4_floor_left_2": (2185, -75, ["r4_floor_left", "r4_plat_left_1"]),
    "r4_plat_left_1": (2150, -200, ["r4_floor_left_2", "r4_plat_left_2"]),
    "r4_plat_left_2": (2250, -200, ["r4_plat_left_2", "r4_floor_left_2", "r4_floor_left_2_2"]),
    "r4_plat_left_2_2": (2400, -200, ["r4_floor_left", "r4_plat_left_2", "r4_plat_left_mid"]),
    "r4_plat_left_mid": (2200, -375, ["r4_plat_left_1", "r4_plat_left_mid_2"]),
    "r4_plat_left_mid_2": (2350, -375, ["r4_plat_left_mid", "r4_plat_left_2_2", "r4_plat_left_right", "r4_plat_left_hight"]),
    "r4_plat_left_right": (2450, -490, ["r4_plat_left_mid_2", "r4_plat_left_high"]),
    "r4_plat_left_high": (2295, -540, ["r4_plat_left_right", "r4_plat_left_mid_2"]),

    #room 5(x: 2000 - 3000, y: -1500 - -750)
    "r5_floor_left": (2275, -825, ["r5_floor_right", "r5_plat_left_1"]),
    "r5_floor_right": (2725, -825, ["r5_floor_left", "r5_plat_right_1"]),
    "r5_plat_left_1": (2200, -925, ["r5_floor_left", "r5_plat_mid_1", "r5_plat_left_2"]),
    "r5_plat_right_1": (2800, -925, ["r5_floor_right", "r5_plat_mid_2", "r5_plat_right_2"]),
    "r5_plat_mid_1": (2375, -990, ["r5_plat_left_1", "r5_plat_mid_2", "r5_plat_mid_mid"]),
    "r5_plat_mid_2": (2625, -990, ["r5_plat_right_1", "r5_plat_mid_1", "r5_plat_mid_mid"]),
    "r5_plat_mid_mid": (2500, -1050, ["r5_plat_mid_1", "r5_plat_mid_2", "r5_plat_left_2", "r5_plat_right_2"]),
    "r5_plat_left_2": (2225, -1100, ["r5_plat_mid_mid", "r5_plat_left_1", "r5_plat_right_2"]),
    "r5_plat_right_2": (2750, -1100, ["r5_plat_mid_mid", "r5_plat_right_1", "r5_plat_left_2"]),

    #room 6(x : 2000 - 3000, y: 750 - 1500)
    "r6_plat_1_1": (2100, 825, ["r6_plat_1_1"]),
    "r6_plat_1_2": (2690, 825, ["r6_plat_2_1", "r6_plat_1_1"]),
    "r6_plat_2_1": (2900, 950, ["r6_plat_1_2", "r6_plat_2_2"]),
    "r6_plat_2_2": (2350, 1000, ["r6_plat_2_1", "r6_plat_3_1"]),
    "r6_plat_3_1": (2350, 1110, ["r6_plat_2_2", "r6_plat_3_2"]),
    "r6_plat_3_2": (2525, 1110, ["r6_plat_3_1", "r6_plat_4_1"]),
    "r6_plat_4_1": (2500, 1225, ["r6_plat_3_2", "r6_plat_4_2", "r6_plat_4_3"]),
    "r6_plat_4_2": (2300, 1275, ["r6_plat_4_1", "r6_plat_4_3", "r6_floor_1"]),
    "r6_plat_4_3": (2700, 1275, ["r6_plat_4_1", "r6_plat_4_2", "r6_floor_2"]),
    "r6_floor_1": (2150, 1450, ["r6_plat_4_2"]),
    "r6_floor_2": (2850, 1450, ["r6_plat_4_3"]),

    #room 12 (x : 4000 - 5000, y: 0 - 750)
    "r12_enemy_plat": (4450, 200, ["r12_plat_low"]),
    "r12_plat_low": (4400, 475, ["r12_enemy_plat"]),

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


def build_level(level):
    global warden
    warden = None

    rooms = [
        pygame.Rect(0, 0, 1000, 750), #room 0
        pygame.Rect(0, 750, 1000, 750),  #room 1
        pygame.Rect(1000, 0, 1000, 750), #room 2
        pygame.Rect(2000, 0, 1000, 750), #room 3
        pygame.Rect(2000, -750, 1000, 750), #room 4
        pygame.Rect(2000, -1500, 1000, 750), #room 5
        pygame.Rect(2000, 750, 1000, 750), #room 6
        pygame.Rect(1000, 750, 1000, 750), #room 7
        pygame.Rect(1000, 1500, 1000, 750), #room 8
        pygame.Rect(3000, 750, 1000, 750), #room 9
        pygame.Rect(3000, 1500, 1000, 750), #room 10
        pygame.Rect(3000, 0, 1000, 750), #room 11
        pygame.Rect(4000, 0, 1000, 750), #room 12
        pygame.Rect(4000, -750, 1000, 750), #room 13
        pygame.Rect(5000, 0, 1000, 750), #room 14
        pygame.Rect(5000, -750, 1000, 750), #room 15
        pygame.Rect(6000, -750, 1000, 750), #room 16
        pygame.Rect(7000, -750, 1000, 750), #room 17
        pygame.Rect(7000, -1500, 1000, 750), #room 18
        pygame.Rect(6000, -1500, 1000, 750), #room 19
        pygame.Rect(6000, -2250, 1000, 750), #room 20 (warden room 1)
        pygame.Rect(5000, -2250, 1000, 750), #room 21 (warden room 2)
        pygame.Rect(6000, -3000, 1000, 750), #room 22 (warden room 3)
        pygame.Rect(5000, -3000, 1000, 750), #room 23 (warden room 4)
        pygame.Rect(7000, -3000, 1000, 750), #room 24 (ending room) 

        #build rooms off of this :thumbsUp:
    ]

    platforms = [
        #room 0 (0 - 1000, 0 - 750)
        pygame.Rect(0, 725, 450, 40),
        pygame.Rect(550, 725, 450, 40),
        pygame.Rect(200, 550, 150, 20),
        pygame.Rect(700, 600, 200, 20),
        pygame.Rect(0, 0, 25, 750),
        pygame.Rect(0, 0, 1000, 25),
        pygame.Rect(425, 375, 150, 20),
        pygame.Rect(675, 200, 50, 20),

        #room 1 (0 - 1000, 750 - 1500)
        pygame.Rect(0, 1475, 1000, 40),
        pygame.Rect(200, 1225, 200, 30),
        pygame.Rect(500, 1350, 300, 30),
        pygame.Rect(550, 1050, 200, 30),
        pygame.Rect(350, 900, 250, 30),
        pygame.Rect(0, 750, 25, 1000),
        pygame.Rect(25, 1325, 300, 30),
        pygame.Rect(700, 1150, 150, 30),
        pygame.Rect(975, 750, 25, 750),

        #room 2 (1000 - 2000, 0 - 750)
        pygame.Rect(1000, 725, 1000, 40),
        pygame.Rect(1050, 550, 150, 20),
        pygame.Rect(1250, 450, 150, 20),
        pygame.Rect(1400, 300, 200, 20),
        pygame.Rect(1700, 100, 200, 650),
        pygame.Rect(1000, 0, 1000, 25),
        pygame.Rect(1900, 500, 150, 250),

        #room 3 (2000 - 3000, 0 - 750)
        pygame.Rect(2000, 725, 450, 40), #floor left
        pygame.Rect(2550, 725, 450, 40), #floor right
        pygame.Rect(2000, -25, 450, 50), #roof left
        pygame.Rect(2550, -25, 450, 50), #roof right
        pygame.Rect(2200, 375, 25, 225),
        pygame.Rect(2425, 375, 25, 225),
        pygame.Rect(2425, 85, 25, 225),
        pygame.Rect(2550, 375, 25, 225),
        pygame.Rect(2550, 85, 25, 225),
        pygame.Rect(2750, 85, 25, 225),
        pygame.Rect(2725, 575, 200, 25),
        pygame.Rect(2975, 100, 50, 650),

        #room 4 (2000 - 3000, -750 - 0)
        pygame.Rect(2000, -750, 25, 750),
        pygame.Rect(2975, -750, 25, 750),
        pygame.Rect(2000, -775, 450, 50), #roof left
        pygame.Rect(2550, -775, 450, 50), #roof right
        pygame.Rect(2750, -400, 20, 250),
        pygame.Rect(2750, -550, 250, 20),
        pygame.Rect(2000, -150, 150, 20),
        pygame.Rect(2250, -150, 150, 20),
        pygame.Rect(2200, -350, 150, 20),
        pygame.Rect(2000, -500, 300, 20),
        pygame.Rect(2300, -650, 250, 20),
        pygame.Rect(2550, -750, 20, 320),
        pygame.Rect(2450, -450, 100, 20),

        #room 5(2000 - 3000, -1500 - -750)
        pygame.Rect(2000, -1500, 25, 750),
        pygame.Rect(2975, -1500, 25, 750),
        pygame.Rect(2000, -1500, 1000, 25),
        pygame.Rect(2000, -900, 200, 25),
        pygame.Rect(2800, -900, 200, 25),
        pygame.Rect(2250, -1050, 200, 25),
        pygame.Rect(2550, -1050, 200, 25),
        pygame.Rect(2480, -1400, 40, 300),
        pygame.Rect(2375, -950, 250, 25),

        #room 6(2000 - 3000, 750 - 1500)
        pygame.Rect(2000, 1475, 1000, 25), #floor
        pygame.Rect(1975, 750, 50, 650), # wall left
        pygame.Rect(2975, 750, 50, 650), #wall right
        pygame.Rect(2000, 850, 700, 20),
        pygame.Rect(2400, 1000, 600, 20),
        pygame.Rect(2000, 1150, 500, 20),
        pygame.Rect(2300, 1300, 400, 200),

        #room 7(1000 - 2000, 750 - 1500)
        pygame.Rect(1000, 750, 25, 750), #left wall
        pygame.Rect(1000, 1475, 450, 50),
        pygame.Rect(1550, 1475, 450, 50),
        pygame.Rect(1000, 1250, 150, 250),
        pygame.Rect(1130, 875, 20, 270),
        pygame.Rect(1150, 875, 100, 20),
        pygame.Rect(1400, 875, 250, 20),
        pygame.Rect(1230, 875, 20, 250),
        pygame.Rect(1400, 875, 20, 425),
        pygame.Rect(1230, 1125, 175, 20),
        pygame.Rect(1650, 875, 20, 350),
        pygame.Rect(1850, 875, 20, 350),
        pygame.Rect(1650, 1225, 220, 20),
        pygame.Rect(1400, 1380, 600, 20),
        pygame.Rect(1475, 975, 125, 20),

        #room 8 (1000 - 2000, 1500 - 2250)
        pygame.Rect(1000, 1500, 25, 750), #wall left
        pygame.Rect(1975, 1500, 25, 750), #wall right
        pygame.Rect(1000, 2225, 1000, 25), #floor
        pygame.Rect(1550, 1475, 25, 250),
        pygame.Rect(1400, 1725, 175, 25),
        pygame.Rect(1400, 1650, 25, 75),
        pygame.Rect(1025, 1850, 225, 25),
        pygame.Rect(1450, 1900, 125, 25),
        pygame.Rect(1000, 2075, 900, 25),
        pygame.Rect(1700, 1575, 200, 25),
        pygame.Rect(1875, 1575, 25, 500),
        pygame.Rect(1800, 1800, 75, 25),
        pygame.Rect(1700, 2150, 25, 75),
        pygame.Rect(1600, 2100, 25, 75),
        pygame.Rect(1500, 2150, 25, 75),
        pygame.Rect(1400, 2100, 25, 75),
        pygame.Rect(1300, 2150, 25, 75),
        pygame.Rect(1200, 2100, 25, 75),

        #room 9 (3000 - 4000, 750 - 1500)
        pygame.Rect(3000, 750, 1000, 25), #roof
        pygame.Rect(3975, 750, 25, 750), #right wall
        pygame.Rect(3000, 1475, 800, 50), #floor
        pygame.Rect(3250, 900, 20, 600),
        pygame.Rect(3025, 1380, 150, 20),
        pygame.Rect(3100, 1230, 150, 20),
        pygame.Rect(3025, 1080, 150, 20),
        pygame.Rect(3100, 880, 250, 20),
        pygame.Rect(3450, 750, 20, 250),
        pygame.Rect(3450, 1200, 200, 20),
        pygame.Rect(3650, 900, 20, 320),
        pygame.Rect(3550, 900, 100, 20),
        pygame.Rect(3470, 1350, 150, 20),
        pygame.Rect(3800, 900, 20, 625),
        pygame.Rect(3450, 1200, 20, 170),

        #room 10 (3000 - 4000, 1500 - 2250)
        pygame.Rect(3975, 1500, 25, 750), #wall right
        pygame.Rect(3000, 2225, 1000, 25), # floor
        pygame.Rect(3000, 1500, 25, 750),
        pygame.Rect(3800, 1500, 20, 300),
        pygame.Rect(3100, 2100, 900, 25),
        pygame.Rect(3700, 1950, 100, 20),
        pygame.Rect(3500, 1650, 20, 300),
        pygame.Rect(3600, 1780, 300, 20),
        pygame.Rect(3450, 1650, 150, 20),
        pygame.Rect(3375, 1500, 20, 275),
        pygame.Rect(3100, 1925, 200, 20),
        pygame.Rect(3295, 1775, 100, 20),
        pygame.Rect(3025, 1650, 100, 25),
        pygame.Rect(3100, 1925, 25, 175),

        #room 11 (3000 - 4000, 0 - 750)
        pygame.Rect(3000, 0, 1000, 25), #roof
        pygame.Rect(3000, 725, 1000, 25), #floor
        pygame.Rect(3975, 100, 50, 650), #right wall
        pygame.Rect(3000, 150, 300, 400),
        pygame.Rect(3000, 650, 300, 100),
        pygame.Rect(3000, 550, 150, 200),
        pygame.Rect(3150, 125, 50, 25),
        pygame.Rect(3200, 100, 50, 50),
        pygame.Rect(3300, 250, 100, 25),
        pygame.Rect(3500, 150, 250, 450),
        pygame.Rect(3400, 450, 100, 25),
        pygame.Rect(3750, 250, 50, 350),
        pygame.Rect(3925, 250, 50, 350),
        pygame.Rect(3800, 350, 35, 250),
        pygame.Rect(3895, 350, 35, 250),
        pygame.Rect(3550, 100, 50, 50),
        pygame.Rect(3600, 125, 50, 25),

        #room 12 (4000 - 5000, 0 - 750)
        pygame.Rect(4000, -25, 450, 50), #roof left
        pygame.Rect(4550, -25, 450, 50), #rooft right
        pygame.Rect(4000, 725, 1000, 25), #floor
        pygame.Rect(4975, 0, 50, 150), #right wall up
        pygame.Rect(4975, 350, 50, 400), #right wall down
        pygame.Rect(4075, 0, 10, 400),
        pygame.Rect(4150, 300, 10, 250),
        pygame.Rect(4200, 75, 100, 10),
        pygame.Rect(4300, 75, 10, 425),
        pygame.Rect(4400, 250, 100, 10),
        pygame.Rect(4300, 500, 200, 10),
        pygame.Rect(4600, 75, 25, 500),

        #room 13(4000 - 5000, -750 - 0)
        pygame.Rect(4000, -750, 25, 750),
        pygame.Rect(4000, -750, 1000, 25),
        pygame.Rect(4975, -600, 50, 600),
        pygame.Rect(4150, -160, 550, 10),
        pygame.Rect(4150, -310, 550, 10),
        pygame.Rect(4150, -460, 550, 10),
        pygame.Rect(4150, -600, 550, 10),
        pygame.Rect(4850, -750, 25, 650),

        #room 14(5000 - 6000, 0 - 750)
        pygame.Rect(5000, 0, 1000, 25),
        pygame.Rect(5975, 0, 25, 750),
        pygame.Rect(5000, 725, 1000, 25),
        pygame.Rect(5000, 600, 200, 150),
        pygame.Rect(5200, 125, 25, 400),
        pygame.Rect(5200, 500, 700, 25),
        pygame.Rect(5400, 600, 100, 25),
        pygame.Rect(5700, 600, 100, 25),
        pygame.Rect(5900, 100, 25, 425),
        pygame.Rect(5300, 250, 600, 25),
        pygame.Rect(5300, 125, 25, 125),
        pygame.Rect(5575, 125, 100, 25),
        pygame.Rect(5400, 350, 25, 150),
        pygame.Rect(5550, 250, 25, 150),
        pygame.Rect(5700, 350, 25, 150),

        #room 15(5000 - 6000, -750 - 0)
        pygame.Rect(5000, -750, 1000, 25),
        pygame.Rect(5975, -750, 50, 650),
        pygame.Rect(5000, -25, 1000, 25),
        pygame.Rect(5000, -350, 100, 25),
        pygame.Rect(5075, -750, 25, 250),
        pygame.Rect(5200, -600, 200, 25),
        pygame.Rect(5300, -600, 25, 500),
        pygame.Rect(5500, -750, 25, 300),
        pygame.Rect(5400, -300, 100, 25),
        pygame.Rect(5600, -500, 25, 400),
        pygame.Rect(5600, -500, 200, 25),
        pygame.Rect(5800, -500, 25, 250),
        pygame.Rect(5800, -200, 100, 25),
        pygame.Rect(5900, -200, 25, 100),

        #room 16 (6000 - 7000, -750 - 0)
        pygame.Rect(6000, -25, 1000, 25), #floor
        pygame.Rect(6200, -750, 800, 25), #roof
        pygame.Rect(6975, -750, 50, 600), # right wall
        pygame.Rect(6100, -100, 100, 100),
        pygame.Rect(6800, -100, 100, 100),
        pygame.Rect(6500, -750, 25, 400),
        pygame.Rect(6100, -400, 300, 25),
        pygame.Rect(6600, -400, 300, 25),
        pygame.Rect(6300, -550, 100,  25),
        pygame.Rect(6600, -550, 100, 25),

        #room 17 (7000 - 8000, -750 - 0)
        pygame.Rect(7000, -25, 1000, 25), #floor
        pygame.Rect(7975, -750, 25, 750), #right wall
        pygame.Rect(7000, -750, 725, 25),
        pygame.Rect(7200, -250, 25, 250),
        pygame.Rect(7150, -275, 100, 25),
        pygame.Rect(7025, -350, 200, 25),
        pygame.Rect(7025, -475, 75, 25),
        pygame.Rect(7100, -650, 25, 200),
        pygame.Rect(7200, -750, 25, 175),
        pygame.Rect(7400, -525, 150, 25),
        pygame.Rect(7600, -550, 25, 250),
        pygame.Rect(7600, -200, 100, 25),
        pygame.Rect(7700, -400, 25, 225),
        pygame.Rect(7775, -550, 25, 150),
        pygame.Rect(7850, -325, 150, 25),
        pygame.Rect(7900, -750, 100, 225),
        pygame.Rect(7600, -550, 250, 25),

        #room 18 (7000 - 8000, -1500 - 750) [This is a troll room... just felt like it lol]
        pygame.Rect(7000, -775, 725, 25),
        pygame.Rect(7900, -775, 100, 25),
        pygame.Rect(7975, -1650, 25, 900),
        pygame.Rect(7000, -1650, 25, 900),
        pygame.Rect(7000, -1650, 1000, 25),

        #room 19 (6000 - 7000, -1500 - -750)
        pygame.Rect(6000, -1500, 25, 750),
        pygame.Rect(6200, -775, 1000, 25),
        pygame.Rect(6975, -1500, 25, 750),
        pygame.Rect(6125, -1500, 900, 25),
        pygame.Rect(6480, -1250, 40, 250),





]

    terminals = [
        Terminal(x = 250, y = 500, **copy.deepcopy(PUZZLES[0]) ,timeLimit = 20.0, room="general"),
        Terminal(x = 1300, y = 400, **copy.deepcopy(PUZZLES[1]),timeLimit = 20.0, room="general"),
        Terminal(x = 300, y = 1175, **copy.deepcopy(PUZZLES[2]),timeLimit = 20.0, room="general"),
        Terminal(x = 2750, y = 525, **copy.deepcopy(PUZZLES[2]), timeLimit=20.0, room="general"),
        Terminal(x = 2800, y = -600, **copy.deepcopy(PUZZLES[1]), timeLimit = 20.0, room="general"),
        Terminal(x = 2480, y = -1450, **copy.deepcopy(PUZZLES[2]), timeLimit = 20.0, room="general"),
        Terminal(x = 2400, y = 1250, **copy.deepcopy(PUZZLES[3]), timeLimit=20.0, room="general"),
        Terminal(x = 1515, y = 925, **copy.deepcopy(PUZZLES[4]), timeLimit=20.0, room="general"),
        Terminal(x = 1025, y = 2175, **copy.deepcopy(PUZZLES[5]), timeLimit = 20.0, room="general"),
        Terminal(x = 3500, y = 1300, **copy.deepcopy(PUZZLES[4]), timeLimit=20.0, room="general"),
        Terminal(x = 3900, y = 2175, **copy.deepcopy(PUZZLES[5]), timeLimit=20.0, room="general"),
        Terminal(x = 3190, y = 600, **copy.deepcopy(PUZZLES[3]), timeLimit=20.0, room="general"),
        Terminal(x = 4625, y = 450, **copy.deepcopy(PUZZLES[4]), timeLimit=20.0, room="general"),
        Terminal(x=4650, y=-75, **copy.deepcopy(PUZZLES[5]), timeLimit=20.0, room="general"),
        Terminal(x=5800, y=450, **copy.deepcopy(PUZZLES[4]), timeLimit=20.0, room="general"),
        Terminal(x=5425, y=-350, **copy.deepcopy(PUZZLES[5]), timeLimit=20.0, room="general"),

        Terminal(x=6325, y = -450, **copy.deepcopy(PUZZLES[6]), timeLimit=20.0, room="general"),
        Terminal(x=6650, y = -450, **copy.deepcopy(PUZZLES[7]), timeLimit=20.0, room="general"),

        Terminal(x = 7050, y = -525, **copy.deepcopy(PUZZLES[8]), timeLimit=20.0, room="general"),
        Terminal(x = 7900, y=-375, **copy.deepcopy(PUZZLES[9]), timeLimit=20.0, room="general"),

        Terminal(x = 7550, y = -825, **copy.deepcopy(PUZZLES[4]), timeLimit=20.0, room="general"),

        Terminal(x = 6480, y = -950, **copy.deepcopy(PUZZLES[5]), timeLimit=20.0, room="general"),
        # for the warden fight, do room="warden" instead
    ]

    doors = [
        Door(x = 450, y = 725, width=100, height = 20, openX=-100, openY = -0, requiredTerminals=[terminals[0]]),
        Door(x = 990, y = 25, width = 20, height = 700, openX = 0, openY = -800, requiredTerminals=[terminals[0], terminals[2]]),
        Door(x = 1700, y = 25, width = 50, height = 75, openX = 0, openY = -100, requiredTerminals=[terminals[0], terminals[1], terminals[2]]),
        Door(x = 2450, y = 0, width = 100, height = 25,  openX = -100, openY = -0, requiredTerminals=[terminals[3]]),
        Door(x = 2450, y = 725, width = 100, height = 25,  openX = -100, openY = -0, requiredTerminals=[terminals[3], terminals[4], terminals[5]]),
        Door(x = 2450, y = -750, width = 100, height = 25,  openX = -100, openY = -0, requiredTerminals=[terminals[3], terminals[4]]),
        Door(x = 1975, y = 1400, width=50, height=75, openX = -0, openY = -100, requiredTerminals=[terminals[6]]),
        Door(x = 1450, y = 1475, width = 100, height=50, openX = -100, openY = -0, requiredTerminals=[terminals[6], terminals[7]]),
        Door(x = 1400, y = 1300, width = 20, height = 100, openX = -0, openY = -100, requiredTerminals=[terminals[6], terminals[7]]),
        Door(x = 2975, y = 1400, width = 50, height=75, openX= -0, openY = -100, requiredTerminals=[terminals[6], terminals[7], terminals[8]]),
        Door(x = 3800, y = 900, width=200, height=25, openX=200, openY= -0, requiredTerminals=[terminals[9]]),
        Door(x = 2975, y = 25, width=25, height=75, openX=-0, openY=100, requiredTerminals=[terminals[9], terminals[10]]),
        Door(x = 3660, y = 25, width=25, height=125, openX = -0, openY = -125, requiredTerminals=[terminals[11]]),
        Door(x = 3975, y = 25, width = 25, height = 75, openX = -0, openY = -75, requiredTerminals=[terminals[11]]),
        Door(x = 4350, y = 0, width=200, height=25, openX = -0, openY=75, requiredTerminals=[terminals[11], terminals[12]]),
        Door(x= 5000, y = 150, width = 25, height = 200, openX = -175, openY = -0, requiredTerminals=[terminals[12]]),

        Door(x=4550, y= -150, width=25, height=150, openX=-125, openY=-0, requiredTerminals=[terminals[12], terminals[13]]),
        Door(x= 4975, y = 150, width = 25, height = 200, openX = -0, openY = -200, requiredTerminals=[terminals[12], terminals[13]]),

        Door(x = 4975, y = 125, width=225, height=25, openX = -0, openY = 100, requiredTerminals=[terminals[13], terminals[14]]),
        Door(x=4975, y = -725, width=50, height=125, openX= -0, openY=-125, requiredTerminals=[terminals[13], terminals[14]]),

        Door(x=5300, y=-100, width=25, height=100, openX = -0, openY = -100, requiredTerminals=[terminals[15]]),
        Door(x=5600, y=-100, width=25, height=100, openX = -0, openY = -100, requiredTerminals=[terminals[15]]),
        Door(x=5900, y=-100, width=25, height=100, openX = -0, openY = -100, requiredTerminals=[terminals[15]]),
        Door(x=5975, y=-100, width=50, height=100, openX = -0, openY = -100, requiredTerminals=[terminals[15]]),

        Door(x=6975, y = -150, width=50, height=125, openX=-0, openY=-200, requiredTerminals=[terminals[16], terminals[17]]),

        Door(x=7725, y = -750, width=175, height=25, openX=-200, openY=-200, requiredTerminals=[terminals[18], terminals[19]]),
        Door(x=7600, y = -750, width=25, height=200, openX = -0, openY=-200, requiredTerminals=[terminals[18], terminals[19]]),

        Door(x = 7000, y = -1500, width=1000, height=25, openX=1000, openY=0, requiredTerminals=[terminals[20]]),

        Door(x=6000, y = -750, width=200, height=25, openX=400, openY=-150, requiredTerminals=[terminals[16], terminals[17], terminals[18], terminals[19], terminals[20]]),

        Door(x = 6025, y = -1500, width=100, height=25, openX=100, openY=-0, requiredTerminals=[terminals[21]]),


    ]

    enemies = [
        Enemy(750, 550, patrol_range = 500, waypoints = WAYPOINTS),
        Enemy(600, 1300, patrol_range = 500, waypoints = WAYPOINTS),
        Enemy(2700, 675, patrol_range= 150, waypoints= WAYPOINTS),
        Enemy(2300, -200, patrol_range=150, waypoints=WAYPOINTS),
        Enemy(2100, -950, patrol_range = 150, waypoints=WAYPOINTS),
        Enemy(2900, -950, patrol_range=150, waypoints=WAYPOINTS),
        Enemy(2900, 950, patrol_range=600, waypoints=WAYPOINTS),
        Enemy(1775, 1175, patrol_range=200, waypoints=WAYPOINTS),
        Enemy(1275, 1075, patrol_range=150, waypoints=WAYPOINTS),
        Enemy(1450, 1675, patrol_range=100, waypoints=WAYPOINTS),
        Enemy(1175, 2025, patrol_range=750, waypoints=WAYPOINTS),
        Enemy(1700, 2025, patrol_range=700, waypoints=WAYPOINTS),
        Enemy(3400, 1425, patrol_range=500, waypoints=WAYPOINTS),
        Enemy(3700, 1425, patrol_range=500, waypoints=WAYPOINTS),
        Enemy(3200, 2050, patrol_range=800, waypoints=WAYPOINTS),
        Enemy(3700, 2050, patrol_range=800, waypoints=WAYPOINTS),

        Enemy(4125, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4250, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4375, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4500, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4625, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4750, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4875, 675, patrol_range=1000, waypoints=WAYPOINTS),

        Enemy(4450, 200, patrol_range=100, waypoints=WAYPOINTS),

        Enemy(4200, -210, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4650, -210, patrol_range=1000, waypoints=WAYPOINTS, facing = -1),
        
        Enemy(4300, -360, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(4550, -360, patrol_range=1000, waypoints=WAYPOINTS, facing = -1 ),
        
        Enemy(4500, -510, patrol_range=1000, waypoints=WAYPOINTS),

        Enemy(5350, 675, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(5850, 675, patrol_range=1000, waypoints=WAYPOINTS, facing=-1),

        Enemy(5400, 200, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(5800, 200, patrol_range=1000, waypoints=WAYPOINTS, facing=-1),

        Enemy(5200, -75, patrol_range=750, waypoints=WAYPOINTS),
        Enemy(5500, -75, patrol_range=750, waypoints=WAYPOINTS),
        Enemy(5700, -75, patrol_range=750, waypoints=WAYPOINTS),

        Enemy(6200, -450, patrol_range=300, waypoints=WAYPOINTS),
        Enemy(6800, -450, patrol_range=300, waypoints=WAYPOINTS, facing =-1),

        Enemy(7400, -75, patrol_range=600, waypoints=WAYPOINTS),
        Enemy(7600, -75, patrol_range=600, waypoints = WAYPOINTS),
        Enemy(7800, -75, patrol_range=600, waypoints=WAYPOINTS, facing=-1),

        Enemy(7100, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7200, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7300, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7400, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7500, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7600, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7700, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7800, -1550, patrol_range=1000, waypoints=WAYPOINTS),
        Enemy(7900, -1550, patrol_range=1000, waypoints=WAYPOINTS),
    ]

    loreKeys = [
        LoreKey(685, 160, "prologue_1"),
        LoreKey(750, 1425, "prologue_2"),
        LoreKey(1800, 55, "prologue_3"),
        LoreKey(2750, 40, "ch1_1"),
        LoreKey(2500, -500, "ch1_2"),
        LoreKey(1825, 1750, "ch2_1"),
        LoreKey(3050, 1600, "ch2_2"),
        LoreKey(3935, 675, "ch3_1"),
        LoreKey(5700, -450, "ch3_2"),
        LoreKey(6480, -1300, "ch3_3"),

        
    ]

    checkPoints = [
        Checkpoint(x = 100, y = 625, width = 100, height = 100),
        Checkpoint(x = 2000, y = 25, width = 50, height = 475),
        Checkpoint(x = 2300, y = 1250, width = 400, height = 50),
        Checkpoint(x = 3050, y = 25, width = 50, height = 125),
        Checkpoint(x = 6100, y = -200, width=100, height=100),
        Checkpoint(x = 6400, y = -875, width=200, height=100),

    ]

    if len(rooms) > max(WARDEN_ARENA_ROOMS):
        arenaStartRoom = rooms[WARDEN_ARENA_ROOMS[0]]
        warden_x = arenaStartRoom.left + (arenaStartRoom.width // 2) - 25
        warden_y = arenaStartRoom.top + (arenaStartRoom.height - 150)
        warden = Warden(warden_x, warden_y)

        loreKeys.extend([
            LoreKey(arenaStartRoom.left + 180, arenaStartRoom.top + 650, "ch4_1"),
            LoreKey(arenaStartRoom.left + 800, arenaStartRoom.top + 650, "ch4_2"),
            LoreKey(arenaStartRoom.left + 360, arenaStartRoom.top + 450, "ch5_1"),
            LoreKey(arenaStartRoom.left + 640, arenaStartRoom.top + 450, "ch5_2")
        ])

    return {
        "rooms": rooms,
        "platforms": platforms,
        "terminals": terminals,
        "enemies": enemies,
        "doors": doors,
        "loreKeys": loreKeys,
        "checkPoints": checkPoints
    }

levelData = build_level(0)
rooms = levelData["rooms"]
platforms = levelData["platforms"]
terminals = levelData["terminals"]
enemies = levelData["enemies"]
doors = levelData["doors"]
loreKeys = levelData["loreKeys"]
checkPoints = levelData["checkPoints"]
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
    global current_slot, player, levelData, rooms, platforms, currRoom, terminals, enemies, doors, loreKeys, checkPoints, world_timer, timer_active
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
        lines = wrap_text(line, small_font, boxRect.width - 40)
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


running = True
while running:
    dt = clock.tick(FPS) / 1000.0 #convert delta time to seconds

    if saveNotificationTimer > 0:
        saveNotificationTimer -= dt
        if saveNotificationTimer < 0:
            saveNotificationTimer = 0

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
                    warden.dialogue_index += 1
                    if warden.dialogue_index >= len(warden.dialogue_lines):
                        warden.talking = False
                        current_state = PLAYING
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_state == READING:
                current_state = PLAYING
            elif current_state == WARDEN_DIALOGUE and warden and not warden.defeated:
                warden.dialogue_index += 1
                if warden.dialogue_index >= len(warden.dialogue_lines):
                    warden.talking = False
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
        
    if current_state == PLAYING or current_state == HACKING:
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
                    break
    
            if player.rect.top > 5000: #change this later for whenever more rooms are added upwards
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

    elif current_state in (PLAYING, HACKING, PAUSED, GAME_OVER):
        screen.fill((30, 30, 60))

        # if currRoom == 18 and not camera.isTrans:
        #     roomText = small_font.render("WATCH OUT!", True, WHITE)
        #     worldRect = pygame.Rect(7450, -1250, roomText.get_width(), roomText.get_height())
        #     screenRect = camera.apply(worldRect)
        #     screen.blit(roomText, screenRect.topleft)

        if currRoom == 19 and not camera.isTrans:
            lines = [
                "I ran out of room ideas...",
                "Here's a free room before the boss room",
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