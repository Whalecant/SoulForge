import pygame
import copy
from hackTerminal import Terminal #type: ignore
from enemy import Enemy #type: ignore
from door import Door #type: ignore
from lore import LoreKey, JournalManager, NotificationManager, JOURNAL_CHAPTERS, wrap_text #type: ignore
from warden import Warden #type: ignore
from checkpointManager import Checkpoint #type: ignore
#imma be honest, idk why the three things above are that bugged lol

#change these values later
WARDEN_ARENA_ROOMS = [20, 21, 22, 23]
ENDING_ROOM_INDEX = 24

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

def build_level(level):
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

        #warden room 1 (6000 - 7000, -2250 - -1500)
        pygame.Rect(6000, -2250, 25, 600),
        pygame.Rect(6000, -2250, 800, 25),
        pygame.Rect(6975, -2250, 25, 750),
        pygame.Rect(6100, -1525, 900, 25),

        #warden room 2 (6000 - 7000, -3000 -2250)
        pygame.Rect(6000, -2275, 800, 25),
        pygame.Rect(6975, -3000, 50, 750),
        pygame.Rect(6000, -3000, 1000, 25),
        pygame.Rect(6000, -2850, 25, 600),

        #warden room 3 (5000 - 6000, -3000 - -2250)
        pygame.Rect(5000, -3000, 1000, 25),
        pygame.Rect(5000, -3000, 25, 750),
        pygame.Rect(5975, -2850, 25, 600),
        pygame.Rect(5200, -2275, 800, 50),

        #warden room 4 (5000 - 6000, -2250 - -1500)
        pygame.Rect(5000, -2250, 25, 750),
        pygame.Rect(5000, -1525, 1000, 25),
        pygame.Rect(5975, -2250, 25, 600),
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

        Door(x = 7000, y = -1500, width=1000, height=25, openX=1000, openY=0, moveSpd=7.5, requiredTerminals=[terminals[20]]),

        Door(x=6000, y = -750, width=200, height=25, openX=400, openY=-150, requiredTerminals=[terminals[16], terminals[17], terminals[18], terminals[19], terminals[20]]),
        Door(x = 6225, y = -775, width = 200, height = 25, openX = -200, openY = -0, requiredTerminals=[terminals[21]]),

        Door(x = 6000, y = -1525, width=125, height=50, openX=125, openY=-0, requiredTerminals=[terminals[21]]),


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
        "checkPoints": checkPoints,
        "warden": warden
    }