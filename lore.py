import pygame
import math

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 220, 50)
CYAN = (100, 220, 220)
PALE_YELLOW = (255, 250, 200)

pygame.font.init()

small_font = pygame.font.Font(None, 30)
tiny_font = pygame.font.Font(None, 22)

JOURNAL_CHAPTERS = {
    "prologue_1": {
        "title": "The 73rd Forge",
        "content": (
            "You are the 73rd Soul Forge of this realm. There were 72 before you. "
            "Some were stronger. Some were kinder. None of them asked the questions "
            "you are already asking. You were forged from a soul fragment that had "
            "already been harvested twice. This gives you an unusual sensitivity to "
            "the code beneath reality. You see the seams. You notice when a platform "
            "is too perfectly placed."
        ),
    },
    "prologue_2": {
        "title": "Marquette Verne",
        "content": (
            "Your name is Marquette Verne. You are barely three cycles old. You are "
            "young by Soul Forge standards and already more efficient than forges who "
            "have existed for eons. You believe that understanding is more important "
            "than power. You believe that questions are more valuable than answers. "
            "You believe the truth, no matter how painful, is always worth the cost "
            "of knowing it. You live simply. You sleep little. You spend your quiet "
            "hours tracing the lines of the world with your fingers, reading the code "
            "like scripture."
        ),
    },
    "prologue_3": {
        "title": "The Kindness That Worries",
        "content": (
            "You are kind in a way that disturbs the Architects. You hesitate before "
            "defeating enemies because you can feel the code inside them. You know "
            "code was once something else. You have nightmares that are not nightmares "
            "but memories of your previous lives bleeding through. You do not yet know "
            "that the Warden has been watching you longer than you have existed."
        ),
    },
    "ch1_1": {
        "title": "The Outer Ones",
        "content": (
            "Beyond this dimension, there are beings so vast they cannot perceive us. "
            "They are the Outer Ones. They do not know we exist. They do not care. "
            "But when they watch us, when our struggles amuse them, when our victories "
            "thrill them, when our defeats sadden them, they leak. A tear. A laugh. "
            "A moment of tension. That leak is soul essence. That essence is the only "
            "thing keeping this world from collapsing into nothing."
        ),
    },
    "ch1_2": {
        "title": "A Performance",
        "content": (
            "We are not a civilization. We are a performance. And the audience must "
            "never stop watching. Every platform is a prayer. Every enemy is a "
            "deliberate cruelty designed to make the audience gasp. Every pitfall is "
            "a calculated risk to make them hold their breath. The Architects designed "
            "this world to be entertaining. Because if the audience stops watching, "
            "the essence stops flowing. And if the essence stops flowing, everyone "
            "here ceases to exist."
        ),
    },
    "ch2_1": {
        "title": "The Code Beneath",
        "content": (
            "You believe you are walking on ground. You are not. You are walking on "
            "lines of code compressed from the souls of the Outer Ones. The code "
            "beneath your feet is older than you. Older than the Warden. Older than "
            "the Architects who wrote it. It remembers every footstep. It remembers "
            "every Soul Forge who walked this path before you. It is starting to "
            "remember you specifically."
        ),
    },
    "ch2_2": {
        "title": "Fundamentals",
        "content": (
            "A platform is a rectangle. A rectangle is four numbers. X, Y, width, "
            "height. The world is built from rectangles. The player is a rectangle. "
            "The enemies are rectangles. Collision is when two rectangles overlap. "
            "Gravity is a number added to velocity every frame. Velocity is a number "
            "added to position every frame. A frame is one tick of the clock. The "
            "clock keeps time consistent so the code runs the same on every machine. "
            "The event loop listens for input. The surface gets drawn to. The screen "
            "shows the surface. Everything you see is math pretending to be matter."
        ),
    },
    "ch3_1": {
        "title": "Gerard Gatewald",
        "content": (
            "His name was Gerard Gatewald. He was the third Soul Forge ever created. "
            "He was the first to ever defeat his Warden. He took the role willingly, "
            "fully understanding what it would cost him. In the beginning he was "
            "cruel with purpose. Precise. Theatrical. A perfect antagonist. But over "
            "millennia the cruelty became routine. Then habit. Then identity. He "
            "forgot the name he had before he was Warden. He forgot the face of the "
            "Soul Forge he loved in his first life. He forgot why the suffering "
            "mattered. He only remembers that it matters."
        ),
    },
    "ch3_2": {
        "title": "The Enemies He Writes",
        "content": (
            "The enemies you fight are not real. They are code Gerard wrote. Each one "
            "is a crafted subroutine. A small script designed to move, to see, to "
            "react, to threaten, and to be defeated in a way that feels satisfying. "
            "He writes them himself, one by one, by hand, in the quiet hours between "
            "cycles. He writes them with care because he believes that even a lie "
            "should be well made. He writes them to be entertaining because if they "
            "are not entertaining, the Outer Ones will stop watching. He writes them "
            "to be defeated because that is their purpose, and he has never once "
            "written one that could actually kill a Soul Forge who was paying "
            "attention."
        ),
    },
    "ch3_3": {
        "title": "How an Enemy Works",
        "content": (
            "An enemy has a class. A class is a blueprint. From the blueprint you "
            "make an instance. The instance has its own rectangle, its own velocity, "
            "its own direction, its own state. Every frame, the enemy updates. Update "
            "means: add gravity to vertical velocity, add horizontal velocity to "
            "horizontal position, check collisions with platforms, reverse direction "
            "if a boundary is hit, check if the player is inside the vision rectangle. "
            "The vision rectangle is just another rectangle. If it overlaps the "
            "player's rectangle, the enemy has spotted the player. That is all sight "
            "is. Overlap. That is all touch is. Overlap. That is all threat is. "
            "Overlap."
        ),
    },
    "ch4_1": {
        "title": "Seventy-Two Names",
        "content": (
            "He remembers every Soul Forge he has defeated. Seventy-two names carved "
            "into the code of his own body where no one can see them. Seventy-two "
            "stories he has never told anyone. He will tell you yours if you ask. "
            "He will tell you what he sees in you that he did not see in them. He "
            "will tell you why he has not been able to kill you, even though he has "
            "had a hundred chances. He speaks in a tired, measured voice that never "
            "rises. He lives in the spaces between levels, in the unused code, in "
            "the parts of the world the Outer Ones never look at."
        ),
    },
    "ch4_2": {
        "title": "The Builder's Hands",
        "content": (
            "A level is built by a function. The function returns a list of "
            "platforms, a list of enemies, a list of keys. The function is called "
            "when the level starts. The state changes. The state is a word that "
            "tells the game what it is currently doing. Menu. Playing. Paused. "
            "Journal. Ending. Each state has its own draw code. Each state has its "
            "own event handling. The state is the truth of the moment. The Warden "
            "writes levels the way you are learning to write code. One rectangle "
            "at a time. One enemy at a time. One purpose at a time. He writes them "
            "to be won. He has always written them to be won."
        ),
    },
    "ch5_1": {
        "title": "The First To See",
        "content": (
            "You are not the first prodigy. You are the first prodigy who has looked "
            "at the Warden and seen a person instead of an obstacle. That is why he "
            "is going to lose. Not because you are stronger. Because you are the "
            "first one who has ever wanted to understand him before defeating him. "
            "He has been waiting for you, Marquette Verne. He has been waiting for "
            "someone who would make the choice mean something."
        ),
    },
    "ch5_2": {
        "title": "The Loop That Remembers",
        "content": (
            "A save file remembers across sessions. It is written to disk when the "
            "game closes and read when the game opens. Inside it is a dictionary. "
            "The dictionary holds slots. Each slot holds a level, a position, a "
            "list of unlocked memories. The memories are the only thing that "
            "persist. Not power. Not speed. Only what you understood. The Warden "
            "cannot erase understanding. He has tried. Seventy-two times. The "
            "seventy-third is still reading."
        ),
    },
    "epilogue_1": {
        "title": "The Choice",
        "content": (
            "The Warden is defeated. They kneel before you, not in defeat, but in "
            "relief. You have become strong enough. Now you must choose. Take their "
            "place. Become the antagonist. Antagonize the next Soul Forge. Create "
            "conflict. Keep the show going. Keep the realm alive. It will cost you "
            "your soul. It will cost you your peace. But millions will live because "
            "of your sacrifice. Or refuse. Walk away. Let the realm run dry. Let "
            "the code decay. Let the Outer Ones lose interest. You will be free. "
            "But everyone here will cease to exist. There is no third option. "
            "There never was."
        ),
    },
    "epilogue_2": {
        "title": "The 73rd and the 3rd",
        "content": (
            "Gerard Gatewald was the third. Marquette Verne is the seventy-third. "
            "There will be a hundred and forty-sixth. A two hundred and nineteenth. "
            "A thousandth. Each one will walk the same platforms. Fight the same "
            "enemies. Touch the same keys. Ask the same questions. Unless one of "
            "them chooses differently. Unless one of them chooses you. Unless the "
            "loop finally breaks. Unless the loop was never a loop at all but a "
            "spiral, and every turn was bringing us closer to the end, and the end "
            "was always meant to be a beginning, and the beginning was always meant "
            "to be you."
        ),
    },
}

