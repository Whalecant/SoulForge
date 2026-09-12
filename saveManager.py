import pygame
import json
import os

WHITE = (255, 255, 255)

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, font=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = font or pygame.font.Font(None, 32)
        self.text = text
        self.text_surface = self.font.render(text, True, WHITE)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, mouse_pos):
        self.current_color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=8)
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))

class SaveManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self.load()

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self.default_data()

    def default_data(self):
        return {
            "slots": [
                {"level": 1, "player_x": 100, "player_y": 675, "exists": False},
                {"level": 1, "player_x": 100, "player_y": 675, "exists": False},
                {"level": 1, "player_x": 100, "player_y": 675, "exists": False},
            ]
        }

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

    def write_slot(self, index, level, player_x, player_y, terminalsData = None):
        self.data["slots"][index] = {
            "level": level,
            "player_x": player_x,
            "player_y": player_y,
            "exists": True,
            "terminals": terminalsData if terminalsData is not None else [],
        }

        self.save()

    def reset_slot(self, index):
        self.data["slots"][index] = {
            "level": 1,
            "player_x": 100,
            "player_y": 675,
            "exists": False,
            "terminals": [],
        }
        self.save()

    def get_slot(self, index):
        return self.data["slots"][index]