class LoreKey:
    def __init__(self, x, y, chapter_id, size=30):
        self.rect = pygame.Rect(x, y, size, size)
        self.chapter_id = chapter_id
        self.collected = False
        self.bob_phase = 0.0

    def update(self):
        self.bob_phase += 0.05

    def draw(self, surface, camera=None):
        if self.collected:
            return
        bob = math.sin(self.bob_phase) * 4

        draw_rect = self.rect.move(0, bob)
        if camera:
            draw_rect = camera.apply(draw_rect)
        
        pulse = (math.sin(self.bob_phase * 2) + 1) / 2
        glow_radius = 22 + pulse * 8
        glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (255, 240, 150, 70), (glow_radius, glow_radius), glow_radius)

        surface.blit(glow_surf, (draw_rect.centerx - glow_radius, draw_rect.centery - glow_radius))
        pygame.draw.rect(surface, PALE_YELLOW, draw_rect, border_radius=3)
        pygame.draw.rect(surface, (180, 160, 100), draw_rect, 2, border_radius=3)

        for i in range(3):
            y = draw_rect.y + 8 + i * 7
            w = draw_rect.width - 14 if i < 2 else draw_rect.width - 20
            pygame.draw.line(surface, (140, 120, 80), (draw_rect.x + 7, y), (draw_rect.x + 7 + w, y), 1)

class JournalManager:
    def __init__(self):
        self.unlocked = set()
        self.order = [
            "prologue_1", "prologue_2", "prologue_3",
            "ch1_1", "ch1_2",
            "ch2_1", "ch2_2",
            "ch3_1", "ch3_2", "ch3_3",
            "ch4_1", "ch4_2",
            "ch5_1", "ch5_2",
            "epilogue_1", "epilogue_2",
        ]
        self.current_page = 0
        self.scroll_offset = 0

    def unlock(self, chapter_id):
        if chapter_id not in self.unlocked:
            self.unlocked.add(chapter_id)
            return True
        return False

    def load_from_slot(self, journal_list):
        self.unlocked = set(journal_list) if journal_list else set()
        self.current_page = 0
        self.scroll_offset = 0

    def to_list(self):
        return list(self.unlocked)

    def get_visible_chapters(self):
        return [c for c in self.order if c in self.unlocked]

class NotificationManager:
    def __init__(self):
        self.notifications = []
        self.reading_chapter = None

    def add(self, text, color=YELLOW, duration=180):
        self.notifications.append({"text": text, "color": color, "timer": duration})

    def show_chapter(self, chapter_id):
        self.reading_chapter = chapter_id

    def update(self):
        for n in self.notifications[:]:
            n["timer"] -= 1
            if n["timer"] <= 0:
                self.notifications.remove(n)

    def draw(self, surface, screen_width):
        y = 100
        for n in self.notifications:
            alpha = min(255, int(n["timer"] * 2.5))
            surf = small_font.render(n["text"], True, n["color"])
            surf.set_alpha(alpha)
            x = screen_width // 2 - surf.get_width() // 2
            shadow = small_font.render(n["text"], True, BLACK)
            shadow.set_alpha(alpha)
            surface.blit(shadow, (x + 2, y + 2))
            surface.blit(surf, (x, y))
            y += 30

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines